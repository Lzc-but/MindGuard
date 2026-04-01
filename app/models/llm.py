from langchain_core.language_models.chat_models import BaseChatModel
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_community.chat_models.tongyi import ChatTongyi
from app.core.config import settings


def get_chat_model() -> BaseChatModel:

    # 判断：如果配置里选了openai，并且填了API key
    if settings.llm_provider.lower() == "openai" and settings.openai_api_key:
        # 就返回OpenAI的模型
        return ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key)
    
    if settings.llm_provider.lower() == "dashscope" and settings.dashscope_api_key:
        return ChatTongyi(model=settings.dashscope_model, api_key=settings.dashscope_api_key)
    
    # 否则返回本地Ollama模型（qwen2.5:7b）
    return ChatOllama(base_url=settings.ollama_base_url, model=settings.ollama_model)
