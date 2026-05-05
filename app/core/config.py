from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# 项目根目录（自动找到 mental_guard_ai 文件夹）
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # 项目基础信息
    app_name: str = "Mental Guard AI"   # 项目名字
    app_env: str = "dev"                # 开发环境
    app_host: str = "0.0.0.0"           # 服务监听地址
    app_port: int = 8000                # 服务端口

    # JWT登录权限配置
    jwt_secret_key: str = "change_me_in_env"    # 密钥
    jwt_algorithm: str = "HS256"                # 加密算法
    access_token_expire_minutes: int = 60       # Token有效期60分钟

    # AI大模型配置（ollma/openai）
    openai_api_key: str = ""                        # OpenAI密钥
    openai_model: str = "gpt-4o-mini"               # GPT模型
    ollama_base_url: str = "http://localhost:11434" # 本地Ollma地址
    ollama_model: str = "qwen2.5:7b"                # 本地运行的模型
    llm_provider: str = "ollama"                    # 默认使用本地模型
    llm_timeout: int = 30                           # LLM请求超时秒数
    retrieval_score_threshold: float = 1.0            # 向量检索L2距离阈值（越小越严格，默认1.0≈余弦0.5+）
    
    # 阿里云百炼
    dashscope_api_key: str = ""
    dashscope_model: str = "qwen3-max"

    # 嵌入模型
    embedding_model: str = "text-embedding-v1"

    # 项目所有文件夹路径
    vector_store_path: str = str(BASE_DIR / "data" / "vector_store")    # 向量库
    knowledge_path: str = str(BASE_DIR / "data" / "knowledge")          # 知识库文件
    exports_path: str = str(BASE_DIR / "data" / "exports")              # Excel导出
    logs_path: str = str(BASE_DIR / "data" / "logs")                    # 日志
    model_path: str = str(BASE_DIR / "models" / "finetuned")            # 微调模型
    sqlite_path: str = str(BASE_DIR / "data" / "app.db")                # SQLite数据库

    # 外部服务地址
    mcp_endpoint: str = "http://localhost:9001/mcp/mental-state"

    # 管理员默认账号密码
    admin_username: str = "admin"
    admin_password: str = "admin123"

    # 从 .env 文件读取配置
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
