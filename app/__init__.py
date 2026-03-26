# app/__init__.py
import logging
from flask import Flask, jsonify, request
from werkzeug.exceptions import NotFound
from app.auth.exceptions import AuthError
from app.utils.config import load_config
from app.extensions.db import init_db, close_db_session

# 初始化日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(env: str = None) -> Flask:
    """创建 Flask 应用实例"""
    # 1. 初始化 Flask 应用
    app = Flask(__name__)
    
    # 2. 加载配置
    config = load_config(env)
    app.config.update(config)
    logger.info(f"Flask 应用配置加载完成，当前环境：{config.get('FLASK_ENV')}")
    
    # 3. 初始化扩展
    init_db(app)  # 初始化数据库
    app.teardown_appcontext(close_db_session)  # 请求结束关闭数据库会话
    
    # 4. 注册蓝图
    from app.auth import auth_bp
    app.register_blueprint(auth_bp)
    logger.info("已注册 auth 蓝图")
    
    # 新增：注册模拟 IAM 蓝图
    from app.mock_iam import mock_iam_bp
    app.register_blueprint(mock_iam_bp)
    logger.info("已注册模拟 IAM 蓝图")
    
    # 5. 添加根路由
    @app.route("/")
    def index():
        return jsonify({
            "message": "RAG 美食问答系统已启动",
            "status": "success",
            "docs": "访问 /auth/login 测试认证接口"
        }), 200
    
    # 6. 优化全局异常处理器
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, AuthError):
            return jsonify({"error": e.message}), e.code
        elif isinstance(e, NotFound):
            return jsonify({
                "error": "请求的接口不存在",
                "request_url": e.description.split()[-1],
                "code": 404
            }), 404
        logger.error(f"全局异常：{str(e)}")
        return jsonify({"error": "服务器内部错误", "code": 500}), 500
    
    @app.route("/api/recipe/search", methods=["GET"])
    def search_recipe():
        """菜谱检索接口（示例）"""
        keyword = request.args.get("keyword", "")
        if not keyword:
            return jsonify({"error": "请传入检索关键词（?keyword=鱼香肉丝）"}), 400
        
        # 后续可接入你的 RAG 检索逻辑
        return jsonify({
            "keyword": keyword,
            "status": "success",
            "result": [
                {"title": f"{keyword}（家常版）", "url": "/recipe/1"},
                {"title": f"{keyword}（川菜正宗版）", "url": "/recipe/2"}
            ]
        }), 200
    return app

