# main.py - Orquestador PRINCIPAL
import sys
from golex import lexer
from goYacc import parse_code
import semant

def run_lexical_analysis(code):
    print("\n" + "="*60)
    print("   ANÁLISIS LÉXICO")
    print("="*60)
    lexer.input(code)
    tokens_list = []
    for tok in lexer:
        tokens_list.append(tok)
        print(f"  {tok}")
    print(f"\nTotal de tokens: {len(tokens_list)}")
    return tokens_list

def run_syntax_and_semantic(code, github_user):
    print("\n" + "="*60)
    print("   ANÁLISIS SINTÁCTICO Y SEMÁNTICO")
    print("="*60)
    
    # Configurar usuario de GitHub en el módulo semant
    semant.GIT_USER = github_user
    
    success, ast, sem_errors = parse_code(code, do_semantic=True, git_user=github_user)

    if not success:
        print("\nSe detectaron errores sintácticos.")
        print("   El análisis semántico no se pudo completar.")
        return False
    
    print("\n✔ Análisis sintáctico completado exitosamente")
    print("\nÁRBOL DE SINTAXIS ABSTRACTA (AST):")
    print("-"*60)
    print(ast)

    print("\n" + "="*60)
    print("   ERRORES SEMÁNTICOS DETECTADOS")
    print("="*60)
    if sem_errors:
        for i, err in enumerate(sem_errors, 1):
            print(f"{i}. {err}")
        print(f"\nTotal de errores semánticos: {len(sem_errors)}")
    else:
        print("✔ No se encontraron errores semánticos.")

    return success

def main():
    print("="*60)
    print("         ANALIZADOR DE GO LITE")
    print("="*60)

    # Solicitar usuario GitHub
    github_user = input("\nIngresa tu usuario de GitHub: ").strip()
    if not github_user:
        github_user = "UnknownUser"
    print(f"Usuario: {github_user}")

    # Revisión de argumentos
    if len(sys.argv) < 2:
        print("\n Error: Debes proporcionar un archivo .go")
        print("Uso: python3 main.py archivo.go")
        return

    filename = sys.argv[1]
    print(f"Archivo: {filename}")

    # Leer el archivo
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"\nError: No se pudo abrir el archivo: {filename}")
        return
    except Exception as e:
        print(f"\nError al leer el archivo: {e}")
        return

    # Ejecutar análisis léxico
    run_lexical_analysis(code)
    
    # Ejecutar análisis sintáctico y semántico
    run_syntax_and_semantic(code, github_user)
    
    print("\n" + "="*60)
    print("   ANÁLISIS COMPLETADO")
    print("="*60)


if __name__ == "__main__":
    main()