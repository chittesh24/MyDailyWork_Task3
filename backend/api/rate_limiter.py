"""
Rate limiting implementation.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict
import threading


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        """
        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[int, list] = defaultdict(list)
        self.lock = threading.Lock()
    
    def allow_request(self, user_id: int) -> bool:
        """
        Check if request is allowed for user.
        
        Args:
            user_id: User ID
            
        Returns:
            allowed: True if request allowed, False otherwise
        """
        with self.lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(seconds=self.window_seconds)
            
            # Remove old requests
            self.requests[user_id] = [
                req_time for req_time in self.requests[user_id]
                if req_time > cutoff
            ]
            
            # Check limit
            if len(self.requests[user_id]) >= self.max_requests:
                return False
            
            # Add new request
            self.requests[user_id].append(now)
            return True
    
    def get_remaining(self, user_id: int) -> int:
        """Get remaining requests for user."""
        with self.lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(seconds=self.window_seconds)
            
            # Remove old requests
            self.requests[user_id] = [
                req_time for req_time in self.requests[user_id]
                if req_time > cutoff
            ]
            
            return max(0, self.max_requests - len(self.requests[user_id]))
