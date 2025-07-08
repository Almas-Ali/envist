"""Integration tests for the entire Envist package"""

import os
import tempfile
from pathlib import Path

import pytest

from envist import Envist
from envist.core.exceptions import EnvistCastError, EnvistParseError, FileNotFoundError


class TestEnvistIntegration:
    """Integration tests for the complete Envist functionality"""

    def test_complete_workflow(self, temp_env_file):
        """Test complete workflow from file creation to value retrieval"""
        # Create a comprehensive .env file
        env_content = """# Configuration file
APP_NAME=MyApp
DEBUG<bool>=true
PORT<int>=8080
VERSION<float>=1.5
FEATURES<list<str>>=auth,logging,metrics

# Database configuration
DB_CONFIG<dict<str, str>>=host=localhost,port=5432,name=myapp

# Nested structures
MATRIX<list<list<int>>>=[[1,2,3],[4,5,6],[7,8,9]]
USER_ROLES<dict<str, list<str>>>=admin=[read,write,delete],user=[read]

# Variable resolution
BASE_URL=https://api.example.com
API_ENDPOINT=${BASE_URL}/v1
FULL_ENDPOINT=${API_ENDPOINT}/users

# Empty and special values
EMPTY_VALUE=
QUOTED_VALUE="Hello World"
SPECIAL_CHARS=!@#$%^&*()
"""

        with open(temp_env_file, "w", encoding="utf-8") as f:
            f.write(env_content)

        # Load and test
        env = Envist(temp_env_file, accept_empty=True)

        # Test simple values
        assert env.get("APP_NAME") == "MyApp"
        assert env.get("DEBUG") is True
        assert env.get("PORT") == 8080
        assert env.get("VERSION") == 1.5

        # Test list casting
        features = env.get("FEATURES")
        assert features == ["auth", "logging", "metrics"]
        assert all(isinstance(f, str) for f in features)

        # Test dict casting
        db_config = env.get("DB_CONFIG")
        assert db_config == {"host": "localhost", "port": "5432", "name": "myapp"}

        # Test nested structures
        matrix = env.get("MATRIX")
        assert matrix == [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        assert all(isinstance(row, list) for row in matrix)
        assert all(isinstance(cell, int) for row in matrix for cell in row)

        user_roles = env.get("USER_ROLES")
        assert user_roles == {"admin": ["read", "write", "delete"], "user": ["read"]}

        # Test variable resolution
        assert env.get("BASE_URL") == "https://api.example.com"
        assert env.get("API_ENDPOINT") == "https://api.example.com/v1"
        assert env.get("FULL_ENDPOINT") == "https://api.example.com/v1/users"

        # Test special values
        assert env.get("EMPTY_VALUE") is None
        assert env.get("QUOTED_VALUE") == "Hello World"
        assert env.get("SPECIAL_CHARS") == "!@#$%^&*()"

    def test_auto_cast_toggle(self, temp_env_file):
        """Test toggling auto_cast functionality"""
        env_content = """AGE<int>=25
SCORES<list<float>>=95.5,87.2,92.1
IS_ACTIVE<bool>=true"""

        with open(temp_env_file, "w") as f:
            f.write(env_content)

        # With auto_cast enabled
        env_auto = Envist(temp_env_file, auto_cast=True)
        assert env_auto.get("AGE") == 25
        assert isinstance(env_auto.get("AGE"), int)
        assert env_auto.get("SCORES") == [95.5, 87.2, 92.1]
        assert env_auto.get("IS_ACTIVE") is True

        # With auto_cast disabled
        env_no_auto = Envist(temp_env_file, auto_cast=False)
        assert env_no_auto.get("AGE") == "25"
        assert isinstance(env_no_auto.get("AGE"), str)
        assert env_no_auto.get("SCORES") == "95.5,87.2,92.1"
        assert env_no_auto.get("IS_ACTIVE") == "true"

        # Manual casting should still work when auto_cast is disabled
        age = env_no_auto.get("AGE", cast="int")
        assert age == 25
        assert isinstance(age, int)

    def test_environment_variable_sync(self, temp_env_file):
        """Test synchronization with OS environment variables"""
        env_content = """SYNC_TEST=value1
SYNC_INT<int>=42"""

        with open(temp_env_file, "w") as f:
            f.write(env_content)

        env = Envist(temp_env_file)

        # Check that values are in OS environment
        assert os.environ.get("SYNC_TEST") == "value1"
        assert os.environ.get("SYNC_INT") == "42"  # OS env vars are always strings

        # Test setting new values
        env.set("NEW_VAR", "new_value")
        assert os.environ.get("NEW_VAR") == "new_value"

        # Test unsetting
        env.unset("SYNC_TEST")
        assert "SYNC_TEST" not in os.environ

        # Cleanup
        env.unset_all()
        assert "SYNC_INT" not in os.environ
        assert "NEW_VAR" not in os.environ

    def test_file_persistence(self, temp_env_file):
        """Test file persistence functionality"""
        # Create initial file
        env = Envist(temp_env_file, accept_empty=True)

        # Add some values
        env.set("PERSIST_STRING", "test_value")
        env.set("PERSIST_INT", 42)
        env.set("PERSIST_BOOL", True)

        # Save to file
        env.save()

        # Load from file again
        new_env = Envist(
            temp_env_file, auto_cast=False
        )  # No auto-cast to verify raw values

        assert new_env.get("PERSIST_STRING") == "test_value"
        assert new_env.get("PERSIST_INT") == "42"  # Saved as string
        assert new_env.get("PERSIST_BOOL") == "True"  # Saved as string

        # Test pretty format
        env.save(pretty=True, sort_keys=True)

        with open(temp_env_file, "r") as f:
            content = f.read()
            lines = [line.strip() for line in content.split("\n") if line.strip()]

            # Should have pretty format (spaces around =)
            assert all(" = " in line for line in lines)

            # Should be sorted
            keys = [line.split(" = ")[0] for line in lines]
            assert keys == sorted(keys)

    def test_complex_variable_resolution(self, temp_env_file):
        """Test complex variable resolution scenarios"""
        env_content = """# Base variables
PROTOCOL=https
DOMAIN=example.com
PORT<int>=8080

# Composed variables
BASE_URL=${PROTOCOL}://${DOMAIN}:${PORT}
API_BASE=${BASE_URL}/api
API_V1=${API_BASE}/v1

# Nested resolution
USER_ENDPOINT=${API_V1}/users
USER_PROFILE=${USER_ENDPOINT}/profile

# Variable in lists and dicts
ENDPOINTS<list<str>>=${API_V1}/users,${API_V1}/posts
CONFIG<dict<str, str>>=api_url=${API_V1},base_url=${BASE_URL}"""

        with open(temp_env_file, "w") as f:
            f.write(env_content)

        env = Envist(temp_env_file)

        # Test basic resolution
        assert env.get("BASE_URL") == "https://example.com:8080"
        assert env.get("API_BASE") == "https://example.com:8080/api"
        assert env.get("API_V1") == "https://example.com:8080/api/v1"

        # Test nested resolution
        assert env.get("USER_ENDPOINT") == "https://example.com:8080/api/v1/users"
        assert (
            env.get("USER_PROFILE") == "https://example.com:8080/api/v1/users/profile"
        )

        # Test variables in collections
        endpoints = env.get("ENDPOINTS")
        assert endpoints == [
            "https://example.com:8080/api/v1/users",
            "https://example.com:8080/api/v1/posts",
        ]

        config = env.get("CONFIG")
        assert config == {
            "api_url": "https://example.com:8080/api/v1",
            "base_url": "https://example.com:8080",
        }

    def test_error_handling_integration(self, temp_env_file):
        """Test comprehensive error handling"""
        # Test file not found
        with pytest.raises(FileNotFoundError):
            Envist("non_existent_file.env")

        # Test invalid syntax
        with open(temp_env_file, "w") as f:
            f.write("INVALID LINE WITHOUT EQUALS\nVALID=value")

        with pytest.raises(EnvistParseError, match="Line 1"):
            Envist(temp_env_file)

        # Test invalid type casting
        with open(temp_env_file, "w") as f:
            f.write("INVALID_INT<int>=not_a_number")

        with pytest.raises(EnvistCastError):
            Envist(temp_env_file)

        # Test circular references
        with open(temp_env_file, "w") as f:
            f.write("VAR1=${VAR2}\nVAR2=${VAR1}")

        with pytest.raises(EnvistParseError, match="Circular reference"):
            Envist(temp_env_file)

    def test_edge_cases_integration(self, temp_env_file):
        """Test edge cases in integrated scenarios"""
        env_content = """# Edge cases
ZERO<int>=0
EMPTY_LIST<list<int>>=
EMPTY_DICT<dict<str, str>>=
FALSE_BOOL<bool>=false
NEGATIVE<int>=-123
DECIMAL<float>=0.0001

# Special characters
UNICODE=café_naïve_🚀
SYMBOLS=!@#$%^&*()_+-=[]{}|;:,.<>?
QUOTES_MIXED="single'quote'inside"

# Whitespace edge cases
LEADING_SPACES<str>=   value_without_spaces   
TRAILING_TABS<str>=value	
MIXED_WHITESPACE<str>=	  value  	

# Inline comments
INLINE_COMMENT=value # This should be ignored

# Complex nesting
DEEP_NESTED<list<list<list<int>>>>=[[1,2],[3,4]],[[5,6],[7,8]]
VERY_COMPLEX<dict<str, list<dict<str, int>>>>=group1=[{"a":1,"b":2}],group2=[{"c":3,"d":4}]"""

        with open(temp_env_file, "w", encoding="utf-8") as f:
            f.write(env_content)

        env = Envist(temp_env_file, accept_empty=True)

        # Test edge values
        assert env.get("ZERO") == 0
        assert env.get("EMPTY_LIST") == []
        assert env.get("EMPTY_DICT") == {}
        assert env.get("FALSE_BOOL") is False
        assert env.get("NEGATIVE") == -123
        assert env.get("DECIMAL") == 0.0001

        # Test special characters
        assert env.get("UNICODE") == "café_naïve_🚀"
        assert env.get("SYMBOLS") == "!@#$%^&*()_+-=[]{}|;:,.<>?"
        assert env.get("QUOTES_MIXED") == "single'quote'inside"

        # Test whitespace handling
        assert env.get("LEADING_SPACES") == "value_without_spaces"
        assert env.get("TRAILING_TABS") == "value"
        assert env.get("MIXED_WHITESPACE") == "value"

        # Test inline comments
        assert env.get("INLINE_COMMENT") == "value"

        # Test complex nesting
        deep_nested = env.get("DEEP_NESTED")
        assert deep_nested == [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]

        very_complex = env.get("VERY_COMPLEX")
        expected = {"group1": [{"a": 1, "b": 2}], "group2": [{"c": 3, "d": 4}]}
        assert very_complex == expected

    def test_dictionary_interface_integration(self, temp_env_file):
        """Test dictionary-like interface in integrated scenarios"""
        env_content = """KEY1=value1
KEY2<int>=42
KEY3<list<str>>=a,b,c"""

        with open(temp_env_file, "w") as f:
            f.write(env_content)

        env = Envist(temp_env_file)

        # Test __getitem__
        assert env["KEY1"] == "value1"
        assert env["KEY2"] == 42
        assert env["KEY3"] == ["a", "b", "c"]

        # Test __setitem__
        env["NEW_KEY"] = "new_value"
        assert env.get("NEW_KEY") == "new_value"

        # Test __delitem__
        del env["KEY1"]
        assert "KEY1" not in env

        # Test __contains__
        assert "KEY2" in env
        assert "DELETED_KEY" not in env

        # Test __len__
        original_len = len(env)
        env["TEMP_KEY"] = "temp"
        assert len(env) == original_len + 1
        del env["TEMP_KEY"]
        assert len(env) == original_len

        # Test iteration
        keys = list(env)
        assert "KEY2" in keys
        assert "KEY3" in keys

    def test_reload_functionality(self, temp_env_file):
        """Test reload functionality in practical scenarios"""
        # Initial content
        initial_content = """INITIAL_VAR=initial_value
SHARED_VAR=shared_value"""

        with open(temp_env_file, "w") as f:
            f.write(initial_content)

        env = Envist(temp_env_file)

        assert env.get("INITIAL_VAR") == "initial_value"
        assert env.get("SHARED_VAR") == "shared_value"

        # Modify the file
        updated_content = """INITIAL_VAR=updated_value
SHARED_VAR=shared_value
NEW_VAR=new_value"""

        with open(temp_env_file, "w") as f:
            f.write(updated_content)

        # Reload
        env.reload()

        assert env.get("INITIAL_VAR") == "updated_value"
        assert env.get("SHARED_VAR") == "shared_value"
        assert env.get("NEW_VAR") == "new_value"

    def test_performance_with_large_file(self, temp_env_file):
        """Test performance with larger .env files"""
        # Generate a large .env file
        lines = []
        for i in range(1000):
            lines.append(f"VAR_{i}=value_{i}")
            if i % 10 == 0:
                lines.append(f"INT_VAR_{i}<int>={i}")
            if i % 20 == 0:
                lines.append(f"LIST_VAR_{i}<list<int>>={i},{i + 1},{i + 2}")

        content = "\n".join(lines)

        with open(temp_env_file, "w") as f:
            f.write(content)

        # Load and test - should complete without timeout
        env = Envist(temp_env_file)

        assert len(env) == 1150  # 1000 + 100 + 50
        assert env.get("VAR_500") == "value_500"
        assert env.get("INT_VAR_100") == 100
        assert env.get("LIST_VAR_40") == [40, 41, 42]

    def test_concurrent_access(self, temp_env_file):
        """Test concurrent access scenarios"""
        env_content = """SHARED_VAR=initial
COUNTER<int>=0"""

        with open(temp_env_file, "w") as f:
            f.write(env_content)

        # Multiple Envist instances
        env1 = Envist(temp_env_file)
        env2 = Envist(temp_env_file)

        # Both should have same initial values
        assert env1.get("SHARED_VAR") == "initial"
        assert env2.get("SHARED_VAR") == "initial"
        assert env1.get("COUNTER") == 0
        assert env2.get("COUNTER") == 0

        # Modify one instance
        env1.set("SHARED_VAR", "modified_by_env1")
        env1.set("COUNTER", 42)

        # Other instance should be unchanged until reload
        assert env2.get("SHARED_VAR") == "initial"
        assert env2.get("COUNTER") == 0

        # Save and reload
        env1.save()
        env2.reload()

        # Now both should have updated values
        assert env2.get("SHARED_VAR") == "modified_by_env1"
        # Note: After save/reload, type annotations are lost, so COUNTER becomes a string
        assert env2.get("COUNTER") == "42"
