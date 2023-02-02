import json

from InterCodeGen import InterCodeGen
from Scanner import Scanner, TokenType

DEBUG_MODE = False


def debug_print(*args):
    if DEBUG_MODE: print(*args)


class Node:
    def __init__(self, value, children):
        self.value = value
        self.children = children
        self.visited = False
        self.depth = 0

    def __repr__(self):
        return str(self.value)

    def increase_depth(self):
        self.depth += 1


class Parser:
    def __init__(self, syntax_error_file_name, parse_tree_file_name, SLR_table_file_name, scanner: Scanner,
                 inter_code_gen: InterCodeGen):
        self.syntax_error_file_name = syntax_error_file_name
        self.parse_tree_file_name = parse_tree_file_name
        self.SLR_table_file_name = SLR_table_file_name
        self.scanner = scanner
        self.intermediate_code_generator = inter_code_gen
        self.extract_grammar_from_SLR_table()

        self.parse_stack = ['0']
        self.parse_stack_nodes = ['0']
        self.parse_tree = []
        self.current_node = None
        self.array_history = []
        self.syntax_error_message = ''
        self.parse_finished = False
        self.parse_halted = False

    def extract_grammar_from_SLR_table(self):
        table_json = open(self.SLR_table_file_name)
        data_table = json.load(table_json)
        self.terminals = data_table['terminals']  # a list of terminals, the values are: $, (, ), *, ...
        self.non_terminals = data_table[
            'non_terminals']  # a list non terminals, the values are: $accept, program, declaration_lost, declaration, ...
        self.first = data_table[
            'first']  # a dictionary of first values of each non terminal, the keys are: $accept, program, declaration_lost, declaration, ...
        self.follow = data_table[
            'follow']  # a dictionary of follow values of each non terminal, the keys are: $accept, program, declaration_lost, declaration, ...
        self.grammar = data_table[
            'grammar']  # a dictionary of lists,  the keys are 0, 1, ..., the values are 'non_terminal', '->', 'production'
        self.parse_table = data_table[
            'parse_table']  # a dictionary of dictionary, the keys are 0, 1, ..., the values are "accept", "shift_17", "reduce_1", "goto_9"
        debug_print("terminals = ", self.terminals)
        debug_print("non_terminals = ", self.non_terminals)
        debug_print("first = ", self.first)
        debug_print("follow = ", self.follow)
        debug_print("grammar = ", self.grammar)
        debug_print("parse_table = ", self.parse_table)

    def get_next_token_from_scanner(self):
        token = self.scanner.get_next_token()
        while token.type in (TokenType.COMMENT, TokenType.WHITESPACE):
            token = self.scanner.get_next_token()
        debug_print('new token is taken from scanner:', token)
        return token

    def process(self):
        token = self.get_next_token_from_scanner()
        while not self.parse_finished:
            current_state = self.parse_stack[-1]
            debug_print("current_state = ", current_state)
            what_to_do_dictionary = self.parse_table[current_state]
            debug_print("what_to_do_dictionary = ", what_to_do_dictionary)
            debug_print("what_to_do_dictionary.keys() = ", what_to_do_dictionary.keys())
            debug_print("token string = ", token.string)

            if token.string not in what_to_do_dictionary.keys() and token.type not in what_to_do_dictionary.keys():
                debug_print('******************************\nEntering panic mode')
                debug_print('parse_stack before panic mode: ', self.parse_stack)
                self.syntax_error_message += f'#{self.scanner.line_number} : syntax error , illegal {token.string}\n'
                while not list(filter(lambda x: x.startswith('goto'), self.parse_table[self.parse_stack[-1]].values())):
                    self.parse_stack.pop(-1)
                    self.parse_stack.pop(-1)
                    self.parse_stack_nodes.pop(-1)
                    discarded = self.parse_stack_nodes.pop(-1)
                    self.syntax_error_message += f'syntax error , discarded {discarded} from stack\n'
                s = self.parse_stack[-1]
                panic_goto_options = sorted(list(
                    filter(lambda x: self.parse_table[self.parse_stack[-1]][x].startswith('goto'),
                           self.parse_table[self.parse_stack[-1]])))
                debug_print('panic goto options:', panic_goto_options)
                panic_non_terminal = None
                token = self.get_next_token_from_scanner()
                while not panic_non_terminal:
                    for option in panic_goto_options:
                        if token.string in self.follow[option] or token.type in self.follow[option]:
                            panic_non_terminal = option
                            break
                    if not panic_non_terminal:
                        if token.string == '$':
                            self.halt_process()
                            break
                        self.syntax_error_message += f'#{self.scanner.line_number} : syntax error , discarded {token.string} from input\n'
                        token = self.get_next_token_from_scanner()
                if self.parse_halted: break
                self.syntax_error_message += f'#{self.scanner.line_number} : syntax error , missing {panic_non_terminal}\n'

                self.parse_stack.append(panic_non_terminal)
                self.parse_stack.append(self.parse_table[s][panic_non_terminal][5:])
                self.parse_stack_nodes.append(Node(panic_non_terminal, []))
                self.parse_stack_nodes.append(self.parse_table[s][panic_non_terminal][5:])

                debug_print('parse_stack after panic mode: ', self.parse_stack)
                debug_print(self.syntax_error_message)
                debug_print('******************************\nExiting panic mode')
            else:
                if token.string in what_to_do_dictionary.keys():
                    what_to_do = what_to_do_dictionary[token.string]
                elif token.type in what_to_do_dictionary.keys():
                    what_to_do = what_to_do_dictionary[token.type]

                debug_print("what_to_do = ", what_to_do)
                if what_to_do.startswith("shift_"):
                    self.parse_stack.append(token.string)
                    self.parse_stack.append(what_to_do[6:])
                    self.parse_stack_nodes.append(Node(token, []))
                    self.parse_stack_nodes.append(what_to_do[6:])
                    # When we push sth to stack, we go to new state, so we should update below two variables
                    current_state = self.parse_stack[-1]
                    what_to_do_dictionary = self.parse_table[current_state]
                    debug_print("Shift Successful")
                    debug_print("parse_stack = ", self.parse_stack)
                    debug_print("current_state = ", current_state)
                    debug_print("what_to_do_dictionary = ", what_to_do_dictionary)
                    token = self.get_next_token_from_scanner()
                elif what_to_do.startswith("reduce_"):
                    production_rule_for_reduction = self.grammar[what_to_do[7:]]
                    debug_print("production_rule_for_reduction = ", production_rule_for_reduction)
                    non_terminal_at_left_side = production_rule_for_reduction[0]
                    debug_print("non_terminal_at_left_side = ", non_terminal_at_left_side)
                    size_of_right_side = len(production_rule_for_reduction) - 2
                    special_case = False
                    if 'epsilon' in production_rule_for_reduction[2:]:
                        size_of_right_side -= 1
                        special_case = True
                    debug_print("self.parse_stack_nodes = ", self.parse_stack_nodes)
                    if special_case == False:
                        list_of_parse_stack_nodes_to_be_thrown_away = self.parse_stack_nodes[len(
                            self.parse_stack_nodes) - 2 * size_of_right_side:]
                    else:
                        list_of_parse_stack_nodes_to_be_thrown_away = [Node('epsilon', []), '100000']
                    self.current_node = self.create_node(list_of_parse_stack_nodes_to_be_thrown_away,
                                                         non_terminal_at_left_side)
                    debug_print("self.parse_stack before = ", self.parse_stack)
                    if special_case == False:
                        self.parse_stack = self.parse_stack[:-2 * size_of_right_side]
                        self.parse_stack_nodes = self.parse_stack_nodes[:-2 * size_of_right_side]
                    debug_print("self.parse_stack kept = ", self.parse_stack)
                    current_state = self.parse_stack[-1]
                    debug_print("current_state = ", current_state)
                    goto_rule = self.parse_table[current_state][non_terminal_at_left_side]
                    debug_print("goto_rule = ", goto_rule)
                    goto_reduction_number = goto_rule[5:]
                    debug_print("goto_reduction_number = ", goto_reduction_number)
                    self.parse_stack.append(non_terminal_at_left_side)
                    self.parse_stack.append(goto_reduction_number)
                    self.parse_stack_nodes.append(self.current_node)
                    self.parse_stack_nodes.append(goto_reduction_number)
                    # When we push sth to stack, we go to new state, so we should update below two variables
                    current_state = self.parse_stack[-1]
                    what_to_do_dictionary = self.parse_table[current_state]

                    # Call code generator
                    self.intermediate_code_generator.codegen(action=self.grammar[what_to_do[7:]][0],
                                                             last_input=token.string)
                    debug_print("Reduction Successful")
                    debug_print("parse_stack = ", self.parse_stack)
                    debug_print("current_state = ", current_state)
                    debug_print("what_to_do_dictionary = ", what_to_do_dictionary)
                elif what_to_do.startswith("accept"):
                    debug_print("Parsing Acceptance Successful")
                    debug_print("parse_stack = ", self.parse_stack)
                    debug_print("parse_stack_nodes = ", self.parse_stack_nodes)
                    debug_print("current_state = ", current_state)
                    debug_print("what_to_do_dictionary = ", what_to_do_dictionary)
                    first_node = self.parse_stack_nodes[1]
                    the_dollar_token = Node('$', [])
                    the_dollar_token.increase_depth()
                    first_node.children.append(the_dollar_token)
                    second_node = self.parse_stack_nodes[3]
                    debug_print("first_node = ", first_node.value, " ", first_node.children)
                    debug_print("second_node = ", second_node.value, " ", second_node.children)
                    self.parse_finished = True
                    self.get_next_token_from_scanner()
        if self.parse_finished and not self.parse_halted:
            self.save_parse_tree()
            self.save_syntax_errors()
            self.intermediate_code_generator.write_program_block_to_file()

    def create_node(self, parse_stack_stats, current_non_terminal):
        debug_print("create node: parse_stack_stats = ", parse_stack_stats)
        list_of_children = []
        length = len(parse_stack_stats)
        index = 0
        while index < length:
            debug_print("Appending parse_stack_stats[index] = ", parse_stack_stats[index])
            list_of_children.append(parse_stack_stats[index])
            parse_stack_stats[index].increase_depth()
            index += 2
        node = Node(current_non_terminal, list_of_children)
        return node

    def halt_process(self):
        self.parse_finished = True
        self.parse_halted = True
        self.syntax_error_message += f'#{self.scanner.line_number} : syntax error , Unexpected EOF\n'
        with open(self.parse_tree_file_name, 'w') as f:
            f.write('')
        self.save_syntax_errors()

    def save_syntax_errors(self):
        if not self.syntax_error_message:
            self.syntax_error_message = 'There is no syntax error.'
        with open(self.syntax_error_file_name, 'w') as f:
            f.write(self.syntax_error_message)

    def save_parse_tree(self):
        def recursive_save(array_history: list, string='') -> str:
            string_save = string
            parent, last_child_reached = array_history[-1]
            for i in range(1, len(array_history) - 1):
                if array_history[i][1]:
                    string_save += 4 * ' '
                else:
                    string_save += '│' + 3 * ' '
            value = f'({parent.value[0]}, {parent.value[1]})' if isinstance(parent.value, tuple) else parent.value
            if len(array_history) == 1:
                string_save += f'{value}\n'
            else:
                if last_child_reached:
                    string_save += f'└── {value}\n'
                else:
                    string_save += f'├── {value}\n'
            for i, child in enumerate(parent.children):
                if i == len(parent.children) - 1:
                    string_save = recursive_save(array_history + [(child, True)], string_save)
                else:
                    string_save = recursive_save(array_history + [(child, False)], string_save)
            return string_save

        root = self.current_node

        # array_history is the array of (Node, True/False) showing the path inside the tree we are currently traversing. The first element is probably the root.
        # If (Node, True) is inside the array, it means we have reached the last child of Node. (Node, False) means otherwise.
        array_history = [(root, False)]
        string = recursive_save(array_history)
        with open(self.parse_tree_file_name, 'w', encoding='utf-8') as f:
            f.write(string.strip())
