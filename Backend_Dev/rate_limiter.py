"""
rate_limiter.py — Simple in-memory rate limiting for API endpoints
"""
import time
from collections import defaultdict
from threading import Lock
from typing import Optional
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class RateLimiter:
    """
    In-memory rate limiter using sliding window algorithm.
    For production, replace with Redis-based rate limiting.
    """
    
    def __init__(self):
        # Store: {ip: [(timestamp, count)]}
        self.requests = defaultdict(list)
        self.lock = Lock()
    
    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """
        Check if request is allowed based on rate limit.
        
        Args:
            key: Identifier (usually IP address or user ID)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        
        Returns:
            True if allowed, False if rate limited
        """
        current_time = time.time()
        window_start = current_time - window_seconds
        
        with self.lock:
            # Remove old requests outside the window
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if req_time > window_start
            ]
            
            # Check if under limit
            if len(self.requests[key]) >= max_requests:
                return False
            
            # Add current request
            self.requests[key].append(current_time)
            return True
    
    def get_remaining(self, key: str, max_requests: int, window_seconds: int) -> int:
        """Get remaining requests allowed in current window."""
        current_time = time.time()
        window_start = current_time - window_seconds
        
        with self.lock:
            recent_requests = [
                req_time for req_time in self.requests[key]
                if req_time > window_start
            ]
            return max(0, max_requests - len(recent_requests))
    
    def get_retry_after(self, key: str, window_seconds: int) -> int:
        """Get seconds until rate limit resets."""
        current_time = time.time()
        window_start = current_time - window_seconds
        
        with self.lock:
            old_requests = [
                req_time for req_time in self.requests[key]
                if req_time <= window_start
            ]
            if old_requests:
                oldest_in_window = min(self.requests[key])
                return int(oldest_in_window + window_seconds - current_time) + 1
            return 0
    
    def cleanup(self, max_age_seconds: int = 3600):
        """Remove old entries to prevent memory leak."""
        current_time = time.time()
        cutoff = current_time - max_age_seconds
        
        with self.lock:
            keys_to_delete = []
            for key in self.requests:
                self.requests[key] = [
                    req_time for req_time in self.requests[key]
                    if req_time > cutoff
                ]
                if not self.requests[key]:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self.requests[key]


# Global rate limiter instance
rate_limiter = RateLimiter()


# Rate limit configurations
RATE_LIMITS = {
    "login": {"max_requests": 5, "window": 900},      # 5 attempts per 15 minutes
    "register": {"max_requests": 3, "window": 3600},  # 3 registrations per hour
    "scan": {"max_requests": 100, "window": 3600},    # 100 scans per hour
    "history": {"max_requests": 50, "window": 3600},  # 50 history requests per hour
    "default": {"max_requests": 1000, "window": 3600} # 1000 requests per hour
}


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request."""
    # Check for forwarded headers (behind proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"


def check_rate_limit(
    request: Request,
    endpoint: str = "default",
    max_requests: Optional[int] = None,
    window_seconds: Optional[int] = None
):
    """
    FastAPI dependency to check rate limits.
    
    Usage:
        @app.post("/login")
        async def login(request: Request, _: None = Depends(lambda r: check_rate_limit(r, "login"))):
            ...
    """
    if max_requests is None or window_seconds is None:
        config = RATE_LIMITS.get(endpoint, RATE_LIMITS["default"])
        max_requests = config["max_requests"]
        window_seconds = config["window"]
    
    client_ip = get_client_ip(request)
    rate_key = f"{endpoint}:{client_ip}"
    
    if not rate_limiter.is_allowed(rate_key, max_requests, window_seconds):
        remaining = 0
        retry_after = rate_limiter.get_retry_after(rate_key, window_seconds)
        
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Please try again in {retry_after} seconds.",
                "retry_after": retry_after,
                "limit": max_requests,
                "window": f"{window_seconds} seconds"
            }
        )
    
    return True


# Cleanup old entries periodically (call this in a background task)
def cleanup_rate_limiter():
    """Clean up old rate limiter entries."""
    rate_limiter.cleanup()
