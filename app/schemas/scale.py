"""Schemas de Escalas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.scale import AssignmentStatus


class ScaleAssignmentBase(BaseModel):
    person_id: int
    status: AssignmentStatus = AssignmentStatus.SCHEDULED
    observations: Optional[str] = None


class ScaleAssignmentCreate(ScaleAssignmentBase):
    pass


class ScaleAssignmentUpdate(BaseModel):
    person_id: Optional[int] = None
    status: Optional[AssignmentStatus] = None
    observations: Optional[str] = None


class ScaleAssignmentResponse(ScaleAssignmentBase):
    id: int
    scale_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ScaleBase(BaseModel):
    mass_id: int
    notes: Optional[str] = None


class ScaleCreate(ScaleBase):
    pass


class ScaleUpdate(BaseModel):
    notes: Optional[str] = None
    published: Optional[bool] = None


class ScaleResponse(ScaleBase):
    id: int
    published: bool
    created_at: datetime
    assignments: List[ScaleAssignmentResponse] = []
    
    class Config:
        from_attributes = True
