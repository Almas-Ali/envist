"""Additional tests to cover specific missing lines in parser.py"""

import os
import tempfile

import pytest

from envist import Envist
from envist.core.exceptions import EnvistCastError


class TestParserCoverage:
    """Tests to cover specific missing lines in parser.py"""

    def test_empty_value_casting_failure_reraise(self):
        """Test re-raising of casting errors for empty values (lines 130-135)"""
        
        # Create a custom type caster that will fail on empty values
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            # Create a scenario where empty value casting will fail
            f.write("EMPTY_CUSTOM <invalid_type> = \n")
            f.flush()
            temp_file = f.name

        try:
            # This should trigger a casting error that gets re-raised
            with pytest.raises(EnvistCastError):
                Envist(temp_file, accept_empty=True)
        finally:
            os.unlink(temp_file)

    def test_save_method_example_file_creation(self):
        """Test save method example file creation with both pretty options"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("TEST_VAR1=value1\nTEST_VAR2=value2\n")
            f.flush()
            temp_file = f.name

        try:
            env = Envist(temp_file)
            
            # Test with pretty=True and example_file=True (lines 329-335)
            env.save(pretty=True, example_file=True)
            
            example_file = os.path.splitext(temp_file)[0] + ".example"
            assert os.path.exists(example_file)
            
            with open(example_file, 'r') as f:
                content = f.read()
                # Should contain pretty formatted empty values
                assert "TEST_VAR1 = \n" in content
                assert "TEST_VAR2 = \n" in content
            
            os.unlink(example_file)
            
            # Test with pretty=False and example_file=True
            env.save(pretty=False, example_file=True)
            
            assert os.path.exists(example_file)
            
            with open(example_file, 'r') as f:
                content = f.read()
                # Should contain compact formatted empty values
                assert "TEST_VAR1=\n" in content
                assert "TEST_VAR2=\n" in content
            
            os.unlink(example_file)
            
        finally:
            os.unlink(temp_file)

    def test_annotations_property_with_various_types(self):
        """Test __annotations__ property with various value types (lines 388-389)"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("STRING_VAR <str> = hello\n")
            f.write("INT_VAR <int> = 42\n")
            f.write("BOOL_VAR <bool> = true\n")
            f.write("LIST_VAR <list> = 1,2,3\n")
            f.flush()
            temp_file = f.name

        try:
            env = Envist(temp_file)
            
            # Access the __annotations__ property
            annotations = env.__annotations__
            
            # Should include all environment variables with their types
            assert 'STRING_VAR' in annotations
            assert 'INT_VAR' in annotations
            assert 'BOOL_VAR' in annotations
            assert 'LIST_VAR' in annotations
            
            # Should also include parent annotations
            assert isinstance(annotations, dict)
            
        finally:
            os.unlink(temp_file)

    def test_getattr_with_underscore_attributes(self):
        """Test __getattr__ with attributes starting with underscore (lines 394-396)"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("NORMAL_VAR=value\n")
            f.flush()
            temp_file = f.name

        try:
            env = Envist(temp_file)
            
            # Test accessing non-existent attribute that starts with underscore
            with pytest.raises(AttributeError) as exc_info:
                _ = env._non_existent_internal_attr
            
            assert "object has no attribute '_non_existent_internal_attr'" in str(exc_info.value)
            
            # Test accessing non-existent normal attribute
            with pytest.raises(AttributeError) as exc_info:
                _ = env.non_existent_attr
            
            assert "object has no attribute 'non_existent_attr'" in str(exc_info.value)
            
        finally:
            os.unlink(temp_file)

    def test_setattr_with_path_attribute(self):
        """Test __setattr__ with 'path' attribute (lines 406-409)"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("VAR=value\n")
            f.flush()
            temp_file = f.name

        try:
            env = Envist(temp_file)
            
            # The 'path' attribute is a property with only a getter, 
            # so attempting to set it will fail
            # But the __setattr__ method does handle this case
            original_path = env.path
            
            # Test that attempting to set path goes through __setattr__
            # even though it will fail at the property level
            with pytest.raises(AttributeError):
                env.path = "new_path_value"
            
            # Path should remain unchanged
            assert env.path == original_path
            
        finally:
            os.unlink(temp_file)

    def test_setattr_during_uninitialized_state(self):
        """Test __setattr__ when _env doesn't exist yet"""
        
        # This is harder to test directly since it happens during __init__
        # The __delattr__ method prevents deletion of internal attributes
        # So we test the behavior indirectly
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("VAR=value\n")
            f.flush()
            temp_file = f.name

        try:
            env = Envist(temp_file)
            
            # Test that we can't delete internal attributes
            with pytest.raises(AttributeError) as exc_info:
                del env._env
            assert "Cannot delete internal attribute '_env'" in str(exc_info.value)
            
            # Test setting a regular attribute after initialization
            env.test_attr = "test_value"
            assert env.get('test_attr') == "test_value"
            
        finally:
            os.unlink(temp_file)

    def test_delattr_internal_attribute_protection(self):
        """Test __delattr__ protection of internal attributes (lines 414-419)"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("DELETE_ME=value\n")
            f.flush()
            temp_file = f.name

        try:
            env = Envist(temp_file)
            
            # Test deleting internal attribute should raise error
            with pytest.raises(AttributeError) as exc_info:
                del env._env
            
            assert "Cannot delete internal attribute '_env'" in str(exc_info.value)
            
            # Test deleting non-existent environment variable
            with pytest.raises(AttributeError) as exc_info:
                del env.non_existent_var
            
            assert "object has no attribute 'non_existent_var'" in str(exc_info.value)
            
            # Test successful deletion of environment variable
            del env.DELETE_ME
            assert 'DELETE_ME' not in env._env
            
        finally:
            os.unlink(temp_file)

    def test_dir_method_includes_env_vars_and_methods(self):
        """Test __dir__ method includes both env vars and object methods (line 423)"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("ENV_VAR1=value1\nENV_VAR2=value2\n")
            f.flush()
            temp_file = f.name

        try:
            env = Envist(temp_file)
            
            # Get directory listing
            dir_result = dir(env)
            
            # Should include environment variables
            assert 'ENV_VAR1' in dir_result
            assert 'ENV_VAR2' in dir_result
            
            # Should include standard methods
            assert 'get' in dir_result
            assert 'set' in dir_result
            assert 'unset' in dir_result
            assert 'save' in dir_result
            assert 'reload' in dir_result
            
            # Should be a list
            assert isinstance(dir_result, list)
            
        finally:
            os.unlink(temp_file)

    def test_complex_attribute_access_scenarios(self):
        """Test complex attribute access scenarios"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("ATTR_VAR=original_value\n")
            f.flush()
            temp_file = f.name

        try:
            env = Envist(temp_file)
            
            # Test attribute-style access of existing env var
            assert env.ATTR_VAR == "original_value"
            
            # Test attribute-style setting of new env var
            env.NEW_ATTR_VAR = "new_value"
            assert env.get('NEW_ATTR_VAR') == "new_value"
            
            # Test that it's also accessible via attribute access
            assert env.NEW_ATTR_VAR == "new_value"
            
            # Test modifying existing via attribute access
            env.ATTR_VAR = "modified_value"
            assert env.get('ATTR_VAR') == "modified_value"
            
        finally:
            os.unlink(temp_file)

    def test_value_none_handling_in_various_scenarios(self):
        """Test handling of None values in various scenarios"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("EMPTY_VAR=\n")  # This will be None when accept_empty=False
            f.flush()
            temp_file = f.name

        try:
            # Test with accept_empty=False (default)
            env = Envist(temp_file, accept_empty=False)
            
            # Empty values should result in None being stored
            # and handled correctly in various contexts
            empty_value = env.get('EMPTY_VAR')
            
            # Test attribute access of None value
            if 'EMPTY_VAR' in env._env:
                attr_value = env.EMPTY_VAR
                assert attr_value == empty_value
            
        finally:
            os.unlink(temp_file)
