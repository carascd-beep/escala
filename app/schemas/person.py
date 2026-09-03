"""Schemas de Pessoa e visualização segura do perfil."""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.person import ServerType


class PersonBase(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    display_name: str = Field(min_length=1, max_length=100)
    server_type: ServerType
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    availability: Optional[str] = None
    experience: Optional[int] = Field(default=None, ge=0, le=3)
    email: Optional[str] = None
    observations: Optional[str] = None
    fixed_schedule_ids: list[int] = Field(default_factory=list)
    fixed_weekdays: list[int] = Field(default_factory=list)

    @field_validator("fixed_weekdays", mode="before")
    @classmethod
    def normalize_fixed_weekdays(cls, value):
        if value in (None, ""):
            return []
        if isinstance(value, str):
            return [int(item) for item in value.split(",") if item.strip().isdigit()]
        return value

    @field_validator("availability")
    @classmethod
    def validate_availability(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            return ""
        normalized = " ".join(cleaned.lower().replace("-", " ").split())
        canonical = {
            "semana": "semana",
            "dia de semana": "semana",
            "fim de semana": "fim de semana",
            "ambos": "ambos",
            "todo dia": "ambos",
            "todo dias": "ambos",
        }
        if normalized not in canonical:
            raise ValueError("Disponibilidade deve ser Semana, Fim de Semana ou Ambos")
        return canonical[normalized]


class PersonCreate(PersonBase):
    pass


class PersonUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    display_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    server_type: Optional[ServerType] = None
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    availability: Optional[str] = None
    experience: Optional[int] = Field(default=None, ge=0, le=3)
    email: Optional[str] = None
    observations: Optional[str] = None
    is_active: Optional[bool] = None
    fixed_schedule_ids: Optional[list[int]] = None
    fixed_weekdays: list[int] = Field(default_factory=list)

    @field_validator("fixed_weekdays", mode="before")
    @classmethod
    def normalize_fixed_weekdays(cls, value):
        if value in (None, ""):
            return []
        if isinstance(value, str):
            return [int(item) for item in value.split(",") if item.strip().isdigit()]
        return value


class PersonResponse(PersonBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PersonSelfResponse(BaseModel):
    """Perfil do coroinha: experiência é deliberadamente omitida."""
    id: int
    full_name: str
    display_name: str
    server_type: ServerType
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    availability: Optional[str] = None
    email: Optional[str] = None
    observations: Optional[str] = None
    fixed_schedule_ids: list[int] = Field(default_factory=list)
    fixed_weekdays: list[int] = Field(default_factory=list)
    is_active: bool

    @field_validator("fixed_weekdays", mode="before")
    @classmethod
    def normalize_fixed_weekdays(cls, value):
        if value in (None, ""):
            return []
        if isinstance(value, str):
            return [int(item) for item in value.split(",") if item.strip().isdigit()]
        return value

    class Config:
        from_attributes = True


EXPERIENCE_LABELS = {0: "Muito Baixa", 1: "Baixa", 2: "Média", 3: "Alta"}
