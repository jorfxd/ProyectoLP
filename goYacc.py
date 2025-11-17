# goYacc.py - Analizador sintáctico (y orquesta semántica) - VERSIÓN CORREGIDA
import ply.yacc as yacc
from golex import tokens
from semant import SemanticAnalyzer

# Precedencia (tokens definidos en golex.py)
precedence = (
    ('left', 'OR'),        # lógico ||  (si tu lexer usa 'OR')
    ('left', 'AND'),       # lógico &&  (si tu lexer usa 'AND')
    ('nonassoc', 'EQ', 'NE', 'LT', 'LE', 'GT', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MODULO'),
    ('right', 'UMINUS', 'NOT'),
)

# Bandera de errores sintácticos
syntax_error_flag = False

# ============================
# Reglas del Parser (AST simple usando tuplas)
# ============================

def p_program(p):
    """program : top_declaration_list"""
    p[0] = ('program', p[1])

def p_top_declaration_list(p):
    """top_declaration_list : top_declaration top_declaration_list
                             | top_declaration"""
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_top_declaration(p):
    """
    top_declaration : PACKAGE ID SEMI
                    | IMPORT STRING_LITERAL SEMI
                    | FUNC ID LPAREN param_list RPAREN func_return LBRACE statement_list RBRACE
                    | VAR ID type_spec ASSIGN expression SEMI
                    | VAR ID type_spec SEMI
                    | ID DECLARE_ASSIGN expression SEMI
                    | ID ASSIGN expression SEMI
    """
    # Normalizamos nodos (p[1] es el lexema de la palabra reservada o el ID)
    if p[1] == 'package':
        p[0] = ('package', p[2])
    elif p[1] == 'import':
        p[0] = ('import', p[2])
    elif p[1] == 'func':
        # ('func', name, params, return_type, body_statements)
        p[0] = ('func', p[2], p[4], p[6], p[8])
    elif p[1] == 'var':
        if len(p) == 6:
            p[0] = ('var', p[2], p[3], p[5])  # var x type = expr
        else:
            p[0] = ('var', p[2], p[3], None)  # var x type
    else:
        # ID := expr  o ID = expr
        if p[2] == ':=' or p.slice[2].type == 'DECLARE_ASSIGN':
            p[0] = ('declare_short', p[1], p[3])
        else:
            p[0] = ('assign', p[1], p[3])

def p_func_return(p):
    """func_return : type_spec
                   | empty"""
    p[0] = p[1]

def p_param_list(p):
    """param_list : param COMMA param_list
                  | param
                  | empty"""
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    elif len(p) == 2:
        p[0] = [p[1]] if p[1] is not None else []
    else:
        p[0] = []

def p_param(p):
    """param : ID type_spec"""
    p[0] = (p[1], p[2])

def p_statement_list(p):
    """statement_list : statement statement_list
                      | empty"""
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []

def p_statement(p):
    """statement : declaration
                 | control_structure
                 | expression SEMI
                 | print_statement SEMI"""
    p[0] = p[1]

# Declarations
def p_declaration_short(p):
    """declaration : ID DECLARE_ASSIGN expression"""
    p[0] = ('declare_short', p[1], p[3])

def p_declaration_assign(p):
    """declaration : ID ASSIGN expression"""
    p[0] = ('assign', p[1], p[3])

def p_declaration_long(p):
    """declaration : VAR ID type_spec ASSIGN expression"""
    p[0] = ('var', p[2], p[3], p[5])

def p_type_spec(p):
    """type_spec : INT_TYPE
                 | FLOAT_TYPE
                 | STRING_TYPE
                 | BOOL_TYPE"""
    p[0] = p[1]

# Control structures
def p_control_structure_if(p):
    """control_structure : IF expression LBRACE statement_list RBRACE else_part"""
    p[0] = ('if', p[2], p[4], p[6])

def p_else_part(p):
    """else_part : ELSE LBRACE statement_list RBRACE
                 | empty"""
    if len(p) == 5:
        p[0] = p[2]
    else:
        p[0] = None

# Print statement (ej. fmt.Println)
def p_print_statement(p):
    """print_statement : ID DOT ID LPAREN arg_list RPAREN"""
    p[0] = ('call', p[1], p[3], p[5])

def p_arg_list(p):
    """arg_list : expression COMMA arg_list
                | expression
                | empty"""
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    elif len(p) == 2:
        p[0] = [p[1]] if p[1] is not None else []
    else:
        p[0] = []

# ----------------------------
# Expresiones y factores
# ----------------------------
def p_expression(p):
    """
    expression : expression PLUS expression
               | expression MINUS expression
               | expression TIMES expression
               | expression DIVIDE expression
               | expression MODULO expression
               | expression OR expression
               | expression AND expression
               | expression EQ expression
               | expression NE expression
               | expression LT expression
               | expression LE expression
               | expression GT expression
               | expression GE expression
               | MINUS expression %prec UMINUS
               | NOT expression
               | factor
    """
    if len(p) == 4:
        p[0] = ('binop', p[2], p[1], p[3])
    elif len(p) == 3:
        p[0] = ('unary', p[1], p[2])
    else:
        p[0] = p[1]

def p_factor(p):
    """factor : INTEGER
              | FLOAT
              | STRING_LITERAL
              | RAW_STRING
              | ID
              | BOOL_LITERAL
              | LPAREN expression RPAREN"""
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = p[1]

# Empty
def p_empty(p):
    "empty :"
    p[0] = None

# ----------------------------
# Manejo de errores sintácticos
# ----------------------------
def p_error(p):
    global syntax_error_flag
    syntax_error_flag = True
    if p:
        print(f"*** ERROR SINTÁCTICO *** Línea {p.lineno}, cerca de '{p.value}' (Token: {p.type}).")
        # intentar sincronizar: descartar tokens hasta '}' o ';' o EOF
        while True:
            tok = parser.token()
            if not tok or tok.type == 'RBRACE' or tok.type == 'SEMI':
                break
        parser.errok()
        return tok
    else:
        print("*** ERROR SINTÁCTICO *** Fin del archivo inesperado")

# Construcción del parser
parser = yacc.yacc()

# Función que usa main.py
def parse_code(code, do_semantic=True, sem_logger=None):
    """
    Analiza sintácticamente el código. Si do_semantic=True y no hay errores sintácticos,
    invoca el analizador semántico (semant.SemanticAnalyzer).
    sem_logger: instancia opcional de SemanticAnalyzer (para reusar).
    Retorna (success_bool, ast_or_none, sem_errors_list).
    """
    global syntax_error_flag
    syntax_error_flag = False
    result = parser.parse(code)
    if syntax_error_flag:
        return (False, None, [])
    ast = result
    sem = sem_logger or SemanticAnalyzer()
    sem_errors = sem.analyze(ast)
    return (len(sem_errors) == 0, ast, sem_errors)
