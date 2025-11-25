# Specify CLI Test Suite

This test suite documents the behavior of the Python Specify CLI to enable accurate porting to Node.js.

## Test Structure

```
tests/
├── __init__.py           # Package init
├── conftest.py           # Shared fixtures and utilities
├── pytest.ini            # pytest configuration
├── README.md             # This file
├── test_config.py        # Configuration and constants
├── test_github.py        # GitHub API integration
├── test_tools.py         # Tool detection
├── test_template.py      # Template download/extraction
├── test_git.py           # Git operations
├── test_ui.py            # UI components
├── test_commands.py      # CLI commands
└── test_integration.py   # End-to-end tests
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_config.py
```

### Run Specific Test Class
```bash
pytest tests/test_config.py::TestAgentConfig
```

### Run Specific Test
```bash
pytest tests/test_config.py::TestAgentConfig::test_agent_config_has_expected_agents
```

### Run with Verbose Output
```bash
pytest -v
```

### Skip Integration Tests
```bash
pytest -m "not integration"
```

### Skip Network Tests
```bash
pytest -m "not network"
```

### Run Only Fast Tests
```bash
pytest -m "not slow and not integration"
```

## Test Categories

### Unit Tests (Fast, No Network)
- `test_config.py` - Tests configuration constants
- `test_tools.py` - Tests tool detection logic
- `test_ui.py` - Tests UI components

### Mock-Based Tests
- `test_github.py` - Tests GitHub API with mocked responses
- `test_template.py` - Tests template handling with mocked files
- `test_git.py` - Tests Git operations with mocked subprocess

### Integration Tests (Slow, May Need Network)
- `test_integration.py` - End-to-end workflow tests
- `test_commands.py` - Full command execution tests

## Key Behaviors Documented

### 1. AGENT_CONFIG Structure
```python
AGENT_CONFIG = {
    "copilot": {
        "name": "GitHub Copilot",
        "folder": ".github/",
        "install_url": None,
        "requires_cli": False,
    },
    # ... more agents
}
```

### 2. GitHub Token Resolution
Priority order:
1. `--github-token` CLI argument
2. `GH_TOKEN` environment variable
3. `GITHUB_TOKEN` environment variable

### 3. Tool Detection
- Uses `shutil.which()` (equivalent to `which`/`where`)
- Special handling for Claude at `~/.claude/local/claude`

### 4. Template Asset Naming
Pattern: `spec-kit-template-{ai}-{script}-{version}.zip`

### 5. VS Code Settings Merge
`.vscode/settings.json` is deep-merged, not overwritten.

### 6. Script Permissions (Unix)
`.sh` files are made executable with chmod.

## Node.js Equivalents

Each test file includes Node.js/TypeScript equivalents in docstrings.

### Example: Tool Detection

**Python:**
```python
import shutil

def check_tool(tool):
    return shutil.which(tool) is not None
```

**Node.js:**
```typescript
import { execSync } from 'child_process';

function checkTool(tool: string): boolean {
  try {
    const cmd = process.platform === 'win32' ? `where ${tool}` : `which ${tool}`;
    execSync(cmd, { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}
```

## Test Markers

| Marker | Description |
|--------|-------------|
| `@pytest.mark.integration` | Slow integration tests |
| `@pytest.mark.network` | Requires network access |
| `@pytest.mark.slow` | Particularly slow tests |
| `@pytest.mark.windows` | Windows-only tests |
| `@pytest.mark.unix` | Unix-only tests |

## Fixtures

### `temp_dir`
Creates a temporary directory, cleaned up after test.

### `mock_env`
Temporarily modifies environment variables.

### `project_root`
Returns the project root directory.

### `sample_release_response`
Sample GitHub release API response for mocking.

### `sample_rate_limit_headers`
Sample rate limit headers for testing error handling.

## Writing New Tests

### For the Python CLI
```python
def test_my_feature():
    """
    Description of what this tests.
    
    Node.js equivalent:
    ```typescript
    // TypeScript code here
    ```
    """
    # Test implementation
```

### For the Node.js Port (Vitest)
```typescript
import { describe, it, expect } from 'vitest';

describe('MyFeature', () => {
  it('should do something', () => {
    // Test implementation
    expect(result).toBe(expected);
  });
});
```

## Coverage

To run with coverage:
```bash
pytest --cov=specify_cli --cov-report=html
```

View report at `htmlcov/index.html`.

## CI Integration

These tests are designed to run in CI environments:

```yaml
# GitHub Actions example
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.9', '3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e ".[dev]"
      - run: pytest -m "not network"
```

## Troubleshooting

### Import Errors
Ensure the `src` directory is in the Python path:
```bash
pip install -e .
# or
PYTHONPATH=src pytest
```

### Network Tests Failing
Skip with: `pytest -m "not network"`

### Platform-Specific Failures
Tests marked `@pytest.mark.windows` or `@pytest.mark.unix` are automatically skipped on incompatible platforms.
