from datetime import date

from app.models.person import Person, ServerType
from app.services.schedule_engine import ScheduleParameters, generate_assignments


def person(name, experience, server_type):
    return Person(
        full_name=name, display_name=name, server_type=server_type,
        experience=experience, availability="ambos", is_active=True,
    )


def test_supports_quantity_by_function():
    people = [
        person("Coroinha alta", 3, ServerType.COROINHA),
        person("Coroinha base", 2, ServerType.COROINHA),
        person("Acolito", 2, ServerType.ACOLITO),
    ]
    result = generate_assignments(
        people,
        [{"id": 1, "date": date(2026, 9, 12)}],
        ScheduleParameters(participants_per_scale=3, participants_by_server_type={"coroinha": 2, "acolito": 1}),
    )
    assert {p.server_type for p in result[1]} == {ServerType.COROINHA, ServerType.ACOLITO}
    assert sum(p.server_type == ServerType.COROINHA for p in result[1]) == 2
    assert sum(p.server_type == ServerType.ACOLITO for p in result[1]) == 1


def test_scope_does_not_generate_assignments_for_other_day_type():
    people = [person("Alta", 3, ServerType.COROINHA), person("Base", 1, ServerType.COROINHA)]
    result = generate_assignments(
        people,
        [
            {"id": 1, "date": date(2026, 9, 7)},
            {"id": 2, "date": date(2026, 9, 12)},
        ],
        ScheduleParameters(scope="weekday"),
    )
    assert list(result) == [1]
