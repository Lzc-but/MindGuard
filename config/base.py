
import os
from pathlib import Path

# ===================== 项目基础配置 =====================
# 项目根目录（自动计算，无需手动改）
BASE_DIR = Path(__file__).parent.parent.absolute()
# 应用名称
APP_NAME = "enterprise-sso-sync"
# API 版本前缀
API_VERSION = "/api/v1"
# 调试模式默认关闭（各环境自行覆盖）
DEBUG = False
# 密钥（生产环境通过环境变量注入，此处仅占位）
SECRET_KEY = os.getenv("SECRET_KEY", "default-dev-key-keep-safe")

# ===================== 日志配置 =====================
# 日志目录
LOG_DIR = os.path.join(BASE_DIR, "logs")
# 日志级别（通用为 INFO，开发环境可改为 DEBUG）
LOG_LEVEL = "INFO"
# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"

# ===================== 数据库通用配置（SQLAlchemy） =====================
# 数据库类型（通用，如 mysql/postgresql）
DB_TYPE = "mysql"
# 数据库驱动
DB_DRIVER = "pymysql"
# 数据库编码
DB_CHARSET = "utf8mb4"
# 数据库连接池大小
DB_POOL_SIZE = 10
# 连接池超时时间
DB_POOL_TIMEOUT = 30
# 是否开启 SQL 语句打印（生产环境关闭，开发环境开启）
SQLALCHEMY_ECHO = False
# 禁用 SQLAlchemy 旧版警告
SQLALCHEMY_TRACK_MODIFICATIONS = False

# ===================== Redis 通用配置 =====================
# Redis 数据库编号（通用，如 0 库存缓存，1 库存分布式锁）
REDIS_DB = 0
# Redis 连接超时时间
REDIS_TIMEOUT = 5
# 分布式锁默认超时时间（秒）
LOCK_DEFAULT_EXPIRE = 60

# ===================== OAuth2 通用配置（IAM） =====================
# OAuth2 授权模式（固定为授权码模式）
OAUTH2_GRANT_TYPE = "authorization_code"
# Token 有效期（通用，由 IAM 定义）
OAUTH2_TOKEN_EXPIRE = 3600
# 用户信息接口路径（IAM 通用路径，域名由各环境覆盖）
OAUTH2_USER_INFO_PATH = "/api/v1/user/info"
# 授权码回调路径（通用，域名由各环境覆盖）
OAUTH2_REDIRECT_URI = "/auth/callback"

# ===================== 定时任务通用配置 =====================
# 定时任务时区
SCHEDULER_TIMEZONE = "Asia/Shanghai"
# 是否开启定时任务（默认开启）
SCHEDULER_ENABLED = True