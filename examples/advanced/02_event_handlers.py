import logging
from pathlib import Path

from envist.logger import (
    EnvistLogger,
    create_file_handler,
    create_json_handler,
    create_rotating_handler,
    create_stream_handler,
)

print("=== Testing each handler individually ===")

# Test each handler type individually
print("\n1. Testing create_file_handler:")
try:
    handler1 = create_file_handler("test1.log", level=logging.DEBUG)
    print(f"  Created: {type(handler1)}, level: {handler1.level}")
except Exception as e:
    print(f"  Error: {e}")

print("\n2. Testing create_json_handler:")
try:
    handler2 = create_json_handler("test2.json", level=logging.DEBUG)
    print(f"  Created: {type(handler2)}, level: {handler2.level}")
except Exception as e:
    print(f"  Error: {e}")

print("\n3. Testing create_rotating_handler:")
try:
    handler3 = create_rotating_handler("test3.log", level=logging.DEBUG)
    print(f"  Created: {type(handler3)}, level: {handler3.level}")
except Exception as e:
    print(f"  Error: {e}")

print("\n4. Testing create_stream_handler:")
try:
    handler4 = create_stream_handler(level=logging.DEBUG)
    print(f"  Created: {type(handler4)}, level: {handler4.level}")
except Exception as e:
    print(f"  Error: {e}")

print("\n=== Testing all handlers together ===")

# Create all handlers
all_handlers = [
    create_stream_handler(level=logging.DEBUG),
    create_file_handler("all_test.log", level=logging.DEBUG),
    create_json_handler("all_test.json", level=logging.DEBUG),
    create_rotating_handler("all_test_rotating.log", level=logging.DEBUG),
]

print(f"Created {len(all_handlers)} handlers")

# Configure logger
logger = EnvistLogger.configure(custom_handlers=all_handlers, reset=True)
logger.set_level("DEBUG")

print(f"Logger has {len(logger.get_handlers())} handlers")
for i, handler in enumerate(logger.get_handlers()):
    print(f"  Handler {i}: {type(handler).__name__}, level: {handler.level}")

# Test logging
print("\nTesting logging with all handlers...")
logger.debug("Debug test message")
logger.info("Info test message")
logger.warning("Warning test message")
logger.error("Error test message")

# Flush all handlers
for handler in logger.get_handlers():
    handler.flush()

print("\nChecking file sizes:")
for filename in ["all_test.log", "all_test.json", "all_test_rotating.log"]:
    if Path(filename).exists():
        size = Path(filename).stat().st_size
        print(f"  {filename}: {size} bytes")
        if size > 0:
            content = Path(filename).read_text()[:100]
            print(f"    Preview: {content}...")
    else:
        print(f"  {filename}: NOT FOUND")
