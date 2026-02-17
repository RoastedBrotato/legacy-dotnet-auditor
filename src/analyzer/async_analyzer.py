"""
Async Analyzer Module
Detects synchronous blocking calls and identifies async/await opportunities.
"""

import re
from typing import List
from analyzer.base_analyzer import BaseAnalyzer
from models.data_models import FileInfo, PerformanceIssue, IssueType, IssueSeverity


class AsyncAnalyzer(BaseAnalyzer):
    """Analyzes files for async/await issues and opportunities"""

    # Patterns for synchronous blocking calls
    BLOCKING_PATTERNS = [
        (r'\.Result\b', 'Task.Result blocks the thread'),
        (r'\.Wait\(\)', 'Task.Wait() blocks the thread'),
        (r'\.GetAwaiter\(\)\.GetResult\(\)', 'GetAwaiter().GetResult() blocks the thread'),
    ]

    # Patterns for I/O operations that should be async
    IO_PATTERNS = [
        r'File\.ReadAllText\(',
        r'File\.ReadAllLines\(',
        r'File\.WriteAllText\(',
        r'File\.WriteAllLines\(',
        r'StreamReader\.Read\(',
        r'StreamWriter\.Write\(',
        r'HttpClient\..*\(',
        r'WebClient\.',
        r'SqlCommand\.Execute',
        r'SqlDataReader\.Read\(',
    ]

    # HTTP client patterns for sequential calls
    HTTP_CALL_PATTERNS = [
        r'HttpClient',
        r'WebClient',
        r'RestClient',
        r'HttpWebRequest',
        r'\.GetAsync\(',
        r'\.PostAsync\(',
        r'\.PutAsync\(',
        r'\.DeleteAsync\(',
    ]

    def analyze(self, file_info: FileInfo) -> List[PerformanceIssue]:
        """
        Analyze a file for async/await issues.

        Args:
            file_info: FileInfo object

        Returns:
            List of detected async-related issues
        """
        issues = []

        if file_info.path.suffix != '.cs':
            return issues

        lines = self._read_file_lines(file_info.path)

        # Detect synchronous blocking calls
        blocking_issues = self._detect_blocking_calls(file_info, lines)
        issues.extend(blocking_issues)

        # Detect sequential HTTP calls
        sequential_http_issues = self._detect_sequential_http(file_info, lines)
        issues.extend(sequential_http_issues)

        # Detect missing async in I/O operations
        sync_io_issues = self._detect_sync_io(file_info, lines)
        issues.extend(sync_io_issues)

        return issues

    def _detect_blocking_calls(self, file_info: FileInfo, lines: List[str]) -> List[PerformanceIssue]:
        """Detect synchronous blocking calls on Tasks"""
        issues = []

        for i, line in enumerate(lines, start=1):
            for pattern, description in self.BLOCKING_PATTERNS:
                if re.search(pattern, line):
                    issues.append(PerformanceIssue(
                        file_path=file_info.relative_path,
                        issue_type=IssueType.SYNC_BLOCKING,
                        severity=IssueSeverity.CRITICAL,
                        line_number=i,
                        description=f"Synchronous blocking call detected: {description}",
                        code_snippet=self._get_code_snippet(lines, i),
                        recommendation="Replace with 'await' and make the containing method async"
                    ))

        return issues

    def _detect_sequential_http(self, file_info: FileInfo, lines: List[str]) -> List[PerformanceIssue]:
        """Detect sequential HTTP calls that could be parallelized"""
        issues = []
        http_calls = []

        # Find all HTTP calls in the file
        for i, line in enumerate(lines, start=1):
            if any(re.search(pattern, line) for pattern in self.HTTP_CALL_PATTERNS):
                # Check if it's an await call
                if 'await' in line:
                    http_calls.append(i)

        # If we have multiple HTTP calls close together, flag as potential sequential calls
        if len(http_calls) >= 2:
            for i in range(len(http_calls) - 1):
                line1 = http_calls[i]
                line2 = http_calls[i + 1]

                # If calls are within 20 lines of each other
                if line2 - line1 <= 20:
                    # Check if they're actually sequential (not in different methods)
                    context = lines[line1 - 1:line2]
                    context_str = ''.join(context)

                    # If no new method declaration between them, they might be sequential
                    if not re.search(r'(public|private|protected)\s+.*\s+\w+\s*\(', context_str):
                        issues.append(PerformanceIssue(
                            file_path=file_info.relative_path,
                            issue_type=IssueType.SEQUENTIAL_HTTP,
                            severity=IssueSeverity.HIGH,
                            line_number=line1,
                            description=f"Sequential HTTP calls detected (lines {line1} and {line2})",
                            code_snippet=self._get_code_snippet(lines, line1, context=5),
                            recommendation="Consider using Task.WhenAll() to execute HTTP calls in parallel if they are independent"
                        ))
                        break  # Only report once per pair

        return issues

    def _detect_sync_io(self, file_info: FileInfo, lines: List[str]) -> List[PerformanceIssue]:
        """Detect synchronous I/O operations that should be async"""
        issues = []

        for i, line in enumerate(lines, start=1):
            # Skip if already in an async context with await
            if 'await' in line:
                continue

            # Check for synchronous I/O patterns
            for pattern in self.IO_PATTERNS:
                if re.search(pattern, line):
                    issues.append(PerformanceIssue(
                        file_path=file_info.relative_path,
                        issue_type=IssueType.NO_ASYNC,
                        severity=IssueSeverity.MEDIUM,
                        line_number=i,
                        description="Synchronous I/O operation detected",
                        code_snippet=self._get_code_snippet(lines, i),
                        recommendation="Replace with async equivalent (e.g., File.ReadAllTextAsync, HttpClient with await)"
                    ))
                    break  # Only report once per line

        return issues

    def identify_async_opportunities(self, file_info: FileInfo) -> List[str]:
        """
        Identify methods that could benefit from async/await.

        Args:
            file_info: FileInfo object

        Returns:
            List of opportunity descriptions
        """
        opportunities = []

        if file_info.path.suffix != '.cs':
            return opportunities

        content = self._read_file(file_info.path)

        # Check if file has any async usage
        if not file_info.has_async:
            # Check if it has I/O operations
            has_io = any(re.search(pattern, content) for pattern in self.IO_PATTERNS)
            has_db = file_info.has_entity_framework or file_info.has_sql
            has_http = any(re.search(pattern, content) for pattern in self.HTTP_CALL_PATTERNS)

            if has_io or has_db or has_http:
                operations = []
                if has_io:
                    operations.append("file I/O")
                if has_db:
                    operations.append("database operations")
                if has_http:
                    operations.append("HTTP calls")

                opportunities.append(
                    f"{file_info.relative_path}: No async/await usage found despite {', '.join(operations)}"
                )

        return opportunities
