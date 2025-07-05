"""Tests for the main package initialization"""

import pytest

import envist
from envist import Envist
from envist.core.exceptions import (
    EnvistError,
    FileNotFoundError,
    EnvistParseError,
    EnvistCastError,
    EnvistTypeError,
    EnvistValueError
)


class TestPackageInit:
    """Test cases for package initialization and exports"""
    
    def test_package_version(self):
        """Test that package has a version"""
        assert hasattr(envist, '__version__')
        assert isinstance(envist.__version__, str)
        assert len(envist.__version__) > 0
    
    def test_main_class_import(self):
        """Test that main Envist class can be imported"""
        assert Envist is not None
        assert hasattr(Envist, '__init__')
        assert hasattr(Envist, 'get')
        assert hasattr(Envist, 'set')
        assert hasattr(Envist, 'get_all')
    
    def test_exception_imports(self):
        """Test that all exceptions can be imported"""
        exceptions = [
            EnvistError,
            FileNotFoundError,
            EnvistParseError,
            EnvistCastError,
            EnvistTypeError,
            EnvistValueError
        ]
        
        for exc_class in exceptions:
            assert exc_class is not None
            assert issubclass(exc_class, Exception)
    
    def test_package_docstring(self):
        """Test that package has proper documentation"""
        assert envist.__doc__ is not None
        assert len(envist.__doc__.strip()) > 0
    
    def test_all_exports(self):
        """Test __all__ exports if defined"""
        if hasattr(envist, '__all__'):
            for export_name in envist.__all__:
                assert hasattr(envist, export_name)
                obj = getattr(envist, export_name)
                assert obj is not None
    
    def test_package_metadata(self):
        """Test package metadata"""
        # Test common metadata attributes
        metadata_attrs = ['__name__', '__package__']
        for attr in metadata_attrs:
            if hasattr(envist, attr):
                assert getattr(envist, attr) is not None
    
    def test_direct_instantiation(self, temp_env_file):
        """Test that Envist can be instantiated directly from package import"""
        with open(temp_env_file, 'w') as f:
            f.write("TEST_VAR=test_value")
        
        # Should be able to instantiate directly
        env = Envist(temp_env_file)
        assert env.get('TEST_VAR') == 'test_value'
    
    def test_exception_hierarchy_from_package(self):
        """Test exception hierarchy when imported from package"""
        # All custom exceptions should inherit from EnvistError
        custom_exceptions = [
            FileNotFoundError,
            EnvistParseError,
            EnvistCastError,
            EnvistTypeError,
            EnvistValueError
        ]
        
        for exc_class in custom_exceptions:
            assert issubclass(exc_class, EnvistError)
            assert issubclass(exc_class, Exception)
    
    def test_package_structure(self):
        """Test that package has expected structure"""
        # Test that core modules are accessible
        from envist.core import parser, exceptions
        from envist.utils import file_handler, type_casters
        from envist.validators import env_validator
        
        # Test that classes are accessible
        assert hasattr(parser, 'Envist')
        assert hasattr(exceptions, 'EnvistError')
        assert hasattr(file_handler, 'FileHandler')
        assert hasattr(type_casters, 'TypeCaster')
        assert hasattr(env_validator, 'EnvValidator')
