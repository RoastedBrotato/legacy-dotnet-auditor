"""
Performance Analyzer Module
Detects performance-related issues like large files, DB in loops, etc.
"""

import re
from typing import List
from analyzer.base_analyzer import BaseAnalyzer
from models.data_models import FileInfo, PerformanceIssue, IssueType, IssueSeverity


class PerformanceAnalyzer(BaseAnalyzer):
    """Analyzes files for performance issues"""

    # Thresholds
    LARGE_FILE_THRESHOLD = 300  # lines
    VERY_LARGE_FILE_THRESHOLD = 500  # lines

    # Patterns for database operations
    DB_OPERATION_PATTERNS = [
        r'\.SaveChanges\(\)',
        r'\.SaveChangesAsync\(\)',
        r'\.ExecuteSqlCommand',
        r'\.ExecuteSqlCommandAsync',
        r'\.Query<',
        r'\.ToList\(\)',
        r'\.ToListAsync\(\)',
        r'\.FirstOrDefault\(\)',
        r'\.FirstOrDefaultAsync\(\)',
        r'\.SingleOrDefault\(\)',
        r'\.Find\(',
        r'\.FindAsync\(',
        r'SqlCommand',
        r'SqlDataReader',
    ]

    # Loop patterns
    LOOP_PATTERNS = [
        r'\bfor\s*\(',
        r'\bforeach\s*\(',
        r'\bwhile\s*\(',
    ]

    def analyze(self, file_info: FileInfo) -> List[PerformanceIssue]:
        """
        Analyze a file for performance issues.

        Args:
            file_info: FileInfo object

        Returns:
            List of detected performance issues
        """
        issues = []

        # Check for large files
        if file_info.line_count > self.LARGE_FILE_THRESHOLD:
            issues.append(self._create_large_file_issue(file_info))

        # Only analyze .cs files for code issues
        if file_info.path.suffix == '.cs':
            content = self._read_file(file_info.path)
            lines = self._read_file_lines(file_info.path)

            # Check for DB operations in loops
            db_in_loop_issues = self._detect_db_in_loops(file_info, lines)
            issues.extend(db_in_loop_issues)

            # Check for N+1 query patterns
            n_plus_one_issues = self._detect_n_plus_one(file_info, lines)
            issues.extend(n_plus_one_issues)

        return issues

    def _create_large_file_issue(self, file_info: FileInfo) -> PerformanceIssue:
        """Create an issue for large files"""
        severity = IssueSeverity.MEDIUM
        if file_info.line_count > self.VERY_LARGE_FILE_THRESHOLD:
            severity = IssueSeverity.HIGH

        return PerformanceIssue(
            file_path=file_info.relative_path,
            issue_type=IssueType.LARGE_FILE,
            severity=severity,
            line_number=0,
            description=f"File is {file_info.line_count} lines long (threshold: {self.LARGE_FILE_THRESHOLD})",
            recommendation="Consider refactoring into smaller, focused classes following Single Responsibility Principle"
        )

    def _detect_db_in_loops(self, file_info: FileInfo, lines: List[str]) -> List[PerformanceIssue]:
        """Detect database operations inside loops"""
        issues = []
        in_loop = False
        loop_start_line = 0
        brace_count = 0

        for i, line in enumerate(lines, start=1):
            stripped = line.strip()

            # Detect loop start
            if any(re.search(pattern, stripped) for pattern in self.LOOP_PATTERNS):
                in_loop = True
                loop_start_line = i
                brace_count = 0

            # Track braces to know when we exit the loop
            if in_loop:
                brace_count += stripped.count('{')
                brace_count -= stripped.count('}')

                # Check for DB operations inside loop
                if any(re.search(pattern, stripped) for pattern in self.DB_OPERATION_PATTERNS):
                    issues.append(PerformanceIssue(
                        file_path=file_info.relative_path,
                        issue_type=IssueType.DB_IN_LOOP,
                        severity=IssueSeverity.CRITICAL,
                        line_number=i,
                        description=f"Database operation detected inside loop (started at line {loop_start_line})",
                        code_snippet=self._get_code_snippet(lines, i),
                        recommendation="Move database operations outside loop or use batch operations. Consider using .Include() for eager loading."
                    ))

                # Exit loop when braces balance
                if brace_count == 0 and '{' in line:
                    in_loop = False

        return issues

    def _detect_n_plus_one(self, file_info: FileInfo, lines: List[str]) -> List[PerformanceIssue]:
        """Detect potential N+1 query patterns"""
        issues = []

        # Look for pattern: foreach with navigation property access
        for i, line in enumerate(lines, start=1):
            if i < len(lines) - 3:  # Need to look ahead
                # Check for foreach over collection
                if re.search(r'foreach\s*\(', line):
                    # Check next few lines for property navigation
                    context = '\n'.join(lines[i:min(i + 10, len(lines))])

                    # Look for navigation property patterns that might cause lazy loading
                    if re.search(r'\.\w+\.\w+', context) and not re.search(r'\.Include\(', context):
                        # This might be an N+1 query
                        issues.append(PerformanceIssue(
                            file_path=file_info.relative_path,
                            issue_type=IssueType.N_PLUS_ONE,
                            severity=IssueSeverity.HIGH,
                            line_number=i,
                            description="Potential N+1 query: Navigation property accessed in loop without eager loading",
                            code_snippet=self._get_code_snippet(lines, i, context=4),
                            recommendation="Use .Include() or .ThenInclude() to eager load related data before the loop"
                        ))
                        break  # Only report once per foreach

        return issues
