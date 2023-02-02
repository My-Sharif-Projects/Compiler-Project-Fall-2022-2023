# This is a c-minus compiler program written by
# Parham Bateni     Student number: 99105294
# Pooya EsmaeilAkhoondi       Student number: 99109303
# as the project of Compiler Design course held at Sharif University of Technology at Fall semester of 2022-2023
# More details on the project can be found at https://github.com/My-Sharif-Projects/Compiler-Project-Fall-2022-2023
from InterCodeGen import InterCodeGen
from Parser import Parser
from Scanner import Scanner

INPUT_FILE_NAME = 'input.txt'
TOKENS_FILE_NAME = 'tokens.txt'
ERRORS_FILE_NAME = 'lexical_errors.txt'
SYMBOL_TABLE_FILE_NAME = 'symbol_table.txt'
SYNTAX_ERROR_FILE_NAME = 'syntax_errors.txt'
PARSE_TREE_FILE_NAME = 'parse_tree.txt'
SLR_TABLE_FILE_NAME = 'table.json'
OUTPUT_FILE_NAME = 'output.txt'
SEMANTIC_ERROR_FILE_NAME = 'semantic_errors.txt'

if __name__ == '__main__':
    try:
        scanner = Scanner(input_file_name=INPUT_FILE_NAME, tokens_file_name=TOKENS_FILE_NAME,
                          errors_file_name=ERRORS_FILE_NAME, symbol_table_file_name=SYMBOL_TABLE_FILE_NAME)
        intermediate_code_generator = InterCodeGen(output_file_name=OUTPUT_FILE_NAME,
                                                   semantic_error_file_name=SEMANTIC_ERROR_FILE_NAME,
                                                   symbol_table=scanner.ids_table)
        parser = Parser(syntax_error_file_name=SYNTAX_ERROR_FILE_NAME, parse_tree_file_name=PARSE_TREE_FILE_NAME,
                        SLR_table_file_name=SLR_TABLE_FILE_NAME, scanner=scanner,
                        inter_code_gen=intermediate_code_generator)
        parser.process()
    except Exception as e:
        print('Error:', e.args)
        input('Compiling failed! Press enter to exit...')
        exit()
