# app/auth/decorators.py
import logging
from functools import wraps
from flask import session, jsonify
from app.auth.exceptions import AuthError

logger = logging.getLogger(__name__)

def login_required(f):
    """
    登录验证装饰器：校验用户是否已登录（会话中 is_login 为 True）
    使用方式：@login_required 装饰视图函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. 校验会话是否有效
        if not session.get("is_login") or not session.get("iam_user_id"):
            logger.warning("未登录用户访问受保护资源")
            raise AuthError("请先登录", code=401)
        
        # 2. 校验 token 是否过期（可选，根据 IAM 规则实现）
        # if is_token_expired(session.get("access_token")):
        #     raise AuthError("登录已过期，请重新登录", code=401)
        
        # 3. 执行原函数
        return f(*args, **kwargs)
    return decorated_function

def tenant_required(f):
    """
    租户权限验证装饰器（扩展：校验用户是否有租户权限）
    """
    @wraps(f)
    @login_required  # 依赖登录验证
    def decorated_function(*args, **kwargs):
        from app.extensions.db import get_db_session
        from app.models.user import User
        
        db_session = get_db_session()
        iam_user_id = session.get("iam_user_id")
        user = db_session.query(User).filter_by(iam_user_id=iam_user_id).first()
        
        if not user or not user.tenant_id:
            logger.warning(f"用户 {iam_user_id} 无租户权限")
            raise AuthError("无租户访问权限", code=403)
        
        # 将租户 ID 传入视图函数
        kwargs["tenant_id"] = user.tenant_id
        return f(*args, **kwargs)
    return decorated_function