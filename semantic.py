import memoria

# Cubo semántico
# resultado = cubo[tipo1][tipo2][operador]
# tipos: int, float, bool, string
cubo = {
    'int': {
        'int': {
            '+': 'int',
            '-': 'int',
            '*': 'int',
            '/': 'int',
            '=': 'int',
            '==': 'bool',
            '!=': 'bool',
            '<': 'bool',
            '>': 'bool',
            '<=': 'bool',
            '>=': 'bool'
        },
        'float': {
            '+': 'float',
            '-': 'float',
            '*': 'float',
            '/': 'float',
            '=': 'float',
            '==': 'bool',
            '!=': 'bool',
            '<': 'bool',
            '>': 'bool',
            '<=': 'bool',
            '>=': 'bool'
        }
    },
    'float': {
        'float': {
            '+': 'float',
            '-': 'float',
            '*': 'float',
            '/': 'float',
            '=': 'float',
            '==': 'bool',
            '!=': 'bool',
            '<': 'bool',
            '>': 'bool',
            '<=': 'bool',
            '>=': 'bool'
        },
        'int': {
            '+': 'float',
            '-': 'float',
            '*': 'float',
            '/': 'float',
            '=': 'float',
            '==': 'bool',
            '!=': 'bool',
            '<': 'bool',
            '>': 'bool',
            '<=': 'bool',
            '>=': 'bool'
        }
    },
    'bool': {
        'bool': {
            '==': 'bool',
            '!=': 'bool',
        }
    },
    'string': {
        'string': {
            '+': 'string', # concat
            '=': 'string',
            '==': 'bool',
            '!=': 'bool'
        }
    }
}

def oraculo_cubo(tipo1, tipo2, operador):
    try:
        return cubo[tipo1][tipo2][operador]
    except KeyError:
        raise Exception(f"Error semántico: operación inválida {tipo1} {operador} {tipo2}")

# ---------------------
# Guardar variables declaradas y temporales
# ---------------------

# Variables de la tabla de símbolos (variables declaradas)
tabla_simbolos = {}
direcciones_globales = {}
def add_var(nombre, tipo):
    """
    nombre: str, nombre de la variable
    tipo: str, tipo de la variable (ej. 'int')
    """
    if nombre in tabla_simbolos:
        raise Exception(f"Variable '{nombre}' ya declarada")
    direcciones_globales[nombre] = memoria.reservar('global', tipo)
    tabla_simbolos[nombre] = tipo

def rm_var(nombre):
    """
    nombre: str, nombre de la variable
    return: None
    """
    if nombre not in tabla_simbolos:
        raise Exception(f"Variable '{nombre}' no declarada")
    del tabla_simbolos[nombre]
    del direcciones_globales[nombre]

def get_var_type(nombre):
    """
    nombre: str, nombre de la variable
    return: str, tipo de la variable
    """
    if nombre not in tabla_simbolos:
        raise Exception(f"Variable '{nombre}' no declarada")
    return tabla_simbolos[nombre]

# Variables temporales (dirección virtual -> tipo)
tabla_temporales = {}

def add_temp(nombre, tipo):
    """
    Agregar una variable temporal a la tabla de temporales.

    nombre: int, dirección virtual del temporal
    tipo: str, tipo del temporal (ej. 'int')
    """
    if nombre in tabla_temporales:
        raise Exception(f"Temporal '{nombre}' ya declarada")
    tabla_temporales[nombre] = tipo

def rm_temp(nombre):
    """
    Eliminar una variable temporal de la tabla de temporales.
    nombre: int, dirección virtual del temporal
    return: None
    """
    if nombre not in tabla_temporales:
        raise Exception(f"Temporal '{nombre}' no declarada")
    del tabla_temporales[nombre]

def get_temp_type(nombre):
    """
    Obtener el tipo de una variable temporal.
    nombre: int, dirección virtual del temporal
    return: str, tipo del temporal
    """
    if nombre not in tabla_temporales:
        raise Exception(f"Temporal '{nombre}' no declarada")
    return tabla_temporales[nombre]

# ---------------------
# Guardar variables de funciones
# ---------------------

# Funciones declaradas
directorio_funciones = {}
# directorio_funciones[nombre_funcion] = {
#     'tipo_retorno': tipo_retorno,
#     'parametros': [(nombre_parametro, tipo_parametro), ...],
#     'variables': {nombre_variable: tipo_variable, ...},
# }

nombre_programa = None
funcion_actual = None

def reiniciar_estado_semantico():
    """
    Borra tablas, memoria virtual y cuádruplos para un nuevo programa.
    """
    import cuadruplos
    global nombre_programa, funcion_actual

    # limpiar tablas
    tabla_simbolos.clear()
    direcciones_globales.clear()
    tabla_temporales.clear()
    directorio_funciones.clear()
    nombre_programa = None
    funcion_actual = None
    cuadruplos.limpiar()
    memoria.limpiar()

def iniciar_programa(nombre):
    """
    Inicia un nuevo programa.
    nombre: str, nombre del programa
    """
    global nombre_programa, funcion_actual
    reiniciar_estado_semantico()
    nombre_programa = nombre

def iniciar_funcion(nombre, tipo_retorno):
    """
    Inicia una nueva función (rastrear variables locales y parámetros).
    nombre: str, nombre de la función
    tipo_retorno: str, tipo de retorno de la función
    """
    global funcion_actual
    add_function(nombre, tipo_retorno, []) # crear la función en el directorio de funciones
    memoria.iniciar_memoria() # iniciar la memoria para la nueva función
    tabla_temporales.clear() # limpiar la tabla de temporales para la nueva función
    funcion_actual = nombre # global scope nombre de la función actual

def registrar_parametros(parametros):
    """
    Registra parámetros en el directorio y en la tabla local de la función.
    """
    # si no hay función global activa, error
    if funcion_actual is None:
        raise Exception("Error semántico: no hay una función activa para sus parámetros")
    
    # registrar parámetros en el directorio de funciones y en la tabla de variables locales
    directorio_funciones[funcion_actual]['parametros'] = list(parametros)

    for nombre, tipo in parametros:
        # Reservar memoria para la variable en local de la función y agregarla al directorio de funciones.
        add_function_variable(funcion_actual, nombre, tipo)
    
    # registrar en la tupla cuántos parámetros tiene la función
    directorio_funciones[funcion_actual]['num_parametros'] = len(parametros)

def finalizar_funcion():
    """
    Finaliza la función actual.
    """
    import cuadruplos as q
    global funcion_actual
    funcion = directorio_funciones[funcion_actual] # obtener la función actual tupla (tipo_retorno, parametros, variables, direcciones, num_parametros, inicio, espacio)
    funcion['num_locales'] = len(funcion['variables']) - funcion['num_parametros'] # contar sólo las variables locales de esa función
    funcion['espacio'] = {
        'locales': memoria.espacio('local'), # guardar el espacio de memoria de esta función
        'temporales': memoria.espacio('temporal'), # guardar el espacio de memoria de esta función
    }
    funcion['num_temporales'] = sum(funcion['espacio']['temporales'].values()) # contar el número de temporales de esta función
    q.push_cuadruplo('ENDFUNC', None, None, None) # agregar cuádruplo de fin de función
    funcion_actual = None # resetear la función actual a None

def finalizar_programa():
    """
    Finaliza el programa actual.
    """
    global nombre_programa, funcion_actual
    nombre_programa = None
    funcion_actual = None

def agregar_variable_declarada(nombre, tipo):
    """
    Registra una variable global o local según el ámbito activo.
    """
    if funcion_actual is None:
        # registrar variable global
        add_var(nombre, tipo)
    else:
        # registrar variable local de la función actual
        add_function_variable(funcion_actual, nombre, tipo)

def obtener_tipo_variable(nombre):
    """
    Busca primero en el ámbito local y luego en la tabla global.
    """
    if funcion_actual is not None:
        variables = directorio_funciones[funcion_actual].get('variables', {})
        if nombre in variables:
            return variables[nombre]
    if nombre in tabla_simbolos:
        return tabla_simbolos[nombre]
    raise Exception(f"Variable '{nombre}' no declarada")


def obtener_direccion_variable(nombre):
    """
    Obtiene la dirección de memoria de una variable.
    """
    obtener_tipo_variable(nombre)
    if funcion_actual is not None:
        # si hay una función activa, buscar en su tabla de direcciones locales
        direcciones = directorio_funciones[funcion_actual]['direcciones']
        if nombre in direcciones:
            return direcciones[nombre]
    # si no hay función activa o no se encontró en la tabla local, buscar en la tabla global
    return direcciones_globales[nombre]

def add_function(nombre, tipo_retorno, parametros):
    """
    nombre: str, nombre de la función
    tipo_retorno: str, tipo de retorno de la función (ej. 'int', 'float', 'void')
    parametros: list, lista de tuplas (nombre, tipo) de los parámetros de la función
    """
    # (tipo_retorno, parametros, variables, direcciones, num_parametros, inicio, espacio)
    if nombre in directorio_funciones:
        raise Exception(f"Función '{nombre}' ya declarada")
    directorio_funciones[nombre] = {
        'tipo_retorno': tipo_retorno, # tipo de retorno de la función
        'parametros': parametros, # lista de tuplas (nombre, tipo)
        'variables': {},
        'direcciones': {},
        'num_parametros': 0,
        'inicio': None,
        'espacio': None,
        'retorno': memoria.reservar('global', tipo_retorno) if tipo_retorno != 'void' else None,
    }

def add_function_variable(nombre_funcion, nombre_variable, tipo_variable):
    """
    nombre_funcion: str, nombre de la función
    nombre_variable: str, nombre de la variable
    tipo_variable: str, tipo de la variable (ej. 'int', 'float', 'void')

    Reservar memoria para la variable en local de la función y agregarla al directorio de funciones.
    """
    if nombre_funcion not in directorio_funciones:
        raise Exception(f"Función '{nombre_funcion}' no declarada")
    
    if 'variables' not in directorio_funciones[nombre_funcion]:
        directorio_funciones[nombre_funcion]['variables'] = {}
    
    if nombre_variable in directorio_funciones[nombre_funcion]['variables']:
        raise Exception(f"Variable '{nombre_variable}' ya declarada en la función '{nombre_funcion}'")
    
    # Registrar la variable en el directorio de funciones y en la tabla de variables locales
    directorio_funciones[nombre_funcion]['direcciones'][nombre_variable] = memoria.reservar('local', tipo_variable)
    directorio_funciones[nombre_funcion]['variables'][nombre_variable] = tipo_variable

def get_function_variable_type(nombre_funcion, nombre_variable):
    """
    nombre_funcion: str, nombre de la función
    nombre_variable: str, nombre de la variable
    """
    if nombre_funcion not in directorio_funciones:
        raise Exception(f"Función '{nombre_funcion}' no declarada")
    
    if 'variables' not in directorio_funciones[nombre_funcion]:
        raise Exception(f"Función '{nombre_funcion}' no tiene variables declaradas")
    
    if nombre_variable not in directorio_funciones[nombre_funcion]['variables']:
        raise Exception(f"Variable '{nombre_variable}' no declarada en la función '{nombre_funcion}'")
    
    return directorio_funciones[nombre_funcion]['variables'][nombre_variable]

def get_function_return_type(nombre_funcion):
    """
    nombre_funcion: str, nombre de la función
    """
    if nombre_funcion not in directorio_funciones:
        raise Exception(f"Función '{nombre_funcion}' no declarada")
    
    return directorio_funciones[nombre_funcion]['tipo_retorno']

def get_function_parameters(nombre_funcion):
    """
    nombre_funcion: str, nombre de la función
    """
    if nombre_funcion not in directorio_funciones:
        raise Exception(f"Función '{nombre_funcion}' no declarada")
    
    return directorio_funciones[nombre_funcion]['parametros']
