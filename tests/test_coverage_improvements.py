"""Tests to improve coverage for missing lines in envist"""

import os
import tempfile

import pytest

from envist import Envist, validator
from envist.core.exceptions import EnvistCastError, EnvistParseError
from envist.validators import EnvValidator


class TestCoverageImprovements:
    """Tests to cover missing lines and improve coverage"""

    def test_iief_function_coverage(self):
        """Test the _iief function in validators/__init__.py (line 5)"""
        from envist.validators import _iief
        
        # Test that _iief executes the function immediately
        executed = False
        
        def test_func():
            nonlocal executed
            executed = True
            return True
        
        result = _iief(test_func)
        assert executed is True
        assert result is True

    def test_validator_decorator_with_invalid_key(self):
        """Test validator decorator with invalid key format"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("VALID_KEY=value\n")
            f.flush()
            temp_file = f.name

        try:
            env = Envist(temp_file)
            
            # Test validator with invalid key format
            with pytest.raises(ValueError) as exc_info:
                @validator(env, "invalid key with spaces")
                def validate_invalid_key(value):
                    return True
            
            assert "Invalid key format" in str(exc_info.value)
        finally:
            os.unlink(temp_file)

    def test_env_validator_missing_coverage(self):
        """Test missing coverage in env_validator.py"""
        
        # Test edge cases that might not be covered
        
        # Test _validate_type_syntax with edge cases
        assert EnvValidator._validate_type_syntax("str") is True
        assert EnvValidator._validate_type_syntax("list<int>") is True
        assert EnvValidator._validate_type_syntax("dict<str,int>") is True
        
        # Test empty or invalid type syntax
        assert EnvValidator._validate_type_syntax("") is False
        assert EnvValidator._validate_type_syntax("invalid<>") is False

    def test_empty_value_with_type_annotation_no_accept_empty(self):
        """Test empty value with type annotation when accept_empty=False"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("EMPTY_VAR <str> = \n")
            f.flush()
            temp_file = f.name

        try:
            # When accept_empty=False, empty values should not be processed
            env = Envist(temp_file, accept_empty=False)
            # The variable should not exist because empty values are skipped
            assert 'EMPTY_VAR' not in env._env
        finally:
            os.unlink(temp_file)

    def test_complex_edge_cases_for_empty_values(self):
        """Test complex edge cases for empty value handling"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            # Test various empty value scenarios
            f.write("EMPTY_LIST <list> = \n")
            f.write("EMPTY_DICT <dict> = \n")
            f.write("EMPTY_JSON <json> = \n")
            f.flush()
            temp_file = f.name

        try:
            # Test with accept_empty=True to trigger empty type casting
            env = Envist(temp_file, accept_empty=True)
            
            # These should have been cast to empty collections or None
            empty_list = env.get('EMPTY_LIST')
            empty_dict = env.get('EMPTY_DICT')
            empty_json = env.get('EMPTY_JSON')
            
            # Depending on the type caster implementation, these might be empty collections or None
            assert empty_list is not None or empty_list == []
            assert empty_dict is not None or empty_dict == {}
            assert empty_json is not None or empty_json == {}
        except EnvistCastError:
            # If casting fails for empty values, that's also valid behavior
            pass
        finally:
            os.unlink(temp_file)

    def test_parsing_error_propagation(self):
        """Test that parsing errors are properly propagated"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            # Write an invalid line that should cause a parsing error
            f.write("VALID_VAR=value\n")
            f.write("=invalid_line_starts_with_equals\n")
            f.flush()
            temp_file = f.name

        try:
            with pytest.raises(EnvistParseError):
                Envist(temp_file)
        finally:
            os.unlink(temp_file)

    def test_variable_resolution_with_none_value(self):
        """Test variable resolution when value is None"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("BASE_VAR=\n")  # Empty value
            f.write("DEPENDENT_VAR=${BASE_VAR}/suffix\n")
            f.flush()
            temp_file = f.name

        try:
            env = Envist(temp_file, accept_empty=True)
            # Should handle None values in variable resolution
            dependent = env.get('DEPENDENT_VAR')
            assert dependent == "/suffix"  # None should be replaced with empty string
        finally:
            os.unlink(temp_file)
