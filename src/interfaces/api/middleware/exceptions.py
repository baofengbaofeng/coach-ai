"""
中间件异常类
"""

from tornado.web import HTTPError


class AuthenticationError(HTTPError):
    """认证错误"""
    
    def __init__(self, message: str, error_code: str = "AUTH_ERROR", status_code: int = 401):
        super().__init__(status_code, message)
        self.error_code = error_code
        self.reason = message


class AuthorizationError(HTTPError):
    """授权错误"""
    
    def __init__(self, message: str, error_code: str = "AUTHZ_ERROR", status_code: int = 403):
        super().__init__(status_code, message)
        self.error_code = error_code
        self.reason = message


class ValidationError(HTTPError):
    """验证错误"""
    
    def __init__(self, message: str, error_code: str = "VALIDATION_ERROR", status_code: int = 400):
        super().__init__(status_code, message)
        self.error_code = error_code
        self.reason = message


class RateLimitError(HTTPError):
    """速率限制错误"""
    
    def __init__(self, message: str = "Rate limit exceeded", error_code: str = "RATE_LIMIT", status_code: int = 429):
        super().__init__(status_code, message)
        self.error_code = error_code
        self.reason = message


class MaintenanceError(HTTPError):
    """维护错误"""
    
    def __init__(self, message: str = "Service under maintenance", error_code: str = "MAINTENANCE", status_code: int = 503):
        super().__init__(status_code, message)
        self.error_code = error_code
        self.reason = message