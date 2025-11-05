"""Caching utilities for performance optimization."""
import hashlib
import json
import pickle
import time
from pathlib import Path
from typing import Any, Optional, Callable
from functools import wraps


class SimpleCache:
    """Simple file-based cache for images and data."""

    def __init__(self, cache_dir: Optional[Path] = None, ttl: int = 3600):
        """Initialize cache.

        Args:
            cache_dir: Directory to store cache files (default: .cache in project root)
            ttl: Time-to-live in seconds (default: 1 hour)
        """
        self.cache_dir = cache_dir or (Path.home() / ".cache" / "linkedin-cv")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl

    def _get_cache_key(self, key: str) -> str:
        """Generate cache key hash.

        Args:
            key: Original key

        Returns:
            MD5 hash of key
        """
        return hashlib.md5(key.encode()).hexdigest()

    def _get_cache_path(self, key: str, extension: str = "cache") -> Path:
        """Get cache file path.

        Args:
            key: Cache key
            extension: File extension

        Returns:
            Path to cache file
        """
        cache_key = self._get_cache_key(key)
        return self.cache_dir / f"{cache_key}.{extension}"

    def _get_metadata_path(self, key: str) -> Path:
        """Get metadata file path.

        Args:
            key: Cache key

        Returns:
            Path to metadata file
        """
        cache_key = self._get_cache_key(key)
        return self.cache_dir / f"{cache_key}.meta"

    def _is_valid(self, metadata_path: Path) -> bool:
        """Check if cache entry is still valid.

        Args:
            metadata_path: Path to metadata file

        Returns:
            True if cache is valid, False otherwise
        """
        if not metadata_path.exists():
            return False

        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)

            timestamp = metadata.get('timestamp', 0)
            return (time.time() - timestamp) < self.ttl
        except Exception:
            return False

    def get(self, key: str, extension: str = "cache") -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key
            extension: File extension

        Returns:
            Cached value or None if not found/expired
        """
        cache_path = self._get_cache_path(key, extension)
        metadata_path = self._get_metadata_path(key)

        if not cache_path.exists() or not self._is_valid(metadata_path):
            return None

        try:
            if extension in ['txt', 'json', 'html', 'css']:
                # Text files
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif extension == 'json':
                # JSON files
                with open(cache_path, 'r') as f:
                    return json.load(f)
            else:
                # Binary files (images, pickled data)
                with open(cache_path, 'rb') as f:
                    return f.read()
        except Exception:
            return None

    def set(self, key: str, value: Any, extension: str = "cache"):
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            extension: File extension
        """
        cache_path = self._get_cache_path(key, extension)
        metadata_path = self._get_metadata_path(key)

        try:
            # Write value
            if extension in ['txt', 'json', 'html', 'css']:
                # Text files
                with open(cache_path, 'w', encoding='utf-8') as f:
                    if isinstance(value, str):
                        f.write(value)
                    else:
                        f.write(str(value))
            elif extension == 'json':
                # JSON files
                with open(cache_path, 'w') as f:
                    json.dump(value, f)
            else:
                # Binary files
                with open(cache_path, 'wb') as f:
                    if isinstance(value, bytes):
                        f.write(value)
                    else:
                        # Try to pickle
                        pickle.dump(value, f)

            # Write metadata
            metadata = {
                'timestamp': time.time(),
                'key': key,
                'extension': extension,
                'size': cache_path.stat().st_size
            }

            with open(metadata_path, 'w') as f:
                json.dump(metadata, f)

        except Exception as e:
            # Clean up on error
            if cache_path.exists():
                cache_path.unlink()
            if metadata_path.exists():
                metadata_path.unlink()
            raise e

    def delete(self, key: str):
        """Delete cache entry.

        Args:
            key: Cache key
        """
        cache_key = self._get_cache_key(key)

        # Delete all files with this cache key
        for file in self.cache_dir.glob(f"{cache_key}.*"):
            file.unlink()

    def clear(self):
        """Clear all cache entries."""
        for file in self.cache_dir.glob("*"):
            if file.is_file():
                file.unlink()

    def get_size(self) -> int:
        """Get total cache size in bytes.

        Returns:
            Total size of all cache files
        """
        return sum(f.stat().st_size for f in self.cache_dir.glob("*") if f.is_file())

    def get_stats(self) -> dict:
        """Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        files = list(self.cache_dir.glob("*.cache"))
        meta_files = list(self.cache_dir.glob("*.meta"))

        total_size = self.get_size()
        entry_count = len(files)

        # Count valid entries
        valid_count = sum(1 for meta in meta_files if self._is_valid(meta))

        return {
            'entry_count': entry_count,
            'valid_count': valid_count,
            'expired_count': entry_count - valid_count,
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'cache_dir': str(self.cache_dir)
        }

    def cleanup_expired(self):
        """Remove expired cache entries."""
        removed_count = 0

        for meta_path in self.cache_dir.glob("*.meta"):
            if not self._is_valid(meta_path):
                cache_key = meta_path.stem
                for file in self.cache_dir.glob(f"{cache_key}.*"):
                    file.unlink()
                removed_count += 1

        return removed_count


class ImageCache(SimpleCache):
    """Specialized cache for profile images."""

    def __init__(self, cache_dir: Optional[Path] = None, ttl: int = 86400):
        """Initialize image cache.

        Args:
            cache_dir: Directory to store cache files
            ttl: Time-to-live in seconds (default: 24 hours)
        """
        cache_dir = cache_dir or (Path.home() / ".cache" / "linkedin-cv" / "images")
        super().__init__(cache_dir, ttl)

    def get_image(self, url: str) -> Optional[bytes]:
        """Get cached image data.

        Args:
            url: Image URL

        Returns:
            Image data as bytes or None
        """
        return self.get(url, extension="img")

    def set_image(self, url: str, image_data: bytes):
        """Cache image data.

        Args:
            url: Image URL
            image_data: Image data as bytes
        """
        self.set(url, image_data, extension="img")


def cached(cache_instance: SimpleCache, key_func: Optional[Callable] = None, ttl: Optional[int] = None):
    """Decorator to cache function results.

    Args:
        cache_instance: Cache instance to use
        key_func: Function to generate cache key from args (default: str(args[0]))
        ttl: Time-to-live override for this decorator

    Returns:
        Decorated function

    Example:
        @cached(image_cache, key_func=lambda url: url)
        def download_image(url):
            return requests.get(url).content
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            elif args:
                cache_key = f"{func.__name__}:{str(args[0])}"
            else:
                cache_key = f"{func.__name__}:{str(kwargs)}"

            # Override TTL if specified
            original_ttl = cache_instance.ttl
            if ttl is not None:
                cache_instance.ttl = ttl

            try:
                # Try to get from cache
                cached_value = cache_instance.get(cache_key)
                if cached_value is not None:
                    return cached_value

                # Call function and cache result
                result = func(*args, **kwargs)
                cache_instance.set(cache_key, result)

                return result
            finally:
                # Restore original TTL
                cache_instance.ttl = original_ttl

        return wrapper
    return decorator


# Global cache instances
_default_cache = SimpleCache()
_image_cache = ImageCache()


def get_cache() -> SimpleCache:
    """Get default cache instance."""
    return _default_cache


def get_image_cache() -> ImageCache:
    """Get image cache instance."""
    return _image_cache
