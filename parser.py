# https://ply.readthedocs.io/en/latest/ply.html#yacc
# parser usando ply.yacc

import ply.yacc as yacc
from lexer import tokens, literals
import cuadruplos as q
import semantic
from semantic import *

start = 'PROGRAMA'


def p_ASSIGN(p):
    '''
        ASSIGN : ID '=' EXPRESION ';'
    '''
    # Sacar el operando de la expresión y el tipo de la variable
    valor, tipo_valor = q.pop_operando()
    tipo_destino = obtener_tipo_variable(p[1])
    # comprueba compatibilidad
    tipo_resultado = oraculo_cubo(tipo_destino, tipo_valor, '=')
    if tipo_resultado != tipo_destino:
        raise Exception(
            f"Error semántico: no se puede asignar {tipo_valor} a {tipo_destino} en '{p[1]}'"
        )
    # meter el cuádruplo de asignación
    q.push_cuadruplo('=', valor, None, p[1])

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
        tipo = 'int'
    elif p.slice[1].type == 'CTE_FLOAT':
        tipo = 'float'
    else:
        tipo = 'string'

    q.push_operando(p[1], tipo)


def p_CYCLE(p):
    '''
        CYCLE : WHILE '(' EXPRESION ')' DO STATEMENT ';'
    '''


def p_EXP(p):
    '''
        EXP : TERMINO
            | EXP operador_aditivo TERMINO
    '''
    # resolver la expresión si hay un operador aditivo
    if len(p) == 4:
        q.resolver_expresion(('+', '-'))


def p_operador_aditivo(p):
    '''
        operador_aditivo : '+'
                         | '-'
    '''
    q.push_operador(p[1])


def p_EXPRESION(p):
    '''
        EXPRESION : EXP
                  | EXP operador_relacional EXP
    '''
    if len(p) == 4:
        q.resolver_expresion(('<', '>', '!='))


def p_operador_relacional(p):
    '''
        operador_relacional : '<'
                            | '>'
                            | NEQ
    '''
    q.push_operador(p[1])


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
    q.pop_operando()


def p_FACTOR(p):
    '''
        FACTOR : FCALL
               | '(' fondo_falso EXPRESION ')'
               | ID
               | '+' ID
               | '-' ID
               | CTE
               | '+' CTE
               | '-' CTE
    '''
    # len 5 es para el caso de los parentesis
    if len(p) == 5:
        # pop el fondo falso más reciente
        q.pop_operador()
        return
        
    # revisar si el último token es un ID
    pos = len(p) - 1
    if p.slice[pos].type == 'ID':
        # si es un ID, obtener su tipo de la tabla de símbolos
        q.push_operando(p[pos], obtener_tipo_variable(p[pos]))

    # si es + ID o - ID, revisar que el tipo sea numérico
    if pos == 2:
        _, tipo = q.top_operando()
        if tipo not in ('int', 'float'):
            raise Exception(f"Error semántico: signo unario inválido para {tipo}")

    # Resolver la expresión si hay un negativo
    if pos == 2 and p[1] == '-':
        q.push_operando(-1, 'int')
        q.push_operador('*')
        q.resolver_expresion(('*',))


def p_fondo_falso(p):
    'fondo_falso :'
    # crear un fondo falso para los paréntesis
    q.push_operador(False)


def p_FUNCS(p):
    '''
        FUNCS : LEFT_FUNCS ID iniciar_funcion '(' id_FUNCS ')' '[' vars_FUNCS ']' BODY ';'
    '''
    # Finalizar la función y limpiar las pilas
    finalizar_funcion()

def p_iniciar_funcion(p):
    '''
        iniciar_funcion : empty
    '''
    # Iniciar la función en el directorio de funciones
    iniciar_funcion(p[-1], p[-2])


def p_LEFT_FUNCS(p):
    '''
        LEFT_FUNCS : VOID
                   | TYPE
    '''
    # Pasar el tipo de retorno a la función iniciar_funcion
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
    # Sacar el operando de la expresión y generar el cuádruplo de impresión
    valor, _ = q.pop_operando()
    q.push_cuadruplo('PRINT', valor, None, None)


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
    # revisar que la variable exista y obtener su tipo
    obtener_tipo_variable(p[3])
    # generar el cuádruplo de lectura
    q.push_cuadruplo('READ', p[3], None, None)


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
    # Sacar el operando de la expresión y su tipo
    _, tipo = q.pop_operando()
    if semantic.funcion_actual is None:
        raise Exception("Error semántico: return solo se permite dentro de una función")
    tipo_retorno = get_function_return_type(semantic.funcion_actual)
    if tipo != tipo_retorno:
        raise Exception(
            f"Error semántico: la función '{semantic.funcion_actual}' debe retornar {tipo_retorno}, no {tipo}"
        )

    # aquí alguna instrucción sobre qué hacer con el retorno

def p_TERMINO(p):
    '''
        TERMINO : FACTOR
                | TERMINO operador_multiplicativo FACTOR
    '''
    # resolver la expresión si hay un operador multiplicativo
    if len(p) == 4:
        q.resolver_expresion(('*', '/'))


def p_operador_multiplicativo(p):
    '''
        operador_multiplicativo : '*'
                                | '/'
    '''
    # Push el operador a la pila de operadores
    q.push_operador(p[1])


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
