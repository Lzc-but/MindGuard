# config/dev.py
import os
from .base import *  # 继承基础配置

# ===================== 开发环境专属基础配置 =====================
# 开启调试模式
DEBUG = True
# 开发环境允许的主机（通配符，方便本地调试）
ALLOWED_HOSTS = ["*"]
# 开发环境日志级别改为 DEBUG
LOG_LEVEL = "DEBUG"
# 开启 SQL 语句打印（方便调试 SQL）
SQLALCHEMY_ECHO = True

# ===================== 开发环境数据库配置 =====================
# 开发环境数据库地址（本地/测试库）
DB_HOST = os.getenv("DEV_DB_HOST", "127.0.0.1")
# 开发环境数据库端口
DB_PORT = os.getenv("DEV_DB_PORT", 3306)
# 开发环境数据库名
DB_NAME = os.getenv("DEV_DB_NAME", "enterprise_sso_dev")
# 开发环境数据库用户名
DB_USER = os.getenv("DEV_DB_USER", "root")
# 开发环境数据库密码
DB_PASSWORD = os.getenv("DEV_DB_PASSWORD", "123456")
# 拼接数据库连接串
SQLALCHEMY_DATABASE_URI = f"{DB_TYPE}+{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset={DB_CHARSET}"

# ===================== 开发环境 Redis 配置 =====================
# 开发环境 Redis 地址（本地）
REDIS_HOST = os.getenv("DEV_REDIS_HOST", "127.0.0.1")
# 开发环境 Redis 端口
REDIS_PORT = os.getenv("DEV_REDIS_PORT", 6379)
# 开发环境 Redis 密码（本地通常无密码）
REDIS_PASSWORD = os.getenv("DEV_REDIS_PASSWORD", "")
# Redis 连接串
REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}?socket_timeout={REDIS_TIMEOUT}"

# # ===================== 开发环境 OAuth2（IAM）配置 =====================
# # 开发环境 IAM 域名（测试环境 IAM 地址）
# OAUTH2_IAM_DOMAIN = os.getenv("DEV_OAUTH2_IAM_DOMAIN", "http://test-iam.enterprise.com")
# # 开发环境客户端 ID（测试环境申请的 OAuth2 客户端 ID）
# OAUTH2_CLIENT_ID = os.getenv("DEV_OAUTH2_CLIENT_ID", "dev-sso-client-123")
# # 开发环境客户端密钥（测试环境）
# OAUTH2_CLIENT_SECRET = os.getenv("DEV_OAUTH2_CLIENT_SECRET", "dev-secret-456")
# # 授权码请求地址
# OAUTH2_AUTHORIZE_URL = f"{OAUTH2_IAM_DOMAIN}/oauth2/authorize"
# # Token 换取地址
# OAUTH2_TOKEN_URL = f"{OAUTH2_IAM_DOMAIN}/oauth2/token"
# # 完整的回调地址（开发环境本地地址）
# OAUTH2_REDIRECT_URI = f"http://127.0.0.1:5000{OAUTH2_REDIRECT_URI}"

# ===================== 模拟 OAuth2（IAM）配置 =====================
OAUTH2_IAM_DOMAIN = "http://127.0.0.1:5000/mock-iam"  # 本地模拟 IAM 地址
OAUTH2_CLIENT_ID = "dev-sso-client-123"  # 模拟的 Client Secret（和 mock_iam/oauth2.py 中保持一致）
OAUTH2_CLIENT_SECRET = "dev-secret-456"  # 直接使用模拟的 client_secret
OAUTH2_AUTHORIZE_URL = f"{OAUTH2_IAM_DOMAIN}/oauth2/authorize"  # 模拟授权页地址
OAUTH2_TOKEN_URL = f"{OAUTH2_IAM_DOMAIN}/oauth2/token"  # 模拟获取 token 地址
OAUTH2_REDIRECT_URI = "http://127.0.0.1:5000/auth/callback"  # 应用回调地址

# ===================== 开发环境定时任务配置 =====================
# 开发环境定时任务频率调高（如 10 分钟一次，避免频繁同步）
SYNC_USER_CRON = "*/10 * * * *"
# 开发环境允许手动触发定时任务
SCHEDULER_ALLOW_MANUAL = True