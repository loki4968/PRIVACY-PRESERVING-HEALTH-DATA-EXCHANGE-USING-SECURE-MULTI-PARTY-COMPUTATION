import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app, requests_per_minute: int = 180, requests_per_hour: int = 3000):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_requests: Dict[str, List[float]] = {}
        self.hour_requests: Dict[str, List[float]] = {}
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if client is rate limited"""
        current_time = time.time()
        
        # Clean old entries
        self._cleanup_old_entries(client_ip, current_time)
        
        # Check minute limit
        if len(self.minute_requests.get(client_ip, [])) >= self.requests_per_minute:
            return True
        
        # Check hour limit
        if len(self.hour_requests.get(client_ip, [])) >= self.requests_per_hour:
            return True
        
        return False
    
    def _cleanup_old_entries(self, client_ip: str, current_time: float):
        """Clean up old rate limit entries"""
        # Clean minute requests (older than 60 seconds)
        if client_ip in self.minute_requests:
            self.minute_requests[client_ip] = [
                req_time for req_time in self.minute_requests[client_ip]
                if current_time - req_time < 60
            ]
        
        # Clean hour requests (older than 3600 seconds)
        if client_ip in self.hour_requests:
            self.hour_requests[client_ip] = [
                req_time for req_time in self.hour_requests[client_ip]
                if current_time - req_time < 3600
            ]
    
    def _add_request(self, client_ip: str):
        """Add request to rate limit tracking"""
        current_time = time.time()
        
        if client_ip not in self.minute_requests:
            self.minute_requests[client_ip] = []
        if client_ip not in self.hour_requests:
            self.hour_requests[client_ip] = []
        
        self.minute_requests[client_ip].append(current_time)
        self.hour_requests[client_ip].append(current_time)
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_ip = self._get_client_ip(request)
        
        # Skip rate limiting for health checks, static files, and secure computation endpoints
        if request.url.path in ["/health", "/docs", "/openapi.json"] or request.url.path.startswith("/static") or request.url.path.startswith("/secure-computations/"):
            return await call_next(request)
        
        # Check rate limit
        if self._is_rate_limited(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please try again later.",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
            )
        
        # Add request to tracking
        self._add_request(client_ip)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Minute"] = str(
            self.requests_per_minute - len(self.minute_requests.get(client_ip, []))
        )
        response.headers["X-RateLimit-Remaining-Hour"] = str(
            self.requests_per_hour - len(self.hour_requests.get(client_ip, []))
        )
        
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Security headers middleware"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Request logging middleware"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        
        # Skip logging for WebSocket ping messages
        is_websocket = request.url.path.startswith("/ws/")
        
        # Log request (except for WebSocket ping messages)
        if not is_websocket:
            logger.info(f"Request: {request.method} {request.url.path} from {request.client.host}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response (except for WebSocket ping messages)
        if not is_websocket:
            logger.info(
                f"Response: {request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )
        
        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

class CORSMiddleware(BaseHTTPMiddleware):
    """Enhanced CORS middleware"""
    
    def __init__(self, app, allowed_origins: List[str] = None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["http://localhost:3000"]
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Handle preflight OPTIONS requests
        if request.method == "OPTIONS":
            response = JSONResponse(content={"message": "OK"})
        else:
            response = await call_next(request)
        
        origin = request.headers.get("origin")
        if origin in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, X-Force-Upload"
            response.headers["Access-Control-Max-Age"] = "86400"  # 24 hours
        
        return response
