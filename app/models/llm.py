from langchain_core.language_models.chat_models import BaseChatModel
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_community.chat_models.tongyi import ChatTongyi
from app.core.config import settings


def get_chat_model() -> BaseChatModel:

    timeout = settings.llm_timeout

    # 判断：如果配置里选了openai，并且填了API key
    if settings.llm_provider.lower() == "openai" and settings.openai_api_key:
        # 就返回OpenAI的模型
        return ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key, request_timeout=timeout)
    
    if settings.llm_provider.lower() == "dashscope" and settings.dashscope_api_key:
        return ChatTongyi(model=settings.dashscope_model, api_key=settings.dashscope_api_key, timeout=timeout)
    
    # 否则返回本地Ollama模型（qwen2.5:7b）
    return ChatOllama(base_url=settings.ollama_base_url, model=settings.ollama_model, timeout=timeout)


def get_streaming_chat_model() -> BaseChatModel:
    """流式模型工厂，用于 SSE 逐 token 输出"""
    timeout = settings.llm_timeout

    if settings.llm_provider.lower() == "openai" and settings.openai_api_key:
        return ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key, request_timeout=timeout, streaming=True)

    if settings.llm_provider.lower() == "dashscope" and settings.dashscope_api_key:
        return ChatTongyi(model=settings.dashscope_model, api_key=settings.dashscope_api_key, timeout=timeout, streaming=True)

    return ChatOllama(base_url=settings.ollama_base_url, model=settings.ollama_model, timeout=timeout)
