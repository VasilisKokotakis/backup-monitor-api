from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class ClientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    contact_email: EmailStr


class ClientOut(BaseModel):
    id: int
    name: str
    contact_email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}
