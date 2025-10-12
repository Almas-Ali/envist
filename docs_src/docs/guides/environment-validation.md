# Validation Recipes

The `@validator` decorator gives you a declarative way to assert that environment variables contain acceptable values before the rest of your application runs.

## Quick Start

```python
from envist import Envist, validator

env = Envist()

@validator(env, "PORT")
def validate_port(value: int) -> bool:
    if not (1 <= value <= 65535):
        raise ValueError("PORT must be within TCP range")
    return True
```

The decorator runs immediately, so misconfigured deployments fail fast.

## Under the Hood

- Validators call `env.get(name)` using the same casting rules as the rest of your code.
- Envist checks keys with `EnvValidator.validate_key` before executing your custom logic, catching typos automatically.
- Any exception raised inside the validator stops startup—use descriptive error messages for better DX.

## Practical Examples

### Guard Required Secrets

```python
@validator(env, "API_KEY")
def validate_api_key(value: str) -> bool:
    if len(value) < 32:
        raise ValueError("API_KEY must be at least 32 characters long")
    return True
```

### Validate Choice Lists

```python
VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

@validator(env, "LOG_LEVEL")
def validate_log_level(value: str) -> bool:
    if value.upper() not in VALID_LEVELS:
        raise ValueError(f"LOG_LEVEL must be one of {', '.join(sorted(VALID_LEVELS))}")
    return True
```

### Cross-Field Validation

Use existing getters to compare values:

```python
@validator(env, "MAX_CONNECTIONS")
def validate_connection_limits(value: int) -> bool:
    min_connections = env.get("MIN_CONNECTIONS", default=1)
    if value < min_connections:
        raise ValueError("MAX_CONNECTIONS must be >= MIN_CONNECTIONS")
    return True
```

## Best Practices

- Keep validators close to `Envist()` instantiation so they run during import.
- Raise `ValueError` with actionable messages instead of returning `False` silently.
- Group related validators into modules for complex systems (e.g., `validators/database.py`).
- Use standard Python typing to document expected input.

## Testing Validators

Leverage fixtures to assert validator behavior:

```python
import pytest
from envist import Envist, validator

def test_port_validator(monkeypatch):
    monkeypatch.setenv("PORT", "70000")
    env = Envist(auto_cast=True)
    with pytest.raises(ValueError):
        @validator(env, "PORT")
        def validate_port(value: int) -> bool:
            if not (1 <= value <= 65535):
                raise ValueError
            return True
```

Envist reuses `os.environ` during parsing, so standard testing utilities like `monkeypatch` integrate seamlessly.
