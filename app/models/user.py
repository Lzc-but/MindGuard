# app/models/user.py
import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions.db import Base
from app.models.team import Team
from app.models.user_team_rel import user_team_rel

class User(Base):
    """用户表（关联租户，支持SSO）"""
    __tablename__ = "user"

    # 核心字段
    id = Column(String(64), primary_key=True, comment="用户ID（系统内唯一）")
    username = Column(String(64), unique=True, nullable=False, comment="用户名（登录名）")
    phone = Column(String(20), unique=True, nullable=True, comment="手机号")
    email = Column(String(128), unique=True, nullable=True, comment="邮箱")
    iam_user_id = Column(String(64), unique=True, nullable=False, comment="IAM系统用户ID（SSO关联）")
    tenant_id = Column(
        String(64),
        ForeignKey("tenant.id"),
        nullable=False,
        comment="所属租户ID（外键关联租户表）"
    )
    is_first_login = Column(Boolean, default=True, comment="是否首次登录（用于自动分配租户）")
    is_active = Column(Boolean, default=True, comment="是否启用")
    create_time = Column(DateTime, default=datetime.datetime.now, comment="创建时间")
    update_time = Column(
        DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        comment="更新时间"
    )

    # 关联关系
    # 1. 一对一：用户 -> 租户（反向关联：租户 -> 用户列表）
    tenant = relationship("Tenant", backref="users")
    # 2. 多对多：用户 <-> 团队（通过中间表 user_team_rel）
    teams = relationship(
        "Team",
        secondary=user_team_rel,
        backref="users",
        lazy="dynamic"  # 动态加载，提升查询性能
    )

    def __repr__(self):
        return f"<User(username='{self.username}', iam_user_id='{self.iam_user_id}', tenant_id='{self.tenant_id}')>"