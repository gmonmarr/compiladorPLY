# https://ply.readthedocs.io/en/latest/ply.html#yacc
# parser usando ply.yacc

import ply.yacc as yacc
from lexer import tokens, literals
import cuadruplos as q
import memoria
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
    q.push_cuadruplo('=', valor, None, obtener_direccion_variable(p[1]))

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
        CONDITION : IF '(' EXPRESION ')' condicion_falsa STATEMENT else_CONDITION ';'
    '''
    q.rellenar(q.pila_saltos.pop(), len(q.cuadruplos))


def p_condicion_falsa(p):
    'condicion_falsa :'
    q.salto_falso() # push de cuadruplo GotoF (salto falso) para la condición del if


def p_else_CONDITION(p):
    '''
        else_CONDITION : ELSE salto_else STATEMENT
                       | empty
    '''


def p_salto_else(p):
    'salto_else :'
    falso = q.pila_saltos.pop() # obtener lineno. del salto falso del if
    q.pila_saltos.append(q.push_cuadruplo('GOTO', None, None, None)) # push de Goto para el else
    q.rellenar(falso, len(q.cuadruplos)) # rellenar el gotof del if con el salto para el else

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

    q.push_operando(memoria.constante(p[1], tipo), tipo)


def p_CYCLE(p):
    '''
        CYCLE : WHILE inicio_ciclo '(' EXPRESION ')' condicion_falsa DO STATEMENT ';'
    '''
    falso = q.pila_saltos.pop() # obtener el lineno. gotof del while
    inicio = q.pila_saltos.pop() # obtener el lineno. del inicio del while
    q.push_cuadruplo('GOTO', None, None, inicio) # push de Goto para regresar al inicio del while
    q.rellenar(falso, len(q.cuadruplos)) # rellenar el gotof del while con el salto para salir del while


def p_inicio_ciclo(p):
    'inicio_ciclo :'
    q.pila_saltos.append(len(q.cuadruplos)) # push del lineno. del inicio del while 


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
        FCALL : llamada ';'
    '''


def p_llamada(p):
    '''
        llamada : ID '(' iniciar_llamada argumentos ')'
    '''
    # punto neuráligo 5 y 6 de FunctionCall
    # este código corre después de que se han procesado los argumentos y se ha generado el cuádruplo de GOSUB
    nombre, cantidad = q.pila_llamadas.pop() # pop de la pila de llamadas el nombre de la función y la cantidad de argumentos que se registraron
    funcion = semantic.directorio_funciones[nombre] # obtener la información de la función del directorio de funciones tupla (nombre, tipo_retorno, parametros, inicio, espacio, retorno)
    if cantidad != funcion['num_parametros']: # revisar que num argumentos == num parámetros esperados
        raise Exception(f"Error semántico: número de argumentos incorrecto para '{nombre}'")
    q.pop_operador()  # fondo falso de la llamada
    q.push_cuadruplo('GOSUB', nombre, None, funcion['inicio']) # cuádruplo de go subrutina
    if funcion['tipo_retorno'] != 'void': # si la función no es void, generar un temporal para guardar el valor de retorno
        temporal = q.nuevo_temp(funcion['tipo_retorno'])
        q.push_cuadruplo('=', funcion['retorno'], None, temporal)
        p[0] = (temporal, funcion['tipo_retorno'])


def p_iniciar_llamada(p):
    'iniciar_llamada :'
    # punto neurálgico 1 y 2 de FunctionCall
    nombre = p[-2] # revisar que la función exista sucede después de 'ID ('
    if nombre not in semantic.directorio_funciones:
        raise Exception(f"Función '{nombre}' no declarada")
    q.push_cuadruplo('ERA', nombre, None, None) # reservar espacio en memoria para la función
    q.pila_llamadas.append([nombre, 0]) # declarar que para función nombre se han registrado 0 parámetros
    q.push_operador(False) # fondo falso para la instrucción de llamada (ERA) (depsués se genera el cuádruplo de (GoSub, nombre, None, inicio_función) y se saca el fondo falso)


def p_argumentos(p):
    '''
        argumentos : lista_argumentos
                   | empty
    '''
    # revisar si hay argumentos 


def p_lista_argumentos(p):
    '''
        lista_argumentos : EXPRESION argumento
                         | lista_argumentos ',' EXPRESION argumento
    '''
    # revisar si hay argumentos (variables) y expresiones (operaciones) para que se generen los cuádruplos necesarios


def p_argumento(p):
    'argumento :'
    # punto neurálgico 3 y 4 de FunctionCall
    nombre, indice = q.pila_llamadas[-1] # obtener el nombre de la función y el índice del argumento que se está procesando
    parametros = semantic.directorio_funciones[nombre]['parametros'] # obtener la lista de parámetros de la función
    valor, tipo = q.pop_operando() # obtener el valor y tipo del argumento que se está procesando
    if indice >= len(parametros): # revisar que no nos hayamos pasado de num params de la función
        raise Exception(f"Error semántico: número de argumentos incorrecto para '{nombre}'")
    if tipo != parametros[indice][1]: # type match de args y params
        raise Exception(f"Error semántico: tipo de argumento {indice + 1} incorrecto para '{nombre}'")
    q.push_cuadruplo('PARAMETER', valor, None, indice + 1) # si pasan las excepciones, generar cuádruplo
    q.pila_llamadas[-1][1] += 1 # incrementar el num args de [funcion, num_args] en la pila de llamadas


def p_FACTOR(p):
    '''
        FACTOR : llamada
               | '(' fondo_falso EXPRESION ')'
               | ID
               | '+' ID
               | '-' ID
               | CTE
               | '+' CTE
               | '-' CTE
    '''
    #
    if p.slice[1].type == 'llamada':
        if p[1] is None:
            raise Exception("Error semántico: una función void no produce un operando")
        q.push_operando(*p[1])
        return
    # len 5 es para el caso de los parentesis
    if len(p) == 5:
        # pop el fondo falso más reciente
        q.pop_operador()
        return
        
    # revisar si el último token es un ID
    pos = len(p) - 1
    if p.slice[pos].type == 'ID':
        # si es un ID, obtener su dirección de memoria y tipo de la tabla de símbolos (memaddr, tipo)
        q.push_operando(obtener_direccion_variable(p[pos]), obtener_tipo_variable(p[pos]))

    # si es + ID o - ID, revisar que el tipo sea numérico
    if pos == 2:
        _, tipo = q.top_operando()
        if tipo not in ('int', 'float'):
            raise Exception(f"Error semántico: signo unario inválido para {tipo}")

    # Resolver la expresión si hay un negativo
    if pos == 2 and p[1] == '-':
        q.push_operando(memoria.constante(-1, 'int'), 'int')
        q.push_operador('*')
        q.resolver_expresion(('*',))


def p_fondo_falso(p):
    'fondo_falso :'
    # crear un fondo falso para los paréntesis
    q.push_operador(False)


def p_FUNCS(p):
    '''
        FUNCS : LEFT_FUNCS ID iniciar_funcion '(' id_FUNCS ')' '[' vars_FUNCS ']' inicio_funcion BODY ';'
    '''
    # punto neurálgico 7 de Module (FUNCS) declaración de función
    # finalizar la función en el directorio de funciones
    finalizar_funcion()


def p_inicio_funcion(p):
    'inicio_funcion :'
    # punto neurálgico 6 de Module (FUNCS) declaración de función
    # guardar lineno. del inicio de la función en el directorio de funciones
    semantic.directorio_funciones[semantic.funcion_actual]['inicio'] = len(q.cuadruplos)


def p_iniciar_funcion(p):
    '''
        iniciar_funcion : empty
    '''
    # Iniciar la función en el directorio de funciones
    # punto neurálgico 1 de Module (FUNCS) declaración de función
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
    # punto neurálgico 2, 3, 4 de Module (FUNCS) declaración de función
    parametros = p[1] if p[1] is not None else []
    registrar_parametros(parametros) # tupla de (nombre, tipo) de los parámetros de la función
    p[0] = parametros


def p_ids_FUNCS(p):
    '''
        ids_FUNCS : ID ':' TYPE
                  | ids_FUNCS ',' ID ':' TYPE
    '''
    if len(p) == 4:
        p[0] = [(p[1], p[3])] # p[1] es el nombre del parámetro, p[3] es el tipo
    else:
        # p[3] es el nombre del parámetro, p[5] es el tipo
        # agregar el parámetro a la lista de parámetros (almacenada en p[1]) y pasarla a p[0]
        p[0] = p[1] + [(p[3], p[5])]


def p_vars_FUNCS(p):
    '''
        vars_FUNCS : VARS
                   | empty
    '''
    # decidir si hay variables locales de la función y procesarlas si existen
    # punto neurálgico 5 de Module (FUNCS) declaración de función

def p_VARS(p):
    '''
        VARS : VAR right_VARS
    '''
    # VAR es el literal 'var'

def p_right_VARS(p):
    '''
        right_VARS : ids_VARS ':' TYPE ';'
                   | ids_VARS ':' TYPE ';' right_VARS
    '''
    # procesar la lista de variables declaradas
    for nombre in p[1]:
        agregar_variable_declarada(nombre, p[3])

def p_ids_VARS(p):
    '''
        ids_VARS : ID
                 | ID ',' ids_VARS
    '''
    # para cada ID , agregarlo a una lista almacenada en p[0] (ids_VARS)
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

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
        PROGRAMA : PROGRAM ID ';' iniciar_programa vars_PROGRAMA funcs_PROGRAMA MAIN inicio_main BODY END finalizar_programa
    '''


def p_iniciar_programa(p):
    '''
        iniciar_programa : empty
    '''
    iniciar_programa(p[-2]) # p[-2] es el nombre del programa
    q.pila_saltos.append(q.push_cuadruplo('GOTO', None, None, None)) # goto main, se rellenará cuando se llegue a main


def p_inicio_main(p):
    'inicio_main :'
    q.rellenar(q.pila_saltos.pop(), len(q.cuadruplos)) # rellenar el GOTO del inicio del programa con el inicio de main
    memoria.iniciar_memoria() # iniciar la memoria para el main (local y temporal)
    semantic.tabla_temporales.clear() # limpiar la tabla de temporales para el main (local y temporal)


def p_finalizar_programa(p):
    '''
        finalizar_programa : empty
    '''
    finalizar_programa()
    q.push_cuadruplo('END', None, None, None)
    # rellenar los cuádruplos de ERA con el espacio de memoria de cada función
    for indice, (operador, nombre, _, _) in enumerate(q.cuadruplos):
        if operador == 'ERA':
            q.rellenar(indice, semantic.directorio_funciones[nombre]['espacio'])


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
    # revisar que la variable exista y obtener su tipo
    obtener_tipo_variable(p[3])
    # generar el cuádruplo de lectura
    q.push_cuadruplo('READ', obtener_direccion_variable(p[3]), None, None)


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
    valor, tipo = q.pop_operando()
    if semantic.funcion_actual is None:
        raise Exception("Error semántico: return solo se permite dentro de una función")
    tipo_retorno = get_function_return_type(semantic.funcion_actual)
    if tipo != tipo_retorno:
        raise Exception(
            f"Error semántico: la función '{semantic.funcion_actual}' debe retornar {tipo_retorno}, no {tipo}"
        )

    destino = semantic.directorio_funciones[semantic.funcion_actual]['retorno']
    q.push_cuadruplo('RETURN', valor, None, destino)

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
        mensaje = f"Error de sintaxis en la línea {p.lineno}: token inesperado '{p.value}'"
    else:
        mensaje = "Error de sintaxis: fin de archivo inesperado"
    print(mensaje)
    raise SyntaxError(mensaje)


parser = yacc.yacc()
