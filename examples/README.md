# Examples

This folder contains sample .NET projects used to exercise the auditor.

These are demo inputs only and are not part of the auditor product runtime.

## Included Projects

- `demo-project/`: Minimal legacy sample for quick smoke runs.
- `task-audit-demo/`: End-to-end task workflow sample with dashboard, assignment, status updates, and approvals.

## Run Examples

From the repository root:

```bash
python3 run_auditor.py examples/demo-project -o reports/demo-project-report.md
python3 run_auditor.py examples/task-audit-demo -o reports/task-audit-demo-report.md
```
