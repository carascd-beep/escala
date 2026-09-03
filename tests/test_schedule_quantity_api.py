import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def api_client(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'schedule.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(bind=engine)

    def override_get_db():
        db = session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_schedule_crud_persists_participants_count(api_client):
    client = api_client
    created = client.post("/api/horarios", json={
        "day_of_week": "saturday",
        "time": "22:55",
        "description": "Teste quantidade",
        "participants_count": 4,
    })
    assert created.status_code == 201
    schedule_id = created.json()["id"]
    assert created.json()["participants_count"] == 4

    fetched = client.get(f"/api/horarios/{schedule_id}")
    assert fetched.status_code == 200
    assert fetched.json()["participants_count"] == 4

    updated = client.put(f"/api/horarios/{schedule_id}", json={"participants_count": 5})
    assert updated.status_code == 200
    assert updated.json()["participants_count"] == 5

    deleted = client.delete(f"/api/horarios/{schedule_id}")
    assert deleted.status_code == 204
