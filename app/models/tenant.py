# app/models/tenant.py
import datetime
from sqlalchemy import Column, String, DateTime, Integer, Boolean
from app.extensions.db import Base

class Tenant(Base):
    """租户表（企业/组织）"""
    __tablename__ = "tenant"  # 数据库表名

    # 核心字段
    id = Column(String(64), primary_key=True, comment="租户ID（唯一标识，如企业编码）")
    name = Column(String(128), nullable=False, comment="租户名称（企业/组织名称）")
    description = Column(String(512), nullable=True, comment="租户描述")
    is_active = Column(Boolean, default=True, comment="是否启用")
    create_time = Column(DateTime, default=datetime.datetime.now, comment="创建时间")
    update_time = Column(
        DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        comment="更新时间"
    )

    def __repr__(self):
        return f"<Tenant(id='{self.id}', name='{self.name}')>"