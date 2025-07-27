"""Tests for the validator decorator functionality"""

import os
import tempfile
from pathlib import Path

import pytest

from envist import Envist, validator


class TestValidatorDecorator:
    """Test cases for the @validator decorator"""

    def setup_method(self):
        """Set up test environment for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.env_file = Path(self.temp_dir) / ".env.test"

        # Create a test .env file
        env_content = """
# Test environment variables
NAME=John Doe
AGE<int>=25
HEIGHT<float>=5.9
IS_ACTIVE<bool>=true
DEBUG<bool>=false
EMPTY_STRING=
COUNT<int>=0
INVALID_AGE<int>=-1
LONG_NAME=ThisIsAReallyLongNameThatShouldExceedLimits
"""
        with open(self.env_file, "w") as f:
            f.write(env_content.strip())

        self.env = Envist(str(self.env_file), accept_empty=True)

    def teardown_method(self):
        """Clean up after each test"""
        if self.env_file.exists():
            self.env_file.unlink()
        os.rmdir(self.temp_dir)

    def test_validator_decorator_valid_key_valid_value(self):
        """Test validator decorator with valid key and valid value"""

        @validator(self.env, "AGE")
        def validate_age(value: int) -> bool:
            """Validate age to be a positive integer."""
            if value <= 0:
                raise ValueError("Age must be a positive integer.")
            return True

        # The decorator executes immediately (IIFE) and should return True
        assert validate_age is True

    def test_validator_decorator_valid_key_invalid_value(self):
        """Test validator decorator with valid key but invalid value"""

        with pytest.raises(ValueError, match="Age must be a positive integer"):

            @validator(self.env, "INVALID_AGE")
            def validate_invalid_age(value: int) -> bool:
                """Validate age to be a positive integer."""
                if value <= 0:
                    raise ValueError("Age must be a positive integer.")
                return True

    def test_validator_decorator_invalid_key_format(self):
        """Test validator decorator with invalid key format"""

        with pytest.raises(ValueError, match="Invalid key format"):

            @validator(self.env, "123_INVALID_KEY")
            def validate_invalid_key(value: str) -> bool:
                """This should fail due to invalid key format."""
                return True

    def test_validator_decorator_nonexistent_key(self):
        """Test validator decorator with nonexistent key"""

        with pytest.raises(ValueError, match="Key does not exist"):
            @validator(self.env, "NONEXISTENT_KEY")
            def validate_nonexistent(value) -> bool:
                """Validate nonexistent key - should get None."""
                # env.get() returns None for nonexistent keys
                if value is None:
                    raise ValueError("Key does not exist")
                return True

    def test_validator_decorator_string_validation(self):
        """Test validator decorator with string validation"""

        @validator(self.env, "NAME")
        def validate_name(value: str) -> bool:
            """Validate name to be non-empty."""
            if not value or len(value.strip()) == 0:
                raise ValueError("Name cannot be empty.")
            if len(value) > 50:
                raise ValueError("Name too long.")
            return True

        assert validate_name is True

    def test_validator_decorator_string_validation_too_long(self):
        """Test validator decorator with string that's too long"""

        with pytest.raises(ValueError, match="Name too long"):

            @validator(self.env, "LONG_NAME")
            def validate_long_name(value: str) -> bool:
                """Validate name length."""
                if len(value) > 20:
                    raise ValueError("Name too long.")
                return True

    def test_validator_decorator_boolean_validation(self):
        """Test validator decorator with boolean validation"""

        @validator(self.env, "IS_ACTIVE")
        def validate_boolean(value: bool) -> bool:
            """Validate boolean value."""
            if not isinstance(value, bool):
                raise ValueError("Value must be a boolean.")
            return True

        assert validate_boolean is True

    def test_validator_decorator_float_validation(self):
        """Test validator decorator with float validation"""

        @validator(self.env, "HEIGHT")
        def validate_height(value: float) -> bool:
            """Validate height to be reasonable."""
            if value <= 0 or value > 10:
                raise ValueError("Height must be between 0 and 10 feet.")
            return True

        assert validate_height is True

    def test_validator_decorator_float_validation_out_of_range(self):
        """Test validator decorator with float out of range"""
        # Add a height that's out of range
        self.env.set("TALL_HEIGHT", 15.0)

        with pytest.raises(ValueError, match="Height must be between 0 and 10 feet"):

            @validator(self.env, "TALL_HEIGHT")
            def validate_tall_height(value: float) -> bool:
                """Validate height to be reasonable."""
                if value <= 0 or value > 10:
                    raise ValueError("Height must be between 0 and 10 feet.")
                return True

    def test_validator_decorator_empty_string_handling(self):
        """Test validator decorator with empty string values"""

        @validator(self.env, "EMPTY_STRING")
        def validate_empty_string(value) -> bool:
            """Validate empty string handling."""
            # With accept_empty=True, empty values are stored as None
            if value is None:
                return True
            raise ValueError("Expected None value for empty string.")

        assert validate_empty_string is True

    def test_validator_decorator_zero_value_handling(self):
        """Test validator decorator with zero values"""

        @validator(self.env, "COUNT")
        def validate_count(value: int) -> bool:
            """Validate count allowing zero."""
            if value < 0:
                raise ValueError("Count cannot be negative.")
            return True

        assert validate_count is True

    def test_validator_decorator_multiple_validators_same_key(self):
        """Test multiple validators on the same key"""

        # First validator - check type
        @validator(self.env, "AGE")
        def validate_age_type(value: int) -> bool:
            """Validate age type."""
            if not isinstance(value, int):
                raise ValueError("Age must be an integer.")
            return True

        # Second validator - check range
        @validator(self.env, "AGE")
        def validate_age_range(value: int) -> bool:
            """Validate age range."""
            if value < 18 or value > 120:
                raise ValueError("Age must be between 18 and 120.")
            return True

        assert validate_age_type is True
        assert validate_age_range is True

    def test_validator_decorator_custom_validation_logic(self):
        """Test validator decorator with custom validation logic"""

        @validator(self.env, "NAME")
        def validate_name_format(value: str) -> bool:
            """Validate name format - must contain only letters and spaces."""
            import re

            if not re.match(r"^[a-zA-Z\s]+$", value):
                raise ValueError("Name must contain only letters and spaces.")
            return True

        assert validate_name_format is True

    def test_validator_decorator_with_special_characters_in_key(self):
        """Test validator decorator with special characters in key names"""

        # Valid key with underscores
        self.env.set("VALID_KEY_NAME", "test")

        @validator(self.env, "VALID_KEY_NAME")
        def validate_valid_key(value: str) -> bool:
            """Validate valid key with underscores."""
            return True

        assert validate_valid_key is True

        # Invalid key with special characters
        with pytest.raises(ValueError, match="Invalid key format"):

            @validator(self.env, "INVALID-KEY-NAME")
            def validate_invalid_key_dash(value: str) -> bool:
                """This should fail due to dashes in key."""
                return True

    def test_validator_decorator_preserves_function_metadata(self):
        """Test that validator decorator executes validation immediately"""

        @validator(self.env, "NAME")
        def validate_with_metadata(value: str) -> bool:
            """This function executes immediately due to IIFE."""
            return True

        # Due to IIFE, validate_with_metadata is now the return value (True)
        assert validate_with_metadata is True

    def test_validator_decorator_with_type_mismatches(self):
        """Test validator decorator when type casting creates mismatches"""

        # Create a string value that should be an int
        self.env.set("STRING_NUMBER", "not_a_number")

        @validator(self.env, "STRING_NUMBER")
        def validate_string_as_number(value) -> bool:
            """Validate when type casting might fail."""
            # The value should be a string since casting will fail
            if not isinstance(value, str):
                raise ValueError("Expected string value due to casting failure.")
            return True

        assert validate_string_as_number is True
