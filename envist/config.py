import os
import logging
from typing import List, Optional
from .logger import EnvistLogger, create_json_handler, create_rotating_handler

class EnvistConfig:
    """Configuration for Envist logging and behavior."""
    
    def __init__(self):
        self.debug_mode = os.getenv('ENVIST_DEBUG', 'false').lower() == 'true'
        self.log_level = os.getenv('ENVIST_LOG_LEVEL', 'INFO').upper()
        self.log_format = os.getenv('ENVIST_LOG_FORMAT', 'standard')  # standard, json
        self.log_file = os.getenv('ENVIST_LOG_FILE', None)
        self.rotating_logs = os.getenv('ENVIST_ROTATING_LOGS', 'false').lower() == 'true'
        
        # Configure logger based on environment
        self._configure_logger()
    
    def _configure_logger(self):
        """Configure logger based on environment variables."""
        handlers = []
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING if not self.debug_mode else logging.DEBUG)
        console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        handlers.append(console_handler)
        
        # File handler if specified
        if self.log_file:
            if self.log_format == 'json':
                file_handler = create_json_handler(self.log_file)
            elif self.rotating_logs:
                file_handler = create_rotating_handler(self.log_file)
            else:
                file_handler = logging.FileHandler(self.log_file)
                file_handler.setFormatter(logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                ))
            handlers.append(file_handler)
        
        # Configure the logger
        logger = EnvistLogger.configure(custom_handlers=handlers)
        logger.set_level(self.log_level)
    
    def add_custom_handler(self, handler: logging.Handler):
        """Add a custom handler to the current logger."""
        EnvistLogger().add_handler(handler)

config = EnvistConfig()