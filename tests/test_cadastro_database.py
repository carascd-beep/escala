from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.person import Person
from app.services.cadastro_service import import_cadastro_if_empty


EXCEL_PATH = Path(__file__).parents[1] / "docs" / "CadastroCoroinhas.xlsx"


def test_import_cadastro_persists_records_and_is_idempotent(tmp_path):
    engine = create_engine("sqlite:///%s" % (tmp_path / "cadastro.db"))
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()

    assert import_cadastro_if_empty(session, EXCEL_PATH) == 47
    assert session.query(Person).count() == 47
    assert session.query(Person).filter_by(server_type="acolito").count() == 12

    assert import_cadastro_if_empty(session, EXCEL_PATH) == 0
    assert session.query(Person).count() == 47

    session.close()
