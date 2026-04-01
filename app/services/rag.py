from langchain_community.vectorstores import FAISS

from app.core.config import settings
from app.utils.vector import get_embeddings


def load_vector_store() -> FAISS | None:
    try:
        return FAISS.load_local(
            settings.vector_store_path,
            get_embeddings(),
            allow_dangerous_deserialization=True,
        )
    except Exception:
        return None


def similarity_search(query: str, k: int = 4) -> list[str]:
    vector_store = load_vector_store()
    if vector_store is None:
        return []
    docs = vector_store.similarity_search(query, k=k)
    return [doc.page_content for doc in docs]
