# Envist

<p align="center">
	<img src="assets/images/logo.png" alt="Envist logo" width="160" />
</p>

Envist turns plain `.env` files into an intelligent, type-safe configuration layer for Python applications. Parse annotated environment variables, expand references, validate values, and log everything without adding external dependencies.

> **TL;DR:** Annotate your `.env` once, enjoy reliable configuration everywhere.

## Why Teams Choose Envist

- Built-in type casting with nested data structures such as `list<int>` or `dict<str, list<bool>>`
- Variable expansion that understands chained references and prevents circular loops
- Validator decorator for enforcing business rules before your app starts
- Observable by design through the dedicated `EnvistLogger`
- Zero dependencies and full backwards compatibility with traditional `.env` files

## At a Glance

```env
APP_NAME <str> = Envist Demo
PORT <int> = 8080
DEBUG <bool> = true
HOSTS <list> = localhost, 127.0.0.1
DATABASE_URL <str> = postgresql://user:pass@${HOSTS[0]}:5432/app
FEATURE_FLAGS <dict<str, bool>> = auth:true, caching:false
```

```python
from envist import Envist

env = Envist()
print(env.get("PORT"))           # 8080 (int)
print(env.get("FEATURE_FLAGS"))  # {'auth': True, 'caching': False}
```

## Explore the Documentation

- New here? Start with the [Getting Started](getting-started.md) guide.
- Need syntax examples? Check the [Smart .env Syntax](guides/env-file-syntax.md) page.
- Looking for programmatic details? Dive into the [API Reference](reference/api.md).
- Browse ready-to-run snippets on the [Examples & Recipes](examples.md) page.

## Proven in Real Projects

Envist powers anything from local prototypes to production services. With a single import you get:

- Deterministic configuration loading for CI/CD pipelines
- Consistent typing for data science notebooks and ML jobs
- Declarative validation for platform engineering teams

Ready to adopt? Install the package with `pip install envist` and keep reading. We'll handle the rest.
