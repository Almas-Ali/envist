# Exceptions

Envist raises descriptive exceptions so you can distinguish parsing issues from type errors and missing keys.

## Hierarchy Overview

```text
EnvistError (base)
├── EnvistParseError
├── EnvistCastError
├── EnvistTypeError
├── EnvistValueError
└── FileNotFoundError (Envist variant)
```

All exceptions live under `envist.core.exceptions` and are re-exported at the package root.

## `EnvistError`

Base class for all custom exceptions. Catch this when you need a single fallback handler for any Envist-related failure.

## `EnvistParseError`

Raised during file parsing when:

- Lines contain invalid syntax.
- Keys violate naming rules.
- Variable expansion hits circular references or missing placeholders.

## `EnvistCastError`

Triggered when type casting fails, including nested conversions and runtime `env.get(..., cast=...)` calls. Error messages include the problematic value and target type.

## `EnvistTypeError`

Used by mutating methods (`set_all`, etc.) when passed incorrect data structures.

## `EnvistValueError`

Raised when attempting to `unset` or access keys that are absent from the current environment mapping.

## `FileNotFoundError`

Custom variant aligned with the standard library name. It is raised when the `.env` file cannot be located or read.

Catch Envist's `FileNotFoundError` instead of the built-in one if you want to handle parser-specific messaging.

## Handling Exceptions Gracefully

```python
from envist import Envist, EnvistError

try:
    env = Envist(path="config/.env")
except EnvistError as exc:
    print(f"Configuration failed: {exc}")
```

If you need precise control, catch specialized subclasses and tailor your remediation steps accordingly.
