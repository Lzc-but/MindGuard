from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user, require_admin
from app.schemas.admin import UserCreateRequest, UserResponse, UserUpdateRequest
from app.services.user import create_user, delete_user, list_users, update_user

router = APIRouter(prefix="/api/admin/users", tags=["admin-users"])

# 所有管理接口统一要求 admin 角色
_require_admin = Annotated[None, Depends(require_admin)]


@router.get("", response_model=list[UserResponse])
async def get_users(_: _require_admin) -> list[UserResponse]:
    """列出所有用户"""
    rows = list_users()
    return [UserResponse(**row) for row in rows]


@router.post("", response_model=UserResponse)
async def create_new_user(
    payload: UserCreateRequest,
    _: _require_admin,
) -> UserResponse:
    """新增用户"""
    try:
        user = create_user(
            username=payload.username,
            password=payload.password,
            role=payload.role,
            display_name=payload.display_name or "",
        )
        return UserResponse(**user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{user_id}", response_model=UserResponse)
async def update_existing_user(
    user_id: str,
    payload: UserUpdateRequest,
    _: _require_admin,
) -> UserResponse:
    """更新用户（角色、显示名、状态、密码均可选）"""
    try:
        user = update_user(
            user_id,
            role=payload.role,
            display_name=payload.display_name,
            status=payload.status,
            password=payload.password,
        )
        return UserResponse(**user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}")
async def remove_user(
    user_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    _: _require_admin,
) -> dict:
    """删除用户（禁止删除自己）"""
    if user_id == _get_current_user_id(current_user):
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    try:
        delete_user(user_id)
        return {"message": "deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: Annotated[dict, Depends(get_current_user)],
) -> UserResponse:
    """获取当前登录用户详情"""
    from app.services.user import get_user_by_username

    user = get_user_by_username(current_user["username"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**user)


def _get_current_user_id(current_user: dict) -> str:
    from app.services.user import get_user_by_username

    user = get_user_by_username(current_user["username"])
    return user["id"] if user else ""