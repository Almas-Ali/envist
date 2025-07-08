"""
A simple .env file parser with types and nested type support.

Usage:

```python
    from envist import Envist

    >>> env = Envist()

    # Print env object as string
    print(env)
    # <Envist path=".env">

    # Get default env file path
    print(env.path)
    # .env

    # Custom env file path
    >>> env = Envist(path='my/path/.env')

    # Get a specific env variable
    >>> env.get('name')

    # Get a specific env variable with default value
    >>> env.get('name', default='John Doe')

    # Get a specific env variable with default value and cast
    >>> env.get('name', default='John Doe', cast=int)

    # Get all env variables
    >>> env.get_all()

    # Set a specific env variable
    >>> env.set('name', 'John Doe')
    >>> env.set('age', 20)
    >>> env.set('is_admin', True)

    # Set multiple env variables
    >>> env.set_all({
        'name': 'John Doe',
        'age': 20,
        'is_admin': True
    })

    # Unset a specific env variable
    >>> env.unset('name')

    # Unset multiple env variables
    >>> env.unset_all(['name', 'age'])

    # Unset all env variables
    >>> env.unset_all()

    # Save updated env variables to file
    # Save to default file, i.e. .env
    # You can also specify a custom file path in Emvist constructor object.
    >>> env.save(
        pretty=True, # Pretty print
        sort_keys=True # Sort keys
    )

    # Get a list from env variable
    # list_elements <list> = 1, 2, 3, 4, 5
    >>> env.get('list_elements', cast=list)

    # Working with variables
    # server <str> = 127.0.0.1
    # port <int> = 8080
    # url <str> = http://${server}:${port}
    >>> env.get('url') # Output: 'http://127.0.0.1:8080'
```
"""

"""
Envist - A simple .env file parser for Python
"""

from .core.exceptions import (
    EnvistCastError,
    EnvistError,
    EnvistParseError,
    EnvistTypeError,
    EnvistValueError,
    FileNotFoundError,
)
from .core.parser import Envist

__version__ = "0.1.1"
__all__ = ["Envist"]
__author__ = "Md. Almas Ali"
__all__ = [
    "Envist",
    "EnvistError",
    "FileNotFoundError",
    "EnvistParseError",
    "EnvistCastError",
    "EnvistTypeError",
    "EnvistValueError",
]
