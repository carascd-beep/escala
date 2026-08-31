from app.database import database_url_options


def test_sqlite_url_keeps_thread_safety_option():
    options = database_url_options("sqlite:///./data/escala.db")

    assert options["connect_args"] == {"check_same_thread": False}


def test_postgres_url_uses_psycopg_driver_without_sqlite_options():
    options = database_url_options("postgresql://user:pass@host/db")

    assert options["url"] == "postgresql+psycopg2://user:pass@host/db"
    assert options["connect_args"] == {}


def test_supabase_postgres_url_is_not_misclassified_as_sqlite():
    options = database_url_options("postgres://user:pass@host/db?sslmode=require")

    assert options["url"].startswith("postgresql+psycopg2://")
    assert options["connect_args"] == {}
