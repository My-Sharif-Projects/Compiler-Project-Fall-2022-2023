TOKEN_TYPES = ['NUM', 'ID', 'KEYWORD', 'SYMBOL', 'COMMENT', 'WHITESPACE']
KEYWORDS = ['if', 'else', 'void', 'int', 'while', 'break', 'switch', 'default', 'case', 'return', 'endif']
SYMBOLS = [';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '<', '=', '/']
WHITESPACES = [' ', '\n', '\r', '\t', '\v', '\f']
ACCEPTABLE_CHARS = [chr(i) for i in range(65, 65 + 26)] + [chr(i) for i in range(97, 97 + 26)] + [chr(i) for i in
                                                                                                  range(48,
                                                                                                        48 + 10)] + SYMBOLS + WHITESPACES


class TokenType:
    NUM = 'NUM'
    ID = 'ID'
    KEYWORD = 'KEYWORD'
    SYMBOL = 'SYMBOL'
    COMMENT = 'COMMENT'
    WHITESPACE = 'WHITESPACE'
    EOF = 'EOF'

    def __init__(self):
        pass


class Token:
    def __init__(self, type: str, string: str):
        self.type = type
        self.string = string


class Scanner:
    def __init__(self, input_file_name, tokens_file_name, errors_file_name, symbol_table_file_name):
        self.input_file_name = input_file_name
        self.tokens_file_name = tokens_file_name
        self.errors_file_name = errors_file_name
        self.symbol_table_file_name = symbol_table_file_name
        try:
            self.text = open(self.input_file_name, 'r').read()
        except:
            raise Exception(f'There is no file in this directory called {self.input_file_name}.')
        self.pointer = 0
        self.current_token_string = ''
        self.eof_pointer = len(self.text)
        self.line_number = 1
        self.comment_start_line = None
        self.scan_is_ended = False
        self.q_state = 0

        self.tokens_table = ''
        self.errors_table = ''
        self.symbols_table = '\n'.join([f'{i + 1}.\t{KEYWORDS[i]}' for i in range(len(KEYWORDS))]) + '\n'
        self.symbols = KEYWORDS.copy()
        self.symbols_table_counter = len(KEYWORDS) + 2

    def move_pointer_back(self, current_character):
        self.pointer -= 1
        if current_character == '\n':
            self.line_number -= 1

    def switch_case_on_q0_state(self, current_character):
        token_found_bool = False
        found_token = None
        if 48 <= ord(current_character) <= 48 + 9:  # this means current_character is 0-9
            self.q_state = 1
            self.current_token_string += current_character
        elif 65 <= ord(current_character) <= 65 + 25 or 97 <= ord(current_character) <= 97 + 25:
            self.q_state = 3
            self.current_token_string += current_character
        elif current_character in [';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '<']:
            self.current_token_string += current_character
            token_found_bool = True
            found_token = Token(TokenType.SYMBOL, self.current_token_string)
        elif current_character == '*':
            self.q_state = 16
            self.current_token_string += current_character
        elif current_character == '=':
            self.q_state = 18
            self.current_token_string += current_character
        elif current_character in [' ', '\n', '\r', '\t', '\v', '\f']:
            token_found_bool = True
            self.current_token_string += current_character
            found_token = Token(TokenType.WHITESPACE, self.current_token_string)
        elif current_character == '/':
            self.q_state = 21
            self.current_token_string += current_character

        return token_found_bool, found_token

    def switch_case_on_comments(self,
                                current_character):  # this part checks both for comments and misleading symbols, /=
        token_found_bool = False
        found_token = None
        if self.q_state == 21:
            if current_character == '/':
                self.current_token_string += current_character
                self.q_state = 25
            elif current_character == '*':
                self.current_token_string += current_character
                self.q_state = 23
                self.comment_start_line = self.line_number  # save the line number of start of the comment
            else:
                token_found_bool = True
                found_token = Token(TokenType.SYMBOL, self.current_token_string)  # self.current_token_string = '/'
                self.move_pointer_back(current_character)
        elif self.q_state == 23:
            if current_character == '*':
                self.q_state = 24
                self.current_token_string += current_character
            else:
                self.current_token_string += current_character
        elif self.q_state == 24:
            if current_character == '/':
                self.current_token_string += current_character
                token_found_bool = True
                found_token = Token(TokenType.COMMENT,
                                    self.current_token_string)  # self.current_token_string = '/* some comments */'
            elif current_character == '*':
                self.current_token_string += current_character
            else:
                self.q_state = 23
                self.current_token_string += current_character
        elif self.q_state == 25:
            if current_character == '\n':  # or EOF
                token_found_bool = True
                found_token = Token(TokenType.COMMENT,
                                    self.current_token_string)  # self.current_token_string = '// some comments'
            else:
                self.current_token_string += current_character
        return token_found_bool, found_token

    def switch_case_on_q1_state(self, current_character):
        token_found_bool = False
        found_token = None
        if 48 <= ord(current_character) <= 48 + 9:  # this means current_character is 0-9
            self.current_token_string += current_character
        else:
            token_found_bool = True
            found_token = Token(TokenType.NUM, self.current_token_string)
            self.move_pointer_back(current_character)
        return token_found_bool, found_token

    def switch_case_on_q3_state(self, current_character):
        token_found_bool = False
        found_token = None
        if 65 <= ord(current_character) <= 65 + 25 or 97 <= ord(current_character) <= 97 + 25 or 48 <= ord(
                current_character) <= 48 + 9:  # this means current_character is A-Za-z0-9
            self.current_token_string += current_character
        else:
            token_found_bool = True
            found_token = Token(TokenType.KEYWORD if self.current_token_string in KEYWORDS else TokenType.ID,
                                self.current_token_string)  # the token type is set to ID or KEYWORD based on its content
            self.move_pointer_back(current_character)
        return token_found_bool, found_token

    def switch_case_on_q16_state(self, current_character):
        token_found_bool = True
        found_token = Token(TokenType.SYMBOL, self.current_token_string)
        self.move_pointer_back(current_character)
        return token_found_bool, found_token

    def switch_case_on_q18_state(self, current_character):
        if current_character == '=':
            self.current_token_string += current_character
            token_found_bool = True
            found_token = Token(TokenType.SYMBOL, self.current_token_string)  # self.current_token_string = '=='
        else:
            token_found_bool = True
            found_token = Token(TokenType.SYMBOL, self.current_token_string)  # self.current_token_string = '='
            self.move_pointer_back(current_character)
        return token_found_bool, found_token

    def consider_token_at_eof(self):
        # Here, we don't put token_found_bool = True. We assume the method that called this already knows we are at EOF, so token_found_bool = True
        # Here, we don't self.pointer -= 1. We assume the method that called this already knows self.pointer >= len(self.text) so it won't read next characters, there isn't any.
        if self.q_state == 1:
            found_token = Token(TokenType.NUM, self.current_token_string)  # NUM
        elif self.q_state == 3:
            found_token = Token(TokenType.KEYWORD if self.current_token_string in KEYWORDS else TokenType.ID,
                                self.current_token_string)  # ID or KEYWORD
        elif self.q_state == 21:
            found_token = Token(TokenType.SYMBOL, self.current_token_string)  # SYMBOL: '/'
        elif self.q_state in [23, 24, 25]:
            found_token = Token(TokenType.COMMENT,
                                self.current_token_string)  # This means self.current_token_string = '/*', or '/**' or '//' we are assuming this is COMMENT
        else:
            found_token = Token(TokenType.EOF, '$')
        return found_token

    def get_next_token(self) -> Token:
        token_found_bool = False
        self.q_state = 0
        self.current_token_string = ''
        found_token = None
        while not token_found_bool:
            if self.pointer >= self.eof_pointer:
                # Here, we should check that the last token be automatically taken as a terminating state.
                # e.g. If " abc" is at the end of document, we get stuck in q_state = 3 and "abc" will not be saved as a token.
                self.handle_error(None)
                found_token = self.consider_token_at_eof()
                if found_token.type == TokenType.EOF:
                    self.save_tokens_table()
                    self.save_errors_table()
                    self.save_symbols_table()
                    self.scan_is_ended = True
                token_found_bool = True
            else:
                current_character = self.text[self.pointer]
                error_happened = self.handle_error(current_character)
                if error_happened:
                    continue
                if current_character == '\n':
                    self.line_number += 1
                if self.q_state == 0:
                    terminating_state, terminating_token = self.switch_case_on_q0_state(current_character)
                    if terminating_state:
                        token_found_bool = True
                        found_token = terminating_token
                elif self.q_state == 1:
                    terminating_state, terminating_token = self.switch_case_on_q1_state(current_character)
                    if terminating_state:
                        token_found_bool = True
                        found_token = terminating_token
                elif self.q_state == 3:
                    terminating_state, terminating_token = self.switch_case_on_q3_state(current_character)
                    if terminating_state:
                        token_found_bool = True
                        found_token = terminating_token
                elif self.q_state == 16:
                    terminating_state, terminating_token = self.switch_case_on_q16_state(current_character)
                    if terminating_state:
                        token_found_bool = True
                        found_token = terminating_token
                elif self.q_state == 18:
                    terminating_state, terminating_token = self.switch_case_on_q18_state(current_character)
                    if terminating_state:
                        token_found_bool = True
                        found_token = terminating_token
                elif self.q_state in [21, 23, 24, 25]:
                    terminating_state, terminating_token = self.switch_case_on_comments(current_character)
                    if terminating_state:
                        token_found_bool = True
                        found_token = terminating_token
                self.pointer += 1
        if not self.scan_is_ended:
            if found_token.type not in [TokenType.WHITESPACE, TokenType.COMMENT]:
                # Because we want to update self.tokens_table, we should exclude COMMENT and WHITESPACE
                self.update_tokens_table(found_token)
                if found_token.type == TokenType.ID and found_token.string not in self.symbols:
                    self.update_symbols_table(found_token.string)
        return found_token

    def update_tokens_table(self, token: Token):
        if self.tokens_table.split('\n')[-1].startswith(str(self.line_number)):
            self.tokens_table += f' ({token.type}, {token.string})'
        else:
            if self.tokens_table:
                self.tokens_table += '\n'
            self.tokens_table += f'{self.line_number}.\t({token.type}, {token.string})'

    def update_errors_table(self, string, error_message, line_number=None):
        if not line_number:
            line_number = self.line_number
        if len(string) > 7:
            string = string[:7] + '...'
        if self.errors_table.split('\n')[-1].startswith(str(line_number)):
            self.errors_table += f' ({string}, {error_message})'
        else:
            if self.errors_table:
                self.errors_table += '\n'
            self.errors_table += f'{line_number}.\t({string}, {error_message})'

    def update_symbols_table(self, string):
        self.symbols_table += f'{self.symbols_table_counter}.\t{string}\n'
        self.symbols_table_counter += 1
        self.symbols.append(string)

    def handle_error(self, current_character):

        # check for unclosed comment error
        if current_character is None and self.q_state in [23, 24]:
            self.update_errors_table(self.current_token_string, 'Unclosed comment', self.comment_start_line)
        elif current_character is None:
            return False
        # check for Invalid input
        # note that there could be invalid input inside of a comment! :)
        if self.q_state not in [23, 24, 25] and current_character not in ACCEPTABLE_CHARS:
            self.update_errors_table(self.current_token_string + current_character, 'Invalid input')
            self.pointer += 1
            self.q_state = 0
            self.current_token_string = ''
            return True

        # check for Invalid number (eg: 125d)
        if self.q_state == 1 and (65 <= ord(current_character) <= 65 + 25 or 97 <= ord(current_character) <= 97 + 25):
            self.update_errors_table(self.current_token_string + current_character, 'Invalid number')
            self.pointer += 1
            self.q_state = 0
            self.current_token_string = ''
            return True

        # check for unmatched comment
        if self.q_state == 16 and current_character == '/':
            self.update_errors_table(self.current_token_string + current_character, 'Unmatched comment')
            self.pointer += 1
            self.q_state = 0
            self.current_token_string = ''
            return True
        return False

    def save_tokens_table(self):
        with open(self.tokens_file_name, 'w') as f:
            f.write(self.tokens_table)

    def save_errors_table(self):
        if not self.errors_table:
            self.errors_table = 'There is no lexical error'
        with open(self.errors_file_name, 'w') as f:
            f.write(self.errors_table)

    def save_symbols_table(self):
        with open(self.symbol_table_file_name, 'w') as f:
            f.write(self.symbols_table)
