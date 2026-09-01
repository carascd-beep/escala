"""Schemas do fluxo de troca de escala."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from app.models.scale import SwapRequestStatus


class SwapRequestCreate(BaseModel):
    assignment_id: int
    requester_id: int
    substitute_id: int
    reason: Optional[str] = Field(default=None, max_length=500)


class SwapRequestResponse(SwapRequestCreate):
    id: int
    status: SwapRequestStatus
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True
