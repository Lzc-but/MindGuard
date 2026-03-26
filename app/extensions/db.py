# app/extensions/db.py
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
from app.utils.config import load_config

# 初始化日志
logger = logging.getLogger(__name__)

# 声明 SQLAlchemy 基类（所有模型继承此类）
Base = declarative_base()

# 全局变量：存储数据库引擎和会话工厂
_engine = None
_db_session = None


def init_db(app=None):
    """
    初始化 SQLAlchemy 连接
    :param app: Flask 应用实例（可选，用于从 app.config 读取配置）
    """
    global _engine, _db_session

    # 加载配置（优先从 Flask app 读取，否则从 config 模块读取）
    if app and hasattr(app, 'config'):
        config = app.config
    else:
        config = load_config()
        
    db_charset = config.get("DB_CHARSET", "utf8mb4")
    # 拼接数据库连接 URI（兼容你定义的 config/base.py + dev.py 配置）
    db_uri = config.get("SQLALCHEMY_DATABASE_URI")
    if not db_uri:
        # 若未直接配置 URI，从基础字段拼接（兼容手动配置场景）
        db_type = config.get("DB_TYPE", "mysql")
        db_driver = config.get("DB_DRIVER", "pymysql")
        db_user = config.get("DB_USER")
        db_password = config.get("DB_PASSWORD")
        db_host = config.get("DB_HOST")
        db_port = config.get("DB_PORT")
        db_name = config.get("DB_NAME")
        db_charset = config.get("DB_CHARSET", "utf8mb4")

        if not all([db_user, db_host, db_name]):
            raise ValueError("数据库配置不完整！请检查 DB_USER/DB_HOST/DB_NAME 等配置")

        db_uri = f"{db_type}+{db_driver}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset={db_charset}"

    try:
        # 创建 SQLAlchemy 引擎（配置连接池、超时等）
        _engine = create_engine(
            db_uri,
            pool_size=config.get("DB_POOL_SIZE", 10),  # 连接池大小
            pool_timeout=config.get("DB_POOL_TIMEOUT", 30),  # 连接超时
            pool_recycle=3600,  # 连接回收时间（避免长连接失效）
            echo=config.get("SQLALCHEMY_ECHO", False),  # 是否打印 SQL 语句
            # encoding=db_charset
        )

        # 创建会话工厂（线程安全的 scoped_session）
        _db_session = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=_engine
            )
        )

        # 绑定会话到 Base 基类（模型可直接使用 query 属性）
        Base.query = _db_session.query_property()

        # 测试数据库连接
        test_db_connection()
        logger.info("✅ SQLAlchemy 初始化成功，数据库连接正常！")

    except OperationalError as e:
        logger.error(f"❌ 数据库连接失败：{str(e)}，请检查数据库地址/账号/密码是否正确")
        raise
    except SQLAlchemyError as e:
        logger.error(f"❌ SQLAlchemy 初始化失败：{str(e)}")
        raise
    except Exception as e:
        logger.error(f"❌ 数据库初始化未知错误：{str(e)}")
        raise


def test_db_connection():
    """
    测试数据库连接是否正常（核心函数）
    """
    if not _engine:
        raise RuntimeError("请先调用 init_db() 初始化数据库引擎！")

    # 执行简单的 SQL 测试连接
    try:
        with _engine.connect() as conn:
            # 执行无副作用的测试语句（兼容 MySQL/PostgreSQL）
            result = conn.execute(text('SELECT 1'))
            # conn.execute("SELECT 1")
        logger.debug("数据库连接测试通过")
    except OperationalError as e:
        raise RuntimeError(f"数据库连接测试失败：{str(e)}")


def get_db_session():
    """
    获取数据库会话实例（供业务代码调用）
    :return: scoped_session 实例
    """
    if not _db_session:
        raise RuntimeError("数据库会话未初始化！请先调用 init_db()")
    return _db_session


def close_db_session(exception=None):
    """
    关闭数据库会话（用于 Flask 应用的 teardown 回调）
    """
    global _db_session
    if _db_session:
        _db_session.remove()
        logger.debug("数据库会话已关闭")


def create_all_tables():
    """
    创建所有数据表（基于 Base 基类的模型）
    注：生产环境建议使用 Alembic 迁移，此函数仅用于开发/测试环境快速建表
    """
    if not _engine:
        raise RuntimeError("请先调用 init_db() 初始化数据库引擎！")

    # 手动导入所有模型（确保 SQLAlchemy 识别）
    try:
        from app.models import User, Tenant, Team, user_team_rel
        print("✅ 已导入所有模型")
    except ImportError as e:
        print(f"❌ 导入模型失败：{e}")
        raise

    try:
        Base.metadata.create_all(bind=_engine)
        print("✅ 所有数据表创建成功！")
    except SQLAlchemyError as e:
        print(f"❌ 创建数据表失败：{str(e)}")
        raise