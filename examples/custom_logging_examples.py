import logging
from pathlib import Path

from envist.logger import (
    EnvistLogger,
    configure_logger,
    create_default_handlers,
    create_file_handler,
    create_json_handler,
    create_rotating_handler,
    create_stream_handler,
    create_syslog_handler,
    logger,
)

# Example 1: Using custom handlers during initialization
custom_handlers = [
    create_stream_handler(level=logging.DEBUG),  # Set DEBUG level
    create_file_handler("app.log", level=logging.DEBUG),  # Set DEBUG level
    create_json_handler("app.json", level=logging.DEBUG),  # Set DEBUG level
    create_rotating_handler(
        "rotating.log", max_bytes=5 * 1024 * 1024, backup_count=5, level=logging.DEBUG
    ),
]

# Configure with custom handlers
custom_logger = EnvistLogger.configure(custom_handlers=custom_handlers, reset=True)
custom_logger.set_level("DEBUG")  # Important: Set logger level to DEBUG

# Add debug info
print(f"Number of handlers: {len(custom_logger.get_handlers())}")
print(f"Logger level: {custom_logger.logger.level}")
for i, handler in enumerate(custom_logger.get_handlers()):
    print(f"Handler {i}: {type(handler).__name__}, level: {handler.level}")

# Test the logging
print("Testing direct logging...")
custom_logger.debug("Debug message test")
custom_logger.info("Info message test")
custom_logger.warning("Warning message test")
custom_logger.error("Error message test")

# Force flush all handlers to ensure writes
for handler in custom_logger.get_handlers():
    if hasattr(handler, 'flush'):
        handler.flush()
    if hasattr(handler, 'close'):
        # Don't close stream handlers as it might close stdout
        if not isinstance(handler, logging.StreamHandler):
            handler.close()

print("Direct logging test complete. Check files...")

# Test file existence
for filename in ["app.log", "app.json", "rotating.log"]:
    if Path(filename).exists():
        print(f"✓ {filename} exists, size: {Path(filename).stat().st_size} bytes")
    else:
        print(f"✗ {filename} does not exist")

# Example 2: Test with actual Envist usage
print("\nTesting with Envist...")
import envist

# Create .env.example if it doesn't exist
env_file = Path(".env.example")
if not env_file.exists():
    env_file.write_text("name=John Doe\nage=30\ndebug=true\n")
    print("Created .env.example file")

# Create Envist instance - this should now generate logs
env = envist.Envist(".env.example")

# Get some variables - this should log access attempts
name = env.get("NAME")
age = env.get("AGE", cast=int)
missing = env.get("missing_var", default="fallback")

print(f"Name: {name}")
print(f"Age: {age}")
print(f"Missing: {missing}")

# Force flush again
for handler in custom_logger.get_handlers():
    handler.flush()

print("\nFinal check - log files should contain entries:")
for filename in ["app.log", "app.json", "rotating.log"]:
    if Path(filename).exists():
        size = Path(filename).stat().st_size
        print(f"✓ {filename}: {size} bytes")
        if size > 0:
            print(f"  Content preview: {Path(filename).read_text()[:100]}...")
    else:
        print(f"✗ {filename} not found")
