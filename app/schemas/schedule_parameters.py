"""Schema de parâmetros da geração automática."""
from datetime import date
from pydantic import BaseModel, Field, field_validator


class ScheduleParametersCreate(BaseModel):
    start_date: date
    end_date: date
    scope: str = "all"
    participants_per_scale: int = Field(default=2, ge=1, le=10)
    priority_experience: list[int] = Field(default_factory=lambda: [3, 2, 1, 0])
    priority_server_types: list[str] = Field(default_factory=list)
    participants_by_server_type: dict[str, int] = Field(default_factory=dict)

    @field_validator("priority_experience")
    @classmethod
    def validate_priority_experience(cls, value: list[int]) -> list[int]:
        if any(level not in {0, 1, 2, 3} for level in value):
            raise ValueError("Experiência deve usar níveis de 0 a 3")
        return value

    @field_validator("scope")
    @classmethod
    def validate_scope(cls, value: str) -> str:
        if value not in {"all", "weekday", "weekend"}:
            raise ValueError("Escopo deve ser all, weekday ou weekend")
        return value


class ScheduleParametersResponse(ScheduleParametersCreate):
    id: int

    class Config:
        from_attributes = True
