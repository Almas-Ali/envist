# Logging & Observability

Envist ships with a dedicated logger so you can trace parsing, casting, and runtime mutations.

## Default Behavior

Without additional configuration, Envist:

- Logs warnings and errors to stdout.
- Writes a verbose log file to `~/.envist/envist.log`.
- Annotates events with function names and line numbers for quick debugging.

## Enabling Debug Mode

Set environment variables before instantiating `Envist`:

```bash
setx ENVIST_DEBUG true
setx ENVIST_LOG_LEVEL DEBUG
```

On Unix shells use `export` instead of `setx`. Debug mode increases console verbosity, making it easier to understand parsing decisions.

## Configuring Handlers Programmatically

Use the factory helpers in `envist.logger`:

```python
import logging
from envist.logger import (
    configure_logger,
    create_stream_handler,
    create_file_handler,
)

logger = configure_logger(
    handlers=[
        create_stream_handler(level=logging.DEBUG),
        create_file_handler("logs/envist.log", level=logging.INFO),
    ],
    level="DEBUG",
)
```

Subsequent `Envist()` instances reuse the configured logger.

## Structured Logging

Write JSON payloads for ingestion into centralized platforms:

```python
import logging
from envist.logger import create_json_handler, EnvistLogger

handler = create_json_handler("logs/envist.json", level=logging.INFO)
EnvistLogger.configure(custom_handlers=[handler], reset=True)
```

Each record includes a timestamp, module, and message so observability tools can index them effectively.

## Rotating Logs

Prevent disk bloat with rotating handlers:

```python
import logging
from envist.logger import create_rotating_handler, configure_logger

configure_logger([
    create_rotating_handler(
        "logs/envist.log",
        max_bytes=10 * 1024 * 1024,
        backup_count=5,
        level=logging.INFO,
    )
])
```

## Runtime Signals

The logger exposes helper methods for granular instrumentation:

```python
from envist.logger import logger

logger.log_env_parse(".env", variables_found=12)
logger.log_typecast("PORT", "8080", "int", success=True)
logger.log_variable_access("DATABASE_URL", found=True, cast_type="str")
```

## Integrating With Existing Loggers

Wrap Envist events into your application logger:

```python
import logging
from envist.logger import EnvistLogger

app_logger = logging.getLogger("myapp")

class ForwardHandler(logging.Handler):
    def emit(self, record):
        app_logger.log(record.levelno, "[ENVIST] %s", record.getMessage())

EnvistLogger.configure(custom_handlers=[ForwardHandler()], reset=True)
```

## Environment Variables Reference

| Variable | Description |
|----------|-------------|
| `ENVIST_DEBUG` | When `true`, outputs debug logs to the console |
| `ENVIST_LOG_LEVEL` | Overrides the log level (`DEBUG`, `INFO`, etc.) |
| `ENVIST_LOG_FORMAT` | `standard` or `json` formatting |
| `ENVIST_LOG_FILE` | Absolute or relative path for file logging |
| `ENVIST_ROTATING_LOGS` | Enable rotation when combined with `ENVIST_LOG_FILE` |

Fine-tuned logging turns configuration issues into actionable alerts rather than silent failures.
