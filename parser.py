# https://ply.readthedocs.io/en/latest/ply.html#yacc
# parser usando ply.yacc

import ply.yacc as yacc
from lexer import tokens, literals
import semantic
from semantic import *

start = 'PROGRAMA'


def p_ASSIGN(p):
    '''
        ASSIGN : ID '=' EXPRESION ';'
    '''
    tipo_destino = obtener_tipo_variable(p[1])
    tipo_resultado = oraculo_cubo(tipo_destino, p[3], '=')
    if tipo_resultado != tipo_destino:
        raise Exception(
            f"Error semántico: no se puede asignar {p[3]} a {tipo_destino} en '{p[1]}'"
        )


def p_BODY(p):
    '''
        BODY : '{' body_STATEMENTS '}'
    '''


def p_body_STATEMENTS(p):
    '''
        body_STATEMENTS : body_STATEMENTS STATEMENT
                        | empty
    '''


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
            | CTE_STRING
    '''
    if p.slice[1].type == 'CTE_INT':
        p[0] = 'int'
    elif p.slice[1].type == 'CTE_FLOAT':
        p[0] = 'float'
    else:
        p[0] = 'string'


def p_CYCLE(p):
    '''
        CYCLE : WHILE '(' EXPRESION ')' DO STATEMENT ';'
    '''


def p_EXP(p):
    '''
        EXP : TERMINO terminos_EXP
    '''
    tipo = p[1]
    for operador, tipo_derecho in p[2]:
        tipo = oraculo_cubo(tipo, tipo_derecho, operador)
        crear_temporal(tipo)
    p[0] = tipo


def p_terminos_EXP(p):
    '''
        terminos_EXP : '+' TERMINO terminos_EXP
                     | '-' TERMINO terminos_EXP
                     | empty
    '''
    if len(p) == 4:
        p[0] = [(p[1], p[2])] + p[3]
    else:
        p[0] = []


def p_EXPRESION(p):
    '''
        EXPRESION : EXP
                  | EXP '>' EXP
                  | EXP '<' EXP
                  | EXP NEQ EXP
    '''
    if len(p) == 2:
        p[0] = p[1]
        return
    operador = '!=' if p.slice[2].type == 'NEQ' else p[2]
    p[0] = oraculo_cubo(p[1], p[3], operador)
    crear_temporal(p[0])


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
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]


def p_FACTOR(p):
    '''
        FACTOR : FCALL
               | '(' EXPRESION ')'
               | ID
               | '+' ID
               | '-' ID
               | CTE
               | '+' CTE
               | '-' CTE
    '''
    if len(p) == 2 and p.slice[1].type == 'FCALL':
        p[0] = p[1]
    elif len(p) == 4:
        p[0] = p[2]
    elif len(p) == 2 and p.slice[1].type == 'ID':
        p[0] = obtener_tipo_variable(p[1])
    elif len(p) == 2:
        p[0] = p[1]
    elif p.slice[2].type == 'ID':
        p[0] = obtener_tipo_variable(p[2])
    else:
        p[0] = p[2]
    if len(p) == 3 and p[1] in ('+', '-') and p[0] not in ('int', 'float'):
        raise Exception(f"Error semántico: signo unario inválido para {p[0]}")


def p_FUNCS(p):
    '''
        FUNCS : LEFT_FUNCS ID iniciar_funcion '(' id_FUNCS ')' '[' vars_FUNCS ']' BODY ';'
    '''
    finalizar_funcion()

def p_iniciar_funcion(p):
    '''
        iniciar_funcion : empty
    '''
    iniciar_funcion(p[-1], p[-2])


def p_LEFT_FUNCS(p):
    '''
        LEFT_FUNCS : VOID
                   | TYPE
    '''
    p[0] = 'void' if p.slice[1].type == 'VOID' else p[1]


def p_id_FUNCS(p):
    '''
        id_FUNCS : ids_FUNCS
                 | empty
    '''
    parametros = p[1] if p[1] is not None else []
    registrar_parametros(parametros)
    p[0] = parametros


def p_ids_FUNCS(p):
    '''
        ids_FUNCS : ID ':' TYPE
                  | ids_FUNCS ',' ID ':' TYPE
    '''
    if len(p) == 4:
        p[0] = [(p[1], p[3])]
    else:
        p[0] = p[1] + [(p[3], p[5])]


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
                        | printable_PRINT ',' EXPRESION
    '''


def p_programa(p):
    '''
        PROGRAMA : PROGRAM ID ';' iniciar_programa vars_PROGRAMA funcs_PROGRAMA MAIN BODY END finalizar_programa
    '''


def p_iniciar_programa(p):
    '''
        iniciar_programa : empty
    '''
    iniciar_programa(p[-2])


def p_finalizar_programa(p):
    '''
        finalizar_programa : empty
    '''
    finalizar_programa()


def p_vars_PROGRAMA(p):
    '''
        vars_PROGRAMA : VARS
                      | empty
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
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]


def p_right_VARS(p):
    '''
        right_VARS : ids_VARS ':' TYPE ';'
                   | ids_VARS ':' TYPE ';' right_VARS
    '''
    for nombre in p[1]:
        agregar_variable_declarada(nombre, p[3])


def p_funcs_PROGRAMA(p):
    '''
        funcs_PROGRAMA : FUNCS funcs_PROGRAMA
                       | empty
    '''


def p_read_statement(p):
    '''
        read_statement : READ '(' ID ')' ';'
    '''
    obtener_tipo_variable(p[3])


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
    if semantic.funcion_actual is None:
        raise Exception("Error semántico: return solo se permite dentro de una función")
    tipo_retorno = get_function_return_type(semantic.funcion_actual)
    if p[2] != tipo_retorno:
        raise Exception(
            f"Error semántico: la función '{semantic.funcion_actual}' debe retornar {tipo_retorno}, no {p[2]}"
        )


def p_TERMINO(p):
    '''
        TERMINO : FACTOR
                | FACTOR '*' TERMINO
                | FACTOR '/' TERMINO
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = oraculo_cubo(p[1], p[3], p[2])
        crear_temporal(p[0])


def p_TYPE(p):
    '''
        TYPE : INT
             | FLOAT
             | STRING
    '''
    if p.slice[1].type == 'INT':
        p[0] = 'int'
    elif p.slice[1].type == 'FLOAT':
        p[0] = 'float'
    else:
        p[0] = 'string'


def p_empty(p):
    '''
        empty :
    '''
    p[0] = None


def p_error(p):
    if p:
        print(f"Error de sintaxis en la línea {p.lineno}: token inesperado '{p.value}'")
    else:
        print("Error de sintaxis: fin de archivo inesperado")


parser = yacc.yacc()
