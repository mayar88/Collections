# app/models/user_model.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional

class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: EmailStr
    level: str
    password: str

    @validator("password", pre=True)
    def truncate_password(cls, v):
        if isinstance(v, str):
            # Enforce 72-byte limit early
            return v.encode("utf-8")[:72].decode("utf-8", "ignore")
        return v