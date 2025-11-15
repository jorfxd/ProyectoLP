# goparser.py - Analizador Sintáctico para Go (Golang)
import ply.yacc as yacc
import sys

# Importar el léxico (golex.py/golexer.py)
try:
    # Nota: Se asume que el archivo del léxico se llama golex.py o golexer.py
    # y la variable del lexer es 'lexer'.
    from golex import tokens, lexer
except ImportError:
    sys.stderr.write("Error: No se pudo importar golexer.py. Asegúrate de la ruta.\n")
    tokens = []

# Tabla de Símbolos Placeholder (para futura implementación semántica)
symbol_table = {}

# 1. Precedencia y Asociatividad
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'EQ', 'NE', 'LT', 'LE', 'GT', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MODULO'),
    ('right', 'UMINUS', 'NOT'),
)


# 2. Reglas Gramaticales (Producciones BNF)

# Símbolo inicial
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
    # ACCIÓN SEMÁNTICA: Registrar la función o variable global.
    p[0] = p[1]

# Regla de función (Simplificación de la propuesta)
def p_func_return(p):
    """
    func_return : type_spec
                | empty
    """
    pass

# Regla de lista de parámetros (necesaria para la función)
def p_param_list(p):
    """
    param_list : param COMMA param_list
               | param
               | empty
    """
    pass

def p_param(p):
    """
    param : ID type_spec
    """
    pass

def p_statement_list(p):
    """
    statement_list : statement statement_list
                   | empty
    """
    # Si la longitud es 3 (statement statement_list), construye la lista. Si es 1 (empty), es una lista vacía [].
    p[0] = [p[1]] + p[2] if len(p) == 3 else []


def p_statement(p):
    """
    statement : declaration SEMI_OPTIONAL
              | control_structure
              | expression SEMI_OPTIONAL
              | print_statement SEMI_OPTIONAL
    """
    p[0] = p[1]

# --- Declaración de Variables ---
def p_declaration_short(p):
    """
    declaration : ID DECLARE_ASSIGN expression
    """
    print(f"[INFO SINTÁCTICO] Declaración corta verificada: {p[1]} := ...")
    p[0] = p[1]

def p_declaration_long(p):
    """
    declaration : VAR ID type_spec ASSIGN expression
    """
    print(f"[INFO SINTÁCTICO] Declaración larga verificada: var {p[2]} ...")
    p[0] = p[2]

def p_type_spec(p):
    """
    type_spec : T_INT
              | T_FLOAT
              | T_STRING
              | T_BOOL
    """
    p[0] = p[1]

# --- Estructuras de Control ---
def p_control_structure_if(p):
    """
    control_structure : IF expression LBRACE statement_list RBRACE else_part
    """
    print("[INFO SINTÁCTICO] Estructura IF-ELSE verificada.")
    p[0] = True

def p_else_part(p):
    """
    else_part : ELSE LBRACE statement_list RBRACE
              | empty
    """
    pass

# --- Impresión (Necesaria para fmt.Println) ---
def p_print_statement(p):
    """
    print_statement : ID DOT ID LPAREN arg_list RPAREN
    """
    # Simple check para fmt.Println
    if p[1] == 'fmt' and p[3] == 'Println':
        print(f"[INFO SINTÁCTICO] Llamada a 'fmt.Println' verificada.")
    else:
        # Aquí se debería manejar una llamada a función genérica.
        print(f"[INFO SINTÁCTICO] Llamada a función genérica verificada: {p[1]}.{p[3]}(...)")
    p[0] = p[1]

def p_arg_list(p):
    """
    arg_list : expression COMMA arg_list
             | expression
             | empty
    """
    pass

# --- Expresiones (Aritméticas/Lógicas/Factores) ---

# Regla de expresión principal: incluye operaciones y factores
def p_expression(p):
    """
    expression : expression PLUS expression
               | expression MINUS expression
               | expression TIMES expression
               | expression DIVIDE expression
               | expression MODULO expression
               | expression AND expression
               | expression OR expression
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
    # ACCIÓN SEMÁNTICA: Se realizaría la verificación de tipos aquí.
    if len(p) == 4:
        p[0] = (p[2], p[1], p[3]) # Estructura para el árbol
    elif len(p) == 3:
        p[0] = (p[1], p[2]) # Unarios
    else:
        p[0] = p[1]

# Factores: los elementos más básicos de las expresiones
def p_factor(p):
    """
    factor : INTEGER
           | FLOAT
           | ID
           | STRING_LITERAL
           | LPAREN expression RPAREN
           | TRUE
           | FALSE
           | RAW_STRING
           | RUNE_LITERAL
    """
    if len(p) == 4:
        p[0] = p[2] # ( expression )
    else:
        p[0] = p[1] # Literal, ID, TRUE, FALSE

# Regla de sincronización para el punto y coma (Go lo infiere o se puede escribir)
def p_semi_optional(p):
    """
    SEMI_OPTIONAL : SEMI
                  | empty
    """
    pass

def p_empty(p):
    'empty :'
    p[0] = None


# 3. Manejo de Errores
def p_error(p):
    """
    Regla de manejo de errores sintácticos.
    """
    global syntax_error_flag
    syntax_error_flag = True

    if p:
        print(f"*** ERROR SINTÁCTICO *** Línea {p.lineno}, cerca de '{p.value}' (Token: {p.type}).")
        # Modo pánico: intenta descartar tokens hasta encontrar una llave de cierre o EOF
        while True:
            # Tok.type es None si llegamos al final del archivo
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

# Función que main.py usará
def parse_code(code):
    """Resetea el estado de error y analiza el código."""
    global syntax_error_flag
    syntax_error_flag = False
    parser.parse(code)
    return not syntax_error_flag