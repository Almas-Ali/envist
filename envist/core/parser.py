"""Main Envist parser class"""

import os
import re
from typing import Any, Callable, Dict
from typing import List as ListType
from typing import Optional, Union

from ..utils.file_handler import FileHandler
from ..utils.type_casters import TypeCaster
from ..validators.env_validator import EnvValidator
from .exceptions import (
    EnvistCastError,
    EnvistParseError,
    EnvistTypeError,
    EnvistValueError,
    FileNotFoundError,
)


class Envist:
    """
    Envist is a simple .env file parser for Python.
    It's a modular package with clear separation of concerns.
    """

    def __init__(
        self, path: str = ".env", accept_empty: bool = False, auto_cast: bool = True
    ) -> None:
        """Constructor for Envist

        Args:
            path: Path to file containing environment variables. Defaults to '.env'.
            accept_empty: Accept keys declared without values. Defaults to False.
            auto_cast: Automatically cast values when type annotations are present.
                      If False, values remain as strings even with type annotations. Defaults to True.
        """
        self._path: str = path
        self._env: Dict[str, Any] = {}
        self._accept_empty: bool = accept_empty
        self._file_handler = FileHandler()
        self._validator = EnvValidator()
        self._type_caster = TypeCaster()
        self._auto_cast: bool = auto_cast
        self._load_env()

    def _load_env(self) -> None:
        """Load environment variables from file"""
        try:
            # Read and filter file lines
            raw_lines = self._file_handler.read_file(self._path)
            clean_lines = self._file_handler.filter_lines(raw_lines)

            # First pass: Parse all lines and store raw values
            raw_env = {}
            cast_types = {}

            for line_num, line in enumerate(clean_lines, 1):
                try:
                    key, value, cast_type = self._validator.parse_line_with_cast(
                        line, self._accept_empty
                    )
                    raw_env[key] = value
                    if cast_type:
                        cast_types[key] = cast_type

                except EnvistParseError as e:
                    raise EnvistParseError(f"Line {line_num}: {e}")

            # Second pass: Resolve variables and apply type casting
            for key, value in raw_env.items():
                try:
                    # Resolve variables if present
                    if self._is_variable(value):
                        value = self._resolve_variable_with_env(value, raw_env)

                    # Handle empty values
                    if value or self._accept_empty:
                        # Apply type casting only if auto_cast is enabled AND cast_type is specified
                        cast_type = cast_types.get(key)
                        if self._auto_cast and cast_type and value:
                            value = self._type_caster.cast_value(value, cast_type)
                        # If auto_cast is False, keep the value as string even if type annotation exists

                        self._env[key] = value
                        # OS environment variable is always string
                        os.environ[key] = str(value) if value is not None else ""
                    else:
                        # Key declared without value
                        self._env[key] = None
                        os.environ[key] = ""

                except Exception as e:
                    raise EnvistParseError(f"Error processing variable '{key}': {e}")

        except Exception as e:
            if not isinstance(e, (EnvistParseError, FileNotFoundError)):
                raise EnvistParseError(f"Unexpected error loading env file: {e}")
            raise

    def _is_variable(self, value: str) -> bool:
        """Check if value contains variable references"""
        if not isinstance(value, str):
            return False
        pattern = re.compile(r"\$\{(.+?)\}")
        return bool(pattern.search(value))

    def _resolve_variable(self, value: str) -> str:
        """Resolve variable references in value using current environment"""
        return self._resolve_variable_with_env(value, self._env)

    def _resolve_variable_with_env(self, value: str, env_dict: Dict[str, Any]) -> str:
        """Resolve variable references in value using provided environment dictionary"""
        if not isinstance(value, str):
            return value

        pattern = re.compile(r"\$\{(.+?)\}")
        matches = pattern.findall(value)

        # Track circular references
        resolved_vars = set()

        def resolve_recursively(val: str, depth: int = 0) -> str:
            if depth > 10:  # Prevent infinite recursion
                raise EnvistParseError(
                    f"Circular reference detected or too deep nesting in variable resolution"
                )

            current_matches = pattern.findall(val)

            for match in current_matches:
                if match in resolved_vars:
                    raise EnvistParseError(
                        f"Circular reference detected for variable: {match}"
                    )

                if match in env_dict:
                    resolved_vars.add(match)
                    replacement = (
                        str(env_dict[match]) if env_dict[match] is not None else ""
                    )

                    # If the replacement also contains variables, resolve them recursively
                    if self._is_variable(replacement):
                        replacement = resolve_recursively(replacement, depth + 1)

                    val = val.replace(f"${{{match}}}", replacement)
                    resolved_vars.discard(match)
                else:
                    # Variable not found - could be from OS environment or undefined
                    os_value = os.environ.get(match, "")
                    val = val.replace(f"${{{match}}}", os_value)

            return val

        return resolve_recursively(value)

    def get(
        self,
        key: str,
        *,
        default: Any = None,
        cast: Optional[Union[Callable[[str], Any], str]] = None,
    ) -> Any:
        """Get environment variable value

        Args:
            key: Environment variable key
            default: Default value if key not found
            cast: Type to cast the value to (overrides auto_cast behavior)

        Returns:
            Value or default, optionally cast to specified type
        """
        value = self._env.get(key, default)

        # Only apply casting if explicitly requested via cast parameter
        # auto_cast only affects parsing time, not runtime get() calls
        if cast and value is not None:
            try:
                value = self._type_caster.cast_value(value, cast)
            except Exception as e:
                raise EnvistCastError(f'Unable to cast "{value}" to "{cast}": {e}')

        return value

    def get_all(self) -> Dict[str, Any]:
        """Get all environment variables

        Returns:
            Dictionary of all env vars
        """
        return self._env.copy()

    def set(self, key: str, value: Any, cast: Optional[str] = None) -> Any:
        """Set environment variable

        Args:
            key: Environment variable key
            value: Environment variable value
            cast: Optional type casting hint

        Returns:
            The set value
        """
        if not self._validator.validate_key(key):
            raise EnvistParseError(f"Invalid key format: {key}")

        # Resolve variables in the new value if it's a string
        if isinstance(value, str) and self._is_variable(value):
            value = self._resolve_variable(value)

        self._env[key] = value
        os.environ[key] = str(value) if value is not None else ""
        return self._env[key]

    def set_all(self, data: Dict[str, Any]) -> None:
        """Set multiple environment variables

        Args:
            data: Dictionary of key-value pairs to set
        """
        if not isinstance(data, dict):
            raise EnvistTypeError("data must be a dictionary")

        for key, value in data.items():
            self.set(key, value)

    def unset(self, key: str) -> None:
        """Unset a specific environment variable

        Args:
            key: Environment variable key to unset
        """
        if key not in self._env:
            raise EnvistValueError(f'"{key}" not found in env')

        self._env.pop(key, None)
        os.environ.pop(key, None)

    def unset_all(self, data_list: Optional[ListType[str]] = None) -> None:
        """Unset multiple environment variables

        Args:
            data_list: List of keys to unset. If None, clears all variables.
        """
        if data_list:
            for key in data_list:
                if key not in self._env:
                    raise EnvistValueError(f'"{key}" not found in env')
                self._env.pop(key, None)
                os.environ.pop(key, None)
        else:
            # Clear all environment variables
            for key in list(self._env.keys()):
                os.environ.pop(key, None)
            self._env.clear()

    def save(self, pretty: bool = False, sort_keys: bool = False) -> None:
        """Save updated environment variables to file

        Args:
            pretty: Whether to use pretty formatting with spaces
            sort_keys: Whether to sort keys alphabetically
        """
        env_to_save = self._env

        if sort_keys:
            env_to_save = dict(sorted(self._env.items()))

        with open(self._path, "w", encoding="utf-8") as file:
            for key, value in env_to_save.items():
                if pretty:
                    file.write(f"{key} = {value}\n")
                else:
                    file.write(f"{key}={value}\n")

    def reload(self) -> None:
        """Reload environment variables from file"""
        # Clear current environment variables from os.environ
        for key in list(self._env.keys()):
            os.environ.pop(key, None)

        self._env.clear()
        self._load_env()

    @property
    def path(self) -> str:
        """Get the file path"""
        return self._path

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access"""
        if key not in self._env:
            raise KeyError(f"Environment variable '{key}' not found")
        return self._env[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Allow dictionary-style assignment"""
        self.set(key, value)

    def __delitem__(self, key: str) -> None:
        """Allow dictionary-style deletion"""
        self.unset(key)

    def __contains__(self, key: str) -> bool:
        """Allow 'in' operator"""
        return key in self._env

    def __len__(self) -> int:
        """Return number of environment variables"""
        return len(self._env)

    def __iter__(self):
        """Allow iteration over keys"""
        return iter(self._env)

    def __repr__(self) -> str:
        """Return a string representation of the object"""
        return f'<Envist path="{self._path}">'

    def __str__(self) -> str:
        """Return a string representation of the object"""
        return f'<Envist path="{self._path}">'
