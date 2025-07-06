import logging

from envist.logger import EnvistLogger, create_file_handler, create_stream_handler


# Create a simple test
def test_logging():
    # Create handlers with DEBUG level
    handlers = [
        create_stream_handler(level=logging.DEBUG),
        create_file_handler("test.log", level=logging.DEBUG),
    ]

    # Configure logger
    logger = EnvistLogger.configure(custom_handlers=handlers)
    logger.set_level("DEBUG")  # Make sure we capture all messages

    # Test all log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    # Test custom methods
    logger.log_env_parse(".env", 5)
    logger.log_typecast("age", "25", "int", True)
    logger.log_variable_access("name", True, "str")


if __name__ == "__main__":
    test_logging()
    print("Check test.log file for output")
