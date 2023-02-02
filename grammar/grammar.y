%token NUM
%token ID
%start program
%%
program: declaration_list
;
declaration_list: declaration_list declaration
| declaration
;
declaration: var_declaration 
| fun_declaration 
;
var_declaration: type_specifier PID ID ';' Declare
| type_specifier PID ID '[' Num ']' ';' Array_declare
;
type_specifier: "int" 
| "void"
;
fun_declaration: type_specifier PID ID '(' params ')' compound_stmt
;
params: param_list
| "void"
;
param_list: param_list ',' param
| param
;
param: type_specifier PID ID
| type_specifier PID ID '[' ']'
;
compound_stmt: Add_scope '{' local_declarations statement_list '}' Reduce_scope
;
local_declarations: local_declarations var_declaration
| /* epsilon */
;
statement_list: statement_list statement
| /* epsilon */
;
statement: expression_stmt
| compound_stmt
| selection_stmt
| iteration_stmt
| return_stmt
| switch_stmt
| output_stmt
;
expression_stmt: expression ';' Mark_assignment
| "break" ';' Break
| ';'
;
selection_stmt: "if" '(' expression ')' Save statement "endif" Jpf
| "if" '(' expression ')' Save statement "else" Jpf_save statement Jp "endif"
;
iteration_stmt: Jmp_save "while" Label '(' expression ')' Save statement While
;
return_stmt: "return" ';'
| "return" expression ';'
;
switch_stmt: Jmp_save "switch" '(' expression ')' Add_scope '{' "case" Num Eq_switch ':' Save statement_list case_stmts default_stmt '}' Switch_Jmp
| Jmp_save "switch" '(' expression ')' Add_scope '{' "default" ':' statement_list '}' Switch_Jmp
;
case_stmts: case_stmts case_stmt
| /* epsilon */
;
case_stmt: Jpf "case" Num Eq_switch ':' Save statement_list
;
default_stmt: Jpf "default" ':' statement_list
| /* epsilon */
;
expression: var '=' expression Assign
| simple_expression
;
var: PID ID
| PID ID '[' expression ']' Array_access
;
simple_expression: additive_expression lt additive_expression Lt
| additive_expression eq additive_expression Eq
| additive_expression
;
lt: '<'
;
additive_expression: additive_expression addop term Add
| additive_expression subop term Sub
| term
;
output_stmt: "output" '(' simple_expression ')' ';' Print
;
term: term mulop factor Mult
| term divop factor Div
| factor
;
eq: "=="
;
factor: '(' expression ')'
| var
| call
| Num
;
call: PID ID '(' args ')'
;
args: arg_list
| /* epsilon */
;
arg_list: arg_list ',' expression
| expression
;
addop: '+'
;
subop: '-'
;
mulop: '*'
;
divop: '/'
;
PID: /* epsilon */
;
Assign: /* epsilon */
;
Add: /* epsilon */
;
Sub: /* epsilon */
;
Mult: /* epsilon */
;
Div: /* epsilon */
;
While: /* epsilon */
;
Label: /* epsilon */
;
Save: /* epsilon */
;
Jpf: /* epsilon */
;
Jp: /* epsilon */
;
Jpf_save: /* epsilon */
;
Print: /* epsilon */
;
Lt: /* epsilon */
;
Eq: /* epsilon */
;
Declare: /* epsilon */
;
Num: Save_constant NUM
;
Save_constant: /* epsilon */
;
Array_declare: /* epsilon */
;
Array_access: /* epsilon */
;
Jmp_save: /* epsilon */
;
Eq_switch: /* epsilon */
;
Break: /* epsilon */
;
Switch_Jmp: /* epsilon */
;
Add_scope: /* epsilon */
;
Reduce_scope: /* epsilon */
;
Mark_assignment: /* epsilon */
;
%%
