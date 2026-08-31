"""Schemas de Pessoa"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.person import ServerType


class PersonBase(BaseModel):
    full_name: str
    display_name: str
    server_type: ServerType
    phone: Optional[str] = None
    email: Optional[str] = None
    observations: Optional[str] = None


class PersonCreate(PersonBase):
    pass


class PersonUpdate(BaseModel):
    full_name: Optional[str] = None
    display_name: Optional[str] = None
    server_type: Optional[ServerType] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    observations: Optional[str] = None
    is_active: Optional[bool] = None


class PersonResponse(PersonBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
