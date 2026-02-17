# Legacy App Auditor

A Python-based static analysis tool for auditing ASP.NET MVC and WebForms applications. Identifies performance issues, anti-patterns, and modernization opportunities.

## Features

🔍 **Comprehensive Analysis**
- Detects large controllers (>300 lines)
- Finds database operations in loops
- Identifies synchronous blocking calls (`.Result`, `.Wait()`)
- Spots sequential HTTP calls that could be parallelized
- Detects N+1 query patterns
- Identifies duplicate repository patterns

📊 **Detailed Reporting**
- File structure summary
- Endpoint mapping
- Performance risk table with severity levels
- Async/await opportunities
- SignalR real-time opportunities
- Background queue candidates
- Modernization roadmap

## Architecture

```
┌─────────────┐
│   Scanner   │  → Recursively finds all .cs files
└──────┬──────┘
       │
┌──────▼──────┐
│ Classifier  │  → Categorizes files (Controller/Service/Repository)
└──────┬──────┘
       │
┌──────▼──────┐
│  Analyzer   │  → Detects anti-patterns & risks
│  (Multiple) │     - Performance Analyzer
│             │     - Async Analyzer
│             │     - Pattern Analyzer
└──────┬──────┘
       │
┌──────▼──────┐
│  Reporter   │  → Generates Markdown audit report
└─────────────┘
```

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd legacy-app-auditor

# No dependencies to install! Uses only Python standard library
```

## Usage

### Basic Usage

```bash
python3 run_auditor.py /path/to/dotnet/project
```

### Custom Output Path

```bash
python3 run_auditor.py /path/to/project -o custom-report.md
```

### Help

```bash
python3 run_auditor.py --help
```

## Example Output

```
🔍 Legacy App Auditor
============================================================
Project: /path/to/MyApp

📂 Step 1/5: Scanning project files...
   Found 127 files
🏷️  Step 2/5: Classifying files...
   Classified 127 files
🔎 Step 3/5: Analyzing code...
   Analyzed 127 files
   Found 23 issues
🌐 Step 4/5: Extracting endpoints...
   Found 45 endpoints
📝 Step 5/5: Generating report...
   Report saved to: reports/audit.md

============================================================
📊 Summary:
   Total Issues: 23
   Critical: 5
   High: 12

✅ Audit complete! Report: reports/audit.md
```

## Report Sections

The generated Markdown report includes:

1. **Executive Summary** - Overall health and quick stats
2. **File Structure** - Breakdown by file type
3. **Endpoint Map** - All controllers and actions
4. **Performance Risks** - Issues grouped by type and severity
5. **Async Opportunities** - Places to introduce async/await
6. **SignalR Opportunities** - Real-time feature candidates
7. **Queue Opportunities** - Background job candidates
8. **Modernization Roadmap** - Phased approach to improvements
9. **Detailed Issues** - Full issue details with code snippets

## Issue Severity Levels

- 🔴 **Critical** - Must fix immediately (e.g., DB in loops, sync blocking)
- 🟡 **High** - Should fix soon (e.g., large files, sequential HTTP)
- 🟠 **Medium** - Plan to fix (e.g., missing async)
- 🔵 **Low** - Nice to have (e.g., duplicate patterns)

## Detected Issues

### Performance Issues
- Large controllers/files (>300 lines)
- Database operations in loops
- N+1 query patterns
- Missing eager loading

### Async/Await Issues
- Synchronous blocking (`.Result`, `.Wait()`)
- Sequential HTTP calls
- Synchronous I/O operations
- Missing async/await

### Pattern Issues
- Duplicate method signatures
- Duplicate repository patterns
- Polling instead of real-time
- Long-running operations in request threads

## Extensibility

The tool is designed for easy extension:

### Add a New Analyzer

1. Create a new analyzer class inheriting from `BaseAnalyzer`
2. Implement the `analyze()` method
3. Register it in `main.py`

```python
from analyzer.base_analyzer import BaseAnalyzer

class MyCustomAnalyzer(BaseAnalyzer):
    def analyze(self, file_info: FileInfo) -> List[PerformanceIssue]:
        # Your analysis logic
        return issues
```

### Add a New Report Format

1. Create a new reporter class
2. Implement the `generate()` method
3. Use it in `main.py`

## Requirements

- Python 3.7+
- No external dependencies

## Project Structure

```
legacy-app-auditor/
├── src/
│   ├── scanner/          # File discovery
│   │   └── file_scanner.py
│   ├── classifier/       # File categorization
│   │   └── file_classifier.py
│   ├── analyzer/         # Anti-pattern detection
│   │   ├── base_analyzer.py
│   │   ├── performance_analyzer.py
│   │   ├── async_analyzer.py
│   │   └── pattern_analyzer.py
│   ├── reporter/         # Report generation
│   │   └── markdown_reporter.py
│   ├── models/           # Data classes
│   │   └── data_models.py
│   └── main.py           # CLI entry point
├── examples/             # Non-product sample .NET apps for auditing
│   ├── demo-project/
│   └── task-audit-demo/
├── reports/              # Output directory
├── tests/                # Python test scaffold (expand with real tests)
├── run_auditor.py        # Wrapper entry point
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## Limitations

- Works with .NET Framework and .NET Core/5+
- Requires source code access (not binary analysis)
- Heuristic-based detection (may have false positives/negatives)
- Does not execute code (static analysis only)

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review example reports

## Roadmap

- [ ] Support for VB.NET
- [ ] Integration with CI/CD pipelines
- [ ] HTML report format
- [ ] JSON export for further processing
- [ ] Configuration file support
- [ ] Custom rule definitions
- [ ] Performance metrics tracking

---

**Built with ❤️ for .NET developers modernizing legacy applications**
