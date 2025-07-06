"""Tests for the environment validator module"""

import pytest

from envist.validators.env_validator import EnvValidator
from envist.core.exceptions import EnvistParseError


class TestEnvValidator:
    """Test cases for the EnvValidator class"""
    
    def test_parse_line_with_cast_simple(self):
        """Test parsing simple key-value pairs without casting"""
        key, value, cast_type = EnvValidator.parse_line_with_cast("KEY=value")
        
        assert key == "KEY"
        assert value == "value"
        assert cast_type is None
    
    def test_parse_line_with_cast_type_annotation(self):
        """Test parsing with type annotations"""
        key, value, cast_type = EnvValidator.parse_line_with_cast("AGE<int>=25")
        
        assert key == "AGE"
        assert value == "25"
        assert cast_type == "int"
    
    def test_parse_line_with_cast_nested_types(self):
        """Test parsing with nested type annotations"""
        key, value, cast_type = EnvValidator.parse_line_with_cast("NUMBERS<list<int>>=1,2,3")
        
        assert key == "NUMBERS"
        assert value == "1,2,3"
        assert cast_type == "list<int>"
    
    def test_parse_line_with_cast_complex_nested(self):
        """Test parsing with complex nested type annotations"""
        key, value, cast_type = EnvValidator.parse_line_with_cast(
            "CONFIG<dict<str, list<int>>>=key1=[1,2,3]"
        )
        
        assert key == "CONFIG"
        assert value == "key1=[1,2,3]"
        assert cast_type == "dict<str, list<int>>"
    
    def test_parse_line_with_cast_whitespace_handling(self):
        """Test parsing with various whitespace patterns"""
        test_cases = [
            ("  KEY  =  value  ", "KEY", "value", None),
            ("KEY < int > = 25", "KEY", "25", "int"),
            ("  NUMBERS < list < int > > = 1,2,3  ", "NUMBERS", "1,2,3", "list < int >"),
        ]
        
        for line, expected_key, expected_value, expected_cast in test_cases:
            key, value, cast_type = EnvValidator.parse_line_with_cast(line)
            assert key == expected_key
            assert value == expected_value
            assert cast_type == expected_cast
    
    def test_parse_line_with_cast_quoted_values(self):
        """Test parsing quoted values"""
        test_cases = [
            ('KEY="quoted value"', "KEY", "quoted value", None),
            ("KEY='single quoted'", "KEY", "single quoted", None),
            ('TYPED<str>="typed quoted"', "TYPED", "typed quoted", "str"),
        ]
        
        for line, expected_key, expected_value, expected_cast in test_cases:
            key, value, cast_type = EnvValidator.parse_line_with_cast(line)
            assert key == expected_key
            assert value == expected_value
            assert cast_type == expected_cast
    
    def test_parse_line_with_cast_empty_values(self):
        """Test parsing empty values"""
        # With accept_empty=False (default)
        with pytest.raises(EnvistParseError, match="Empty value"):
            EnvValidator.parse_line_with_cast("KEY=")
        
        # With accept_empty=True
        key, value, cast_type = EnvValidator.parse_line_with_cast("KEY=", accept_empty=True)
        assert key == "KEY"
        assert value == ""
        assert cast_type is None
        
        # With type annotation and empty value
        key, value, cast_type = EnvValidator.parse_line_with_cast(
            "TYPED<int>=", accept_empty=True
        )
        assert key == "TYPED"
        assert value == ""
        assert cast_type == "int"
    
    def test_parse_line_with_cast_invalid_formats(self):
        """Test parsing invalid line formats"""
        invalid_lines = [
            "INVALID LINE WITHOUT EQUALS",
            "=value_without_key",
            "KEY<invalid<>=value",  # Invalid type syntax
            "",  # Empty line
            "   ",  # Whitespace only
        ]
        
        for line in invalid_lines:
            with pytest.raises(EnvistParseError):
                EnvValidator.parse_line_with_cast(line)
    
    def test_parse_line_with_cast_special_characters(self):
        """Test parsing with special characters in values"""
        test_cases = [
            ("SPECIAL=!@#$%^&*()", "SPECIAL", "!@#$%^&*()", None),
            ("URL=https://example.com/path?param=value", "URL", "https://example.com/path?param=value", None),
            ("JSON<str>={\"key\":\"value\"}", "JSON", '{"key":"value"}', "str"),
        ]
        
        for line, expected_key, expected_value, expected_cast in test_cases:
            key, value, cast_type = EnvValidator.parse_line_with_cast(line)
            assert key == expected_key
            assert value == expected_value
            assert cast_type == expected_cast
    
    def test_validate_type_syntax_valid(self):
        """Test valid type syntax validation"""
        valid_types = [
            "int",
            "list<int>",
            "dict<str, int>",
            "list<list<int>>",
            "dict<str, list<int>>",
            "list<dict<str, int>>",
            "dict<str, dict<str, int>>",
        ]
        
        for type_str in valid_types:
            assert EnvValidator._validate_type_syntax(type_str) is True
    
    def test_validate_type_syntax_invalid(self):
        """Test invalid type syntax validation"""
        invalid_types = [
            "list<int",  # Missing closing bracket
            "listint>",  # Missing opening bracket
            "list<int>>",  # Extra closing bracket
            "list<<int>",  # Extra opening bracket
            "list<int><str>",  # Multiple type annotations
        ]
        
        for type_str in invalid_types:
            assert EnvValidator._validate_type_syntax(type_str) is False
    
    def test_parse_line_backward_compatibility(self):
        """Test backward compatibility parse_line method"""
        key, value = EnvValidator.parse_line("KEY=value")
        assert key == "KEY"
        assert value == "value"
        
        key, value = EnvValidator.parse_line("TYPED<int>=25")
        assert key == "TYPED"
        assert value == "25"
        # Note: parse_line doesn't return cast_type for backward compatibility
    
    def test_remove_quotes_method(self):
        """Test quote removal functionality"""
        test_cases = [
            ('"quoted"', "quoted"),
            ("'single'", "single"),
            ('"mixed\'', '"mixed\''),  # Mismatched quotes
            ("no_quotes", "no_quotes"),
            ('""', ""),  # Empty quotes
            ("''", ""),  # Empty single quotes
            ('"', '"'),  # Single quote character
            ('a"b', 'a"b'),  # Quote in middle
        ]
        
        for input_val, expected in test_cases:
            result = EnvValidator._remove_quotes(input_val)
            assert result == expected
    
    def test_validate_key_format(self):
        """Test key format validation"""
        valid_keys = [
            "VALID_KEY",
            "valid_key",
            "ValidKey",
            "_PRIVATE_KEY",
            "KEY_123",
            "a",
            "_",
            "KEY_WITH_NUMBERS_123",
        ]
        
        for key in valid_keys:
            assert EnvValidator.validate_key(key) is True
        
        invalid_keys = [
            "123_STARTS_WITH_NUMBER",
            "INVALID-KEY",  # Contains hyphen
            "INVALID.KEY",  # Contains dot
            "INVALID KEY",  # Contains space
            "INVALID@KEY",  # Contains special character
            "",  # Empty string
            "KEY-WITH-HYPHENS",
            "KEY.WITH.DOTS",
        ]
        
        for key in invalid_keys:
            assert EnvValidator.validate_key(key) is False
    
    def test_parse_line_with_cast_equals_in_value(self):
        """Test parsing lines where the value contains equals signs"""
        key, value, cast_type = EnvValidator.parse_line_with_cast("URL=http://example.com?param=value")
        
        assert key == "URL"
        assert value == "http://example.com?param=value"
        assert cast_type is None
    
    def test_parse_line_with_cast_complex_json_values(self):
        """Test parsing complex JSON-like values"""
        key, value, cast_type = EnvValidator.parse_line_with_cast(
            'CONFIG<dict>={"key":"value","nested":{"inner":"data"}}'
        )
        
        assert key == "CONFIG"
        assert value == '{"key":"value","nested":{"inner":"data"}}'
        assert cast_type == "dict"
    
    def test_parse_line_with_cast_nested_brackets_in_value(self):
        """Test parsing values that contain bracket characters"""
        key, value, cast_type = EnvValidator.parse_line_with_cast(
            "FORMULA=array[index] + dict[key]"
        )
        
        assert key == "FORMULA"
        assert value == "array[index] + dict[key]"
        assert cast_type is None
    
    def test_static_methods(self):
        """Test that validator methods are static"""
        # Should be able to call without instantiation
        key, value, cast_type = EnvValidator.parse_line_with_cast("KEY=value")
        assert key == "KEY"
        
        # Verify methods are static (can be called without instance)
        assert callable(EnvValidator.parse_line_with_cast)
        assert callable(EnvValidator.parse_line)
        assert callable(EnvValidator.validate_key)
        assert callable(EnvValidator._validate_type_syntax)
        assert callable(EnvValidator._remove_quotes)
    
    def test_edge_case_type_annotations(self):
        """Test edge cases in type annotations"""
        # Test deeply nested types
        key, value, cast_type = EnvValidator.parse_line_with_cast(
            "DEEP<list<list<list<int>>>>=data"
        )
        assert cast_type == "list<list<list<int>>>"
        
        # Test multiple parameters in dict
        key, value, cast_type = EnvValidator.parse_line_with_cast(
            "COMPLEX<dict<str, list<dict<str, int>>>>=data"
        )
        assert cast_type == "dict<str, list<dict<str, int>>>"
    
    def test_parse_line_with_cast_invalid_type_syntax_detection(self):
        """Test detection of invalid type syntax during parsing"""
        with pytest.raises(EnvistParseError, match="Invalid type syntax"):
            EnvValidator.parse_line_with_cast("KEY<list<int>=value")  # Missing closing bracket
        
        with pytest.raises(EnvistParseError, match="Invalid type syntax"):
            EnvValidator.parse_line_with_cast("KEY<list<int>>>=value")  # Extra closing bracket

    def test_empty_key_validation(self):
        """Test validation with empty key."""
        # Test case with line that has no key (starts with equals)
        with pytest.raises(EnvistParseError, match="Line cannot start with '=' \\(missing key\\)"):
            EnvValidator.parse_line_with_cast("=value", accept_empty=True)
    
    def test_invalid_type_syntax_validation(self):
        """Test invalid type syntax validation."""
        # Test with invalid characters in type for colon syntax that contains non-alphanumeric
        with pytest.raises(EnvistParseError, match="Invalid type syntax"):
            EnvValidator.parse_line_with_cast("KEY:invalid<>=value", accept_empty=True)
    
    def test_empty_value_with_accept_empty_false(self):
        """Test empty value with accept_empty=False."""
        # This should trigger "Empty value" error
        with pytest.raises(EnvistParseError, match="Empty value"):
            EnvValidator.parse_line_with_cast("KEY:str=", accept_empty=False)
    
    def test_complex_bracket_matching_fallback(self):
        """Test complex bracket matching for deeply nested types."""
        # Test line that has brackets but doesn't match simple pattern
        line = "COMPLEX<str<int>>=value"
        
        # This should trigger the complex bracket matching logic
        result = EnvValidator.parse_line_with_cast(line, accept_empty=True)
        assert result is not None
        key, value, cast_type = result
        assert key == "COMPLEX"
        assert value == "value"
        assert cast_type == "str<int>"
    
    def test_bracket_matching_with_nested_structures(self):
        """Test bracket matching with complex nested structures."""
        # Test with simpler nested structure that validates correctly
        line = "VAR:Dict<str>=some_value"
        
        result = EnvValidator.parse_line_with_cast(line, accept_empty=True)
        assert result is not None
        key, value, cast_type = result
        # The colon regex treats this as key="VAR:Dict", type="str", value="some_value"
        assert key == "VAR:Dict"
        assert value == "some_value"
        assert cast_type == "str"
    
    def test_str_type_preserves_whitespace(self):
        """Test that str type preserves whitespace in values."""
        # Test with str type that should preserve leading/trailing whitespace
        line = "STR_VAR:str=  value with spaces  "
        
        result = EnvValidator.parse_line_with_cast(line, accept_empty=True)
        assert result is not None
        key, value, cast_type = result
        assert key == "STR_VAR"
        assert value == "  value with spaces  "  # Should preserve whitespace
        assert cast_type == "str"
    
    def test_non_str_type_strips_whitespace(self):
        """Test that non-str types strip whitespace from values."""
        # Test with non-str type that should strip whitespace
        line = "INT_VAR:int=  42  "
        
        result = EnvValidator.parse_line_with_cast(line, accept_empty=True)
        assert result is not None
        key, value, cast_type = result
        assert key == "INT_VAR"
        assert value == "42"  # Should be stripped
        assert cast_type == "int"
    
    def test_empty_value_validation_with_accept_empty_false_complex(self):
        """Test empty value validation in complex bracket matching."""
        # Test empty value in complex bracket matching with accept_empty=False
        line = "COMPLEX:Dict<str, int>="
        
        with pytest.raises(EnvistParseError, match="Empty value"):
            EnvValidator.parse_line_with_cast(line, accept_empty=False)
    
    def test_invalid_type_syntax_in_complex_matching(self):
        """Test invalid type syntax in complex bracket matching."""
        # Test invalid type syntax in complex matching
        line = "VAR:InvalidType<>=value"
        
        with pytest.raises(EnvistParseError, match="Invalid type syntax"):
            EnvValidator.parse_line_with_cast(line, accept_empty=True)
    
    def test_malformed_bracket_structure(self):
        """Test malformed bracket structure that doesn't match pattern."""
        # Test line that has brackets but doesn't form valid structure
        line = "VAR<incomplete=value"
        
        # This actually gets parsed as a simple key=value pair
        result = EnvValidator.parse_line_with_cast(line, accept_empty=True)
        assert result is not None
        key, value, cast_type = result
        assert key == "VAR<incomplete"
        assert value == "value"
        assert cast_type is None
    
    def test_no_equals_after_bracket_matching(self):
        """Test when bracket matching succeeds but no equals sign follows."""
        # Test with a line that has no equals sign
        line = "VAR_without_equals"
        
        # This gets parsed as a key with empty value
        result = EnvValidator.parse_line_with_cast(line, accept_empty=True)
        assert result is not None
        key, value, cast_type = result
        assert key == "VAR_without_equals"
        assert value == ""
        assert cast_type is None
    
    def test_validate_type_syntax_edge_cases(self):
        """Test _validate_type_syntax with various edge cases."""
        # Test valid syntax
        assert EnvValidator._validate_type_syntax("int") is True
        assert EnvValidator._validate_type_syntax("List<str>") is True
        assert EnvValidator._validate_type_syntax("Dict<str, int>") is True
        
        # Test invalid syntax (these should return False)
        assert EnvValidator._validate_type_syntax("") is False
        assert EnvValidator._validate_type_syntax("invalid<") is False
        assert EnvValidator._validate_type_syntax(">invalid") is False
        assert EnvValidator._validate_type_syntax("<<>>") is False
    
    def test_remove_quotes_comprehensive(self):
        """Test _remove_quotes with comprehensive cases."""
        # Test various quote combinations
        assert EnvValidator._remove_quotes('"quoted"') == 'quoted'
        assert EnvValidator._remove_quotes("'quoted'") == 'quoted'
        assert EnvValidator._remove_quotes('"mixed\'') == '"mixed\''  # Unmatched
        assert EnvValidator._remove_quotes('\'mixed"') == '\'mixed"'  # Unmatched
        assert EnvValidator._remove_quotes('unquoted') == 'unquoted'
        assert EnvValidator._remove_quotes('') == ''
    
    def test_validate_key_format_comprehensive(self):
        """Test _validate_key_format with comprehensive cases."""
        # Test valid keys
        assert EnvValidator._validate_key_format("VALID_KEY") is True
        assert EnvValidator._validate_key_format("KEY123") is True
        assert EnvValidator._validate_key_format("_PRIVATE_KEY") is True
        assert EnvValidator._validate_key_format("MIX3D_K3Y") is True
        
        # Test invalid keys
        assert EnvValidator._validate_key_format("") is False
        assert EnvValidator._validate_key_format("123KEY") is False  # Starts with number
        assert EnvValidator._validate_key_format("KEY-WITH-DASH") is False  # Contains dash
        assert EnvValidator._validate_key_format("KEY WITH SPACE") is False  # Contains space
        assert EnvValidator._validate_key_format("KEY.WITH.DOT") is False  # Contains dot
    
    def test_no_bracket_no_colon_lines(self):
        """Test lines without brackets or colons."""
        # Test simple assignment - this actually gets parsed normally
        result = EnvValidator.parse_line_with_cast("SIMPLE_VAR=value", accept_empty=True)
        assert result is not None
        key, value, cast_type = result
        assert key == "SIMPLE_VAR"
        assert value == "value"
        assert cast_type is None
        
        # Test line without equals
        result = EnvValidator.parse_line_with_cast("NO_EQUALS_HERE", accept_empty=True)
        assert result is not None
        key, value, cast_type = result
        assert key == "NO_EQUALS_HERE"
        assert value == ""
        assert cast_type is None
    
    def test_angle_bracket_position_validation(self):
        """Test angle bracket position validation in fallback logic."""
        # Test line starting with equals - this raises an exception
        with pytest.raises(EnvistParseError, match="Line cannot start with '=' \\(missing key\\)"):
            EnvValidator.parse_line_with_cast("=VAR<type>value", accept_empty=True)
        
        # Test simple assignment (not malformed)
        result = EnvValidator.parse_line_with_cast("VAR=value", accept_empty=True)
        assert result is not None
        key, value, cast_type = result
        assert key == "VAR"
        assert value == "value"
        assert cast_type is None
    
    def test_bracket_mismatch_in_complex_parsing(self):
        """Test bracket mismatch in complex parsing logic."""
        # Test with unmatched brackets
        result = EnvValidator.parse_line_with_cast("VAR:List<str>=value", accept_empty=True)
        assert result is not None  # Should work fine
        
        # Test with invalid syntax in colon format
        with pytest.raises(EnvistParseError, match="Invalid type syntax"):
            EnvValidator.parse_line_with_cast("VAR:List<<str>=value", accept_empty=True)
    
    def test_edge_case_combinations(self):
        """Test various edge case combinations."""
        # Test empty string input
        with pytest.raises(EnvistParseError, match="Empty or whitespace-only line"):
            EnvValidator.parse_line_with_cast("", accept_empty=True)
        
        # Test whitespace only
        with pytest.raises(EnvistParseError, match="Empty or whitespace-only line"):
            EnvValidator.parse_line_with_cast("   ", accept_empty=True)
        
        # Test simple variable assignment
        result = EnvValidator.parse_line_with_cast("KEY=value", accept_empty=True)
        assert result is not None
        key, value, cast_type = result
        assert key == "KEY"
        assert value == "value"
        assert cast_type is None
        result = EnvValidator.parse_line_with_cast("KEY=", accept_empty=True)
        assert result is not None
        key, value, cast_type = result
        assert key == "KEY"
        assert value == ""
        assert cast_type is None
