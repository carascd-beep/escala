"""Testa a conexão PostgreSQL sem expor a DATABASE_URL."""
import os
import sys

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


def main() -> int:
    raw_url = os.getenv("DATABASE_URL", "").strip()
    if not raw_url:
        print("ERRO: defina DATABASE_URL no ambiente antes de executar.")
        return 2

    try:
        url = make_url(raw_url)
        safe_url = url.render_as_string(hide_password=True)
        engine = create_engine(raw_url, pool_pre_ping=True, connect_args={"connect_timeout": 10})
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.scalar_one()
        print(f"OK: conexão realizada com {safe_url}")
        return 0
    except Exception as error:  # noqa: BLE001 - script diagnóstico
        message = str(error)
        if raw_url:
            message = message.replace(raw_url, "<DATABASE_URL ocultada>")
        print(f"FALHA: {message}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
