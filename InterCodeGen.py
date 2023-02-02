DEBUG_MODE = False


def debug_print(*args):
    if DEBUG_MODE: print(*args)


class InterCodeGen:
    def __init__(self, output_file_name, semantic_error_file_name, symbol_table):
        self.program_block = []
        self.semantic_stack = []
        self.top = -1  # pointer for semantic stack
        self.i = 0  # pointer for program block
        self.data_p = 100  # pointer for data block, as in the slides, we assume it starts with 100
        self.temp_p = 500  # pointer for temporary block, as in the slides, we assume it starts with 500
        self.program_file_name = output_file_name
        self.semantic_error_file_name = semantic_error_file_name
        self.symbol_table = symbol_table
        self.data_block = dict()
        self.scope_p = 0
        self.while_switch_scope_stack = [0] * 100
        self.error_message = ''

    def pop(self, n):
        self.semantic_stack = self.semantic_stack[:self.top - n + 1]
        self.top -= n

    def push(self, m):
        self.semantic_stack.append(m)
        self.top += 1

    def get_temp(self):
        t = self.temp_p
        self.temp_p += 4
        return t

    def codegen(self, action,
                last_input=''):  # let's assume action is a string starting with actionsymbol e.g. actionsymbol8, actionsymbol9, ....
        debug_print(action)

        if action == 'PID':  # let's assume action_number = 1 is for #pid action in the slides
            p = self.find_address_in_symbol_table(last_input)
            self.push(p)
        elif action == 'Assign':  # let's assume action_number = 2 is for #assign action in the slides
            a = self.semantic_stack[self.top]
            b = self.semantic_stack[self.top - 1]
            self.program_block.append('(ASSIGN, ' + str(a) + ', ' + str(b) + ',   )')
            self.i += 1
            self.pop(1)
        elif action in ['Add', 'Sub', 'Mult', 'Div', 'Lt', 'Eq']:
            t = self.get_temp()
            a = self.semantic_stack[self.top]
            b = self.semantic_stack[self.top - 1]
            self.program_block.append('(' + action.upper() + ', ' + str(b) + ', ' + str(a) + ', ' + str(t) + ' )')
            self.i += 1
            self.pop(2)
            self.push(t)
        elif action == 'Save':
            self.push(self.i)
            self.program_block.append('')
            self.i += 1
        elif action == 'Label':  # label_while action in the slides
            self.push(self.i)
        elif action == 'While':  # while action in the slides
            self.program_block[self.semantic_stack[self.top - 3]] = f'(JP, {self.i + 1},  ,   )'
            a = self.semantic_stack[self.top]
            b = self.semantic_stack[self.top - 1]
            self.program_block[int(a)] = '(JPF, ' + str(b) + ', ' + str(self.i + 1) + ' )'
            c = self.semantic_stack[self.top - 2]
            self.program_block.append('(JP, ' + str(c) + ',  ,   )')
            self.i += 1
            self.pop(4)
        elif action == 'Jpf_save':  # jpf_save for 'if' action in the slides
            a = self.semantic_stack[self.top]
            b = self.semantic_stack[self.top - 1]
            self.program_block[int(a)] = '(JPF, ' + str(b) + ', ' + str(self.i + 1) + ' )'
            self.pop(2)
            self.push(self.i)
            self.program_block.append('')
            self.i += 1
        elif action == 'Jp':  # jp for 'if' action in the slides
            a = self.semantic_stack[self.top]
            self.program_block[int(a)] = '(JP, ' + str(self.i) + ',  ,   )'
            self.pop(1)
        elif action == 'Jpf':  # jpf for 'if' action in the slides
            a = self.semantic_stack[self.top]
            b = self.semantic_stack[self.top - 1]
            self.program_block[int(a)] = '(JPF, ' + str(b) + ', ' + str(self.i) + ' )'
            self.pop(2)
        elif action == 'Declare':
            a = self.semantic_stack[self.top]
            self.program_block.append('(ASSIGN, #0, ' + str(a) + ',   )')
            self.i += 1
            self.pop(1)
        elif action == 'Print':
            a = self.semantic_stack[self.top]
            self.program_block.append('(PRINT, ' + str(a) + ',  ,   )')
            self.i += 1
            self.pop(1)
        elif action == 'Save_constant':
            self.push(f'#{last_input}')
        elif action == 'Break':
            last_while_scope = self.find_last_while_scope()
            last_switch_scope = self.find_last_switch_scope()
            if last_switch_scope == last_while_scope == -1:
                print('There is no while or switch to break from in the code! We simply deny the break')
                return
            if last_switch_scope < last_while_scope:
                a = self.semantic_stack[self.top - (self.scope_p - last_while_scope) * 2] - 1
            else:
                a = self.semantic_stack[self.top - (self.scope_p - last_switch_scope) * 2 - 1]
            self.program_block.append(f'(JP, {a},  ,   )')
            self.i += 1
        elif action == 'Jmp_save':
            self.while_switch_scope_stack[self.scope_p] = last_input
            self.program_block.append(f'(JP, {self.i + 2},  ,   )')
            self.i += 1
            self.push(self.i)
            self.program_block.append('')
            self.i += 1
        elif action == 'Eq_switch':
            t = self.get_temp()
            a = self.semantic_stack[self.top]
            b = self.semantic_stack[self.top - 1]
            self.program_block.append('(EQ, ' + str(b) + ', ' + str(a) + ', ' + str(t) + ' )')
            self.i += 1
            self.pop(1)
            self.push(t)
        elif action == 'Switch_Jmp':
            # Here is the end of the switch so the scope pointer should be reduced by one
            self.scope_p -= 1
            a = self.semantic_stack[self.top - 1]
            self.program_block[int(a)] = f'(JP, {self.i},  ,   )'
            self.pop(2)
        elif action == 'Array_declare':
            a = self.semantic_stack[self.top - 1]  # I am assuming this is address of array
            b = self.semantic_stack[self.top]  # I am assuming this is Num pushed to stack
            self.program_block.append('(ASSIGN, #0, ' + str(a) + ',   )')
            self.i += 1
            self.pop(2)
            # Allocate the required space for the array in data block
            self.data_p += 4 * (int(b[1:]) - 1)

        elif action == 'Array_access':
            t = self.get_temp()
            a = self.semantic_stack[self.top - 1]  # I am assuming this is address of array
            b = self.semantic_stack[
                self.top]  # I am assuming this is expression pushed to stack, interestingly, it can be either #4 , a constant, or 502 , an address
            self.program_block.append('(MULT, ' + str(b) + ', #4, ' + str(t) + ' )')
            self.program_block.append('(ADD, #' + str(a) + ', ' + str(t) + ', ' + str(t) + ' )')
            self.i += 2
            self.pop(2)
            self.push(f'@{t}')
        elif action == 'Add_scope':
            self.scope_p += 1
        elif action == 'Reduce_scope':
            self.scope_p -= 1
        elif action == 'Mark_assignment':
            self.pop(1)

    def write_program_block_to_file(self):
        with open(self.program_file_name, 'w') as f:
            f.write('\n'.join(
                [f'{num}\t{code}' for num, code in zip(list(range(len(self.program_block))), self.program_block)]))

        if not self.error_message:
            self.error_message = 'The input program is semantically correct.'
        with open(self.semantic_error_file_name, 'w') as f:
            f.write(self.error_message)

    def find_address_in_symbol_table(self, ID):
        if ID not in self.symbol_table:
            raise Exception('Variable has not been declared yet')
        if self.data_block.get(ID) is None:
            self.data_block[ID] = self.data_p
            self.data_p += 4
        return self.data_block[ID]

    def find_last_while_scope(self):
        for i in reversed(range(self.scope_p)):
            if self.while_switch_scope_stack[i] == 'while':
                return i
        return -1

    def find_last_switch_scope(self):
        for i in reversed(range(self.scope_p)):
            if self.while_switch_scope_stack[i] == 'switch':
                return i
        return -1
