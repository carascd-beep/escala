"""Serviço de Escalas"""
from sqlalchemy.orm import Session, joinedload
from app.models.scale import Scale, ScaleAssignment, AssignmentStatus, SwapRequest, SwapRequestStatus
from app.models.mass import Mass
from app.models.person import Person
from typing import List, Optional
from datetime import date, datetime
from app.services.schedule_engine import generate_assignments


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


def create_swap_request(db: Session, assignment_id: int, requester_id: int,
                        substitute_id: int, reason: str = None) -> SwapRequest:
    """Cria solicitação somente para substituto compatível."""
    assignment = db.query(ScaleAssignment).options(
        joinedload(ScaleAssignment.scale).joinedload(Scale.mass)
    ).filter(ScaleAssignment.id == assignment_id).first()
    requester = db.query(Person).filter(Person.id == requester_id, Person.is_active.is_(True)).first()
    substitute = db.query(Person).filter(Person.id == substitute_id, Person.is_active.is_(True)).first()
    if not assignment or not requester or not substitute or requester_id == substitute_id:
        raise ValueError("Solicitação de troca inválida")
    if assignment.person_id != requester_id or substitute.experience not in (1, 2):
        raise ValueError("Substituto não respeita a composição de experiência")
    value = (substitute.availability or "").lower()
    weekend = assignment.scale.mass.date.weekday() in {5, 6}
    if ("fim" in value) != weekend and "ambos" not in value and "todo" not in value:
        raise ValueError("Substituto não está disponível para esta data")
    request = SwapRequest(assignment_id=assignment_id, requester_id=requester_id,
                          substitute_id=substitute_id, reason=reason)
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def resolve_swap_request(db: Session, request_id: int, approve: bool) -> Optional[SwapRequest]:
    """Aprova/rejeita e consolida uma troca aprovada."""
    request = db.query(SwapRequest).filter(SwapRequest.id == request_id).first()
    if not request or request.status != SwapRequestStatus.PENDING:
        return None
    request.status = SwapRequestStatus.APPROVED if approve else SwapRequestStatus.REJECTED
    request.resolved_at = datetime.utcnow()
    if approve:
        assignment = db.query(ScaleAssignment).filter(ScaleAssignment.id == request.assignment_id).first()
        if assignment:
            assignment.status = AssignmentStatus.SUBSTITUTED
            db.add(ScaleAssignment(scale_id=assignment.scale_id, person_id=request.substitute_id))
    db.commit()
    db.refresh(request)
    return request
