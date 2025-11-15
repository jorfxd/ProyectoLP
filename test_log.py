# test_log.py - Ejecuta el lexer (y opcionalmente el parser) y genera el log requerido
import argparse
from datetime import datetime
from pathlib import Path

from golex import lexer, ERRORS  # Importamos el lexer y la lista de errores léxicos

# Intentamos importar el parser desde el archivo correcto
goparser = None
for candidate in ("goparser", "main", "goYacc", "parser"):
    try:
        goparser = __import__(candidate)
        break
    except Exception:
        pass


def scan_tokens(text):
    """Escanea tokens y devuelve una lista con información detallada."""
    tokens_info = []
    lexer.lineno = 1  # Reiniciar conteo de líneas
    ERRORS.clear()    # Limpiar errores previos
    lexer.input(text)

    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens_info.append({
            'type': tok.type,
            'value': tok.value,
            'line': tok.lineno,
            'lexpos': tok.lexpos,
        })
    return tokens_info


def main():
    ap = argparse.ArgumentParser(description="Generar log léxico y sintáctico")
    ap.add_argument('--user', required=True, help='Usuario Git para el nombre del log')
    ap.add_argument('--input', required=True, help='Archivo .go de prueba')
    ap.add_argument('--parse', action='store_true', help='Analizar sintácticamente también')
    args = ap.parse_args()

    src_path = Path(args.input)
    if not src_path.exists():
        raise SystemExit(f"ERROR: No existe el archivo: {src_path}")

    text = src_path.read_text(encoding='utf-8')
    tokens_info = scan_tokens(text)

    parsed_ok = None
    if args.parse:
        if goparser is not None and hasattr(goparser, "parse_code"):
            parsed_ok = goparser.parse_code(text)
        else:
            print("AVISO: no se encontró parse_code; se omite análisis sintáctico.")

    # Crear carpeta /logs si no existe
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)

    stamp = datetime.now().strftime('%d-%m-%Y-%Hh%M')
    log_name = f"lexico-{args.user}-{stamp}.txt"
    log_path = logs_dir / log_name

    with log_path.open('w', encoding='utf-8') as f:
        f.write(f"Archivo: {src_path.name}\n")
        f.write(f"Usuario: {args.user}\n")
        f.write(f"Fecha: {stamp}\n")
        f.write("\n--- TOKENS ---\n\n")

        for t in tokens_info:
            val = t['value']
            if isinstance(val, str) and len(val) > 40:
                val_show = val[:40] + '…'
            else:
                val_show = val
            f.write(f"{t['type']:<15} line={t['line']:<4} pos={t['lexpos']:<6} value={val_show}\n")

        f.write("\n--- ERRORES LÉXICOS ---\n\n")
        if ERRORS:
            for e in ERRORS:
                f.write(f"{e}\n")
        else:
            f.write("(ninguno)\n")

        if parsed_ok is not None:
            f.write("\n--- PARSEO SINTÁCTICO ---\n\n")
            f.write(f"Resultado: {'OK' if parsed_ok else 'ERRORES'}\n")

    print(f"\n✅ Log generado correctamente en:\n{log_path}\n")


if __name__ == '__main__':
    main()
