from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.knowledge import router as knowledge_router
from app.api.mental import router as mental_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.utils.file import ensure_data_dirs
import fastapi_cdn_host

def create_app() -> FastAPI:
    # 创建FastAPI主应用实例
    app = FastAPI(title=settings.app_name, version="0.1.0")

    # 修复接口文档的加载速度
    fastapi_cdn_host.patch_docs(app)

    # 自动创建项目需要的文件夹
    ensure_data_dirs()

    # 注册全局异常处理
    register_exception_handlers(app)

    # 注册4个核心模块
    app.include_router(auth_router)  # 权限、登录接口
    app.include_router(chat_router)  #聊天对话接口
    app.include_router(knowledge_router)  # 知识库管理接口
    app.include_router(mental_router)  # 心理状态识别接口

    # 注册一个健康检查接口
    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok", "app": settings.app_name}

    return app


app = create_app()
