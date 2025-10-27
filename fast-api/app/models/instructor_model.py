from pydantic import BaseModel
from typing import Optional

class Instructor(BaseModel):
    id: int
    name: str
    role: Optional[str] = None
    model_version: Optional[str] = None
    expertise: str