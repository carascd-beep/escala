"""Importação idempotente do cadastro inicial para o banco."""
from datetime import date, timedelta
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.person import Person, ServerType
from app.services.person_service import _canonical_availability
from app.utils.cadastro_import import read_cadastro_excel


def _excel_date(value: str) -> date | None:
    """Converte o número serial de data do Excel para uma data Python."""
    if not value:
        return None
    return date(1899, 12, 30) + timedelta(days=int(float(value)))


def import_cadastro_if_empty(db: Session, excel_path: str | Path) -> int:
    """Importa o Excel apenas quando ainda não há pessoas cadastradas."""
    if db.query(Person).count() > 0:
        return 0

    records = read_cadastro_excel(excel_path)
    for record in records:
        db.add(Person(
            full_name=record["full_name"],
            display_name=record["full_name"],
            server_type=ServerType(record["server_type"]),
            birth_date=_excel_date(record["birth_date_serial"]),
            availability=_canonical_availability(record["availability"]),
            experience=record["experience"],
        ))
    db.commit()
    return len(records)