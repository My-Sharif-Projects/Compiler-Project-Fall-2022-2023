INPUT_FILE_NAME='input.txt'
TOKENS_FILE_NAME='tokens.txt'
ERRORS_FILE_NAME='lexical_errors.txt'
SYMBOL_TABLE_FILE_NAME='symbol_table.txt'

class Token:
    def __init__(self,type,string):
        self.type=type
        self.string=string

class Scanner:
    def __init__(self,text):
        self.text=text
        self.pointer=0
        self.current_token_string=''
        self.eof_pointer=len(text)-1
        self.line_number=0
        self.scan_is_ended=False

        self.tokens_table= 'lineno\tRecognized Tokens\n'
        self.errors_table= 'lineno\tError Message\n'
        self.symbols_table= 'no\tlexeme\n'
    def get_next_token(self)->Token:
        if self.pointer==self.eof_pointer:
            #try tokenizing self.current_token_string
            # update error table if there is an unclosed comment
            self.save_tokens_table()
            self.save_errors_table()
            self.save_symbols_table()
            self.scan_is_ended=True

            # return token

        #todo: when approaching a \n
        # self.tokens_table+='\n'
        self.pointer+=1

        #return token
    def update_tokens_table(self,token:Token):
        self.tokens_table+=f'({token.type},{token.string})'
    def update_errors_table(self,string,error_message):
        if len(string)>7:
            string=string[:7]+'...'
        self.errors_table+= f'{self.line_number}\t({string},{error_message})\n'
    def update_symbols_table(self,string):
        self.symbols_table.append((len(self.symbols_table + 1), string))
    def handle_error(self):
        # todo: Error handling
        pass
    def save_tokens_table(self):
        with open(SYMBOL_TABLE_FILE_NAME,'w') as f:
            f.write(self.symbols_table)
    def save_errors_table(self):
        if self.errors_table=='lineno\tError Message\n':self.errors_table='There is no lexical error'
        with open(ERRORS_FILE_NAME,'w') as f:
            f.write(self.errors_table)
    def save_symbols_table(self):
        with open(SYMBOL_TABLE_FILE_NAME,'w') as f:
            f.write(self.symbols_table)



if __name__ == '__main__':
    code=open('input.txt','r').read()
    scanner=Scanner(code)
    print(code)
    while not scanner.scan_is_ended:
        token=scanner.get_next_token()
        # parse the token to parser in the next phase









