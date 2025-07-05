"""Edge case tests for complete coverage"""

import os
import tempfile
import pytest
from unittest.mock import patch, mock_open
from pathlib import Path

from envist import Envist
from envist.core.exceptions import *
from envist.utils.file_handler import FileHandler
from envist.utils.type_casters import TypeCaster
from envist.validators.env_validator import EnvValidator


class TestEdgeCases:
    """Test edge cases for 100% coverage"""
    
    def test_file_handler_edge_cases(self, temp_env_file):
        """Test FileHandler edge cases"""
        # Test with file containing only newlines
        with open(temp_env_file, 'w') as f:
            f.write('\n\n\n\n')
        
        lines = FileHandler.read_file(temp_env_file)
        assert lines == ['\n', '\n', '\n', '\n']
        
        filtered = FileHandler.filter_lines(lines)
        assert filtered == []
        
        # Test with mixed line endings
        with open(temp_env_file, 'wb') as f:
            f.write(b'VAR1=value1\r\nVAR2=value2\nVAR3=value3\r')
        
        lines = FileHandler.read_file(temp_env_file)
        filtered = FileHandler.filter_lines(lines)
        assert len(filtered) >= 2  # Should handle different line endings
    
    def test_type_caster_edge_cases(self):
        """Test TypeCaster edge cases"""
        caster = TypeCaster()
        
        # Test with non-string value to _is_variable equivalent
        assert caster._cast_simple_type(123, 'str') == '123'
        
        # Test CSV with complex content
        csv_result = caster._cast_to_csv('a,"b,c",d')
        assert csv_result == ['a', 'b,c', 'd']
        
        # Test JSON casting errors
        with pytest.raises(EnvistCastError):
            caster._cast_to_json('invalid json')
        
        # Test empty bracket list
        result = caster._parse_bracket_list('[]')
        assert result == []
        
        # Test nested bracket with empty content
        result = caster._parse_nested_bracket_structure('')
        assert result == []
        
        # Test dict value parsing with JSON error fallback
        result = caster._parse_dict_value('{"invalid": json}')
        assert result == '{"invalid": json}'  # Should fallback to string
        
        # Test smart split with empty input
        result = caster._smart_split('', ',')
        assert result == []
        
        # Test remove quotes with edge cases
        assert caster._remove_quotes('') == ''
        assert caster._remove_quotes('a') == 'a'
        assert caster._remove_quotes('"') == '"'
        
        # Test split type args with no comma
        result = caster._split_type_args('int')
        assert result == ['int']
        
        # Test apply type casting with tuple and set
        list_type = {'type': 'tuple', 'inner_type': {'type': 'int'}}
        result = caster._apply_type_casting('[1,2,3]', list_type)
        assert result == (1, 2, 3)
        
        set_type = {'type': 'set', 'inner_type': {'type': 'str'}}
        result = caster._apply_type_casting('[a,b,c]', set_type)
        assert result == {'a', 'b', 'c'}
    
    def test_validator_edge_cases(self):
        """Test EnvValidator edge cases"""
        # Test _validate_type_syntax with deeply nested valid syntax
        assert EnvValidator._validate_type_syntax('dict<str, list<dict<str, int>>>') is True
        
        # Test parse_line_with_cast with complex whitespace
        key, value, cast_type = EnvValidator.parse_line_with_cast(
            '   KEY   <   list < int >   >   =   value   ', accept_empty=True
        )
        assert key == 'KEY'
        assert value == 'value'
        assert cast_type == 'list < int >'
        
        # Test validate_key with edge cases
        assert EnvValidator.validate_key('_') is True
        assert EnvValidator.validate_key('a') is True
        assert EnvValidator.validate_key('A1_B2_C3') is True
        assert EnvValidator.validate_key('') is False
        
        # Test remove quotes with partial quotes
        assert EnvValidator._remove_quotes('"incomplete') == '"incomplete'
        assert EnvValidator._remove_quotes('incomplete"') == 'incomplete"'
    
    def test_parser_edge_cases(self, temp_env_file):
        """Test Envist parser edge cases"""
        # Test with file that becomes invalid after initial creation
        with open(temp_env_file, 'w') as f:
            f.write('VALID=value')
        
        env = Envist(temp_env_file)
        assert env.get('VALID') == 'value'
        
        # Test variable resolution with empty result
        with open(temp_env_file, 'w') as f:
            f.write('VAR1=${UNDEFINED}\nVAR2=prefix_${UNDEFINED}_suffix')
        
        env = Envist(temp_env_file)
        assert env.get('VAR1') == ''
        assert env.get('VAR2') == 'prefix__suffix'
        
        # Test set with invalid key
        with pytest.raises(EnvistParseError):
            env.set('123invalid', 'value')
        
        # Test unset with non-existent key
        with pytest.raises(EnvistValueError):
            env.unset('NON_EXISTENT')
        
        # Test unset_all with mixed existent/non-existent keys
        env.set('EXISTS', 'value')
        with pytest.raises(EnvistValueError):
            env.unset_all(['EXISTS', 'DOES_NOT_EXIST'])
    
    def test_parser_os_environment_edge_cases(self, temp_env_file):
        """Test OS environment variable edge cases"""
        # Set an OS environment variable
        os.environ['TEST_OS_VAR'] = 'from_os'
        
        try:
            with open(temp_env_file, 'w') as f:
                f.write('LOCAL_VAR=${TEST_OS_VAR}')
            
            env = Envist(temp_env_file)
            assert env.get('LOCAL_VAR') == 'from_os'
            
            # Test that unset removes from OS environment
            env.set('TEMP_VAR', 'temp_value')
            assert os.environ.get('TEMP_VAR') == 'temp_value'
            
            env.unset('TEMP_VAR')
            assert 'TEMP_VAR' not in os.environ
            
        finally:
            # Cleanup
            if 'TEST_OS_VAR' in os.environ:
                del os.environ['TEST_OS_VAR']
    
    def test_parser_boolean_edge_cases(self, temp_env_file):
        """Test boolean casting edge cases"""
        with open(temp_env_file, 'w') as f:
            f.write("""BOOL_TRUE_CAPS<bool>=TRUE
BOOL_YES<bool>=YES
BOOL_ON<bool>=ON
BOOL_ONE<bool>=1
BOOL_FALSE_CAPS<bool>=FALSE
BOOL_NO<bool>=NO
BOOL_OFF<bool>=OFF
BOOL_ZERO<bool>=0
BOOL_RANDOM<bool>=maybe""")
        
        env = Envist(temp_env_file)
        
        # True cases
        assert env.get('BOOL_TRUE_CAPS') is True
        assert env.get('BOOL_YES') is True
        assert env.get('BOOL_ON') is True
        assert env.get('BOOL_ONE') is True
        
        # False cases
        assert env.get('BOOL_FALSE_CAPS') is False
        assert env.get('BOOL_NO') is False
        assert env.get('BOOL_OFF') is False
        assert env.get('BOOL_ZERO') is False
        assert env.get('BOOL_RANDOM') is False
    
    def test_parser_variable_resolution_edge_cases(self, temp_env_file):
        """Test variable resolution edge cases"""
        with open(temp_env_file, 'w') as f:
            f.write("""VAR1=value1
VAR2=${VAR1}${VAR1}
VAR3=${VAR2}_${VAR1}
RECURSIVE_VAR=prefix_${RECURSIVE_VAR}_suffix""")
        
        # This should cause a circular reference error
        with pytest.raises(EnvistParseError, match="Circular reference"):
            Envist(temp_env_file)
    
    def test_parser_casting_edge_cases(self, temp_env_file):
        """Test type casting edge cases"""
        with open(temp_env_file, 'w') as f:
            f.write("""# Test various casting scenarios
NEGATIVE_INT<int>=-42
NEGATIVE_FLOAT<float>=-3.14
SCIENTIFIC<float>=1.5e-10
ZERO_INT<int>=0
ZERO_FLOAT<float>=0.0
EMPTY_LIST<list<str>>=
EMPTY_DICT<dict<str, str>>=
SINGLE_ITEM_LIST<list<int>>=42
BOOL_FROM_INT<bool>=1""")
        
        env = Envist(temp_env_file, accept_empty=True)
        
        assert env.get('NEGATIVE_INT') == -42
        assert env.get('NEGATIVE_FLOAT') == -3.14
        assert env.get('SCIENTIFIC') == 1.5e-10
        assert env.get('ZERO_INT') == 0
        assert env.get('ZERO_FLOAT') == 0.0
        assert env.get('EMPTY_LIST') == []
        assert env.get('EMPTY_DICT') == {}
        assert env.get('SINGLE_ITEM_LIST') == [42]
        assert env.get('BOOL_FROM_INT') is True
    
    def test_type_caster_complex_structures(self):
        """Test complex nested structure parsing"""
        caster = TypeCaster()
        
        # Test deeply nested list parsing
        deep_list = caster.cast_value('[[[1,2],[3,4]],[[5,6],[7,8]]]', 'list<list<list<int>>>')
        assert deep_list == [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
        
        # Test complex dict with nested types
        complex_dict = caster.cast_value(
            'users=[{"name":"John","age":30}],roles=["admin","user"]',
            'dict<str, list<str>>'
        )
        # Note: This will parse as strings, but structure should be preserved
        assert isinstance(complex_dict, dict)
        assert 'users' in complex_dict
        assert 'roles' in complex_dict
    
    def test_error_message_formatting(self, temp_env_file):
        """Test error message formatting"""
        # Test line number in error messages
        with open(temp_env_file, 'w') as f:
            f.write("""VALID=value
INVALID LINE
ANOTHER_VALID=value""")
        
        with pytest.raises(EnvistParseError) as exc_info:
            Envist(temp_env_file)
        
        assert "Line 2" in str(exc_info.value)
    
    def test_manual_casting_edge_cases(self, temp_env_file):
        """Test manual casting in get method"""
        with open(temp_env_file, 'w') as f:
            f.write('STRING_NUM=42')
        
        env = Envist(temp_env_file, auto_cast=False)
        
        # Test manual casting with various types
        assert env.get('STRING_NUM', cast=int) == 42
        assert env.get('STRING_NUM', cast='int') == 42
        assert env.get('STRING_NUM', cast=str) == '42'
        
        # Test casting error in get method
        with pytest.raises(EnvistCastError):
            env.get('STRING_NUM', cast='list<invalid_type>')  # Invalid type syntax should fail
    
    def test_save_edge_cases(self, temp_env_file):
        """Test save method edge cases"""
        env = Envist(temp_env_file, accept_empty=True)
        
        # Add values with None
        env._env['NULL_VALUE'] = None
        env._env['EMPTY_STRING'] = ''
        env._env['NORMAL_VALUE'] = 'test'
        
        # Save and verify
        env.save()
        
        with open(temp_env_file, 'r') as f:
            content = f.read()
            assert 'NULL_VALUE=None' in content or 'NULL_VALUE=' in content
            assert 'EMPTY_STRING=' in content
            assert 'NORMAL_VALUE=test' in content
    
    def test_set_all_edge_cases(self, temp_env_file):
        """Test set_all method edge cases"""
        env = Envist(temp_env_file)
        
        # Test with empty dict
        env.set_all({})
        assert len(env._env) == 0
        
        # Test with None values
        env.set_all({'NULL_VAR': None, 'NORMAL_VAR': 'value'})
        assert env.get('NULL_VAR') is None
        assert env.get('NORMAL_VAR') == 'value'
    
    def test_reload_with_os_env_cleanup(self, temp_env_file):
        """Test reload properly cleans OS environment"""
        with open(temp_env_file, 'w') as f:
            f.write('TEST_RELOAD=initial')
        
        env = Envist(temp_env_file)
        assert os.environ.get('TEST_RELOAD') == 'initial'
        
        # Modify file
        with open(temp_env_file, 'w') as f:
            f.write('DIFFERENT_VAR=new')
        
        # Reload should clean old variables from OS env
        env.reload()
        assert 'TEST_RELOAD' not in os.environ
        assert os.environ.get('DIFFERENT_VAR') == 'new'
        
        # Cleanup
        env.unset_all()
    
    @patch('pathlib.Path.exists')
    def test_file_handler_path_exists_mock(self, mock_exists):
        """Test file existence check with mock"""
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError):
            FileHandler.read_file('fake_file.env')
        
        mock_exists.assert_called_once()
    
    def test_type_syntax_validation_comprehensive(self):
        """Test comprehensive type syntax validation"""
        validator = EnvValidator()
        
        # Test various invalid bracket combinations
        invalid_syntaxes = [
            'list<int',      # Missing closing
            'listint>',      # Missing opening  
            'list<>',        # Empty brackets
            'list<<int>',    # Double opening
            'list<int>>',    # Double closing
            '<int>',         # No base type
            'list<int><str>', # Multiple brackets
        ]
        
        for syntax in invalid_syntaxes:
            assert validator._validate_type_syntax(syntax) is False
    
    def test_complete_coverage_methods(self, temp_env_file):
        """Test methods for complete coverage"""
        with open(temp_env_file, 'w') as f:
            f.write('TEST=value')
        
        env = Envist(temp_env_file)
        
        # Test __iter__
        keys = list(iter(env))
        assert 'TEST' in keys
        
        # Test __len__
        assert len(env) >= 1
        
        # Test __contains__
        assert 'TEST' in env
        assert 'NONEXISTENT' not in env
        
        # Test path property
        assert env.path == temp_env_file
        
        # Test __repr__ and __str__
        repr_str = repr(env)
        str_str = str(env)
        assert 'Envist' in repr_str
        assert 'Envist' in str_str
        assert temp_env_file in repr_str
        assert temp_env_file in str_str
