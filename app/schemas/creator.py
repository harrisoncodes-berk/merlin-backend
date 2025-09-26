from pydantic import BaseModel

class Race(BaseModel):
    id: str
    name: str
    description: str
    