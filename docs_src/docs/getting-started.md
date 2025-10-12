# Getting Started

Set up Envist in minutes and load typed configuration straight from your `.env` files. This guide walks through prerequisites, installation, and the core workflow.

## Prerequisites

- Python 3.7 or newer
- An existing `.env` file (optional but recommended)
- Familiarity with standard environment variables

## Installation

### pip (recommended)

```bash
pip install envist
```

### Conda

```bash
conda install -c conda-forge envist
```

### Poetry

```bash
poetry add envist
```

### From source

```bash
git clone https://github.com/Almas-Ali/envist.git
cd envist
pip install -e .
```

## Your First Typed `.env`

Create a `.env` file alongside your application:

```env
APP_NAME <str> = Envist Demo
PORT <int> = 8080
DEBUG <bool> = true
DATABASE_URL <str> = postgresql://user:pass@localhost:5432/app
ALLOWED_HOSTS <list> = localhost, 127.0.0.1
```

Load it in Python:

```python
from envist import Envist

env = Envist()

print(env.get("APP_NAME"))       # 'Envist Demo'
print(env.get("PORT"))           # 8080
print(env.get("ALLOWED_HOSTS"))  # ['localhost', '127.0.0.1']
```

## Core Workflow

1. **Annotate** values in `.env` with `<type>` descriptors.
2. **Instantiate** `Envist()` in your codebase.
3. **Retrieve** values with `env.get()` or dictionary-style access (`env["KEY"]`).
4. **Update** configuration dynamically using `env.set()` and `env.save()` if required.

## Switching Files

Pass a custom path when you need environment-specific configs:

```python
env = Envist(path="config/production.env")
```

Combine configurations by instantiating multiple readers and merging dictionaries. See [Multiple Environments](guides/multi-environments.md) for patterns.

## Accepting Empty Values

Some workflows require declaring keys without immediate values. Enable this by setting `accept_empty=True`:

```python
env = Envist(accept_empty=True)
optional = env.get("OPTIONAL_SETTING")  # returns None when empty
```

## Disabling Auto Casting

To keep raw strings—useful during incremental migrations—set `auto_cast=False` and override per lookup:

```python
env = Envist(auto_cast=False)
size = env.get("BATCH_SIZE", cast=int)
```

## Next Steps

- Learn about the declarative syntax in [Smart .env Syntax](guides/env-file-syntax.md).
- Explore complex data types in [Type Casting & Data Shapes](guides/type-casting.md).
- Add runtime safeguards with the [Validation Recipes](guides/environment-validation.md).
