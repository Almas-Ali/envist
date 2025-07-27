from envist import Envist, validator

env: Envist = Envist(".env.example")


@validator(env, "age")
def validate_age(value: int) -> bool:
    """Validate age to be a positive integer."""

    if value <= 0:
        raise ValueError("Age must be a positive integer.")

    print(f"Validating age: {value}")


@validator(env, "name")
def validate_name(value: str) -> bool:
    """Validate name to be non-empty."""

    if not value:
        raise ValueError("Name cannot be empty.")

    print(f"Validating name: {value}")


@validator(env, "debug")
def validate_debug(value: bool) -> bool:
    """Validate debug to be a boolean."""

    if not isinstance(value, bool):
        raise ValueError("Debug must be a boolean.")

    print(f"Validating debug: {value}")
