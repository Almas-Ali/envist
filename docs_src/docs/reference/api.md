# API Reference

This reference documents the public classes, methods, and decorators exposed by Envist.

## `Envist`

Main entry point for loading and managing environment variables.

```python
from envist import Envist
```

### Constructor

```python
Envist(
    path: str = ".env",
    accept_empty: bool = False,
    auto_cast: bool = True,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | `str` | `.env` | File to load variables from |
| `accept_empty` | `bool` | `False` | Allow blank values and store them as `None` |
| `auto_cast` | `bool` | `True` | Automatically apply type annotations while parsing |

### Properties

- `path`: Returns the underlying file path.

### Read Methods

| Method | Returns | Notes |
|--------|---------|-------|
| `get(key, *, default=None, cast=None)` | `Any` | Retrieve a single value; optional runtime casting |
| `get_all()` | `dict[str, Any]` | Copy of all parsed variables |

### Write Methods

| Method | Returns | Notes |
|--------|---------|-------|
| `set(key, value, cast=None)` | `Any` | Assigns a value and updates `os.environ` |
| `set_all(mapping)` | `None` | Bulk assignment from a dictionary |
| `unset(key)` | `None` | Delete a variable from Envist and `os.environ` |
| `unset_all(keys=None)` | `None` | Remove listed keys or wipe everything |
| `save(pretty=False, sort_keys=False, example_file=False)` | `None` | Persist values back to disk |
| `reload()` | `None` | Re-read the file and refresh cached values |

### Special Methods

- `__getitem__`, `__setitem__`, `__delitem__`: Dictionary-style access (`env["KEY"]`).
- `__contains__`: Enables membership checks (`"KEY" in env`).
- `__iter__` and `__len__`: Iterate over keys or inspect counts.
- `__getattr__`: Attribute-style access when keys are valid identifiers (`env.PORT`).

### Error Handling

Most incorrect operations raise specific exceptions from `envist.core.exceptions`. See [Exceptions](exceptions.md) for full details.

## `validator`

Decorator that validates configuration immediately after parsing.

```python
from envist import validator

@validator(env, "KEY")
def validate(value):
    ...
```

- Accepts an `Envist` instance and the variable name.
- Runs at definition time via an IIFE pattern.
- Raises when keys fail `EnvValidator.validate_key`.

## `EnvistLogger`

Singleton wrapper around Python's logging module.

```python
from envist.logger import EnvistLogger
```

### Key Methods

| Method | Description |
|--------|-------------|
| `configure(custom_handlers=None, reset=False)` | Rebuild the singleton with new handlers |
| `set_level(level)` | Adjust log level at runtime |
| `add_handler(handler)` / `remove_handler(handler)` | Manage handlers dynamically |
| `log_env_parse(path, variables_found)` | Convenience logging helper |
| `log_typecast(key, value, target_type, success)` | Emit structured type casting messages |
| `log_variable_access(key, found, cast_type=None)` | Trace lookups |

See [Logging & Observability](../guides/logging.md) for usage patterns.

## Utilities

### `create_stream_handler(stream=None, level=logging.INFO)`

Returns a ready-to-use `logging.StreamHandler` with Envist formatting.

### `create_file_handler(log_file, level=logging.INFO)`

Creates a file handler that ensures the target directory exists.

### `create_json_handler(log_file, level=logging.INFO)`

Writes logs as JSON records—ideal for log aggregation systems.

### `create_rotating_handler(log_file, max_bytes=10_485_760, backup_count=5, level=logging.INFO)`

Generates a `RotatingFileHandler` for production setups.

### `create_syslog_handler(address=("localhost", 514), level=logging.INFO)`

Sends Envist logs to Syslog.

## Module-Level Configuration

`envist.config.EnvistConfig` reads environment variables (`ENVIST_DEBUG`, `ENVIST_LOG_LEVEL`, etc.) and auto-configures logging on import. Instantiate it manually if you need to reapply settings after runtime changes.

```python
from envist.config import EnvistConfig

config = EnvistConfig()
config.add_custom_handler(...)
```
