"""
File Classifier Module
Categorizes .NET files by their type (Controller, Service, Repository, etc.)
based on naming conventions, inheritance, and content patterns.
"""

import re
from typing import List, Set
from models.data_models import FileInfo, FileType


class FileClassifier:
    """Classifies C# files into categories"""

    # Patterns for identifying file types by name
    CONTROLLER_PATTERNS = [
        r'Controller\.cs$',
        r'Controllers/',
    ]

    API_CONTROLLER_PATTERNS = [
        r'ApiController\.cs$',
        r'Api.*Controller\.cs$',
    ]

    SERVICE_PATTERNS = [
        r'Service\.cs$',
        r'Services/',
        r'Manager\.cs$',
        r'Managers/',
        r'Handler\.cs$',
        r'Handlers/',
    ]

    REPOSITORY_PATTERNS = [
        r'Repository\.cs$',
        r'Repositories/',
        r'Dal\.cs$',
        r'DataAccess/',
    ]

    MODEL_PATTERNS = [
        r'Models/',
        r'Entities/',
        r'Dto\.cs$',
        r'ViewModel\.cs$',
        r'Model\.cs$',
    ]

    def __init__(self):
        """Initialize the classifier"""
        pass

    def classify(self, file_info: FileInfo) -> FileInfo:
        """
        Classify a file and update its metadata.

        Args:
            file_info: FileInfo object to classify

        Returns:
            Updated FileInfo object with classification
        """
        # Read file content
        content = self._read_file(file_info.path)

        # Classify file type
        file_info.file_type = self._determine_file_type(
            file_info.relative_path,
            content
        )

        # Extract class names and methods
        file_info.class_names = self._extract_class_names(content)
        file_info.method_names = self._extract_method_names(content)

        # Detect technology usage
        file_info.has_async = self._has_async(content)
        file_info.has_entity_framework = self._has_entity_framework(content)
        file_info.has_sql = self._has_sql(content)

        return file_info

    def classify_batch(self, files: List[FileInfo]) -> List[FileInfo]:
        """
        Classify multiple files.

        Args:
            files: List of FileInfo objects

        Returns:
            List of classified FileInfo objects
        """
        return [self.classify(f) for f in files]

    def _read_file(self, file_path) -> str:
        """Read file content safely"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            return ""

    def _determine_file_type(self, relative_path: str, content: str) -> FileType:
        """
        Determine file type based on path and content.

        Args:
            relative_path: Relative path of the file
            content: File content

        Returns:
            Detected FileType
        """
        # Check for .cshtml (View)
        if relative_path.endswith('.cshtml'):
            return FileType.VIEW

        # Check API Controller first (more specific)
        if any(re.search(pattern, relative_path) for pattern in self.API_CONTROLLER_PATTERNS):
            return FileType.API_CONTROLLER

        # Check for ApiController inheritance
        if re.search(r':\s*ApiController', content):
            return FileType.API_CONTROLLER

        # Check Controller
        if any(re.search(pattern, relative_path) for pattern in self.CONTROLLER_PATTERNS):
            return FileType.CONTROLLER

        # Check for Controller inheritance
        if re.search(r':\s*Controller', content):
            return FileType.CONTROLLER

        # Check Repository
        if any(re.search(pattern, relative_path) for pattern in self.REPOSITORY_PATTERNS):
            return FileType.REPOSITORY

        # Check for IRepository interface
        if re.search(r':\s*I.*Repository', content):
            return FileType.REPOSITORY

        # Check Service
        if any(re.search(pattern, relative_path) for pattern in self.SERVICE_PATTERNS):
            return FileType.SERVICE

        # Check for IService interface
        if re.search(r':\s*I.*Service', content):
            return FileType.SERVICE

        # Check Model
        if any(re.search(pattern, relative_path) for pattern in self.MODEL_PATTERNS):
            return FileType.MODEL

        # Check for config files
        if 'web.config' in relative_path.lower() or 'app.config' in relative_path.lower():
            return FileType.CONFIG

        return FileType.UNKNOWN

    def _extract_class_names(self, content: str) -> List[str]:
        """Extract class names from C# content"""
        pattern = r'(?:public|internal|private|protected)?\s+(?:static\s+)?(?:partial\s+)?class\s+(\w+)'
        matches = re.findall(pattern, content)
        return matches

    def _extract_method_names(self, content: str) -> List[str]:
        """Extract method names from C# content"""
        # Match public/private/protected methods (both sync and async)
        pattern = r'(?:public|private|protected|internal)\s+(?:static\s+)?(?:async\s+)?(?:Task<?[^>]*>?|void|[\w<>]+)\s+(\w+)\s*\('
        matches = re.findall(pattern, content)
        return matches

    def _has_async(self, content: str) -> bool:
        """Check if file uses async/await"""
        return bool(re.search(r'\basync\b', content) or re.search(r'\bawait\b', content))

    def _has_entity_framework(self, content: str) -> bool:
        """Check if file uses Entity Framework"""
        patterns = [
            r'using\s+System\.Data\.Entity',
            r'using\s+Microsoft\.EntityFrameworkCore',
            r'DbContext',
            r'DbSet<',
        ]
        return any(re.search(pattern, content) for pattern in patterns)

    def _has_sql(self, content: str) -> bool:
        """Check if file contains SQL queries"""
        patterns = [
            r'SqlCommand',
            r'SqlConnection',
            r'ExecuteSqlCommand',
            r'FromSql',
            r'@"SELECT\s+',
            r"'SELECT\s+",
            r'@"INSERT\s+',
            r'@"UPDATE\s+',
            r'@"DELETE\s+',
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns)
