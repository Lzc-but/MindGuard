from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS

from app.core.config import settings
from app.utils.vector import get_embeddings


def build_knowledge_index() -> int:
    knowledge_dir = Path(settings.knowledge_path)
    files = list(knowledge_dir.glob("*.txt")) + list(knowledge_dir.glob("*.md"))
    if not files:
        raise ValueError("No text/markdown files found in knowledge directory")

    docs = []
    for file_path in files:
        loader = TextLoader(str(file_path), encoding="utf-8")
        docs.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=80)
    chunks = splitter.split_documents(docs)
    vector_store = FAISS.from_documents(chunks, get_embeddings())
    vector_store.save_local(settings.vector_store_path)
    return len(chunks)
