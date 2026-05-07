from pathlib import Path
from typing import Union

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader

from app.core.config import settings
from app.services.retrieval import invalidate_cache
from app.rag.index_construction import IndexConstructionModule
from app.rag.data_preparation import DataPreparationModule


def _create_index_module() -> IndexConstructionModule:
    return IndexConstructionModule(
        model_key=settings.dashscope_api_key,
        model_name=settings.embedding_model,
        index_save_path=settings.vector_store_path,
    )


def build_knowledge_index() -> int:
    """全量重建知识库索引（使用 IndexConstructionModule 分批处理 DashScope 限制）"""
    knowledge_dir = Path(settings.knowledge_path)
    files = list(knowledge_dir.glob("*.txt")) + list(knowledge_dir.glob("*.md")) + list(knowledge_dir.glob("*.pdf"))
    if not files:
        return 0

    docs = []
    for file_path in files:
        if file_path.suffix.lower() == ".pdf":
            loader = PyPDFLoader(str(file_path))
        else:
            loader = TextLoader(str(file_path), encoding="utf-8")
        docs.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=80)
    chunks = splitter.split_documents(docs)

    index_module = _create_index_module()
    index_module.build_vector_index(chunks)
    index_module.save_index()
    invalidate_cache()
    return len(chunks)


def build_knowledge_by_file(file_path: Union[str, Path]) -> int:
    """增量构建知识库索引（Markdown 结构感知分块 + batch 向量化）"""
    file_path = Path(file_path)
    if settings.knowledge_path not in str(file_path.parent.resolve()):
        raise ValueError("Invalid file path")
    data_module = DataPreparationModule(str(file_path))
    try:
        data_module.load_documents()
    except Exception as e:
        raise ValueError(f"Failed to read file: {str(e)}") from e

    chunks = data_module.chunk_documents()

    index_module = _create_index_module()
    vector_store = index_module.load_index()

    if vector_store is None:
        index_module.build_vector_index(chunks)
    else:
        index_module.add_documents(chunks)

    index_module.save_index()
    invalidate_cache()
    return len(chunks)