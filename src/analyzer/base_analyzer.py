"""
Base Analyzer Module
Abstract base class for all analyzers.
"""

from abc import ABC, abstractmethod
from typing import List
from models.data_models import FileInfo, AnalysisResult, PerformanceIssue


class BaseAnalyzer(ABC):
    """Abstract base class for file analyzers"""

    def __init__(self):
        """Initialize the analyzer"""
        self.name = self.__class__.__name__

    @abstractmethod
    def analyze(self, file_info: FileInfo) -> List[PerformanceIssue]:
        """
        Analyze a file and return detected issues.

        Args:
            file_info: FileInfo object containing file metadata

        Returns:
            List of detected PerformanceIssue objects
        """
        pass

    def _read_file(self, file_path) -> str:
        """Read file content safely"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            return ""

    def _read_file_lines(self, file_path) -> List[str]:
        """Read file as list of lines"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.readlines()
        except Exception:
            return []

    def _get_code_snippet(self, lines: List[str], line_number: int, context: int = 2) -> str:
        """
        Extract a code snippet around a specific line.

        Args:
            lines: List of file lines
            line_number: Target line number (1-indexed)
            context: Number of lines before/after to include

        Returns:
            Code snippet as string
        """
        start = max(0, line_number - context - 1)
        end = min(len(lines), line_number + context)
        snippet_lines = lines[start:end]

        # Add line numbers
        numbered_lines = []
        for i, line in enumerate(snippet_lines, start=start + 1):
            numbered_lines.append(f"{i:4d} | {line.rstrip()}")

        return "\n".join(numbered_lines)
