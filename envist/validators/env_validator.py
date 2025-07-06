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
        # Strip leading whitespace but preserve internal whitespace
        line = line.lstrip()

        # Check for empty or whitespace-only lines
        if not line or not line.strip():
            raise EnvistParseError("Empty or whitespace-only line")

        # Check for lines that start with equals (no key)
        if line.strip().startswith("="):
            raise EnvistParseError("Line cannot start with '=' (missing key)")

        # Handle lines without equals sign
        if "=" not in line:
            # Only accept as key with empty value if line is just whitespace or a simple identifier
            key = line.strip()
            if not key:
                raise EnvistParseError("Key cannot be empty")

            # Check if it looks like a valid environment variable key
            # Only allow simple identifiers without spaces for keys without values
            if " " in key or not key.replace("_", "").replace("-", "").isalnum():
                raise EnvistParseError(
                    f"Invalid line format: '{line.strip()}' (missing '=' assignment)"
                )

            # Return empty value for keys without equals
            return key, "", None

        # Parse type annotations with balanced brackets
        # Look for pattern: KEY<...>=value where <...> contains balanced brackets
        # Use regex to match the proper pattern first - preserve whitespace in value for str types
        type_annotation_pattern = r"^([^<>=]+)<([^<>]+(?:<[^<>]*>[^<>]*)*)>=(.*)$"
        type_match = re.match(type_annotation_pattern, line)

        # Also check for colon syntax: KEY:type=value
        colon_annotation_pattern = r"^([^:=]+):([^:=]+)=(.*)$"
        colon_match = re.match(colon_annotation_pattern, line)

        if type_match:
            key, cast_type, value = type_match.groups()
            key = key.strip()
            cast_type = cast_type.strip()
            # For string types, preserve whitespace in value
            if cast_type.lower() == "str":
                value = value if value else ""
            else:
                value = value.strip() if value else ""

            # Validate key format
            if not key:
                raise EnvistParseError("Key cannot be empty")

            # Validate nested type syntax
            if not EnvValidator._validate_type_syntax(cast_type):
                raise EnvistParseError(f"Invalid type syntax: {cast_type}")

            # Remove quotes from values
            value = EnvValidator._remove_quotes(value)

            # Check empty value constraint
            if not accept_empty and not value:
                raise EnvistParseError(f"Empty value")

            return key, value, cast_type
        elif colon_match:
            key, cast_type, value = colon_match.groups()
            key = key.strip()
            cast_type = cast_type.strip()
            # For string types, preserve whitespace in value
            if cast_type.lower() == "str":
                value = value if value else ""
            else:
                value = value.strip() if value else ""

            # Validate key format
            if not key:
                raise EnvistParseError("Key cannot be empty")

            # Validate type syntax (simpler validation for colon syntax)
            if not cast_type or not cast_type.replace("_", "").isalnum():
                raise EnvistParseError(f"Invalid type syntax: {cast_type}")

            # Remove quotes from values
            value = EnvValidator._remove_quotes(value)

            # Check empty value constraint
            if not accept_empty and not value:
                raise EnvistParseError(f"Empty value")

            return key, value, cast_type

        # Fallback to more complex bracket matching for deeply nested types
        # Only if the pattern looks like a valid type annotation format
        if "<" in line and ">" in line and "=" in line:
            # Check if '<' appears before '=' and after a valid identifier
            equals_pos = line.find("=")
            first_bracket_pos = line.find("<")

            # Only proceed if < comes before = and after some valid characters
            if first_bracket_pos > 0 and first_bracket_pos < equals_pos:
                key = line[:first_bracket_pos].strip()

                # Validate key format
                if not key:
                    raise EnvistParseError("Key cannot be empty")

                # Find the matching closing bracket
                bracket_count = 0
                close_bracket_pos = -1
                for i in range(first_bracket_pos, len(line)):
                    if line[i] == "<":
                        bracket_count += 1
                    elif line[i] == ">":
                        bracket_count -= 1
                        if bracket_count == 0:
                            close_bracket_pos = i
                            break

                if close_bracket_pos > first_bracket_pos:
                    cast_type = line[first_bracket_pos + 1 : close_bracket_pos].strip()
                    remainder = line[close_bracket_pos + 1 :].strip()

                    # Check for extra closing brackets in remainder before =
                    if ">" in remainder.split("=")[0]:
                        raise EnvistParseError(
                            f"Invalid type syntax: extra closing brackets in {line}"
                        )

                    if remainder.startswith("="):
                        raw_value = remainder[1:]
                        # For string types, preserve whitespace in value
                        if cast_type.lower() == "str":
                            value = raw_value if raw_value else ""
                        else:
                            value = raw_value.strip() if raw_value else ""
                        # Remove quotes from values
                        value = EnvValidator._remove_quotes(value)

                        # Check empty value constraint
                        if not accept_empty and not value:
                            raise EnvistParseError(f"Empty value")

                        # Validate nested type syntax
                        if not EnvValidator._validate_type_syntax(cast_type):
                            raise EnvistParseError(f"Invalid type syntax: {cast_type}")

                        return key, value, cast_type
                    else:
                        # Has type annotation but no equals after it
                        raise EnvistParseError(
                            f"Invalid type annotation format: {line}"
                        )
                else:
                    # Unmatched brackets
                    raise EnvistParseError(
                        f"Invalid type syntax: unmatched brackets in {line}"
                    )
            # If < and > exist but not in the right position, treat as simple line

        # Try to match simple pattern: KEY = value (always use permissive regex)
        simple_pattern = r"(.+?)\s*=\s*(.*)"

        match = re.search(simple_pattern, line)
        if match:
            key, value = match.groups()
            key = key.strip()
            value = value.strip() if value else ""

            # Validate key format
            if not key:
                raise EnvistParseError("Key cannot be empty")

            # Remove quotes from values
            value = EnvValidator._remove_quotes(value)
            cast_type = None

            # Check empty value constraint after parsing
            if not accept_empty and not value:
                raise EnvistParseError(f"Empty value")
        else:
            raise EnvistParseError(f"Invalid line format: {line}")

        return key, value, cast_type

        # Remove quotes if present
        value = EnvValidator._remove_quotes(value)

        return key, value, cast_type

    @staticmethod
    def _validate_type_syntax(type_str: str) -> bool:
        """Validate nested type syntax"""
        if not type_str:
            return False

        # Check for balanced angle brackets
        bracket_count = 0
        for char in type_str:
            if char == "<":
                bracket_count += 1
            elif char == ">":
                bracket_count -= 1
                if bracket_count < 0:
                    return False

        if bracket_count != 0:
            return False

        # Check for obviously invalid patterns
        if "<>" in type_str or type_str.startswith("<"):
            return False

        # Check for multiple type annotations at the same level like "list<int><str>"
        # This is more sophisticated - we need to check if there are multiple complete
        # type expressions at the top level

        # Remove whitespace for analysis
        clean_str = "".join(type_str.split())

        # If there are no brackets, it's a simple type - valid
        if "<" not in clean_str:
            return True

        # For expressions with brackets, we need to ensure it follows valid patterns
        # Valid: list<int>, dict<str,int>, list<list<int>>, etc.
        # Invalid: list<int><str>, list<>, <int>, etc.

        # Check for the pattern: type<inner> where inner can be nested
        import re

        # This pattern allows nested brackets
        pattern = r"^[a-zA-Z_][a-zA-Z0-9_]*<.+>$"
        if not re.match(pattern, clean_str):
            return False

        # Check that we don't have multiple top-level brackets like list<int><str>
        # Count angle bracket groups at top level
        top_level_groups = 0
        bracket_depth = 0
        in_group = False

        for char in clean_str:
            if char == "<":
                if bracket_depth == 0:
                    if in_group:
                        # Starting a new group while already in one at top level
                        return False
                    in_group = True
                    top_level_groups += 1
                bracket_depth += 1
            elif char == ">":
                bracket_depth -= 1
                if bracket_depth == 0:
                    in_group = False

        # Should have exactly one top-level bracket group
        return top_level_groups == 1

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

    @staticmethod
    def _validate_key_format(key: str) -> bool:
        """Validate environment variable key format

        Args:
            key: Key to validate

        Returns:
            True if key format is valid, False otherwise
        """
        if not key:
            return False

        # Key should start with letter or underscore
        if not (key[0].isalpha() or key[0] == "_"):
            return False

        # Key should only contain alphanumeric characters and underscores
        for char in key:
            if not (char.isalnum() or char == "_"):
                return False

        return True
