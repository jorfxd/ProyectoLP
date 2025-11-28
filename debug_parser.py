#!/usr/bin/env python3
# debug_parser.py - Script para diagnosticar el problema del parser

from golex import lexer

# Código de prueba
test_code = """package main

import "fmt"

func main() {
    mensaje := "Hello, world!";
    fmt.Println(mensaje);
}
"""

print("="*60)
print("PRUEBA 1: Tokens generados por el lexer")
print("="*60)

lexer.input(test_code)
tokens_list = []
for tok in lexer:
    tokens_list.append(tok)
    print(f"Línea {tok.lineno}: {tok.type:20s} = {repr(tok.value)}")

print(f"\nTotal tokens: {len(tokens_list)}")

print("\n" + "="*60)
print("PRUEBA 2: Intentar parsear")
print("="*60)

# Eliminar archivos cache
import os
if os.path.exists('parser.out'):
    os.remove('parser.out')
if os.path.exists('parsetab.py'):
    os.remove('parsetab.py')

from goYacc import parse_code

success, ast, errors = parse_code(test_code, do_semantic=True, git_user="TestUser")

print(f"\nÉxito del parsing: {success}")
print(f"AST generado: {ast is not None}")
print(f"Errores semánticos: {len(errors)}")

if success:
    print("\n✔ Parsing exitoso!")
    print("\nAST generado:")
    print(ast)
    
    if errors:
        print("\nErrores semánticos encontrados:")
        for err in errors:
            print(f"  - {err}")
    else:
        print("\n Sin errores semánticos")
else:
    print("\n Parsing falló")
    print("No se pudo generar el AST")