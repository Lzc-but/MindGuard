from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Conversation session id")
    question: str


class ChatResponse(BaseModel):
    answer: str
    references: list[str] = []
