from datetime import date

import pytest

from app.models.mass import DayOfWeek
from app.models.person import Person, ServerType
from app.services.schedule_engine import ScheduleParameters, generate_assignments


def person(name, experience=3, availability="semana", fixed_weekdays=None, fixed_schedule_ids=None):
    return Person(
        id=None,
        full_name=name,
        display_name=name,
        server_type=ServerType.COROINHA,
        experience=experience,
        availability=availability,
        is_active=True,
        fixed_weekdays=fixed_weekdays or [],
        fixed_schedule_ids=fixed_schedule_ids or [],
    )


def masses(*items):
    return [
        {"id": index, "date": day, "schedule_id": schedule_id}
        for index, (day, schedule_id) in enumerate(items, start=1)
    ]


def test_weekday_person_serves_at_most_once_per_calendar_month():
    people = [person("Ana", 3), person("Apoio", 3), person("Reserva", 3)]
    selected = masses((date(2026, 9, 3), 1), (date(2026, 9, 17), 1))

    result = generate_assignments(
        people,
        selected,
        ScheduleParameters(participants_per_scale=1),
    )

    ana_assignments = sum(
        any(p.display_name == "Ana" for p in assignment)
        for assignment in result.values()
    )
    assert ana_assignments <= 1


def test_weekday_person_can_serve_again_in_another_month():
    people = [person("Ana", 3), person("Apoio", 3)]
    selected = masses((date(2026, 9, 3), 1), (date(2026, 10, 2), 1))

    result = generate_assignments(
        people,
        selected,
        ScheduleParameters(participants_per_scale=1),
    )

    months = {(selected[mass_id - 1]["date"].year, selected[mass_id - 1]["date"].month)
              for mass_id in result}
    assert months == {(2026, 9), (2026, 10)}
    for assignment in result.values():
        assert len(assignment) == 1


def test_exact_fixed_weekday_and_schedule_can_repeat_in_same_month():
    fixed = person("Ana", 3, fixed_weekdays=[3], fixed_schedule_ids=[1])
    people = [fixed, person("Apoio", 2), person("Reserva", 1)]
    selected = masses((date(2026, 9, 3), 1), (date(2026, 9, 17), 1))

    result = generate_assignments(
        people,
        selected,
        ScheduleParameters(participants_per_scale=1),
    )

    assert all(any(p.display_name == "Ana" for p in assignment) for assignment in result.values())


def test_fixed_day_without_exact_schedule_does_not_bypass_monthly_limit():
    person_with_wrong_schedule = person("Ana", 3, fixed_weekdays=[3], fixed_schedule_ids=[2])
    people = [person_with_wrong_schedule, person("Apoio", 3), person("Reserva", 3)]
    selected = masses((date(2026, 9, 3), 1), (date(2026, 9, 17), 1))

    result = generate_assignments(people, selected, ScheduleParameters(participants_per_scale=1))
    assert all(not any(p.display_name == "Ana" for p in assignment) for assignment in result.values())


def test_each_mass_uses_its_schedule_participant_count():
    people = [person("Alta", 3, "ambos"), person("Média", 2, "ambos"), person("Baixa", 1, "ambos")]
    selected = [
        {"id": 1, "date": date(2026, 9, 3), "schedule_id": 1, "participants_count": 1},
        {"id": 2, "date": date(2026, 9, 5), "schedule_id": 2, "participants_count": 3},
    ]

    result = generate_assignments(people, selected, ScheduleParameters(participants_per_scale=2))

    assert len(result[1]) == 1
    assert len(result[2]) == 3


def test_schedule_count_must_be_positive():
    with pytest.raises(ValueError):
        ScheduleParameters(participants_per_scale=0)
