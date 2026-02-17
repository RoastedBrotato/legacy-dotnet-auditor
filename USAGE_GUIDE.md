# Legacy App Auditor - Usage Guide

## Quick Start

### 1. Run the Auditor

```bash
python3 run_auditor.py /path/to/your/dotnet/project
```

### 2. View the Report

The report will be generated at `reports/audit.md` by default. You can view it with any Markdown reader or text editor.

```bash
# View in terminal
cat reports/audit.md

# Or open in your editor
code reports/audit.md  # VS Code
vim reports/audit.md   # Vim
```

### 3. Custom Output Location

```bash
python3 run_auditor.py /path/to/project -o custom/path/report.md
```

## Understanding the Report

### Report Sections Explained

#### 1. Executive Summary
- **Overall Status**: Quick health indicator
- **Issue Counts**: Total, Critical, and High priority issues
- **File Statistics**: Breakdown by file type

#### 2. File Structure Summary
Shows distribution of:
- Controllers
- API Controllers
- Services
- Repositories
- Models

#### 3. Endpoint Map
Lists all detected API endpoints with:
- Controller name
- Method name
- Route path

#### 4. Performance Risk Summary
Grouped issues by type:
- **DuplicatePattern**: Code duplication across files
- **SynchronousBlocking**: `.Result` or `.Wait()` calls
- **SequentialHttpCalls**: HTTP calls that could be parallelized
- **DatabaseInLoop**: DB operations inside loops
- **NPlusOneQuery**: Potential N+1 query patterns

#### 5. Async/Await Opportunities
Files that:
- Use I/O operations without async
- Could benefit from async/await patterns
- Have database operations that should be async

#### 6. SignalR Opportunities
Areas with:
- Polling loops
- Timers for status checking
- Real-time requirements

#### 7. Background Queue Opportunities
Operations that should be queued:
- Email sending
- Report generation
- File processing
- Long-running tasks

#### 8. Modernization Roadmap
Phased approach to improvements:
- **Phase 1**: Critical fixes (immediate)
- **Phase 2**: Performance optimization (2-4 weeks)
- **Phase 3**: Architecture modernization (1-2 months)
- **Phase 4**: Platform migration (3-6 months)

#### 9. Detailed Issues
Full details for each issue:
- File path and line number
- Severity level
- Code snippet
- Description
- Recommendation

## Issue Severity Guide

### 🔴 Critical
**Fix immediately** - These cause serious performance or reliability issues:
- Synchronous blocking calls (`.Result`, `.Wait()`)
- Database operations in loops
- N+1 query patterns

**Impact**: Thread starvation, deadlocks, slow response times

### 🟡 High
**Fix soon** - These significantly impact performance:
- Large files (>300 lines)
- Sequential HTTP calls
- Missing async in I/O operations

**Impact**: Poor performance, maintainability issues

### 🟠 Medium
**Plan to fix** - These should be addressed:
- Duplicate code patterns
- Missing error handling

**Impact**: Technical debt, harder maintenance

### 🔵 Low
**Nice to have** - Improvements:
- Code style issues
- Minor refactoring opportunities

**Impact**: Code quality improvements

## Common Issues and Solutions

### Issue: Synchronous Blocking

**Problem:**
```csharp
var users = GetUsersAsync().Result;  // BAD
```

**Solution:**
```csharp
var users = await GetUsersAsync();   // GOOD
// And make the method async:
public async Task<ActionResult> Index()
```

### Issue: Database in Loop

**Problem:**
```csharp
foreach (var user in users)
{
    var orders = _repo.GetOrders(user.Id);  // BAD: N+1 query
}
```

**Solution:**
```csharp
// Use eager loading
var users = _context.Users
    .Include(u => u.Orders)
    .ToList();

// Or batch load
var userIds = users.Select(u => u.Id).ToList();
var orders = _repo.GetOrdersByUserIds(userIds);
```

### Issue: Sequential HTTP Calls

**Problem:**
```csharp
var result1 = await client.GetAsync(url1);  // BAD: Sequential
var result2 = await client.GetAsync(url2);
var result3 = await client.GetAsync(url3);
```

**Solution:**
```csharp
// Parallel execution
var task1 = client.GetAsync(url1);
var task2 = client.GetAsync(url2);
var task3 = client.GetAsync(url3);
await Task.WhenAll(task1, task2, task3);
```

### Issue: Large Controller

**Problem:**
```csharp
public class UserController : Controller
{
    // 500+ lines of code  // BAD
}
```

**Solution:**
1. Extract business logic to services
2. Move data access to repositories
3. Split into multiple controllers if needed
4. Follow Single Responsibility Principle

## Example Workflow

### 1. Run Initial Audit

```bash
python3 run_auditor.py ~/projects/MyLegacyApp
```

### 2. Review Critical Issues

Open `reports/audit.md` and focus on 🔴 Critical section.

### 3. Fix Issues

Address issues starting from highest severity:
1. Fix `.Result` and `.Wait()` calls
2. Fix database operations in loops
3. Add async/await to I/O operations

### 4. Re-run Audit

```bash
python3 run_auditor.py ~/projects/MyLegacyApp -o reports/audit-after-fixes.md
```

### 5. Compare Results

Check if issue count decreased.

### 6. Repeat

Continue with High priority issues, then Medium.

## Advanced Usage

### Scan Specific Subdirectory

```bash
python3 run_auditor.py ~/projects/MyApp/src/WebAPI
```

### Multiple Projects

```bash
# Audit multiple projects
for project in ~/projects/*/; do
    python3 run_auditor.py "$project" -o "reports/$(basename $project).md"
done
```

### CI/CD Integration

```bash
#!/bin/bash
# audit.sh - Run auditor in CI/CD

python3 run_auditor.py $PROJECT_PATH -o audit-report.md

# Check for critical issues
CRITICAL_COUNT=$(grep -c "🔴 Critical" audit-report.md)

if [ $CRITICAL_COUNT -gt 0 ]; then
    echo "Found $CRITICAL_COUNT critical issues!"
    exit 1
fi
```

## Limitations to Note

1. **False Positives**: Some patterns may be flagged incorrectly
   - Review recommendations carefully
   - Use judgment based on your context

2. **False Negatives**: Some issues may not be detected
   - Heuristic-based detection
   - Complex patterns may be missed

3. **Context Matters**:
   - A large file might be justified in some cases
   - Some synchronous calls might be intentional

4. **Static Analysis Only**:
   - Doesn't execute code
   - Can't measure runtime performance
   - Use profiling tools for runtime analysis

## Best Practices

1. **Run regularly**: Include in your development workflow
2. **Track progress**: Keep reports to compare over time
3. **Prioritize**: Focus on Critical and High issues first
4. **Verify**: Always review code before making changes
5. **Test**: Run tests after fixing issues
6. **Document**: Note why certain warnings are ignored

## Troubleshooting

### No Files Found

**Problem**: "Found 0 files"

**Solutions**:
- Check the path is correct
- Ensure `.cs` files exist in the directory
- Check permissions

### Import Errors

**Problem**: "ImportError" or "ModuleNotFoundError"

**Solutions**:
- Use `run_auditor.py` instead of running `src/main.py` directly
- Ensure Python 3.7+ is installed

### Out of Memory

**Problem**: Process killed or out of memory

**Solutions**:
- Scan subdirectories instead of entire solution
- Exclude `bin`, `obj`, `packages` (already excluded by default)
- Process in batches

## Getting Help

- Check the README.md for general information
- Review example report in `reports/audit.md`
- Create an issue on GitHub for bugs or questions

## Next Steps

After reviewing the audit report:

1. **Create tickets** for high-priority issues
2. **Estimate effort** for each fix
3. **Plan sprints** following the roadmap
4. **Track progress** by re-running audits
5. **Celebrate wins** as issue count decreases!

---

Happy auditing! 🚀
