from datetime import date

from app.models.person import Person, ServerType
from app.services.schedule_engine import ScheduleParameters, generate_assignments


def person(name, experience, server_type):
    return Person(
        full_name=name,
        display_name=name,
        server_type=server_type,
        experience=experience,
        availability="ambos",
        is_active=True,
    )


def test_prioritizes_coroinhas_before_acolitos_when_slots_are_limited():
    people = [
        person("Coroinha experiente", 3, ServerType.COROINHA),
        person("Coroinha iniciante", 1, ServerType.COROINHA),
        person("Acolito", 2, ServerType.ACOLITO),
    ]

    result = generate_assignments(
        people,
        [{"id": 1, "date": date(2026, 9, 12)}],
        ScheduleParameters(participants_per_scale=2),
    )

    assigned = result[1]
    assert assigned[0].server_type == ServerType.COROINHA
    assert assigned[1].server_type == ServerType.COROINHA
    assert "Acolito" in {person.display_name for person in assigned}


def test_can_override_function_priority_explicitly():
    people = [
        person("Coroinha experiente", 3, ServerType.COROINHA),
        person("Acolito experiente", 3, ServerType.ACOLITO),
    ]

    result = generate_assignments(
        people,
        [{"id": 1, "date": date(2026, 9, 12)}],
        ScheduleParameters(
            participants_per_scale=2,
            priority_server_types=("acolito", "coroinha"),
        ),
    )

    assert result[1][0].server_type == ServerType.ACOLITO
    assert result[1][1].server_type == ServerType.COROINHA
