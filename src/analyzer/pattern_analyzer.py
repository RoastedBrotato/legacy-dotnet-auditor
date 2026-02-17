"""
Pattern Analyzer Module
Detects duplicate patterns, architectural issues, and identifies modernization opportunities.
"""

import re
from typing import List, Dict
from collections import defaultdict
from analyzer.base_analyzer import BaseAnalyzer
from models.data_models import FileInfo, PerformanceIssue, IssueType, IssueSeverity


class PatternAnalyzer(BaseAnalyzer):
    """Analyzes files for duplicate patterns and modernization opportunities"""

    def __init__(self):
        super().__init__()
        # Track method signatures across files to detect duplicates
        self.method_signatures: Dict[str, List[str]] = defaultdict(list)
        self.repository_patterns: Dict[str, List[str]] = defaultdict(list)

    # Patterns for real-time opportunities
    REALTIME_INDICATORS = [
        r'Timer\(',
        r'polling',
        r'setInterval',
        r'while\s*\(true\)',
        r'Thread\.Sleep',
        r'Task\.Delay.*while',
        r'GetLatest',
        r'GetUpdates',
        r'CheckStatus',
        r'RefreshData',
    ]

    # Patterns for queue opportunities
    QUEUE_INDICATORS = [
        r'SendEmail',
        r'SendNotification',
        r'ProcessReport',
        r'GenerateReport',
        r'ExportData',
        r'ImportData',
        r'BackgroundJob',
        r'Task\.Run\(',
    ]

    def analyze(self, file_info: FileInfo) -> List[PerformanceIssue]:
        """
        Analyze a file for pattern-related issues.

        Args:
            file_info: FileInfo object

        Returns:
            List of detected issues
        """
        issues = []

        if file_info.path.suffix != '.cs':
            return issues

        content = self._read_file(file_info.path)
        lines = self._read_file_lines(file_info.path)

        # Track method signatures for duplicate detection
        self._track_methods(file_info, content)

        # Track repository patterns
        if file_info.file_type.value == 'Repository':
            self._track_repository_patterns(file_info, content)

        return issues

    def analyze_batch(self, files: List[FileInfo]) -> List[PerformanceIssue]:
        """
        Analyze multiple files and detect cross-file patterns.

        Args:
            files: List of FileInfo objects

        Returns:
            List of detected issues
        """
        issues = []

        # First pass: track all patterns
        for file_info in files:
            self.analyze(file_info)

        # Second pass: detect duplicates
        duplicate_issues = self._detect_duplicate_patterns()
        issues.extend(duplicate_issues)

        return issues

    def _track_methods(self, file_info: FileInfo, content: str):
        """Track method signatures for duplicate detection"""
        # Extract method signatures
        pattern = r'(?:public|private|protected)\s+(?:static\s+)?(?:async\s+)?(?:\w+<?[^>]*>?)\s+(\w+)\s*\([^)]*\)'
        matches = re.finditer(pattern, content)

        for match in matches:
            method_name = match.group(1)
            # Ignore common method names like constructors, Main, etc.
            if method_name not in ['Main', 'Configure', 'Dispose']:
                signature = match.group(0)
                self.method_signatures[signature].append(file_info.relative_path)

    def _track_repository_patterns(self, file_info: FileInfo, content: str):
        """Track repository method patterns"""
        # Common repository method patterns
        patterns = ['GetById', 'GetAll', 'Add', 'Update', 'Delete', 'Save', 'Find']

        for pattern in patterns:
            if re.search(rf'\b{pattern}\b', content):
                self.repository_patterns[pattern].append(file_info.relative_path)

    def _detect_duplicate_patterns(self) -> List[PerformanceIssue]:
        """Detect duplicate method signatures across files"""
        issues = []

        # Find signatures that appear in multiple files
        for signature, files in self.method_signatures.items():
            if len(files) > 1:
                issues.append(PerformanceIssue(
                    file_path=', '.join(files[:3]),  # Show first 3 files
                    issue_type=IssueType.DUPLICATE_PATTERN,
                    severity=IssueSeverity.MEDIUM,
                    line_number=0,
                    description=f"Duplicate method pattern found in {len(files)} files: {signature[:80]}...",
                    recommendation="Consider extracting common logic into a shared service or base class"
                ))

        # Check for duplicate repository patterns
        for pattern, files in self.repository_patterns.items():
            if len(files) > 2:  # More than 2 repositories with same method
                issues.append(PerformanceIssue(
                    file_path=', '.join(files[:3]),
                    issue_type=IssueType.DUPLICATE_PATTERN,
                    severity=IssueSeverity.LOW,
                    line_number=0,
                    description=f"Repository pattern '{pattern}' repeated in {len(files)} repositories",
                    recommendation="Consider using a generic repository pattern or base repository class"
                ))

        return issues

    def identify_signalr_opportunities(self, file_info: FileInfo) -> List[str]:
        """
        Identify methods that could benefit from SignalR.

        Args:
            file_info: FileInfo object

        Returns:
            List of opportunity descriptions
        """
        opportunities = []

        if file_info.path.suffix != '.cs':
            return opportunities

        content = self._read_file(file_info.path)
        lines = self._read_file_lines(file_info.path)

        # Check for real-time indicators
        for i, line in enumerate(lines, start=1):
            for pattern in self.REALTIME_INDICATORS:
                if re.search(pattern, line, re.IGNORECASE):
                    opportunities.append(
                        f"{file_info.relative_path}:{i} - Potential real-time use case (polling/timer detected)"
                    )
                    break  # Only report once per line

        return opportunities

    def identify_queue_opportunities(self, file_info: FileInfo) -> List[str]:
        """
        Identify methods that could benefit from background queues.

        Args:
            file_info: FileInfo object

        Returns:
            List of opportunity descriptions
        """
        opportunities = []

        if file_info.path.suffix != '.cs':
            return opportunities

        content = self._read_file(file_info.path)
        lines = self._read_file_lines(file_info.path)

        # Check for queue indicators
        found_patterns = set()
        for i, line in enumerate(lines, start=1):
            for pattern in self.QUEUE_INDICATORS:
                if re.search(pattern, line, re.IGNORECASE) and pattern not in found_patterns:
                    opportunities.append(
                        f"{file_info.relative_path}:{i} - Background queue candidate (long-running task detected)"
                    )
                    found_patterns.add(pattern)

        return opportunities
