from datetime import date

import pytest

from app.models.person import Person, ServerType
from app.services.schedule_engine import generate_assignments


def person(name, experience, availability="ambos"):
    return Person(
        id=None,
        full_name=name,
        display_name=name,
        server_type=ServerType.COROINHA,
        experience=experience,
        availability=availability,
        is_active=True,
    )


def test_generates_two_people_per_mass_with_experienced_pairing_and_equity():
    people = [
        person("Alta semana", 3, "semana"),
        person("Alta fim", 3, "fim de semana"),
        person("Media semana", 2, "semana"),
        person("Baixa fim", 1, "fim de semana"),
    ]
    masses = [
        {"id": 1, "date": date(2026, 9, 7)},
        {"id": 2, "date": date(2026, 9, 12)},
    ]

    result = generate_assignments(people, masses)

    assert all(len(pair) == 2 for pair in result.values())
    assert {p.display_name for pair in result.values() for p in pair} == {
        p.display_name for p in people
    }
    assert result[1][0].experience == 3
    assert result[1][1].experience in (1, 2)
    assert result[2][0].experience == 3
    assert result[2][1].experience in (1, 2)


def test_respects_weekday_and_weekend_availability():
    people = [person("Alta", 3, "semana"), person("Base", 1, "semana")]
    masses = [{"id": 1, "date": date(2026, 9, 7)}]

    result = generate_assignments(people, masses)

    assert [p.display_name for p in result[1]] == ["Alta", "Base"]


def test_fails_when_strict_rules_are_impossible():
    people = [person("Alta", 3, "semana")]
    masses = [{"id": 1, "date": date(2026, 9, 7)}]

    with pytest.raises(ValueError, match="não foi possível"):
        generate_assignments(people, masses)


def test_person_self_view_schema_does_not_expose_experience():
    from app.schemas.person import PersonSelfResponse

    assert "experience" not in PersonSelfResponse.model_fields
    assert "availability" in PersonSelfResponse.model_fields
