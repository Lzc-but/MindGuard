"""
数据准备模块
"""

import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Any

from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from pathlib import Path
import uuid

from app.core.config import settings
logger = logging.getLogger(__name__)

class DataPreparationModule:
    """数据准备模块 - 负责数据加载、清洗和预处理"""
    def __init__(self, data_path: str):
        """
        初始化数据准备模块
        
        Args:
            data_path: 数据文件夹路径
        """
        self.data_path = data_path
        self.documents: List[Document] = []  # 父文档
        self.chunks: List[Document] = []     # 子文档（分块后的文档片段）
        self.parent_child_map: Dict[str, str] = {}  # 子块ID -> 父文档ID的映射
    
    def load_documents(self) -> List[Document]:
        """
        加载文档数据
        
        Returns:
            加载的文档列表
        """
        logger.info(f"正在从 {self.data_path} 加载文档...")
        
        # 直接读取Markdown文件以保持原始格式
        documents = []
        errors = []
        path_obj = Path(self.data_path).resolve()
        file_list: List[Path] = []
        if path_obj.is_file():
                file_list.append(path_obj)
        else:
            file_list.extend(path_obj.rglob())
        for md_file in file_list:
            try:
                file_path_obj = Path(md_file)
                if file_path_obj.suffix.lower() == ".pdf":
                    loader = PyPDFLoader(str(md_file))
                else:
                    loader = TextLoader(str(md_file), encoding="utf-8")
                loaded_docs = loader.load()
                if not loaded_docs:
                    logger.warning(f"文件 {md_file} 加载后为空，跳过")
                    continue

                # 为每个父文档分配确定性的唯一ID（基于数据根目录的相对路径）
                try:
                    data_root = Path(settings.knowledge_path).resolve()
                    relative_path = Path(md_file).resolve().relative_to(data_root).as_posix()
                except Exception:
                    relative_path = Path(md_file).as_posix()
                parent_id = hashlib.md5(relative_path.encode("utf-8")).hexdigest()

                # PDF 按页加载，每页为一个独立文档；txt/md 只有一份文档
                for doc in loaded_docs:
                    doc.metadata["parent_id"] = parent_id
                    doc.metadata["doc_type"] = "parent"
                    documents.append(doc)

            except Exception as e:
                logger.warning(f"读取文件 {md_file} 失败: {e}")
                errors.append(f"{md_file}: {e}")
        
        if not documents and errors:
            raise RuntimeError(f"所有文件加载失败: {'; '.join(errors)}")
        
        self.documents = documents
        logger.info(f"成功加载 {len(documents)} 个文档")
        return documents
    
    def chunk_documents(self) -> List[Document]:
        """
        Markdown结构感知分块

        Returns:
            分块后的文档列表
        """
        logger.info("正在进行Markdown结构感知分块...")

        if not self.documents:
            raise ValueError("请先加载文档")
        markdown_docs = []
        other_docs = []
        chunks = []
        for doc in self.documents:
            file_path = Path(doc.metadata["source"])
            if file_path.suffix.lower() == ".md":
                markdown_docs.append(doc)
            else:
                other_docs.append(doc)
                
        if markdown_docs:
            # 使用Markdown标题分割器
            chunks_md = self._markdown_header_split(markdown_docs)
            chunks.extend(chunks_md)

        if other_docs:
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=80)
            chunks_txt = splitter.split_documents(other_docs)
            chunks.extend(chunks_txt)
        # 为每个chunk添加基础元数据
        for i, chunk in enumerate(chunks):
            if 'chunk_id' not in chunk.metadata:
                # 如果没有chunk_id（比如分割失败的情况），则生成一个
                chunk.metadata['chunk_id'] = str(uuid.uuid4())
            chunk.metadata['batch_index'] = i  # 在当前批次中的索引
            chunk.metadata['chunk_size'] = len(chunk.page_content)

        self.chunks = chunks
        logger.info(f"Markdown分块完成，共生成 {len(chunks)} 个chunk")
        return chunks

    def _markdown_header_split(self, docs: List[Document]) -> List[Document]:
        """
        使用Markdown标题分割器进行结构化分割

        Returns:
            按标题结构分割的文档列表
        """
        # 定义要分割的标题层级
        headers_to_split_on = [
            ("#", "一级标题"),
            ("##", "二级标题"),
            ("###", "三级标题")
        ]

        # 创建Markdown分割器
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
            strip_headers=False  # 保留标题，便于理解上下文
        )

        all_chunks = []

        for doc in docs:
            try:
                # 检查文档内容是否包含Markdown标题
                content_preview = doc.page_content[:200]
                has_headers = any(line.strip().startswith('#') for line in content_preview.split('\n'))

                if not has_headers:
                    logger.warning(f"文档 {doc.metadata.get('source', '未知')} 内容中没有发现Markdown标题")
                    logger.debug(f"内容预览: {content_preview}")

                # 对每个文档进行Markdown分割
                md_chunks = markdown_splitter.split_text(doc.page_content)

                logger.debug(f"文档 {doc.metadata.get('source', '未知')} 分割成 {len(md_chunks)} 个chunk")

                # 如果没有分割成功，说明文档可能没有标题结构
                if len(md_chunks) <= 1:
                    logger.warning(f"文档 {doc.metadata.get('source', '未知')} 未能按标题分割，可能缺少标题结构")

                # 为每个子块建立与父文档的关系
                parent_id = doc.metadata["parent_id"]

                for i, chunk in enumerate(md_chunks):
                    # 为子块分配唯一ID
                    child_id = str(uuid.uuid4())

                    # 合并原文档元数据和新的标题元数据
                    chunk.metadata.update(doc.metadata)
                    chunk.metadata.update({
                        "chunk_id": child_id,
                        "parent_id": parent_id,
                        "doc_type": "child",  # 标记为子文档
                        "chunk_index": i      # 在父文档中的位置
                    })

                    # 建立父子映射关系
                    self.parent_child_map[child_id] = parent_id

                all_chunks.extend(md_chunks)

            except Exception as e:
                logger.warning(f"文档 {doc.metadata.get('source', '未知')} Markdown分割失败: {e}")
                # 如果Markdown分割失败，将整个文档作为一个chunk
                all_chunks.append(doc)

        logger.info(f"Markdown结构分割完成，生成 {len(all_chunks)} 个结构化块")
        return all_chunks

    def get_parent_documents(self, child_chunks: List[Document]) -> List[Document]:
        """
        根据子块获取对应的父文档（智能去重）

        Args:
            child_chunks: 检索到的子块列表

        Returns:
            对应的父文档列表（去重，按相关性排序）
        """
        # 统计每个父文档被匹配的次数（相关性指标）
        parent_relevance = {}
        parent_docs_map = {}

        # 收集所有相关的父文档ID和相关性分数
        for chunk in child_chunks:
            parent_id = chunk.metadata.get("parent_id")
            if parent_id:
                # 增加相关性计数
                parent_relevance[parent_id] = parent_relevance.get(parent_id, 0) + 1

                # 缓存父文档（避免重复查找）
                if parent_id not in parent_docs_map:
                    for doc in self.documents:
                        if doc.metadata.get("parent_id") == parent_id:
                            parent_docs_map[parent_id] = doc
                            break

        # 按相关性排序（匹配次数多的排在前面）
        sorted_parent_ids = sorted(parent_relevance.keys(),
                                 key=lambda x: parent_relevance[x],
                                 reverse=True)

        # 构建去重后的父文档列表
        parent_docs = []
        for parent_id in sorted_parent_ids:
            if parent_id in parent_docs_map:
                parent_docs.append(parent_docs_map[parent_id])

        # 收集父文档名称和相关性信息用于日志
        parent_info = []
        for doc in parent_docs:
            source = doc.metadata.get('source', '未知文件')
            parent_id = doc.metadata.get('parent_id')
            relevance_count = parent_relevance.get(parent_id, 0)
            parent_info.append(f"{source}({relevance_count}块)")

        logger.info(f"从 {len(child_chunks)} 个子块中找到 {len(parent_docs)} 个去重父文档: {', '.join(parent_info)}")
        return parent_docs
