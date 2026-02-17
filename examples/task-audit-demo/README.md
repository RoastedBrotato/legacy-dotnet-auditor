# Task Audit Demo Project

This sample project is intentionally built in a legacy MVC style so you can test `legacy-app-auditor`.

## Included Features

- Dashboard summary (`DashboardController`, `DashboardViewModel`, and `Views/Dashboard/Index.cshtml`)
- Task assignment (manager assigns task to contributor)
- Task status updates by assignee (`TaskController.UpdateStatus`)
- Task approval/rejection by approver (`ApprovalController`)

## Quick Audit

From the repository root:

```bash
python3 run_auditor.py examples/task-audit-demo -o reports/task-audit-demo-report.md
```
