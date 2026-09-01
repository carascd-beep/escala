"""Serviço de Missas"""
from sqlalchemy.orm import Session
from app.models.mass import MassSchedule, Mass, DayOfWeek
from datetime import date, timedelta
from typing import List, Optional


def get_mass_schedules(db: Session, is_active: Optional[bool] = None) -> List[MassSchedule]:
    """Lista horários de missa"""
    query = db.query(MassSchedule)
    if is_active is not None:
        query = query.filter(MassSchedule.is_active == is_active)
    return query.all()


def get_mass_schedule(db: Session, schedule_id: int) -> Optional[MassSchedule]:
    """Busca horário por ID"""
    return db.query(MassSchedule).filter(MassSchedule.id == schedule_id).first()


def create_mass_schedule(db: Session, day_of_week: DayOfWeek, time: str, description: str = None) -> MassSchedule:
    """Cria horário de missa"""
    schedule = MassSchedule(
        day_of_week=day_of_week,
        time=time,
        description=description
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


def update_mass_schedule(db: Session, schedule_id: int, **kwargs) -> Optional[MassSchedule]:
    """Atualiza horário de missa"""
    schedule = get_mass_schedule(db, schedule_id)
    if not schedule:
        return None
    
    for key, value in kwargs.items():
        if value is not None:
            setattr(schedule, key, value)
    
    db.commit()
    db.refresh(schedule)
    return schedule


def delete_mass_schedule(db: Session, schedule_id: int) -> bool:
    """Exclui horário sem missas já geradas."""
    schedule = get_mass_schedule(db, schedule_id)
    if not schedule:
        return False
    if schedule.masses:
        raise ValueError("Não é possível excluir horário com missas vinculadas")
    db.delete(schedule)
    db.commit()
    return True


def get_masses_by_date_range(db: Session, start_date: date, end_date: date) -> List[Mass]:
    """Lista missas em um período"""
    return db.query(Mass).filter(
        Mass.date >= start_date,
        Mass.date <= end_date
    ).order_by(Mass.date, Mass.time).all()


def get_mass(db: Session, mass_id: int) -> Optional[Mass]:
    """Busca missa por ID"""
    return db.query(Mass).filter(Mass.id == mass_id).first()


def create_mass(db: Session, date_val: date, time: str, schedule_id: int = None, 
                celebration: str = None, observations: str = None) -> Mass:
    """Cria missa específica"""
    mass = Mass(
        date=date_val,
        time=time,
        schedule_id=schedule_id,
        celebration=celebration,
        observations=observations
    )
    db.add(mass)
    db.commit()
    db.refresh(mass)
    return mass


def generate_masses_for_period(db: Session, start_date: date, end_date: date, scope: str = "all") -> int:
    """Gera missas para um período usando apenas horários ativos e escopo."""
    if scope not in {"all", "weekday", "weekend"}:
        raise ValueError("Escopo deve ser all, weekday ou weekend")
    schedules = get_mass_schedules(db, is_active=True)
    
    # Mapeamento dia da semana -> número Python (0=segunda, 6=domingo)
    day_map = {
        DayOfWeek.MONDAY: 0,
        DayOfWeek.TUESDAY: 1,
        DayOfWeek.WEDNESDAY: 2,
        DayOfWeek.THURSDAY: 3,
        DayOfWeek.FRIDAY: 4,
        DayOfWeek.SATURDAY: 5,
        DayOfWeek.SUNDAY: 6,
    }
    
    created_count = 0
    current_date = start_date
    
    while current_date <= end_date:
        weekday = current_date.weekday()
        if scope == "weekday" and weekday >= 5:
            current_date += timedelta(days=1)
            continue
        if scope == "weekend" and weekday < 5:
            current_date += timedelta(days=1)
            continue
        
        for schedule in schedules:
            if day_map[schedule.day_of_week] == weekday:
                # Verificar se já existe missa nesta data/horário
                existing = db.query(Mass).filter(
                    Mass.date == current_date,
                    Mass.time == schedule.time
                ).first()
                
                if not existing:
                    mass = Mass(
                        date=current_date,
                        time=schedule.time,
                        schedule_id=schedule.id
                    )
                    db.add(mass)
                    created_count += 1
        
        current_date += timedelta(days=1)
    
    db.commit()
    return created_count
