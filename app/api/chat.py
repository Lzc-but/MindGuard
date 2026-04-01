from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import chat_with_context

router = APIRouter(prefix="/api/chat", tags=["chat"])

# AI 聊天接口（POST 请求）
# 必须登录才能访问
# 返回格式固定为 ChatResponse
@router.post("", response_model=ChatResponse)
async def chat(
    # 前端传过来的请求数据：session_id(会话ID) + question(问题)
    payload: ChatRequest,

    # 登录校验：必须传 Token 才能调用这个接口
    # _ 代表“我需要校验登录，但我不用这个用户数据”
    _: Annotated[dict, Depends(get_current_user)],
) -> ChatResponse:
    
    # 调用核心聊天服务
    # 传入：会话ID + 用户问题
    # 返回：AI 答案 + 引用的知识库片段
    answer, refs = chat_with_context(payload.session_id, payload.question)
    
    # 把答案和引用返回给前端
    return ChatResponse(answer=answer, references=refs)
