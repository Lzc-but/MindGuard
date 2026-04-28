from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Conversation session id")
    question: str


class ChatResponse(BaseModel):
    answer: str
    references: list[str] = []


class ConversationCreateRequest(BaseModel):
    title: str | None = None


class ConversationRenameRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=50)


class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str


class ConversationMessage(BaseModel):
    role: str
    content: str
    created_at: str


class ConversationChatRequest(BaseModel):
    question: str
