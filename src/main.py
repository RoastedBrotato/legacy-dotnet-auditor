#!/usr/bin/env python3
"""
Legacy .NET Auditor - Main Entry Point
Orchestrates the complete audit pipeline.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

from models.data_models import (
    AnalysisResult,
    AuditReport,
    FileInfo,
    FileType,
)
from scanner.file_scanner import FileScanner
from classifier.file_classifier import FileClassifier
from analyzer.performance_analyzer import PerformanceAnalyzer
from analyzer.async_analyzer import AsyncAnalyzer
from analyzer.pattern_analyzer import PatternAnalyzer
from reporter.markdown_reporter import MarkdownReporter


class LegacyDotNetAuditor:
    """Main auditor orchestrator"""

    ENDPOINT_PATTERN = re.compile(
        r"public\s+(?:async\s+)?(?:[\w<>,\[\]\.?]+)\s+(\w+)\s*\(",
        re.MULTILINE,
    )

    METHOD_PATTERN = re.compile(
        r"(?:public|private|protected|internal)\s+"
        r"(?:virtual\s+|override\s+|static\s+|sealed\s+|new\s+|partial\s+)*"
        r"(?:async\s+)?[\w<>,\[\]\.\?]+\s+(\w+)\s*\([^;{}]*\)\s*\{",
        re.MULTILINE,
    )

    FIELD_PATTERN = re.compile(
        r"(?:private|protected|internal)\s+(?:readonly\s+)?"
        r"([A-Za-z_]\w*(?:<[^>]+>)?)\s+(_[A-Za-z_]\w*)\s*;"
    )

    MEMBER_CALL_PATTERN = re.compile(r"(_[A-Za-z_]\w*)\s*\.\s*([A-Za-z_]\w*)\s*\(")

    DB_TOUCH_PATTERNS = [
        r"\.SaveChanges(?:Async)?\s*\(",
        r"\.ExecuteSql(?:Command|Raw|Interpolated)(?:Async)?\s*\(",
        r"\.FromSql(?:Raw|Interpolated)?\s*\(",
        r"\.ToList(?:Async)?\s*\(",
        r"\.FirstOrDefault(?:Async)?\s*\(",
        r"\.SingleOrDefault(?:Async)?\s*\(",
        r"\.Find(?:Async)?\s*\(",
        r"\.Any(?:Async)?\s*\(",
        r"\.Count(?:Async)?\s*\(",
        r"SqlCommand\s*\(",
        r"SqlConnection\s*\(",
        r"SqlDataReader\b",
        r"CommandType\.StoredProcedure",
    ]

    SQL_STRING_PATTERN = re.compile(r"(?:\$@|@\$|@|\$)?\"(?:\"\"|\\\"|[^\"])*\"", re.DOTALL)

    SP_EXEC_PATTERN = re.compile(r"\bEXEC(?:UTE)?\s+((?:\[?\w+\]?\.)*\[?\w+\]?)", re.IGNORECASE)

    COMMAND_TEXT_PATTERN = re.compile(
        r"CommandText\s*=\s*@?\"([^\"]+)\"", re.IGNORECASE
    )

    SQL_FRAGMENT_PATTERN = re.compile(
        r"\b(select|insert|update|delete|merge|with|join|exec(?:ute)?)\b", re.IGNORECASE
    )

    def __init__(
        self,
        project_path: str,
        output_path: str = "reports/audit.md",
        database_hotspot_mode: bool = False,
    ):
        """
        Initialize the auditor.

        Args:
            project_path: Path to the .NET project root
            output_path: Path for the output report
            database_hotspot_mode: Enable database hotspot graphing and SQL/SP extraction
        """
        self.project_path = Path(project_path).resolve()
        self.output_path = output_path
        self.database_hotspot_mode = database_hotspot_mode

        # Initialize components
        self.scanner = FileScanner(str(self.project_path))
        self.classifier = FileClassifier()
        self.performance_analyzer = PerformanceAnalyzer()
        self.async_analyzer = AsyncAnalyzer()
        self.pattern_analyzer = PatternAnalyzer()
        self.reporter = MarkdownReporter(output_path)

    def run(self) -> str:
        """
        Run the complete audit pipeline.

        Returns:
            Path to the generated report
        """
        print("🔍 Legacy .NET Auditor")
        print("=" * 60)
        print(f"Project: {self.project_path}")
        print()

        # Step 1: Scan files
        print("📂 Step 1/6: Scanning project files...")
        files = self.scanner.scan()
        print(f"   Found {len(files)} files")

        # Step 2: Classify files
        print("🏷️  Step 2/6: Classifying files...")
        classified_files = self.classifier.classify_batch(files)
        file_structure = self._build_file_structure(classified_files)
        print(f"   Classified {len(classified_files)} files")

        # Step 3: Analyze files
        print("🔎 Step 3/6: Analyzing code...")
        results = self._analyze_files(classified_files)
        print(f"   Analyzed {len(results)} files")
        print(f"   Found {sum(len(r.issues) for r in results)} issues")

        # Step 4: Extract endpoints
        print("🌐 Step 4/6: Extracting endpoints...")
        endpoints = self._extract_endpoints(classified_files)
        print(f"   Found {len(endpoints)} endpoints")

        # Step 5: Database hotspot mode
        db_call_graph: List[dict] = []
        db_hotspot_endpoints: List[dict] = []
        stored_procedures: List[str] = []
        sql_fragments: List[str] = []

        if self.database_hotspot_mode:
            print("🧪 Step 5/6: Running database hotspot mode...")
            db_call_graph, db_hotspot_endpoints, stored_procedures, sql_fragments = self._analyze_database_hotspots(
                classified_files,
                endpoints,
            )
            print(f"   Built {len(db_call_graph)} endpoint DB call paths")
            print(f"   Hotspots (multi-touch endpoints): {len(db_hotspot_endpoints)}")
            print(f"   Stored procedures referenced: {len(stored_procedures)}")

        # Step 6: Generate report
        print("📝 Step 6/6: Generating report...")
        audit_report = AuditReport(
            project_path=str(self.project_path),
            total_files=len(files),
            analyzed_files=len(results),
            file_structure=file_structure,
            endpoints=endpoints,
            results=results,
            database_hotspot_mode=self.database_hotspot_mode,
            db_call_graph=db_call_graph,
            db_hotspot_endpoints=db_hotspot_endpoints,
            stored_procedures=stored_procedures,
            sql_fragments=sql_fragments,
        )

        report_path = self.reporter.generate(audit_report)
        print(f"   Report saved to: {report_path}")

        # Print summary
        print()
        print("=" * 60)
        print("📊 Summary:")
        print(f"   Total Issues: {audit_report.total_issues}")
        print(f"   Critical: {len(audit_report.critical_issues)}")
        print(f"   High: {len(audit_report.high_issues)}")
        if self.database_hotspot_mode:
            print(f"   DB Hotspots: {len(db_hotspot_endpoints)}")
        print()
        print(f"✅ Audit complete! Report: {report_path}")

        return report_path

    def _build_file_structure(self, files: List[FileInfo]) -> dict:
        """Build file structure summary"""
        structure = {}
        for file_info in files:
            file_type = file_info.file_type
            structure[file_type] = structure.get(file_type, 0) + 1
        return structure

    def _analyze_files(self, files: List[FileInfo]) -> List[AnalysisResult]:
        """Analyze all files and collect issues"""
        results = []

        for i, file_info in enumerate(files, 1):
            if i % 10 == 0:
                print(f"   Progress: {i}/{len(files)} files...", end='\r')

            issues = []
            issues.extend(self.performance_analyzer.analyze(file_info))
            issues.extend(self.async_analyzer.analyze(file_info))
            issues.extend(self.pattern_analyzer.analyze(file_info))

            async_opportunities = self.async_analyzer.identify_async_opportunities(file_info)
            signalr_opportunities = self.pattern_analyzer.identify_signalr_opportunities(file_info)

            results.append(
                AnalysisResult(
                    file_info=file_info,
                    issues=issues,
                    async_opportunities=async_opportunities,
                    signalr_opportunities=signalr_opportunities,
                )
            )

        batch_issues = self.pattern_analyzer.analyze_batch(files)
        if batch_issues and results:
            results[0].issues.extend(batch_issues)

        print()
        return results

    def _extract_endpoints(self, files: List[FileInfo]) -> List[dict]:
        """Extract API endpoints from controllers"""
        endpoints = []

        for file_info in files:
            if file_info.file_type not in [FileType.CONTROLLER, FileType.API_CONTROLLER]:
                continue

            content = self._read_file(file_info.path)
            if not content:
                continue

            controller_name = file_info.class_names[0] if file_info.class_names else file_info.path.stem
            actions = [
                action for action in self.ENDPOINT_PATTERN.findall(content)
                if action != controller_name
            ]

            for action in actions:
                endpoints.append(
                    {
                        "controller": controller_name,
                        "method": action,
                        "route": f"/{controller_name.replace('Controller', '')}/{action}",
                        "file": file_info.relative_path,
                    }
                )

        return endpoints

    def _analyze_database_hotspots(
        self,
        files: List[FileInfo],
        endpoints: List[dict],
    ) -> Tuple[List[dict], List[dict], List[str], List[str]]:
        """Build controller->service->repo call graph and flag multi-touch DB endpoints."""
        class_to_file: Dict[str, FileInfo] = {}
        class_to_content: Dict[str, str] = {}
        method_bodies: Dict[Tuple[str, str], str] = {}
        member_types: Dict[str, Dict[str, str]] = {}
        method_calls: Dict[Tuple[str, str], List[Tuple[str, str]]] = {}
        method_db_touches: Dict[Tuple[str, str], int] = {}

        all_stored_procs: Set[str] = set()
        all_sql_fragments: Set[str] = set()

        for file_info in files:
            if file_info.path.suffix != ".cs":
                continue

            content = self._read_file(file_info.path)
            if not content:
                continue

            class_name = file_info.class_names[0] if file_info.class_names else file_info.path.stem
            class_to_file[class_name] = file_info
            class_to_content[class_name] = content

            stored_procs, sql_fragments = self._extract_sql_artifacts(content)
            all_stored_procs.update(stored_procs)
            all_sql_fragments.update(sql_fragments)

        interface_map = self._build_interface_map(class_to_file)

        for class_name, content in class_to_content.items():
            member_types[class_name] = self._extract_member_types(content, interface_map)
            extracted_methods = self._extract_method_bodies(content)
            for method_name, body in extracted_methods.items():
                key = (class_name, method_name)
                method_bodies[key] = body
                method_db_touches[key] = self._count_db_touches(body)
                method_calls[key] = self._extract_member_calls(
                    body,
                    member_types[class_name],
                    interface_map,
                )

        db_call_graph: List[dict] = []
        hotspots: List[dict] = []

        for endpoint in endpoints:
            controller = endpoint.get("controller", "")
            action = endpoint.get("method", "")
            endpoint_name = f"{controller}.{action}"

            chains: List[str] = []
            services: Set[str] = set()
            repositories: Set[str] = set()

            total_db_touches = method_db_touches.get((controller, action), 0)
            direct_calls = method_calls.get((controller, action), [])

            for target_class, target_method in direct_calls:
                target_file = class_to_file.get(target_class)
                target_type = target_file.file_type if target_file else FileType.UNKNOWN

                if self._is_service(target_class, target_type):
                    services.add(target_class)
                    total_db_touches += method_db_touches.get((target_class, target_method), 0)
                    repo_links = method_calls.get((target_class, target_method), [])

                    found_repo = False
                    for repo_class, repo_method in repo_links:
                        repo_file = class_to_file.get(repo_class)
                        repo_type = repo_file.file_type if repo_file else FileType.UNKNOWN
                        if self._is_repository(repo_class, repo_type):
                            found_repo = True
                            repositories.add(repo_class)
                            total_db_touches += method_db_touches.get((repo_class, repo_method), 0)
                            chains.append(
                                f"{controller}.{action} -> {target_class}.{target_method} -> {repo_class}.{repo_method}"
                            )

                    if not found_repo:
                        chains.append(f"{controller}.{action} -> {target_class}.{target_method}")

                elif self._is_repository(target_class, target_type):
                    repositories.add(target_class)
                    total_db_touches += method_db_touches.get((target_class, target_method), 0)
                    chains.append(f"{controller}.{action} -> {target_class}.{target_method}")

            if not chains:
                chains.append(f"{endpoint_name} (no downstream service/repository call inferred)")

            entry = {
                "endpoint": endpoint_name,
                "route": endpoint.get("route", "-"),
                "db_touches": total_db_touches,
                "services": sorted(services),
                "repositories": sorted(repositories),
                "chains": chains,
            }
            db_call_graph.append(entry)

            if total_db_touches > 1:
                hotspots.append(entry)

        return (
            db_call_graph,
            hotspots,
            sorted(all_stored_procs),
            sorted(all_sql_fragments),
        )

    def _extract_method_bodies(self, content: str) -> Dict[str, str]:
        """Extract method names and bodies using brace matching."""
        methods: Dict[str, str] = {}

        for match in self.METHOD_PATTERN.finditer(content):
            method_name = match.group(1)
            body_start = match.end() - 1
            body_end = self._find_matching_brace(content, body_start)
            if body_end <= body_start:
                continue
            methods[method_name] = content[body_start + 1:body_end]

        return methods

    def _find_matching_brace(self, content: str, start_index: int) -> int:
        """Find matching closing brace index for an opening brace."""
        depth = 0
        for index in range(start_index, len(content)):
            if content[index] == "{":
                depth += 1
            elif content[index] == "}":
                depth -= 1
                if depth == 0:
                    return index
        return -1

    def _extract_member_types(self, content: str, interface_map: Dict[str, str]) -> Dict[str, str]:
        """Extract field member->type map, resolving interfaces to likely concrete classes."""
        members: Dict[str, str] = {}

        for field_type, field_name in self.FIELD_PATTERN.findall(content):
            normalized = self._normalize_type_name(field_type)
            members[field_name] = interface_map.get(normalized, normalized)

        return members

    def _extract_member_calls(
        self,
        body: str,
        members: Dict[str, str],
        interface_map: Dict[str, str],
    ) -> List[Tuple[str, str]]:
        """Extract calls like _service.DoWork() and resolve to target class names."""
        calls: List[Tuple[str, str]] = []

        for member_name, method_name in self.MEMBER_CALL_PATTERN.findall(body):
            member_type = members.get(member_name)
            if not member_type:
                continue
            target_class = interface_map.get(member_type, member_type)
            calls.append((target_class, method_name))

        return calls

    def _count_db_touches(self, code: str) -> int:
        """Count likely DB operations in a method body."""
        return sum(len(re.findall(pattern, code, re.IGNORECASE)) for pattern in self.DB_TOUCH_PATTERNS)

    def _build_interface_map(self, class_to_file: Dict[str, FileInfo]) -> Dict[str, str]:
        """Build a light interface->implementation map (e.g., IUserService -> UserService)."""
        interface_map: Dict[str, str] = {}

        for class_name in class_to_file.keys():
            interface_map[f"I{class_name}"] = class_name

        return interface_map

    def _normalize_type_name(self, type_name: str) -> str:
        """Normalize type names by removing nullable, generic and namespace wrappers."""
        cleaned = type_name.replace("?", "").strip()
        if "<" in cleaned:
            cleaned = cleaned.split("<", 1)[0]
        if "." in cleaned:
            cleaned = cleaned.split(".")[-1]
        return cleaned

    def _is_service(self, class_name: str, file_type: FileType) -> bool:
        """Heuristic service detection."""
        return file_type == FileType.SERVICE or class_name.endswith("Service")

    def _is_repository(self, class_name: str, file_type: FileType) -> bool:
        """Heuristic repository detection."""
        return file_type == FileType.REPOSITORY or class_name.endswith("Repository")

    def _extract_sql_artifacts(self, content: str) -> Tuple[Set[str], Set[str]]:
        """Extract stored procedure names and SQL fragments from string literals and ADO.NET patterns."""
        stored_procs: Set[str] = set()
        sql_fragments: Set[str] = set()

        for literal in self.SQL_STRING_PATTERN.findall(content):
            text = self._decode_csharp_string_literal(literal)
            compact = re.sub(r"\s+", " ", text).strip()

            if not compact:
                continue

            if self.SQL_FRAGMENT_PATTERN.search(compact):
                sql_fragments.add(compact[:180])

            for match in self.SP_EXEC_PATTERN.finditer(compact):
                raw_name = match.group(1).split(".")[-1].replace("[", "").replace("]", "")
                if raw_name:
                    stored_procs.add(raw_name)

        if re.search(r"CommandType\.StoredProcedure", content, re.IGNORECASE):
            for command_text in self.COMMAND_TEXT_PATTERN.findall(content):
                cleaned = command_text.split(".")[-1].replace("[", "").replace("]", "").strip()
                if cleaned:
                    stored_procs.add(cleaned)

        return stored_procs, sql_fragments

    def _decode_csharp_string_literal(self, literal: str) -> str:
        """Decode a basic C# string/verbatim string literal into raw text."""
        text = literal

        prefix = ""
        while text and text[0] in ("@", "$"):
            prefix += text[0]
            text = text[1:]

        if len(text) < 2 or text[0] != '"' or text[-1] != '"':
            return ""

        body = text[1:-1]

        if "@" in prefix:
            return body.replace('""', '"')

        return body.replace(r'\"', '"').replace(r"\n", "\n").replace(r"\t", "\t")

    def _read_file(self, file_path: Path) -> str:
        """Read file content safely."""
        try:
            return file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Legacy .NET Auditor - Analyze .NET applications for modernization opportunities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/dotnet/project
  %(prog)s /path/to/project -o custom-report.md
  %(prog)s . --output reports/my-audit.md
  %(prog)s . --database-hotspot-mode
        """,
    )

    parser.add_argument(
        "project_path",
        help="Path to the .NET project root directory",
    )

    parser.add_argument(
        "-o",
        "--output",
        default="reports/audit.md",
        help="Output path for the audit report (default: reports/audit.md)",
    )

    parser.add_argument(
        "--database-hotspot-mode",
        action="store_true",
        help=(
            "Enable best-effort DB hotspot analysis: controller->service->repository call graph, "
            "multi-touch endpoint flags, and stored procedure/SQL fragment extraction"
        ),
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="Legacy .NET Auditor 1.0.0",
    )

    args = parser.parse_args()

    project_path = Path(args.project_path)
    if not project_path.exists():
        print(f"❌ Error: Project path does not exist: {args.project_path}", file=sys.stderr)
        sys.exit(1)

    if not project_path.is_dir():
        print(f"❌ Error: Project path is not a directory: {args.project_path}", file=sys.stderr)
        sys.exit(1)

    try:
        auditor = LegacyDotNetAuditor(
            args.project_path,
            args.output,
            database_hotspot_mode=args.database_hotspot_mode,
        )
        report_path = auditor.run()
        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n⚠️  Audit cancelled by user")
        sys.exit(130)

    except Exception as e:
        print(f"\n❌ Error during audit: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
