# Smart .env Syntax

Envist extends the plain key=value format with annotations that tell the parser how to interpret and validate your configuration.

## Anatomy of a Smart Line

```env
PORT <int> = 8080
```

- `PORT` is the key.
- `<int>` is the type directive.
- `8080` is the literal value.

Type directives are optional—omit them to keep backwards compatibility with classic `.env` files.

## Supported Delimiters

- `KEY <type> = value` is the primary format.
- `KEY:type=value` is also accepted for teams that prefer colon syntax.
- `KEY=value` works exactly like traditional dotenv files.

Whitespace around the equals sign is ignored. For readability, align values however you like.

## Comments and Empty Lines

- Lines starting with `#` or containing ` # ` comments are ignored.
- Inline comments inside quotes are preserved: `SECRET <str> = "value #secure"`.
- Empty lines are skipped, making it easy to group related variables.

## Declaring Empty Values

When `Envist(accept_empty=True)` is enabled, you can leave values blank:

```env
# Placeholder for local overrides
REDIS_URL <str> =
```

Without `accept_empty=True`, empty declarations are ignored to avoid surprises.

## Environment Variable Names

Envist enforces conventional naming:

- Keys must start with a letter or underscore.
- Only alphanumeric characters and underscores are allowed.

If a key fails validation, the loader raises `EnvistParseError`, helping you catch typos early.

## Example Layout

```env
# Application metadata
APP_NAME <str> = Envist Demo
APP_VERSION <str> = 1.0.0

# Server config
HOST <str> = 0.0.0.0
PORT <int> = 8000
DEBUG <bool> = false

# Database with variable expansion
DB_HOST <str> = localhost
DB_PORT <int> = 5432
DATABASE_URL <str> = postgresql://user:pass@${DB_HOST}:${DB_PORT}/envist
```

## Migration Strategy

1. Keep your existing `.env` file untouched.
2. Introduce type annotations incrementally.
3. Enable `auto_cast=True` (default) to benefit immediately.

This approach keeps deployments safe while unlocking richer tooling over time.
