# Examples & Recipes

Kick-start your integration with copy-paste-friendly snippets drawn from real-world Envist usage.

## FastAPI Application

```python
from fastapi import FastAPI
from envist import Envist

env = Envist()

app = FastAPI(title=env.get("APP_NAME", default="Envist API"))

@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": env.get("APP_VERSION", default="dev"),
        "debug": env.get("DEBUG", default=False),
    }
```

Pair this with a `.env` file:

```env
APP_NAME <str> = Envist Service
APP_VERSION <str> = 1.2.0
DEBUG <bool> = false
```

## Django Settings Bridge

```python
# settings.py
from envist import Envist

env = Envist()

SECRET_KEY = env.get("SECRET_KEY")
DEBUG = env.get("DEBUG", default=False)
ALLOWED_HOSTS = env.get("ALLOWED_HOSTS", default=["localhost"])
DATABASES = {
    "default": env.get("DATABASE_CONFIG", cast="json"),
}
```

## Data Pipelines

```python
from envist import Envist

env = Envist(path="config/pipeline.env")

BATCH_SIZE = env.get("BATCH_SIZE", default=1000)
SOURCES = env.get("SOURCES", cast="list<str>")
RETRY_POLICY = env.get("RETRY_POLICY", cast="dict<str, int>")
```

`pipeline.env` may look like:

```env
BATCH_SIZE <int> = 500
SOURCES <list> = s3://bucket/raw, s3://bucket/enriched
RETRY_POLICY <dict<str, int>> = attempts:3, backoff:5
```

## CLI Tools

```python
import click
from envist import Envist

env = Envist()

@click.command()
@click.argument("key")
@click.option("--value")
def set_env(key, value):
    env.set(key, value)
    env.save(pretty=True, sort_keys=True)
    click.echo(f"Updated {key}")
```

## Advanced Logging Setup

```python
from envist.logger import configure_logger, create_stream_handler, create_json_handler

configure_logger(
    handlers=[
        create_stream_handler(level="INFO"),
        create_json_handler("logs/envist.json", level="DEBUG"),
    ],
    level="DEBUG",
)
```

## Browse the Repository

More end-to-end scripts live in the `examples/` directory:

- `examples/getting_started/01_basic_usage.py`
- `examples/advanced/01_custom_logging.py`
- `examples/advanced/04_validation.py`

Each script mirrors the concepts documented here, so you can experiment locally or adapt them to your stack.
