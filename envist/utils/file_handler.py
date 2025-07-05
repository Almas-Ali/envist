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
    def filter_lines(lines: List[str]) -> List[str]:
        """Filter out empty lines and comments

        Args:
            lines: Raw lines from file

        Returns:
            Filtered lines
        """
        return [
            line.strip()
            for line in lines
            if line.strip() and not line.strip().startswith("#")
        ]
