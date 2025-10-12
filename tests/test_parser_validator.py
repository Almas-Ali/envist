"""Tests for the Envist.validator decorator and deprecated validator."""

from pathlib import Path

import pytest

from envist import Envist
from envist import validator as deprecated_validator


def _create_env(tmp_path, content: str) -> Envist:
    env_file = Path(tmp_path) / ".env.test"
    env_file.write_text(content, encoding="utf-8")
    return Envist(str(env_file), accept_empty=True)


def test_instance_validator_valid_key(tmp_path):
    """Instance-based validator should return True and provide the value."""
    env = _create_env(tmp_path, "NAME=Jane Doe\n")
    captured = {}

    @env.validator("NAME")
    def validate_name(value: str) -> bool:
        captured["value"] = value
        return True

    assert captured["value"] == "Jane Doe"
    assert validate_name is True


def test_instance_validator_invalid_key_format(tmp_path):
    """Instance-based validator should reject invalid key formats."""
    env = _create_env(tmp_path, "VALID_KEY=value\n")

    with pytest.raises(ValueError, match="Invalid key format"):

        @env.validator("invalid key")
        def validate_invalid(_: str) -> bool:
            return True


def test_instance_validator_missing_key(tmp_path):
    """Instance-based validator should surface errors from the wrapped function."""
    env = _create_env(tmp_path, "KNOWN=value\n")

    with pytest.raises(ValueError, match="Key does not exist"):

        @env.validator("UNKNOWN")
        def validate_missing(value) -> bool:
            if value is None:
                raise ValueError("Key does not exist")
            return True


def test_instance_validator_preserves_casting(tmp_path):
    """Instance-based validator should receive auto-cast values."""
    env = _create_env(tmp_path, "AGE<int>=29\n")
    captured = {}

    @env.validator("AGE")
    def validate_age(value: int) -> bool:
        captured["type"] = type(value)
        captured["value"] = value
        return True

    assert captured["value"] == 29
    assert captured["type"] is int
    assert validate_age is True


def test_deprecated_validator_emits_warning(tmp_path):
    """Deprecated module-level validator should emit a warning and still work."""
    env = _create_env(tmp_path, "FLAG<bool>=true\n")

    with pytest.deprecated_call():

        @deprecated_validator(env, "FLAG")
        def validate_flag(value: bool) -> bool:
            assert value is True
            return True

        assert validate_flag is True
