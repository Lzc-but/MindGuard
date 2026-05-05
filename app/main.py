from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.knowledge import router as knowledge_router
from app.api.mental import router as mental_router
from app.api.admin.users import router as admin_users_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.services.conversation import init_chat_db
from app.services.user import init_users_db
from app.utils.file import ensure_data_dirs
import fastapi_cdn_host

def create_app() -> FastAPI:
    # 创建FastAPI主应用实例
    app = FastAPI(title=settings.app_name, version="0.1.0")

    # 修复接口文档的加载速度
    fastapi_cdn_host.patch_docs(app)

    # 自动创建项目需要的文件夹 + 初始化数据库表
    ensure_data_dirs()
    init_chat_db()
    init_users_db()

    # 注册全局异常处理
    register_exception_handlers(app)

    # 注册路由模块
    app.include_router(auth_router)           # 认证登录
    app.include_router(chat_router)           # 对话（用户端）
    app.include_router(knowledge_router)      # 知识库管理
    app.include_router(mental_router)         # 心理分析
    app.include_router(admin_users_router)    # 管理员-用户管理

    # 注册一个健康检查接口
    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok", "app": settings.app_name}

    return app


app = create_app()
