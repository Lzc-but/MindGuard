# app/models/__init__.py
from app.models.user import User
from app.models.tenant import Tenant
from app.models.team import Team
from app.models.user_team_rel import user_team_rel

# 导出所有模型类，供 Alembic 和业务代码使用
__all__ = ["User", "Tenant", "Team", "user_team_rel"]