from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.security import (
    authenticate_user,
    create_access_token,
    get_current_user,
)
from app.schemas.user import TokenResponse, UserInfo

router = APIRouter(prefix="/api/auth", tags=["auth"])

# 登录接口：接收用户名密码，验证后返回JWT令牌
@router.post("/login", response_model=TokenResponse)
async def login(
    # 接收前端表单提交的用户名、密码
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
    ) -> TokenResponse:

    # 1.调用认证函数，校验用户名和密码是否正确
    user = authenticate_user(form_data.username, form_data.password)

    # 2.如果用户不存在/密码错误，抛出401未授权异常
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    # 3.认证成功->生成JWT访问令牌
    token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return TokenResponse(access_token=token)

# 获取【当前已登录】的用户信息接口
# 必须登录、有合法Token才能访问
@router.get("/me", response_model=UserInfo)
async def me(
    # Depends(get_current_user) = 自动校验Token
    # 校验通过后，把当前用户信息直接注入到 current_user 变量
    current_user: Annotated[dict, Depends(get_current_user)]
    ) -> UserInfo:

    # 把用户信息返回给前端（格式化为 UserInfo 结构）
    return UserInfo(**current_user)
