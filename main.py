# main.py - Orquestador y Clase Principal

import sys
# Importamos las herramientas de análisis
from golex import lexer
from goYacc import parse_code


def run_lexical_analysis(code):
    """
    Ejecuta solo el análisis léxico y muestra los tokens.
    """
    print("\n--- INICIANDO ANÁLISIS LÉXICO ---")
    lexer.input(code)
    tokens_list = []

    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens_list.append(f"Tipo: {tok.type:<15} Valor: {repr(tok.value):<15} Línea: {tok.lineno}")

    # Reiniciar el lexer para el sintáctico si fuera necesario
    lexer.lineno = 1
    lexer.lexpos = 0

    if tokens_list:
        print("Tokens Encontrados:")
        print("\n".join(tokens_list))
    else:
        print("No se encontraron tokens válidos.")
    print("--- ANÁLISIS LÉXICO FINALIZADO ---\n")
    return tokens_list


def run_syntax_analysis(code):
    """
    Ejecuta el análisis sintáctico.
    """
    print("\n--- INICIANDO ANÁLISIS SINTÁCTICO ---")

    # parse_code() llamará al parser y manejará los errores.
    success = parse_code(code)

    if success:
        print("\n ÉXITO: El análisis sintáctico completó sin errores.")
    else:
        print("\n FALLO: Se encontraron errores sintácticos en el código.")
    print("--- ANÁLISIS SINTÁCTICO FINALIZADO ---\n")


def main():
    """
    Función principal que simula la interacción con el usuario/GUI.
    """
    print("====================================================")
    print(" ANALIZADOR LÉXICO Y SINTÁCTICO DE GO (PLY)")
    print("====================================================\n")

    # Algoritmo de prueba (Ejemplo de un integrante)
    codigo_go_ejemplo = """
package main 

import "fmt"

func main() {
    var contador int = 100;
    
    // Pruebas léxicas y sintácticas de expresiones
    x := 5 + 3.14 * (10 % 2);

    if x < 10 && contador == 100 {
        fmt.Println("Todo OK"); 
    } else {
        otro := 10;
        // La sentencia "otro := 10;" es una declaración corta.
    }
}
"""
    print("CÓDIGO DE ENTRADA:\n------------------------------------")
    print(codigo_go_ejemplo)
    print("------------------------------------\n")

    # 1. Ejecutar Fase Léxica
    run_lexical_analysis(codigo_go_ejemplo)

    # 2. Ejecutar Fase Sintáctica
    run_syntax_analysis(codigo_go_ejemplo)


if __name__ == '__main__':
    main()