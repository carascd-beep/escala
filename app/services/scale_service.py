"""Serviço de Escalas"""
from sqlalchemy.orm import Session, joinedload
from app.models.scale import Scale, ScaleAssignment, AssignmentStatus
from app.models.mass import Mass
from app.models.person import Person
from typing import List, Optional
from datetime import date


def get_scale_by_mass(db: Session, mass_id: int) -> Optional[Scale]:
    """Busca escala de uma missa"""
    return db.query(Scale).filter(Scale.mass_id == mass_id).first()


def get_or_create_scale(db: Session, mass_id: int) -> Scale:
    """Obtém ou cria escala para uma missa"""
    scale = get_scale_by_mass(db, mass_id)
    if not scale:
        scale = Scale(mass_id=mass_id)
        db.add(scale)
        db.commit()
        db.refresh(scale)
    return scale


def add_assignment(db: Session, scale_id: int, person_id: int, 
                   status: AssignmentStatus = AssignmentStatus.SCHEDULED,
                   observations: str = None) -> ScaleAssignment:
    """Adiciona pessoa à escala"""
    # Verificar se já existe
    existing = db.query(ScaleAssignment).filter(
        ScaleAssignment.scale_id == scale_id,
        ScaleAssignment.person_id == person_id
    ).first()
    
    if existing:
        raise ValueError("Pessoa já está escalada para esta missa")
    
    # Verificar conflito de horário
    scale = db.query(Scale).options(joinedload(Scale.mass)).filter(Scale.id == scale_id).first()
    if scale:
        conflict = db.query(ScaleAssignment).join(Scale).join(Mass).filter(
            ScaleAssignment.person_id == person_id,
            Mass.date == scale.mass.date,
            Mass.time == scale.mass.time,
            Scale.id != scale_id,
            ScaleAssignment.status.in_([AssignmentStatus.SCHEDULED, AssignmentStatus.CONFIRMED])
        ).first()
        
        if conflict:
            raise ValueError("Pessoa já está escalada para outra missa no mesmo horário")
    
    assignment = ScaleAssignment(
        scale_id=scale_id,
        person_id=person_id,
        status=status,
        observations=observations
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


def remove_assignment(db: Session, assignment_id: int) -> bool:
    """Remove pessoa da escala"""
    assignment = db.query(ScaleAssignment).filter(ScaleAssignment.id == assignment_id).first()
    if not assignment:
        return False
    
    db.delete(assignment)
    db.commit()
    return True


def update_assignment(db: Session, assignment_id: int, **kwargs) -> Optional[ScaleAssignment]:
    """Atualiza atribuição"""
    assignment = db.query(ScaleAssignment).filter(ScaleAssignment.id == assignment_id).first()
    if not assignment:
        return None
    
    for key, value in kwargs.items():
        if value is not None:
            setattr(assignment, key, value)
    
    db.commit()
    db.refresh(assignment)
    return assignment


def substitute_person(db: Session, assignment_id: int, new_person_id: int, 
                      observations: str = None) -> Optional[ScaleAssignment]:
    """Substitui pessoa na escala"""
    assignment = db.query(ScaleAssignment).filter(ScaleAssignment.id == assignment_id).first()
    if not assignment:
        return None
    
    # Marcar original como substituído
    assignment.status = AssignmentStatus.SUBSTITUTED
    assignment.observations = f"Substituído. {observations or ''}"
    
    # Criar nova atribuição
    new_assignment = ScaleAssignment(
        scale_id=assignment.scale_id,
        person_id=new_person_id,
        status=AssignmentStatus.SCHEDULED,
        observations=f"Substituição. {observations or ''}"
    )
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    return new_assignment


def get_scales_by_date_range(db: Session, start_date: date, end_date: date) -> List[Scale]:
    """Lista escalas em um período"""
    return db.query(Scale).join(Mass).filter(
        Mass.date >= start_date,
        Mass.date <= end_date
    ).options(joinedload(Scale.mass), joinedload(Scale.assignments).joinedload(ScaleAssignment.person)).all()


def publish_scale(db: Session, scale_id: int) -> Optional[Scale]:
    """Publica escala"""
    scale = db.query(Scale).filter(Scale.id == scale_id).first()
    if not scale:
        return None
    
    scale.published = True
    db.commit()
    db.refresh(scale)
    return scale


def unpublish_scale(db: Session, scale_id: int) -> Optional[Scale]:
    """Despublica escala"""
    scale = db.query(Scale).filter(Scale.id == scale_id).first()
    if not scale:
        return None
    
    scale.published = False
    db.commit()
    db.refresh(scale)
    return scale
