"""
Envist Exceptions Module.
"""


class EnvistError(Exception):
    """
    Base exception for all Envist errors.
    """


class EnvistCastError(EnvistError):
    """
    Raised when unable to cast a value to a specific type.
    """


class EnvistParseError(EnvistError):
    """
    Raised when unable to parse a line in env file.
    """


class EnvistValueError(EnvistError):
    """
    Raised when a value is not found in env.
    """


class EnvistTypeError(EnvistError):
    """
    Raised when data is not a dictionary.
    """


class FileNotFoundError(EnvistError):
    """
    Raised when the specified file is not found.
    """
