# Multiple Environments

Envist adapts to multi-stage workflows—development, staging, production—without complex boilerplate.

## Load Specific Files

```python
from envist import Envist

env = Envist(path="config/production.env")
```

Keep environment-specific files under `config/` and commit `.env.example` templates for visibility.

## Layer Configurations

Merge shared settings with overrides:

```python
base = Envist(path="config/base.env")
local = Envist(path="config/local.env")

config = {**base.get_all(), **local.get_all()}
```

Prioritize the right order (`local` last) to emulate cascading configuration.

## Feature Flags & Toggles

Mix static values and dynamic flags:

```env
FEATURE_FLAGS <dict<str, bool>> = auth:true, caching:false
```

Retrieve them as part of your runtime configuration dictionary.

## Working With CI/CD

- Store production secrets as environment variables in your deployment platform.
- Define fallbacks in `.env` for local development.
- Envist resolves `${VAR}` using both the file and `os.environ`, making the same code path work locally and in CI.

## Handling Optional Values

Set `accept_empty=True` for staging environments where certain keys are intentionally blank:

```python
staging_env = Envist(path="config/staging.env", accept_empty=True)
```

`None` values can signal disabled subsystems without extra conditionals.

## Saving Changes

Use `.save()` when you need to persist runtime edits, such as CLI tools that manage environment files:

```python
auto_env = Envist(path="config/generated.env")
auto_env.set("LAST_UPDATED", "2025-10-12")
auto_env.save(pretty=True, sort_keys=True)
```

Enable `example_file=True` to generate `.env.example` files that mirror your live environment without leaking secrets.

## Recommended Directory Layout

```
config/
  base.env
  development.env
  staging.env
  production.env
```

Pair this structure with Git-ignored `.env` secrets and version-controlled `.env.example` templates for consistency across teams.
