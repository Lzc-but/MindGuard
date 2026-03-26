# app/auth/sso.py
import uuid
import logging
from flask import session, redirect, jsonify, current_app
from app.extensions.db import get_db_session
from app.models.user import User
from app.models.tenant import Tenant
from app.auth.exceptions import UserNotFoundError, TenantAssignError
from app.auth.decorators import login_required

# 初始化日志
logger = logging.getLogger(__name__)

def handle_first_login(iam_user_info):
    """
    处理首次登录：检查用户是否存在，不存在则创建并分配租户
    :param iam_user_info: IAM 返回的用户信息
    """
    db_session = get_db_session()
    iam_user_id = iam_user_info.get("user_id")
    
    try:
        # 1. 查询用户是否存在
        user = db_session.query(User).filter_by(iam_user_id=iam_user_id).first()
        
        if not user:
            logger.info(f"用户 {iam_user_id} 首次登录，开始自动分配租户并创建用户")
            
            # 2. 自动分配租户（规则：按 IAM 用户 ID 生成租户，或默认租户）
            tenant = assign_tenant(iam_user_info)
            
            # 3. 创建新用户
            new_user = User(
                id=str(uuid.uuid4()),  # 生成唯一用户 ID
                username=iam_user_info.get("username"),
                phone=iam_user_info.get("phone"),
                email=iam_user_info.get("email"),
                iam_user_id=iam_user_id,
                tenant_id=tenant.id,
                is_first_login=True  # 标记首次登录
            )
            db_session.add(new_user)
            db_session.commit()
            logger.info(f"用户 {new_user.username} 创建成功，分配租户：{tenant.name}")
        else:
            # 非首次登录，更新首次登录标识
            if user.is_first_login:
                user.is_first_login = False
                db_session.commit()
            logger.info(f"用户 {user.username} 已存在，无需重复创建")
    
    except Exception as e:
        db_session.rollback()
        logger.error(f"处理首次登录失败：{str(e)}")
        raise TenantAssignError(f"首次登录租户分配失败：{str(e)}")

def assign_tenant(iam_user_info):
    """
    自动分配租户（可自定义规则，此处示例：按用户名生成租户，无则创建）
    :param iam_user_info: IAM 用户信息
    :return: Tenant 实例
    """
    db_session = get_db_session()
    username = iam_user_info.get("username")
    tenant_name = f"tenant_{username}"  # 租户命名规则
    
    # 检查租户是否存在，不存在则创建
    tenant = db_session.query(Tenant).filter_by(name=tenant_name).first()
    if not tenant:
        tenant_id = str(uuid.uuid4())
        tenant = Tenant(
            id=tenant_id,
            name=tenant_name,
            description=f"自动分配租户 - {username}"
        )
        db_session.add(tenant)
        db_session.commit()
        logger.info(f"创建新租户：{tenant_name}（ID：{tenant_id}）")
    
    return tenant

@login_required
def get_user_info():
    """
    获取当前登录用户信息（测试 @login_required 装饰器）
    路由：/auth/user/info
    """
    db_session = get_db_session()
    iam_user_id = session.get("iam_user_id")
    
    # 查询用户详情
    user = db_session.query(User).filter_by(iam_user_id=iam_user_id).first()
    if not user:
        raise UserNotFoundError("用户信息不存在")
    
    return {
        "username": user.username,
        "phone": user.phone,
        "email": user.email,
        "iam_user_id": user.iam_user_id,
        "tenant_id": user.tenant_id,
        "is_first_login": user.is_first_login,
        "create_time": user.create_time.strftime("%Y-%m-%d %H:%M:%S")
    }

def logout():
    """
    登出：清除会话 + 通知 IAM 登出（可选）
    路由：/auth/logout
    """
    # 1. 清除本地会话
    session.clear()
    # 2. 通知 IAM 登出（可选，根据 IAM 接口规范实现）
    # revoke_token(session.get("access_token"))
    logger.info("用户已登出，会话已清除")
    return redirect("/auth/authorize")  # 登出后跳转至授权页