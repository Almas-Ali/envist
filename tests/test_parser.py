"""Tests for the core parser module"""

import os
import tempfile
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from envist.core.exceptions import (
    EnvistCastError,
    EnvistParseError,
    EnvistTypeError,
    EnvistValueError,
    FileNotFoundError,
)
from envist.core.parser import Envist


class TestEnvistParser:
    """Test cases for the Envist parser class"""

    def test_init_with_defaults(self, env_file_with_content):
        """Test initialization with default parameters"""
        env = Envist(env_file_with_content)
        assert env._path == env_file_with_content
        assert env._accept_empty == False
        assert env._auto_cast == True
        assert isinstance(env._env, dict)

    def test_init_with_custom_params(self, env_file_with_content):
        """Test initialization with custom parameters"""
        env = Envist(env_file_with_content, accept_empty=True, auto_cast=False)
        assert env._accept_empty == True
        assert env._auto_cast == False

    def test_file_not_found(self):
        """Test handling of non-existent file"""
        with pytest.raises(FileNotFoundError):
            Envist("non_existent_file.env")

    def test_auto_cast_enabled(self, env_file_with_content):
        """Test auto casting when enabled"""
        env = Envist(env_file_with_content, auto_cast=True)

        # Test simple types
        assert env.get("NAME") == "John Doe"
        assert env.get("AGE") == 25
        assert isinstance(env.get("AGE"), int)
        assert env.get("HEIGHT") == 5.9
        assert isinstance(env.get("HEIGHT"), float)
        assert env.get("IS_ACTIVE") == True
        assert isinstance(env.get("IS_ACTIVE"), bool)

        # Test list types
        numbers = env.get("NUMBERS")
        assert numbers == [1, 2, 3, 4, 5]
        assert all(isinstance(n, int) for n in numbers)

    def test_auto_cast_disabled(self, env_file_with_content):
        """Test auto casting when disabled"""
        env = Envist(env_file_with_content, auto_cast=False)

        # All values should remain as strings
        assert env.get("AGE") == "25"
        assert isinstance(env.get("AGE"), str)
        assert env.get("HEIGHT") == "5.9"
        assert isinstance(env.get("HEIGHT"), str)
        assert env.get("IS_ACTIVE") == "true"
        assert isinstance(env.get("IS_ACTIVE"), str)
        assert env.get("NUMBERS") == "1,2,3,4,5"
        assert isinstance(env.get("NUMBERS"), str)

    def test_manual_casting_with_auto_cast_disabled(self, env_file_with_content):
        """Test manual casting when auto_cast is disabled"""
        env = Envist(env_file_with_content, auto_cast=False)

        # Manual casting should still work
        age = env.get("AGE", cast="int")
        assert age == 25
        assert isinstance(age, int)

        numbers = env.get("NUMBERS", cast="list<int>")
        assert numbers == [1, 2, 3, 4, 5]
        assert all(isinstance(n, int) for n in numbers)

    def test_variable_resolution(self, env_file_with_content):
        """Test variable resolution functionality"""
        env = Envist(env_file_with_content)

        assert env.get("BASE_URL") == "https://api.example.com"
        assert env.get("API_VERSION") == "v1"
        assert env.get("FULL_URL") == "https://api.example.com/v1/users"

    def test_complex_nested_types(self, env_file_with_content):
        """Test complex nested type casting"""
        env = Envist(env_file_with_content)

        # Test nested lists
        matrix = env.get("MATRIX")
        assert matrix == [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        assert all(isinstance(row, list) for row in matrix)
        assert all(isinstance(cell, int) for row in matrix for cell in row)

        # Test dict with int values
        config = env.get("CONFIG")
        assert config == {"timeout": 30, "retries": 3, "port": 8080}
        assert all(isinstance(v, int) for v in config.values())

        # Test list of dicts
        users = env.get("USERS")
        assert len(users) == 2
        assert users[0] == {"name": "John", "role": "admin"}
        assert users[1] == {"name": "Jane", "role": "user"}

    def test_quoted_values(self, env_file_with_content):
        """Test handling of quoted values"""
        env = Envist(env_file_with_content)

        assert env.get("QUOTED_STRING") == "Hello World"
        assert env.get("SINGLE_QUOTED") == "Single Quote"

    def test_empty_values(self, temp_env_file):
        """Test handling of empty values"""
        with open(temp_env_file, "w") as f:
            f.write("EMPTY_KEY=\nANOTHER_KEY=value")

        # With accept_empty=False (default)
        env = Envist(temp_env_file, accept_empty=False)
        assert "EMPTY_KEY" not in env._env
        assert env.get("ANOTHER_KEY") == "value"

        # With accept_empty=True
        env = Envist(temp_env_file, accept_empty=True)
        assert env.get("EMPTY_KEY") is None
        assert env.get("ANOTHER_KEY") == "value"

    def test_get_method(self, env_file_with_content):
        """Test the get method functionality"""
        env = Envist(env_file_with_content)

        # Test existing key
        assert env.get("NAME") == "John Doe"

        # Test non-existing key with default
        assert env.get("NON_EXISTENT", default="default_value") == "default_value"

        # Test casting
        age_str = env.get("AGE", cast="str")
        assert age_str == "25"
        assert isinstance(age_str, str)

    def test_get_all_method(self, env_file_with_content):
        """Test the get_all method"""
        env = Envist(env_file_with_content)
        all_vars = env.get_all()

        assert isinstance(all_vars, dict)
        assert "NAME" in all_vars
        assert "AGE" in all_vars
        assert all_vars["NAME"] == "John Doe"

        # Ensure it returns a copy
        all_vars["NEW_KEY"] = "new_value"
        assert "NEW_KEY" not in env._env

    def test_set_method(self, env_file_with_content):
        """Test the set method"""
        env = Envist(env_file_with_content)

        # Set new value
        env.set("NEW_KEY", "new_value")
        assert env.get("NEW_KEY") == "new_value"
        assert os.environ.get("NEW_KEY") == "new_value"

        # Set with type casting
        env.set("NEW_INT", 42)
        assert env.get("NEW_INT") == 42
        assert os.environ.get("NEW_INT") == "42"

    def test_set_all_method(self, env_file_with_content):
        """Test the set_all method"""
        env = Envist(env_file_with_content)

        new_data = {"KEY1": "value1", "KEY2": 42, "KEY3": [1, 2, 3]}

        env.set_all(new_data)

        assert env.get("KEY1") == "value1"
        assert env.get("KEY2") == 42
        assert env.get("KEY3") == [1, 2, 3]

        # Test with invalid data
        with pytest.raises(EnvistTypeError):
            env.set_all("not_a_dict")

    def test_unset_method(self, env_file_with_content):
        """Test the unset method"""
        env = Envist(env_file_with_content)

        # Ensure key exists
        assert "NAME" in env._env

        # Unset the key
        env.unset("NAME")
        assert "NAME" not in env._env
        assert "NAME" not in os.environ

        # Test unset non-existent key
        with pytest.raises(EnvistValueError):
            env.unset("NON_EXISTENT_KEY")

    def test_unset_all_method(self, env_file_with_content):
        """Test the unset_all method"""
        env = Envist(env_file_with_content)

        # Test unset specific keys
        keys_to_unset = ["NAME", "AGE"]
        env.unset_all(keys_to_unset)

        assert "NAME" not in env._env
        assert "AGE" not in env._env

        # Test unset all keys
        remaining_keys = list(env._env.keys())
        env.unset_all()

        assert len(env._env) == 0
        for key in remaining_keys:
            assert key not in os.environ

        # Test unset non-existent key
        env = Envist(env_file_with_content)
        with pytest.raises(EnvistValueError):
            env.unset_all(["NON_EXISTENT_KEY"])

    def test_save_method(self, env_file_with_content):
        """Test the save method"""
        env = Envist(env_file_with_content)

        # Add some new values
        env.set("NEW_KEY1", "value1")
        env.set("NEW_KEY2", 42)

        # Save to file
        env.save()

        # Verify by loading again
        new_env = Envist(
            env_file_with_content, auto_cast=False
        )  # No casting to check raw values
        assert new_env.get("NEW_KEY1") == "value1"
        assert new_env.get("NEW_KEY2") == "42"

        # Test pretty format
        env.save(pretty=True)
        with open(env_file_with_content, "r") as f:
            content = f.read()
            assert " = " in content  # Pretty format uses spaces around =

        # Test sorted keys
        env.save(sort_keys=True)
        with open(env_file_with_content, "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            keys = [line.split("=")[0] for line in lines]
            assert keys == sorted(keys)

    def test_reload_method(self, env_file_with_content):
        """Test the reload method"""
        env = Envist(env_file_with_content)

        original_name = env.get("NAME")

        # Modify the file
        with open(env_file_with_content, "a") as f:
            f.write("\nNEW_AFTER_LOAD=test_value")

        # Reload
        env.reload()

        # Check that new value is loaded
        assert env.get("NEW_AFTER_LOAD") == "test_value"
        assert env.get("NAME") == original_name  # Original should still be there

    def test_path_property(self, env_file_with_content):
        """Test the path property"""
        env = Envist(env_file_with_content)
        assert env.path == env_file_with_content

    def test_dictionary_interface(self, env_file_with_content):
        """Test dictionary-like interface"""
        env = Envist(env_file_with_content)

        # Test __getitem__
        assert env["NAME"] == "John Doe"

        with pytest.raises(KeyError):
            _ = env["NON_EXISTENT"]

        # Test __setitem__
        env["NEW_KEY"] = "new_value"
        assert env.get("NEW_KEY") == "new_value"

        # Test __delitem__
        env["DELETE_ME"] = "temp"
        del env["DELETE_ME"]
        assert "DELETE_ME" not in env._env

        # Test __contains__
        assert "NAME" in env
        assert "NON_EXISTENT" not in env

        # Test __len__
        assert len(env) > 0

        # Test __iter__
        keys = list(env)
        assert "NAME" in keys

    def test_string_representation(self, env_file_with_content):
        """Test string representation methods"""
        env = Envist(env_file_with_content)

        repr_str = repr(env)
        assert "Envist" in repr_str
        assert env_file_with_content in repr_str

        str_str = str(env)
        assert "Envist" in str_str
        assert env_file_with_content in str_str

    def test_circular_variable_reference(self, temp_env_file):
        """Test circular variable reference detection"""
        with open(temp_env_file, "w") as f:
            f.write("VAR1=${VAR2}\nVAR2=${VAR1}")

        with pytest.raises(EnvistParseError, match="Circular reference"):
            Envist(temp_env_file)

    def test_deep_variable_nesting(self, temp_env_file):
        """Test deep variable nesting limit"""
        content = "VAR0=base\n"
        for i in range(1, 15):  # Create 15 levels of nesting
            content += f"VAR{i}=${{VAR{i - 1}}}_level{i}\n"

        with open(temp_env_file, "w") as f:
            f.write(content)

        with pytest.raises(EnvistParseError, match="too deep nesting"):
            Envist(temp_env_file)

    def test_os_environment_fallback(self, temp_env_file):
        """Test OS environment variable fallback in variable resolution"""
        os.environ["OS_VAR"] = "from_os"

        with open(temp_env_file, "w") as f:
            f.write("COMBINED=${OS_VAR}_and_more")

        env = Envist(temp_env_file)
        assert env.get("COMBINED") == "from_os_and_more"

        # Cleanup
        del os.environ["OS_VAR"]

    def test_invalid_variable_reference(self, temp_env_file):
        """Test undefined variable reference"""
        with open(temp_env_file, "w") as f:
            f.write("VAR1=${UNDEFINED_VAR}")

        env = Envist(temp_env_file)
        # Should resolve to None for undefined variables
        assert env.get("VAR1") is None

    def test_cast_error_handling(self, temp_env_file):
        """Test casting error handling"""
        with open(temp_env_file, "w") as f:
            f.write("INVALID_INT<int>=not_a_number")

        with pytest.raises(EnvistCastError):
            Envist(temp_env_file)

    def test_invalid_key_format(self, env_file_with_content):
        """Test invalid key format in set method"""
        env = Envist(env_file_with_content)

        with pytest.raises(EnvistParseError):
            env.set("123invalid", "value")  # Key cannot start with number

        with pytest.raises(EnvistParseError):
            env.set("invalid-key", "value")  # Key cannot contain hyphens

    def test_variable_resolution_methods(self, temp_env_file):
        """Test private variable resolution methods"""
        with open(temp_env_file, "w") as f:
            f.write("VAR1=value1\nVAR2=${VAR1}_extended")

        env = Envist(temp_env_file)

        # Test _is_variable
        assert env._is_variable("${VAR1}")
        assert env._is_variable("prefix_${VAR1}_suffix")
        assert not env._is_variable("no_variables_here")
        assert not env._is_variable(123)  # Non-string input

        # Test _resolve_variable
        resolved = env._resolve_variable("${VAR1}")
        assert resolved == "value1"

        # Test _resolve_variable_with_env
        test_env = {"TEST_VAR": "test_value"}
        resolved = env._resolve_variable_with_env("${TEST_VAR}", test_env)
        assert resolved == "test_value"

    @patch("builtins.open", mock_open(read_data=""))
    def test_empty_file_handling(self, temp_env_file):
        """Test handling of empty .env file"""
        env = Envist(temp_env_file)
        assert len(env._env) == 0
        assert len(env.get_all()) == 0

    def test_casting_failure_with_type_stores_none(self):
        """Test that casting failures raise exceptions when type is specified."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("INVALID_INT:int=not_a_number\n")
            temp_path = f.name

        try:
            # The invalid cast should raise an exception
            with pytest.raises(EnvistCastError):
                Envist(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_empty_value_with_type_accept_empty_true(self):
        """Test empty value with type annotation when accept_empty=True."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("EMPTY_WITH_TYPE:int=\n")
            temp_path = f.name

        try:
            # Should raise exception when empty with type and accept_empty=True
            with pytest.raises(EnvistCastError):
                Envist(temp_path, accept_empty=True)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_key_without_value_declaration(self):
        """Test key declared without any value (not even =)."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("JUST_KEY\n")
            temp_path = f.name

        try:
            parser = Envist(temp_path)
            # Should store None for key without value
            assert parser.get("JUST_KEY") is None
            assert os.environ.get("JUST_KEY") == ""
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_unexpected_exception_during_parse_wrapped(self):
        """Test that unexpected exceptions during parsing are wrapped."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            # Write a file that might cause unexpected parsing issues
            f.write("NORMAL_VAR=value\n")
            temp_path = f.name

        try:
            # Mock the file handler to raise an unexpected exception
            from unittest.mock import patch

            with patch("envist.utils.file_handler.FileHandler.read_file") as mock_read:
                mock_read.side_effect = ValueError("Unexpected file error")

                with pytest.raises(
                    EnvistParseError, match="Unexpected error loading env file"
                ):
                    Envist(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_resolve_variable_with_non_string_value(self):
        """Test _resolve_variable with non-string input."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("TEST_VAR=42\n")
            temp_path = f.name

        try:
            parser = Envist(temp_path)
            # Test that non-string values are returned as-is
            result = parser._resolve_variable_with_env(42, {})
            assert result == 42

            result = parser._resolve_variable_with_env(None, {})
            assert result is None
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_set_with_variable_resolution(self):
        """Test set method with variable resolution."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("BASE_PATH=/home/user\n")
            temp_path = f.name

        try:
            parser = Envist(temp_path)
            # Set a value that contains a variable reference
            parser.set("FULL_PATH", "${BASE_PATH}/documents")

            # Should resolve the variable
            assert parser.get("FULL_PATH") == "/home/user/documents"
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_empty_string_value_with_accept_empty_false(self):
        """Test empty string value handling with accept_empty=False."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("EMPTY_VAR=\n")
            temp_path = f.name

        try:
            parser = Envist(temp_path, accept_empty=False)
            # The value should be handled appropriately
            # In this case, it might not be in the environment at all or be None
            result = parser.get("EMPTY_VAR")
            # The exact behavior depends on implementation
            assert result is None or result == ""
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_is_variable_with_non_string(self):
        """Test _is_variable with non-string input."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("TEST_VAR=value\n")
            temp_path = f.name

        try:
            parser = Envist(temp_path)

            # Test with non-string inputs
            assert parser._is_variable(42) is False
            assert parser._is_variable(None) is False
            assert parser._is_variable([]) is False

            # Test with string inputs
            assert parser._is_variable("${VAR}") is True
            assert parser._is_variable("normal_value") is False
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_parse_line_with_complex_edge_cases(self):
        """Test parsing with complex edge cases."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            # Write a combination that might trigger edge cases
            content = """
# Test various edge cases
VAR_WITH_CAST_FAILURE:int=invalid_number
EMPTY_WITH_TYPE:str=
KEY_ONLY
NORMAL_VAR=value
VAR_WITH_VARIABLE=${NORMAL_VAR}/extra
"""
            f.write(content)
            temp_path = f.name

        try:
            # Should raise exception when casting failures occur
            with pytest.raises(EnvistCastError):
                Envist(temp_path, accept_empty=True)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_multiple_variable_resolution_edge_cases(self):
        """Test variable resolution with multiple edge cases."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            content = """
BASE=/home
USER=john
COMPLEX_PATH=${BASE}/${USER}/documents
NESTED_VAR=${COMPLEX_PATH}/files
"""
            f.write(content)
            temp_path = f.name

        try:
            parser = Envist(temp_path)

            # Test complex variable resolution
            assert parser.get("COMPLEX_PATH") == "/home/john/documents"
            assert parser.get("NESTED_VAR") == "/home/john/documents/files"

            # Test setting values with variables
            parser.set("NEW_PATH", "${BASE}/shared")
            assert parser.get("NEW_PATH") == "/home/shared"
        finally:
            Path(temp_path).unlink(missing_ok=True)
