"""Integração do motor automático com a persistência."""
from datetime import date
from sqlalchemy.orm import Session
from app.models.mass import Mass, MassSchedule
from app.models.person import Person
from app.models.scale import Scale, ScaleAssignment
from app.services.scale_service import get_or_create_scale
from app.services.schedule_engine import ScheduleParameters, generate_assignments


def generate_scales_for_period(db: Session, start_date: date, end_date: date,
                               parameters: ScheduleParameters | None = None) -> int:
    parameters = parameters or ScheduleParameters()
    from app.services.mass_service import generate_masses_for_period
    generate_masses_for_period(db, start_date, end_date, parameters.scope)
    masses = db.query(Mass).outerjoin(MassSchedule).filter(
        Mass.date >= start_date, Mass.date <= end_date,
        Mass.is_cancelled.is_(False),
        (Mass.schedule_id.is_(None) | MassSchedule.is_active.is_(True)),
    ).order_by(Mass.date, Mass.time).all()
    generated = generate_assignments(
        db.query(Person).filter(Person.is_active.is_(True)).all(),
        ({"id": m.id, "date": m.date, "schedule_id": m.schedule_id} for m in masses),
        parameters,
    )
    total = 0
    for mass in masses:
        # O motor pode excluir missas fora do escopo (por exemplo, fins de
        # semana quando a geração foi configurada para dias úteis). Essas
        # missas não devem ser limpas nem alteradas.
        if mass.id not in generated:
            continue
        scale = get_or_create_scale(db, mass.id)
        for assignment in list(scale.assignments):
            db.delete(assignment)
        db.flush()
        for person in generated[mass.id]:
            db.add(ScaleAssignment(scale_id=scale.id, person_id=person.id))
            total += 1
    db.commit()
    return total


def clear_unpublished_scales(db: Session, start_date: date, end_date: date,
                             scope: str = "all") -> dict[str, int]:
    """Remove rascunhos e as missas da agenda dentro do escopo informado."""
    if scope not in {"all", "weekday", "weekend"}:
        raise ValueError("Escopo deve ser all, weekday ou weekend")
    scales = db.query(Scale).join(Mass).filter(
        Mass.date >= start_date, Mass.date <= end_date, Scale.published.is_(False)
    ).all()
    removed_assignments = 0
    removed_masses = 0
    for scale in scales:
        if scope == "weekday" and scale.mass.date.weekday() >= 5:
            continue
        if scope == "weekend" and scale.mass.date.weekday() < 5:
            continue
        removed_assignments += len(scale.assignments)
        for assignment in list(scale.assignments):
            db.delete(assignment)
        mass = scale.mass
        db.delete(scale)
        db.delete(mass)
        removed_masses += 1
    # Remove missas de agenda sem escala, ou com escala de rascunho. A
    # consulta é restrita ao escopo e nunca toca em missas publicadas.
    draft_mass_ids = {scale.mass_id for scale in scales}
    agenda_query = db.query(Mass).filter(
        Mass.date >= start_date,
        Mass.date <= end_date,
        Mass.is_cancelled.is_(False),
    )
    for mass in agenda_query.all():
        if scope == "weekday" and mass.date.weekday() >= 5:
            continue
        if scope == "weekend" and mass.date.weekday() < 5:
            continue
        if mass.id in draft_mass_ids:
            continue
        if mass.scale is None:
            db.delete(mass)
            removed_masses += 1
    db.commit()
    return {"assignments": removed_assignments, "masses": removed_masses}
