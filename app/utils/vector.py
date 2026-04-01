from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.embeddings import DashScopeEmbeddings
from app.core.config import settings

def get_embeddings() -> HuggingFaceEmbeddings:
    return DashScopeEmbeddings(model=settings.embedding_model, dashscope_api_key=settings.dashscope_api_key)
