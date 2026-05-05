"""用户管理服务：SQLite 持久化存储 + CRUD"""

import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Optional

from passlib.context import CryptContext

from app.core.config import settings

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---- 预置的默认账户（仅首次初始化时写入） ----
SEED_USERS = [
    {
        "username": settings.admin_username,
        "password": settings.admin_password,
        "role": "admin",
        "display_name": "管理员",
        "status": "active",
    },
    {
        "username": "user",
        "password": "user123",
        "role": "user",
        "display_name": "普通用户",
        "status": "active",
    },
]

ROLE_ORDER = {"admin": 100, "user": 10}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.sqlite_path)
    conn.row_factory = sqlite3.Row
    return conn


# ========== 初始化 ==========

def init_users_db() -> None:
    """创建 users 表并写入预置账户（幂等）"""
    conn = _connect()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                display_name TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'active',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()

        for seed in SEED_USERS:
            existing = conn.execute(
                "SELECT id FROM users WHERE username = ?", (seed["username"],)
            ).fetchone()
            if existing:
                continue
            now = _utc_now()
            conn.execute(
                """INSERT INTO users (id, username, password_hash, role, display_name, status, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    str(uuid.uuid4()),
                    seed["username"],
                    pwd_context.hash(seed["password"]),
                    seed["role"],
                    seed["display_name"],
                    seed["status"],
                    now,
                    now,
                ),
            )
        conn.commit()
        logger.info("Users table initialized successfully")
    finally:
        conn.close()


# ========== 认证查询 ==========

def get_user_by_username(username: str) -> Optional[dict]:
    """按用户名查询（用于登录）"""
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ? AND status = 'active'",
            (username,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def verify_user_password(username: str, plain_password: str) -> Optional[dict]:
    """校验密码，通过后返回用户信息（不含密码哈希）"""
    user = get_user_by_username(username)
    if not user:
        return None
    if not pwd_context.verify(plain_password, user["password_hash"]):
        return None
    return {
        "username": user["username"],
        "role": user["role"],
        "display_name": user["display_name"],
    }


# ========== 管理 CRUD ==========

def list_users() -> list[dict]:
    """列出所有用户"""
    conn = _connect()
    try:
        rows = conn.execute(
            """SELECT id, username, role, display_name, status, created_at, updated_at
               FROM users
               ORDER BY
                   CASE role
                       WHEN 'admin' THEN 1
                       WHEN 'user' THEN 2
                       ELSE 3
                   END,
                   created_at ASC"""
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def create_user(
    username: str,
    password: str,
    role: str = "user",
    display_name: str = "",
) -> dict:
    """新增用户"""
    if role not in ("admin", "user"):
        raise ValueError("role must be 'admin' or 'user'")
    conn = _connect()
    try:
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()
        if existing:
            raise ValueError(f"Username '{username}' already exists")

        now = _utc_now()
        uid = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO users (id, username, password_hash, role, display_name, status, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, 'active', ?, ?)""",
            (uid, username, pwd_context.hash(password), role, display_name or username, now, now),
        )
        conn.commit()
        logger.info("User created: %s (role=%s)", username, role)
        return {
            "id": uid,
            "username": username,
            "role": role,
            "display_name": display_name or username,
            "status": "active",
            "created_at": now,
            "updated_at": now,
        }
    finally:
        conn.close()


def update_user(
    user_id: str,
    *,
    role: Optional[str] = None,
    display_name: Optional[str] = None,
    status: Optional[str] = None,
    password: Optional[str] = None,
) -> dict:
    """更新用户信息（角色、显示名、状态、密码）"""
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if not row:
            raise ValueError("User not found")

        now = _utc_now()
        updates = []
        params = []

        if role is not None:
            if role not in ("admin", "user"):
                raise ValueError("role must be 'admin' or 'user'")
            updates.append("role = ?")
            params.append(role)
        if display_name is not None:
            updates.append("display_name = ?")
            params.append(display_name.strip() or row["username"])
        if status is not None:
            if status not in ("active", "disabled"):
                raise ValueError("status must be 'active' or 'disabled'")
            updates.append("status = ?")
            params.append(status)
        if password is not None:
            updates.append("password_hash = ?")
            params.append(pwd_context.hash(password))

        if not updates:
            return dict(row)

        updates.append("updated_at = ?")
        params.append(now)
        params.append(user_id)

        conn.execute(
            f"UPDATE users SET {', '.join(updates)} WHERE id = ?",
            params,
        )
        conn.commit()
        logger.info("User updated: %s", row["username"])
        return dict(conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone())
    finally:
        conn.close()


def delete_user(user_id: str) -> None:
    """删除用户（禁止删除自己）"""
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT username FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if not row:
            raise ValueError("User not found")
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        logger.info("User deleted: %s", row["username"])
    finally:
        conn.close()