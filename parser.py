# https://ply.readthedocs.io/en/latest/ply.html#yacc
# parser usando ply.yacc

import ply.yacc as yacc
from lexer import tokens, literals # tokens del otro archivo

# reglas gramaticales
# todos los tokens van en mayúsculas

start = 'PROGRAMA' # regla inicial

def p_ASSIGN(p):
    '''
        ASSIGN : ID '=' EXPRESION ';'
    '''
    # aquí uso '=' y ';' porque es un literal token

def p_BODY(p):
    '''
        BODY : '{' body_STATEMENTS '}'
    '''
    # cero o más statements

def p_body_STATEMENTS(p):
    '''
        body_STATEMENTS : body_STATEMENTS STATEMENT
                        | empty
    '''
    # aquí uso 'STATEMENT' y 'body_STATEMENTS' porque son tokens
    # empty va después del otro porque en Ply el orden importa
    # body_STATEMENTS es recursivo a la izquierda, porque Ply es un parser LALR(1) y es bottom-up

def p_CONDITION(p):
    '''
        CONDITION : IF '(' EXPRESION ')' STATEMENT else_CONDITION ';'
    '''

def p_else_CONDITION(p):
    '''
        else_CONDITION : ELSE STATEMENT
                       | empty
    '''

def p_CTE(p):
    '''
        CTE : CTE_INT
            | CTE_FLOAT
    '''

def p_CYCLE(p):
    '''
        CYCLE : WHILE '(' EXPRESION ')' DO STATEMENT ';'
    '''

def p_EXP(p):
    '''
        EXP : TERMINO terminos_EXP
    '''

def p_terminos_EXP(p):
    '''
        terminos_EXP : '+' TERMINO terminos_EXP
                     | '-' TERMINO terminos_EXP
                     | empty
    '''

def p_EXPRESION(p):
    '''
        EXPRESION : EXP
                  | EXP '>' EXP
                  | EXP '<' EXP
                  | EXP NEQ EXP
    '''

def p_FCALL(p):
    '''
        FCALL : ID '(' expresiones_FCALL ')' ';'
              | ID '(' ')' ';'
    '''

def p_expresiones_FCALL(p):
    '''
        expresiones_FCALL : EXPRESION
                          | EXPRESION ',' expresiones_FCALL
    '''

def p_FACTOR(p):
    '''
        FACTOR : FCALL
               | '(' EXPRESION ')'
               | left_FACTOR ID
               | left_FACTOR CTE
    '''

def p_left_FACTOR(p):
    '''
        left_FACTOR : '-'
                    | '+'
                    | empty
    '''

def p_FUNCS(p):
    '''
        FUNCS : LEFT_FUNCS ID '(' id_FUNCS ')' '[' vars_FUNCS ']' BODY ';'
    '''

def p_LEFT_FUNCS(p):
    '''
        LEFT_FUNCS : VOID
                   | TYPE
    '''

# vacío, 1, o más
def p_id_FUNCS(p):
    '''
        id_FUNCS : ids_FUNCS
                 | empty
    '''

def p_ids_FUNCS(p):
    '''
        ids_FUNCS : ID ':' TYPE
                  | ids_FUNCS ',' ID ':' TYPE
    '''

def p_vars_FUNCS(p):
    '''
        vars_FUNCS : VARS
                   | empty
    '''

def p_print_statement(p):
    '''
        print_statement : PRINT '(' printable_PRINT ')' ';'
    '''

def p_printable_PRINT(p):
    '''
        printable_PRINT : EXPRESION
                        | CTE_STRING
                        | printable_PRINT ',' EXPRESION
                        | printable_PRINT ',' CTE_STRING
    '''

def p_programa(p):
    '''
        PROGRAMA : PROGRAM ID ';' vars_PROGRAMA funcs_PROGRAMA MAIN BODY END
    '''

def p_vars_PROGRAMA(p):
    '''
        vars_PROGRAMA : VARS
                      | empty
    '''

def p_funcs_PROGRAMA(p):
    '''
        funcs_PROGRAMA : FUNCS funcs_PROGRAMA
                       | empty
    '''

def p_read_statement(p):
    '''
        read_statement : READ '(' ID ')' ';'
    '''

def p_STATEMENT(p):
    '''
        STATEMENT : ASSIGN
                  | CONDITION
                  | CYCLE
                  | FCALL
                  | print_statement
                  | read_statement
                  | return_statement
                  | '[' mult_STATEMENT ']'
    '''

def p_mult_STATEMENT(p):
    '''
        mult_STATEMENT : STATEMENT mult_STATEMENT
                       | empty
    '''

def p_return_statement(p):
    '''
        return_statement : RETURN EXPRESION ';'
    '''

def p_TERMINO(p):
    '''
        TERMINO : FACTOR
                | FACTOR '*' TERMINO
                | FACTOR '/' TERMINO
    '''

def p_TYPE(p):
    '''
        TYPE : INT
             | FLOAT
    '''

def p_VARS(p):
    '''
        VARS : VAR right_VARS
    '''

def p_ids_VARS(p):
    '''
        ids_VARS : ID 
                 | ID ',' ids_VARS
    '''

def p_right_VARS(p):
    '''
        right_VARS : ids_VARS ':' TYPE ';'
                   | ids_VARS ':' TYPE ';' right_VARS
    '''

def p_empty(p):
    '''
        empty :
    '''
    pass

def p_error(p):
    if p:
        print(f"Error de sintaxis en la línea {p.lineno}: token inesperado '{p.value}'")
    else:
        print("Error de sintaxis: fin de archivo inesperado")

parser = yacc.yacc()