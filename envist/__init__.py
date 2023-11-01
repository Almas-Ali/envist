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
    # Save to default file, i.e. .env
    # You can also specify a custom file path in Emvist constructor object.
    env.save(
        pretty=True, # Pretty print
        sort_keys=True # Sort keys
    )

    # Get a list from env variable
    # list_elements <list> = 1, 2, 3, 4, 5
    env.get('list_elements', cast=list)

    # Working with variables
    # server <str> = 127.0.0.1
    # port <int> = 8080
    # url <str> = http://${server}:${port}
    env.get('url') # Output: 'http://127.0.0.1:8080'

'''

from typing import Any, Callable, Optional, Union
import os
import re


__version__ = '0.0.3'
__all__ = ['Envist']
__author__ = 'Md. Almas Ali'


class EnvistCastError(Exception):
    '''
    Raised when unable to cast a value to a specific type.
    '''


class EnvistParseError(Exception):
    '''
    Raised when unable to parse a line in env file.
    '''


class EnvistValueError(Exception):
    '''
    Raised when a value is not found in env.
    '''


class EnvistTypeError(Exception):
    '''
    Raised when data is not a dictionary.
    '''


class Envist:
    '''
    Envist is a simple .env file parser for Python. It's a single file module with no dependencies.
    '''

    def __init__(self, path: str = '.env') -> None:
        self.path: str = path
        self.env: dict[str, str] = {}
        self.__load_env()

    def __load_env(self) -> dict:
        '''
        Load env variables from file.
        '''
        with open(self.path, 'r', encoding='utf-8') as file:
            # Remove empty lines, newlines, and comments
            _lines = [line.strip() for line in file.readlines()
                      if line.strip() and not line.startswith('#')]

            try:
                for line in _lines:
                    try:
                        key, cast, value = re.search(
                            r'(.+?)\s*<\s*(.+?)\s*>?\s*=\s*(.+)', line
                        ).groups()
                    except AttributeError:
                        key, value = re.search(
                            (r'(.+?)\s*=\s*(.+)'), line).groups()
                        cast = None

                    if self.__is_variable(value):
                        value = self.__resolve_variable(value)

                    if cast:
                        value = self.__resolve_type_cast(value, cast)

                    self.env[key] = value
                    # OS environment variable is always string
                    os.environ[key] = str(value)

            except ValueError as exception:
                raise EnvistParseError(
                    f'Unable to parse "{line}"') from exception
        return self.env

    def __resolve_variable(self, value: str) -> str:
        # Checking variable match ${var}
        pattern = re.compile(r'\$\{(.+?)\}')
        match = pattern.findall(value)
        if match:
            for match_element in match:
                if match_element in self.env:
                    value = value.replace(
                        f'${{{match_element}}}', str(self.env[match_element]))
        return value

    def __resolve_type_cast(self, value: str, cast: str) -> Any:
        '''
        Validate cast type.
        '''
        if cast == 'int':
            value = int(value)
        elif cast == 'float':
            value = float(value)
        elif cast == 'bool':
            value = bool(value)
        elif cast in ('list', 'List'):
            value = List(value)
        elif cast == 'str':
            value = str(value)
        elif cast in ('dict', 'Dict'):
            value = Dict(value)
        elif cast in ('tuple', 'Tuple'):
            value = Tuple(value)
        elif cast in ('set', 'Set'):
            value = Set(value)
        elif cast in ('csv', 'CSV'):
            value = CSV(value)
        elif cast in ('json', 'JSON'):
            value = JSON(value)
        else:
            raise EnvistCastError(f'"{cast}" is not a valid cast type')

        return value

    def __is_variable(self, value: str) -> bool:
        '''
        Check if value is a variable.
        '''
        pattern = re.compile(r'\$\{(.+?)\}')
        match = pattern.findall(value)
        if match:
            return True

    def get(self, key: str, *, default: Any = None,
            cast: Optional[Union[Callable[[str], Any], str]] = None) -> Any:
        '''
        Get a specific env variable.
        '''
        value: Any = self.env.get(key, default)

        try:
            if cast:
                if isinstance(cast, list):
                    value = List(value)
                elif isinstance(cast, dict):
                    value = Dict(value)
                elif isinstance(cast, tuple):
                    value = Tuple(value)
                elif isinstance(cast, set):
                    value = Set(value)
                elif isinstance(cast, str):
                    value = str(value)
                elif isinstance(cast, int):
                    value = int(value)
                elif isinstance(cast, float):
                    value = float(value)
                elif isinstance(cast, bool):
                    value = bool(value)
                elif isinstance(cast, CSV):
                    value = CSV(value)
                elif isinstance(cast, JSON):
                    value = JSON(value)
                else:
                    value = cast(value)

        except ValueError as exception:
            raise EnvistCastError(
                f'Unable to cast "{value}" to "{cast}"') from exception

        return value

    def get_all(self) -> dict[str, str]:
        '''
        Get all env variables.
        '''
        return self.env

    def set(self, key: str, value: Any,
            cast: Optional[Callable[[str], Any]] = None) -> Any:
        '''
        Set a specific env variable.
        '''
        self.env[key] = value
        return self.env[key]

        # self.env[f'{key} <{cast}>'] = value
        # return self.env[key]

    def set_all(self, data: dict[str, str]) -> None:
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

    def unset_all(self, data_list: list[str] | None = None) -> None:
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

    def save(self, pretty: bool = False, sort_keys: bool = False) -> None:
        '''
        Save updated env variables to file.
        '''

        if sort_keys:
            self.env = dict(sorted(self.env.items()))

        with open(self.path, 'w', encoding='utf-8') as file:
            if pretty:
                for key, value in self.env.items():
                    file.write(f'{key} = {value}\n')
            else:
                for key, value in self.env.items():
                    file.write(f'{key}={value}\n')

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


class List(list):
    '''
    A list subclass to cast env variable to list.
    '''

    def __new__(cls, value: str) -> list:
        return super().__new__(cls, value.split(','))

    def __init__(self, value: str) -> None:
        super().__init__(value.split(','))

    # def __repr__(self) -> str:
    #     return f'<envist.List {super().__repr__()}>'

    def __str__(self) -> str:
        return f'{super().__str__()}'


class Dict(dict):
    '''
    A dict subclass to cast env variable to dict.
    '''

    def __new__(cls, value: str) -> dict:
        return super().__new__(cls, value.split(','))

    def __init__(self, value: str) -> None:
        super().__init__(value.split(','))

    # def __repr__(self) -> str:
    #     return f'<envist.Dict {super().__repr__()}>'

    def __str__(self) -> str:
        return f'{super().__str__()}'


class Tuple(tuple):
    '''
    A tuple subclass to cast env variable to tuple.
    '''

    def __new__(cls, value: str) -> tuple:
        return super().__new__(cls, value.split(','))

    def __init__(self, value: str) -> None:
        super().__init__(value.split(','))

    # def __repr__(self) -> str:
    #     return f'<envist.Tuple {super().__repr__()}>'

    def __str__(self) -> str:
        return f'{super().__str__()}'


class Set(set):
    '''
    A set subclass to cast env variable to set.
    '''

    def __new__(cls, value: str) -> set:
        return super().__new__(cls, value.split(','))

    def __init__(self, value: str) -> None:
        super().__init__(value.split(','))

    # def __repr__(self) -> str:
    #     return f'<envist.Set {super().__repr__()}>'

    def __str__(self) -> str:
        return f'{super().__str__()}'


class CSV:
    '''
    A class to cast env variable to csv.
    '''

    def __new__(cls, value: str) -> str:
        return super().__new__(cls, value.split(','))

    def __init__(self, value: str) -> None:
        super().__init__(value.split(','))

    # def __repr__(self) -> str:
    #     return f'<envist.CSV {super().__repr__()}>'

    def __str__(self) -> str:
        return f'{super().__str__()}'


class JSON:
    '''
    A class to cast env variable to json.
    '''

    def __new__(cls, value: str) -> str:
        return super().__new__(cls, value.split(','))

    def __init__(self, value: str) -> None:
        super().__init__(value.split(','))

    # def __repr__(self) -> str:
    #     return f'<envist.JSON {super().__repr__()}>'

    def __str__(self) -> str:
        return f'{super().__str__()}'
