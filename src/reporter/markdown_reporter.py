"""
Markdown Reporter Module
Generates structured Markdown audit reports.
"""

from datetime import datetime
import re
from typing import List, Dict, Tuple
from pathlib import Path
from models.data_models import AuditReport, AnalysisResult, FileType, IssueSeverity, IssueType


class MarkdownReporter:
    """Generates Markdown audit reports"""

    def __init__(self, output_path: str = "reports/audit.md"):
        """
        Initialize the reporter.

        Args:
            output_path: Path where the report will be saved
        """
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def generate(self, audit_report: AuditReport) -> str:
        """
        Generate a complete audit report.

        Args:
            audit_report: AuditReport object with all analysis data

        Returns:
            Path to the generated report file
        """
        sections = []

        # Header
        sections.append(self._generate_header(audit_report))

        # Executive Summary
        sections.append(self._generate_executive_summary(audit_report))

        # File Structure Summary
        sections.append(self._generate_file_structure(audit_report))

        # Architecture Diagrams
        sections.append(self._generate_architecture_diagrams(audit_report))

        # Endpoint Map
        sections.append(self._generate_endpoint_map(audit_report))

        # Database hotspot mode sections
        sections.append(self._generate_database_hotspots(audit_report))
        sections.append(self._generate_sql_review_checklist(audit_report))

        # Performance Risk Table
        sections.append(self._generate_performance_risks(audit_report))

        # Async Opportunities
        sections.append(self._generate_async_opportunities(audit_report))

        # SignalR Opportunities
        sections.append(self._generate_signalr_opportunities(audit_report))

        # Queue Opportunities
        sections.append(self._generate_queue_opportunities(audit_report))

        # Modernization Roadmap
        sections.append(self._generate_roadmap(audit_report))

        # Detailed Issues
        sections.append(self._generate_detailed_issues(audit_report))

        # Write report
        report_content = "\n\n".join(sections)
        self.output_path.write_text(report_content, encoding='utf-8')

        return str(self.output_path)

    def _generate_header(self, audit_report: AuditReport) -> str:
        """Generate report header"""
        return f"""# Legacy .NET Audit Report

**Project:** {audit_report.project_path}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Files Scanned:** {audit_report.total_files}
**Files Analyzed:** {audit_report.analyzed_files}

---"""

    def _generate_executive_summary(self, audit_report: AuditReport) -> str:
        """Generate executive summary"""
        critical = len(audit_report.critical_issues)
        high = len(audit_report.high_issues)
        total = audit_report.total_issues

        severity_badge = "🔴 Critical" if critical > 0 else ("🟡 Warning" if high > 0 else "🟢 Good")

        return f"""## 📊 Executive Summary

**Overall Status:** {severity_badge}

- **Total Issues Found:** {total}
- **Critical Issues:** {critical}
- **High Priority Issues:** {high}
- **Files with Issues:** {len([r for r in audit_report.results if r.has_issues])}

### Quick Stats
- **Controllers:** {audit_report.file_structure.get(FileType.CONTROLLER, 0)} files
- **API Controllers:** {audit_report.file_structure.get(FileType.API_CONTROLLER, 0)} files
- **Services:** {audit_report.file_structure.get(FileType.SERVICE, 0)} files
- **Repositories:** {audit_report.file_structure.get(FileType.REPOSITORY, 0)} files
"""

    def _generate_file_structure(self, audit_report: AuditReport) -> str:
        """Generate file structure summary"""
        lines = ["## 📁 File Structure Summary", ""]
        lines.append("| File Type | Count |")
        lines.append("|-----------|-------|")

        for file_type, count in sorted(audit_report.file_structure.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                lines.append(f"| {file_type.value} | {count} |")

        return "\n".join(lines)

    def _generate_endpoint_map(self, audit_report: AuditReport) -> str:
        """Generate endpoint map"""
        lines = ["## 🌐 Endpoint Map", ""]

        if not audit_report.endpoints:
            lines.append("_No endpoints detected_")
            return "\n".join(lines)

        lines.append("| Controller | Method | Route/Action |")
        lines.append("|------------|--------|--------------|")

        for endpoint in audit_report.endpoints:
            controller = endpoint.get('controller', 'Unknown')
            method = endpoint.get('method', '-')
            route = endpoint.get('route', '-')
            lines.append(f"| {controller} | {method} | {route} |")

        return "\n".join(lines)

    def _generate_architecture_diagrams(self, audit_report: AuditReport) -> str:
        """Generate Mermaid architecture diagrams based on inferred system structure."""
        lines = ["## 🧭 Architecture Diagrams", ""]
        lines.append("These diagrams are inferred from file classification and class references.")
        lines.append("")

        lines.extend(self._generate_layer_overview_diagram(audit_report))
        lines.append("")
        lines.extend(self._generate_dependency_diagram(audit_report))

        return "\n".join(lines)

    def _generate_database_hotspots(self, audit_report: AuditReport) -> str:
        """Generate best-effort controller->service->repository DB call graph and hotspots."""
        lines = ["## 🧪 Database Hotspot Mode", ""]

        if not audit_report.database_hotspot_mode:
            lines.append("_Disabled (run with `--database-hotspot-mode` to enable)_")
            return "\n".join(lines)

        call_graph = audit_report.db_call_graph or []
        hotspots = audit_report.db_hotspot_endpoints or []

        lines.append(f"- Endpoint call paths analyzed: **{len(call_graph)}**")
        lines.append(f"- Endpoints with multiple DB touches: **{len(hotspots)}**")
        lines.append("")

        if hotspots:
            lines.append("### Endpoints With Multiple DB Touches")
            lines.append("")
            lines.append("| Endpoint | Route | DB Touches |")
            lines.append("|----------|-------|------------|")
            for hotspot in sorted(hotspots, key=lambda item: item.get("db_touches", 0), reverse=True)[:20]:
                lines.append(
                    f"| {hotspot.get('endpoint', '-')} | {hotspot.get('route', '-')} | {hotspot.get('db_touches', 0)} |"
                )
            lines.append("")
        else:
            lines.append("✅ No endpoints exceeded one inferred DB touch.")
            lines.append("")

        lines.append("### Inferred Call Graph (controller -> service -> repository)")
        lines.append("")
        if not call_graph:
            lines.append("_No endpoint call graph data available._")
            return "\n".join(lines)

        for entry in call_graph[:30]:
            lines.append(f"- **{entry.get('endpoint', '-')}** ({entry.get('db_touches', 0)} DB touches)")
            for chain in entry.get("chains", [])[:3]:
                lines.append(f"  - `{chain}`")
            extra = len(entry.get("chains", [])) - 3
            if extra > 0:
                lines.append(f"  - _... {extra} more inferred paths_")

        return "\n".join(lines)

    def _generate_sql_review_checklist(self, audit_report: AuditReport) -> str:
        """Generate stored procedure and SQL fragment review checklist."""
        lines = ["## 🧾 Stored Procedures & Join Review Checklist", ""]

        if not audit_report.database_hotspot_mode:
            lines.append("_Disabled (run with `--database-hotspot-mode` to enable)_")
            return "\n".join(lines)

        stored_procedures = audit_report.stored_procedures or []
        sql_fragments = audit_report.sql_fragments or []

        lines.append("### Checklist")
        lines.append("- [ ] Validate all stored procedure result cardinality assumptions")
        lines.append("- [ ] Confirm every SQL join has indexed predicates on join/filter columns")
        lines.append("- [ ] Review execution plans for the listed SQL fragments")
        lines.append("- [ ] Verify SQL uses parameterization for user inputs")
        lines.append("- [ ] Ensure SP/SQL calls include timeout and error handling strategy")
        lines.append("")

        lines.append("### Referenced Stored Procedures")
        lines.append("")
        if stored_procedures:
            for sp in stored_procedures[:50]:
                lines.append(f"- `{sp}`")
        else:
            lines.append("_No stored procedure references detected_")

        lines.append("")
        lines.append("### SQL Fragments Found")
        lines.append("")
        if sql_fragments:
            for fragment in sql_fragments[:50]:
                lines.append(f"- `{fragment}`")
        else:
            lines.append("_No SQL fragments detected_")

        return "\n".join(lines)

    def _generate_layer_overview_diagram(self, audit_report: AuditReport) -> List[str]:
        """Generate high-level layer overview diagram."""
        controllers = audit_report.file_structure.get(FileType.CONTROLLER, 0)
        api_controllers = audit_report.file_structure.get(FileType.API_CONTROLLER, 0)
        services = audit_report.file_structure.get(FileType.SERVICE, 0)
        repositories = audit_report.file_structure.get(FileType.REPOSITORY, 0)
        models = audit_report.file_structure.get(FileType.MODEL, 0)
        views = audit_report.file_structure.get(FileType.VIEW, 0)

        return [
            "### Layer Overview",
            "",
            "```mermaid",
            "flowchart LR",
            f'  UI["Controllers/API ({controllers + api_controllers})"]',
            f'  VIEW["Views ({views})"]',
            f'  SVC["Services ({services})"]',
            f'  REPO["Repositories ({repositories})"]',
            f'  MODEL["Models ({models})"]',
            '  DATA[("Data Store")]',
            "",
            "  UI --> SVC",
            "  SVC --> REPO",
            "  REPO --> DATA",
            "  UI -.uses.-> MODEL",
            "  SVC -.uses.-> MODEL",
            "  VIEW -.binds.-> MODEL",
            "  UI --> VIEW",
            "```",
        ]

    def _generate_dependency_diagram(self, audit_report: AuditReport) -> List[str]:
        """Generate inferred cross-class dependency diagram."""
        max_nodes = 24
        max_edges = 40

        relevant_results = [
            r for r in audit_report.results
            if r.file_info.file_type in {
                FileType.CONTROLLER,
                FileType.API_CONTROLLER,
                FileType.SERVICE,
                FileType.REPOSITORY,
                FileType.MODEL,
            }
        ]

        class_to_info: Dict[str, Tuple[FileType, str, Path]] = {}
        for result in relevant_results:
            file_info = result.file_info
            class_name = file_info.class_names[0] if file_info.class_names else file_info.path.stem
            class_to_info[class_name] = (file_info.file_type, file_info.relative_path, file_info.path)

        if not class_to_info:
            return ["### Inferred Class Dependencies", "", "_Insufficient data to infer dependencies._"]

        sorted_class_names = sorted(class_to_info.keys())[:max_nodes]
        allowed_names = set(sorted_class_names)
        edges = set()

        for class_name in sorted_class_names:
            _, _, file_path = class_to_info[class_name]
            content = self._read_file(file_path)
            if not content:
                continue

            for target_name in sorted_class_names:
                if class_name == target_name:
                    continue

                if re.search(rf"\b{re.escape(target_name)}\b", content):
                    source_type = class_to_info[class_name][0]
                    target_type = class_to_info[target_name][0]

                    if source_type == FileType.MODEL and target_type == FileType.MODEL:
                        continue

                    edges.add((class_name, target_name))
                    if len(edges) >= max_edges:
                        break

            if len(edges) >= max_edges:
                break

        if not edges:
            return ["### Inferred Class Dependencies", "", "_No cross-class dependencies inferred._"]

        lines = [
            "### Inferred Class Dependencies",
            "",
            "```mermaid",
            "flowchart TD",
        ]

        for class_name in sorted(allowed_names):
            file_type = class_to_info[class_name][0]
            node_id = self._to_mermaid_id(class_name)
            lines.append(f'  {node_id}["{class_name} ({file_type.value})"]')

        lines.append("")
        for source, target in sorted(edges):
            source_id = self._to_mermaid_id(source)
            target_id = self._to_mermaid_id(target)
            lines.append(f"  {source_id} --> {target_id}")

        lines.append("```")
        lines.append("")
        lines.append("_Dependency edges are heuristic and intended for architecture exploration, not strict compile-time truth._")

        return lines

    def _read_file(self, file_path: Path) -> str:
        """Safely read a file for architecture inference."""
        try:
            return file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return ""

    def _to_mermaid_id(self, value: str) -> str:
        """Create Mermaid-safe node IDs."""
        normalized = re.sub(r'[^A-Za-z0-9_]', '_', value)
        if normalized and normalized[0].isdigit():
            normalized = f"N_{normalized}"
        return normalized or "UnknownNode"

    def _generate_performance_risks(self, audit_report: AuditReport) -> str:
        """Generate performance risk table"""
        lines = ["## ⚠️ Performance Risk Summary", ""]

        # Group issues by type
        issues_by_type: Dict[IssueType, int] = {}
        for issue in audit_report.all_issues:
            issues_by_type[issue.issue_type] = issues_by_type.get(issue.issue_type, 0) + 1

        if not issues_by_type:
            lines.append("✅ **No major performance risks detected!**")
            return "\n".join(lines)

        lines.append("| Issue Type | Count | Severity |")
        lines.append("|------------|-------|----------|")

        # Sort by count
        for issue_type, count in sorted(issues_by_type.items(), key=lambda x: x[1], reverse=True):
            # Get typical severity for this issue type
            severity = self._get_typical_severity(audit_report, issue_type)
            severity_icon = self._get_severity_icon(severity)
            lines.append(f"| {issue_type.value} | {count} | {severity_icon} {severity.value} |")

        return "\n".join(lines)

    def _generate_async_opportunities(self, audit_report: AuditReport) -> str:
        """Generate async/await opportunities section"""
        lines = ["## 🚀 Async/Await Opportunities", ""]

        opportunities = []
        for result in audit_report.results:
            opportunities.extend(result.async_opportunities)

        if not opportunities:
            lines.append("✅ **Async patterns are well utilized or not applicable**")
            return "\n".join(lines)

        lines.append(f"Found **{len(opportunities)}** opportunities to introduce async/await:")
        lines.append("")
        for opp in opportunities[:10]:  # Show first 10
            lines.append(f"- {opp}")

        if len(opportunities) > 10:
            lines.append(f"\n_... and {len(opportunities) - 10} more_")

        return "\n".join(lines)

    def _generate_signalr_opportunities(self, audit_report: AuditReport) -> str:
        """Generate SignalR opportunities section"""
        lines = ["## 📡 Real-time (SignalR) Opportunities", ""]

        opportunities = []
        for result in audit_report.results:
            opportunities.extend(result.signalr_opportunities)

        if not opportunities:
            lines.append("_No obvious real-time patterns detected_")
            return "\n".join(lines)

        lines.append(f"Found **{len(opportunities)}** potential real-time use cases:")
        lines.append("")
        lines.append("These areas use polling or timers and could benefit from SignalR:")
        lines.append("")

        for opp in opportunities[:10]:
            lines.append(f"- {opp}")

        if len(opportunities) > 10:
            lines.append(f"\n_... and {len(opportunities) - 10} more_")

        return "\n".join(lines)

    def _generate_queue_opportunities(self, audit_report: AuditReport) -> str:
        """Generate background queue opportunities"""
        lines = ["## 🔄 Background Queue Opportunities", ""]
        lines.append("Consider using message queues (RabbitMQ, Azure Queue, Hangfire) for:")
        lines.append("")

        # Look for long-running operations in issues
        queue_candidates = set()
        for result in audit_report.results:
            for issue in result.issues:
                if any(keyword in issue.description.lower() for keyword in
                       ['email', 'notification', 'report', 'export', 'import', 'background']):
                    queue_candidates.add(result.file_info.relative_path)

        if queue_candidates:
            for candidate in sorted(queue_candidates)[:10]:
                lines.append(f"- {candidate}")
        else:
            lines.append("_No obvious background job candidates detected_")

        return "\n".join(lines)

    def _generate_roadmap(self, audit_report: AuditReport) -> str:
        """Generate modernization roadmap"""
        critical = len(audit_report.critical_issues)
        high = len(audit_report.high_issues)

        return f"""## 🗺️ Recommended Modernization Roadmap

### Phase 1: Critical Fixes (Immediate)
**Priority:** 🔴 Critical
**Timeline:** 1-2 weeks

{self._format_roadmap_items([
    "Fix all synchronous blocking calls (.Result, .Wait())",
    "Eliminate database operations inside loops",
    "Address N+1 query problems",
], critical)}

### Phase 2: Performance Optimization
**Priority:** 🟡 High
**Timeline:** 2-4 weeks

{self._format_roadmap_items([
    "Refactor large controllers (>300 lines)",
    "Implement async/await throughout I/O operations",
    "Parallelize independent HTTP calls with Task.WhenAll()",
], high)}

### Phase 3: Architecture Modernization
**Priority:** 🟢 Medium
**Timeline:** 1-2 months

{self._format_roadmap_items([
    "Introduce SignalR for real-time features",
    "Implement background job processing (Hangfire/Azure Functions)",
    "Consolidate duplicate repository patterns",
    "Apply CQRS pattern where appropriate",
], len(audit_report.all_issues))}

### Phase 4: Platform Migration
**Priority:** 🔵 Future
**Timeline:** 3-6 months

{self._format_roadmap_items([
    "Migrate to .NET 8/9",
    "Adopt minimal APIs for new endpoints",
    "Implement containerization (Docker)",
    "Set up CI/CD pipeline improvements",
], 0)}
"""

    def _format_roadmap_items(self, items: List[str], issue_count: int) -> str:
        """Format roadmap items with issue count"""
        lines = []
        if issue_count > 0:
            lines.append(f"**{issue_count} issues to address:**\n")
        for item in items:
            lines.append(f"- [ ] {item}")
        return "\n".join(lines)

    def _generate_detailed_issues(self, audit_report: AuditReport) -> str:
        """Generate detailed issues section"""
        lines = ["## 📋 Detailed Issues", ""]

        # Group by severity
        critical = audit_report.critical_issues
        high = audit_report.high_issues

        if critical:
            lines.append("### 🔴 Critical Issues")
            lines.append("")
            for issue in critical[:20]:  # Show first 20
                lines.append(self._format_issue(issue))

        if high:
            lines.append("### 🟡 High Priority Issues")
            lines.append("")
            for issue in high[:20]:
                lines.append(self._format_issue(issue))

        if not critical and not high:
            lines.append("✅ **No critical or high priority issues found!**")

        return "\n".join(lines)

    def _format_issue(self, issue) -> str:
        """Format a single issue for the report"""
        lines = [f"#### {issue.issue_type.value} - {issue.file_path}"]

        if issue.line_number > 0:
            lines.append(f"**Location:** Line {issue.line_number}")

        lines.append(f"**Severity:** {self._get_severity_icon(issue.severity)} {issue.severity.value}")
        lines.append(f"**Description:** {issue.description}")

        if issue.code_snippet:
            lines.append("\n**Code:**")
            lines.append("```csharp")
            lines.append(issue.code_snippet)
            lines.append("```")

        if issue.recommendation:
            lines.append(f"\n**Recommendation:** {issue.recommendation}")

        lines.append("\n---\n")
        return "\n".join(lines)

    def _get_severity_icon(self, severity: IssueSeverity) -> str:
        """Get emoji icon for severity level"""
        icons = {
            IssueSeverity.CRITICAL: "🔴",
            IssueSeverity.HIGH: "🟡",
            IssueSeverity.MEDIUM: "🟠",
            IssueSeverity.LOW: "🔵",
            IssueSeverity.INFO: "ℹ️",
        }
        return icons.get(severity, "⚪")

    def _get_typical_severity(self, audit_report: AuditReport, issue_type: IssueType) -> IssueSeverity:
        """Get the typical severity for an issue type"""
        for issue in audit_report.all_issues:
            if issue.issue_type == issue_type:
                return issue.severity
        return IssueSeverity.MEDIUM
