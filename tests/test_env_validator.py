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
