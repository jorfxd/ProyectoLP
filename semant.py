## semant.py - Analizador semántico simple y logger de errores semánticos
import os
import sys
from datetime import datetime

# NO IMPORTAR goYacc AQUÍ — evita import circular

# El parser SOLO será usado si ejecutas este archivo directamente.
parser_available = False
if __name__ == "__main__":
    try:
        from goYacc import parse_code

        parser_available = True
    except:
        parser_available = False

# El usuario Git se pedirá en main() (NO aquí)
GIT_USER = None  # será asignado por main.py

LOGS_DIR = 'logs'
os.makedirs(LOGS_DIR, exist_ok=True)


def make_log_filename():
    now = datetime.now()
    stamp = now.strftime('%Y%m%d-%H%M')
    user = GIT_USER if GIT_USER else "UnknownUser"
    return f"semantico-{user}-{stamp}.txt"


class SemanticAnalyzer:
    """
    Analizador semántico simple:
      - Tabla de símbolos
      - Reglas básicas
    """

    def __init__(self):
        self.symtab = {}
        self.errors = []
        self.imports = set()

    # Método auxiliar para inferir tipo de expresión
    def infer_type(self, expr):
        """Infiere el tipo de una expresión"""
        if isinstance(expr, int):
            return 'INT_TYPE'
        elif isinstance(expr, float):
            return 'FLOAT_TYPE'
        elif isinstance(expr, str):
            return 'STRING_TYPE'
        elif isinstance(expr, bool):
            return 'BOOL_TYPE'
        elif isinstance(expr, tuple):
            if expr[0] == 'binop':
                left_type = self.infer_type(expr[2])
                right_type = self.infer_type(expr[3])
                if left_type == 'FLOAT_TYPE' or right_type == 'FLOAT_TYPE':
                    return 'FLOAT_TYPE'
                return left_type
            elif expr[0] in ['call']:
                return None
        elif isinstance(expr, str):
            if expr in self.symtab:
                return self.symtab[expr]
        return None

    # Reglas semánticas
    def rule_redeclaration(self, node):
        if not isinstance(node, tuple):
            return

        kind = node[0]

        if kind == "var":
            name = node[1]
            declared_type = node[2]
            if name in self.symtab:
                self.errors.append(f"ERROR SEMÁNTICO: Redeclaración de variable '{name}'")
            else:
                self.symtab[name] = declared_type

        elif kind == "declare_short":
            name = node[1]
            expr = node[2]
            if name in self.symtab:
                self.errors.append(f"ERROR SEMÁNTICO: Redeclaración de variable (:=) '{name}'")
            else:
                inferred = self.infer_type(expr)
                self.symtab[name] = inferred if inferred else "inferred"

    def rule_undefined_var(self, node):
        """Verifica variables no declaradas en expresiones"""
        if isinstance(node, str):
            reserved_words = ['fmt', 'Println', 'main', 'INT_TYPE', 'FLOAT_TYPE',
                              'STRING_TYPE', 'BOOL_TYPE', 'true', 'false']
            operators = ['+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=',
                         '&&', '||', '!', '&', '|', '^', '<<', '>>', '&^']

            if node in self.imports:
                return

            is_valid_identifier = node.replace('_', '').isalnum() and not node[0].isdigit()

            if (is_valid_identifier and
                    node not in self.symtab and
                    node not in reserved_words and
                    node not in operators):
                self.errors.append(f"ERROR SEMÁNTICO: Variable '{node}' no declarada")

    def rule_type_compatibility(self, node):
        if not isinstance(node, tuple):
            return
        kind = node[0]
        if kind == 'var' and len(node) > 3 and node[3] is not None:
            name, declared_type, expr = node[1], node[2], node[3]
            if isinstance(expr, tuple):
                expr_type = self.infer_type(expr)
                if expr_type and expr_type != declared_type:
                    self.errors.append(
                        f"ERROR SEMÁNTICO: Incompatibilidad de tipo en variable '{name}' "
                        f"(esperado {declared_type}, obtenido {expr_type})"
                    )
                return
            if declared_type == 'INT_TYPE' and not isinstance(expr, int):
                self.errors.append(
                    f"ERROR SEMÁNTICO: Incompatibilidad de tipo en variable '{name}' "
                    f"(esperado int, obtenido {type(expr).__name__})"
                )
            elif declared_type == 'FLOAT_TYPE' and not isinstance(expr, (float, int)):
                self.errors.append(
                    f"ERROR SEMÁNTICO: Incompatibilidad de tipo en variable '{name}' "
                    f"(esperado float, obtenido {type(expr).__name__})"
                )
            elif declared_type == 'STRING_TYPE' and not isinstance(expr, str):
                self.errors.append(
                    f"ERROR SEMÁNTICO: Incompatibilidad de tipo en variable '{name}' "
                    f"(esperado string, obtenido {type(expr).__name__})"
                )
            elif declared_type == 'BOOL_TYPE' and not isinstance(expr, bool):
                self.errors.append(
                    f"ERROR SEMÁNTICO: Incompatibilidad de tipo en variable '{name}' "
                    f"(esperado bool, obtenido {type(expr).__name__})"
                )

    def rule_import_check(self, node):
        """Registra imports y verifica su uso"""
        if isinstance(node, tuple):
            if node[0] == 'import':
                pkg_name = node[1]
                self.imports.add(pkg_name)
            elif node[0] == 'call':
                pkg = node[1]
                if pkg not in self.imports and pkg != 'fmt':
                    pass

    # Recorrido del AST
    def traverse(self, node):
        try:
            # Primero procesamos imports
            if isinstance(node, tuple) and node[0] == 'import':
                self.rule_import_check(node)

            # Primero registrar variables
            if isinstance(node, tuple) and node[0] in ['var', 'declare_short']:
                self.rule_redeclaration(node)

            # Verificar compatibilidad de tipos
            self.rule_type_compatibility(node)

            # Revisar variables no declaradas
            should_check = True
            if isinstance(node, str) and node.endswith('_TYPE'):
                should_check = False
            elif isinstance(node, tuple) and node[0] in ['binop', 'unary']:
                should_check = False
            if should_check:
                self.rule_undefined_var(node)

        except Exception as e:
            self.errors.append(f"ERROR INTERNO: Error en semántica: {e}")

        # Recorrido recursivo
        if isinstance(node, tuple):
            if node[0] == 'binop':
                self.traverse(node[2])
                self.traverse(node[3])
            elif node[0] == 'unary':
                self.traverse(node[2])
            elif node[0] in ['var', 'declare_short']:
                if len(node) > 3 and node[3] is not None:
                    self.traverse(node[3])
            else:
                for child in node[1:]:
                    if isinstance(child, list):
                        for elem in child:
                            self.traverse(elem)
                    elif isinstance(child, tuple):
                        self.traverse(child)
        elif isinstance(node, list):
            for elem in node:
                self.traverse(elem)

    # Punto de entrada
    def analyze(self, ast):
        self.symtab = {}
        self.errors = []
        self.imports = set()

        if ast is None:
            self.errors.append("AST vacío - no se ejecutó análisis.")
        else:
            if ast[0] == "program":
                for top in ast[1]:
                    self.traverse(top)
            else:
                self.traverse(ast)

        # Guardar LOG
        filename = os.path.join(LOGS_DIR, make_log_filename())
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("  REPORTE DE ANÁLISIS SEMÁNTICO\n")
            f.write("=" * 60 + "\n\n")

            user = GIT_USER if GIT_USER else "UnknownUser"
            f.write(f"Usuario: {user}\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("TABLA DE SÍMBOLOS:\n")
            f.write("-" * 60 + "\n")
            if self.symtab:
                for name, tipo in self.symtab.items():
                    f.write(f"  {name}: {tipo}\n")
            else:
                f.write("  (vacía)\n")

            f.write("\n" + "=" * 60 + "\n")
            f.write("ERRORES SEMÁNTICOS DETECTADOS:\n")
            f.write("=" * 60 + "\n\n")

            if self.errors:
                for i, e in enumerate(self.errors, 1):
                    f.write(f"{i}. {e}\n")
                f.write(f"\nTotal de errores: {len(self.errors)}\n")
            else:
                f.write("No se encontraron errores semánticos.\n")

        print(f"[SEMÁNTICO] Log guardado en: {filename}")
        return self.errors


# MAIN SOLO SI EJECUTAS ESTE ARCHIVO DIRECTO
def main():
    global GIT_USER

    if not parser_available:
        print("ERROR: No se puede ejecutar semant.py directamente (parser no disponible).")
        return

    user_input = input("GitHub user: ").strip()
    GIT_USER = user_input if user_input else "UnknownUser"
    print(f"Usuario configurado: {GIT_USER}")

    if len(sys.argv) < 2:
        file_path = input("Archivo .go: ").strip()
    else:
        file_path = sys.argv[1]

    try:
        code = open(file_path).read()
    except:
        print("No se pudo abrir:", file_path)
        return

    print(f"[INFO] Usuario para el log: {GIT_USER}")
    print("[INFO] Parseando archivo...")
    success, ast, errors = parse_code(code, git_user=GIT_USER)

    print("\n=== RESULTADO DEL ANÁLISIS SEMÁNTICO ===")
    if errors:
        for e in errors:
            print(" -", e)
    else:
        print("Sin errores semánticos")


if __name__ == "__main__":
    main()
