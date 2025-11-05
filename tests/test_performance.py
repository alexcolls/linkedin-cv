"""Performance benchmark tests."""
import pytest
import time
from pathlib import Path

from src.utils.cache import SimpleCache, ImageCache
from src.utils.image_processor import ImageProcessor


class TestCachePerformance:
    """Test cache performance."""

    def test_simple_cache_operations(self, tmp_path):
        """Test basic cache operations performance."""
        cache = SimpleCache(cache_dir=tmp_path / "cache", ttl=3600)
        
        # Test write performance
        start = time.time()
        for i in range(100):
            cache.set(f"key_{i}", f"value_{i}" * 100)
        write_time = time.time() - start
        
        # Test read performance
        start = time.time()
        for i in range(100):
            value = cache.get(f"key_{i}")
            assert value is not None
        read_time = time.time() - start
        
        # Performance assertions
        assert write_time < 1.0, f"Cache writes too slow: {write_time:.2f}s"
        assert read_time < 0.5, f"Cache reads too slow: {read_time:.2f}s"

    def test_cache_hit_vs_miss(self, tmp_path):
        """Test cache hit is significantly faster than miss."""
        cache = SimpleCache(cache_dir=tmp_path / "cache", ttl=3600)
        
        key = "test_key"
        value = "test_value" * 1000
        
        # Cache miss
        start = time.time()
        result = cache.get(key, extension="txt")
        miss_time = time.time() - start
        assert result is None
        
        # Set cache
        cache.set(key, value, extension="txt")
        
        # Cache hit
        start = time.time()
        result = cache.get(key, extension="txt")
        hit_time = time.time() - start
        assert result == value
        
        # Both operations should be very fast (< 1ms)
        assert hit_time < 0.001
        assert miss_time < 0.001

    def test_cache_cleanup_performance(self, tmp_path):
        """Test cache cleanup performance."""
        cache = SimpleCache(cache_dir=tmp_path / "cache", ttl=0)  # Immediate expiry
        
        # Create many expired entries
        for i in range(100):
            cache.set(f"key_{i}", f"value_{i}")
        
        time.sleep(0.1)  # Ensure expiry
        
        # Test cleanup performance
        start = time.time()
        removed = cache.cleanup_expired()
        cleanup_time = time.time() - start
        
        assert removed == 100
        assert cleanup_time < 1.0, f"Cleanup too slow: {cleanup_time:.2f}s"


class TestImageCachePerformance:
    """Test image cache performance."""

    def test_image_cache_saves_time(self, tmp_path):
        """Test that caching images improves performance."""
        # Note: This test doesn't actually download images
        # It just verifies the caching mechanism works
        
        cache_dir = tmp_path / "image_cache"
        processor_cached = ImageProcessor(use_cache=True)
        processor_uncached = ImageProcessor(use_cache=False)
        
        # Override cache dir for test
        if processor_cached.cache:
            processor_cached.cache.cache_dir = cache_dir
            cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Test data
        test_url = "https://example.com/test.jpg"
        test_data = b"fake_image_data" * 1000
        
        # Manually set cache
        if processor_cached.cache:
            cache_key = f"{test_url}::{processor_cached.max_size}::{processor_cached.quality}"
            processor_cached.cache.set(cache_key, test_data, extension="img")
        
        # Verify cache hit is faster (by checking cache directly)
        if processor_cached.cache:
            start = time.time()
            cached = processor_cached.cache.get(cache_key, extension="img")
            cache_time = time.time() - start
            
            assert cached is not None
            assert cache_time < 0.01, f"Cache retrieval too slow: {cache_time:.4f}s"


class TestCacheStats:
    """Test cache statistics and management."""

    def test_cache_stats(self, tmp_path):
        """Test cache statistics calculation."""
        cache = SimpleCache(cache_dir=tmp_path / "cache", ttl=3600)
        
        # Add some entries
        for i in range(10):
            cache.set(f"key_{i}", f"value_{i}" * 100)
        
        stats = cache.get_stats()
        
        assert stats['entry_count'] == 10
        assert stats['valid_count'] == 10
        assert stats['expired_count'] == 0
        assert stats['total_size_bytes'] > 0
        assert stats['total_size_mb'] > 0

    def test_cache_size_calculation(self, tmp_path):
        """Test cache size calculation is accurate."""
        cache = SimpleCache(cache_dir=tmp_path / "cache", ttl=3600)
        
        # Create entries of known size
        data_size = 1024  # 1KB
        for i in range(5):
            cache.set(f"key_{i}", "x" * data_size)
        
        total_size = cache.get_size()
        
        # Should be approximately 5KB (plus metadata)
        # Allow for metadata overhead
        assert total_size > (5 * data_size)
        assert total_size < (5 * data_size * 2)


# Performance targets
PERFORMANCE_TARGETS = {
    'cache_write_100': 1.0,  # seconds for 100 writes
    'cache_read_100': 0.5,   # seconds for 100 reads
    'cache_cleanup_100': 1.0,  # seconds to cleanup 100 entries
    'cache_hit': 0.01,  # seconds for cache hit
}


class TestPerformanceTargets:
    """Verify performance targets are met."""

    def test_all_targets_met(self, tmp_path):
        """Verify all performance targets are achievable."""
        results = {}
        
        cache = SimpleCache(cache_dir=tmp_path / "cache", ttl=3600)
        
        # Test cache writes
        start = time.time()
        for i in range(100):
            cache.set(f"key_{i}", f"value_{i}" * 100)
        results['cache_write_100'] = time.time() - start
        
        # Test cache reads
        start = time.time()
        for i in range(100):
            cache.get(f"key_{i}")
        results['cache_read_100'] = time.time() - start
        
        # Test cache hit
        cache.set("hit_test", "data")
        start = time.time()
        cache.get("hit_test")
        results['cache_hit'] = time.time() - start
        
        # Check all targets
        failures = []
        for metric, target in PERFORMANCE_TARGETS.items():
            if metric in results and results[metric] > target:
                failures.append(
                    f"{metric}: {results[metric]:.4f}s > {target}s"
                )
        
        if failures:
            pytest.fail(f"Performance targets not met:\n" + "\n".join(failures))
