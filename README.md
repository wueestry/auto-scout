# auto-scout

**Auto-Scout** is a powerful, extensible reconnaissance and scanning framework built in Python. It provides a flexible architecture for running security scans with conditional logic, parallel execution, and rich terminal output.

Perfect for CTFs, OSCP prep, and penetration testing workflows.

## Features

- 🚀 **Pure Python Architecture** - Clean, extensible codebase with type hints
- 🔄 **Async/Parallel Execution** - Run multiple scans concurrently for speed
- 🎯 **Conditional Logic** - Scans decide whether to run based on previous results
- 🔌 **Plugin System** - Easily add custom scans by dropping Python files
- 📊 **Rich Visualization** - Beautiful terminal output with progress tracking
- 💾 **Result Persistence** - Save results to JSON for later analysis
- 🧪 **Fully Tested** - Comprehensive pytest test suite
- 📝 **Type Safe** - Full type annotations with mypy checking

## Installation

### Prerequisites

- Python >= 3.12
- nmap (for built-in scans)
- sudo/root access (for some scans)

### Install

```bash
# Clone the repository
git clone https://github.com/yourusername/auto-scout.git
cd auto-scout

# Install the package
pip install -e .

# Install development dependencies (optional)
pip install -e .[dev]
```

## Quick Start

### Basic Usage

```bash
# Run the default pentest workflow on a target
auto-scout 192.168.1.100

# Specify output directory
auto-scout 192.168.1.100 -o /tmp/scan_results

# Enable verbose logging
auto-scout 192.168.1.100 -v

# List all available scans
auto-scout --list-scans
```

### Example Output

```
▄▖  ▗     ▄▖      ▗ 
▌▌▌▌▜▘▛▌▄▖▚ ▛▘▛▌▌▌▜▘
▛▌▙▌▐▖▙▌  ▄▌▙▖▙▌▙▌▐▖

Target: 192.168.1.100
Output Directory: ./output

[Stage 1/3] Quick Port Discovery
✓ Found 5 open ports

[Stage 2/3] Detailed Service Detection  
✓ Identified 5 services

[Stage 3/3] Vulnerability Assessment
✓ Vulnerability scan complete

┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┓
┃ Scan           ┃ Status   ┃ Duration ┃ Details  ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━┩
│ quick_nmap     │ ✓ Success│   12.34s │ 5 ports  │
│ detailed_nmap  │ ✓ Success│   8.76s  │ 5 services│
│ vuln_nmap      │ ✓ Success│   45.12s │           │
└────────────────┴──────────┴──────────┴──────────┘
```

## Architecture

### Core Components

```
auto_scout/
├── core/              # Core framework
│   ├── scan.py        # Base Scan class
│   ├── workflow.py    # Base Workflow class
│   ├── context.py     # ScanContext (state management)
│   ├── result.py      # ScanResult data structure
│   ├── executor.py    # Async scan execution engine
│   ├── registry.py    # Scan plugin registry
│   └── decorators.py  # @register_scan decorator
├── scans/             # Built-in scans
│   └── nmap/          # Nmap scan implementations
├── workflows/         # Built-in workflows
│   └── pentest.py     # Default pentest workflow
├── parsers/           # Output parsers
│   └── nmap.py        # Nmap XML parser
├── cli/               # CLI interface
│   └── main.py        # Entry point
└── utils/             # Utilities
    └── storage.py     # Result persistence
```

### Key Concepts

#### 1. Scans

Scans are the basic building blocks. Each scan:
- Extends the `Scan` base class
- Implements `execute()` to run the scan
- Can implement `can_run()` for conditional logic
- Registers itself with `@register_scan`

#### 2. Workflows

Workflows orchestrate multiple scans:
- Extend the `Workflow` base class
- Define scan execution order in `define()`
- Can run scans sequentially or in parallel
- Have access to shared `ScanContext`

#### 3. Context

The `ScanContext` carries state between scans:
- Target information
- Results from previous scans
- Helper methods like `get_open_ports()`

## Creating Custom Scans

### Simple Example

```python
# user_scans/my_scan.py
from auto_scout.core.scan import Scan
from auto_scout.core.decorators import register_scan
from auto_scout.core.context import ScanContext
from auto_scout.core.result import ScanResult
from datetime import datetime

@register_scan
class MyScan(Scan):
    @property
    def name(self) -> str:
        return "my_custom_scan"
    
    @property
    def description(self) -> str:
        return "My custom security scan"
    
    async def execute(self, ctx: ScanContext) -> ScanResult:
        start_time = datetime.now()
        
        # Your scan logic here
        command = ["your-tool", ctx.target_ip]
        stdout, stderr, returncode = await self._run_command(command)
        
        # Parse results
        parsed_data = {"example": "data"}
        
        return self._create_result(
            success=returncode == 0,
            start_time=start_time,
            end_time=datetime.now(),
            raw_output=stdout,
            parsed_data=parsed_data
        )
```

### Conditional Scan Example

```python
@register_scan
class WebEnumerationScan(Scan):
    @property
    def name(self) -> str:
        return "web_enum"
    
    async def can_run(self, ctx: ScanContext) -> bool:
        """Only run if web ports are open"""
        web_ports = {80, 443, 8080, 8443}
        open_ports = set(ctx.get_open_ports())
        return bool(web_ports & open_ports)
    
    async def execute(self, ctx: ScanContext) -> ScanResult:
        # Enumerate web services
        ...
```

## Creating Custom Workflows

```python
# user_workflows/my_workflow.py
from auto_scout.core.workflow import Workflow
from auto_scout.scans.nmap import QuickNmapScan, DetailedNmapScan

class MyWorkflow(Workflow):
    async def define(self) -> None:
        # Stage 1: Discovery
        await self.execute_scan(QuickNmapScan())
        
        # Stage 2: Conditional detailed scan
        if len(self.context.get_open_ports()) > 10:
            await self.execute_scan(DetailedNmapScan())
        
        # Stage 3: Parallel custom scans
        from user_scans.my_scan import MyScan
        from user_scans.other_scan import OtherScan
        
        await self.execute_parallel([
            MyScan(),
            OtherScan()
        ])
```

## Built-in Scans

### Nmap Scans

#### Quick Nmap Scan
- **Name**: `quick_nmap`
- **Description**: Fast TCP SYN scan of all ports
- **Requires Root**: Yes
- **Timeout**: 10 minutes

#### Detailed Nmap Scan
- **Name**: `detailed_nmap`
- **Description**: Service version detection and OS fingerprinting
- **Requires Root**: Yes
- **Conditional**: Only runs if ports were found
- **Timeout**: 15 minutes

#### Vulnerability Scan
- **Name**: `vuln_nmap`
- **Description**: Nmap vulnerability detection scripts
- **Requires Root**: Yes
- **Conditional**: Only runs if 3+ ports found
- **Timeout**: 30 minutes

## API Reference

### Scan Base Class

```python
class Scan(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier"""
        
    @property
    def description(self) -> str:
        """Human-readable description"""
        
    @property
    def timeout(self) -> int:
        """Timeout in seconds (default: 300)"""
        
    @property
    def requires_root(self) -> bool:
        """Whether scan needs sudo"""
        
    async def can_run(self, ctx: ScanContext) -> bool:
        """Conditional logic"""
        
    @abstractmethod
    async def execute(self, ctx: ScanContext) -> ScanResult:
        """Main scan logic"""
```

### Workflow Base Class

```python
class Workflow(ABC):
    @abstractmethod
    async def define(self) -> None:
        """Define workflow logic"""
        
    async def execute_scan(self, scan: Scan) -> ScanResult:
        """Execute a single scan"""
        
    async def execute_parallel(self, scans: list[Scan]) -> list[ScanResult]:
        """Execute scans in parallel"""
```

### ScanContext

```python
class ScanContext:
    target_ip: str
    output_dir: Path
    results: dict[str, ScanResult]
    metadata: dict[str, Any]
    
    def get_open_ports(self) -> list[int]
    def get_services(self) -> dict[int, str]
    def get_ports_by_service(self, pattern: str) -> list[int]
    def has_open_ports(self) -> bool
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=auto_scout

# Run specific test file
pytest tests/test_context.py
```

### Linting and Formatting

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type check
mypy .
```

### Project Structure for Contributors

```
auto-scout/
├── auto_scout/        # Main package
├── tests/             # Test suite
├── user_scans/        # User custom scans (not in git)
├── user_workflows/    # User custom workflows (not in git)
├── output/            # Default scan output (not in git)
├── pyproject.toml     # Dependencies and config
├── README.md          # This file
└── AGENTS.md          # Development guidelines
```

## Troubleshooting

### Permission Errors

Some scans (like SYN scans) require root:
```bash
sudo auto-scout 192.168.1.100
```

### No Scans Found

Make sure to import or discover scans:
```bash
auto-scout --discover ./user_scans 192.168.1.100
```

### Timeout Issues

Increase scan timeout by modifying the scan class:
```python
@property
def timeout(self) -> int:
    return 1800  # 30 minutes
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Follow the coding standards in `AGENTS.md`
4. Add tests for new features
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built for CTF players and penetration testers
- Inspired by the need for flexible, scriptable reconnaissance
- Uses the amazing [rich](https://github.com/Textualize/rich) library for terminal output

## Support

- 🐛 **Issues**: GitHub Issues
- 💬 **Discussions**: GitHub Discussions
- 📧 **Email**: your@email.com

---

**Happy Hacking! 🎯**
