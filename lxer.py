"""Lexer para el lenguaje descrito en tokens.csv, usando PLY."""

import ply.lex as lex

# Las palabras reservadas se reconocen desde la regla de identificadores.
reserved = {
    "do": "DO",
    "else": "ELSE",
    "end": "END",
    "if": "IF",
    "main": "MAIN",
    "print": "PRINT",
    "program": "PROGRAM",
    "read": "READ",
    "return": "RETURN",
    "void": "VOID",
    "while": "WHILE",
    "var": "VAR",
}

# Solo categorías léxicas; las reglas como BODY y STATEMENT pertenecen al parser.
tokens = (
    "ID",
    "CTE_INT",
    "CTE_FLOAT",
    "CTE_STRING",
    "NE",
) + tuple(sorted(set(reserved.values())))

# Símbolos de un carácter que PLY devuelve usando su propio carácter como tipo.
literals = "- , ; : ( ) { } [ ] * / + = < >".split()

# PLY ignora estos caracteres entre tokens.
t_ignore = " \t\r"

# Los patrones de constantes flotantes se evalúan antes que los enteros.
def t_CTE_FLOAT(t):
    r"\d+\.\d+"
    t.value = float(t.value)
    return t


def t_CTE_INT(t):
    r"\d+"
    t.value = int(t.value)
    return t


def t_CTE_STRING(t):
    r'''("([^\\\n]|\\.)*"|'([^\\\n]|\\.)*')'''
    # Conserva las comillas en el valor para que el parser/semántica decida qué hacer.
    return t


def t_NE(t):
    r"!="
    return t


def t_ID(t):
    r"[a-zA-Z][a-zA-Z0-9]*(?:_[a-zA-Z0-9]+)?"
    t.type = reserved.get(t.value, "ID")
    return t


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    print(f"Error léxico en línea {t.lexer.lineno}: carácter no válido {t.value[0]!r}")
    t.lexer.skip(1)


lexer = lex.lex()


if __name__ == "__main__":
    import sys

    source = sys.stdin.read() if not sys.stdin.isatty() else "3 + 4 * 10\n"
    lexer.input(source)
    for token in lexer:
        print(token)
