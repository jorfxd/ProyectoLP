# golexer.py - Analizador Léxico para Go (Golang)
import ply.lex as lex

# =========================
# 1. Palabras Reservadas
# =========================
reserved = {
    'package': 'PACKAGE',
    'import': 'IMPORT',
    'func': 'FUNC',
    'var': 'VAR',
    'const': 'CONST',
    'type': 'TYPE',
    'if': 'IF',
    'else': 'ELSE',
    'for': 'FOR',
    'return': 'RETURN',
    'fmt': 'FMT',

    # Tipos
    'int': 'INT_TYPE',
    'float64': 'FLOAT_TYPE',
    'bool': 'BOOL_TYPE',
    'string': 'STRING_TYPE',

    # NOTA IMPORTANTE:
    # 'true' y 'false' NO deben incluirse aquí para evitar duplicados
}

# =========================
# 2. Lista de Tokens
# =========================
tokens = [
    'ID', 'INTEGER', 'FLOAT',
    'STRING_LITERAL', 'RAW_STRING',
    'BOOL_LITERAL',

    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO',

    'BIT_OR', 'BIT_XOR', 'AND_NOT',
    'LSHIFT', 'RSHIFT',

    'OR_ASSIGN', 'XOR_ASSIGN', 'AND_ASSIGN',
    'LSHIFT_ASSIGN', 'RSHIFT_ASSIGN',
    'MOD_ASSIGN', 'PLUS_ASSIGN', 'MINUS_ASSIGN',
    'TIMES_ASSIGN', 'DIVIDE_ASSIGN',

    'ASSIGN',
    'DECLARE_ASSIGN',

    'EQ', 'NE', 'LT', 'LE', 'GT', 'GE',

    'NOT', 'AND', 'OR',

    'LPAREN', 'RPAREN',
    'LBRACE', 'RBRACE',
    'LBRACKET', 'RBRACKET',
    'SEMI', 'COMMA', 'DOT',
    'AMPERSAND',
] + list(reserved.values())

# Lista global para errores léxicos
ERRORS = []

# =========================
# 3. Reglas para Tokens
# =========================

# ---------- Asignaciones compuestas ----------
t_LSHIFT_ASSIGN  = r'<<='
t_RSHIFT_ASSIGN  = r'>>='
t_PLUS_ASSIGN    = r'\+='
t_MINUS_ASSIGN   = r'-='
t_TIMES_ASSIGN   = r'\*='
t_DIVIDE_ASSIGN  = r'/='
t_MOD_ASSIGN     = r'%='
t_AND_ASSIGN     = r'&='
t_OR_ASSIGN      = r'\|='
t_XOR_ASSIGN     = r'\^='

# ---------- Comparadores ----------
t_DECLARE_ASSIGN = r':='
t_EQ = r'=='
t_NE = r'!='
t_LE = r'<='
t_GE = r'>='

# ---------- Lógicos ----------
t_AND = r'\&\&'
t_OR = r'\|\|'

# ---------- Bits ----------
t_AND_NOT = r'&\^'
t_LSHIFT  = r'<<'
t_RSHIFT  = r'>>'

# ---------- Operadores de un carácter ----------
t_ASSIGN = r'='
t_LT = r'<'
t_GT = r'>'
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MODULO = r'%'
t_NOT = r'!'

t_AMPERSAND = r'&'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_SEMI = r';'
t_COMMA = r','
t_DOT = r'\.'

# =========================
# 4. Reglas con Acción
# =========================

# Identificadores y palabras reservadas
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t

# Booleanos (corregido)
def t_BOOL_LITERAL(t):
    r'(true|false)'
    t.value = True if t.value == "true" else False
    return t

# Floats
def t_FLOAT(t):
    r'\d+\.\d*([Ee][\+-]?\d+)?'
    t.value = float(t.value)
    return t

# Enteros
def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Strings normales
def t_STRING_LITERAL(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = t.value[1:-1]
    return t

# Strings raw (backticks)
def t_RAW_STRING(t):
    r'`[^`]*`'
    t.value = t.value[1:-1]
    return t

# Comentarios
def t_COMMENT_BLOCK(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')

def t_COMMENT_LINE(t):
    r'//.*'
    pass

# Nuevas líneas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Ignorar espacios y tabs
t_ignore = ' \t'

# Errores
def t_error(t):
    msg = f"*** ERROR LÉXICO *** [Línea {t.lineno}, Columna {t.lexpos}] Carácter ilegal: '{t.value[0]}'"
    print(msg)
    ERRORS.append(msg)
    t.lexer.skip(1)

# Construir lexer
lexer = lex.lex()
