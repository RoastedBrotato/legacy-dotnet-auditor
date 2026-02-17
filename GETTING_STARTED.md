# Getting Started with LegacyAppAuditor

## 🚀 Quick Start (3 Steps)

### 1. Prerequisites

Just Python 3.7 or higher. No other dependencies needed!

```bash
python3 --version  # Should be 3.7+
```

### 2. Run the Auditor

```bash
# Navigate to the project directory
cd legacy-app-auditor

# Run on your .NET project
python3 run_auditor.py /path/to/your/dotnet/project
```

### 3. View the Report

```bash
# The report is generated at reports/audit.md
cat reports/audit.md

# Or open in your favorite editor/viewer
```

That's it! 🎉

## 📝 What You'll Get

The audit report includes:

### Executive Summary
- Overall health status (🔴 Critical, 🟡 Warning, or 🟢 Good)
- Total issues count
- Critical and high-priority issue counts
- Project statistics

### Detailed Analysis
1. **File Structure** - Breakdown by type (Controllers, Services, etc.)
2. **Endpoint Map** - All detected API endpoints
3. **Performance Risks** - Issues grouped by type and severity
4. **Async Opportunities** - Where to add async/await
5. **SignalR Opportunities** - Real-time feature candidates
6. **Queue Opportunities** - Background job candidates
7. **Modernization Roadmap** - Phased implementation plan
8. **Detailed Issues** - Full details with code snippets

## 🎯 Example Usage

### Audit a Single Project

```bash
python3 run_auditor.py ~/projects/MyLegacyApp
```

### Custom Output Location

```bash
python3 run_auditor.py ~/projects/MyApp -o ~/reports/my-audit.md
```

### Audit Demo Project (Included)

```bash
python3 run_auditor.py examples/demo-project
cat reports/audit.md
```

### Audit Workflow Demo (Assignment + Status + Approval)

```bash
python3 run_auditor.py examples/task-audit-demo -o reports/task-audit-demo-report.md
cat reports/task-audit-demo-report.md
```

## 📊 Understanding Results

### Severity Levels

- **🔴 Critical** - Fix immediately (e.g., `.Result`, DB in loops)
  - Impact: Thread starvation, deadlocks, performance issues

- **🟡 High** - Fix soon (e.g., large files, sequential HTTP)
  - Impact: Performance degradation, maintainability issues

- **🟠 Medium** - Plan to fix (e.g., duplicate patterns)
  - Impact: Technical debt, harder maintenance

- **🔵 Low** - Nice to have (e.g., code style)
  - Impact: Code quality improvements

### Common Issues Detected

1. **Synchronous Blocking**
   ```csharp
   var result = GetDataAsync().Result;  // ❌ BAD
   var result = await GetDataAsync();   // ✅ GOOD
   ```

2. **Database in Loop**
   ```csharp
   foreach (var user in users) {
       var orders = db.GetOrders(user.Id);  // ❌ BAD
   }

   // Use eager loading
   var users = db.Users.Include(u => u.Orders).ToList();  // ✅ GOOD
   ```

3. **Sequential HTTP Calls**
   ```csharp
   var r1 = await http.GetAsync(url1);  // ❌ BAD
   var r2 = await http.GetAsync(url2);

   // Parallelize
   await Task.WhenAll(
       http.GetAsync(url1),
       http.GetAsync(url2)
   );  // ✅ GOOD
   ```

## 🔧 Next Steps After Running

### 1. Review the Report

Start with the Executive Summary, then dive into Critical issues.

### 2. Prioritize Fixes

Follow this order:
1. Critical issues (🔴)
2. High priority issues (🟡)
3. Medium priority issues (🟠)
4. Low priority issues (🔵)

### 3. Create Action Items

For each issue:
- Create a ticket in your project tracker
- Assign to a team member
- Estimate effort
- Schedule for a sprint

### 4. Track Progress

Re-run the auditor periodically to track improvements:

```bash
# Before fixes
python3 run_auditor.py ~/projects/MyApp -o reports/audit-before.md

# After fixes
python3 run_auditor.py ~/projects/MyApp -o reports/audit-after.md

# Compare
diff reports/audit-before.md reports/audit-after.md
```

## 📚 Additional Resources

- **README.md** - Project overview and features
- **USAGE_GUIDE.md** - Comprehensive usage instructions
- **ARCHITECTURE.md** - Design and implementation details
- **PROJECT_SUMMARY.md** - Complete feature list

## ❓ Troubleshooting

### "No files found"

**Cause**: Path doesn't contain .cs files or is incorrect

**Solution**:
```bash
# Verify path
ls /path/to/project/*.cs

# Try absolute path
python3 run_auditor.py /absolute/path/to/project
```

### "Import errors"

**Cause**: Running main.py directly instead of via wrapper

**Solution**:
```bash
# Don't do this:
python3 src/main.py project-path

# Do this instead:
python3 run_auditor.py project-path
```

### "Permission denied"

**Cause**: No read access to some directories

**Solution**: The tool will skip inaccessible files and continue. This is normal for system directories.

## 💡 Tips

1. **Start Small**: Audit a single module first
2. **Run Regularly**: Include in your development workflow
3. **Share Results**: Discuss with your team
4. **Track Trends**: Keep old reports to see progress
5. **Customize**: Fork and add your own analyzers

## 🎓 Learning Path

### Beginner
1. Run tool on demo project
2. Review generated report
3. Understand severity levels
4. Fix one critical issue

### Intermediate
1. Audit your actual project
2. Prioritize issues by severity
3. Create tickets for top issues
4. Re-run after fixes

### Advanced
1. Add custom analyzers
2. Integrate with CI/CD
3. Create custom report formats
4. Contribute improvements

## 🤝 Getting Help

- Check documentation in this repo
- Review the demo project and its report
- Open an issue on GitHub for bugs
- Read the architecture docs for implementation details

## ✨ Success Tips

1. **Don't fix everything at once** - Start with critical issues
2. **Test after fixes** - Ensure changes don't break functionality
3. **Document decisions** - Note why certain warnings are ignored
4. **Share knowledge** - Teach team about common patterns
5. **Celebrate wins** - Acknowledge when issue counts decrease

---

Ready to modernize your legacy app? Run the auditor now! 🚀

```bash
python3 run_auditor.py /path/to/your/project
```
