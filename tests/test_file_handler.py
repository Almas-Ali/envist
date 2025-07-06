"""Tests for the file handler utility module"""

import os
import tempfile
from unittest.mock import mock_open, patch

import pytest

from envist.core.exceptions import FileNotFoundError
from envist.utils.file_handler import FileHandler


class TestFileHandler:
    """Test cases for the FileHandler utility class"""

    def test_read_file_success(self, temp_env_file):
        """Test successful file reading"""
        content = "LINE1\nLINE2\nLINE3\n"
        with open(temp_env_file, "w", encoding="utf-8") as f:
            f.write(content)

        lines = FileHandler.read_file(temp_env_file)

        assert len(lines) == 3
        assert lines[0] == "LINE1\n"
        assert lines[1] == "LINE2\n"
        assert lines[2] == "LINE3\n"

    def test_read_file_not_found(self):
        """Test file not found error"""
        with pytest.raises(FileNotFoundError, match="File not found"):
            FileHandler.read_file("non_existent_file.env")

    def test_read_file_io_error(self):
        """Test IO error handling"""
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", side_effect=IOError("Permission denied")),
        ):
            with pytest.raises(FileNotFoundError, match="Error reading file"):
                FileHandler.read_file("some_file.env")

    def test_read_file_empty(self, temp_env_file):
        """Test reading empty file"""
        # Create empty file
        with open(temp_env_file, "w", encoding="utf-8") as f:
            f.write("")

        lines = FileHandler.read_file(temp_env_file)
        assert lines == []

    def test_read_file_unicode(self, temp_env_file):
        """Test reading file with unicode characters"""
        content = "UNICODE_VAR=café naïve\nEMOJI=🚀\n"
        with open(temp_env_file, "w", encoding="utf-8") as f:
            f.write(content)

        lines = FileHandler.read_file(temp_env_file)

        assert len(lines) == 2
        assert "café naïve" in lines[0]
        assert "🚀" in lines[1]

    def test_filter_lines_basic(self):
        """Test basic line filtering"""
        lines = [
            "# This is a comment\n",
            "VALID_VAR=value\n",
            "\n",
            "   \n",  # Whitespace only
            "ANOTHER_VAR=another_value\n",
            "# Another comment\n",
            "FINAL_VAR=final\n",
        ]

        filtered = FileHandler.filter_lines(lines)

        expected = ["VALID_VAR=value", "ANOTHER_VAR=another_value", "FINAL_VAR=final"]

        assert filtered == expected

    def test_filter_lines_empty_input(self):
        """Test filtering empty line list"""
        filtered = FileHandler.filter_lines([])
        assert filtered == []

    def test_filter_lines_all_comments(self):
        """Test filtering lines with only comments"""
        lines = ["# Comment 1\n", "# Comment 2\n", "   # Comment with spaces\n"]

        filtered = FileHandler.filter_lines(lines)
        assert filtered == []

    def test_filter_lines_all_empty(self):
        """Test filtering lines with only empty lines"""
        lines = ["\n", "   \n", "\t\n", "    \t   \n"]

        filtered = FileHandler.filter_lines(lines)
        assert filtered == []

    def test_filter_lines_mixed_whitespace(self):
        """Test filtering lines with various whitespace patterns"""
        lines = ["  VAR1=value1  \n", "\tVAR2=value2\t\n", "   VAR3   =   value3   \n"]

        filtered = FileHandler.filter_lines(lines)

        expected = ["VAR1=value1", "VAR2=value2", "VAR3   =   value3"]

        assert filtered == expected

    def test_filter_lines_comment_variations(self):
        """Test filtering various comment formats"""
        lines = [
            "#Standard comment\n",
            "# Comment with space\n",
            "   # Indented comment\n",
            "\t#\tComment with tabs\n",
            "VALID=value\n",
            "##Double hash\n",
        ]

        filtered = FileHandler.filter_lines(lines)
        assert filtered == ["VALID=value"]

    def test_filter_lines_preserve_hash_in_values(self):
        """Test that hash symbols in values are preserved"""
        lines = [
            "PASSWORD=secret#123\n",
            "URL=http://example.com#section\n",
            "# This is a comment\n",
            "HASH_VALUE=#startswithash\n",
        ]

        filtered = FileHandler.filter_lines(lines)

        expected = [
            "PASSWORD=secret#123",
            "URL=http://example.com#section",
            "HASH_VALUE=#startswithash",
        ]

        assert filtered == expected

    def test_filter_lines_edge_cases(self):
        """Test edge cases in line filtering"""
        lines = [
            "=value_without_key\n",  # Should be kept for validation to catch
            "KEY_WITHOUT_VALUE=\n",  # Should be kept
            "   =   \n",  # Whitespace around equals
            "#\n",  # Just hash
            "NORMAL=value\n",
        ]

        filtered = FileHandler.filter_lines(lines)

        expected = ["=value_without_key", "KEY_WITHOUT_VALUE=", "=", "NORMAL=value"]

        assert filtered == expected

    def test_filter_lines_no_newlines(self):
        """Test filtering lines without newline characters"""
        lines = ["# Comment", "VAR1=value1", "", "VAR2=value2"]

        filtered = FileHandler.filter_lines(lines)

        expected = ["VAR1=value1", "VAR2=value2"]

        assert filtered == expected

    def test_read_file_with_different_encodings(self, temp_env_file):
        """Test reading files with different content that might cause encoding issues"""
        # Test with various characters that might cause encoding issues
        content = "ASCII=basic\nUTF8=测试\nLATIN=résumé\n"

        with open(temp_env_file, "w", encoding="utf-8") as f:
            f.write(content)

        lines = FileHandler.read_file(temp_env_file)

        assert len(lines) == 3
        assert "basic" in lines[0]
        assert "测试" in lines[1]
        assert "résumé" in lines[2]

    @patch("pathlib.Path.exists")
    def test_file_exists_check(self, mock_exists, temp_env_file):
        """Test file existence checking"""
        # Test when file doesn't exist
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError, match="File not found"):
            FileHandler.read_file("some_file.env")

        mock_exists.assert_called_once()

    def test_static_methods(self):
        """Test that FileHandler methods are static"""
        # Should be able to call without instantiation
        lines = ["# comment\n", "VAR=value\n"]
        filtered = FileHandler.filter_lines(lines)
        assert filtered == ["VAR=value"]

        # Verify methods are static (can be called without instance)
        assert callable(FileHandler.read_file)
        assert callable(FileHandler.filter_lines)
