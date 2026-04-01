from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# 定义两个固定用户
FAKE_USERS = {
    settings.admin_username: {
        "username": settings.admin_username,
        "hashed_password": pwd_context.hash(settings.admin_password),
        "role": "admin",
    },
    "user": {
        "username": "user",
        "hashed_password": pwd_context.hash("user123"),
        "role": "user",
    },
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str) -> dict | None:
    """登录校验函数"""
    user = FAKE_USERS.get(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload.update({"exp": expire})
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    """获取当前登录用户的信息"""
    # 定义通用登录失败异常
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 1.用密钥解密Token,拿到里面存储的：用户名(sub)、角色(role)
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

        # 2. 从解密后的内容里取出用户名和角色
        username: str | None = payload.get("sub")
        role: str | None = payload.get("role")

        # 3. 如果缺少用户名或角色 → 判定无效
        if username is None or role is None:
            raise credentials_exception
        
    # 4. 如果 Token 过期、伪造、格式错误 → 全部判定无效
    except JWTError as exc:
        raise credentials_exception from exc
    
    # 5. 检查用户是否真实存在（这里是模拟用户库）
    user = FAKE_USERS.get(username)
    if user is None:
        raise credentials_exception
    
    # 6. 全部验证通过 → 返回用户信息（用户名+角色）
    return {"username": username, "role": role}


def require_admin(current_user: Annotated[dict, Depends(get_current_user)]) -> dict:
    """判断当前用户是不是管理员"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user
