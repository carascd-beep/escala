"""Router de API REST"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.database import get_db
from app.services import person_service, mass_service, scale_service
from app.schemas.person import PersonCreate, PersonUpdate, PersonResponse
from app.schemas.mass import MassScheduleCreate, MassScheduleUpdate, MassScheduleResponse, MassCreate, MassResponse
from app.schemas.scale import ScaleResponse, ScaleAssignmentCreate, ScaleAssignmentUpdate, ScaleAssignmentResponse
from app.schemas.swap import SwapRequestCreate, SwapRequestResponse
from app.schemas.schedule_parameters import ScheduleParametersCreate
from app.services.schedule_engine import ScheduleParameters
from app.services.scale_engine_adapter import generate_scales_for_period, clear_unpublished_scales
from app.models.person import ServerType
from app.models.scale import AssignmentStatus

router = APIRouter(prefix="/api", tags=["API"])


# ===== PESSOAS =====

@router.get("/pessoas", response_model=List[PersonResponse])
def list_pessoas(
    server_type: ServerType = None,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """Lista pessoas"""
    return person_service.get_persons(db, server_type=server_type, is_active=is_active)


@router.post("/pessoas", response_model=PersonResponse, status_code=status.HTTP_201_CREATED)
def create_pessoa(person: PersonCreate, db: Session = Depends(get_db)):
    """Cria pessoa"""
    return person_service.create_person(
        db,
        full_name=person.full_name,
        display_name=person.display_name,
        server_type=person.server_type,
        phone=person.phone,
        birth_date=person.birth_date,
        availability=person.availability,
        experience=person.experience,
        fixed_schedule_ids=person.fixed_schedule_ids,
        fixed_weekdays=person.fixed_weekdays,
        email=person.email,
        observations=person.observations
    )


@router.get("/pessoas/{person_id}", response_model=PersonResponse)
def get_pessoa(person_id: int, db: Session = Depends(get_db)):
    """Busca pessoa"""
    person = person_service.get_person(db, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    return person


@router.put("/pessoas/{person_id}", response_model=PersonResponse)
def update_pessoa(person_id: int, person: PersonUpdate, db: Session = Depends(get_db)):
    """Atualiza pessoa"""
    updated = person_service.update_person(db, person_id, **person.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    return updated


@router.delete("/pessoas/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pessoa(person_id: int, db: Session = Depends(get_db)):
    """Desativa pessoa"""
    person = person_service.deactivate_person(db, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")


# ===== HORÁRIOS =====

@router.get("/horarios", response_model=List[MassScheduleResponse])
def list_horarios(is_active: bool = None, db: Session = Depends(get_db)):
    """Lista horários de missa"""
    return mass_service.get_mass_schedules(db, is_active=is_active)


@router.post("/horarios", response_model=MassScheduleResponse, status_code=status.HTTP_201_CREATED)
def create_horario(schedule: MassScheduleCreate, db: Session = Depends(get_db)):
    """Cria horário de missa"""
    return mass_service.create_mass_schedule(
        db,
        day_of_week=schedule.day_of_week,
        time=schedule.time,
        description=schedule.description
    )


@router.get("/horarios/{schedule_id}", response_model=MassScheduleResponse)
def get_horario(schedule_id: int, db: Session = Depends(get_db)):
    """Busca um horário para edição."""
    schedule = mass_service.get_mass_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Horário não encontrado")
    return schedule


@router.put("/horarios/{schedule_id}", response_model=MassScheduleResponse)
def update_horario(schedule_id: int, schedule: MassScheduleUpdate, db: Session = Depends(get_db)):
    """Atualiza horário"""
    updated = mass_service.update_mass_schedule(db, schedule_id, **schedule.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Horário não encontrado")
    return updated


@router.delete("/horarios/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_horario(schedule_id: int, db: Session = Depends(get_db)):
    try:
        if not mass_service.delete_mass_schedule(db, schedule_id):
            raise HTTPException(status_code=404, detail="Horário não encontrado")
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


# ===== MISSAS =====

@router.get("/missas", response_model=List[MassResponse])
def list_missas(start_date: date = None, end_date: date = None, db: Session = Depends(get_db)):
    """Lista missas"""
    if start_date and end_date:
        return mass_service.get_masses_by_date_range(db, start_date, end_date)
    return []


@router.post("/missas", response_model=MassResponse, status_code=status.HTTP_201_CREATED)
def create_missa(mass: MassCreate, db: Session = Depends(get_db)):
    """Cria missa"""
    return mass_service.create_mass(
        db,
        date_val=mass.date,
        time=mass.time,
        schedule_id=mass.schedule_id,
        celebration=mass.celebration,
        observations=mass.observations
    )


@router.post("/missas/gerar", status_code=status.HTTP_201_CREATED)
def generate_masses(start_date: date, end_date: date, scope: str = "all", db: Session = Depends(get_db)):
    """Gera missas para um período"""
    try:
        count = mass_service.generate_masses_for_period(db, start_date, end_date, scope)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return {"message": f"{count} missas geradas com sucesso"}


# ===== ESCALAS =====

@router.get("/escalas", response_model=List[ScaleResponse])
def list_escalas(start_date: date, end_date: date, db: Session = Depends(get_db)):
    """Lista escalas"""
    return scale_service.get_scales_by_date_range(db, start_date, end_date)


@router.post("/escalas/gerar", status_code=status.HTTP_201_CREATED)
def generate_scales(start_date: date, end_date: date, parameters: ScheduleParametersCreate | None = None, db: Session = Depends(get_db)):
    """Gera escalas automáticas para as missas do período."""
    try:
        params = ScheduleParameters(
            scope=parameters.scope,
            participants_per_scale=parameters.participants_per_scale,
            priority_experience=tuple(parameters.priority_experience),
            priority_server_types=tuple(parameters.priority_server_types),
            participants_by_server_type=parameters.participants_by_server_type,
        ) if parameters else None
        assignments = generate_scales_for_period(db, start_date, end_date, params)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return {"assignments": assignments}


@router.delete("/escalas/rascunhos", status_code=status.HTTP_200_OK)
def clear_draft_scales(start_date: date, end_date: date, scope: str = "all", db: Session = Depends(get_db)):
    try:
        return clear_unpublished_scales(db, start_date, end_date, scope)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/escalas/{mass_id}", response_model=ScaleResponse)
def create_or_get_scale(mass_id: int, db: Session = Depends(get_db)):
    """Cria ou obtém escala para uma missa"""
    return scale_service.get_or_create_scale(db, mass_id)


@router.post("/escalas/{scale_id}/atribuicoes", response_model=ScaleAssignmentResponse)
def add_assignment(scale_id: int, assignment: ScaleAssignmentCreate, db: Session = Depends(get_db)):
    """Adiciona pessoa à escala"""
    try:
        return scale_service.add_assignment(
            db,
            scale_id=scale_id,
            person_id=assignment.person_id,
            status=assignment.status,
            observations=assignment.observations
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/escalas/atribuicoes/{assignment_id}", response_model=ScaleAssignmentResponse)
def update_assignment(assignment_id: int, assignment: ScaleAssignmentUpdate, db: Session = Depends(get_db)):
    """Atualiza atribuição"""
    updated = scale_service.update_assignment(db, assignment_id, **assignment.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Atribuição não encontrada")
    return updated


@router.delete("/escalas/atribuicoes/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """Remove atribuição"""
    if not scale_service.remove_assignment(db, assignment_id):
        raise HTTPException(status_code=404, detail="Atribuição não encontrada")


@router.post("/escalas/{scale_id}/publicar", response_model=ScaleResponse)
def publish_scale(scale_id: int, db: Session = Depends(get_db)):
    """Publica escala"""
    scale = scale_service.publish_scale(db, scale_id)
    if not scale:
        raise HTTPException(status_code=404, detail="Escala não encontrada")
    return scale


@router.post("/trocas", response_model=SwapRequestResponse, status_code=status.HTTP_201_CREATED)
def create_swap(request_data: SwapRequestCreate, db: Session = Depends(get_db)):
    try:
        return scale_service.create_swap_request(db, **request_data.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/trocas/{request_id}/aprovar", response_model=SwapRequestResponse)
def approve_swap(request_id: int, db: Session = Depends(get_db)):
    request = scale_service.resolve_swap_request(db, request_id, approve=True)
    if not request:
        raise HTTPException(status_code=404, detail="Solicitação pendente não encontrada")
    return request


@router.post("/trocas/{request_id}/rejeitar", response_model=SwapRequestResponse)
def reject_swap(request_id: int, db: Session = Depends(get_db)):
    request = scale_service.resolve_swap_request(db, request_id, approve=False)
    if not request:
        raise HTTPException(status_code=404, detail="Solicitação pendente não encontrada")
    return request
