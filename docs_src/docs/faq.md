# FAQ

Find quick answers to the most common Envist questions.

## Does Envist work with plain `.env` files?

Yes. If you omit type annotations, Envist behaves like a standard dotenv parser. Introduce types when you are ready.

## How do I handle secrets securely?

Keep secrets out of version control. Store them in runtime environment variables or secret managers, then reference them with `${SECRET_NAME}` placeholders inside your typed `.env` file when necessary.

## What happens when a cast fails?

Envist raises `EnvistCastError` with details about the value and target type. Wrap `Envist()` creation in a `try` block or rely on `pytest` to catch misconfigurations during CI.

## Can I override values at runtime?

Yes. Use `env.set("KEY", value)` to update the in-memory map and `os.environ`. Call `env.save()` if you want to persist changes back to the file.

## How do I toggle features per environment?

Create one file per environment (e.g., `config/staging.env`, `config/production.env`) and load the right file using the `path` parameter. For additional overrides, merge dictionaries from multiple `Envist` instances.

## Is there a CLI?

Envist focuses on the Python API. Build lightweight tooling using `Envist` and libraries like `click` or `typer` to match your workflow.

## Can I extend the caster with custom types?

You can supply a callable to `env.get(key, cast=my_converter)`. For reusable annotations, wrap the callable and reference it from your application code.

## How do I report issues or request features?

Open an issue on [GitHub](https://github.com/Almas-Ali/envist/issues). Include your `.env` snippet, stack trace, and environment details to help us reproduce the problem quickly.
