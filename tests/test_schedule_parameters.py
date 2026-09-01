from datetime import date

from app.models.person import Person, ServerType
from app.models.mass import DayOfWeek
from app.services.schedule_engine import ScheduleParameters, generate_assignments


def person(name, experience, availability="ambos", fixed_schedule_ids=None):
    return Person(
        id=None, full_name=name, display_name=name, server_type=ServerType.COROINHA,
        experience=experience, availability=availability, is_active=True,
        fixed_schedule_ids=fixed_schedule_ids or [],
    )


def test_engine_accepts_participant_count_and_weekend_scope():
    people = [person("Alta", 3, "fim de semana"), person("Media", 2, "fim de semana"), person("Baixa", 1, "fim de semana")]
    masses = [{"id": 1, "date": date(2026, 9, 12), "schedule_id": 4}]

    result = generate_assignments(people, masses, ScheduleParameters(scope="weekend", participants_per_scale=3))

    assert len(result[1]) == 3
    assert sum(p.experience == 3 for p in result[1]) >= 1


def test_engine_respects_fixed_schedule_id():
    people = [person("Alta", 3, "semana", [7]), person("Media", 2, "semana", [7])]
    masses = [{"id": 1, "date": date(2026, 9, 7), "schedule_id": 7}]

    result = generate_assignments(people, masses, ScheduleParameters(participants_per_scale=2))

    assert {p.display_name for p in result[1]} == {"Alta", "Media"}


def test_schedule_schema_has_crud_fields():
    from app.schemas.mass import MassScheduleUpdate
    assert set(MassScheduleUpdate.model_fields) >= {"day_of_week", "time", "description", "is_active"}
