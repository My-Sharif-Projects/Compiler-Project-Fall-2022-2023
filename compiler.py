# This is a c-minus compiler program written by
# Parham Bateni     Student number: 99105294
# Pooya EsmaeilAkhoondi       Student number: 99109303
# as the project of Compiler Design course held at Sharif University of Technology at Fall semester of 2022-2023
# More details on the project can be found at https://github.com/My-Sharif-Projects/Compiler-Project-Fall-2022-2023
from Scanner import Scanner
from Scanner import TokenType

INPUT_FILE_NAME = 'input.txt'
TOKENS_FILE_NAME = 'tokens.txt'
ERRORS_FILE_NAME = 'lexical_errors.txt'
SYMBOL_TABLE_FILE_NAME = 'symbol_table.txt'

if __name__ == '__main__':
    try:
        scanner = Scanner(INPUT_FILE_NAME, TOKENS_FILE_NAME, ERRORS_FILE_NAME, SYMBOL_TABLE_FILE_NAME)
    except Exception as e:
        print(e)
        print('Compiling failed!')
        exit()
    while True:
        token = scanner.get_next_token()
        if token.type != TokenType.EOF:
            # parse the token to parser in the next phase
            pass
        else:
            break
    # print('The program compiled successfully! :))')
