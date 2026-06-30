import sys

from api import create_app


try:
    app = create_app()
except Exception:
    print(
        "[API] Não foi possível iniciar. Verifique se o banco está rodando.\n"
        "[API] Comando esperado: docker compose up -d\n"
        "[API] Porta esperada do PostgreSQL: localhost:5433"
    )
    sys.exit(1)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
