from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SprintStatus(str, Enum):
    PLANNED = "Planned"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    CLOSED = "Closed"


class SprintCreate(BaseModel):
    project_id: UUID
    name: str = Field(..., min_length=1, max_length=150)
    goal: str = Field(..., min_length=1, max_length=2000)
    start_date: date
    end_date: date

    @field_validator("name", "goal")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value cannot be empty")
        return value

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("End date must be greater than or equal to start date")
        return self


class SprintUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=150)
    goal: str | None = Field(None, min_length=1, max_length=2000)
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("End date must be greater than or equal to start date")
        return self


class SprintResponse(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    goal: str
    start_date: date
    end_date: date
    status: SprintStatus
    created_by: UUID | None = None
    updated_by: UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
