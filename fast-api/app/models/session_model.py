from pydantic import BaseModel

class Session(BaseModel):
    id: int
    topic: str
    date: str
    instructor_id: int
    user_id: int
