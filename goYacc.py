# goYacc.py - Analizador sintáctico + integración semántica

import ply.yacc as yacc
from golex import tokens
from semant import SemanticAnalyzer

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'EQ', 'NE', 'LT', 'LE', 'GT', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MODULO'),
    ('right', 'UMINUS', 'NOT'),
)

syntax_error_flag = False


#   REGLAS DEL PARSER
def p_program(p):
    """program : top_declaration_list"""
    p[0] = ('program', p[1])

def p_top_declaration_list(p):
    """top_declaration_list : top_declaration top_declaration_list
                             | top_declaration"""
    p[0] = [p[1]] + p[2] if len(p) == 3 else [p[1]]

def p_top_declaration(p):
    """
    top_declaration : PACKAGE ID
                    | IMPORT STRING_LITERAL
                    | FUNC ID LPAREN param_list RPAREN func_return LBRACE statement_list RBRACE
    """
    if p[1] == 'package':
        p[0] = ('package', p[2])
    elif p[1] == 'import':
        p[0] = ('import', p[2])
    elif p[1] == 'func':
        p[0] = ('func', p[2], p[4], p[6], p[8])

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
    elif p[1] is None:
        p[0] = []
    else:
        p[0] = [p[1]]

def p_param(p):
    """param : ID type_spec"""
    p[0] = (p[1], p[2])

def p_statement_list(p):
    """statement_list : statement statement_list
                      | empty"""
    if len(p) == 3:
        p[0] = [p[1]] + p[2] if p[1] is not None else p[2]
    else:
        p[0] = []

def p_statement(p):
    """statement : VAR ID type_spec ASSIGN expression SEMI
                 | VAR ID type_spec SEMI
                 | ID DECLARE_ASSIGN expression SEMI
                 | ID ASSIGN expression SEMI
                 | control_structure
                 | expression SEMI
                 | SEMI"""
    if len(p) == 2:
        # Solo SEMI (statement vacío)
        p[0] = ('empty_stmt',)
    elif len(p) == 3:
        # expression SEMI
        p[0] = p[1]
    elif len(p) == 5:
        # ID DECLARE_ASSIGN expression SEMI o ID ASSIGN expression SEMI o VAR ID type_spec SEMI
        if p[1] == 'var':
            p[0] = ('var', p[2], p[3], None)
        elif p.slice[2].type == 'DECLARE_ASSIGN':
            p[0] = ('declare_short', p[1], p[3])
        else:
            p[0] = ('assign', p[1], p[3])
    elif len(p) == 7:
        # VAR ID type_spec ASSIGN expression SEMI
        p[0] = ('var', p[2], p[3], p[5])

def p_type_spec(p):
    """type_spec : INT_TYPE
                 | FLOAT_TYPE
                 | STRING_TYPE
                 | BOOL_TYPE"""
    mapping = {
        'int': 'INT_TYPE',
        'float64': 'FLOAT_TYPE',
        'string': 'STRING_TYPE',
        'bool': 'BOOL_TYPE'
    }
    p[0] = mapping.get(p[1], p[1])

def p_control_structure_if(p):
    """control_structure : IF expression LBRACE statement_list RBRACE else_part"""
    p[0] = ('if', p[2], p[4], p[6])

def p_else_part(p):
    """else_part : ELSE LBRACE statement_list RBRACE
                 | empty"""
    p[0] = p[3] if len(p) == 5 else None

def p_arg_list(p):
    """arg_list : expression COMMA arg_list
                | expression
                | empty"""
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    elif len(p) == 2:
        p[0] = [p[1]] if p[1] else []
    else:
        p[0] = []

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
              | ID DOT ID LPAREN arg_list RPAREN
              | LPAREN expression RPAREN"""
    if len(p) == 4:
        p[0] = p[2]  # (expression)
    elif len(p) == 7:
        p[0] = ('call', p[1], p[3], p[5])  # ID.ID(args)
    else:
        p[0] = p[1]

def p_empty(p):
    "empty :"
    p[0] = None

def p_error(p):
    global syntax_error_flag
    syntax_error_flag = True
    if p:
        print(f"*** ERROR SINTÁCTICO *** Línea {p.lineno}, cerca de '{p.value}'")
        # Intentar recuperarse
        while True:
            tok = parser.token()
            if not tok or tok.type in ('RBRACE', 'SEMI'):
                break
        parser.errok()
    else:
        print("*** ERROR SINTÁCTICO *** Fin del archivo inesperado")

# Construir parser
parser = yacc.yacc()


#       FUNCIÓN FINAL parse_code()
def parse_code(code, do_semantic=True, sem_logger=None, git_user=None):
    """
    Retorna:
      (success, ast, sem_errors)
    """
    global syntax_error_flag
    syntax_error_flag = False

    ast = parser.parse(code)

    if syntax_error_flag:
        return (False, None, [])

    # Si no se quiere análisis semántico
    if not do_semantic:
        return (True, ast, [])

    # Configurar usuario de GitHub antes de crear el analizador
    if git_user:
        import semant as sem_module
        sem_module.GIT_USER = git_user

    # Ejecutar semántico
    sem = sem_logger or SemanticAnalyzer()
    sem_errors = sem.analyze(ast)

    success = len(sem_errors) == 0
    return (success, ast, sem_errors)