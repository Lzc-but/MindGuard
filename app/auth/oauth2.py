# app/auth/oauth2.py
import urllib.parse
import requests
import logging
from flask import redirect, request, session, current_app
from app.utils.config import get_oauth2_config
from app.auth.exceptions import OAuth2Error

# 初始化日志
logger = logging.getLogger(__name__)

# OAuth2 配置缓存（避免重复读取）
_oauth2_config = None

def get_oauth2_conf():
    """获取 OAuth2 配置"""
    global _oauth2_config
    if not _oauth2_config:
        _oauth2_config = get_oauth2_config()
        # 校验必填配置
        required_keys = ["client_id", "client_secret", "authorize_url", "token_url", "redirect_uri"]
        missing = [k for k in required_keys if not _oauth2_config.get(k)]
        if missing:
            raise OAuth2Error(f"OAuth2 配置缺失：{missing}")
    return _oauth2_config

def authorize():
    """
    跳转 IAM 授权页（第一步：获取授权码）
    路由：/auth/authorize
    """
    try:
        conf = get_oauth2_conf()
        # 构建授权页 URL
        params = {
            "response_type": "code",  # 授权码模式固定值
            "client_id": conf["client_id"],
            "redirect_uri": conf["redirect_uri"],
            "scope": "openid profile phone email",  # 申请的权限范围（根据 IAM 要求调整）
            "state": "random_state_123"  # 防 CSRF，生产环境建议随机生成
        }
        authorize_url = f"{conf['authorize_url']}?{urllib.parse.urlencode(params)}"
        logger.info(f"跳转 IAM 授权页：{authorize_url}")
        return redirect(authorize_url)
    except OAuth2Error as e:
        logger.error(f"授权页跳转失败：{e.message}")
        return {"error": e.message}, e.code
    except Exception as e:
        logger.error(f"授权页跳转异常：{str(e)}")
        return {"error": "授权页跳转失败"}, 500

def callback():
    """
    授权码回调（第二步：换取 token + 解析用户信息）
    路由：/auth/callback
    """
    try:
        # 1. 获取回调参数
        code = request.args.get("code")
        state = request.args.get("state")
        error = request.args.get("error")
        
        if error:
            raise OAuth2Error(f"IAM 授权失败：{error}")
        if not code:
            raise OAuth2Error("未获取到授权码")
        if state != "random_state_123":  # 校验 state，防 CSRF
            raise OAuth2Error("State 校验失败，可能是 CSRF 攻击")
        
        # 2. 换取 access_token
        conf = get_oauth2_conf()
        token_params = {
            "grant_type": "authorization_code",
            "client_id": conf["client_id"],
            "client_secret": conf["client_secret"],
            "code": code,
            "redirect_uri": conf["redirect_uri"]
        }
        logger.info(f"换取 token 请求：{conf['token_url']}，参数：{token_params}")
        token_response = requests.post(
            conf["token_url"],
            data=token_params,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        token_response.raise_for_status()  # 抛出 HTTP 错误
        token_data = token_response.json()
        
        if "access_token" not in token_data:
            raise OAuth2Error(f"换取 token 失败：{token_data}")
        
        # 3. 解析用户信息
        access_token = token_data["access_token"]
        user_info = get_user_info_from_iam(access_token)
        logger.info(f"从 IAM 获取用户信息：{user_info}")
        
        # 4. 存储 token 和用户信息到会话
        session["access_token"] = access_token
        session["iam_user_id"] = user_info.get("user_id")  # IAM 唯一用户 ID
        session["username"] = user_info.get("username")
        session["is_login"] = True
        
        # 5. 交给 SSO 处理（首次登录分配租户 + 创建用户）
        from app.auth.sso import handle_first_login
        handle_first_login(user_info)
        
        # 6. 跳转至首页（或业务页面）
        return redirect("/auth/user/info")  # 测试跳转至用户信息页
    
    except OAuth2Error as e:
        logger.error(f"授权回调失败：{e.message}")
        return {"error": e.message}, e.code
    except requests.exceptions.RequestException as e:
        logger.error(f"IAM 接口请求失败：{str(e)}")
        return {"error": "IAM 服务不可用"}, 500
    except Exception as e:
        logger.error(f"授权回调异常：{str(e)}")
        return {"error": "授权回调处理失败"}, 500

def get_user_info_from_iam(access_token):
    """
    从 IAM 获取用户信息（第三步：解析用户信息）
    :param access_token: 访问令牌
    :return: 用户信息字典
    """
    conf = get_oauth2_conf()
    user_info_url = f"{conf['oauth2_iam_domain']}{conf['user_info_path']}"  # 完整用户信息接口 URL
    headers = {"Authorization": f"Bearer {access_token}"}
    
    logger.info(f"获取用户信息请求：{user_info_url}")
    response = requests.get(user_info_url, headers=headers, timeout=10)
    response.raise_for_status()
    user_info = response.json()
    
    # 校验必要字段
    required_fields = ["user_id", "username"]
    missing = [f for f in required_fields if not user_info.get(f)]
    if missing:
        raise OAuth2Error(f"IAM 返回用户信息缺失字段：{missing}")
    
    return user_info