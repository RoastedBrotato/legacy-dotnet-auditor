#!/usr/bin/env python3
"""
Legacy App Auditor - Main Entry Point
Orchestrates the complete audit pipeline.
"""

import argparse
import sys
from pathlib import Path
from typing import List

from models.data_models import (
    FileInfo, FileType, AnalysisResult, AuditReport,
    PerformanceIssue, IssueSeverity
)
from scanner.file_scanner import FileScanner
from classifier.file_classifier import FileClassifier
from analyzer.performance_analyzer import PerformanceAnalyzer
from analyzer.async_analyzer import AsyncAnalyzer
from analyzer.pattern_analyzer import PatternAnalyzer
from reporter.markdown_reporter import MarkdownReporter


class LegacyAppAuditor:
    """Main auditor orchestrator"""

    def __init__(self, project_path: str, output_path: str = "reports/audit.md"):
        """
        Initialize the auditor.

        Args:
            project_path: Path to the .NET project root
            output_path: Path for the output report
        """
        self.project_path = Path(project_path).resolve()
        self.output_path = output_path

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
        print("🔍 Legacy App Auditor")
        print("=" * 60)
        print(f"Project: {self.project_path}")
        print()

        # Step 1: Scan files
        print("📂 Step 1/5: Scanning project files...")
        files = self.scanner.scan()
        print(f"   Found {len(files)} files")

        # Step 2: Classify files
        print("🏷️  Step 2/5: Classifying files...")
        classified_files = self.classifier.classify_batch(files)
        file_structure = self._build_file_structure(classified_files)
        print(f"   Classified {len(classified_files)} files")

        # Step 3: Analyze files
        print("🔎 Step 3/5: Analyzing code...")
        results = self._analyze_files(classified_files)
        print(f"   Analyzed {len(results)} files")
        print(f"   Found {sum(len(r.issues) for r in results)} issues")

        # Step 4: Extract endpoints
        print("🌐 Step 4/5: Extracting endpoints...")
        endpoints = self._extract_endpoints(classified_files)
        print(f"   Found {len(endpoints)} endpoints")

        # Step 5: Generate report
        print("📝 Step 5/5: Generating report...")
        audit_report = AuditReport(
            project_path=str(self.project_path),
            total_files=len(files),
            analyzed_files=len(results),
            file_structure=file_structure,
            endpoints=endpoints,
            results=results
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

            # Collect issues from all analyzers
            issues = []

            # Performance analysis
            perf_issues = self.performance_analyzer.analyze(file_info)
            issues.extend(perf_issues)

            # Async analysis
            async_issues = self.async_analyzer.analyze(file_info)
            issues.extend(async_issues)

            # Pattern analysis (individual)
            pattern_issues = self.pattern_analyzer.analyze(file_info)
            issues.extend(pattern_issues)

            # Identify opportunities
            async_opportunities = self.async_analyzer.identify_async_opportunities(file_info)
            signalr_opportunities = self.pattern_analyzer.identify_signalr_opportunities(file_info)

            # Create result
            result = AnalysisResult(
                file_info=file_info,
                issues=issues,
                async_opportunities=async_opportunities,
                signalr_opportunities=signalr_opportunities
            )
            results.append(result)

        # Run batch pattern analysis for cross-file duplicates
        batch_issues = self.pattern_analyzer.analyze_batch(files)
        if batch_issues:
            # Add batch issues to the first result (they're cross-file)
            if results:
                results[0].issues.extend(batch_issues)

        print()  # Clear progress line
        return results

    def _extract_endpoints(self, files: List[FileInfo]) -> List[dict]:
        """Extract API endpoints from controllers"""
        endpoints = []

        for file_info in files:
            if file_info.file_type in [FileType.CONTROLLER, FileType.API_CONTROLLER]:
                # Read file content
                try:
                    with open(file_info.path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Extract controller name
                    controller_name = file_info.class_names[0] if file_info.class_names else "Unknown"

                    # Extract action methods (simplified)
                    import re
                    action_pattern = r'public\s+(?:async\s+)?(?:Task<)?(?:ActionResult|IActionResult|IHttpActionResult).*?>\s+(\w+)\s*\('
                    actions = re.findall(action_pattern, content)

                    for action in actions:
                        endpoints.append({
                            'controller': controller_name,
                            'method': action,
                            'route': f"/{controller_name.replace('Controller', '')}/{action}"
                        })

                except Exception:
                    pass

        return endpoints


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Legacy App Auditor - Analyze .NET applications for modernization opportunities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/dotnet/project
  %(prog)s /path/to/project -o custom-report.md
  %(prog)s . --output reports/my-audit.md
        """
    )

    parser.add_argument(
        'project_path',
        help='Path to the .NET project root directory'
    )

    parser.add_argument(
        '-o', '--output',
        default='reports/audit.md',
        help='Output path for the audit report (default: reports/audit.md)'
    )

    parser.add_argument(
        '-v', '--version',
        action='version',
        version='Legacy App Auditor 1.0.0'
    )

    args = parser.parse_args()

    # Validate project path
    project_path = Path(args.project_path)
    if not project_path.exists():
        print(f"❌ Error: Project path does not exist: {args.project_path}", file=sys.stderr)
        sys.exit(1)

    if not project_path.is_dir():
        print(f"❌ Error: Project path is not a directory: {args.project_path}", file=sys.stderr)
        sys.exit(1)

    try:
        # Run audit
        auditor = LegacyAppAuditor(args.project_path, args.output)
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
