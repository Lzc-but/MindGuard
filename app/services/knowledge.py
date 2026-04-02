from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS

from app.core.config import settings
from app.utils.vector import get_embeddings
from app.services.rag import load_vector_store
from app.rag.data_preparation import DataPreparationModule

def build_knowledge_index() -> int:
    """重新构建知识库索引"""

    # 1. 获取知识库文件夹路径
    knowledge_dir = Path(settings.knowledge_path)

    # 2. 找出文件夹里所有 .txt 和 .md 文件
    files = list(knowledge_dir.glob("*.txt")) + list(knowledge_dir.glob("*.md"))
    if not files:
        raise ValueError("No text/markdown files found in knowledge directory")

    docs = []
    # 3. 循环读取每一个文件内容
    for file_path in files:
        loader = TextLoader(str(file_path), encoding="utf-8")
        docs.extend(loader.load())

    # 4. 文本切割器（把长文章切成小块）
    # chunk_size=500：每块 500 字符
    # chunk_overlap=80：块之间重叠 80 字符（保证语义不切断）
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=80)

    # 5. 执行切割 → 得到很多小片段（chunks）
    chunks = splitter.split_documents(docs)

    # 6. 把所有小片段 → 生成向量 → 创建 FAISS 向量库
    vector_store = FAISS.from_documents(chunks, get_embeddings())

    # 7. 把向量库保存到本地（data/vector_store）
    vector_store.save_local(settings.vector_store_path)

    # 8. 返回一共切了多少块（给前端显示）
    return len(chunks)

def build_knowledge_by_file(file_path: str) -> int:
    """新增知识库索引"""

    file_path = Path(file_path)

    # 安全校验：必须在知识库目录内
    if settings.knowledge_path not in str(file_path.parent.resolve()):
        raise ValueError("Invalid file path")
    data_module = DataPreparationModule(file_path)
    # 读取文件
    try:
        data_module.load_documents()
        # loader = TextLoader(str(file_path), encoding="utf-8")
        # docs = loader.load()
    except Exception as e:
        raise ValueError(f"Failed to read file: {str(e)}") from e

    # if not docs:
    #     return 0

    # 切分文本
    chunks = data_module.chunk_documents()


    # 加载现有向量库 → 增量添加
    vector_store = load_vector_store()

    if vector_store is None:
        # 第一次创建
        vector_store = FAISS.from_documents(chunks, get_embeddings())
    else:
        # 追加进去（不覆盖、不重建）
        vector_store.add_documents(chunks)

    # 保存
    vector_store.save_local(settings.vector_store_path)
    return len(chunks)