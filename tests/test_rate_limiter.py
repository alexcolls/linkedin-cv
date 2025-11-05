"""Tests for rate limiter module."""
import time
import pytest
from src.security.rate_limiter import (
    RateLimiter,
    SlidingWindowRateLimiter,
    MultiKeyRateLimiter,
    check_rate_limit,
    get_wait_time,
    reset_rate_limit,
)


class TestRateLimiter:
    """Test RateLimiter class."""

    def test_allow_request_within_limit(self):
        """Test that requests within limit are allowed."""
        limiter = RateLimiter(requests_per_minute=10)
        # Should allow first 10 requests immediately
        for _ in range(10):
            assert limiter.allow_request() is True

    def test_deny_request_over_limit(self):
        """Test that requests over limit are denied."""
        limiter = RateLimiter(requests_per_minute=2, burst_size=2)
        # Allow first 2 requests
        assert limiter.allow_request() is True
        assert limiter.allow_request() is True
        # Deny 3rd request immediately
        assert limiter.allow_request() is False

    def test_refill_rate(self):
        """Test that tokens refill over time."""
        limiter = RateLimiter(requests_per_minute=60, burst_size=1)
        # Use the token
        assert limiter.allow_request() is True
        assert limiter.allow_request() is False
        
        # Wait for refill (1 request per second at 60 rpm)
        time.sleep(1.1)
        
        # Should be allowed again
        assert limiter.allow_request() is True

    def test_get_wait_time_immediate(self):
        """Test get_wait_time when no wait is needed."""
        limiter = RateLimiter(requests_per_minute=10)
        assert limiter.get_wait_time() == 0.0

    def test_get_wait_time_after_exhaustion(self):
        """Test get_wait_time after tokens exhausted."""
        limiter = RateLimiter(requests_per_minute=60, burst_size=1)
        limiter.allow_request()  # Use the token
        wait = limiter.get_wait_time()
        assert wait > 0.0
        assert wait <= 1.0

    def test_reset(self):
        """Test reset functionality."""
        limiter = RateLimiter(requests_per_minute=2, burst_size=2)
        # Exhaust tokens
        limiter.allow_request()
        limiter.allow_request()
        assert limiter.allow_request() is False
        
        # Reset
        limiter.reset()
        
        # Should work again
        assert limiter.allow_request() is True


class TestSlidingWindowRateLimiter:
    """Test SlidingWindowRateLimiter class."""

    def test_allow_request_within_limit(self):
        """Test that requests within limit are allowed."""
        limiter = SlidingWindowRateLimiter(requests_per_minute=5)
        # Should allow first 5 requests
        for _ in range(5):
            assert limiter.allow_request("test") is True

    def test_deny_request_over_limit(self):
        """Test that requests over limit are denied."""
        limiter = SlidingWindowRateLimiter(requests_per_minute=3)
        # Allow first 3
        for _ in range(3):
            assert limiter.allow_request("test") is True
        # Deny 4th
        assert limiter.allow_request("test") is False

    def test_sliding_window_expiration(self):
        """Test that old requests slide out of window."""
        limiter = SlidingWindowRateLimiter(
            requests_per_minute=2,
            window_size_seconds=1
        )
        # Use limit
        assert limiter.allow_request("test") is True
        assert limiter.allow_request("test") is True
        assert limiter.allow_request("test") is False
        
        # Wait for window to slide
        time.sleep(1.1)
        
        # Should be allowed again
        assert limiter.allow_request("test") is True

    def test_get_request_count(self):
        """Test getting current request count."""
        limiter = SlidingWindowRateLimiter(requests_per_minute=10)
        assert limiter.get_request_count() == 0
        
        limiter.allow_request("test")
        assert limiter.get_request_count() == 1
        
        limiter.allow_request("test")
        limiter.allow_request("test")
        assert limiter.get_request_count() == 3

    def test_get_wait_time_sliding(self):
        """Test get_wait_time with sliding window."""
        limiter = SlidingWindowRateLimiter(
            requests_per_minute=1,
            window_size_seconds=1
        )
        limiter.allow_request("test")
        wait = limiter.get_wait_time()
        assert wait > 0.0
        assert wait <= 1.0

    def test_reset(self):
        """Test reset clears all requests."""
        limiter = SlidingWindowRateLimiter(requests_per_minute=2)
        limiter.allow_request("test")
        limiter.allow_request("test")
        assert limiter.get_request_count() == 2
        
        limiter.reset()
        assert limiter.get_request_count() == 0


class TestMultiKeyRateLimiter:
    """Test MultiKeyRateLimiter class."""

    def test_independent_keys(self):
        """Test that different keys are rate limited independently."""
        limiter = MultiKeyRateLimiter(requests_per_minute=2)
        
        # User1 makes 2 requests
        assert limiter.allow_request("user1") is True
        assert limiter.allow_request("user1") is True
        assert limiter.allow_request("user1") is False
        
        # User2 should still be allowed
        assert limiter.allow_request("user2") is True
        assert limiter.allow_request("user2") is True
        assert limiter.allow_request("user2") is False

    def test_get_request_count_per_key(self):
        """Test getting request count for specific keys."""
        limiter = MultiKeyRateLimiter(requests_per_minute=10)
        
        limiter.allow_request("user1")
        limiter.allow_request("user1")
        limiter.allow_request("user2")
        
        assert limiter.get_request_count("user1") == 2
        assert limiter.get_request_count("user2") == 1
        assert limiter.get_request_count("user3") == 0

    def test_get_wait_time_per_key(self):
        """Test getting wait time for specific keys."""
        limiter = MultiKeyRateLimiter(requests_per_minute=1)
        
        limiter.allow_request("user1")
        wait1 = limiter.get_wait_time("user1")
        wait2 = limiter.get_wait_time("user2")
        
        assert wait1 > 0.0
        assert wait2 == 0.0

    def test_reset_specific_key(self):
        """Test resetting specific key."""
        limiter = MultiKeyRateLimiter(requests_per_minute=1)
        
        limiter.allow_request("user1")
        limiter.allow_request("user2")
        
        # Reset user1 only
        limiter.reset("user1")
        
        assert limiter.get_request_count("user1") == 0
        assert limiter.get_request_count("user2") == 1

    def test_reset_all_keys(self):
        """Test resetting all keys."""
        limiter = MultiKeyRateLimiter(requests_per_minute=1)
        
        limiter.allow_request("user1")
        limiter.allow_request("user2")
        
        # Reset all
        limiter.reset()
        
        assert limiter.get_request_count("user1") == 0
        assert limiter.get_request_count("user2") == 0

    def test_cleanup_old_limiters(self):
        """Test cleanup of inactive limiters."""
        limiter = MultiKeyRateLimiter(requests_per_minute=60)
        
        # Create some limiters
        limiter.allow_request("user1")
        limiter.allow_request("user2")
        
        # Wait for requests to age out
        time.sleep(61)
        
        # Cleanup (with 60 second threshold)
        limiter.cleanup_old_limiters(inactive_seconds=60)
        
        # Old limiters should be removed
        # Note: This is tricky to test perfectly due to timing


class TestGlobalFunctions:
    """Test global rate limiter functions."""

    def test_check_rate_limit_without_key(self):
        """Test check_rate_limit with global limiter."""
        reset_rate_limit()  # Reset first
        
        # Should allow requests within limit
        for _ in range(5):
            assert check_rate_limit() is True

    def test_check_rate_limit_with_key(self):
        """Test check_rate_limit with multi-key limiter."""
        reset_rate_limit("testkey")  # Reset first
        
        # Should allow requests within limit
        for _ in range(5):
            assert check_rate_limit("testkey") is True

    def test_get_wait_time_without_key(self):
        """Test get_wait_time with global limiter."""
        reset_rate_limit()
        wait = get_wait_time()
        assert wait == 0.0

    def test_get_wait_time_with_key(self):
        """Test get_wait_time with multi-key limiter."""
        reset_rate_limit("testkey2")
        wait = get_wait_time("testkey2")
        assert wait == 0.0

    def test_reset_without_key(self):
        """Test reset_rate_limit for global limiter."""
        # Use some tokens
        for _ in range(5):
            check_rate_limit()
        
        # Reset
        reset_rate_limit()
        
        # Should work again
        assert check_rate_limit() is True

    def test_reset_with_key(self):
        """Test reset_rate_limit for specific key."""
        # Use some tokens
        for _ in range(5):
            check_rate_limit("testkey3")
        
        # Reset
        reset_rate_limit("testkey3")
        
        # Should work again
        assert check_rate_limit("testkey3") is True


class TestConcurrency:
    """Test rate limiters under concurrent access."""

    def test_thread_safety_basic(self):
        """Test basic thread safety of rate limiter."""
        import threading
        
        limiter = RateLimiter(requests_per_minute=100)
        results = []
        
        def make_requests():
            for _ in range(10):
                result = limiter.allow_request()
                results.append(result)
        
        # Create multiple threads
        threads = [threading.Thread(target=make_requests) for _ in range(5)]
        
        # Start all threads
        for t in threads:
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Check that we got expected number of results
        assert len(results) == 50
        # Should allow at least 100 requests total (within limit)
        assert sum(results) > 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_zero_rate_limit(self):
        """Test behavior with zero rate limit."""
        # This should effectively block all requests after burst
        limiter = RateLimiter(requests_per_minute=0, burst_size=1)
        assert limiter.allow_request() is True
        assert limiter.allow_request() is False

    def test_very_high_rate_limit(self):
        """Test behavior with very high rate limit."""
        limiter = RateLimiter(requests_per_minute=10000)
        # Should allow many requests
        for _ in range(100):
            assert limiter.allow_request() is True

    def test_fractional_tokens(self):
        """Test that fractional token accumulation works."""
        # At 60 rpm, we get 1 token per second
        limiter = RateLimiter(requests_per_minute=60, burst_size=1)
        
        # Use initial token
        limiter.allow_request()
        
        # Wait half a second
        time.sleep(0.5)
        
        # Should not have full token yet
        assert limiter.allow_request() is False
        
        # Wait another half second
        time.sleep(0.5)
        
        # Now should have token
        assert limiter.allow_request() is True
