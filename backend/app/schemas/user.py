from datetime import datetime

from pydantic import BaseModel, EmailStr
from pydantic.config import ConfigDict


class User(BaseModel):
    id: str
    email: EmailStr
    store_quota: int = 3
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
