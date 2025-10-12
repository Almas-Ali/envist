# Variable Expansion

Envist resolves `${OTHER_VAR}` placeholders so you can build configuration from reusable building blocks.

## Basic Expansion

```env
HOST <str> = localhost
PORT <int> = 8080
BASE_URL <str> = http://${HOST}:${PORT}
```

`env.get("BASE_URL")` returns `"http://localhost:8080"`.

## Nested References

Values can reference variables that in turn reference others. Envist walks the graph safely and detects loops:

```env
API_HOST <str> = api.local
API_BASE <str> = https://${API_HOST}
HEALTH_ENDPOINT <str> = ${API_BASE}/health
```

All lookups resolve to fully expanded strings.

## OS Environment Fallback

If a placeholder is not found in the `.env` file, Envist checks `os.environ` before substituting an empty string. This makes it easy to mix secrets injected by the host OS or CI server.

## Circular Reference Protection

Envist keeps track of already-resolved keys and raises `EnvistParseError` when it detects a loop:

```env
A <str> = ${B}
B <str> = ${A}
```

Load-time feedback prevents runtime recursion failures.

## Collections & Expansion

Expansion happens before type casting, so nested values also work inside lists or dictionaries:

```env
HOST_PRIMARY <str> = api.local
HOST_SECONDARY <str> = admin.local
HOSTS <list> = ${HOST_PRIMARY}, ${HOST_SECONDARY}
```

Expansion happens before casting, so `HOSTS` becomes `["api.local", "admin.local"]`. Keep separate keys for values you want to reference individually.

## Troubleshooting Tips

- Enable debug logging (`ENVIST_DEBUG=true`) to see expansion traces.
- Prefix optional values with defaults: `${OPTIONAL:-fallback}` is not supported yet; prefer dedicated keys for now.
- When mixing JSON structures and placeholders, ensure the expanded value remains valid JSON.
