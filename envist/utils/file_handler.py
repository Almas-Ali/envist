"""File handling utilities for Envist"""

from pathlib import Path
from typing import List

from ..core.exceptions import FileNotFoundError


class FileHandler:
    """Handles file operations for .env files"""

    @staticmethod
    def read_file(path: str = ".env") -> List[str]:
        """Read and return lines from file

        Args:
            path: Path to the file

        Returns:
            List of lines from the file

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file_path = Path(path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.readlines()
        except IOError as e:
            raise FileNotFoundError(f"Error reading file {path}: {e}")

    @staticmethod
    def filter_lines(lines: List[str], preserve_whitespace: bool = False) -> List[str]:
        """Filter out empty lines and comments

        Args:
            lines: Raw lines from file
            preserve_whitespace: If True, preserve trailing whitespace for values

        Returns:
            Filtered lines
        """
        filtered = []
        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                continue

            # Find comments, ignoring those inside quotes
            in_quotes = False
            quote_char = ""
            comment_start = -1
            for i, char in enumerate(line):
                if char in ("'", '"'):
                    if not in_quotes:
                        in_quotes = True
                        quote_char = char
                    elif char == quote_char:
                        in_quotes = False
                elif char == "#" and not in_quotes:
                    # A comment is a '#' that is at the start of the stripped line
                    # or is preceded by whitespace.
                    if stripped_line.startswith("#") or (
                        i > 0 and line[i - 1].isspace()
                    ):
                        comment_start = i
                        break

            if comment_start != -1:
                line = line[:comment_start]

            if preserve_whitespace:
                line = line.rstrip("\r\n")
            else:
                line = line.strip()

            if line:
                filtered.append(line)
        return filtered
