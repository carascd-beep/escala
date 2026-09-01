from datetime import date

import pytest

from app.models.person import Person, ServerType
from app.services.schedule_engine import ScheduleParameters, generate_assignments


def person(name, experience, availability="ambos", fixed_weekdays=None):
    return Person(
        full_name=name,
        display_name=name,
        server_type=ServerType.COROINHA,
        experience=experience,
        availability=availability,
        is_active=True,
        fixed_weekdays=fixed_weekdays or [],
    )


def test_fixed_weekday_is_prioritized():
    people = [
        person("Alta terça", 3, fixed_weekdays=[1]),
        person("Base terça", 1, fixed_weekdays=[1]),
        person("Alta sem preferência", 3),
        person("Base sem preferência", 1),
    ]

    result = generate_assignments(
        people,
        [{"id": 1, "date": date(2026, 9, 8)}],
        ScheduleParameters(),
    )

    assert [p.display_name for p in result[1][:2]] == ["Alta terça", "Base terça"]


def test_very_low_experience_requires_at_least_three_people():
    people = [
        person("Muito baixa", 0),
        person("Alta", 3),
        person("Média", 2),
    ]

    result = generate_assignments(
        people,
        [{"id": 1, "date": date(2026, 9, 8)}],
        ScheduleParameters(participants_per_scale=2),
    )

    assert len(result[1]) >= 3
    assert any(p.experience == 0 for p in result[1])


def test_capacity_expands_to_cover_all_available_people():
    people = [
        person("Alta", 3),
        person("Base 1", 1),
        person("Base 2", 1),
        person("Base 3", 1),
    ]

    result = generate_assignments(
        people,
        [{"id": 1, "date": date(2026, 9, 8)}],
        ScheduleParameters(participants_per_scale=2),
    )

    assert {p.display_name for p in result[1]} == {
        "Alta", "Base 1", "Base 2", "Base 3"
    }
