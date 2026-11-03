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
}

# tokens que se van a reconocer
tokens = (
    'ID', # id (variables y funciones)
    'CTE_FLOAT', # constante float
    'CTE_INT', # constante int
    'CTE_STRING', # constante string
    'NEQ', # operador desigual
) + tuple(reserved.values())

# ignorar espacios tabuladores y enters
t_ignore = " \t\r"

# declaración de tokens simples
# t_ID = r'[a-zA-Z]+[a-zA-Z0-9]*_?[a-zA-Z0-9]*' # alphabet+ anum* _? anum*
# t_CTE_INT = r'\d+'
# t_CTE_FLOAT = r'\d+\.\d+'
# t_CTE_STRING = r'\".*?\"'

# declaración de tokens con intervenciones
def t_ID(t):
    r'[a-zA-Z]+[a-zA-Z0-9]*_?[a-zA-Z0-9]*'
    # aquí alguna acción
    return t

def t_CTE_INT(t):
    r'\d+'
    # aquí alguna acción
    return t

def t_CTE_FLOAT(t):
    r'\d+\.\d+'
    # aquí alguna acción
    return t

def t_CTE_STRING(t):
    r'\".*?\"'
    # aquí alguna acción
    return t

def t_NEQ(t):
    r'!='
    # aquí alguna acción
    return t

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