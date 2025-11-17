# semant.py - Analizador semántico simple y logger de errores semánticos
import os
from datetime import datetime

# Cambia aquí si quieres otro usuario Git en el nombre de archivo:
GIT_USER = 'francis'  # <- modifica si tu usuario Git es otro

LOGS_DIR = 'logs'
os.makedirs(LOGS_DIR, exist_ok=True)

def make_log_filename():
    now = datetime.now()
    stamp = now.strftime('%Y%m%d-%H%M')
    return f"semantico-{GIT_USER}-{stamp}.txt"

class SemanticAnalyzer:
    """
    Analizador semántico muy simple, mantiene:
     - tabla de símbolos (variables -> tipo)
     - lista de errores semánticos
    Regla = función que recorre AST y agrega errores cuando aplica.
    """
    def __init__(self):
        self.symtab = {}  # nombre -> tipo (str)
        self.errors = []

    # --------------------
    # Reglas semánticas
    # --------------------

    # Regla semántica (Francis - 1):
    # Verificar redeclaración de variables en el mismo scope (error)
    def rule_redeclaration(self, node):
        # busca nodos ('var', name, type, expr) y ('declare_short', name, expr)
        if not isinstance(node, tuple):
            return
        kind = node[0]
        if kind == 'var':
            name = node[1]
            if name in self.symtab:
                self.errors.append(f"Redeclaración de variable '{name}'")
            else:
                self.symtab[name] = node[2]
        elif kind == 'declare_short':
            name = node[1]
            if name in self.symtab:
                self.errors.append(f"Redeclaración de variable (:=) '{name}'")
            else:
                # tipo será inferido por la expresión si es literal; guardamos 'inferred' placeholder
                self.symtab[name] = 'inferred'

    # Regla semántica (Francis - 2):
    # Verificar uso de variable no declarada (error)
    def rule_undefined_var(self, node):
        # Si nodo es ('assign' or use of ID in expression) e ID no está en tabla => error
        if not isinstance(node, tuple):
            return
        kind = node[0]
        if kind == 'assign':
            name = node[1]
            if name not in self.symtab:
                self.errors.append(f"Asiganción a variable no declarada '{name}'")
        # en expresiones se valida en traverse

    # Regla semántica: comprobación básica de tipos en asignaciones literales
    def rule_type_compatibility(self, node):
        # Si var tiene tipo declarado y se asigna un literal incompatible -> error
        if not isinstance(node, tuple):
            return
        kind = node[0]
        if kind == 'var' and node[3] is not None:
            name, declared_type, expr = node[1], node[2], node[3]
            # expr puede ser INT_LITERAL (int) o FLOAT_LITERAL (float) o STRING_LITERAL
            if isinstance(expr, tuple):
                # expresion compleja -> saltar verificacion simple
                return
            if declared_type == 'INT_TYPE' and not isinstance(expr, int):
                self.errors.append(f"Incompatibilidad de tipo: var {name} {declared_type} = {expr}")
            if declared_type == 'FLOAT_TYPE' and not (isinstance(expr, float) or isinstance(expr, int)):
                self.errors.append(f"Incompatibilidad de tipo: var {name} {declared_type} = {expr}")
            if declared_type == 'STRING_TYPE' and not isinstance(expr, str):
                self.errors.append(f"Incompatibilidad de tipo: var {name} {declared_type} = {expr}")

    # Regla semántica: llamada a fmt.Println permite cualquier tipo (solo ejemplo),
    # pero detectamos llamadas a funciones no importadas (muy simple)
    def rule_import_check(self, node):
        if not isinstance(node, tuple):
            return
        if node[0] == 'call':
            pkg = node[1]
            if pkg == 'fmt':
                return
            # si se llama a otro paquete y no hay import explícito, avisar
            # (esto es simplificado: comprobamos si 'import' aparece en symtab as keys)
            if pkg not in self.symtab:
                self.errors.append(f"Llamada a paquete '{pkg}' sin import declarado (sintético)")

    # Reglas adicionales (ejemplos):
    def rule_no_return_in_func(self, node):
        # placeholder: se podría verificar que funciones que declaran tipo devuelvan algo
        return

    # --------------------
    # Recorrido del AST
    # --------------------
    def traverse(self, node):
        """
        Recorrido DFS del AST. Para cada nodo se aplican reglas.
        """
        # aplicar las reglas que inspeccionan el nodo
        try:
            self.rule_redeclaration(node)
            self.rule_undefined_var(node)
            self.rule_type_compatibility(node)
            self.rule_import_check(node)
        except Exception as e:
            # proteccion para no romper el analizador
            self.errors.append(f"Excepción interna en reglas semánticas: {e}")

        # recursión según tipo
        if isinstance(node, tuple):
            for child in node[1:]:
                if isinstance(child, list):
                    for elem in child:
                        self.traverse(elem)
                else:
                    self.traverse(child)

    # --------------------
    # Punto de entrada
    # --------------------
    def analyze(self, ast):
        """
        ast: ('program', [declarations...])
        Retorna lista de errores semánticos (strings). También crea un log en carpeta logs/.
        """
        self.symtab = {}
        self.errors = []

        if ast is None:
            self.errors.append("AST vacío - no se analizó nada.")
        else:
            # Recorrer todo el AST
            if ast[0] == 'program':
                for top in ast[1]:
                    self.traverse(top)
            else:
                self.traverse(ast)

        # Escribir log
        filename = os.path.join(LOGS_DIR, make_log_filename())
        with open(filename, 'w', encoding='utf-8') as f:
            if self.errors:
                f.write("Errores semánticos encontrados:\n")
                for e in self.errors:
                    f.write("- " + e + "\n")
            else:
                f.write("No se encontraron errores semánticos.\n")
        print(f"[SEMÁNTICO] Log de semántica creado: {filename}")
        return self.errors
