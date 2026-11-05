# https://ply.readthedocs.io/en/latest/ply.html
# used to tokenize an input string

import ply.lex as lex

# literals son símbolos de un caracter que se evalúan como ellos mismos. 
literals = ' - , ; : ( ) { } [ ] * / + = < > '.split() # .split para quitar los espacios en blanco

# palabras reservadas que no pueden ser usadas como IDs
reserved = {
    'do': 'DO',
    'else': 'ELSE',
    'end': 'END',
    'if': 'IF',
    'main': 'MAIN',
    'print': 'PRINT',
    'program': 'PROGRAM',
    'read': 'READ',
    'return': 'RETURN',
    'void': 'VOID',
    'while': 'WHILE',
    'var': 'VAR',
    'int': 'INT',
    'float': 'FLOAT',
}

# tokens que se van a reconocer
tokens = (
    'ID', # id (variables y funciones)
    'CTE_FLOAT', # constante float
    'CTE_INT', # constante int
    'CTE_STRING', # constante string
    'NEQ', # operador desigual
    'NEWLINE', # salto de línea, útil para contar líneas y reportar errores
) + tuple(reserved.values())

# ignorar espacios tabuladores y enters
t_ignore = " \t\r"

# declaración de tokens con intervenciones
def t_ID(t):
    r'[a-zA-Z]+[a-zA-Z0-9]*_?[a-zA-Z0-9]*'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
    return t

# reconocer flotantes
def t_CTE_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

# reconocer enteros
def t_CTE_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t

# reconocer strings entre comillas dobles
def t_CTE_STRING(t):
    r'\".*?\"' # espera que haya un string entre comillas dobles
    # "{cualquier caracter si es que hay}"
    # aquí alguna acción
    return t

# token desigualdad
def t_NEQ(t):
    r'!='
    # aquí alguna acción
    return t

# reportar errores de tokens
def t_error(t):
    print(f"Caracter no reconocido: '{t.value[0]}'")
    t.lexer.skip(1)

# contar líneas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# EOF handling rule (saber cuándo termina el input)
# def t_eof(t):
#     # Get more input (Example)
#     more = input('... ')
#     if more:
#         self.lexer.input(more)
#         return self.lexer.token()
#     return None

if __name__ == "__main__":
    # Test it out
    data = '''
    3 + 4 * 10
    + -20 *2
    '''

    # Give the lexer some input
    lexer = lex.lex()
    lexer.input(data)

    # Tokenize
    for tok in lexer:
        print(tok)