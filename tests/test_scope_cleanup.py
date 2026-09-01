from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.mass import Mass, MassSchedule, DayOfWeek
from app.models.scale import Scale
from app.services.mass_service import generate_masses_for_period
from app.services.scale_engine_adapter import clear_unpublished_scales


@pytest.fixture
def db_session(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'scope_cleanup.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_generate_masses_respects_weekday_scope(db_session):
    db_session.add_all([
        MassSchedule(day_of_week=DayOfWeek.MONDAY, time="19:00", is_active=True),
        MassSchedule(day_of_week=DayOfWeek.SATURDAY, time="18:00", is_active=True),
    ])
    db_session.commit()

    created = generate_masses_for_period(
        db_session, date(2026, 9, 7), date(2026, 9, 13), scope="weekday"
    )

    assert created == 1
    assert [mass.date.weekday() for mass in db_session.query(Mass).all()] == [0]


def test_clear_unpublished_scales_removes_agenda_but_preserves_published(db_session):
    monday_schedule = MassSchedule(
        day_of_week=DayOfWeek.MONDAY, time="19:00", is_active=True
    )
    tuesday_schedule = MassSchedule(
        day_of_week=DayOfWeek.TUESDAY, time="19:00", is_active=True
    )
    db_session.add_all([monday_schedule, tuesday_schedule])
    db_session.commit()

    draft_mass = Mass(
        date=date(2026, 9, 7), time="19:00", schedule_id=monday_schedule.id
    )
    published_mass = Mass(
        date=date(2026, 9, 8), time="19:00", schedule_id=tuesday_schedule.id
    )
    db_session.add_all([draft_mass, published_mass])
    db_session.commit()

    draft_scale = Scale(mass_id=draft_mass.id, published=False)
    published_scale = Scale(mass_id=published_mass.id, published=True)
    db_session.add_all([draft_scale, published_scale])
    db_session.commit()

    result = clear_unpublished_scales(
        db_session, date(2026, 9, 1), date(2026, 9, 30), scope="weekday"
    )

    assert result == {"assignments": 0, "masses": 1}
    assert db_session.query(Mass).filter(Mass.id == draft_mass.id).one_or_none() is None
    assert db_session.query(Mass).filter(Mass.id == published_mass.id).one_or_none() is not None
    assert db_session.query(Scale).filter(Scale.id == published_scale.id).one_or_none() is not None


def test_clear_scope_does_not_remove_out_of_scope_draft(db_session):
    saturday_schedule = MassSchedule(
        day_of_week=DayOfWeek.SATURDAY, time="18:00", is_active=True
    )
    db_session.add(saturday_schedule)
    db_session.commit()
    mass = Mass(
        date=date(2026, 9, 12), time="18:00", schedule_id=saturday_schedule.id
    )
    db_session.add(mass)
    db_session.commit()
    scale = Scale(mass_id=mass.id, published=False)
    db_session.add(scale)
    db_session.commit()

    clear_unpublished_scales(
        db_session, date(2026, 9, 1), date(2026, 9, 30), scope="weekday"
    )

    assert db_session.query(Mass).filter(Mass.id == mass.id).one_or_none() is not None
    assert db_session.query(Scale).filter(Scale.id == scale.id).one_or_none() is not None
