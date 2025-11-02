"""
Custom exceptions for the application.
"""
from typing import Any, Optional


class BaseAppException(Exception):
    """Base exception for all application exceptions."""

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = 500,
        details: Optional[Any] = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class NotFoundException(BaseAppException):
    """Exception raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found", details: Optional[Any] = None) -> None:
        super().__init__(message=message, status_code=404, details=details)


class UnauthorizedException(BaseAppException):
    """Exception raised for authentication failures."""

    def __init__(self, message: str = "Unauthorized", details: Optional[Any] = None) -> None:
        super().__init__(message=message, status_code=401, details=details)


class ForbiddenException(BaseAppException):
    """Exception raised for authorization failures."""

    def __init__(self, message: str = "Forbidden", details: Optional[Any] = None) -> None:
        super().__init__(message=message, status_code=403, details=details)


class BadRequestException(BaseAppException):
    """Exception raised for bad requests."""

    def __init__(self, message: str = "Bad request", details: Optional[Any] = None) -> None:
        super().__init__(message=message, status_code=400, details=details)


class ConflictException(BaseAppException):
    """Exception raised for resource conflicts."""

    def __init__(self, message: str = "Resource conflict", details: Optional[Any] = None) -> None:
        super().__init__(message=message, status_code=409, details=details)


class ValidationException(BaseAppException):
    """Exception raised for validation errors."""

    def __init__(self, message: str = "Validation error", details: Optional[Any] = None) -> None:
        super().__init__(message=message, status_code=422, details=details)


class InternalServerException(BaseAppException):
    """Exception raised for internal server errors."""

    def __init__(
        self, message: str = "Internal server error", details: Optional[Any] = None
    ) -> None:
        super().__init__(message=message, status_code=500, details=details)


class ServiceUnavailableException(BaseAppException):
    """Exception raised when a service is unavailable."""

    def __init__(
        self, message: str = "Service unavailable", details: Optional[Any] = None
    ) -> None:
        super().__init__(message=message, status_code=503, details=details)
