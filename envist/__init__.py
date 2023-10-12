'''
Envist is a simple .env file parser for Python. It's a single file module with no dependencies. 

Usage:
    from envist import Envist

    env = Envist()

    # Print env object as string
    print(env)
    # <Envist path=".env">

    # Get default env file path
    print(env.path)
    # .env

    # Custom env file path
    env = Envist(path='my/path/.env')

    # Get a specific env variable
    env.get('name')

    # Get a specific env variable with default value
    env.get('name', default='John Doe')

    # Get a specific env variable with default value and cast
    env.get('name', default='John Doe', cast=int)

    # Get all env variables
    env.get_all()

    # Set a specific env variable
    env.set('name', 'John Doe')
    env.set('age', 20)
    env.set('is_admin', True)

    # Set multiple env variables
    env.set_all({
        'name': 'John Doe',
        'age': 20,
        'is_admin': True
    })

    # Unset a specific env variable
    env.unset('name')

    # Unset multiple env variables
    env.unset_all(['name', 'age'])

    # Unset all env variables
    env.unset_all() 

    # Save updated env variables to file
    env.save()

'''

from typing import Any, Callable, Dict, Optional, Union, List

__version__ = '0.0.1'
__all__ = ['Envist']
__author__ = 'Md. Almas Ali'


class EnvistCastError(Exception):
    ...


class EnvistParseError(Exception):
    ...


class EnvistValueError(Exception):
    ...


class EnvistTypeError(Exception):
    ...


class Envist:
    '''
    Envist is a simple .env file parser for Python. It's a single file module with no dependencies.
    '''

    def __init__(self, path: str = '.env') -> None:
        self.path: str = path
        self.env: Dict[str, str] = {}
        self.__load_env()

    def __load_env(self) -> dict:
        '''
        Load env variables from file.
        '''
        with open(self.path, 'r') as f:
            # Remove empty lines, newlines, and comments
            _lines = [line.strip() for line in f.readlines()
                      if line.strip() and not line.startswith('#')]
            try:
                for line in _lines:
                    key, value = line.strip().split('=')
                    self.env[key.strip()] = value.strip()
            except ValueError:
                raise EnvistParseError(f'Unable to parse "{line}"')
        return self.env

    def get(self, key: str, *,
            default: Any = None,
            cast: Optional[Callable[[str], Any]] = None
            ) -> Union[str, Any]:
        '''
        Get a specific env variable.
        '''
        value: Any = self.env.get(key, default)

        try:
            if cast:
                return cast(value)
        except ValueError:
            raise EnvistCastError(f'Unable to cast "{value}" to "{cast}"')

        return value

    def get_all(self) -> Dict[str, str]:
        '''
        Get all env variables.
        '''
        return self.env

    def set(self, key: str, value: Any) -> Any:
        '''
        Set a specific env variable.
        '''
        self.env[key] = value
        return self.env[key]

    def set_all(self, data: Dict[str, str]) -> None:
        '''
        Set multiple env variables.
        '''
        if not isinstance(data, dict):
            raise EnvistTypeError('data must be a dictionary')
        self.env.update(data)

    def unset(self, key: str) -> None:
        '''
        Unset a specific env variable.
        '''
        if key not in self.env:
            raise EnvistValueError(f'"{key}" not found in env')
        self.env.pop(key, None)

    def unset_all(self, data_list: List[str] = None) -> None:
        '''
        Unset multiple env variables.
        '''
        if data_list:
            for key in data_list:
                if key not in self.env:
                    raise EnvistValueError(f'"{key}" not found in env')
                self.env.pop(key, None)
        else:
            self.env.clear()

    def save(self) -> None:
        '''
        Save updated env variables to file.
        '''
        with open(self.path, 'w') as f:
            for key, value in self.env.items():
                f.write(f'{key}={value}\n')

    def __repr__(self) -> str:
        '''
        Return a string representation of the object.
        '''
        return f'<Envist path="{self.path}">'

    def __str__(self) -> str:
        '''
        Return a string representation of the object.
        '''
        return f'<Envist path="{self.path}">'
