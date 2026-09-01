"""Serviço de Pessoas"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.person import Person, ServerType


def get_persons(db: Session, skip: int = 0, limit: int = 100,
                server_type: Optional[ServerType] = None,
                is_active: Optional[bool] = None) -> List[Person]:
    """Lista pessoas com filtros."""
    query = db.query(Person)
    if server_type:
        query = query.filter(Person.server_type == server_type)
    if is_active is not None:
        query = query.filter(Person.is_active == is_active)
    return query.offset(skip).limit(limit).all()


def get_person(db: Session, person_id: int) -> Optional[Person]:
    """Busca pessoa por ID."""
    return db.query(Person).filter(Person.id == person_id).first()


def create_person(db: Session, full_name: str, display_name: str,
                  server_type: ServerType, phone: str = None,
                  email: str = None, observations: str = None,
                  birth_date=None, availability: str = None,
                  experience: int = None, fixed_schedule_ids=None,
                  fixed_weekdays=None) -> Person:
    """Cria nova pessoa."""
    person = Person(
        full_name=full_name,
        display_name=display_name,
        server_type=server_type,
        phone=phone,
        birth_date=birth_date,
        availability=availability,
        experience=experience,
        email=email,
        observations=observations,
        fixed_weekdays=fixed_weekdays,
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    if fixed_schedule_ids is not None:
        from app.models.mass import MassSchedule
        person.fixed_schedules = db.query(MassSchedule).filter(
            MassSchedule.id.in_(fixed_schedule_ids)
        ).all()
        db.commit()
        db.refresh(person)
    return person


def update_person(db: Session, person_id: int, **kwargs) -> Optional[Person]:
    """Atualiza pessoa."""
    person = get_person(db, person_id)
    if not person:
        return None

    fixed_schedule_ids = kwargs.pop("fixed_schedule_ids", None)
    fixed_weekdays = kwargs.pop("fixed_weekdays", None)
    for key, value in kwargs.items():
        if value is not None:
            setattr(person, key, value)
    if fixed_schedule_ids is not None:
        from app.models.mass import MassSchedule
        person.fixed_schedules = db.query(MassSchedule).filter(
            MassSchedule.id.in_(fixed_schedule_ids)
        ).all()
    if fixed_weekdays is not None:
        person.fixed_weekdays = ",".join(str(day) for day in fixed_weekdays)

    db.commit()
    db.refresh(person)
    return person


def deactivate_person(db: Session, person_id: int) -> Optional[Person]:
    """Desativa pessoa."""
    return update_person(db, person_id, is_active=False)


def activate_person(db: Session, person_id: int) -> Optional[Person]:
    """Ativa pessoa."""
    return update_person(db, person_id, is_active=True)
