# 🌟 Envist

<div align="center">

<a href="https://pypi.org/project/envist" title="Envist PyPI Project">
<img src="https://github.com/Almas-Ali/envist/blob/master/logo.png?raw=true" alt="Envist Logo" width="200"/>
</a>

**The most powerful environment variable manager for Python** 🚀

[![PyPI version](https://badge.fury.io/py/envist.svg)](https://pypi.org/project/envist)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/envist)](https://pypi.org/project/envist)
[![PyPI - License](https://img.shields.io/pypi/l/envist)](https://pypi.org/project/envist)
[![Hits](https://hits.sh/github.com/Almas-Ali/envist.svg?label=Total%20hits&logo=dotenv)](https://github.com/Almas-Ali/envist "Total hits")
[![Code Coverage](https://img.shields.io/codecov/c/github/Almas-Ali/envist)](https://codecov.io/gh/Almas-Ali/envist)
[![Downloads](https://pepy.tech/badge/envist)](https://pepy.tech/project/envist)

*Environment variables have never been this smart!* 

Transform your `.env` files from simple key-value pairs into **type-safe, intelligent configuration management** with automatic typecasting, variable expansion, and zero-hassle setup.

Created with ❤️ by [**Md. Almas Ali**](https://github.com/Almas-Ali)

</div>

---

## 📋 Table of Contents

- [🎯 Why Envist?](#-why-envist)
- [✨ Key Features](#-key-features)
- [⚡ Quick Start](#-quick-start)
- [📦 Installation](#-installation)
- [🎓 Complete Guide](#-complete-guide)
  - [Basic Usage](#basic-usage)
  - [Type Casting Magic](#type-casting-magic)
  - [Variable Expansion](#variable-expansion)
  - [Advanced Operations](#advanced-operations)
- [📚 API Reference](#-api-reference)
- [🏷️ Supported Data Types](#️-supported-data-types)
- [🔧 Configuration](#-configuration)
- [🛠️ Exception Handling](#exception-handling)
- [📊 Logging](#-logging)
- [🎯 Examples](#-examples)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🎯 Why Envist?

**Stop wrestling with environment variables!** 

Traditional `.env` files are just strings. What if your environment variables could be **intelligent**? What if they could know their own types, expand references to other variables, and validate themselves?

**Envist makes this possible:**

```env
# Traditional .env (boring 😴)
PORT=8080
DEBUG=True
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb

# Envist .env (intelligent 🧠)
PORT <int> = 8080
DEBUG <bool> = True
HOST <str> = localhost
DATABASE_URL <str> = postgresql://user:pass@${HOST}:5432/mydb
ALLOWED_HOSTS <list> = localhost, 127.0.0.1, 0.0.0.0
CONFIG <json> = {"timeout": 30, "retries": 3}
```

**The result?** Type-safe, self-documenting configuration that prevents bugs before they happen!

## ✨ Key Features

🎯 **In-File Type Casting** - Define variable types directly in your `.env` file  
🔗 **Variable Expansion** - Reference other variables with `${variable}` syntax  
🛡️ **Type Safety** - Automatic validation and conversion to Python types  
📊 **Rich Data Types** - Support for lists, dicts, JSON, CSV, and more  
🔄 **Backward Compatible** - Works with existing `.env` files  
⚡ **Zero Dependencies** - Lightweight and fast  
🔧 **Full CRUD Operations** - Get, set, unset, and save variables  
📝 **Built-in Logging** - Comprehensive debugging capabilities  

---

## ⚡ Quick Start

**1. Install Envist**
```bash
pip install envist
```

**2. Create your smart `.env` file**
```env
# .env
APP_NAME <str> = My Awesome App
PORT <int> = 8080
DEBUG <bool> = True
ALLOWED_HOSTS <list> = localhost, 127.0.0.1
DATABASE_CONFIG <json> = {"host": "localhost", "port": 5432}
BASE_URL <str> = http://localhost:${PORT}
```

**3. Use it in your Python code**
```python
from envist import Envist

env = Envist()

# ✨ Automatic type casting!
app_name = env.get('APP_NAME')      # Returns: 'My Awesome App' (str)
port = env.get('PORT')              # Returns: 8080 (int)
debug = env.get('DEBUG')            # Returns: True (bool)
hosts = env.get('ALLOWED_HOSTS')    # Returns: ['localhost', '127.0.0.1'] (list)
db_config = env.get('DATABASE_CONFIG')  # Returns: {'host': 'localhost', 'port': 5432} (dict)
base_url = env.get('BASE_URL')      # Returns: 'http://localhost:8080' (str)

print(f"🚀 Starting {app_name} on port {port}")
print(f"🐛 Debug mode: {debug}")
print(f"🔗 Base URL: {base_url}")
```

**That's it!** No more manual type conversion, no more configuration headaches! 🎉

---

## 📦 Installation

### Using pip (Recommended)
```bash
pip install envist
```

### Using conda
```bash
conda install -c conda-forge envist
```

### Using poetry
```bash
poetry add envist
```

### From source
```bash
git clone https://github.com/Almas-Ali/envist.git
cd envist
pip install -e .
```

**Requirements:** Python 3.7+ (No external dependencies!)

---

## 🎓 Complete Guide

### Basic Usage

#### Creating an Envist Instance

```python
from envist import Envist

# Use default .env file with auto-casting enabled
env = Envist()

# Use custom file path
env = Envist(path="config/.env")

# Disable auto-casting (values remain as strings unless explicitly cast)
env = Envist(auto_cast=False)

# Accept empty values (variables declared without values)
env = Envist(accept_empty=True)

# Full configuration
env = Envist(
    path="config/production.env",
    accept_empty=True,
    auto_cast=True
)
```

#### Getting Variables

```python
# Get with automatic type casting (from .env type annotations)
value = env.get('VARIABLE_NAME')

# Get with default value
value = env.get('VARIABLE_NAME', default='fallback_value')

# Get with explicit type casting (overrides .env annotations)
value = env.get('VARIABLE_NAME', cast=int)

# Get all variables
all_vars = env.get_all()
```

### Type Casting Magic

**🎯 The game-changer:** Define types directly in your `.env` file!

#### Traditional .env (Before Envist)
```env
DATABASE_PORT=5432
DEBUG=true
ALLOWED_IPS=192.168.1.1,192.168.1.2,localhost
```

```python
import os
# 😞 Everything is a string, manual conversion needed
port = int(os.getenv('DATABASE_PORT'))  # Manual casting
debug = os.getenv('DEBUG').lower() == 'true'  # Manual parsing
ips = os.getenv('ALLOWED_IPS').split(',')  # Manual splitting
```

#### Smart .env (With Envist)
```env
DATABASE_PORT <int> = 5432
DEBUG <bool> = true
ALLOWED_IPS <list> = 192.168.1.1, 192.168.1.2, localhost
```

```python
from envist import Envist
env = Envist()

# ✨ Automatic type casting!
port = env.get('DATABASE_PORT')    # Already an int!
debug = env.get('DEBUG')           # Already a bool!
ips = env.get('ALLOWED_IPS')       # Already a list!
```

#### Supported Type Annotations

| Syntax | Python Type | Example |
|--------|-------------|---------|
| `<str>` | `str` | `NAME <str> = John Doe` |
| `<int>` | `int` | `PORT <int> = 8080` |
| `<float>` | `float` | `PI <float> = 3.14159` |
| `<bool>` | `bool` | `DEBUG <bool> = True` |
| `<list>` | `list` | `HOSTS <list> = web1, web2, web3` |
| `<tuple>` | `tuple` | `COORDS <tuple> = 10, 20, 30` |
| `<set>` | `set` | `TAGS <set> = python, web, api` |
| `<dict>` | `dict` | `CONFIG <dict> = key1:value1, key2:value2` |
| `<json>` | `dict` | `SETTINGS <json> = {"timeout": 30}` |
| `<csv>` | `list` | `DATA <csv> = name,age,email` |

### Variable Expansion

**🔗 Reference other variables like a pro!**

```env
# .env - Smart variable references
HOST <str> = localhost
PORT <int> = 8080
PROTOCOL <str> = https

# Variable expansion in action
API_BASE <str> = ${PROTOCOL}://${HOST}:${PORT}/api
DATABASE_URL <str> = postgresql://user:pass@${HOST}:5432/mydb
REDIS_URL <str> = redis://${HOST}:6379

# Nested expansion
APP_URL <str> = ${API_BASE}/v1
HEALTH_CHECK <str> = ${APP_URL}/health
```

```python
from envist import Envist
env = Envist()

print(env.get('API_BASE'))      # https://localhost:8080/api
print(env.get('DATABASE_URL'))  # postgresql://user:pass@localhost:5432/mydb
print(env.get('HEALTH_CHECK'))  # https://localhost:8080/api/v1/health
```

### Advanced Operations

#### Setting Variables

```python
# Set single variable
env.set('NEW_VARIABLE', 'some_value')

# Set multiple variables
env.set_all({
    'DATABASE_HOST': 'localhost',
    'DATABASE_PORT': 5432,
    'DATABASE_NAME': 'myapp'
})

# Variables are immediately available
db_host = env.get('DATABASE_HOST')  # 'localhost'
```

#### Removing Variables

```python
# Remove single variable
env.unset('TEMPORARY_VAR')

# Remove multiple variables
env.unset_all(['VAR1', 'VAR2', 'VAR3'])

# Remove all variables (be careful!)
env.unset_all()
```

#### Saving Changes

```python
# Save to the same file
env.save()

# Save with formatting options
env.save(
    pretty=True,     # Add spacing for readability
    sort_keys=True,   # Sort variables alphabetically
    example_file=False  # Save an .env.example file with type annotations
)
```

**Example of saved output:**
```env
# Automatically formatted and sorted
DATABASE_HOST <str> = localhost
DATABASE_PORT <int> = 5432
DEBUG <bool> = True
```

---

## 📚 API Reference

### Class: `Envist`

#### Constructor

```python
Envist(path: str = ".env", accept_empty: bool = False, auto_cast: bool = True)
```

**Parameters:**
- `path` (str, optional): Path to the environment file. Defaults to ".env".
- `accept_empty` (bool, optional): Accept keys declared without values. Defaults to False.
- `auto_cast` (bool, optional): Automatically cast values when type annotations are present. If False, values remain as strings. Defaults to True.

#### Core Methods

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `get(key, *, default=None, cast=None)` | Get a variable with optional type casting | `key`: Variable name<br>`default`: Fallback value<br>`cast`: Type to cast to (overrides auto_cast) | `Any` |
| `get_all()` | Get all environment variables | None | `dict` |
| `set(key, value, cast=None)` | Set a single variable | `key`: Variable name<br>`value`: Variable value<br>`cast`: Optional type casting hint | `Any` |
| `set_all(data)` | Set multiple variables | `data`: Dictionary of key-value pairs | `None` |
| `unset(key)` | Remove a single variable | `key`: Variable name | `None` |
| `unset_all(data_list=None)` | Remove multiple or all variables | `data_list`: List of keys (if None, removes all) | `None` |
| `save(pretty=False, sort_keys=False, example_file=False)` | Save changes to file | `pretty`: Format with spaces<br>`sort_keys`: Sort alphabetically<br>`example_file`: Create .env.example file | `None` |
| `reload()` | Reload environment variables from file | None | `None` |

#### Dictionary-Style Access

Envist supports dictionary-style operations:

```python
env = Envist()

# Dictionary-style access
value = env['DATABASE_URL']        # Same as env.get('DATABASE_URL')
env['NEW_VAR'] = 'value'          # Same as env.set('NEW_VAR', 'value')
del env['OLD_VAR']                # Same as env.unset('OLD_VAR')

# Check if variable exists
if 'API_KEY' in env:
    print("API_KEY is configured")

# Get number of variables
print(f"Total variables: {len(env)}")

# Iterate over keys
for key in env:
    print(f"{key}: {env[key]}")
```

#### Properties

| Property | Description | Type |
|----------|-------------|------|
| `path` | Path to the environment file | `str` |

#### Special Methods

| Method | Description | Example |
|--------|-------------|---------|
| `__getitem__()` | Dictionary-style access | `env['KEY']` |
| `__setitem__()` | Dictionary-style assignment | `env['KEY'] = 'value'` |
| `__delitem__()` | Dictionary-style deletion | `del env['KEY']` |
| `__contains__()` | Check if key exists | `'KEY' in env` |
| `__len__()` | Get number of variables | `len(env)` |
| `__iter__()` | Iterate over keys | `for key in env:` |
| `__repr__()` | String representation | `<Envist path=".env">` |

---

## 🏷️ Supported Data Types

Envist supports a rich set of data types with intelligent parsing, including **nested type support**:

### Simple Types

| Type | Syntax | Description | Example | Python Output |
|------|--------|-------------|---------|---------------|
| **String** | `<str>` | Text values | `NAME <str> = John Doe` | `'John Doe'` |
| **Integer** | `<int>` | Whole numbers | `PORT <int> = 8080` | `8080` |
| **Float** | `<float>` | Decimal numbers | `PI <float> = 3.14159` | `3.14159` |
| **Boolean** | `<bool>` | True/False values | `DEBUG <bool> = True` | `True` |
| **List** | `<list>` or `<array>` | Comma-separated values | `HOSTS <list> = web1, web2, web3` | `['web1', 'web2', 'web3']` |
| **Tuple** | `<tuple>` | Immutable sequences | `COORDS <tuple> = 10, 20, 30` | `(10, 20, 30)` |
| **Set** | `<set>` | Unique values only | `TAGS <set> = python, web, python` | `{'python', 'web'}` |
| **Dictionary** | `<dict>` | Key-value pairs | `CONFIG <dict> = key1:value1, key2:value2` | `{'key1': 'value1', 'key2': 'value2'}` |
| **JSON** | `<json>` | JSON objects | `SETTINGS <json> = {"timeout": 30, "retries": 3}` | `{'timeout': 30, 'retries': 3}` |
| **CSV** | `<csv>` or `<comma_separated>` | CSV-style data | `DATA <csv> = name,age,email` | `['name', 'age', 'email']` |

### 🚀 **New: Nested Type Support**

Envist now supports nested type annotations for complex data structures:

#### Typed Collections

```env
# List of integers
PORTS <list<int>> = 8080, 9000, 3000

# Set of floats  
PRICES <set<float>> = 19.99, 29.95, 19.99

# Tuple of strings
SERVERS <tuple<str>> = web1.example.com, web2.example.com

# List of boolean values
FEATURES <list<bool>> = true, false, true
```

```python
from envist import Envist
env = Envist()

ports = env.get('PORTS')        # [8080, 9000, 3000] (list of ints)
prices = env.get('PRICES')      # {19.99, 29.95} (set of floats)  
servers = env.get('SERVERS')    # ('web1.example.com', 'web2.example.com') (tuple)
features = env.get('FEATURES')  # [True, False, True] (list of bools)
```

#### Typed Dictionaries

```env
# Dictionary with string keys and integer values
PORT_MAP <dict<str, int>> = web:8080, api:9000, db:5432

# Dictionary with string keys and float values
WEIGHTS <dict<str, float>> = cpu:0.7, memory:0.2, disk:0.1

# Dictionary with string keys and boolean values
FEATURES <dict<str, bool>> = auth:true, cache:false, debug:true
```

```python
port_map = env.get('PORT_MAP')   # {'web': 8080, 'api': 9000, 'db': 5432}
weights = env.get('WEIGHTS')     # {'cpu': 0.7, 'memory': 0.2, 'disk': 0.1}
features = env.get('FEATURES')   # {'auth': True, 'cache': False, 'debug': True}
```

#### Complex Nested Types

```env
# Dictionary with string keys and list of integers as values
GROUPS <dict<str, list<int>>> = admins:1,2,3, users:4,5,6, guests:7,8,9

# List of dictionaries (using JSON syntax for complex structures)
ENDPOINTS <json> = [
  {"name": "api", "port": 8080, "ssl": true},
  {"name": "web", "port": 3000, "ssl": false}
]
```

### 🎯 Smart Type Detection

**Boolean values** are parsed intelligently:
```env
# All of these become Python True
ENABLED <bool> = True
ENABLED <bool> = true  
ENABLED <bool> = TRUE
ENABLED <bool> = 1
ENABLED <bool> = yes
ENABLED <bool> = on

# All of these become Python False  
DISABLED <bool> = False
DISABLED <bool> = false
DISABLED <bool> = FALSE
DISABLED <bool> = 0
DISABLED <bool> = no
DISABLED <bool> = off
```

**Lists and tuples** handle whitespace gracefully:
```env
# These are equivalent
HOSTS <list> = web1, web2, web3
HOSTS <list> = web1,web2,web3  
HOSTS <list> = web1 , web2 , web3
```

**JSON values** support complex structures:
```env
# Simple object
CONFIG <json> = {"debug": true, "timeout": 30}

# Nested structures
DATABASE <json> = {
  "host": "localhost",
  "credentials": {"user": "admin", "pass": "secret"},
  "pools": [10, 20, 30]
}
```

### 🔄 Backward Compatibility

**No type annotations?** No problem! Envist works with traditional `.env` files:

```env
# Traditional .env file (no type annotations)
DATABASE_URL=postgresql://localhost:5432/mydb
DEBUG=true
PORT=8080
```

```python
from envist import Envist
env = Envist()

# Manual casting still works
url = env.get('DATABASE_URL', cast=str)
debug = env.get('DEBUG', cast=bool) 
port = env.get('PORT', cast=int)

# Or with nested types
items = env.get('ITEMS', cast='list<int>')
```

### ⚙️ Advanced Type Casting Options

You can control type casting behavior:

```python
# Auto-cast enabled (default) - types are cast automatically from annotations
env = Envist(auto_cast=True)

# Auto-cast disabled - all values remain as strings unless explicitly cast
env = Envist(auto_cast=False)
value = env.get('PORT', cast=int)  # Manual casting required

# Accept empty values
env = Envist(accept_empty=True)
empty_val = env.get('OPTIONAL_SETTING')  # Returns None if empty
```

> **💡 Pro Tip:** Mix and match! You can gradually migrate your `.env` files by adding type annotations to new variables while keeping existing ones unchanged.

---

## 🔧 Configuration

### Custom File Paths

```python
# Development environment
dev_env = Envist(path="environments/development.env")

# Production environment  
prod_env = Envist(path="environments/production.env")

# Testing environment
test_env = Envist(path="tests/fixtures/test.env")
```

### Environment-Specific Loading

```python
import os
from envist import Envist

# Load environment-specific configuration
environment = os.getenv('ENVIRONMENT', 'development')
env_file = f"config/{environment}.env"
env = Envist(path=env_file)

print(f"🌍 Loaded {environment} configuration from {env_file}")
```

### Multiple Environment Files

```python
from envist import Envist

# Base configuration
base_env = Envist(path="config/base.env")

# Environment-specific overrides
local_env = Envist(path="config/local.env")

# Merge configurations (local overrides base)
config = {**base_env.get_all(), **local_env.get_all()}
```

---

### Exception Handling

Envist provides specific exception types for different error scenarios:

```python
from envist import (
    Envist, 
    EnvistError,           # Base exception
    EnvistCastError,       # Type casting failures
    EnvistParseError,      # File parsing errors
    EnvistValueError,      # Value not found errors
    EnvistTypeError,       # Type validation errors
    FileNotFoundError      # File not found errors
)

try:
    env = Envist(path="nonexistent.env")
except FileNotFoundError as e:
    print(f"Environment file not found: {e}")

try:
    value = env.get('PORT', cast='invalid_type')
except EnvistCastError as e:
    print(f"Type casting failed: {e}")

try:
    env.unset('NONEXISTENT_VAR')
except EnvistValueError as e:
    print(f"Variable not found: {e}")
```

---

## 📊 Logging

Envist provides comprehensive logging capabilities with flexible configuration options to help you debug configuration issues and monitor environment variable usage.

### Basic Logging Setup

```python
import logging
from envist import Envist

# Enable basic logging to see Envist operations
logging.basicConfig(level=logging.INFO)

env = Envist()
# Now you'll see info-level logs about file loading and variable parsing
```

### Advanced Logging Configuration

Envist uses a sophisticated logging system with multiple handler types and customizable configurations:

```python
from envist.logger import EnvistLogger, configure_logger, create_stream_handler, create_file_handler

# Configure with custom handlers
logger = configure_logger(
    handlers=[
        create_stream_handler(level=logging.DEBUG),  # Console output
        create_file_handler("envist.log", level=logging.INFO)  # File output
    ],
    level="DEBUG"
)

# Now create Envist instance - it will use the configured logger
env = Envist()
```

### Log Levels and Information

| Level | Information Logged | Use Case |
|-------|-------------------|----------|
| `DEBUG` | Detailed parsing, type casting, variable resolution | Development & troubleshooting |
| `INFO` | File loading, variable counts, set/unset operations | General monitoring |
| `WARNING` | Missing variables, type casting issues | Production monitoring |
| `ERROR` | File read errors, parsing failures | Error tracking |
| `CRITICAL` | System-level failures | Critical error alerts |

### Built-in Logging Methods

The Envist logger provides specialized logging methods:

```python
from envist.logger import logger

# Environment parsing
logger.log_env_parse("/path/to/.env", 15)  # File path and variable count

# Type casting operations
logger.log_typecast("PORT", "8080", "int", True)  # Key, value, type, success

# Variable expansion
logger.log_variable_expansion("${HOST}:${PORT}", "localhost:8080")

# Variable access
logger.log_variable_access("DATABASE_URL", True, "str")  # Key, found, cast_type
```

### Handler Types

Envist supports multiple logging handler types for different use cases:

#### 1. Console/Stream Handler
```python
from envist.logger import create_stream_handler
import sys

# Console output (default to stdout)
console_handler = create_stream_handler(level=logging.INFO)

# Error output to stderr
error_handler = create_stream_handler(stream=sys.stderr, level=logging.ERROR)
```

#### 2. File Handler
```python
from envist.logger import create_file_handler

# Basic file logging
file_handler = create_file_handler("app.log", level=logging.DEBUG)

# Automatic directory creation
file_handler = create_file_handler("logs/envist/app.log", level=logging.INFO)
```

#### 3. JSON Handler (Structured Logging)
```python
from envist.logger import create_json_handler

# JSON formatted logs for log aggregation systems
json_handler = create_json_handler("app.json", level=logging.INFO)
```

JSON output format:
```json
{
  "timestamp": "2025-01-15T10:30:45.123456",
  "level": "INFO",
  "logger": "envist",
  "module": "parser",
  "function": "_load_env",
  "line": 127,
  "message": "Parsed .env: found 12 variables"
}
```

#### 4. Rotating File Handler
```python
from envist.logger import create_rotating_handler

# Rotate when file reaches 10MB, keep 5 backups
rotating_handler = create_rotating_handler(
    "app.log",
    max_bytes=10 * 1024 * 1024,  # 10MB
    backup_count=5,
    level=logging.INFO
)
```

#### 5. Syslog Handler
```python
from envist.logger import create_syslog_handler

# Send logs to system logger
syslog_handler = create_syslog_handler(
    address=("localhost", 514),
    level=logging.WARNING
)
```

### Example Log Output

**Console Output (INFO level):**
```
INFO: Initializing Envist with file: .env
INFO: Parsed .env: found 12 variables
INFO: Set environment variable 'NEW_VAR' = 'test_value'
WARNING: Variable 'OPTIONAL_VAR' not found
```

**File Output (DEBUG level):**
```
2025-01-15 10:30:45,123 - envist - DEBUG - _load_env:127 - Loading environment file: .env
2025-01-15 10:30:45,124 - envist - DEBUG - _apply_type_casting:234 - Successfully cast 'PORT' to int
2025-01-15 10:30:45,125 - envist - DEBUG - _resolve_variable:156 - Expanded '${HOST}:${PORT}' to 'localhost:8080'
2025-01-15 10:30:45,126 - envist - INFO - _load_env:145 - Parsed .env: found 12 variables
```

### Production Logging Setup

For production environments, use a comprehensive logging configuration:

```python
import logging
from pathlib import Path
from envist.logger import (
    EnvistLogger, 
    create_stream_handler, 
    create_rotating_handler,
    create_json_handler
)

# Production logging setup
def setup_production_logging():
    log_dir = Path("/var/log/myapp")
    log_dir.mkdir(exist_ok=True)
    
    handlers = [
        # Console: only warnings and errors
        create_stream_handler(level=logging.WARNING),
        
        # Rotating file: all info and above
        create_rotating_handler(
            log_dir / "app.log",
            max_bytes=50 * 1024 * 1024,  # 50MB
            backup_count=10,
            level=logging.INFO
        ),
        
        # JSON for log aggregation (ELK, Splunk, etc.)
        create_json_handler(
            log_dir / "app.json",
            level=logging.INFO
        )
    ]
    
    return EnvistLogger.configure(custom_handlers=handlers, reset=True)

# Use in production
logger = setup_production_logging()
logger.set_level("INFO")

# Your app code
env = Envist()
```

### Development Logging Setup

For development, you might want more verbose logging:

```python
from envist.logger import configure_logger, create_stream_handler, create_file_handler

# Development: verbose console + debug file
dev_logger = configure_logger(
    handlers=[
        create_stream_handler(level=logging.DEBUG),      # All to console
        create_file_handler("debug.log", level=logging.DEBUG)  # All to file
    ],
    level="DEBUG"
)

env = Envist()
```

### Custom Logger Integration

You can integrate Envist logging with your existing application logger:

```python
import logging
from envist.logger import EnvistLogger

# Get your existing application logger
app_logger = logging.getLogger("myapp")

# Create a custom handler that forwards to your app logger
class AppLoggerHandler(logging.Handler):
    def __init__(self, app_logger):
        super().__init__()
        self.app_logger = app_logger
    
    def emit(self, record):
        # Forward Envist logs to your app logger with prefix
        msg = f"[ENVIST] {self.format(record)}"
        self.app_logger.log(record.levelno, msg)

# Configure Envist to use your app logger
custom_handler = AppLoggerHandler(app_logger)
envist_logger = EnvistLogger.configure(custom_handlers=[custom_handler])

env = Envist()
```

### Dynamic Logging Control

You can change logging levels and handlers at runtime:

```python
from envist.logger import logger, create_file_handler

# Change log level
logger.set_level("DEBUG")

# Add a new handler
debug_handler = create_file_handler("debug.log", level=logging.DEBUG)
logger.add_handler(debug_handler)

# Remove a handler
logger.remove_handler(debug_handler)

# Replace all handlers
new_handlers = [create_stream_handler(level=logging.INFO)]
logger.replace_handlers(new_handlers)
```

> **🔍 Debugging Tips:**
> - Use `DEBUG` level when troubleshooting type casting issues
> - Use `INFO` level for monitoring environment loading in production
> - Use JSON handlers for centralized logging systems
> - Use rotating handlers to prevent log files from growing too large

---

## 🎯 Examples

### 🌐 Web Application Configuration

```env
# config/web.env
APP_NAME <str> = My Web App
APP_VERSION <str> = 1.0.0
HOST <str> = localhost
PORT <int> = 8080
DEBUG <bool> = True

# Database
DB_HOST <str> = localhost
DB_PORT <int> = 5432
DB_NAME <str> = webapp
DB_URL <str> = postgresql://user:pass@${DB_HOST}:${DB_PORT}/${DB_NAME}

# Security
SECRET_KEY <str> = your-secret-key-here
ALLOWED_HOSTS <list> = localhost, 127.0.0.1, 0.0.0.0
CORS_ORIGINS <list> = http://localhost:3000, http://localhost:8080

# External Services
REDIS_URL <str> = redis://${HOST}:6379
EMAIL_CONFIG <json> = {"smtp_server": "smtp.gmail.com", "port": 587, "use_tls": true}

# Feature Flags
ENABLE_ANALYTICS <bool> = True
ENABLE_CACHING <bool> = True
MAINTENANCE_MODE <bool> = False
```

```python
from envist import Envist

# Load configuration
env = Envist(path="config/web.env")

# Flask/FastAPI application setup
app_config = {
    'name': env.get('APP_NAME'),
    'version': env.get('APP_VERSION'),
    'host': env.get('HOST'),
    'port': env.get('PORT'),
    'debug': env.get('DEBUG'),
    'secret_key': env.get('SECRET_KEY'),
    'database_url': env.get('DB_URL'),
    'redis_url': env.get('REDIS_URL'),
    'allowed_hosts': env.get('ALLOWED_HOSTS'),
    'cors_origins': env.get('CORS_ORIGINS'),
    'email_config': env.get('EMAIL_CONFIG'),
}

print(f"🚀 Starting {app_config['name']} v{app_config['version']}")
print(f"🌐 Server: {app_config['host']}:{app_config['port']}")
print(f"🔗 Database: {app_config['database_url']}")
print(f"📧 Email: {app_config['email_config']['smtp_server']}")
```

### 🔬 Data Science Project

```env
# config/ml.env
PROJECT_NAME <str> = ML Pipeline
DATA_PATH <str> = ./data
MODEL_PATH <str> = ./models
OUTPUT_PATH <str> = ./outputs

# Data Processing
BATCH_SIZE <int> = 32
MAX_WORKERS <int> = 4
SAMPLE_RATE <float> = 0.1
RANDOM_SEED <int> = 42

# Model Configuration
MODEL_PARAMS <json> = {
  "learning_rate": 0.001,
  "epochs": 100,
  "dropout": 0.2,
  "hidden_layers": [128, 64, 32]
}

# Feature Engineering
SELECTED_FEATURES <list> = age, income, education, experience
CATEGORICAL_FEATURES <list> = gender, department, city
NUMERICAL_FEATURES <list> = age, income, experience, score

# Paths with expansion
TRAIN_DATA <str> = ${DATA_PATH}/train.csv
TEST_DATA <str> = ${DATA_PATH}/test.csv
MODEL_OUTPUT <str> = ${MODEL_PATH}/${PROJECT_NAME}_model.pkl
```

```python
from envist import Envist
import pandas as pd

# Load ML configuration
env = Envist(path="config/ml.env")

# Training pipeline setup
config = {
    'project_name': env.get('PROJECT_NAME'),
    'batch_size': env.get('BATCH_SIZE'),
    'max_workers': env.get('MAX_WORKERS'),
    'sample_rate': env.get('SAMPLE_RATE'),
    'random_seed': env.get('RANDOM_SEED'),
    'model_params': env.get('MODEL_PARAMS'),
    'selected_features': env.get('SELECTED_FEATURES'),
    'categorical_features': env.get('CATEGORICAL_FEATURES'),
    'numerical_features': env.get('NUMERICAL_FEATURES'),
    'train_data_path': env.get('TRAIN_DATA'),
    'test_data_path': env.get('TEST_DATA'),
    'model_output_path': env.get('MODEL_OUTPUT'),
}

print(f"🔬 {config['project_name']} Configuration:")
print(f"📊 Batch size: {config['batch_size']}")
print(f"🎯 Model params: {config['model_params']}")
print(f"📁 Training data: {config['train_data_path']}")
```

### 🐳 Docker & DevOps

```env
# config/docker.env
ENVIRONMENT <str> = production
SERVICE_NAME <str> = my-api
VERSION <str> = 1.2.3

# Container Configuration
CONTAINER_PORT <int> = 8080
HOST_PORT <int> = 80
MEMORY_LIMIT <str> = 512m
CPU_LIMIT <float> = 0.5

# Registry
REGISTRY_URL <str> = your-registry.com
IMAGE_NAME <str> = ${REGISTRY_URL}/${SERVICE_NAME}:${VERSION}

# Health Check
HEALTH_CHECK_INTERVAL <int> = 30
HEALTH_CHECK_TIMEOUT <int> = 10
HEALTH_CHECK_RETRIES <int> = 3
HEALTH_CHECK_URL <str> = http://localhost:${CONTAINER_PORT}/health

# Environment Variables for Container
CONTAINER_ENV <json> = {
  "NODE_ENV": "production",
  "LOG_LEVEL": "info",
  "DATABASE_URL": "postgresql://prod-db:5432/app"
}
```

```python
from envist import Envist

# Load Docker configuration
env = Envist(path="config/docker.env")

# Generate Docker run command
def generate_docker_command():
    image = env.get('IMAGE_NAME')
    host_port = env.get('HOST_PORT')
    container_port = env.get('CONTAINER_PORT')
    memory = env.get('MEMORY_LIMIT')
    cpu = env.get('CPU_LIMIT')
    container_env = env.get('CONTAINER_ENV')
    
    cmd_parts = [
        "docker run -d",
        f"--name {env.get('SERVICE_NAME')}",
        f"-p {host_port}:{container_port}",
        f"--memory={memory}",
        f"--cpus={cpu}"
    ]
    
    # Add environment variables
    for key, value in container_env.items():
        cmd_parts.append(f"-e {key}={value}")
    
    cmd_parts.append(image)
    
    return " ".join(cmd_parts)

print("🐳 Docker Command:")
print(generate_docker_command())
```

### 🧪 Testing Configuration

```env
# config/test.env
TEST_MODE <bool> = True
TEST_DATABASE <str> = sqlite:///:memory:
MOCK_EXTERNAL_APIS <bool> = True

# Test Data
TEST_DATA_PATH <str> = ./tests/data
FIXTURES_PATH <str> = ${TEST_DATA_PATH}/fixtures
EXPECTED_RESULTS_PATH <str> = ${TEST_DATA_PATH}/expected

# Performance Testing
LOAD_TEST_USERS <int> = 100
LOAD_TEST_DURATION <int> = 300
PERFORMANCE_THRESHOLDS <json> = {
  "response_time_ms": 200,
  "error_rate_percent": 1,
  "throughput_rps": 1000
}

# Test Categories
UNIT_TESTS <list> = user, auth, payment, notification
INTEGRATION_TESTS <list> = api, database, cache
E2E_TESTS <list> = login_flow, purchase_flow, admin_flow
```

---

## 🤝 Contributing

We love contributions! 🎉 Whether you're fixing bugs, adding features, or improving documentation, your help makes Envist better for everyone.

### 🚀 Quick Start for Contributors

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/envist.git
   cd envist
   ```

2. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Create your feature branch**
   ```bash
   git checkout -b feature/amazing-new-feature
   ```

4. **Make your changes and test**
   ```bash
   # Run tests
   pytest

   # Check code style
   flake8 envist/

   # Type checking
   mypy envist/
   ```

5. **Commit and push**
   ```bash
   git commit -am "✨ Add amazing new feature"
   git push origin feature/amazing-new-feature
   ```

6. **Create a Pull Request**
   - Go to GitHub and create a PR
   - Describe your changes clearly
   - Link any related issues

### 🎯 Areas We Need Help With

| Area | Description | Difficulty |
|------|-------------|------------|
| 🐛 **Bug Fixes** | Fix reported issues | Beginner |
| 📚 **Documentation** | Improve examples and guides | Beginner |
| ✨ **New Data Types** | Add support for more types | Intermediate |
| 🔄 **Multi-line Support** | Enable multi-line values | Advanced |
| ⚡ **Performance** | Optimize parsing and loading | Advanced |
| 🧪 **Testing** | Increase test coverage | Intermediate |

### 📋 Development Guidelines

- **Code Style:** Follow PEP 8
- **Testing:** Write tests for new features
- **Documentation:** Update docs for changes
- **Commit Messages:** Use conventional commit format
- **Backwards Compatibility:** Don't break existing APIs

### 🏆 Contributors

Thanks to all our amazing contributors! 🙌

<a href="https://github.com/Almas-Ali/envist/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Almas-Ali/envist" />
</a>

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### What does this mean?

✅ **You can:** Use, copy, modify, merge, publish, distribute, sublicense, and/or sell  
✅ **You must:** Include the original copyright notice and license  
❌ **We're not liable:** The software is provided "as is" without warranty  

**TL;DR:** Free to use for any purpose! 🎉

---

<div align="center">

**Made with ❤️ by [Md. Almas Ali](https://github.com/Almas-Ali)**

⭐ **Star this repo if Envist helped you!** ⭐

[Report Bug](https://github.com/Almas-Ali/envist/issues) • [Request Feature](https://github.com/Almas-Ali/envist/issues) • [Documentation](https://github.com/Almas-Ali/envist) • [Examples](https://github.com/Almas-Ali/envist/tree/master/examples)

</div>
