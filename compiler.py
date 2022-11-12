#This is a c-minus compiler program written by
# Parham Bateni     Student number: 99105294
# Pooya EsmaeilAkhoondi       Student number: 99109303
# Alireza Norouzi       Student number:
# as the project of Compiler Design course held at Sharif University of Technology at Fall semester of 2022-2023

INPUT_FILE_NAME='input.txt'
TOKENS_FILE_NAME='tokens.txt'
ERRORS_FILE_NAME='lexical_errors.txt'
SYMBOL_TABLE_FILE_NAME='symbol_table.txt'

## pooya code
TOKEN_TYPES = ['NUM', 'ID', 'KEYWORD', 'SYMBOL', 'COMMENT', 'WHITESPACE']
## pooya code

class Token:
    def __init__(self,type,string):
        self.type=type
        self.string=string

class Scanner:
    def __init__(self,text):
        self.text=text
        self.pointer=0
        self.current_token_string=''
        self.eof_pointer=len(text)
        self.line_number=0
        self.scan_is_ended=False
        self.q_state=0

        self.tokens_table= 'lineno\tRecognized Tokens\n'
        self.errors_table= 'lineno\tError Message\n'
        self.symbols_table= 'no\tlexeme\n'

    ## pooya code
    def recognize_keyword_from_id(self, token)->Token:
        if token == None:
            return token
        if token.type == 'ID':
            if token.string in ['if', 'else', 'void', 'int', 'while', 'break', 'switch', 'default', 'case', 'return', 'endif']:
                token.type = 'KEYWORD'
        return token

    def switch_case_on_q0_state(self, current_character):
        token_found_bool = False
        found_token = None
        if 48 <= ord(current_character) <= 48 + 9:  # this means current_character is 0-9
            self.q_state = 1
            self.current_token_string += current_character
        elif 65 <= ord(current_character) <= 65 + 25 or 97 <= ord(current_character) <= 97 + 25:
            self.q_state = 3
            self.current_token_string += current_character
        elif current_character in [';', ':', ',', '[', ']', '(', ')', '{', '}']:
            self.current_token_string += current_character
            token_found_bool = True
            found_token = Token(TOKEN_TYPES[3], self.current_token_string)
        elif current_character in ['+', '-', '*', '<', '>', '=']:
            self.q_state = 14 # It can be 17, 20, 23, 26, 29 too. No different :)
            self.current_token_string += current_character
        elif current_character in [' ', '\n', '\r', '\t', '\v', '\f']:
            token_found_bool = True
            # We create the token here, and set token_found_bool = True, but the method that actually called this should take care not to take this token seriously. :)
            self.current_token_string += current_character
            found_token = Token(TOKEN_TYPES[5], self.current_token_string)
            if current_character == '\n':
                self.tokens_table += '\n'
                # this line is extremely important. Discussion:
                # self.tokens_table is a string, and we always use tokens_table += some_other_string using self.update_tokens_table method
                # so basically, self.tokens_table would be just one line.
                # Since we actually want relevant tokens for each line to be printed in the corresponding lines, we should add \n to self.tokens_table too.
                # We assume every \n in self.text is equivalent to a necessary \n in self.tokens_table
        elif current_character == '/':
            self.q_state = 32
            self.current_token_string += current_character

        return token_found_bool, found_token

    def switch_case_on_half_symbol_states(self, current_character): # use this when currently q_state is in [14, 17, 20, 23, 26, 29]
        token_found_bool = False
        found_token = None
        if current_character == '=':
            self.current_token_string += current_character
            token_found_bool = True
            found_token = Token(TOKEN_TYPES[3], self.current_token_string)  # self.current_token_string = '=='
        else:
            token_found_bool = True
            found_token = Token(TOKEN_TYPES[3], self.current_token_string)  # self.current_token_string = '='
            self.pointer -= 1
        return token_found_bool, found_token

    def switch_case_on_comments(self, current_character): # this part checks both for comments and misleading symbols, /=
        token_found_bool = False
        found_token = None
        if self.q_state == 32:
            if current_character == '/':
                self.current_token_string += current_character
                self.q_state = 37
            elif current_character == '*':
                self.current_token_string += current_character
                self.q_state = 35
            elif current_character == '=':
                self.current_token_string += current_character
                token_found_bool = True
                found_token = Token(TOKEN_TYPES[3], self.current_token_string)  # self.current_token_string = '/='
            else:
                token_found_bool = True
                found_token = Token(TOKEN_TYPES[3], self.current_token_string)  # self.current_token_string = '/'
                self.pointer -= 1
        elif self.q_state == 35:
            if current_character == '*':
                self.q_state = 36
                self.current_token_string += current_character
            else:
                self.current_token_string += current_character
        elif self.q_state == 36:
            if current_character == '/':
                self.current_token_string += current_character
                token_found_bool = True
                found_token = Token(TOKEN_TYPES[4], self.current_token_string)  # self.current_token_string = '/* some comments */'
            else:
                self.q_state = 35
                self.current_token_string += current_character
        elif self.q_state == 37:
            if current_character == '\n':  # or EOF
                token_found_bool = True
                found_token = Token(TOKEN_TYPES[4], self.current_token_string)  # self.current_token_string = '/* some comments */'
            else:
                self.current_token_string += current_character
        return token_found_bool, found_token
    def switch_case_on_q1_state(self, current_character):
        token_found_bool = False
        found_token = None
        if 48 <= ord(current_character) <= 48 + 9:  # this means current_character is 0-9
            self.current_token_string += current_character
        else:
            # self.q_state = 2
            token_found_bool = True
            found_token = Token(TOKEN_TYPES[0], self.current_token_string)
            #self.update_tokens_table(found_token)
            self.pointer -= 1
        return token_found_bool, found_token

    def switch_case_on_q3_state(self, current_character):
        token_found_bool = False
        found_token = None
        if 65 <= ord(current_character) <= 65 + 25 or 97 <= ord(current_character) <= 97 + 25 or 48 <= ord(current_character) <= 48 + 9:  # this means current_character is A-Za-z0-9
            self.current_token_string += current_character
        else:
            token_found_bool = True
            found_token = Token(TOKEN_TYPES[1], self.current_token_string)  # actually, where this is really ID or KEYWORD should be handled later, for now, it is ID
            #self.update_tokens_table(found_token)
            self.pointer -= 1
        return token_found_bool, found_token

    def consider_token_at_eof(self):
        # Here, we don't token_found_bool = True. We assume the method that called this already knows we are at EOF, so token_found_bool = True
        # Here, we don't self.pointer -= 1. We assume the method that called this already knows self.pointer >= len(self.text) so it won't read next characters, there aren't any.
        found_token = None
        if self.q_state == 1:
            found_token = Token(TOKEN_TYPES[0], self.current_token_string) # NUM
        elif self.q_state == 3:
            found_token = Token(TOKEN_TYPES[1], self.current_token_string) # ID or KEYWORD
            found_token = self.recognize_keyword_from_id(found_token)      # Finalizing the type
        elif self.q_state in [14, 17, 20, 23, 26, 29]:
            found_token = Token(TOKEN_TYPES[3], self.current_token_string) # SYMBOL
        elif self.q_state == 32:
            found_token = Token(TOKEN_TYPES[3], self.current_token_string)  # This means self.current_token_string = '/'
        elif self.q_state == 35:
            found_token = Token(TOKEN_TYPES[4], self.current_token_string)  # This means self.current_token_string = '/*', we are assuming this is COMMENT
        elif self.q_state == 36:
            found_token = Token(TOKEN_TYPES[4], self.current_token_string)  # This means self.current_token_string = '/**', we are assuming this is COMMENT
        elif self.q_state == 37:
            found_token = Token(TOKEN_TYPES[4], self.current_token_string)  # This means self.current_token_string = '//', we are assuming this is COMMENT
        if found_token is not None:
            if found_token.type in [TOKEN_TYPES[0], TOKEN_TYPES[1], TOKEN_TYPES[3]]: # This is because we shouldn't include COMMENT and WHITESPACE in self.tokens_table
                self.update_tokens_table(found_token)
        return found_token

    def get_next_token(self)->Token:
        ## pooya code
        token_found_bool = False
        self.scan_is_ended = False
        self.q_state = 0
        self.current_token_string = ''
        found_token = None
        while not token_found_bool:
            if self.pointer >= self.eof_pointer:
                # Here, we should check that the last token be automatically be taken as a terminating state.
                # e.g. If " abc" is at the end of document, we get stuck in q_state = 3 and "abc" will not be saved as a token.
                found_token = self.consider_token_at_eof()
                self.save_tokens_table()
                self.save_errors_table()
                self.save_symbols_table()
                self.scan_is_ended = True
                token_found_bool = True
            else:
                current_character = self.text[self.pointer]
                if self.q_state == 1:
                    terminating_state, terminating_token = self.switch_case_on_q1_state(current_character)
                    if terminating_state:
                        token_found_bool = True
                        found_token = terminating_token
                elif self.q_state == 3:
                    terminating_state, terminating_token = self.switch_case_on_q3_state(current_character)
                    if terminating_state:
                        token_found_bool = True
                        found_token = terminating_token
                elif self.q_state in [14, 17, 20, 23, 26, 29]:
                    terminating_state, terminating_token = self.switch_case_on_half_symbol_states(current_character)
                    if terminating_state:
                        token_found_bool = True
                        found_token = terminating_token
                elif self.q_state in [32, 35, 36, 37]:
                    terminating_state, terminating_token = self.switch_case_on_comments(current_character)
                    if terminating_state:
                        token_found_bool = True
                        found_token = terminating_token
                else: # entering this case means we are in q_state = 0
                    terminating_state, terminating_token = self.switch_case_on_q0_state(current_character)
                    if terminating_state:
                        token_found_bool = True
                        found_token = terminating_token
                self.pointer += 1
        if found_token is not None and not self.scan_is_ended: # I think there is only one case where found_token = None at this point. This is:
                                    # 1) We have reached EOF, then we just need to terminate program, no updating tokens
                                    # We also check if self.scan_is_ended = False because if it is True, everything would have ben handled before.
            if found_token.type not in [TOKEN_TYPES[4], TOKEN_TYPES[5]]: # Because we want to update self.tokens_table, we should exclude COMMENT and WHITESPACE
                found_token = self.recognize_keyword_from_id(found_token)
                self.update_tokens_table(found_token)
        return found_token
        ## pooya code

    def update_tokens_table(self,token:Token):
        self.tokens_table+=f'({token.type},{token.string})'

    def update_errors_table(self,string,error_message):
        if len(string)>7:
            string=string[:7]+'...'
        self.errors_table+= f'{self.line_number}\t({string},{error_message})\n'

    def update_symbols_table(self,string):
        self.symbols_table += string
        #self.symbols_table.append((len(self.symbols_table + 1), string))

    def handle_error(self):
        # todo: Error handling
        pass

    def save_tokens_table(self):
        with open(TOKENS_FILE_NAME,'w') as f:
            f.write(self.tokens_table)

    def save_errors_table(self):
        if self.errors_table=='lineno\tError Message\n':
            self.errors_table='There is no lexical error'
        with open(ERRORS_FILE_NAME,'w') as f:
            f.write(self.errors_table)

    def save_symbols_table(self):
        with open(SYMBOL_TABLE_FILE_NAME,'w') as f:
            f.write(self.symbols_table)

if __name__ == '__main__':
    code=open('input.txt','r').read()
    scanner=Scanner(code)
    #print(code)
    while not scanner.scan_is_ended:
        token=scanner.get_next_token()
        if token is not None:
            print("token: type = ", token.type, " string = ", token.string)
    print(scanner.tokens_table, end='')
        # parse the token to parser in the next phase
