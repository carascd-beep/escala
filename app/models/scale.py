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
