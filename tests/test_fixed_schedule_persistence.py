import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.mass import MassSchedule
from app.models.person import Person, ServerType
from app.services.person_service import create_person, update_person


@pytest.fixture
def db_session(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'fixed-schedules.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def api_client(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'fixed-schedules-api.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(bind=engine)

    def override_get_db():
        session = session_local()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(bind=engine)


def test_fixed_schedule_ids_survive_session_reload(db_session):
    schedule = MassSchedule(day_of_week="saturday", time="18:00", is_active=True)
    db_session.add(schedule)
    db_session.commit()

    person = create_person(
        db_session,
        full_name="Pessoa Fixa",
        display_name="Pessoa Fixa",
        server_type=ServerType.COROINHA,
        availability="ambos",
        experience=2,
        fixed_schedule_ids=[schedule.id],
    )
    person_id = person.id
    db_session.expire_all()

    loaded = db_session.get(Person, person_id)
    assert loaded.fixed_schedule_ids == [schedule.id]


def test_update_fixed_schedule_ids_replaces_association(db_session):
    first = MassSchedule(day_of_week="monday", time="19:00", is_active=True)
    second = MassSchedule(day_of_week="friday", time="19:00", is_active=True)
    db_session.add_all([first, second])
    db_session.commit()
    person = create_person(
        db_session,
        full_name="Pessoa Atualizada",
        display_name="Pessoa Atualizada",
        server_type=ServerType.COROINHA,
        availability="ambos",
        fixed_schedule_ids=[first.id],
    )

    update_person(db_session, person.id, fixed_schedule_ids=[second.id])
    db_session.expire_all()
    loaded = db_session.get(Person, person.id)
    assert loaded.fixed_schedule_ids == [second.id]
    assert [schedule.id for schedule in loaded.fixed_schedules] == [second.id]


def test_update_fixed_schedule_ids_empty_clears_association(db_session):
    schedule = MassSchedule(day_of_week="sunday", time="09:00", is_active=True)
    db_session.add(schedule)
    db_session.commit()
    person = create_person(
        db_session,
        full_name="Pessoa Sem Fixo",
        display_name="Pessoa Sem Fixo",
        server_type=ServerType.COROINHA,
        availability="ambos",
        fixed_schedule_ids=[schedule.id],
    )

    update_person(db_session, person.id, fixed_schedule_ids=[])
    db_session.expire_all()
    loaded = db_session.get(Person, person.id)
    assert loaded.fixed_schedule_ids == []
    assert loaded.fixed_schedules == []


def test_person_response_exposes_persisted_fixed_schedule_ids(api_client):
    schedule = api_client.post(
        "/api/horarios",
        json={"day_of_week": "saturday", "time": "18:00", "is_active": True},
    )
    assert schedule.status_code == 201
    schedule_id = schedule.json()["id"]
    created = api_client.post(
        "/api/pessoas",
        json={
            "full_name": "Pessoa API Fixa",
            "display_name": "Pessoa API Fixa",
            "server_type": "coroinha",
            "availability": "ambos",
            "experience": 2,
            "fixed_schedule_ids": [schedule_id],
        },
    )
    assert created.status_code == 201
    person_id = created.json()["id"]
    fetched = api_client.get(f"/api/pessoas/{person_id}")
    assert fetched.status_code == 200
    assert fetched.json()["fixed_schedule_ids"] == [schedule_id]
    api_client.delete(f"/api/pessoas/{person_id}")
