# https://ply.readthedocs.io/en/latest/ply.html#yacc
# parser usando ply.yacc

import ply.yacc as yacc
from lexer import tokens # tokens del otro archivo

# reglas gramaticales
# todos los tokens van en mayúsculas

def p_ASSIGN(p):
    '''
        ASSIGN : ID = EXPRESSION ;
    '''
    # aquí uso '=' y ';' porque es un literal token

def p_BODY(p):
    '''
        BODY : { body_STATEMENTS }
    '''
    # cero o más statements

def body_STATEMENTS(p):
    '''
        body_STATEMENTS : body_STATEMENTS STATEMENT
                        | empty
    '''
    # aquí uso 'STATEMENT' y 'body_STATEMENTS' porque son tokens
    # empty va después del otro porque en Ply el orden importa
    # body_STATEMENTS es recursivo a la izquierda, porque Ply es un parser LALR(1) y es bottom-up

def p_CONDITION(p):
    '''
        CONDITION : IF ( EXPRESSION ) else_CONDITION ;
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
        CYCLE : WHILE ( EXPRESSION ) DO STATEMENT ;
    '''

def p_EXP(p):
    '''
        EXP : TERMINO terminos_EXP
    '''

def p_terminos_EXP(p):
    '''
        terminos_EXP : + TERMINO terminos_EXP
                     | - TERMINO terminos_EXP
                     | empty
    '''

def p_EXPRESION(p):
    '''
        EXPRESION : EXP
                  | EXP > EXP
                  | EXP < EXP
                  | EXP NEQ EXP
    '''

def p_FCALL(p):
    '''
        FCALL : ID ( expresiones_FCALL ) ;
    '''

def p_expresiones_FCALL(p):
    '''
        expresiones_FCALL : EXPRESION
                          | EXPRESION , expresiones_FCALL
    '''

def p_FACTOR(p):
    '''
        FACTOR : FCALL
               | ( EXPRESION )
               | left_FACTOR ID
               | left_FACTOR CTE
    '''

def p_left_FACTOR(p):
    '''
        left_FACTOR : - 
                    | +
                    | empty
    '''

def p_FUNCS(p):
    '''
        FUNCS : LEFT_FUNCS ID ( id_FUNCS ) [ vars_FUNCS ] BODY ;
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
        ids_FUNCS : ID : TYPE
                  | ids_FUNCS , ID : TYPE
    '''

def p_vars_FUNCS(p):
    '''
        vars_FUNCS : VARS
                   | empty
    '''

def p_PRINT(p):
    '''
        PRINT : PRINT ( printable_PRINT ) ;
    '''

def p_printable_PRINT(p):
    '''
        printable_PRINT : EXPRESION
                        | CTE_STRING
                        | printable_PRINT , EXPRESION
                        | printable_PRINT , CTE_STRING
    '''

def p_programa(p):
    '''
        PROGRAMA : PROGRAM ID ; vars_PROGRAMA funcs_PROGRAMA MAIN BODY END
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

def p_READ(p):
    '''
        READ : READ ( ID ) ;
    '''

def p_STATEMENT(p):
    '''
        STATEMENT : ASSIGN
                  | CONDITION
                  | CYCLE
                  | PRINT
                  | READ
                  | RETURN
                  | [ mult_STATEMENT ]
    '''

def p_mult_STATEMENT(p):
    '''
        mult_STATEMENT : STATEMENT mult_STATEMENT
                       | empty
    '''

def p_RETURN(p):
    '''
        RETURN : RETURN EXPRESION ;
    '''

def p_TERMINO(p):
    '''
        TERMINO : FACTOR
                | FACTOR * TERMINO
                | FACTOR / TERMINO
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
                 | ID , ids_VARS
    '''

def p_right_VARS(p):
    '''
        right_VARS : ids_VARS : TYPE ;
                   | ids_VARS : TYPE ; right_VARS
    '''

def p_empty(p):
    '''
        empty :
    '''
    pass