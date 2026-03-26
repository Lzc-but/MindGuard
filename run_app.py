# run_app.py
import logging
from app import create_app

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 创建应用实例（默认 dev 环境）
app = create_app(env="dev")

# 配置会话密钥（必须，否则 session 无法使用）
app.secret_key = app.config.get("SECRET_KEY")

if __name__ == "__main__":
    # 启动 Flask 应用
    logger.info("启动 Flask 应用，访问地址：http://127.0.0.1:5000")
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=app.config.get("DEBUG", True)
    )