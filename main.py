## main.py - Orquestador
import sys
from golex import lexer
from goYacc import parse_code
from semant import SemanticAnalyzer

def run_lexical_analysis(code):
    print("\n--- ANÁLISIS LÉXICO ---")
    lexer.input(code)
    for tok in lexer:
        print(tok)

def run_syntax_and_semantic(code):
    # creamos una instancia del analizador semántico para reusar el logname
    sem = SemanticAnalyzer()
    success, ast, sem_errors = parse_code(code, do_semantic=True, sem_logger=sem)
    print("\n--- ANÁLISIS SINTÁCTICO ---")
    if not success:
        print("Se detectaron errores sintácticos (o semánticos).")
    else:
        print("Parsing OK. AST:", ast)
    print("\n--- ERRORES SEMÁNTICOS ---")
    if sem_errors:
        for e in sem_errors:
            print("- ", e)
    else:
        print("No se encontraron errores semánticos.")
    return success

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 main.py archivo.go")
        return
    filename = sys.argv[1]
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print("No se pudo abrir el archivo:", filename)
        return
    run_lexical_analysis(code)
    run_syntax_and_semantic(code)

if __name__ == "__main__":
    main()
