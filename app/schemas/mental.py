from pydantic import BaseModel


class MentalRequest(BaseModel):
    user_id: str
    text: str


class MentalResponse(BaseModel):
    status: str
    score: float
    suggestion: str
