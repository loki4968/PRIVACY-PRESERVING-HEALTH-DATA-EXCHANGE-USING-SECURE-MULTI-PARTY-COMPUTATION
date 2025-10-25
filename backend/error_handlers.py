import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class AppError(Exception):
    """Base application error class"""
    def __init__(self, message: str, error_code: str = None, status_code: int = 500, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(AppError):
    """Validation error"""
    def __init__(self, message: str, field: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "VALIDATION_ERROR", 400, details)
        self.field = field

class AuthenticationError(AppError):
    """Authentication error"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTH_ERROR", 401)

class AuthorizationError(AppError):
    """Authorization error"""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, "AUTHZ_ERROR", 403)

class NotFoundError(AppError):
    """Resource not found error"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, "NOT_FOUND", 404)

class ConflictError(AppError):
    """Resource conflict error"""
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, "CONFLICT", 409)

class RateLimitError(AppError):
    """Rate limit error"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, "RATE_LIMIT", 429)

def log_error(error: Exception, request: Request = None, user_id: Optional[int] = None):
    """Log error with context"""
    error_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc(),
        "user_id": user_id,
        "request_path": request.url.path if request else None,
        "request_method": request.method if request else None,
        "client_ip": request.client.host if request else None,
        "user_agent": request.headers.get("user-agent") if request else None
    }
    
    logger.error(f"Application Error: {json.dumps(error_data, indent=2)}")
    return error_data

def create_error_response(error: AppError, request: Request = None, include_details: bool = False) -> JSONResponse:
    """Create standardized error response"""
    error_data = {
        "error": {
            "code": error.error_code,
            "message": error.message,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path if request else None
        }
    }
    
    if include_details and error.details:
        error_data["error"]["details"] = error.details
    
    # Log the error
    log_error(error, request)
    
    return JSONResponse(
        status_code=error.status_code,
        content=error_data
    )

async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    error_details = []
    for error in exc.errors():
        error_details.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    error = ValidationError(
        message="Validation failed",
        details={"validation_errors": error_details}
    )
    
    return create_error_response(error, request, include_details=True)

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    error = AppError(
        message=exc.detail,
        error_code="HTTP_ERROR",
        status_code=exc.status_code
    )
    
    return create_error_response(error, request)

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    # Don't expose internal errors in production
    include_details = False  # Set to True for development
    
    error = AppError(
        message="Internal server error" if not include_details else str(exc),
        error_code="INTERNAL_ERROR",
        status_code=500,
        details={"exception_type": type(exc).__name__} if include_details else None
    )
    
    return create_error_response(error, request, include_details)

def setup_error_handlers(app):
    """Setup error handlers for the FastAPI app"""
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Error handlers configured successfully")

# Utility functions for common error scenarios
def raise_validation_error(message: str, field: str = None):
    """Raise a validation error"""
    raise ValidationError(message, field)

def raise_not_found_error(message: str = "Resource not found"):
    """Raise a not found error"""
    raise NotFoundError(message)

def raise_authentication_error(message: str = "Authentication failed"):
    """Raise an authentication error"""
    raise AuthenticationError(message)

def raise_authorization_error(message: str = "Insufficient permissions"):
    """Raise an authorization error"""
    raise AuthorizationError(message)

def raise_conflict_error(message: str = "Resource conflict"):
    """Raise a conflict error"""
    raise ConflictError(message)
