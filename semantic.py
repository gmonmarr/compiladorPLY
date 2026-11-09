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
def add_var(nombre, tipo):
    if nombre in tabla_simbolos:
        raise Exception(f"Variable '{nombre}' ya declarada")
    tabla_simbolos[nombre] = tipo

def rm_var(nombre):
    if nombre not in tabla_simbolos:
        raise Exception(f"Variable '{nombre}' no declarada")
    del tabla_simbolos[nombre]

def get_var_type(nombre):
    if nombre not in tabla_simbolos:
        raise Exception(f"Variable '{nombre}' no declarada")
    return tabla_simbolos[nombre]

# Variables temporales (ej. t1)
tabla_temporales = {}
_contador_temporales = 0

def add_temp(nombre, tipo):
    if nombre in tabla_temporales:
        raise Exception(f"Temporal '{nombre}' ya declarada")
    tabla_temporales[nombre] = tipo

def rm_temp(nombre):
    if nombre not in tabla_temporales:
        raise Exception(f"Temporal '{nombre}' no declarada")
    del tabla_temporales[nombre]

def get_temp_type(nombre):
    if nombre not in tabla_temporales:
        raise Exception(f"Temporal '{nombre}' no declarada")
    return tabla_temporales[nombre]

def crear_temporal(tipo):
    """
    Crea y devuelve el nombre de un temporal del tipo indicado.
    """
    global _contador_temporales
    _contador_temporales += 1
    nombre = f"t{_contador_temporales}"
    add_temp(nombre, tipo)
    return nombre

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
    Prepara las tablas para analizar un programa nuevo.
    """
    global nombre_programa, funcion_actual, _contador_temporales
    tabla_simbolos.clear()
    tabla_temporales.clear()
    directorio_funciones.clear()
    nombre_programa = None
    funcion_actual = None
    _contador_temporales = 0

def iniciar_programa(nombre):
    global nombre_programa, funcion_actual
    reiniciar_estado_semantico()
    nombre_programa = nombre

def iniciar_funcion(nombre, tipo_retorno):
    global funcion_actual
    add_function(nombre, tipo_retorno, [])
    funcion_actual = nombre

def registrar_parametros(parametros):
    """
    Registra parámetros en el directorio y en la tabla local de la función.
    """
    if funcion_actual is None:
        raise Exception("Error semántico: no hay una función activa para sus parámetros")
    directorio_funciones[funcion_actual]['parametros'] = list(parametros)
    for nombre, tipo in parametros:
        add_function_variable(funcion_actual, nombre, tipo)

def finalizar_funcion():
    global funcion_actual
    funcion_actual = None

def finalizar_programa():
    global funcion_actual
    funcion_actual = None

def agregar_variable_declarada(nombre, tipo):
    """
    Registra una variable global o local según el ámbito activo.
    """
    if funcion_actual is None:
        add_var(nombre, tipo)
    else:
        add_function_variable(funcion_actual, nombre, tipo)

def obtener_tipo_variable(nombre):
    '''
    Busca primero en el ámbito local y luego en la tabla global.
    '''
    if funcion_actual is not None:
        variables = directorio_funciones[funcion_actual].get('variables', {})
        if nombre in variables:
            return variables[nombre]
    if nombre in tabla_simbolos:
        return tabla_simbolos[nombre]
    raise Exception(f"Variable '{nombre}' no declarada")

def add_function(nombre, tipo_retorno, parametros):
    '''
    nombre: str, nombre de la función
    tipo_retorno: str, tipo de retorno de la función (ej. 'int', 'float', 'void')
    parametros: list, lista de tuplas (nombre, tipo) de los parámetros de la función
    '''

    if nombre in directorio_funciones:
        raise Exception(f"Función '{nombre}' ya declarada")
    directorio_funciones[nombre] = {
        'tipo_retorno': tipo_retorno, # tipo de retorno de la función
        'parametros': parametros # lista de tuplas (nombre, tipo)
    }

def add_function_variable(nombre_funcion, nombre_variable, tipo_variable):
    '''
    nombre_funcion: str, nombre de la función
    nombre_variable: str, nombre de la variable
    tipo_variable: str, tipo de la variable (ej. 'int', 'float', 'void')
    '''
    if nombre_funcion not in directorio_funciones:
        raise Exception(f"Función '{nombre_funcion}' no declarada")
    
    if 'variables' not in directorio_funciones[nombre_funcion]:
        directorio_funciones[nombre_funcion]['variables'] = {}
    
    if nombre_variable in directorio_funciones[nombre_funcion]['variables']:
        raise Exception(f"Variable '{nombre_variable}' ya declarada en la función '{nombre_funcion}'")
    
    directorio_funciones[nombre_funcion]['variables'][nombre_variable] = tipo_variable

def get_function_variable_type(nombre_funcion, nombre_variable):
    '''
    nombre_funcion: str, nombre de la función
    nombre_variable: str, nombre de la variable
    '''
    if nombre_funcion not in directorio_funciones:
        raise Exception(f"Función '{nombre_funcion}' no declarada")
    
    if 'variables' not in directorio_funciones[nombre_funcion]:
        raise Exception(f"Función '{nombre_funcion}' no tiene variables declaradas")
    
    if nombre_variable not in directorio_funciones[nombre_funcion]['variables']:
        raise Exception(f"Variable '{nombre_variable}' no declarada en la función '{nombre_funcion}'")
    
    return directorio_funciones[nombre_funcion]['variables'][nombre_variable]

def get_function_return_type(nombre_funcion):
    '''
    nombre_funcion: str, nombre de la función
    '''
    if nombre_funcion not in directorio_funciones:
        raise Exception(f"Función '{nombre_funcion}' no declarada")
    
    return directorio_funciones[nombre_funcion]['tipo_retorno']

def get_function_parameters(nombre_funcion):
    '''
    nombre_funcion: str, nombre de la función
    '''
    if nombre_funcion not in directorio_funciones:
        raise Exception(f"Función '{nombre_funcion}' no declarada")
    
    return directorio_funciones[nombre_funcion]['parametros']
