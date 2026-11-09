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