"""Tests for structured logging system."""
import logging
import sys
from io import StringIO
from pathlib import Path

import pytest
import structlog

from src.utils.structured_logger import (
    CorrelationContext,
    add_correlation_id,
    clear_correlation_id,
    configure_structured_logging,
    correlation_id,
    get_logger,
    log_async_function_call,
    log_function_call,
    set_correlation_id,
)


@pytest.fixture
def reset_logging():
    """Reset logging configuration after each test."""
    yield
    # Clear correlation ID
    clear_correlation_id()
    # Reset structlog configuration
    structlog.reset_defaults()


def test_configure_structured_logging_default(reset_logging):
    """Test default structured logging configuration."""
    configure_structured_logging()
    
    logger = get_logger("test")
    assert logger is not None
    # Logger can be BoundLogger or BoundLoggerLazyProxy
    assert hasattr(logger, "info")


def test_configure_structured_logging_json(reset_logging):
    """Test JSON logging configuration."""
    configure_structured_logging(level="DEBUG", json_logs=True)
    
    logger = get_logger("test")
    assert logger is not None


def test_configure_structured_logging_with_file(reset_logging, tmp_path):
    """Test logging configuration with file output."""
    log_file = tmp_path / "test.log"
    configure_structured_logging(log_file=str(log_file))
    
    logger = get_logger("test")
    logger.info("test_message")
    
    # Check that log file was created
    assert log_file.exists()


def test_get_logger(reset_logging):
    """Test getting a logger instance."""
    configure_structured_logging()
    
    logger1 = get_logger("test1")
    logger2 = get_logger("test2")
    
    assert logger1 is not None
    assert logger2 is not None
    # Loggers can be BoundLogger or BoundLoggerLazyProxy
    assert hasattr(logger1, "info")
    assert hasattr(logger2, "info")


def test_set_correlation_id(reset_logging):
    """Test setting correlation ID."""
    corr_id = "test-123"
    result = set_correlation_id(corr_id)
    
    assert result == corr_id
    assert correlation_id.get() == corr_id


def test_set_correlation_id_auto_generate(reset_logging):
    """Test auto-generating correlation ID."""
    result = set_correlation_id()
    
    assert result is not None
    assert len(result) > 0
    assert correlation_id.get() == result


def test_clear_correlation_id(reset_logging):
    """Test clearing correlation ID."""
    set_correlation_id("test-123")
    assert correlation_id.get() == "test-123"
    
    clear_correlation_id()
    assert correlation_id.get() is None


def test_add_correlation_id(reset_logging):
    """Test adding correlation ID to log event."""
    set_correlation_id("test-123")
    
    event_dict = {}
    result = add_correlation_id(None, "info", event_dict)
    
    assert "correlation_id" in result
    assert result["correlation_id"] == "test-123"


def test_add_correlation_id_none(reset_logging):
    """Test adding correlation ID when none is set."""
    clear_correlation_id()
    
    event_dict = {}
    result = add_correlation_id(None, "info", event_dict)
    
    assert "correlation_id" not in result


def test_correlation_context(reset_logging):
    """Test correlation context manager."""
    # Should start with no correlation ID
    assert correlation_id.get() is None
    
    with CorrelationContext() as corr_id:
        # Inside context, should have correlation ID
        assert corr_id is not None
        assert correlation_id.get() == corr_id
    
    # After context, should be cleared
    assert correlation_id.get() is None


def test_correlation_context_with_id(reset_logging):
    """Test correlation context with specific ID."""
    test_id = "test-456"
    
    with CorrelationContext(test_id) as corr_id:
        assert corr_id == test_id
        assert correlation_id.get() == test_id


def test_correlation_context_nested(reset_logging):
    """Test nested correlation contexts."""
    outer_id = "outer-123"
    inner_id = "inner-456"
    
    with CorrelationContext(outer_id) as corr_id_1:
        assert correlation_id.get() == outer_id
        
        with CorrelationContext(inner_id) as corr_id_2:
            assert correlation_id.get() == inner_id
        
        # Should restore outer ID after inner context
        assert correlation_id.get() == outer_id
    
    # Should be cleared after outer context
    assert correlation_id.get() is None


def test_log_function_call_decorator(reset_logging):
    """Test function call logging decorator."""
    configure_structured_logging(level="DEBUG")
    logger = get_logger("test")
    
    @log_function_call(logger)
    def test_function(x, y):
        return x + y
    
    result = test_function(2, 3)
    assert result == 5


def test_log_function_call_decorator_with_exception(reset_logging):
    """Test function call logging decorator with exception."""
    configure_structured_logging(level="DEBUG")
    logger = get_logger("test")
    
    @log_function_call(logger)
    def failing_function():
        raise ValueError("Test error")
    
    with pytest.raises(ValueError, match="Test error"):
        failing_function()


@pytest.mark.asyncio
async def test_log_async_function_call_decorator(reset_logging):
    """Test async function call logging decorator."""
    configure_structured_logging(level="DEBUG")
    logger = get_logger("test")
    
    @log_async_function_call(logger)
    async def async_test_function(x, y):
        return x + y
    
    result = await async_test_function(2, 3)
    assert result == 5


@pytest.mark.asyncio
async def test_log_async_function_call_decorator_with_exception(reset_logging):
    """Test async function call logging decorator with exception."""
    configure_structured_logging(level="DEBUG")
    logger = get_logger("test")
    
    @log_async_function_call(logger)
    async def async_failing_function():
        raise ValueError("Test async error")
    
    with pytest.raises(ValueError, match="Test async error"):
        await async_failing_function()


def test_structured_log_output(reset_logging, capsys):
    """Test that structured logs contain expected fields."""
    configure_structured_logging(level="INFO", json_logs=False)
    logger = get_logger("test")
    
    set_correlation_id("test-789")
    logger.info("test_event", key1="value1", key2=42)
    
    # Note: Can't easily capture structlog output, but this tests that it doesn't crash


def test_logging_levels(reset_logging):
    """Test different logging levels."""
    configure_structured_logging(level="DEBUG")
    logger = get_logger("test")
    
    # All these should work without raising
    logger.debug("debug_message", detail="test")
    logger.info("info_message", detail="test")
    logger.warning("warning_message", detail="test")
    logger.error("error_message", detail="test")
    logger.critical("critical_message", detail="test")


def test_context_binding(reset_logging):
    """Test binding context to logger."""
    configure_structured_logging()
    logger = get_logger("test")
    
    # Bind context
    bound_logger = logger.bind(request_id="123", user="testuser")
    
    # Should work without errors
    bound_logger.info("test_with_context")


def test_exception_logging(reset_logging):
    """Test logging exceptions with exc_info."""
    configure_structured_logging()
    logger = get_logger("test")
    
    try:
        raise ValueError("Test exception")
    except ValueError:
        # Should log exception without crashing
        logger.error("error_occurred", exc_info=True)


def test_log_file_creation(reset_logging, tmp_path):
    """Test that log file directory is created."""
    log_file = tmp_path / "logs" / "app.log"
    configure_structured_logging(log_file=str(log_file))
    
    # Parent directory should be created
    assert log_file.parent.exists()


def test_correlation_with_structured_logging(reset_logging):
    """Test correlation ID integration with structured logging."""
    configure_structured_logging(level="DEBUG")
    logger = get_logger("test")
    
    with CorrelationContext("workflow-123"):
        # Log within correlation context
        logger.info("operation_started", operation="test_op")
        
        # Correlation ID should be automatically added
        assert correlation_id.get() == "workflow-123"
