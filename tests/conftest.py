"""Pytest configuration and fixtures"""

import os
import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest


@pytest.fixture
def temp_env_file():
    """Create a temporary .env file for testing"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        yield f.name
    # Cleanup
    if os.path.exists(f.name):
        os.unlink(f.name)


@pytest.fixture
def sample_env_content():
    """Sample .env file content for testing"""
    return """# This is a comment
NAME=John Doe
AGE<int>=25
HEIGHT<float>=5.9
IS_ACTIVE<bool>=true

# Complex types
NUMBERS<list<int>>=1,2,3,4,5
SCORES<list<float>>=95.5,87.2,92.1
TAGS<list<str>>=python,dev,backend

# Nested types
MATRIX<list<list<int>>>=[[1,2,3],[4,5,6],[7,8,9]]
CONFIG<dict<str, int>>=timeout=30,retries=3,port=8080
USERS<list<dict<str, str>>>={"name":"John","role":"admin"},{"name":"Jane","role":"user"}

# Variable resolution
BASE_URL=https://api.example.com
API_VERSION=v1
FULL_URL=${BASE_URL}/${API_VERSION}/users

# Quoted values
QUOTED_STRING="Hello World"
SINGLE_QUOTED='Single Quote'"""


@pytest.fixture
def complex_env_content():
    """Complex .env file content for advanced testing"""
    return """# Complex nested structures
NESTED_CONFIG<dict<str, dict<str, int>>>={"db":{"port":5432,"timeout":30},"cache":{"ttl":3600,"size":1000}}
COMPLEX<dict<str, list<int>>>=group1=[1,2,3],group2=[4,5,6]
DEEP_NESTED<list<list<list<int>>>>=[[1,2],[3,4]],[[5,6],[7,8]]
MATRIX<list<list<int>>>=[[1,2,3],[4,5,6],[7,8,9]]
USERS<list<dict<str, str>>>={"name":"John","role":"admin"},{"name":"Jane","role":"user"}

# Edge cases
EMPTY_LIST<list<int>>=
EMPTY_DICT<dict<str, str>>=
ZERO_VALUE<int>=0
FALSE_BOOL<bool>=false

# Variable chains
VAR1=value1
VAR2=${VAR1}_extended
VAR3=${VAR2}_final

# Special characters
SPECIAL_CHARS=!@#$%^&*()
UNICODE_VALUE=café_naïve"""


@pytest.fixture
def env_file_with_content(temp_env_file, sample_env_content):
    """Create a temporary .env file with sample content"""
    with open(temp_env_file, "w", encoding="utf-8") as f:
        f.write(sample_env_content)
    return temp_env_file


@pytest.fixture
def complex_env_file(temp_env_file, complex_env_content):
    """Create a temporary .env file with complex content"""
    with open(temp_env_file, "w", encoding="utf-8") as f:
        f.write(complex_env_content)
    return temp_env_file


@pytest.fixture
def empty_env_file(temp_env_file):
    """Create an empty .env file"""
    with open(temp_env_file, "w", encoding="utf-8") as f:
        f.write("")
    return temp_env_file


@pytest.fixture
def invalid_env_file(temp_env_file):
    """Create a .env file with invalid syntax"""
    with open(temp_env_file, "w", encoding="utf-8") as f:
        f.write("""VALID_KEY=value
INVALID LINE WITHOUT EQUALS
ANOTHER_VALID=test
<INVALID_KEY>=value
KEY_WITH_INVALID_TYPE<invalid<>=value""")
    return temp_env_file


@pytest.fixture
def cleanup_env_vars():
    """Cleanup environment variables after tests"""
    original_env = dict(os.environ)
    yield
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_env_data():
    """Mock environment data for testing"""
    return {
        "STRING_VAR": "test_value",
        "INT_VAR": 42,
        "FLOAT_VAR": 3.14,
        "BOOL_VAR": True,
        "LIST_VAR": [1, 2, 3],
        "DICT_VAR": {"key": "value"},
        "NESTED_LIST": [[1, 2], [3, 4]],
        "NESTED_DICT": {"outer": {"inner": "value"}},
    }
