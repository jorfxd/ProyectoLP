# golexer.py - Analizador Léxico para Go (Golang)
import ply.lex as lex

# 1. Palabras Reservadas de Go
reserved = {
    # Estructura del programa
    'package': 'PACKAGE',
    'import': 'IMPORT',
    'func': 'FUNC',
    'var': 'VAR',
    'const': 'CONST',
    'type': 'TYPE',

    # Tipos de datos y estructuras
    'struct': 'STRUCT',
    'interface': 'INTERFACE',
    'map': 'MAP',
    'chan': 'CHAN',

    # Control de flujo
    'if': 'IF',
    'else': 'ELSE',
    'for': 'FOR',
    'range': 'RANGE',
    'switch': 'SWITCH',
    'case': 'CASE',
    'default': 'DEFAULT',
    'return': 'RETURN',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    'defer': 'DEFER',
    'go': 'GO',
    'select': 'SELECT',

    # Tipos primitivos
    'bool': 'BOOL_TYPE',
    'byte': 'BYTE',
    'rune': 'RUNE',
    'int': 'INT_TYPE',
    'int8': 'INT_TYPE',
    'int16': 'INT_TYPE',
    'int32': 'INT_TYPE',
    'int64': 'INT_TYPE',
    'uint': 'UINT_TYPE',
    'uintptr': 'UINT_TYPE',
    'float32': 'FLOAT_TYPE',
    'float64': 'FLOAT_TYPE',
    'complex64': 'COMPLEX_TYPE',
    'complex128': 'COMPLEX_TYPE',
    'string': 'STRING_TYPE',

    # Literales booleanos
    'true': 'BOOL_LITERAL',
    'false': 'BOOL_LITERAL'
}

# 2. Lista de Nombres de Tokens
tokens = [
    # Identificadores y literales
    'ID', 'INT_LITERAL', 'FLOAT_LITERAL', 'IMAG_LITERAL',
    'CHAR_LITERAL', 'STRING_LITERAL', 'RAW_STRING',

    # Operadores aritméticos y de asignación
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
    'PLUSPLUS', 'MINUSMINUS',
    'ASSIGN', 'PLUSEQ', 'MINUSEQ', 'TIMESEQ', 'DIVEQ', 'MODEQ',
    'ANDEQ', 'OREQ', 'XOREQ', 'LSHIFTEQ', 'RSHIFTEQ', 'ANDCONEQ',

    # Comparación
    'EQ', 'NEQ', 'LT', 'GT', 'LE', 'GE',

    # Lógicos y bit a bit
    'LAND', 'LOR', 'NOT', 'AND', 'OR', 'XOR', 'AND_NOT', 'LSHIFT', 'RSHIFT',

    # Delimitadores
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
    'LBRACKET', 'RBRACKET', 'COMMA', 'SEMI', 'DOT', 'COLON', 'ELLIPSIS',

    # Comentarios
    'COMMENT', 'LINECOMMENT',
] + list(set(reserved.values()))

# Lista global para almacenar errores léxicos detectados
ERRORS = []


# 3. Reglas para Tokens Simples (Strings)
t_PLUS       = r'\+'
t_MINUS      = r'-'
t_TIMES      = r'\*'
t_DIVIDE     = r'/'
t_MOD        = r'%'
t_PLUSPLUS   = r'\+\+'
t_MINUSMINUS = r'--'

# Asignaciones
t_ASSIGN     = r'='
t_PLUSEQ     = r'\+='
t_MINUSEQ    = r'-='
t_TIMESEQ    = r'\*='
t_DIVEQ      = r'/='
t_MODEQ      = r'%='
t_ANDEQ      = r'&='
t_OREQ       = r'\|='
t_XOREQ      = r'\^='
t_LSHIFTEQ   = r'<<='
t_RSHIFTEQ   = r'>>='
t_ANDCONEQ   = r'&\^='

# Comparaciones
t_EQ         = r'=='
t_NEQ        = r'!='
t_LE         = r'<='
t_GE         = r'>='
t_LT         = r'<'
t_GT         = r'>'

# Lógicos / Bit a bit
t_LAND       = r'&&'
t_LOR        = r'\|\|'
t_NOT        = r'!'
t_AND        = r'&'
t_OR         = r'\|'
t_XOR        = r'\^'
t_AND_NOT    = r'&\^'
t_LSHIFT     = r'<<'
t_RSHIFT     = r'>>'

# Delimitadores
t_LPAREN     = r'\('
t_RPAREN     = r'\)'
t_LBRACE     = r'\{'
t_RBRACE     = r'\}'
t_LBRACKET   = r'\['
t_RBRACKET   = r'\]'
t_COMMA      = r','
t_SEMI       = r';'
t_DOT        = r'\.'
t_COLON      = r':'
t_ELLIPSIS   = r'\.\.\.'


# COMENTARIOS

# Ignorar espacios y tabs
t_ignore  = ' \t\r'

# 4. Reglas con Acción (Funciones)
def t_LINECOMMENT(t):
    r'//[^\n]*'
    pass  # se ignora, no devuelve token

def t_COMMENT(t):
    r'/\*([^*]|\*(?!/))*\*/'
    t.lexer.lineno += t.value.count('\n')
    pass  # se ignora, no devuelve token


# LITERALES

# Raw string con backticks
def t_RAW_STRING(t):
    r'`[^`]*`'
    t.value = t.value[1:-1]
    return t

# Strings normales con comillas dobles y escapes
def t_STRING_LITERAL(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = t.value[1:-1]
    return t

# Caracteres (rune literals)
def t_CHAR_LITERAL(t):
    r"\'([^\\\n]|(\\.))\'"
    t.value = t.value[1:-1]
    return t

# Números flotantes (con notación científica)
def t_FLOAT_LITERAL(t):
    r'((\d+\.\d*|\.\d+)([eE][+-]?\d+)?|\d+[eE][+-]?\d+)'
    t.value = float(t.value)
    return t

# Números imaginarios (terminan con 'i')
def t_IMAG_LITERAL(t):
    r'(\d+(\.\d*)?|\.\d+)[i]'
    t.value = complex(float(t.value[:-1]))
    return t

# Números enteros (dec, hex, bin, octal)
def t_INT_LITERAL(t):
    r'0[xX][0-9a-fA-F]+|0[bB][01]+|0[oO]?[0-7]+|\d+'
    s = t.value
    if s.startswith(('0x','0X')):
        t.value = int(s, 16)
    elif s.startswith(('0b','0B')):
        t.value = int(s, 2)
    elif s.startswith(('0o','0O')) or (s.startswith('0') and len(s)>1 and s[1].isdigit()):
        t.value = int(s, 8)
    else:
        t.value = int(s, 10)
    return t

# Identificadores y palabras reservadas
def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    if t.value in reserved:
        t.type = reserved[t.value]
        if t.type == 'BOOL_LITERAL':
            t.value = True if t.value == 'true' else False
    return t

# CONTROL DE LÍNEAS Y ERRORES
def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')

def t_error(t):
    print(f"*** ERROR LÉXICO *** [Línea {t.lexer.lineno}] Carácter ilegal: {t.value[0]!r}")
    t.lexer.skip(1)

# Construir el lexer (se exporta como variable global)
lexer = lex.lex()