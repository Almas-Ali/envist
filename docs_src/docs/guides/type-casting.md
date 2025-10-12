# Type Casting & Data Shapes

Envist ships with a powerful caster that understands primitive types, collections, and deeply nested annotations.

## Built-in Types

| Directive | Python type | Notes |
|-----------|-------------|-------|
| `<str>` | `str` | Preserves whitespace and casing |
| `<int>` | `int` | Supports decimal numbers |
| `<float>` | `float` | Parses scientific notation |
| `<bool>` | `bool` | Accepts `true/false`, `1/0`, `yes/no`, `on/off` |
| `<list>` / `<array>` | `list[str]` | Splits on commas, trims whitespace |
| `<tuple>` | `tuple[str, ...]` | Same parsing as list, returns tuple |
| `<set>` | `set[str]` | Removes duplicates automatically |
| `<dict>` | `dict[str, str]` | Accepts `key:value` pairs or JSON |
| `<csv>` | `list[str]` | Alias for comma-separated strings |
| `<json>` | `dict` / `list` | Hands off to `json.loads` |

## Nested Collections

Use angle brackets to describe the shape of nested data:

```env
PORTS <list<int>> = 8080, 8081
FEATURE_FLAGS <dict<str, bool>> = auth:true, cache:false
SERVERS <tuple<str>> = api.example.com, admin.example.com
```

Envist recursively casts each item, so `PORTS` becomes `[8080, 8081]` and `FEATURE_FLAGS` becomes `{"auth": True, "cache": False}`.

### Complex Structures

```env
CLUSTERS <dict<str, list<int>>> = east:8000,8001, west:9000,9001
PIPELINES <json> = [
  {"name": "ingest", "enabled": true},
  {"name": "analytics", "enabled": false}
]
```

The type caster understands JSON arrays, nested lists, and key=value syntax, falling back gracefully when formats mix.

## Manual Casting at Runtime

Disable auto casting globally or override per lookup:

```python
env = Envist(auto_cast=False)
page_size = env.get("PAGE_SIZE", cast=int)
```

Runtime casts accept the same annotations (`"list<int>"`) or regular callables (`cast=list`).

## Casting Errors

- `EnvistCastError` is raised when a value cannot be converted.
- The message includes the original value and the target type to speed up debugging.
- When `accept_empty=True`, Envist tries to cast empty values to sensible defaults (e.g., an empty list for `<list<int>>`).

## Tips for Reliable Data

- Favor JSON for hierarchical payloads (`<json>`), especially when values include commas.
- Keep list items trimmed by adding a space after the comma: `item1, item2`.
- Use nested types for clarity instead of manual parsing in code.
- Pin boolean values to `true`/`false` for readability across tooling.
