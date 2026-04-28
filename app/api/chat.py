from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationChatRequest,
    ConversationCreateRequest,
    ConversationMessage,
    ConversationRenameRequest,
    ConversationResponse,
)
from app.services.conversation import (
    chat_in_conversation,
    create_conversation,
    delete_conversation,
    get_conversation_messages,
    get_or_create_conversation,
    list_conversations,
    rename_conversation,
)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ChatResponse:
    # 兼容旧接口：session_id 作为 conversation_id 使用
    get_or_create_conversation(current_user["username"], payload.session_id)
    answer, refs = chat_in_conversation(current_user["username"], payload.session_id, payload.question)
    return ChatResponse(answer=answer, references=refs)


@router.post("/conversations", response_model=ConversationResponse)
async def create_chat_conversation(
    payload: ConversationCreateRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ConversationResponse:
    convo = create_conversation(current_user["username"], payload.title)
    return ConversationResponse(**convo)


@router.get("/conversations", response_model=list[ConversationResponse])
async def get_chat_conversations(
    current_user: Annotated[dict, Depends(get_current_user)],
) -> list[ConversationResponse]:
    rows = list_conversations(current_user["username"])
    return [ConversationResponse(**row) for row in rows]


@router.delete("/conversations/{conversation_id}")
async def remove_chat_conversation(
    conversation_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    delete_conversation(current_user["username"], conversation_id)
    return {"message": "deleted"}


@router.patch("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_chat_conversation(
    conversation_id: str,
    payload: ConversationRenameRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ConversationResponse:
    row = rename_conversation(current_user["username"], conversation_id, payload.title)
    return ConversationResponse(**row)


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[ConversationMessage],
)
async def get_chat_messages(
    conversation_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
) -> list[ConversationMessage]:
    rows = get_conversation_messages(current_user["username"], conversation_id)
    return [ConversationMessage(**row) for row in rows]


@router.post("/conversations/{conversation_id}/messages", response_model=ChatResponse)
async def send_chat_message(
    conversation_id: str,
    payload: ConversationChatRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ChatResponse:
    answer, refs = chat_in_conversation(current_user["username"], conversation_id, payload.question)
    return ChatResponse(answer=answer, references=refs)
