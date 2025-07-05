"""Validation utilities for environment variables"""

import re
from typing import Optional, Tuple

from ..core.exceptions import EnvistParseError


class EnvValidator:
    """Validates environment variable syntax and values"""

    @staticmethod
    def parse_line_with_cast(
        line: str, accept_empty: bool = False
    ) -> Tuple[str, str, Optional[str]]:
        """Parse a single line into key-value pair with optional nested type casting

        Args:
            line: Line to parse
            accept_empty: Whether to accept empty values

        Returns:
            Tuple of (key, value, cast_type)

        Raises:
            EnvistParseError: If line format is invalid
        """
        # Enhanced pattern to match nested type casting: KEY<type<innertype>> = value
        cast_pattern = (
            r"(.+?)\s*<\s*([^<>=]+(?:<[^<>=]*>)*)\s*>\s*=\s*(.*)"
            if accept_empty
            else r"(.+?)\s*<\s*([^<>=]+(?:<[^<>=]*>)*)\s*>\s*=\s*(.+)"
        )

        match = re.search(cast_pattern, line)
        if match:
            key, cast_type, value = match.groups()
            key = key.strip()
            cast_type = cast_type.strip()
            value = value.strip() if value else ""

            # Validate nested type syntax
            if not EnvValidator._validate_type_syntax(cast_type):
                raise EnvistParseError(f"Invalid type syntax: {cast_type}")

        else:
            # Try to match simple pattern: KEY = value
            simple_pattern = (
                r"(.+?)\s*=\s*(.*)" if accept_empty else r"(.+?)\s*=\s*(.+)"
            )

            match = re.search(simple_pattern, line)
            if match:
                key, value = match.groups()
                key = key.strip()
                value = value.strip() if value else ""
                cast_type = None
            else:
                raise EnvistParseError(f"Invalid line format: {line}")

        if not accept_empty and not value:
            raise EnvistParseError(
                f"Empty value for key '{key}' (use accept_empty=True to allow)"
            )

        # Remove quotes if present
        value = EnvValidator._remove_quotes(value)

        return key, value, cast_type

    @staticmethod
    def _validate_type_syntax(type_str: str) -> bool:
        """Validate nested type syntax"""
        # Check for balanced angle brackets
        bracket_count = 0
        for char in type_str:
            if char == "<":
                bracket_count += 1
            elif char == ">":
                bracket_count -= 1
                if bracket_count < 0:
                    return False

        return bracket_count == 0

    @staticmethod
    def parse_line(line: str, accept_empty: bool = False) -> Tuple[str, str]:
        """Parse a single line into key-value pair (backward compatibility)

        Args:
            line: Line to parse
            accept_empty: Whether to accept empty values

        Returns:
            Tuple of (key, value)

        Raises:
            EnvistParseError: If line format is invalid
        """
        key, value, _ = EnvValidator.parse_line_with_cast(line, accept_empty)
        return key, value

    @staticmethod
    def _remove_quotes(value: str) -> str:
        """Remove surrounding quotes from value"""
        if len(value) >= 2:
            if (value.startswith('"') and value.endswith('"')) or (
                value.startswith("'") and value.endswith("'")
            ):
                return value[1:-1]
        return value

    @staticmethod
    def validate_key(key: str) -> bool:
        """Validate environment variable key format

        Args:
            key: Key to validate

        Returns:
            True if valid, False otherwise
        """
        pattern = r"^[A-Za-z_][A-Za-z0-9_]*$"
        return bool(re.match(pattern, key))
