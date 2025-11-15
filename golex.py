# golexer.py - Analizador Léxico para Go (Golang)
import ply.lex as lex

# 1. Palabras Reservadas de Go
reserved = {
    # ... (El diccionario 'reserved' completo de tu implementación anterior) ...
    'package': 'PACKAGE', 'import': 'IMPORT', 'func': 'FUNC', 'var': 'VAR',
    'const': 'CONST', 'type': 'TYPE', 'interface': 'INTERFACE', 'struct': 'STRUCT',
    'if': 'IF', 'else': 'ELSE', 'for': 'FOR', 'switch': 'SWITCH',
    'case': 'CASE', 'default': 'DEFAULT', 'return': 'RETURN', 'break': 'BREAK',
    'continue': 'CONTINUE', 'go': 'GO', 'int': 'T_INT', 'float64': 'T_FLOAT',
    'bool': 'T_BOOL', 'string': 'T_STRING', 'true': 'TRUE', 'false': 'FALSE',
}

# 2. Lista de Nombres de Tokens
tokens = [
    'ID', 'INTEGER', 'FLOAT',
    'STRING_LITERAL', 'RAW_STRING',

    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO',

    # Operadores bit a bit (tu aporte)
    'BIT_OR', 'BIT_XOR', 'AND_NOT', 'LSHIFT', 'RSHIFT',

    # Asignaciones compuestas (incluye las bitwise)
    'OR_ASSIGN', 'XOR_ASSIGN', 'AND_ASSIGN',
    'LSHIFT_ASSIGN', 'RSHIFT_ASSIGN', 'MOD_ASSIGN',
    'PLUS_ASSIGN', 'MINUS_ASSIGN', 'TIMES_ASSIGN', 'DIVIDE_ASSIGN',

    # Asignación simple
    'ASSIGN',

    # Comparadores
    'DECLARE_ASSIGN',  # :=
    'EQ', 'NE', 'LT', 'LE', 'GT', 'GE',

    # Lógicos
    'NOT', 'AND', 'OR',

    # Símbolos varios
    'LPAREN', 'RPAREN',
    'LBRACE', 'RBRACE',
    'LBRACKET', 'RBRACKET',
    'SEMI', 'COMMA', 'DOT',
    'AMPERSAND',
] + list(reserved.values())

# Lista global para almacenar errores léxicos detectados
ERRORS = []


# 3. Reglas para Tokens Simples (Strings)
# =========================
# Operadores y asignaciones
# =========================

# 1) Asignaciones compuestas (primero las de varios caracteres)
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

# 2) Comparadores y operadores de 2 caracteres
t_DECLARE_ASSIGN = r':='
t_EQ             = r'=='
t_NE             = r'!='
t_LE             = r'<='
t_GE             = r'>='

t_AND            = r'\&\&'
t_OR             = r'\|\|'

t_AND_NOT        = r'&\^'
t_LSHIFT         = r'<<'
t_RSHIFT         = r'>>'

# 3) Operadores de un solo carácter
t_ASSIGN    = r'='
t_LT        = r'<'
t_GT        = r'>'
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_TIMES     = r'\*'
t_DIVIDE    = r'/'
t_MODULO    = r'%'
t_NOT       = r'!'

t_AMPERSAND = r'\&'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'
t_LBRACKET  = r'\['
t_RBRACKET  = r'\]'
t_SEMI      = r';'
t_COMMA     = r','
t_DOT       = r'\.'

# 4. Reglas con Acción (Funciones)
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_FLOAT(t):
    r'\d+\.\d*([Ee][\+-]?\d+)?'
    t.value = float(t.value)
    return t

def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING_LITERAL(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = t.value[1:-1]
    return t

def t_COMMENT_BLOCK(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')
    pass

def t_COMMENT_LINE(t):
    r'//.*'
    pass

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    pass

t_ignore = ' \t'

def t_error(t):
    msg = f"*** ERROR LÉXICO *** [Línea {t.lineno}, Columna {t.lexpos}] Carácter ilegal: '{t.value[0]}'"
    print(msg)
    ERRORS.append(msg)
    t.lexer.skip(1)

def t_RAW_STRING(t):
    r'`[^`]*`'
    t.value = t.value[1:-1]
    return t


# Construir el lexer (se exporta como variable global)
lexer = lex.lex()