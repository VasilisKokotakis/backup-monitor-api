from datetime import datetime
from pydantic import BaseModel, EmailStr


class ClientCreate(BaseModel):
    name: str
    contact_email: EmailStr


class ClientOut(BaseModel):
    id: int
    name: str
    contact_email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}
