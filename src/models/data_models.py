"""
Data models for the Legacy .NET Auditor.
These classes represent the core data structures used throughout the analysis pipeline.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional
from pathlib import Path


class FileType(Enum):
    """Classification of .NET file types"""
    CONTROLLER = "Controller"
    API_CONTROLLER = "ApiController"
    SERVICE = "Service"
    REPOSITORY = "Repository"
    MODEL = "Model"
    VIEW = "View"
    CONFIG = "Config"
    UNKNOWN = "Unknown"


class IssueType(Enum):
    """Types of issues that can be detected"""
    LARGE_FILE = "LargeFile"
    DB_IN_LOOP = "DatabaseInLoop"
    SYNC_BLOCKING = "SynchronousBlocking"
    SEQUENTIAL_HTTP = "SequentialHttpCalls"
    DUPLICATE_PATTERN = "DuplicatePattern"
    NO_ASYNC = "NoAsyncUsage"
    N_PLUS_ONE = "NPlusOneQuery"
    MISSING_ERROR_HANDLING = "MissingErrorHandling"


class IssueSeverity(Enum):
    """Severity levels for detected issues"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Info"


@dataclass
class FileInfo:
    """Represents a scanned file with metadata"""
    path: Path
    relative_path: str
    file_type: FileType = FileType.UNKNOWN
    line_count: int = 0
    class_names: List[str] = field(default_factory=list)
    method_names: List[str] = field(default_factory=list)
    has_async: bool = False
    has_entity_framework: bool = False
    has_sql: bool = False

    def __post_init__(self):
        if isinstance(self.path, str):
            self.path = Path(self.path)


@dataclass
class PerformanceIssue:
    """Represents a detected performance or modernization issue"""
    file_path: str
    issue_type: IssueType
    severity: IssueSeverity
    line_number: int
    description: str
    code_snippet: str = ""
    recommendation: str = ""

    def __str__(self):
        return f"[{self.severity.value}] {self.issue_type.value} at {self.file_path}:{self.line_number}"


@dataclass
class AnalysisResult:
    """Results from analyzing a single file"""
    file_info: FileInfo
    issues: List[PerformanceIssue] = field(default_factory=list)
    async_opportunities: List[str] = field(default_factory=list)
    signalr_opportunities: List[str] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0

    @property
    def critical_issues(self) -> List[PerformanceIssue]:
        return [i for i in self.issues if i.severity == IssueSeverity.CRITICAL]

    @property
    def high_issues(self) -> List[PerformanceIssue]:
        return [i for i in self.issues if i.severity == IssueSeverity.HIGH]


@dataclass
class AuditReport:
    """Complete audit report data"""
    project_path: str
    total_files: int
    analyzed_files: int
    file_structure: Dict[FileType, int] = field(default_factory=dict)
    endpoints: List[Dict[str, str]] = field(default_factory=list)
    results: List[AnalysisResult] = field(default_factory=list)

    @property
    def total_issues(self) -> int:
        return sum(len(r.issues) for r in self.results)

    @property
    def critical_issues(self) -> List[PerformanceIssue]:
        issues = []
        for result in self.results:
            issues.extend(result.critical_issues)
        return issues

    @property
    def high_issues(self) -> List[PerformanceIssue]:
        issues = []
        for result in self.results:
            issues.extend(result.high_issues)
        return issues

    @property
    def all_issues(self) -> List[PerformanceIssue]:
        issues = []
        for result in self.results:
            issues.extend(result.issues)
        return issues
