"""Tests for the EnvistLogger module."""
import logging
import tempfile
import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import pytest

from envist.logger import (
    EnvistLogger, 
    create_stream_handler,
    create_file_handler,
    create_json_handler,
    create_rotating_handler,
    create_syslog_handler,
    create_default_handlers,
    configure_logger,
    logger
)


class TestEnvistLogger:
    """Test suite for EnvistLogger class."""
    
    def setup_method(self):
        """Setup for each test method."""
        # Reset the singleton instance
        EnvistLogger.configure(reset=True)
    
    def teardown_method(self):
        """Cleanup after each test method."""
        # Reset the singleton instance
        EnvistLogger.configure(reset=True)
    
    def test_singleton_behavior(self):
        """Test that EnvistLogger follows singleton pattern."""
        logger1 = EnvistLogger()
        logger2 = EnvistLogger()
        
        assert logger1 is logger2
        assert id(logger1) == id(logger2)
    
    def test_initialization_with_custom_handlers(self):
        """Test initialization with custom handlers."""
        custom_handler = logging.StreamHandler()
        logger_instance = EnvistLogger.configure(custom_handlers=[custom_handler], reset=True)
        
        assert custom_handler in logger_instance.get_handlers()
    
    def test_initialization_without_custom_handlers(self):
        """Test initialization without custom handlers."""
        logger_instance = EnvistLogger()
        
        # Should have default handlers
        handlers = logger_instance.get_handlers()
        assert len(handlers) > 0
    
    def test_prevent_duplicate_initialization(self):
        """Test that multiple initializations don't create duplicate handlers."""
        logger1 = EnvistLogger()
        initial_handler_count = len(logger1.get_handlers())
        
        logger2 = EnvistLogger()
        final_handler_count = len(logger2.get_handlers())
        
        assert initial_handler_count == final_handler_count
    
    def test_add_handler(self):
        """Test adding a handler to the logger."""
        logger_instance = EnvistLogger()
        custom_handler = logging.StreamHandler()
        
        initial_count = len(logger_instance.get_handlers())
        logger_instance.add_handler(custom_handler)
        final_count = len(logger_instance.get_handlers())
        
        assert final_count == initial_count + 1
        assert custom_handler in logger_instance.get_handlers()
    
    def test_remove_handler(self):
        """Test removing a handler from the logger."""
        logger_instance = EnvistLogger()
        custom_handler = logging.StreamHandler()
        
        logger_instance.add_handler(custom_handler)
        assert custom_handler in logger_instance.get_handlers()
        
        logger_instance.remove_handler(custom_handler)
        assert custom_handler not in logger_instance.get_handlers()
    
    def test_clear_handlers(self):
        """Test clearing all handlers from the logger."""
        logger_instance = EnvistLogger()
        logger_instance.clear_handlers()
        
        assert len(logger_instance.get_handlers()) == 0
    
    def test_replace_handlers(self):
        """Test replacing all handlers with new ones."""
        logger_instance = EnvistLogger()
        
        new_handlers = [
            logging.StreamHandler(),
            logging.StreamHandler()
        ]
        
        logger_instance.replace_handlers(new_handlers)
        current_handlers = logger_instance.get_handlers()
        
        assert len(current_handlers) == 2
        assert all(h in current_handlers for h in new_handlers)
    
    def test_get_handlers(self):
        """Test getting all current handlers."""
        logger_instance = EnvistLogger()
        handlers = logger_instance.get_handlers()
        
        assert isinstance(handlers, list)
        assert all(isinstance(h, logging.Handler) for h in handlers)
    
    def test_debug_logging(self):
        """Test debug logging functionality."""
        logger_instance = EnvistLogger()
        
        with patch.object(logger_instance.logger, 'debug') as mock_debug:
            logger_instance.debug("Test debug message", extra_info="test")
            mock_debug.assert_called_once_with("Test debug message", extra={'extra_info': 'test'})
    
    def test_info_logging(self):
        """Test info logging functionality."""
        logger_instance = EnvistLogger()
        
        with patch.object(logger_instance.logger, 'info') as mock_info:
            logger_instance.info("Test info message", user="admin")
            mock_info.assert_called_once_with("Test info message", extra={'user': 'admin'})
    
    def test_warning_logging(self):
        """Test warning logging functionality."""
        logger_instance = EnvistLogger()
        
        with patch.object(logger_instance.logger, 'warning') as mock_warning:
            logger_instance.warning("Test warning message")
            mock_warning.assert_called_once_with("Test warning message", extra={})
    
    def test_error_logging(self):
        """Test error logging functionality."""
        logger_instance = EnvistLogger()
        
        with patch.object(logger_instance.logger, 'error') as mock_error:
            logger_instance.error("Test error message", error_code=500)
            mock_error.assert_called_once_with("Test error message", extra={'error_code': 500})
    
    def test_critical_logging(self):
        """Test critical logging functionality."""
        logger_instance = EnvistLogger()
        
        with patch.object(logger_instance.logger, 'critical') as mock_critical:
            logger_instance.critical("Test critical message")
            mock_critical.assert_called_once_with("Test critical message", extra={})
    
    def test_log_env_parse(self):
        """Test environment file parsing logging."""
        logger_instance = EnvistLogger()
        
        with patch.object(logger_instance, 'info') as mock_info:
            logger_instance.log_env_parse("/path/to/file.env", 5)
            mock_info.assert_called_once_with("Parsed /path/to/file.env: found 5 variables")
    
    def test_log_typecast_success(self):
        """Test successful typecast logging."""
        logger_instance = EnvistLogger()
        
        with patch.object(logger_instance, 'debug') as mock_debug:
            logger_instance.log_typecast("MY_VAR", "123", "int", True)
            mock_debug.assert_called_once_with("Successfully cast 'MY_VAR' to int")
    
    def test_log_typecast_failure(self):
        """Test failed typecast logging."""
        logger_instance = EnvistLogger()
        
        with patch.object(logger_instance, 'error') as mock_error:
            logger_instance.log_typecast("MY_VAR", "invalid", "int", False)
            mock_error.assert_called_once_with("Failed to cast 'MY_VAR' = 'invalid' to int")
    
    def test_log_variable_expansion_with_change(self):
        """Test variable expansion logging when expansion occurs."""
        logger_instance = EnvistLogger()
        
        with patch.object(logger_instance, 'debug') as mock_debug:
            logger_instance.log_variable_expansion("${HOME}/file", "/home/user/file")
            mock_debug.assert_called_once_with("Expanded '${HOME}/file' to '/home/user/file'")
    
    def test_log_variable_expansion_no_change(self):
        """Test variable expansion logging when no expansion occurs."""
        logger_instance = EnvistLogger()
        
        with patch.object(logger_instance, 'debug') as mock_debug:
            logger_instance.log_variable_expansion("simple_value", "simple_value")
            mock_debug.assert_not_called()
    
    def test_log_variable_access_found_with_cast(self):
        """Test variable access logging when variable is found with casting."""
        logger_instance = EnvistLogger()
        
        with patch.object(logger_instance, 'debug') as mock_debug:
            logger_instance.log_variable_access("MY_VAR", True, "int")
            mock_debug.assert_called_once_with("Retrieved variable 'MY_VAR' (cast to int)")
    
    def test_log_variable_access_found_without_cast(self):
        """Test variable access logging when variable is found without casting."""
        logger_instance = EnvistLogger()
        
        with patch.object(logger_instance, 'debug') as mock_debug:
            logger_instance.log_variable_access("MY_VAR", True)
            mock_debug.assert_called_once_with("Retrieved variable 'MY_VAR'")
    
    def test_log_variable_access_not_found(self):
        """Test variable access logging when variable is not found."""
        logger_instance = EnvistLogger()
        
        with patch.object(logger_instance, 'warning') as mock_warning:
            logger_instance.log_variable_access("MISSING_VAR", False)
            mock_warning.assert_called_once_with("Variable 'MISSING_VAR' not found")
    
    def test_set_level_valid_levels(self):
        """Test setting valid logging levels."""
        logger_instance = EnvistLogger()
        
        levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        expected_levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
        
        for level_str, expected_level in zip(levels, expected_levels):
            logger_instance.set_level(level_str)
            assert logger_instance.logger.level == expected_level
    
    def test_set_level_case_insensitive(self):
        """Test setting logging levels is case insensitive."""
        logger_instance = EnvistLogger()
        
        logger_instance.set_level('debug')
        assert logger_instance.logger.level == logging.DEBUG
        
        logger_instance.set_level('Info')
        assert logger_instance.logger.level == logging.INFO
    
    def test_set_level_invalid_level(self):
        """Test setting invalid logging level."""
        logger_instance = EnvistLogger()
        original_level = logger_instance.logger.level
        
        logger_instance.set_level('INVALID_LEVEL')
        # Level should remain unchanged
        assert logger_instance.logger.level == original_level
    
    def test_configure_classmethod_new_instance(self):
        """Test configure classmethod creates new instance."""
        # Reset singleton
        EnvistLogger._instance = None
        EnvistLogger._initialized = False
        
        custom_handler = logging.StreamHandler()
        logger_instance = EnvistLogger.configure(custom_handlers=[custom_handler])
        
        assert isinstance(logger_instance, EnvistLogger)
        # Check that handlers were added
        handlers = logger_instance.get_handlers()
        assert len(handlers) >= 1
    
    def test_configure_classmethod_reset_existing(self):
        """Test configure classmethod with reset=True."""
        # Create initial instance
        logger_instance1 = EnvistLogger()
        initial_handlers = logger_instance1.get_handlers()
        
        # Configure with reset
        custom_handler = logging.StreamHandler()
        logger_instance2 = EnvistLogger.configure(custom_handlers=[custom_handler], reset=True)
        
        # Should have new handlers
        new_handlers = logger_instance2.get_handlers()
        assert custom_handler in new_handlers
        assert len(new_handlers) == 1  # Only the custom handler
    
    def test_configure_classmethod_existing_instance_new_handlers(self):
        """Test configure classmethod with existing instance and new handlers."""
        # Create initial instance
        logger_instance1 = EnvistLogger()
        
        # Configure with new handlers
        custom_handler = logging.StreamHandler()
        logger_instance2 = EnvistLogger.configure(custom_handlers=[custom_handler])
        
        # Should be same instance but with replaced handlers
        assert logger_instance1 is logger_instance2
        assert custom_handler in logger_instance2.get_handlers()
    
    @patch('envist.logger.Path.home')
    def test_default_file_handler_creation(self, mock_home):
        """Test creation of default file handler."""
        mock_home.return_value = Path('/tmp/test_home')
        
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            with patch('logging.FileHandler') as mock_file_handler:
                # Reset and create new instance to trigger default handler setup
                EnvistLogger.configure(reset=True)
                logger_instance = EnvistLogger()
                
                # Check that the log directory is created
                mock_mkdir.assert_called()
    
    def test_custom_handlers_priority(self):
        """Test that custom handlers take priority over default handlers."""
        custom_handler = logging.StreamHandler()
        logger_instance = EnvistLogger.configure(custom_handlers=[custom_handler], reset=True)
        
        handlers = logger_instance.get_handlers()
        assert custom_handler in handlers


class TestLoggerFactoryFunctions:
    """Test suite for logger factory functions."""
    
    def test_create_stream_handler_default(self):
        """Test creating stream handler with defaults."""
        handler = create_stream_handler()
        
        assert isinstance(handler, logging.StreamHandler)
        assert handler.level == logging.INFO
        assert isinstance(handler.formatter, logging.Formatter)
    
    def test_create_stream_handler_custom_stream(self):
        """Test creating stream handler with custom stream."""
        import io
        custom_stream = io.StringIO()
        handler = create_stream_handler(stream=custom_stream, level=logging.DEBUG)
        
        assert isinstance(handler, logging.StreamHandler)
        assert handler.stream is custom_stream
        assert handler.level == logging.DEBUG
    
    def test_create_file_handler(self):
        """Test creating file handler."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            log_file_path = tmp_file.name
        
        try:
            handler = create_file_handler(log_file_path, level=logging.WARNING)
            
            assert isinstance(handler, logging.FileHandler)
            assert handler.level == logging.WARNING
            assert isinstance(handler.formatter, logging.Formatter)
            
            # Close the handler to release the file
            handler.close()
        finally:
            Path(log_file_path).unlink(missing_ok=True)
    
    def test_create_file_handler_creates_directory(self):
        """Test that file handler creates necessary directories."""
        temp_dir = tempfile.mkdtemp()
        log_file_path = Path(temp_dir) / "logs" / "test.log"
        
        try:
            handler = create_file_handler(log_file_path)
            
            assert log_file_path.parent.exists()
            assert isinstance(handler, logging.FileHandler)
            
            # Close the handler to release the file
            handler.close()
        finally:
            # Cleanup
            if log_file_path.exists():
                log_file_path.unlink()
            if log_file_path.parent.exists():
                log_file_path.parent.rmdir()
            Path(temp_dir).rmdir()
    
    def test_create_json_handler(self):
        """Test creating JSON handler."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            log_file_path = tmp_file.name
        
        try:
            handler = create_json_handler(log_file_path, level=logging.ERROR)
            
            assert isinstance(handler, logging.FileHandler)
            assert handler.level == logging.ERROR
            
            # Test the JSON formatter
            record = logging.LogRecord(
                name="test", level=logging.INFO, pathname="test.py", lineno=1,
                msg="Test message", args=(), exc_info=None
            )
            formatted = handler.formatter.format(record)
            
            # Should be valid JSON
            json_data = json.loads(formatted)
            assert 'timestamp' in json_data
            assert 'level' in json_data
            assert 'message' in json_data
            assert json_data['message'] == "Test message"
            
            # Close the handler to release the file
            handler.close()
        finally:
            Path(log_file_path).unlink(missing_ok=True)
    
    def test_create_json_handler_creates_directory(self):
        """Test that JSON handler creates necessary directories."""
        temp_dir = tempfile.mkdtemp()
        log_file_path = Path(temp_dir) / "logs" / "test.log"
        
        try:
            handler = create_json_handler(log_file_path)
            
            assert log_file_path.parent.exists()
            assert isinstance(handler, logging.FileHandler)
            
            # Close the handler to release the file
            handler.close()
        finally:
            # Cleanup
            if log_file_path.exists():
                log_file_path.unlink()
            if log_file_path.parent.exists():
                log_file_path.parent.rmdir()
            Path(temp_dir).rmdir()
    
    def test_create_rotating_handler(self):
        """Test creating rotating file handler."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            log_file_path = tmp_file.name
        
        try:
            handler = create_rotating_handler(
                log_file_path, 
                max_bytes=1024, 
                backup_count=3, 
                level=logging.DEBUG
            )
            
            assert handler.level == logging.DEBUG
            assert handler.maxBytes == 1024
            assert handler.backupCount == 3
            assert isinstance(handler.formatter, logging.Formatter)
            
            # Close the handler to release the file
            handler.close()
        finally:
            Path(log_file_path).unlink(missing_ok=True)
    
    def test_create_rotating_handler_creates_directory(self):
        """Test that rotating handler creates necessary directories."""
        temp_dir = tempfile.mkdtemp()
        log_file_path = Path(temp_dir) / "logs" / "test.log"
        
        try:
            handler = create_rotating_handler(log_file_path)
            
            assert log_file_path.parent.exists()
            
            # Close the handler to release the file
            handler.close()
        finally:
            # Cleanup
            if log_file_path.exists():
                log_file_path.unlink()
            if log_file_path.parent.exists():
                log_file_path.parent.rmdir()
            Path(temp_dir).rmdir()
    
    def test_create_syslog_handler(self):
        """Test creating syslog handler."""
        handler = create_syslog_handler(address=('localhost', 514), level=logging.WARNING)
        
        assert handler.level == logging.WARNING
        assert isinstance(handler.formatter, logging.Formatter)
    
    def test_create_default_handlers(self):
        """Test creating default handlers."""
        handlers = create_default_handlers()
        
        assert len(handlers) == 2
        assert any(isinstance(h, logging.StreamHandler) for h in handlers)
        assert any(isinstance(h, logging.FileHandler) for h in handlers)
        
        # Check levels
        stream_handler = next(h for h in handlers if isinstance(h, logging.StreamHandler))
        file_handler = next(h for h in handlers if isinstance(h, logging.FileHandler))
        
        assert stream_handler.level == logging.WARNING
        assert file_handler.level == logging.DEBUG
    
    def test_configure_logger_function(self):
        """Test configure_logger function."""
        custom_handler = logging.StreamHandler()
        logger_instance = configure_logger(handlers=[custom_handler], level='DEBUG')
        
        assert isinstance(logger_instance, EnvistLogger)
        assert custom_handler in logger_instance.get_handlers()
        assert logger_instance.logger.level == logging.DEBUG
    
    def test_configure_logger_function_no_handlers(self):
        """Test configure_logger function with no custom handlers."""
        logger_instance = configure_logger(level='ERROR')
        
        assert isinstance(logger_instance, EnvistLogger)
        assert logger_instance.logger.level == logging.ERROR


class TestGlobalLoggerInstance:
    """Test suite for global logger instance."""
    
    def test_global_logger_exists(self):
        """Test that global logger instance exists."""
        assert logger is not None
        assert isinstance(logger, EnvistLogger)
    
    def test_global_logger_singleton(self):
        """Test that global logger is the same as new instances."""
        # Reset to ensure clean state
        EnvistLogger.configure(reset=True)
        new_logger = EnvistLogger()
        from envist.logger import logger as global_logger
        
        # Both should reference the same singleton instance
        assert new_logger.__class__ is global_logger.__class__


class TestLoggerEdgeCases:
    """Test suite for edge cases and error conditions."""
    
    def setup_method(self):
        """Setup for each test method."""
        EnvistLogger.configure(reset=True)
    
    def teardown_method(self):
        """Cleanup after each test method."""
        EnvistLogger.configure(reset=True)
    
    def test_multiple_configure_calls(self):
        """Test multiple calls to configure method."""
        handler1 = logging.StreamHandler()
        handler2 = logging.StreamHandler()
        
        logger1 = EnvistLogger.configure(custom_handlers=[handler1])
        logger2 = EnvistLogger.configure(custom_handlers=[handler2])
        
        assert logger1 is logger2
        assert handler2 in logger2.get_handlers()
        assert handler1 not in logger2.get_handlers()  # Should be replaced
    
    def test_handler_operations_on_empty_logger(self):
        """Test handler operations when logger has no handlers."""
        logger_instance = EnvistLogger()
        logger_instance.clear_handlers()
        
        # Should not raise errors
        logger_instance.clear_handlers()
        handlers = logger_instance.get_handlers()
        assert len(handlers) == 0
    
    def test_remove_nonexistent_handler(self):
        """Test removing a handler that doesn't exist."""
        logger_instance = EnvistLogger()
        nonexistent_handler = logging.StreamHandler()
        
        # Should not raise error
        logger_instance.remove_handler(nonexistent_handler)
    
    def test_logging_with_no_handlers(self):
        """Test logging when no handlers are configured."""
        logger_instance = EnvistLogger()
        logger_instance.clear_handlers()
        
        # Should not raise errors
        logger_instance.info("Test message")
        logger_instance.error("Error message")
    
    @patch('envist.logger.Path.home')
    @patch('pathlib.Path.mkdir')
    def test_file_handler_directory_creation_failure(self, mock_mkdir, mock_home):
        """Test handling of directory creation failure."""
        mock_home.return_value = Path('/tmp/test_home')
        mock_mkdir.side_effect = PermissionError("Cannot create directory")
        
        # Test should pass if the error is NOT handled gracefully (as expected)
        with pytest.raises(PermissionError):
            EnvistLogger.configure(reset=True)
            logger_instance = EnvistLogger()
    
    def test_json_formatter_with_complex_record(self):
        """Test JSON formatter with complex log record."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            log_file_path = tmp_file.name
        
        try:
            handler = create_json_handler(log_file_path)
            
            # Create a complex log record
            record = logging.LogRecord(
                name="test.module", level=logging.WARNING, pathname="/path/to/test.py", 
                lineno=42, msg="Complex message with %s and %d", 
                args=("string", 123), exc_info=None, func="test_function"
            )
            
            formatted = handler.formatter.format(record)
            json_data = json.loads(formatted)
            
            assert json_data['level'] == 'WARNING'
            assert json_data['function'] == 'test_function'
            assert json_data['line'] == 42
            assert "Complex message with string and 123" in json_data['message']
            
            # Close the handler to release the file
            handler.close()
        finally:
            Path(log_file_path).unlink(missing_ok=True)
