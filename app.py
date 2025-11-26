
from flask import Flask, render_template, request
from golex import lexer, ERRORS
from goYacc import parse_code
import semant

app = Flask(__name__)


def run_lexical(code: str):
    """Ejecuta SOLO el análisis léxico y devuelve tokens + errores léxicos."""
    ERRORS.clear()
    lexer.lineno = 1
    lexer.input(code)

    tokens = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens.append({
            "type": tok.type,
            "value": repr(tok.value),
            "line": tok.lineno,
            "pos": tok.lexpos,
        })

    # ERRORS es llenado (si quieres) en golex.t_error
    lex_errors = list(ERRORS)
    return tokens, lex_errors


@app.route("/", methods=["GET", "POST"])
def index():
    code = ""
    github_user = ""
    result = None

    if request.method == "POST":
        code = request.form.get("code", "")
        github_user = request.form.get("github_user", "").strip() or "UnknownUser"

        # Configuramos el usuario de Git en el módulo semántico
        semant.GIT_USER = github_user

        # 1) Análisis léxico
        tokens, lex_errors = run_lexical(code)

        # 2) Análisis sintáctico + semántico (ya usa tu parse_code)
        syntax_ok, ast, sem_errors = parse_code(
            code,
            do_semantic=True,
            git_user=github_user
        )

        # Empaquetamos todo para la plantilla
        result = {
            "tokens": tokens,
            "lex_errors": lex_errors,
            "syntax_ok": syntax_ok,
            "ast": ast,
            "sem_errors": sem_errors,
        }

    return render_template(
        "index.html",
        code=code,
        github_user=github_user,
        result=result
    )


if __name__ == "__main__":
    # debug=True solo para desarrollo local
    app.run(debug=True)
