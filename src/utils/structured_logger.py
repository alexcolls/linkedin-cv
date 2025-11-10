"""Structured logging with correlation IDs and rich context."""
import logging
import sys
import uuid
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Dict, Optional

import structlog


# Context variable for correlation ID (thread-safe)
correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


def add_correlation_id(logger: Any, method_name: str, event_dict: Dict) -> Dict:
    """Add correlation ID to log events."""
    corr_id = correlation_id.get()
    if corr_id:
        event_dict["correlation_id"] = corr_id
    return event_dict


def configure_structured_logging(
    level: str = "INFO",
    json_logs: bool = False,
    log_file: Optional[str] = None,
) -> None:
    """Configure structured logging with structlog.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Output logs as JSON (useful for production)
        log_file: Optional file path for log output
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        add_correlation_id,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if json_logs:
        # JSON output for production
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Human-readable output for development
        processors.append(
            structlog.dev.ConsoleRenderer(
                colors=sys.stdout.isatty(),
                exception_formatter=structlog.dev.plain_traceback,
            )
        )
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure stdlib logging
    logging.basicConfig(
        format="%(message)s",
        level=log_level,
        stream=sys.stdout,
    )
    
    # Add file handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        logging.root.addHandler(file_handler)


def get_logger(name: str = "linkedin_cv") -> structlog.BoundLogger:
    """Get a structured logger instance.
    
    Args:
        name: Logger name (usually __name__ of the module)
        
    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)


def set_correlation_id(corr_id: Optional[str] = None) -> str:
    """Set correlation ID for request tracking.
    
    Args:
        corr_id: Correlation ID (generates one if not provided)
        
    Returns:
        The correlation ID that was set
    """
    if corr_id is None:
        corr_id = str(uuid.uuid4())
    correlation_id.set(corr_id)
    return corr_id


def clear_correlation_id() -> None:
    """Clear the correlation ID."""
    correlation_id.set(None)


class CorrelationContext:
    """Context manager for correlation ID tracking."""
    
    def __init__(self, corr_id: Optional[str] = None):
        """Initialize with optional correlation ID."""
        self.corr_id = corr_id
        self.previous_id = None
    
    def __enter__(self) -> str:
        """Set correlation ID on entry."""
        self.previous_id = correlation_id.get()
        self.corr_id = set_correlation_id(self.corr_id)
        return self.corr_id
    
    def __exit__(self, *args) -> None:
        """Restore previous correlation ID on exit."""
        correlation_id.set(self.previous_id)


def log_function_call(logger: structlog.BoundLogger):
    """Decorator to log function entry/exit with timing.
    
    Usage:
        @log_function_call(logger)
        def my_function(arg1, arg2):
            pass
    """
    def decorator(func):
        import functools
        import time
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            logger.debug("function_called", function=func_name)
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger.debug(
                    "function_completed",
                    function=func_name,
                    duration_ms=f"{duration_ms:.2f}",
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    "function_failed",
                    function=func_name,
                    duration_ms=f"{duration_ms:.2f}",
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise
        
        return wrapper
    return decorator


def log_async_function_call(logger: structlog.BoundLogger):
    """Decorator to log async function entry/exit with timing.
    
    Usage:
        @log_async_function_call(logger)
        async def my_async_function(arg1, arg2):
            pass
    """
    def decorator(func):
        import functools
        import time
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            func_name = func.__name__
            logger.debug("async_function_called", function=func_name)
            
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger.debug(
                    "async_function_completed",
                    function=func_name,
                    duration_ms=f"{duration_ms:.2f}",
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    "async_function_failed",
                    function=func_name,
                    duration_ms=f"{duration_ms:.2f}",
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise
        
        return wrapper
    return decorator


# Initialize structured logging with defaults
configure_structured_logging()
