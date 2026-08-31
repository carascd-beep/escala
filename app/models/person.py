"""Modelo de Pessoa (Coroinhas, Acólitos, Cerimoniários)"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


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
    email = Column(String(100), nullable=True)
    observations = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    assignments = relationship("ScaleAssignment", back_populates="person")
