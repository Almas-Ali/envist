import logging
import sys
from typing import Optional, List, Union
from pathlib import Path

class EnvistLogger:
    """Custom logger for Envist with environment-specific configurations."""
    
    _instance: Optional['EnvistLogger'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'EnvistLogger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, custom_handlers: Optional[List[logging.Handler]] = None):
        if self._initialized:
            return
            
        self.logger = logging.getLogger('envist')
        self.logger.setLevel(logging.INFO)
        
        # Store custom handlers for later use
        self.custom_handlers = custom_handlers or []
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
        
        self._initialized = True
    
    def _setup_handlers(self):
        """Setup console and file handlers with appropriate formatters."""
        
        # If custom handlers are provided, use them instead of default ones
        if self.custom_handlers:
            for handler in self.custom_handlers:
                self.logger.addHandler(handler)
            return
        
        # Default console handler for user-facing messages
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # Default file handler for detailed logging
        log_file = Path.home() / '.envist' / 'envist.log'
        log_file.parent.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def add_handler(self, handler: logging.Handler):
        """Add a custom handler to the logger."""
        self.logger.addHandler(handler)
    
    def remove_handler(self, handler: logging.Handler):
        """Remove a handler from the logger."""
        self.logger.removeHandler(handler)
    
    def clear_handlers(self):
        """Remove all handlers from the logger."""
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
    
    def replace_handlers(self, handlers: List[logging.Handler]):
        """Replace all current handlers with new ones."""
        self.clear_handlers()
        for handler in handlers:
            self.add_handler(handler)
    
    def get_handlers(self) -> List[logging.Handler]:
        """Get all current handlers."""
        return self.logger.handlers[:]
    
    def debug(self, message: str, **kwargs):
        """Log debug information for development."""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log general information."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warnings that users should be aware of."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log errors that occurred during processing."""
        self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical errors that may cause system failure."""
        self.logger.critical(message, extra=kwargs)
    
    def log_env_parse(self, file_path: str, variables_found: int):
        """Log environment file parsing results."""
        self.info(f"Parsed {file_path}: found {variables_found} variables")
    
    def log_typecast(self, key: str, value: str, target_type: str, success: bool):
        """Log typecasting operations."""
        if success:
            self.debug(f"Successfully cast '{key}' to {target_type}")
        else:
            self.error(f"Failed to cast '{key}' = '{value}' to {target_type}")
    
    def log_variable_expansion(self, original: str, expanded: str):
        """Log variable expansion operations."""
        if original != expanded:
            self.debug(f"Expanded '{original}' to '{expanded}'")
    
    def log_variable_access(self, key: str, found: bool, cast_type: str = None):
        """Log when variables are accessed."""
        if found:
            cast_info = f" (cast to {cast_type})" if cast_type else ""
            self.debug(f"Retrieved variable '{key}'{cast_info}")
        else:
            self.warning(f"Variable '{key}' not found")
    
    def set_level(self, level: str):
        """Set logging level dynamically."""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        if level.upper() in level_map:
            self.logger.setLevel(level_map[level.upper()])
    
    @classmethod
    def configure(cls, custom_handlers: Optional[List[logging.Handler]] = None, 
                  reset: bool = False) -> 'EnvistLogger':
        """Configure the logger with custom handlers.
        
        Args:
            custom_handlers: List of custom logging handlers
            reset: If True, reset the singleton instance
            
        Returns:
            EnvistLogger instance
        """
        if reset:
            # Clear existing instance completely
            if cls._instance is not None:
                cls._instance.clear_handlers()
            cls._instance = None
            cls._initialized = False
            
            # Also clear the underlying logger if it exists
            existing_logger = logging.getLogger('envist')
            for handler in existing_logger.handlers[:]:
                existing_logger.removeHandler(handler)
        
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance._initialized = False  # Force re-initialization
            cls._instance.__init__(custom_handlers)
        elif custom_handlers:
            # If instance exists but new handlers provided, replace them
            cls._instance.replace_handlers(custom_handlers)
        
        return cls._instance

# Factory functions for creating various handler types
def create_stream_handler(stream=None, level: int = logging.INFO) -> logging.Handler:
    """Create a stream handler (console output)."""
    handler = logging.StreamHandler(stream)
    handler.setLevel(level)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    return handler

def create_file_handler(log_file: Union[str, Path], level: int = logging.INFO) -> logging.Handler:
    """Create a basic file handler."""
    # Ensure directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    handler = logging.FileHandler(log_file)
    handler.setLevel(level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    handler.setFormatter(formatter)
    return handler

def create_json_handler(log_file: Union[str, Path], level: int = logging.INFO) -> logging.Handler:
    """Create a JSON formatter handler for structured logging."""
    import json
    from datetime import datetime
    
    # Ensure directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_entry = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno,
                'message': record.getMessage()
            }
            return json.dumps(log_entry)
    
    handler = logging.FileHandler(log_file)
    handler.setLevel(level)
    handler.setFormatter(JSONFormatter())
    return handler

def create_rotating_handler(log_file: Union[str, Path], max_bytes: int = 10*1024*1024, 
                          backup_count: int = 5, level: int = logging.INFO) -> logging.Handler:
    """Create a rotating file handler."""
    from logging.handlers import RotatingFileHandler
    
    # Ensure directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
    handler.setLevel(level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    handler.setFormatter(formatter)
    return handler

def create_syslog_handler(address: tuple = ('localhost', 514), 
                         level: int = logging.INFO) -> logging.Handler:
    """Create a syslog handler for system logging."""
    from logging.handlers import SysLogHandler
    
    handler = SysLogHandler(address=address)
    handler.setLevel(level)
    formatter = logging.Formatter(
        'envist[%(process)d]: %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    return handler

def create_default_handlers() -> List[logging.Handler]:
    """Create default handlers (console + file)."""
    return [
        create_stream_handler(level=logging.WARNING),
        create_file_handler(Path.home() / '.envist' / 'envist.log', level=logging.DEBUG)
    ]

def configure_logger(handlers: Optional[List[logging.Handler]] = None, 
                    level: str = 'INFO') -> EnvistLogger:
    """Configure the global logger with specified handlers and level."""
    logger_instance = EnvistLogger.configure(custom_handlers=handlers, reset=True)
    logger_instance.set_level(level)
    return logger_instance

# Global logger instance
logger = EnvistLogger()