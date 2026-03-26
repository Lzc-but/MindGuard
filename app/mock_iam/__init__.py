# app/mock_iam/__init__.py
from flask import Blueprint

# 创建模拟 IAM 蓝图（前缀 /mock-iam）
mock_iam_bp = Blueprint("mock_iam", __name__, url_prefix="/mock-iam")

# 导入路由
from app.mock_iam import oauth2

# 注册模拟 IAM 路由
# mock_iam_bp.add_url_rule("/oauth2/authorize", view_func=oauth2.authorize, methods=["GET"])  # 模拟授权页
# mock_iam_bp.add_url_rule("/oauth2/token", view_func=oauth2.get_token, methods=["POST"])    # 模拟获取token
# mock_iam_bp.add_url_rule("/api/v1/user/info", view_func=oauth2.get_user_info, methods=["GET"])  # 模拟用户信息

# 新增：用装饰器注册剩余路由（替代手动 add_url_rule）
@mock_iam_bp.route("/oauth2/authorize", methods=["GET"])
def authorize():
    return oauth2.authorize()

@mock_iam_bp.route("/oauth2/token", methods=["POST"])
def get_token():
    return oauth2.get_token()

@mock_iam_bp.route("/api/v1/user/info", methods=["GET"])
def get_user_info():
    return oauth2.get_user_info()