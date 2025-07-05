"""Tests for the core exceptions module"""

import pytest

from envist.core.exceptions import (
    EnvistError,
    FileNotFoundError,
    EnvistParseError,
    EnvistCastError,
    EnvistTypeError,
    EnvistValueError
)


class TestEnvistExceptions:
    """Test cases for Envist exception classes"""
    
    def test_envist_error_base_exception(self):
        """Test the base EnvistError exception"""
        error = EnvistError("Base error message")
        
        assert str(error) == "Base error message"
        assert isinstance(error, Exception)
        
        # Test without message
        error = EnvistError()
        assert str(error) == ""
    
    def test_file_not_found_error(self):
        """Test FileNotFoundError exception"""
        error = FileNotFoundError("File not found: test.env")
        
        assert str(error) == "File not found: test.env"
        assert isinstance(error, EnvistError)
        assert isinstance(error, Exception)
        
        # Test inheritance chain
        assert issubclass(FileNotFoundError, EnvistError)
    
    def test_parse_error(self):
        """Test EnvistParseError exception"""
        error = EnvistParseError("Invalid syntax on line 5")
        
        assert str(error) == "Invalid syntax on line 5"
        assert isinstance(error, EnvistError)
        assert isinstance(error, Exception)
        
        # Test inheritance chain
        assert issubclass(EnvistParseError, EnvistError)
    
    def test_cast_error(self):
        """Test EnvistCastError exception"""
        error = EnvistCastError("Cannot cast 'abc' to int")
        
        assert str(error) == "Cannot cast 'abc' to int"
        assert isinstance(error, EnvistError)
        assert isinstance(error, Exception)
        
        # Test inheritance chain
        assert issubclass(EnvistCastError, EnvistError)
    
    def test_type_error(self):
        """Test EnvistTypeError exception"""
        error = EnvistTypeError("Expected dict, got str")
        
        assert str(error) == "Expected dict, got str"
        assert isinstance(error, EnvistError)
        assert isinstance(error, Exception)
        
        # Test inheritance chain
        assert issubclass(EnvistTypeError, EnvistError)
    
    def test_value_error(self):
        """Test EnvistValueError exception"""
        error = EnvistValueError("Invalid value for key 'DEBUG'")
        
        assert str(error) == "Invalid value for key 'DEBUG'"
        assert isinstance(error, EnvistError)
        assert isinstance(error, Exception)
        
        # Test inheritance chain
        assert issubclass(EnvistValueError, EnvistError)
    
    def test_exception_inheritance_hierarchy(self):
        """Test that all exceptions inherit from EnvistError"""
        exceptions = [
            FileNotFoundError,
            EnvistParseError,
            EnvistCastError,
            EnvistTypeError,
            EnvistValueError
        ]
        
        for exc_class in exceptions:
            assert issubclass(exc_class, EnvistError)
            assert issubclass(exc_class, Exception)
    
    def test_exception_with_args(self):
        """Test exceptions with multiple arguments"""
        error = EnvistParseError("Error message", "additional_info")
        
        # Should be able to access args
        assert error.args == ("Error message", "additional_info")
        assert str(error) == "('Error message', 'additional_info')"
    
    def test_exception_raising(self):
        """Test raising and catching exceptions"""
        # Test raising FileNotFoundError
        with pytest.raises(FileNotFoundError) as exc_info:
            raise FileNotFoundError("Test file not found")
        
        assert str(exc_info.value) == "Test file not found"
        
        # Test catching as base EnvistError
        with pytest.raises(EnvistError):
            raise FileNotFoundError("Test file not found")
        
        # Test raising EnvistParseError
        with pytest.raises(EnvistParseError) as exc_info:
            raise EnvistParseError("Parse error occurred")
        
        assert str(exc_info.value) == "Parse error occurred"
        
        # Test raising EnvistCastError
        with pytest.raises(EnvistCastError) as exc_info:
            raise EnvistCastError("Cast error occurred")
        
        assert str(exc_info.value) == "Cast error occurred"
        
        # Test raising EnvistTypeError
        with pytest.raises(EnvistTypeError) as exc_info:
            raise EnvistTypeError("Type error occurred")
        
        assert str(exc_info.value) == "Type error occurred"
        
        # Test raising EnvistValueError
        with pytest.raises(EnvistValueError) as exc_info:
            raise EnvistValueError("Value error occurred")
        
        assert str(exc_info.value) == "Value error occurred"
    
    def test_exception_chaining(self):
        """Test exception chaining functionality"""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise EnvistCastError("Cast failed") from e
        except EnvistCastError as exc:
            assert str(exc) == "Cast failed"
            assert isinstance(exc.__cause__, ValueError)
            assert str(exc.__cause__) == "Original error"
    
    def test_exception_without_message(self):
        """Test exceptions without error messages"""
        exceptions_classes = [
            EnvistError,
            FileNotFoundError,
            EnvistParseError,
            EnvistCastError,
            EnvistTypeError,
            EnvistValueError
        ]
        
        for exc_class in exceptions_classes:
            error = exc_class()
            # Should not raise an error when creating without message
            assert isinstance(error, exc_class)
            assert isinstance(error, EnvistError)
    
    def test_exception_with_none_message(self):
        """Test exceptions with None as message"""
        error = EnvistError(None)
        assert str(error) == "None"
        
        error = FileNotFoundError(None)
        assert str(error) == "None"
    
    def test_exception_with_numeric_message(self):
        """Test exceptions with numeric messages"""
        error = EnvistParseError(404)
        assert str(error) == "404"
        
        error = EnvistCastError(123.45)
        assert str(error) == "123.45"
    
    def test_exception_pickling(self):
        """Test that exceptions can be pickled and unpickled"""
        import pickle
        
        exceptions = [
            EnvistError("Base error"),
            FileNotFoundError("File not found"),
            EnvistParseError("Parse error"),
            EnvistCastError("Cast error"),
            EnvistTypeError("Type error"),
            EnvistValueError("Value error")
        ]
        
        for exc in exceptions:
            # Pickle and unpickle
            pickled = pickle.dumps(exc)
            unpickled = pickle.loads(pickled)
            
            # Should have same type and message
            assert type(unpickled) == type(exc)
            assert str(unpickled) == str(exc)
            assert unpickled.args == exc.args
    
    def test_exception_equality(self):
        """Test exception equality comparison"""
        error1 = EnvistError("Same message")
        error2 = EnvistError("Same message")
        error3 = EnvistError("Different message")
        
        # Same type and message should be equal
        assert error1.args == error2.args
        assert error1.args != error3.args
        
        # Different types should not be equal even with same message
        parse_error = EnvistParseError("Same message")
        assert error1.args == parse_error.args  # Same message
        assert type(error1) != type(parse_error)  # Different types
    
    def test_exception_representation(self):
        """Test exception string representation"""
        error = EnvistError("Test error message")
        
        # __str__ should return the message
        assert str(error) == "Test error message"
        
        # __repr__ should show class and message
        repr_str = repr(error)
        assert "EnvistError" in repr_str
        assert "Test error message" in repr_str
