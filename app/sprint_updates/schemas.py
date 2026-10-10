from pydantic import BaseModel, Field
from datetime import datetime


class SprintUpdateCreate(BaseModel):
    task_id: int
    update_text: str = Field(min_length=3, max_length=2000)


class SprintUpdateResponse(BaseModel):
    id: int
    employee_id: int
    task_id: int
    update_text: str
    created_at: datetime

    class Config:
        from_attributes = True