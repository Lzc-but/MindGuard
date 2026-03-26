# app/models/user_team_rel.py
from sqlalchemy import Table, Column, String, ForeignKey
from app.extensions.db import Base

# 多对多中间表：用户-团队关系（无额外字段，纯关联）
user_team_rel = Table(
    "user_team_rel",  # 数据库表名
    Base.metadata,
    Column("user_id", String(64), ForeignKey("user.id"), primary_key=True, comment="用户ID"),
    Column("team_id", String(64), ForeignKey("team.id"), primary_key=True, comment="团队ID"),
    comment="用户-团队多对多关系表"
)