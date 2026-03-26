# app/auth/__init__.py
from flask import Blueprint

# 创建 auth 蓝图（前缀 /auth）
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# 导入路由（必须在蓝图创建后导入，避免循环引用）
from app.auth import oauth2, sso

# 注册核心路由
auth_bp.add_url_rule("/authorize", view_func=oauth2.authorize, methods=["GET"])  # 跳转 IAM 授权页
auth_bp.add_url_rule("/callback", view_func=oauth2.callback, methods=["GET"])   # 授权码回调
auth_bp.add_url_rule("/logout", view_func=sso.logout, methods=["GET"])          # 登出
auth_bp.add_url_rule("/user/info", view_func=sso.get_user_info, methods=["GET"])# 获取当前登录用户信息（测试装饰器）