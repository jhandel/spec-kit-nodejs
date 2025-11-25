# Acceptance Test Suite for Specify CLI Node.js Port

This directory contains comprehensive acceptance tests documenting **ALL behaviors** 
of the Python Specify CLI that must be replicated exactly in the Node.js/TypeScript port.

## Test Categories

| File | Category | Description |
|------|----------|-------------|
| `test_agent_config.py` | CONFIG | AGENT_CONFIG data structure (15 agents, exact values) |
| `test_script_types.py` | CONFIG | SCRIPT_TYPE_CHOICES (sh, ps) |
| `test_claude_path.py` | CONFIG | CLAUDE_LOCAL_PATH special handling |
| `test_banner.py` | UI | ASCII banner and tagline display |
| `test_github_token.py` | TOKEN | Token precedence (CLI > GH_TOKEN > GITHUB_TOKEN) |
| `test_rate_limit_parsing.py` | RATE_LIMIT | GitHub rate limit header parsing |
| `test_rate_limit_error.py` | RATE_LIMIT | Rate limit error message formatting |
| `test_tool_detection.py` | TOOL | CLI tool detection with shutil.which |
| `test_git_operations.py` | GIT | Git repository operations |
| `test_step_tracker.py` | UI | StepTracker progress display component |
| `test_json_merge.py` | TEMPLATE | JSON deep merge for settings.json |
| `test_interactive_selection.py` | UI | Arrow key selection menu |
| `test_init_command.py` | COMMAND | `specify init` command behaviors |
| `test_check_command.py` | COMMAND | `specify check` command behaviors |
| `test_version_command.py` | COMMAND | `specify version` command behaviors |
| `test_template_download.py` | TEMPLATE | GitHub release asset download |
| `test_template_extraction.py` | TEMPLATE | ZIP extraction and directory setup |
| `test_script_permissions.py` | TEMPLATE | Unix script permission setting |
| `test_shell_common.py` | SCRIPT | common.sh/common.ps1 functions |
| `test_shell_create_feature.py` | SCRIPT | create-new-feature.sh behavior |
| `test_shell_check_prereqs.py` | SCRIPT | check-prerequisites.sh behavior |
| `test_shell_setup_plan.py` | SCRIPT | setup-plan.sh behavior |
| `test_shell_update_agent.py` | SCRIPT | update-agent-context.sh behavior |
| `test_template_files.py` | TEMPLATE | Template file structure and placeholders |
| `test_exit_codes.py` | COMMAND | CLI exit codes |
| `test_error_messages.py` | COMMAND | Error message formatting |
| `test_platform_compat.py` | PLATFORM | Cross-platform compatibility |
| `test_tls_handling.py` | NETWORK | TLS/SSL certificate handling |

## Critical Data Structures

### AGENT_CONFIG (16 agents)

```typescript
interface AgentConfig {
  name: string;          // Human-readable display name
  folder: string;        // Directory (starts with '.', ends with '/')
  installUrl: string | null;  // URL for CLI installation (null for IDE-based)
  requiresCli: boolean;  // Whether CLI tool check is needed
}
```

**IDE-based agents** (no CLI check): copilot, cursor-agent, windsurf, kilocode, roo
**CLI-based agents** (requires tool check): claude, gemini, qwen, opencode, codex, auggie, codebuddy, q, amp, shai

### SCRIPT_TYPE_CHOICES

```typescript
const SCRIPT_TYPE_CHOICES: Record<string, string> = {
  sh: "POSIX Shell (bash/zsh)",
  ps: "PowerShell",
};
```

### StepTracker Status Values

```typescript
type StepStatus = "pending" | "running" | "done" | "error" | "skipped";
```

## Key Behaviors to Verify

### 1. GitHub Token Precedence
1. CLI argument (`--github-token`)
2. `GH_TOKEN` environment variable
3. `GITHUB_TOKEN` environment variable
4. None (unauthenticated)

### 2. Claude CLI Special Handling
Check `~/.claude/local/claude` BEFORE `shutil.which('claude')` because `claude migrate-installer` 
removes the original PATH entry.

### 3. Branch Naming Convention
Pattern: `###-feature-name` (3-digit prefix, hyphen, suffix)
- Maximum 244 bytes (GitHub limit)
- Truncate at word boundary
- Remove trailing hyphens

### 4. .vscode/settings.json Merge
- Deep merge existing with template
- Don't overwrite user settings
- Merge nested objects recursively

### 5. Script Permission Setting (Unix only)
- Only process `.sh` files in `.specify/scripts/`
- Only set execute bit if file starts with `#!`
- Add execute for each read permission (r->rx)

## Running Tests

```bash
# Run all acceptance tests
pytest tests/acceptance/ -v

# Run specific category
pytest tests/acceptance/test_agent_config.py -v

# Run with markers
pytest tests/acceptance/ -m "config" -v
```

## Test Philosophy

Each test documents a **specific behavior** that must be replicated:
- Tests are named to describe the exact behavior
- Tests include expected exact values where applicable
- Tests serve as executable documentation
- Placeholder `pass` statements mark behaviors that need runtime verification

## Porting Checklist

When porting to Node.js, verify each test category:

- [ ] All AGENT_CONFIG values match exactly
- [ ] SCRIPT_TYPE_CHOICES match exactly  
- [ ] CLAUDE_LOCAL_PATH is `~/.claude/local/claude`
- [ ] Banner ASCII art and colors match
- [ ] Token precedence is correct
- [ ] Rate limit parsing extracts all headers
- [ ] Tool detection uses correct methods
- [ ] Git operations use correct commands
- [ ] StepTracker has all status transitions
- [ ] JSON merge is recursive for objects
- [ ] Interactive selection uses correct keys
- [ ] Init command has all flags and behaviors
- [ ] Check command scans correct tools
- [ ] Version command shows correct info
- [ ] Template download uses correct API
- [ ] Template extraction handles nested ZIPs
- [ ] Script permissions set correctly (Unix)
- [ ] Shell scripts have equivalent Node.js functions
- [ ] Exit codes match documented values
- [ ] Error messages include actionable guidance
- [ ] Platform-specific code paths work correctly
