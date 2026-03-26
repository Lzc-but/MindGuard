# app/utils/config.py
import os
import logging
from dotenv import load_dotenv
from pathlib import Path

# 初始化日志
logger = logging.getLogger(__name__)

# 加载 .env 文件（优先加载项目根目录的 .env）
# 注：需提前安装 python-dotenv：pip install python-dotenv
BASE_DIR = Path(__file__).parent.parent.parent.absolute()  # 项目根目录
ENV_FILE = os.path.join(BASE_DIR, ".env")
if os.path.exists(ENV_FILE):
    load_dotenv(ENV_FILE, override=True)  # override=True 允许覆盖系统环境变量
    logger.debug(f"✅ 已加载环境变量文件：{ENV_FILE}")
else:
    logger.warning(f"⚠️ 未找到 .env 文件：{ENV_FILE}，将使用系统环境变量")

# 支持的环境列表
SUPPORTED_ENVS = ["dev", "prod", "test"]
# 默认环境
DEFAULT_ENV = "dev"


def load_config(env: str = None) -> dict:
    """
    加载指定环境的配置（核心函数）
    :param env: 环境名称（dev/prod/test），若为 None 则从环境变量 FLASK_ENV 获取
    :return: 合并后的配置字典
    """
    # 1. 确定当前环境
    current_env = env or os.getenv("FLASK_ENV", DEFAULT_ENV)
    if current_env not in SUPPORTED_ENVS:
        logger.warning(f"⚠️ 不支持的环境 {current_env}，将使用默认环境 {DEFAULT_ENV}")
        current_env = DEFAULT_ENV

    # 2. 加载基础配置（base.py）
    try:
        from config.base import __dict__ as base_config
        logger.debug("✅ 已加载基础配置（config/base.py）")
    except ImportError as e:
        raise ImportError(f"加载基础配置失败：{e}，请检查 config/base.py 是否存在")

    # 3. 加载当前环境配置（如 dev.py）
    try:
        env_module = __import__(f"config.{current_env}", fromlist=["__dict__"])
        env_config = env_module.__dict__
        logger.debug(f"✅ 已加载 {current_env} 环境配置（config/{current_env}.py）")
    except ImportError as e:
        raise ImportError(f"加载 {current_env} 环境配置失败：{e}，请检查 config/{current_env}.py 是否存在")

    # 4. 合并配置（环境配置覆盖基础配置）
    merged_config = {}
    # 先加入基础配置（过滤掉内置变量，如 __file__/__name__ 等）
    for key, value in base_config.items():
        if not key.startswith("__") and not callable(value):
            merged_config[key] = value
    # 再加入环境配置（覆盖基础配置的同名项）
    for key, value in env_config.items():
        if not key.startswith("__") and not callable(value):
            merged_config[key] = value

    # 5. 注入环境标识（方便业务代码判断当前环境）
    merged_config["FLASK_ENV"] = current_env
    logger.info(f"✅ 配置加载完成，当前环境：{current_env}")

    return merged_config


def get_config_value(key: str, default=None) -> any:
    """
    快速获取单个配置值（封装 load_config，避免重复加载）
    :param key: 配置键名
    :param default: 默认值
    :return: 配置值
    """
    # 缓存配置（避免每次调用都重新加载）
    if not hasattr(get_config_value, "_cached_config"):
        get_config_value._cached_config = load_config()

    return get_config_value._cached_config.get(key, default)


# ========== 便捷函数：快速获取常用配置 ==========
def get_db_uri() -> str:
    """快速获取数据库连接 URI"""
    return get_config_value("SQLALCHEMY_DATABASE_URI")


def get_redis_url() -> str:
    """快速获取 Redis 连接 URL"""
    return get_config_value("REDIS_URL")


def get_oauth2_config() -> dict:
    """快速获取 OAuth2 相关配置"""
    return {
        "client_id": get_config_value("OAUTH2_CLIENT_ID"),
        "client_secret": get_config_value("OAUTH2_CLIENT_SECRET"),
        "authorize_url": get_config_value("OAUTH2_AUTHORIZE_URL"),
        "token_url": get_config_value("OAUTH2_TOKEN_URL"),
        "user_info_path": get_config_value("OAUTH2_USER_INFO_PATH"),
        "redirect_uri": get_config_value("OAUTH2_REDIRECT_URI"),
        "oauth2_iam_domain": get_config_value("OAUTH2_IAM_DOMAIN") 
    }