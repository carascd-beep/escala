"""Modelos de Escalas"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class AssignmentStatus(str, enum.Enum):
    """Status da atribuição na escala"""
    SCHEDULED = "scheduled"  # Escalado
    CONFIRMED = "confirmed"  # Confirmado
    UNAVAILABLE = "unavailable"  # Não pode comparecer
    SUBSTITUTED = "substituted"  # Substituído
    CANCELLED = "cancelled"  # Cancelado


class Scale(Base):
    """Escala de uma Missa específica"""
    __tablename__ = "scales"
    
    id = Column(Integer, primary_key=True, index=True)
    mass_id = Column(Integer, ForeignKey("masses.id"), unique=True, nullable=False)
    published = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    mass = relationship("Mass", back_populates="scale")
    assignments = relationship("ScaleAssignment", back_populates="scale", cascade="all, delete-orphan")


class ScaleAssignment(Base):
    """Atribuição de pessoa à escala"""
    __tablename__ = "scale_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    scale_id = Column(Integer, ForeignKey("scales.id"), nullable=False)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False)
    status = Column(Enum(AssignmentStatus), default=AssignmentStatus.SCHEDULED)
    observations = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    scale = relationship("Scale", back_populates="assignments")
    person = relationship("Person", back_populates="assignments")


class SwapRequestStatus(str, enum.Enum):
    """Estados do fluxo de solicitação de troca."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class SwapRequest(Base):
    """Troca aguardando aprovação do coordenador."""
    __tablename__ = "swap_requests"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("scale_assignments.id"), nullable=False)
    requester_id = Column(Integer, ForeignKey("persons.id"), nullable=False)
    substitute_id = Column(Integer, ForeignKey("persons.id"), nullable=False)
    status = Column(Enum(SwapRequestStatus), default=SwapRequestStatus.PENDING, nullable=False)
    reason = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    assignment = relationship("ScaleAssignment")
    requester = relationship("Person", foreign_keys=[requester_id])
    substitute = relationship("Person", foreign_keys=[substitute_id])


class ScheduleParameter(Base):
    """Configuração persistida da última geração de escala."""
    __tablename__ = "schedule_parameters"

    id = Column(Integer, primary_key=True, index=True)
    scope = Column(String(20), nullable=False, default="all")
    participants_per_scale = Column(Integer, nullable=False, default=2)
    priority_experience = Column(String(30), nullable=False, default="3,2,1")
    priority_server_types = Column(String(100), nullable=False, default="")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
