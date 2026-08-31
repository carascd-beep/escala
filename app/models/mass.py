"""Modelos de Missas e Horários"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class DayOfWeek(str, enum.Enum):
    """Dias da semana"""
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class MassSchedule(Base):
    """Horário recorrente de Missa"""
    __tablename__ = "mass_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(Enum(DayOfWeek), nullable=False)
    time = Column(String(5), nullable=False)  # Formato HH:MM
    is_active = Column(Boolean, default=True)
    description = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    masses = relationship("Mass", back_populates="schedule")


class Mass(Base):
    """Missa específica em uma data"""
    __tablename__ = "masses"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    time = Column(String(5), nullable=False)  # Formato HH:MM
    schedule_id = Column(Integer, ForeignKey("mass_schedules.id"), nullable=True)
    celebration = Column(String(200), nullable=True)  # Ex: "Missa do Natal"
    observations = Column(String(500), nullable=True)
    is_cancelled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    schedule = relationship("MassSchedule", back_populates="masses")
    scale = relationship("Scale", back_populates="mass", uselist=False)
