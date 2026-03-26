# app/mock_iam/oauth2.py
import uuid
import time
from flask import request, render_template_string, jsonify, redirect
from . import mock_iam_bp

# 模拟 IAM 配置
MOCK_CLIENT_ID = "dev-sso-client-123"
MOCK_CLIENT_SECRET = "dev-secret-456"
# 模拟用户数据（固定测试用户）
MOCK_USER = {
    "user_id": "mock_iam_user_001",
    "username": "test_user",
    "phone": "13800138000",
    "email": "test_user@example.com"
}
# 存储临时授权码（模拟 IAM 服务端存储）
mock_auth_codes = {}
# 存储 token 信息
mock_tokens = {}

# 模拟授权页 HTML 模板
AUTH_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>模拟 IAM 登录授权页</title>
    <style>
        body {font-family: Arial; max-width: 500px; margin: 50px auto; padding: 20px;}
        .form-group {margin: 15px 0;}
        label {display: block; margin-bottom: 5px;}
        input {width: 100%; padding: 8px; box-sizing: border-box;}
        button {background: #007bff; color: white; border: none; padding: 10px 20px; cursor: pointer;}
        button:hover {background: #0056b3;}
    </style>
</head>
<body>
    <h2>模拟 IAM 登录</h2>
    <form method="get" action="/mock-iam/oauth2/authorize/callback">
        <input type="hidden" name="client_id" value="{{ client_id }}">
        <input type="hidden" name="redirect_uri" value="{{ redirect_uri }}">
        <input type="hidden" name="state" value="{{ state }}">
        
        <div class="form-group">
            <label>用户名（固定：test_user）</label>
            <input type="text" name="username" value="test_user" readonly>
        </div>
        <div class="form-group">
            <label>密码（任意输入）</label>
            <input type="password" name="password" placeholder="任意输入即可" required>
        </div>
        <button type="submit">登录并授权</button>
    </form>
</body>
</html>
"""

def authorize():
    """模拟 IAM 授权页"""
    # 获取前端传入的参数
    client_id = request.args.get("client_id")
    redirect_uri = request.args.get("redirect_uri")
    state = request.args.get("state")
    
    # 校验客户端 ID（模拟）
    if client_id != MOCK_CLIENT_ID:
        return jsonify({"error": "无效的 client_id"}), 400
    
    # 渲染模拟登录页
    return render_template_string(
        AUTH_PAGE_TEMPLATE,
        client_id=client_id,
        redirect_uri=redirect_uri,
        state=state
    )

def get_token():
    """模拟获取 token 接口"""
    # 获取请求参数
    grant_type = request.form.get("grant_type")
    client_id = request.form.get("client_id")
    client_secret = request.form.get("client_secret")
    code = request.form.get("code")
    redirect_uri = request.form.get("redirect_uri")
    
    # 校验参数
    if client_id != MOCK_CLIENT_ID or client_secret != MOCK_CLIENT_SECRET:
        return jsonify({"error": "无效的客户端密钥"}), 401
    if grant_type != "authorization_code":
        return jsonify({"error": "仅支持授权码模式"}), 400
    if code not in mock_auth_codes:
        return jsonify({"error": "无效的授权码"}), 400
    
    # 生成模拟 token
    access_token = f"mock_access_token_{uuid.uuid4()}"
    refresh_token = f"mock_refresh_token_{uuid.uuid4()}"
    expires_in = 3600
    
    # 存储 token（模拟）
    mock_tokens[access_token] = {
        "user_id": MOCK_USER["user_id"],
        "expires_at": time.time() + expires_in
    }
    
    # 删除已使用的授权码
    del mock_auth_codes[code]
    
    # 返回 token 信息
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": expires_in
    })

def get_user_info():
    """模拟获取用户信息接口"""
    # 从请求头获取 token
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "未提供 token"}), 401
    
    access_token = auth_header.split(" ")[1]
    # 校验 token
    if access_token not in mock_tokens:
        return jsonify({"error": "无效的 token"}), 401
    
    # 返回模拟用户信息
    return jsonify(MOCK_USER)

@mock_iam_bp.route("/oauth2/authorize/callback")
def authorize_callback():
    """模拟登录授权回调（生成授权码）"""
    # 获取表单参数
    client_id = request.args.get("client_id")
    redirect_uri = request.args.get("redirect_uri")
    state = request.args.get("state")
    username = request.args.get("username")
    password = request.args.get("password")  # 密码不校验，任意输入即可
    
    # 生成授权码
    auth_code = f"mock_auth_code_{uuid.uuid4()}"
    # 存储授权码（模拟 IAM 服务端记录）
    mock_auth_codes[auth_code] = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "user_id": MOCK_USER["user_id"]
    }
    
    # 跳转回应用的回调地址（带授权码）
    callback_url = f"{redirect_uri}?code={auth_code}&state={state}"
    return redirect(callback_url)