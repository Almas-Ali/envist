"""Tests for the EnvistConfig module."""
import os
import tempfile
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from envist.config import EnvistConfig, config
from envist.logger import EnvistLogger


class TestEnvistConfig:
    """Test suite for EnvistConfig class."""
    
    def setup_method(self):
        """Setup for each test method."""
        # Reset any existing configuration
        EnvistLogger.configure(reset=True)
        
    def teardown_method(self):
        """Cleanup after each test method."""
        # Clean up environment variables
        env_vars = ['ENVIST_DEBUG', 'ENVIST_LOG_LEVEL', 'ENVIST_LOG_FORMAT', 
                   'ENVIST_LOG_FILE', 'ENVIST_ROTATING_LOGS']
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]
        
        # Reset logger
        EnvistLogger.configure(reset=True)
    
    def test_default_configuration(self):
        """Test default configuration values."""
        config_instance = EnvistConfig()
        
        assert config_instance.debug_mode is False
        assert config_instance.log_level == 'INFO'
        assert config_instance.log_format == 'standard'
        assert config_instance.log_file is None
        assert config_instance.rotating_logs is False
    
    def test_debug_mode_configuration(self):
        """Test debug mode configuration from environment."""
        with patch.dict(os.environ, {'ENVIST_DEBUG': 'true'}):
            config_instance = EnvistConfig()
            assert config_instance.debug_mode is True
        
        with patch.dict(os.environ, {'ENVIST_DEBUG': 'TRUE'}):
            config_instance = EnvistConfig()
            assert config_instance.debug_mode is True
        
        with patch.dict(os.environ, {'ENVIST_DEBUG': 'false'}):
            config_instance = EnvistConfig()
            assert config_instance.debug_mode is False
        
        with patch.dict(os.environ, {'ENVIST_DEBUG': 'invalid'}):
            config_instance = EnvistConfig()
            assert config_instance.debug_mode is False
    
    def test_log_level_configuration(self):
        """Test log level configuration from environment."""
        levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        for level in levels:
            with patch.dict(os.environ, {'ENVIST_LOG_LEVEL': level}):
                config_instance = EnvistConfig()
                assert config_instance.log_level == level
        
        with patch.dict(os.environ, {'ENVIST_LOG_LEVEL': 'debug'}):
            config_instance = EnvistConfig()
            assert config_instance.log_level == 'DEBUG'
    
    def test_log_format_configuration(self):
        """Test log format configuration from environment."""
        with patch.dict(os.environ, {'ENVIST_LOG_FORMAT': 'json'}):
            config_instance = EnvistConfig()
            assert config_instance.log_format == 'json'
        
        with patch.dict(os.environ, {'ENVIST_LOG_FORMAT': 'standard'}):
            config_instance = EnvistConfig()
            assert config_instance.log_format == 'standard'
    
    def test_log_file_configuration(self):
        """Test log file configuration from environment."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            log_file_path = tmp_file.name
        
        try:
            with patch.dict(os.environ, {'ENVIST_LOG_FILE': log_file_path}):
                config_instance = EnvistConfig()
                assert config_instance.log_file == log_file_path
        finally:
            # Force close any file handlers that might be holding the file
            logger_instance = EnvistLogger()
            for handler in logger_instance.get_handlers():
                if isinstance(handler, logging.FileHandler):
                    handler.close()
            Path(log_file_path).unlink(missing_ok=True)
    
    def test_rotating_logs_configuration(self):
        """Test rotating logs configuration from environment."""
        with patch.dict(os.environ, {'ENVIST_ROTATING_LOGS': 'true'}):
            config_instance = EnvistConfig()
            assert config_instance.rotating_logs is True
        
        with patch.dict(os.environ, {'ENVIST_ROTATING_LOGS': 'false'}):
            config_instance = EnvistConfig()
            assert config_instance.rotating_logs is False
        
        with patch.dict(os.environ, {'ENVIST_ROTATING_LOGS': 'invalid'}):
            config_instance = EnvistConfig()
            assert config_instance.rotating_logs is False
    
    @patch('envist.config.create_json_handler')
    def test_configure_logger_with_json_format(self, mock_json_handler):
        """Test logger configuration with JSON format."""
        mock_handler = MagicMock(spec=logging.Handler)
        mock_json_handler.return_value = mock_handler
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            log_file_path = tmp_file.name
        
        try:
            with patch.dict(os.environ, {
                'ENVIST_LOG_FILE': log_file_path,
                'ENVIST_LOG_FORMAT': 'json'
            }):
                config_instance = EnvistConfig()
                
                mock_json_handler.assert_called_once_with(log_file_path)
        finally:
            Path(log_file_path).unlink(missing_ok=True)
    
    @patch('envist.config.create_rotating_handler')
    def test_configure_logger_with_rotating_logs(self, mock_rotating_handler):
        """Test logger configuration with rotating logs."""
        mock_handler = MagicMock(spec=logging.Handler)
        mock_rotating_handler.return_value = mock_handler
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            log_file_path = tmp_file.name
        
        try:
            with patch.dict(os.environ, {
                'ENVIST_LOG_FILE': log_file_path,
                'ENVIST_ROTATING_LOGS': 'true'
            }):
                config_instance = EnvistConfig()
                
                mock_rotating_handler.assert_called_once_with(log_file_path)
        finally:
            Path(log_file_path).unlink(missing_ok=True)
    
    def test_configure_logger_with_standard_file_handler(self):
        """Test logger configuration with standard file handler."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            log_file_path = tmp_file.name
        
        try:
            with patch.dict(os.environ, {
                'ENVIST_LOG_FILE': log_file_path,
                'ENVIST_LOG_FORMAT': 'standard'
            }):
                config_instance = EnvistConfig()
                
                # Verify the logger was configured with file handler
                logger_instance = EnvistLogger()
                assert len(logger_instance.get_handlers()) >= 2  # Console + File
        finally:
            # Force close any file handlers that might be holding the file
            logger_instance = EnvistLogger()
            for handler in logger_instance.get_handlers():
                if isinstance(handler, logging.FileHandler):
                    handler.close()
            Path(log_file_path).unlink(missing_ok=True)
    
    def test_configure_logger_debug_mode(self):
        """Test logger configuration in debug mode."""
        with patch.dict(os.environ, {'ENVIST_DEBUG': 'true'}):
            config_instance = EnvistConfig()
            
            logger_instance = EnvistLogger()
            handlers = logger_instance.get_handlers()
            
            # Find console handler and check its level
            console_handlers = [h for h in handlers if isinstance(h, logging.StreamHandler)]
            assert len(console_handlers) >= 1
            
            # In debug mode, console handler should be at DEBUG level
            console_handler = console_handlers[0]
            assert console_handler.level == logging.DEBUG
    
    def test_configure_logger_production_mode(self):
        """Test logger configuration in production mode."""
        with patch.dict(os.environ, {'ENVIST_DEBUG': 'false'}):
            config_instance = EnvistConfig()
            
            logger_instance = EnvistLogger()
            handlers = logger_instance.get_handlers()
            
            # Find console handler and check its level
            console_handlers = [h for h in handlers if isinstance(h, logging.StreamHandler)]
            assert len(console_handlers) >= 1
            
            # In production mode, console handler should be at WARNING level
            console_handler = console_handlers[0]
            assert console_handler.level == logging.WARNING
    
    def test_add_custom_handler(self):
        """Test adding custom handlers to the configuration."""
        config_instance = EnvistConfig()
        
        # Create a custom handler
        custom_handler = logging.StreamHandler()
        custom_handler.setLevel(logging.ERROR)
        
        # Add the custom handler
        config_instance.add_custom_handler(custom_handler)
        
        # Verify it was added
        logger_instance = EnvistLogger()
        assert custom_handler in logger_instance.get_handlers()
    
    def test_logger_level_setting(self):
        """Test that logger level is properly set from configuration."""
        with patch.dict(os.environ, {'ENVIST_LOG_LEVEL': 'ERROR'}):
            config_instance = EnvistConfig()
            
            logger_instance = EnvistLogger()
            assert logger_instance.logger.level == logging.ERROR
    
    def test_global_config_instance(self):
        """Test that the global config instance is properly initialized."""
        # The global config instance should be available
        assert config is not None
        assert isinstance(config, EnvistConfig)
    
    def test_multiple_config_instances(self):
        """Test behavior with multiple config instances."""
        config1 = EnvistConfig()
        config2 = EnvistConfig()
        
        # Both should configure the same logger instance
        logger1 = EnvistLogger()
        logger2 = EnvistLogger()
        
        assert logger1 is logger2  # Should be singleton
    
    def test_config_with_all_environment_variables(self):
        """Test configuration with all environment variables set."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            log_file_path = tmp_file.name
        
        try:
            env_vars = {
                'ENVIST_DEBUG': 'true',
                'ENVIST_LOG_LEVEL': 'DEBUG',
                'ENVIST_LOG_FORMAT': 'json',
                'ENVIST_LOG_FILE': log_file_path,
                'ENVIST_ROTATING_LOGS': 'true'
            }
            
            with patch.dict(os.environ, env_vars):
                config_instance = EnvistConfig()
                
                assert config_instance.debug_mode is True
                assert config_instance.log_level == 'DEBUG'
                assert config_instance.log_format == 'json'
                assert config_instance.log_file == log_file_path
                assert config_instance.rotating_logs is True
        finally:
            # Force close any file handlers that might be holding the file
            logger_instance = EnvistLogger()
            for handler in logger_instance.get_handlers():
                if isinstance(handler, logging.FileHandler):
                    handler.close()
            Path(log_file_path).unlink(missing_ok=True)
    
    def test_config_with_no_environment_variables(self):
        """Test configuration with no environment variables set."""
        # Clear all relevant environment variables
        env_vars = ['ENVIST_DEBUG', 'ENVIST_LOG_LEVEL', 'ENVIST_LOG_FORMAT', 
                   'ENVIST_LOG_FILE', 'ENVIST_ROTATING_LOGS']
        
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]
        
        config_instance = EnvistConfig()
        
        assert config_instance.debug_mode is False
        assert config_instance.log_level == 'INFO'
        assert config_instance.log_format == 'standard'
        assert config_instance.log_file is None
        assert config_instance.rotating_logs is False
    
    def test_case_sensitivity_of_boolean_values(self):
        """Test case sensitivity of boolean environment variables."""
        test_cases = [
            ('True', True), ('TRUE', True), ('true', True), ('tRuE', True),
            ('False', False), ('FALSE', False), ('false', False), ('fAlSe', False),
            ('yes', False), ('no', False), ('1', False), ('0', False), ('', False)
        ]
        
        for env_value, expected in test_cases:
            with patch.dict(os.environ, {'ENVIST_DEBUG': env_value}):
                config_instance = EnvistConfig()
                assert config_instance.debug_mode == expected, f"Failed for value: '{env_value}'"

    def test_log_level_case_conversion(self):
        """Test that log levels are properly converted to uppercase."""
        test_cases = ['debug', 'info', 'warning', 'error', 'critical']
        
        for level in test_cases:
            with patch.dict(os.environ, {'ENVIST_LOG_LEVEL': level}):
                config_instance = EnvistConfig()
                assert config_instance.log_level == level.upper()

    def test_invalid_log_level_handling(self):
        """Test handling of invalid log levels."""
        with patch.dict(os.environ, {'ENVIST_LOG_LEVEL': 'INVALID_LEVEL'}):
            config_instance = EnvistConfig()
            # Should still accept the value (logger will handle validation)
            assert config_instance.log_level == 'INVALID_LEVEL'

    def test_empty_environment_variables(self):
        """Test behavior with empty environment variables."""
        with patch.dict(os.environ, {
            'ENVIST_DEBUG': '',
            'ENVIST_LOG_LEVEL': '',
            'ENVIST_LOG_FORMAT': '',
            'ENVIST_LOG_FILE': '',
            'ENVIST_ROTATING_LOGS': ''
        }):
            config_instance = EnvistConfig()
            
            assert config_instance.debug_mode is False  # Empty string != 'true'
            assert config_instance.log_level == ''  # Empty but assigned
            assert config_instance.log_format == ''  # Empty but assigned
            assert config_instance.log_file == ''  # Empty but assigned (not None)
            assert config_instance.rotating_logs is False  # Empty string != 'true'

    def test_whitespace_environment_variables(self):
        """Test behavior with whitespace-only environment variables."""
        with patch.dict(os.environ, {
            'ENVIST_DEBUG': '  ',
            'ENVIST_LOG_LEVEL': '\t',
            'ENVIST_LOG_FORMAT': '\n',
            'ENVIST_ROTATING_LOGS': '  '
        }):
            config_instance = EnvistConfig()
            
            assert config_instance.debug_mode is False  # Whitespace != 'true'
            assert config_instance.log_level == '\t'.upper()  # Whitespace preserved and uppercased
            assert config_instance.log_format == '\n'  # Preserved as-is
            assert config_instance.rotating_logs is False  # Whitespace != 'true'

    def test_boolean_edge_cases_rotating_logs(self):
        """Test edge cases for rotating logs boolean conversion."""
        test_cases = [
            ('True', True), ('TRUE', True), ('true', True),
            ('False', False), ('FALSE', False), ('false', False),
            ('anything_else', False), ('1', False), ('0', False),
            ('yes', False), ('no', False), ('on', False), ('off', False)
        ]
        
        for env_value, expected in test_cases:
            with patch.dict(os.environ, {'ENVIST_ROTATING_LOGS': env_value}):
                config_instance = EnvistConfig()
                assert config_instance.rotating_logs == expected, f"Failed for rotating_logs value: '{env_value}'"

    def test_file_handler_creation_without_log_file(self):
        """Test that no file handler is created when log_file is None."""
        with patch.dict(os.environ, {}, clear=True):  # Clear all env vars
            config_instance = EnvistConfig()
            
            # Should only have console handler, no file handler
            logger_instance = EnvistLogger()
            handlers = logger_instance.get_handlers()
            
            # All handlers should be console handlers (StreamHandler)
            for handler in handlers:
                assert isinstance(handler, logging.StreamHandler)
                assert not isinstance(handler, logging.FileHandler)

    def test_multiple_add_custom_handler_calls(self):
        """Test adding multiple custom handlers."""
        config_instance = EnvistConfig()
        
        # Create multiple custom handlers
        custom_handler1 = logging.StreamHandler()
        custom_handler1.setLevel(logging.ERROR)
        
        custom_handler2 = logging.StreamHandler()
        custom_handler2.setLevel(logging.CRITICAL)
        
        # Add both handlers
        config_instance.add_custom_handler(custom_handler1)
        config_instance.add_custom_handler(custom_handler2)
        
        # Verify both were added
        logger_instance = EnvistLogger()
        handlers = logger_instance.get_handlers()
        assert custom_handler1 in handlers
        assert custom_handler2 in handlers

    def test_global_config_immutability(self):
        """Test that the global config instance maintains its state."""
        # Get reference to global config
        global_config = config
        
        # Create a new instance
        new_config = EnvistConfig()
        
        # Global config should still be the same instance
        assert config is global_config
        # But it's not the same as the new instance
        assert config is not new_config

    @patch('envist.config.create_json_handler')
    @patch('envist.config.create_rotating_handler')
    def test_handler_precedence_json_over_rotating(self, mock_rotating, mock_json):
        """Test that JSON format takes precedence over rotating logs."""
        mock_json_handler = MagicMock(spec=logging.Handler)
        mock_rotating_handler = MagicMock(spec=logging.Handler)
        mock_json.return_value = mock_json_handler
        mock_rotating.return_value = mock_rotating_handler
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            log_file_path = tmp_file.name
        
        try:
            with patch.dict(os.environ, {
                'ENVIST_LOG_FILE': log_file_path,
                'ENVIST_LOG_FORMAT': 'json',
                'ENVIST_ROTATING_LOGS': 'true'  # Both enabled
            }):
                config_instance = EnvistConfig()
                
                # JSON handler should be called, not rotating
                mock_json.assert_called_once_with(log_file_path)
                mock_rotating.assert_not_called()
        finally:
            Path(log_file_path).unlink(missing_ok=True)
