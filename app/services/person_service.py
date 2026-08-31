"""Serviço de Pessoas"""
from sqlalchemy.orm import Session
from app.models.person import Person, ServerType
from typing import List, Optional


def get_persons(db: Session, skip: int = 0, limit: int = 100, server_type: Optional[ServerType] = None, is_active: Optional[bool] = None) -> List[Person]:
    """Lista pessoas com filtros"""
    query = db.query(Person)
    
    if server_type:
        query = query.filter(Person.server_type == server_type)
    if is_active is not None:
        query = query.filter(Person.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()


def get_person(db: Session, person_id: int) -> Optional[Person]:
    """Busca pessoa por ID"""
    return db.query(Person).filter(Person.id == person_id).first()


def create_person(db: Session, full_name: str, display_name: str, server_type: ServerType, 
                  phone: str = None, email: str = None, observations: str = None) -> Person:
    """Cria nova pessoa"""
    person = Person(
        full_name=full_name,
        display_name=display_name,
        server_type=server_type,
        phone=phone,
        email=email,
        observations=observations
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


def update_person(db: Session, person_id: int, **kwargs) -> Optional[Person]:
    """Atualiza pessoa"""
    person = get_person(db, person_id)
    if not person:
        return None
    
    for key, value in kwargs.items():
        if value is not None:
            setattr(person, key, value)
    
    db.commit()
    db.refresh(person)
    return person


def deactivate_person(db: Session, person_id: int) -> Optional[Person]:
    """Desativa pessoa"""
    return update_person(db, person_id, is_active=False)


def activate_person(db: Session, person_id: int) -> Optional[Person]:
    """Ativa pessoa"""
    return update_person(db, person_id, is_active=True)
