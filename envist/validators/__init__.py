from functools import wraps
from typing import TYPE_CHECKING, Callable
from warnings import deprecated

if TYPE_CHECKING:
    from ..core.parser import Envist

from .env_validator import EnvValidator


def _iief(func: Callable[[], bool]) -> Callable[[], bool]:
    return func()


@deprecated(
    "The @validator decorator is deprecated and will be removed in future releases. "
    "Consider using the Envist.validator decorator instead."
)
def validator(env: "Envist", name: str) -> Callable[[Callable[[str], bool]], bool]:
    """Decorator to validate environment variable keys"""

    def decorator(func: Callable[[str], bool]) -> Callable[[str], bool]:
        @_iief
        @wraps(func)
        def wrapper() -> bool:
            if not EnvValidator.validate_key(name):
                raise ValueError(f"Invalid key format: {name}")
            return func(env.get(name))

        return wrapper

    return decorator
