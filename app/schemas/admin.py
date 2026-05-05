from __future__ import annotations

from pydantic import BaseModel, Field


class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=100)
    role: str = Field(default="user", pattern="^(admin|user)$")
    display_name: str = Field(default="")


class UserUpdateRequest(BaseModel):
    role: str | None = Field(default=None, pattern="^(admin|user)$")
    display_name: str | None = None
    status: str | None = Field(default=None, pattern="^(active|disabled)$")
    password: str | None = Field(default=None, min_length=1, max_length=100)


class UserResponse(BaseModel):
    id: str
    username: str
    role: str
    display_name: str
    status: str
    created_at: str
    updated_at: str