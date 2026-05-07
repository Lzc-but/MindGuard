"""
向量检索服务 — 封装 app/rag/ 模块，提供 FAISS 索引加载与多策略检索
"""
import logging
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS

from app.core.config import settings
from app.rag.index_construction import IndexConstructionModule
from app.rag.retrieval_optimization import RetrievalOptimizationModule

logger = logging.getLogger(__name__)

_index_module: IndexConstructionModule | None = None


def _get_index_module() -> IndexConstructionModule:
    """懒加载 IndexConstructionModule 单例"""
    global _index_module
    if _index_module is None:
        _index_module = IndexConstructionModule(
            model_key=settings.dashscope_api_key,
            model_name=settings.embedding_model,
            index_save_path=settings.vector_store_path,
        )
    return _index_module


def load_vector_store() -> FAISS | None:
    """加载本地 FAISS 向量库（委托 IndexConstructionModule）"""
    return _get_index_module().load_index()


def similarity_search(query: str, k: int = 4, score_threshold: float | None = None) -> list[str]:
    """向量相似度检索，低于阈值的 L2 距离结果被丢弃，返回文本内容列表"""
    if score_threshold is None:
        score_threshold = settings.retrieval_score_threshold
    module = _get_index_module()
    if module.vectorstore is None:
        module.load_index()
    if module.vectorstore is None:
        return []
    docs_with_scores = module.vectorstore.similarity_search_with_score(query, k=k)
    return [doc.page_content for doc, score in docs_with_scores if score <= score_threshold]


def _load_chunks() -> List[Document]:
    """从知识库目录加载并分块所有文档"""
    knowledge_dir = Path(settings.knowledge_path)
    files = list(knowledge_dir.glob("*.txt")) + list(knowledge_dir.glob("*.md")) + list(knowledge_dir.glob("*.pdf"))
    if not files:
        return []
    docs = []
    for fp in files:
        if fp.suffix.lower() == ".pdf":
            loader = PyPDFLoader(str(fp))
        else:
            loader = TextLoader(str(fp), encoding="utf-8")
        docs.extend(loader.load())
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=80)
    return splitter.split_documents(docs)


def hybrid_search(query: str, top_k: int = 3) -> list[str]:
    """混合检索：BM25 + 向量 + RRF 重排序，chunks 不可用时退化为纯向量检索"""
    module = _get_index_module()
    if module.vectorstore is None:
        module.load_index()
    if module.vectorstore is None:
        return []
    chunks = _load_chunks()
    if not chunks:
        return similarity_search(query, k=top_k)
    retriever = RetrievalOptimizationModule(module.vectorstore, chunks)
    docs = retriever.hybrid_search(query, top_k=top_k)
    return [doc.page_content for doc in docs]


def invalidate_cache() -> None:
    """清除索引模块缓存（knowledge 重建索引后调用）"""
    global _index_module
    _index_module = None