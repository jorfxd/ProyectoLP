# goparser.py - Analizador Sintáctico para Go (Golang) (versión corregida)
import ply.yacc as yacc
import sys

# Importar el léxico (golex.py)
try:
    from golex import tokens, lexer
except ImportError:
    sys.stderr.write("Error: No se pudo importar golex.py. Asegúrate de la ruta.\n")
    tokens = []

# Tabla de Símbolos Placeholder (para futura implementación semántica)
symbol_table = {}

# 1. Precedencia y Asociatividad (usar tokens que realmente están en el lexer)
precedence = (
    ('left', 'LOR'),                        # ||    (en lexer: LOR)
    ('left', 'LAND'),                       # &&    (en lexer: LAND)
    ('nonassoc', 'EQ', 'NEQ', 'LT', 'LE', 'GT', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),     # usar MOD en lugar de MODULO
    ('right', 'UMINUS', 'NOT'),
)

# Flag de error sintáctico
syntax_error_flag = False

# 2. Reglas Gramaticales (Producciones BNF)

def p_program(p):
    """
    program : top_declaration_list
    """
    print(f"[INFO SINTÁCTICO] Estructura del programa verificada. Total de declaraciones de alto nivel.")
    p[0] = p[1]

def p_top_declaration_list(p):
    """
    top_declaration_list : top_declaration top_declaration_list
                         | top_declaration
    """
    p[0] = [p[1]] + p[2] if len(p) == 3 else [p[1]]

def p_top_declaration(p):
    """
    top_declaration : PACKAGE ID SEMI_OPTIONAL
                    | FUNC ID LPAREN param_list RPAREN func_return LBRACE statement_list RBRACE
                    | VAR ID type_spec ASSIGN expression SEMI_OPTIONAL
                    | CONST ID ASSIGN expression SEMI_OPTIONAL
                    | IMPORT STRING_LITERAL SEMI_OPTIONAL
    """
    p[0] = p[1]

def p_func_return(p):
    """
    func_return : type_spec
                | empty
    """
    pass

def p_param_list(p):
    """
    param_list : param COMMA param_list
               | param
               | empty
    """
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    elif len(p) == 2:
        p[0] = [p[1]] if p[1] is not None else []
    else:
        p[0] = []

def p_param(p):
    """
    param : ID type_spec
    """
    p[0] = (p[1], p[2])

def p_statement_list(p):
    """
    statement_list : statement statement_list
                   | empty
    """
    p[0] = [p[1]] + p[2] if len(p) == 3 else []

def p_statement(p):
    """
    statement : declaration SEMI_OPTIONAL
              | control_structure
              | expression SEMI_OPTIONAL
              | print_statement SEMI_OPTIONAL
    """
    p[0] = p[1]

# Declaraciones: aceptar tanto 'x := expr' como 'x = expr' o 'var x T = expr'
def p_declaration_short_assign(p):
    """
    declaration : ID COLON ASSIGN expression
                | ID ASSIGN expression
    """
    # Acepta "x := expr" (como COLON ASSIGN) o "x = expr"
    if len(p) == 5:
        print(f"[INFO SINTÁCTICO] Declaración corta verificada (:=): {p[1]}")
        p[0] = ('declare_short', p[1], p[4])
    else:
        print(f"[INFO SINTÁCTICO] Asignación verificada (=): {p[1]}")
        p[0] = ('assign', p[1], p[3])

def p_declaration_long(p):
    """
    declaration : VAR ID type_spec ASSIGN expression
    """
    print(f"[INFO SINTÁCTICO] Declaración larga verificada: var {p[2]} ...")
    p[0] = ('var_decl', p[2], p[3], p[5])

def p_type_spec(p):
    """
    type_spec : INT_TYPE
              | FLOAT_TYPE
              | STRING_TYPE
              | BOOL_TYPE
    """
    p[0] = p[1]

# Control de flujo: if / else
def p_control_structure_if(p):
    """
    control_structure : IF expression LBRACE statement_list RBRACE else_part
    """
    print("[INFO SINTÁCTICO] Estructura IF-ELSE verificada.")
    p[0] = ('if', p[2], p[4], p[6])

def p_else_part(p):
    """
    else_part : ELSE LBRACE statement_list RBRACE
              | empty
    """
    p[0] = p[1] if len(p) == 2 else p[3]

# Print (ej. fmt.Println)
def p_print_statement(p):
    """
    print_statement : ID DOT ID LPAREN arg_list RPAREN
    """
    if p[1] == 'fmt' and p[3] == 'Println':
        print(f"[INFO SINTÁCTICO] Llamada a 'fmt.Println' verificada.")
    else:
        print(f"[INFO SINTÁCTICO] Llamada a función genérica verificada: {p[1]}.{p[3]}(...)")
    p[0] = ('call', p[1], p[3], p[5])

def p_arg_list(p):
    """
    arg_list : expression COMMA arg_list
             | expression
             | empty
    """
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    elif len(p) == 2:
        p[0] = [p[1]] if p[1] is not None else []
    else:
        p[0] = []

# Expresiones (usar tokens que el lexer realmente emite)
def p_expression(p):
    """
    expression : expression PLUS expression
               | expression MINUS expression
               | expression TIMES expression
               | expression DIVIDE expression
               | expression MOD expression
               | expression AND expression
               | expression OR expression
               | expression EQ expression
               | expression NEQ expression
               | expression LT expression
               | expression LE expression
               | expression GT expression
               | expression GE expression
               | MINUS expression %prec UMINUS
               | NOT expression
               | factor
    """
    if len(p) == 4:
        p[0] = (p[2], p[1], p[3])
    elif len(p) == 3:
        p[0] = ('unary', p[1], p[2])
    else:
        p[0] = p[1]

def p_factor(p):
    """
    factor : INT_LITERAL
           | FLOAT_LITERAL
           | ID
           | STRING_LITERAL
           | LPAREN expression RPAREN
           | BOOL_LITERAL
    """
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = p[1]

def p_semi_optional(p):
    """
    SEMI_OPTIONAL : SEMI
                  | empty
    """
    pass

def p_empty(p):
    'empty :'
    p[0] = None

# Manejo de errores sintácticos
def p_error(p):
    """
    Regla de manejo de errores sintácticos.
    """
    global syntax_error_flag
    syntax_error_flag = True

    if p:
        print(f"*** ERROR SINTÁCTICO *** Línea {p.lineno}, cerca de '{p.value}' (Token: {p.type}).")
        # Modo pánico: descartar tokens hasta encontrar '}' o ';' o EOF
        while True:
            tok = parser.token()
            if not tok or tok.type == 'RBRACE' or tok.type == 'SEMI':
                break
        parser.errok()
        return tok
    else:
        print("*** ERROR SINTÁCTICO *** Error al final del archivo (EOF). Código incompleto.")

# 4. Construcción del Parser
parser = yacc.yacc()
syntax_error_flag = False

def parse_code(code):
    """Resetea el estado de error y analiza el código."""
    global syntax_error_flag
    syntax_error_flag = False
    parser.parse(code)
    return not syntax_error_flag
