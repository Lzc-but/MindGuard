from langchain_community.vectorstores import FAISS

from app.core.config import settings
from app.utils.vector import get_embeddings

import logging

logger = logging.getLogger(__name__)

def load_vector_store() -> FAISS | None:
    """加载本地保存的FAISS向量库"""
    try:
        return FAISS.load_local(
            settings.vector_store_path,             # 向量库存放位置
            get_embeddings(),                       # 使用的向量模型
            allow_dangerous_deserialization=True,   # 允许加载本地文件
        )
    except Exception:
        return None


def similarity_search(query: str, k: int = 4) -> list[str]:
    # 加载向量库
    vector_store = load_vector_store()
    if vector_store is None:
        return []
    # 找和问题最相似的k条资料
    docs = vector_store.similarity_search(query, k=k)

    # 只把文档内容提取返回给AI
    return [doc.page_content for doc in docs]
