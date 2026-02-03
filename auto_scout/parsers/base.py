"""Base parser class."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class Parser(ABC):
    """Base class for scan output parsers."""

    @abstractmethod
    def parse(self, source: str | Path) -> Any:
        """
        Parse scan output.

        Args:
            source: Either raw output string or path to output file

        Returns:
            Parsed data structure
        """
        pass

    @abstractmethod
    def parse_file(self, file_path: Path) -> Any:
        """
        Parse scan output from a file.

        Args:
            file_path: Path to the file to parse

        Returns:
            Parsed data structure
        """
        pass

    @abstractmethod
    def parse_string(self, content: str) -> Any:
        """
        Parse scan output from a string.

        Args:
            content: Raw output as string

        Returns:
            Parsed data structure
        """
        pass
