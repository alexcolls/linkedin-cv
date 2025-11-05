"""Rate limiting for protection against abuse."""
import time
from collections import deque
from threading import Lock
from typing import Dict, Optional


class RateLimiter:
    """Token bucket rate limiter for request throttling."""

    def __init__(self, requests_per_minute: int = 10, burst_size: Optional[int] = None):
        """Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests allowed per minute
            burst_size: Maximum burst size (defaults to requests_per_minute)
        """
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size or requests_per_minute
        self.tokens = self.burst_size
        self.last_update = time.time()
        self.lock = Lock()

        # Calculate refill rate (tokens per second)
        self.refill_rate = requests_per_minute / 60.0

    def allow_request(self) -> bool:
        """Check if request is allowed under rate limit.

        Returns:
            True if request is allowed, False if rate limited
        """
        with self.lock:
            now = time.time()
            
            # Refill tokens based on time passed
            time_passed = now - self.last_update
            self.tokens = min(
                self.burst_size,
                self.tokens + (time_passed * self.refill_rate)
            )
            self.last_update = now

            # Check if we have tokens available
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return True
            
            return False

    def get_wait_time(self) -> float:
        """Get seconds to wait before next request is allowed.

        Returns:
            Seconds to wait (0 if request would be allowed now)
        """
        with self.lock:
            if self.tokens >= 1.0:
                return 0.0
            
            # Calculate time needed to accumulate 1 token
            tokens_needed = 1.0 - self.tokens
            return tokens_needed / self.refill_rate

    def reset(self):
        """Reset rate limiter to initial state."""
        with self.lock:
            self.tokens = self.burst_size
            self.last_update = time.time()


class SlidingWindowRateLimiter:
    """Sliding window rate limiter with more accurate tracking."""

    def __init__(self, requests_per_minute: int = 10, window_size_seconds: int = 60):
        """Initialize sliding window rate limiter.

        Args:
            requests_per_minute: Maximum requests allowed per minute
            window_size_seconds: Size of sliding window in seconds
        """
        self.requests_per_minute = requests_per_minute
        self.window_size = window_size_seconds
        self.requests: deque = deque()
        self.lock = Lock()

    def allow_request(self, identifier: str = "default") -> bool:
        """Check if request is allowed under rate limit.

        Args:
            identifier: Unique identifier for tracking (e.g., IP address, user ID)

        Returns:
            True if request is allowed, False if rate limited
        """
        with self.lock:
            now = time.time()
            
            # Remove old requests outside the window
            cutoff = now - self.window_size
            while self.requests and self.requests[0][0] < cutoff:
                self.requests.popleft()

            # Check if under limit
            if len(self.requests) < self.requests_per_minute:
                self.requests.append((now, identifier))
                return True
            
            return False

    def get_request_count(self) -> int:
        """Get current number of requests in the window.

        Returns:
            Number of requests in current window
        """
        with self.lock:
            now = time.time()
            cutoff = now - self.window_size
            
            # Remove old requests
            while self.requests and self.requests[0][0] < cutoff:
                self.requests.popleft()
            
            return len(self.requests)

    def get_wait_time(self) -> float:
        """Get seconds to wait before next request is allowed.

        Returns:
            Seconds to wait (0 if request would be allowed now)
        """
        with self.lock:
            if len(self.requests) < self.requests_per_minute:
                return 0.0
            
            # Wait until oldest request falls out of window
            oldest = self.requests[0][0]
            now = time.time()
            wait_until = oldest + self.window_size
            return max(0.0, wait_until - now)

    def reset(self):
        """Reset rate limiter by clearing all tracked requests."""
        with self.lock:
            self.requests.clear()


class MultiKeyRateLimiter:
    """Rate limiter that tracks multiple keys independently."""

    def __init__(self, requests_per_minute: int = 10):
        """Initialize multi-key rate limiter.

        Args:
            requests_per_minute: Maximum requests per key per minute
        """
        self.requests_per_minute = requests_per_minute
        self.limiters: Dict[str, SlidingWindowRateLimiter] = {}
        self.lock = Lock()

    def allow_request(self, key: str) -> bool:
        """Check if request is allowed for specific key.

        Args:
            key: Unique key to rate limit (e.g., IP address, user ID)

        Returns:
            True if request is allowed, False if rate limited
        """
        with self.lock:
            if key not in self.limiters:
                self.limiters[key] = SlidingWindowRateLimiter(
                    requests_per_minute=self.requests_per_minute
                )
        
        return self.limiters[key].allow_request(key)

    def get_wait_time(self, key: str) -> float:
        """Get wait time for specific key.

        Args:
            key: Unique key to check

        Returns:
            Seconds to wait
        """
        with self.lock:
            if key not in self.limiters:
                return 0.0
        
        return self.limiters[key].get_wait_time()

    def get_request_count(self, key: str) -> int:
        """Get request count for specific key.

        Args:
            key: Unique key to check

        Returns:
            Number of requests in current window
        """
        with self.lock:
            if key not in self.limiters:
                return 0
        
        return self.limiters[key].get_request_count()

    def reset(self, key: Optional[str] = None):
        """Reset rate limiter for specific key or all keys.

        Args:
            key: Specific key to reset, or None to reset all
        """
        with self.lock:
            if key:
                if key in self.limiters:
                    self.limiters[key].reset()
            else:
                self.limiters.clear()

    def cleanup_old_limiters(self, inactive_seconds: int = 3600):
        """Remove limiters that haven't been used recently.

        Args:
            inactive_seconds: Seconds of inactivity before removal
        """
        with self.lock:
            now = time.time()
            keys_to_remove = []
            
            for key, limiter in self.limiters.items():
                if limiter.get_request_count() == 0:
                    # Check if last request was long ago
                    if limiter.requests and (now - limiter.requests[-1][0]) > inactive_seconds:
                        keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.limiters[key]


# Global rate limiters for application use
_global_rate_limiter = RateLimiter(requests_per_minute=10)
_multi_key_limiter = MultiKeyRateLimiter(requests_per_minute=10)


def check_rate_limit(key: Optional[str] = None) -> bool:
    """Check if request is allowed under rate limit.

    Args:
        key: Optional key for multi-key rate limiting

    Returns:
        True if allowed, False if rate limited
    """
    if key:
        return _multi_key_limiter.allow_request(key)
    return _global_rate_limiter.allow_request()


def get_wait_time(key: Optional[str] = None) -> float:
    """Get wait time before next request is allowed.

    Args:
        key: Optional key for multi-key rate limiting

    Returns:
        Seconds to wait
    """
    if key:
        return _multi_key_limiter.get_wait_time(key)
    return _global_rate_limiter.get_wait_time()


def reset_rate_limit(key: Optional[str] = None):
    """Reset rate limiter.

    Args:
        key: Optional key for multi-key rate limiting
    """
    if key:
        _multi_key_limiter.reset(key)
    else:
        _global_rate_limiter.reset()
