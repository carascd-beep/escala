"""Modelo de Pessoa (Coroinhas, Acólitos, Cerimoniários)"""
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Enum, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


person_fixed_schedules = Table(
    "person_fixed_schedules",
    Base.metadata,
    Column("person_id", ForeignKey("persons.id"), primary_key=True),
    Column("schedule_id", ForeignKey("mass_schedules.id"), primary_key=True),
)


class ServerType(str, enum.Enum):
    """Tipos de servidores"""
    COROINHA = "coroinha"
    ACOLITO = "acolito"
    CERIMONIARIO = "cerimoniario"


class Person(Base):
    """Pessoa que participa das escalas"""
    __tablename__ = "persons"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False)
    display_name = Column(String(100), nullable=False)
    server_type = Column(Enum(ServerType), nullable=False)
    phone = Column(String(20), nullable=True)
    birth_date = Column(Date, nullable=True)
    availability = Column(String(20), nullable=True)
    experience = Column(Integer, nullable=True)
    fixed_weekdays = Column(String(30), nullable=True)
    email = Column(String(100), nullable=True)
    observations = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    assignments = relationship("ScaleAssignment", back_populates="person")
    fixed_schedules = relationship("MassSchedule", secondary=person_fixed_schedules, back_populates="preferred_people")

    def __init__(self, **kwargs):
        fixed_schedule_ids = kwargs.pop("fixed_schedule_ids", None)
        fixed_weekdays = kwargs.pop("fixed_weekdays", None)
        super().__init__(**kwargs)
        self.fixed_schedule_ids = fixed_schedule_ids or []
        if fixed_weekdays is not None:
            self.fixed_weekdays = ",".join(str(day) for day in fixed_weekdays)
