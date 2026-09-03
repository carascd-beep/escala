"""Configuração do banco de dados"""
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import os

# Criar diretório data se não existir
if settings.DATABASE_URL.startswith("sqlite"):
    os.makedirs("data", exist_ok=True)


def database_url_options(database_url: str) -> dict:
    """Prepara URL e opções específicas para SQLite ou PostgreSQL."""
    if database_url.startswith(("postgres://", "postgresql://")):
        url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return {"url": url, "connect_args": {}}
    return {"url": database_url, "connect_args": {"check_same_thread": False}}


_database_options = database_url_options(settings.DATABASE_URL)

engine = create_engine(
    _database_options["url"],
    connect_args=_database_options["connect_args"]
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def ensure_schema():
    """Adiciona colunas novas sem apagar dados existentes."""
    inspector = inspect(engine)
    if "persons" in inspector.get_table_names():
        existing = {column["name"] for column in inspector.get_columns("persons")}
        additions = {
            "birth_date": "DATE",
            "availability": "VARCHAR(20)",
            "experience": "INTEGER",
            "fixed_weekdays": "VARCHAR(30)",
        }
        with engine.begin() as connection:
            for name, column_type in additions.items():
                if name not in existing:
                    connection.execute(text(f"ALTER TABLE persons ADD COLUMN {name} {column_type}"))
            connection.execute(text("UPDATE persons SET availability = 'ambos' WHERE lower(trim(availability)) IN ('todo dia', 'todo dias')"))
            connection.execute(text("UPDATE persons SET availability = 'semana' WHERE lower(trim(availability)) = 'dia de semana'"))

    if "mass_schedules" in inspector.get_table_names():
        schedule_columns = {column["name"] for column in inspector.get_columns("mass_schedules")}
        if "participants_count" not in schedule_columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE mass_schedules ADD COLUMN participants_count INTEGER NOT NULL DEFAULT 2"))


def get_db():
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
