# app/auth/exceptions.py
class AuthError(Exception):
    """认证基类异常"""
    def __init__(self, message, code=401):
        self.message = message
        self.code = code
        super().__init__(self.message)

class OAuth2Error(AuthError):
    """OAuth2 流程异常"""
    pass

class UserNotFoundError(AuthError):
    """用户未找到异常"""
    pass

class TenantAssignError(AuthError):
    """租户分配异常"""
    pass