"""
File Scanner Module
Recursively scans a directory for .NET project files (.cs files).
"""

import os
from pathlib import Path
from typing import List, Set
from models.data_models import FileInfo


class FileScanner:
    """Scans a directory tree for C# source files"""

    # Directories to exclude from scanning
    EXCLUDED_DIRS = {
        'bin', 'obj', 'packages', 'node_modules', '.git', '.vs',
        'TestResults', 'Debug', 'Release', '.vscode', '.idea'
    }

    # File extensions to scan
    INCLUDE_EXTENSIONS = {'.cs', '.cshtml'}

    def __init__(self, root_path: str):
        """
        Initialize the scanner.

        Args:
            root_path: Root directory of the .NET project
        """
        self.root_path = Path(root_path).resolve()
        if not self.root_path.exists():
            raise ValueError(f"Path does not exist: {root_path}")
        if not self.root_path.is_dir():
            raise ValueError(f"Path is not a directory: {root_path}")

    def scan(self) -> List[FileInfo]:
        """
        Recursively scan for C# files.

        Returns:
            List of FileInfo objects for each discovered file
        """
        files = []
        for file_path in self._walk_directory(self.root_path):
            file_info = self._create_file_info(file_path)
            files.append(file_info)

        return files

    def _walk_directory(self, directory: Path) -> List[Path]:
        """
        Recursively walk directory tree, excluding specified directories.

        Args:
            directory: Directory to walk

        Returns:
            List of file paths
        """
        found_files = []

        try:
            for entry in directory.iterdir():
                # Skip excluded directories
                if entry.is_dir():
                    if entry.name in self.EXCLUDED_DIRS:
                        continue
                    # Recurse into subdirectory
                    found_files.extend(self._walk_directory(entry))

                # Include files with matching extensions
                elif entry.is_file():
                    if entry.suffix in self.INCLUDE_EXTENSIONS:
                        found_files.append(entry)

        except PermissionError:
            # Skip directories we can't access
            pass

        return found_files

    def _create_file_info(self, file_path: Path) -> FileInfo:
        """
        Create a FileInfo object with basic metadata.

        Args:
            file_path: Path to the file

        Returns:
            FileInfo object with initial metadata
        """
        relative_path = str(file_path.relative_to(self.root_path))

        # Count lines in file
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                line_count = sum(1 for _ in f)
        except Exception:
            line_count = 0

        return FileInfo(
            path=file_path,
            relative_path=relative_path,
            line_count=line_count
        )

    def get_project_stats(self) -> dict:
        """
        Get basic statistics about the scanned project.

        Returns:
            Dictionary with project statistics
        """
        files = self.scan()
        total_lines = sum(f.line_count for f in files)

        return {
            'total_files': len(files),
            'total_lines': total_lines,
            'cs_files': len([f for f in files if f.path.suffix == '.cs']),
            'cshtml_files': len([f for f in files if f.path.suffix == '.cshtml'])
        }
