# app/models/team.py
import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions.db import Base

class Team(Base):
    """团队表（隶属于租户）"""
    __tablename__ = "team"

    # 核心字段
    id = Column(String(64), primary_key=True, comment="团队ID")
    name = Column(String(128), nullable=False, comment="团队名称")
    tenant_id = Column(
        String(64),
        ForeignKey("tenant.id"),
        nullable=False,
        comment="所属租户ID（外键关联租户表）"
    )
    description = Column(String(512), nullable=True, comment="团队描述")
    is_active = Column(Boolean, default=True, comment="是否启用")
    create_time = Column(DateTime, default=datetime.datetime.now, comment="创建时间")
    update_time = Column(
        DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        comment="更新时间"
    )

    # 关联关系：团队 -> 租户（反向关联：租户 -> 团队列表）
    tenant = relationship("Tenant", backref="teams")

    def __repr__(self):
        return f"<Team(name='{self.name}', tenant_id='{self.tenant_id}')>"