"""Schemas de Missas"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from app.models.mass import DayOfWeek


class MassScheduleBase(BaseModel):
    day_of_week: DayOfWeek
    time: str
    description: Optional[str] = None
    is_active: bool = True
    participants_count: int = Field(default=2, ge=1, le=10)


class MassScheduleCreate(MassScheduleBase):
    pass


class MassScheduleUpdate(BaseModel):
    day_of_week: Optional[DayOfWeek] = None
    time: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    participants_count: Optional[int] = Field(default=None, ge=1, le=10)


class MassScheduleResponse(MassScheduleBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class MassBase(BaseModel):
    date: date
    time: str
    celebration: Optional[str] = None
    observations: Optional[str] = None


class MassCreate(MassBase):
    schedule_id: Optional[int] = None


class MassUpdate(BaseModel):
    date: Optional[date] = None
    time: Optional[str] = None
    celebration: Optional[str] = None
    observations: Optional[str] = None
    is_cancelled: Optional[bool] = None


class MassResponse(MassBase):
    id: int
    schedule_id: Optional[int]
    is_cancelled: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
