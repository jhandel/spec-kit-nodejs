# Specify CLI Behavioral Specification

This document provides a complete behavioral specification of the Specify CLI,
serving as the authoritative reference for the Node.js port.

## Table of Contents

1. [CLI Commands](#cli-commands)
2. [Configuration](#configuration)
3. [GitHub API Integration](#github-api-integration)
4. [Template Processing](#template-processing)
5. [Tool Detection](#tool-detection)
6. [Git Operations](#git-operations)
7. [UI Components](#ui-components)
8. [Error Handling](#error-handling)
9. [Cross-Platform Behavior](#cross-platform-behavior)

---

## CLI Commands

### `specify init [project-name]`

**Purpose:** Initialize a new Specify project from the latest template.

**Arguments:**
| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| project-name | string | No | None | Directory name for new project |

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--ai` | string | (interactive) | AI assistant: copilot, claude, gemini, etc. |
| `--script` | string | (OS-based) | Script type: sh or ps |
| `--ignore-agent-tools` | flag | false | Skip CLI tool verification |
| `--no-git` | flag | false | Skip Git initialization |
| `--here` | flag | false | Initialize in current directory |
| `--force` | flag | false | Skip non-empty directory confirmation |
| `--skip-tls` | flag | false | Skip TLS verification |
| `--debug` | flag | false | Enable verbose output |
| `--github-token` | string | (env var) | GitHub API token |

**Workflow:**
```
1. Display banner
2. Validate project name/path
3. Check if directory non-empty (prompt or --force)
4. Select AI assistant (interactive or --ai)
5. Verify agent CLI if required (unless --ignore-agent-tools)
6. Select script type (interactive or --script)
7. Initialize StepTracker
8. Download template from GitHub releases
9. Extract template to project directory
10. Merge .vscode/settings.json (if exists)
11. Set executable permissions on .sh files (Unix)
12. Initialize Git repository (unless --no-git)
13. Display completion panel with next steps
```

**Exit Codes:**
- 0: Success
- 1: General error
- 2: Missing dependency
- 3: Invalid argument
- 4: Network error
- 5: File system error

### `specify check`

**Purpose:** Verify that required tools are installed.

**Arguments:** None

**Output Format:**
```
● git - available
● claude - available
○ gemini - not found
○ copilot - IDE-based, no CLI check
● code - available
```

**Tools Checked:**
1. git (version control)
2. All CLI-based agents from AGENT_CONFIG
3. code (VS Code)
4. code-insiders (VS Code Insiders)

### `specify version`

**Purpose:** Display version and system information.

**Output Format:**
```
Specify CLI v0.0.22
Template v0.0.22 (latest)
Python 3.11.5
Platform: win32 (x64)
```

---

## Configuration

### AGENT_CONFIG

Complete agent registry:

```javascript
const AGENT_CONFIG = {
  "copilot": {
    name: "GitHub Copilot",
    folder: ".github/",
    installUrl: null,
    requiresCli: false
  },
  "claude": {
    name: "Claude Code",
    folder: ".claude/",
    installUrl: "https://docs.anthropic.com/en/docs/claude-code/setup",
    requiresCli: true
  },
  "gemini": {
    name: "Gemini CLI",
    folder: ".gemini/",
    installUrl: "https://github.com/google-gemini/gemini-cli",
    requiresCli: true
  },
  "cursor-agent": {
    name: "Cursor",
    folder: ".cursor/",
    installUrl: null,
    requiresCli: false
  },
  "qwen": {
    name: "Qwen Code",
    folder: ".qwen/",
    installUrl: "https://github.com/QwenLM/qwen-code",
    requiresCli: true
  },
  "opencode": {
    name: "opencode",
    folder: ".opencode/",
    installUrl: "https://opencode.ai",
    requiresCli: true
  },
  "codex": {
    name: "Codex CLI",
    folder: ".codex/",
    installUrl: "https://github.com/openai/codex",
    requiresCli: true
  },
  "windsurf": {
    name: "Windsurf",
    folder: ".windsurf/",
    installUrl: null,
    requiresCli: false
  },
  "kilocode": {
    name: "Kilo Code",
    folder: ".kilocode/",
    installUrl: null,
    requiresCli: false
  },
  "auggie": {
    name: "Auggie CLI",
    folder: ".augment/",
    installUrl: "https://docs.augmentcode.com/cli/setup-auggie/install-auggie-cli",
    requiresCli: true
  },
  "codebuddy": {
    name: "CodeBuddy",
    folder: ".codebuddy/",
    installUrl: "https://www.codebuddy.ai/cli",
    requiresCli: true
  },
  "roo": {
    name: "Roo Code",
    folder: ".roo/",
    installUrl: null,
    requiresCli: false
  },
  "q": {
    name: "Amazon Q Developer CLI",
    folder: ".amazonq/",
    installUrl: "https://aws.amazon.com/developer/learning/q-developer-cli/",
    requiresCli: true
  },
  "amp": {
    name: "Amp",
    folder: ".agents/",
    installUrl: "https://ampcode.com/manual#install",
    requiresCli: true
  },
  "shai": {
    name: "SHAI",
    folder: ".shai/",
    installUrl: "https://github.com/ovh/shai",
    requiresCli: true
  }
};
```

### SCRIPT_TYPE_CHOICES

```javascript
const SCRIPT_TYPE_CHOICES = {
  "sh": "POSIX Shell (bash/zsh)",
  "ps": "PowerShell"
};
```

### Constants

```javascript
const REPO_OWNER = "github";
const REPO_NAME = "spec-kit";
const BRANCH_NAME_MAX_LENGTH = 244; // GitHub limit
const DOWNLOAD_CHUNK_SIZE = 8192;
const API_TIMEOUT = 30; // seconds
const DOWNLOAD_TIMEOUT = 60; // seconds
```

---

## GitHub API Integration

### Token Resolution

```javascript
function getGitHubToken(cliToken) {
  // Priority order:
  // 1. CLI argument
  // 2. GH_TOKEN env var
  // 3. GITHUB_TOKEN env var
  const token = cliToken 
    || process.env.GH_TOKEN 
    || process.env.GITHUB_TOKEN 
    || '';
  return token.trim() || undefined;
}
```

### Auth Headers

```javascript
function getAuthHeaders(cliToken) {
  const token = getGitHubToken(cliToken);
  return token ? { 'Authorization': `Bearer ${token}` } : {};
}
```

### Rate Limit Parsing

```javascript
function parseRateLimitHeaders(headers) {
  const info = {};
  
  if (headers.has('X-RateLimit-Limit')) {
    info.limit = headers.get('X-RateLimit-Limit');
  }
  if (headers.has('X-RateLimit-Remaining')) {
    info.remaining = headers.get('X-RateLimit-Remaining');
  }
  if (headers.has('X-RateLimit-Reset')) {
    const epoch = parseInt(headers.get('X-RateLimit-Reset'), 10);
    if (epoch) {
      info.resetEpoch = epoch;
      info.resetTime = new Date(epoch * 1000);
    }
  }
  if (headers.has('Retry-After')) {
    const retryAfter = headers.get('Retry-After');
    const parsed = parseInt(retryAfter, 10);
    if (!isNaN(parsed)) {
      info.retryAfterSeconds = parsed;
    }
  }
  
  return info;
}
```

### Asset Pattern Matching

```javascript
function findMatchingAsset(assets, ai, script) {
  const prefix = `spec-kit-template-${ai}-${script}`;
  return assets.find(asset => 
    asset.name.startsWith(prefix) && asset.name.endsWith('.zip')
  );
}
```

---

## Template Processing

### Download Flow

```javascript
async function downloadTemplate(url, destPath, options) {
  const response = await fetch(url, {
    redirect: 'follow',
    timeout: 60000,
    headers: getAuthHeaders(options.githubToken)
  });
  
  if (!response.ok) {
    throw new Error(formatRateLimitError(response.status, response.headers, url));
  }
  
  const fileStream = fs.createWriteStream(destPath);
  const reader = response.body.getReader();
  let downloaded = 0;
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    fileStream.write(value);
    downloaded += value.length;
    
    if (options.showProgress) {
      // Update progress indicator
    }
  }
  
  fileStream.close();
}
```

### ZIP Extraction

```javascript
function extractTemplate(zipPath, destDir) {
  const zip = new AdmZip(zipPath);
  const entries = zip.getEntries();
  
  // Find common prefix (nested directory)
  let prefix = '';
  if (entries.length > 0) {
    const firstEntry = entries[0].entryName;
    const slashIndex = firstEntry.indexOf('/');
    if (slashIndex > 0) {
      prefix = firstEntry.substring(0, slashIndex + 1);
    }
  }
  
  for (const entry of entries) {
    if (entry.isDirectory) continue;
    
    // Strip prefix if exists
    let targetPath = entry.entryName;
    if (prefix && targetPath.startsWith(prefix)) {
      targetPath = targetPath.substring(prefix.length);
    }
    
    const fullPath = path.join(destDir, targetPath);
    
    // Special handling for .vscode/settings.json
    if (targetPath === '.vscode/settings.json') {
      handleVscodeSettings(entry, fullPath);
    } else {
      fs.ensureDirSync(path.dirname(fullPath));
      fs.writeFileSync(fullPath, entry.getData());
    }
  }
}
```

### VS Code Settings Merge

```javascript
function deepMerge(base, update) {
  const result = { ...base };
  
  for (const [key, value] of Object.entries(update)) {
    if (
      key in result && 
      typeof result[key] === 'object' && 
      typeof value === 'object' &&
      !Array.isArray(result[key]) && 
      !Array.isArray(value)
    ) {
      result[key] = deepMerge(result[key], value);
    } else {
      result[key] = value;
    }
  }
  
  return result;
}

function handleVscodeSettings(entry, destPath) {
  const newSettings = JSON.parse(entry.getData().toString());
  
  if (fs.existsSync(destPath)) {
    try {
      const existing = JSON.parse(fs.readFileSync(destPath, 'utf-8'));
      const merged = deepMerge(existing, newSettings);
      fs.writeFileSync(destPath, JSON.stringify(merged, null, 4) + '\n');
    } catch {
      // Fall back to overwrite on JSON parse error
      fs.writeFileSync(destPath, entry.getData());
    }
  } else {
    fs.ensureDirSync(path.dirname(destPath));
    fs.writeFileSync(destPath, entry.getData());
  }
}
```

### Executable Permissions (Unix)

```javascript
function ensureExecutableScripts(projectPath) {
  if (process.platform === 'win32') return;
  
  const scriptsRoot = path.join(projectPath, '.specify', 'scripts');
  if (!fs.existsSync(scriptsRoot)) return;
  
  walkDir(scriptsRoot, (filePath) => {
    if (!filePath.endsWith('.sh')) return;
    
    const content = fs.readFileSync(filePath);
    // Check for shebang
    if (content.slice(0, 2).toString() !== '#!') return;
    
    const stat = fs.statSync(filePath);
    const mode = stat.mode;
    
    // Skip if already executable
    if (mode & 0o111) return;
    
    // Calculate new mode
    let newMode = mode;
    if (mode & 0o400) newMode |= 0o100;
    if (mode & 0o040) newMode |= 0o010;
    if (mode & 0o004) newMode |= 0o001;
    if (!(newMode & 0o100)) newMode |= 0o100;
    
    fs.chmodSync(filePath, newMode);
  });
}
```

---

## Tool Detection

### Basic Detection

```javascript
function checkTool(tool) {
  // Special handling for Claude
  if (tool === 'claude') {
    const claudePath = path.join(os.homedir(), '.claude', 'local', 'claude');
    if (fs.existsSync(claudePath)) {
      return true;
    }
  }
  
  try {
    const cmd = process.platform === 'win32' ? `where ${tool}` : `which ${tool}`;
    execSync(cmd, { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}
```

### With StepTracker

```javascript
function checkToolForTracker(tool, tracker) {
  const found = checkTool(tool);
  
  if (found) {
    tracker.complete(tool, 'available');
  } else {
    tracker.error(tool, 'not found');
  }
  
  return found;
}
```

---

## Git Operations

### Repository Detection

```javascript
function isGitRepository(dir) {
  try {
    execSync('git rev-parse --git-dir', { 
      cwd: dir, 
      stdio: 'ignore' 
    });
    return true;
  } catch {
    return false;
  }
}

function getRepoRoot(dir) {
  try {
    return execSync('git rev-parse --show-toplevel', {
      cwd: dir,
      encoding: 'utf-8'
    }).trim();
  } catch {
    return null;
  }
}
```

### Repository Initialization

```javascript
function initGitRepo(projectPath) {
  if (isGitRepository(projectPath)) {
    return false; // Already a repo
  }
  
  try {
    execSync('git init', { cwd: projectPath, stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}
```

---

## UI Components

### Banner

```javascript
const BANNER = `
███████╗██████╗ ███████╗ ██████╗██╗███████╗██╗   ██╗
██╔════╝██╔══██╗██╔════╝██╔════╝██║██╔════╝╚██╗ ██╔╝
███████╗██████╔╝█████╗  ██║     ██║█████╗   ╚████╔╝ 
╚════██║██╔═══╝ ██╔══╝  ██║     ██║██╔══╝    ╚██╔╝  
███████║██║     ███████╗╚██████╗██║██║        ██║   
╚══════╝╚═╝     ╚══════╝ ╚═════╝╚═╝╚═╝        ╚═╝   
`;

const TAGLINE = "GitHub Spec Kit - Spec-Driven Development Toolkit";

const COLORS = [
  chalk.blueBright,
  chalk.blue,
  chalk.cyan,
  chalk.cyanBright,
  chalk.white,
  chalk.whiteBright,
];

function showBanner() {
  const lines = BANNER.trim().split('\n');
  const colored = lines.map((line, i) => COLORS[i % COLORS.length](line)).join('\n');
  console.log(centerText(colored));
  console.log(centerText(chalk.italic.yellowBright(TAGLINE)));
  console.log();
}
```

### StepTracker

```javascript
class StepTracker {
  constructor(title) {
    this.title = title;
    this.steps = [];
    this.refreshCallback = null;
  }
  
  attachRefresh(cb) {
    this.refreshCallback = cb;
  }
  
  add(key, label) {
    if (!this.steps.find(s => s.key === key)) {
      this.steps.push({ key, label, status: 'pending', detail: '' });
      this.maybeRefresh();
    }
  }
  
  start(key, detail = '') {
    this.update(key, 'running', detail);
  }
  
  complete(key, detail = '') {
    this.update(key, 'done', detail);
  }
  
  error(key, detail = '') {
    this.update(key, 'error', detail);
  }
  
  skip(key, detail = '') {
    this.update(key, 'skipped', detail);
  }
  
  update(key, status, detail) {
    const step = this.steps.find(s => s.key === key);
    if (step) {
      step.status = status;
      if (detail) step.detail = detail;
    } else {
      this.steps.push({ key, label: key, status, detail });
    }
    this.maybeRefresh();
  }
  
  maybeRefresh() {
    if (this.refreshCallback) {
      this.refreshCallback();
    }
  }
  
  render() {
    const icons = {
      pending: chalk.dim('○'),
      running: chalk.cyan('○'),
      done: chalk.green('●'),
      error: chalk.red('●'),
      skipped: chalk.yellow('○')
    };
    
    const lines = this.steps.map(step => {
      const icon = icons[step.status];
      const detail = step.detail ? ` - ${step.detail}` : '';
      return `${icon} ${step.label}${detail}`;
    });
    
    return lines.join('\n');
  }
}
```

### Interactive Selection

```javascript
async function selectWithArrows(options, prompt, defaultKey) {
  const choices = Object.entries(options).map(([key, desc]) => ({
    name: `${key} (${desc})`,
    value: key,
    short: key,
  }));
  
  const { selection } = await inquirer.prompt([{
    type: 'list',
    name: 'selection',
    message: prompt,
    choices,
    default: defaultKey,
    loop: false,
  }]);
  
  return selection;
}
```

---

## Error Handling

### Error Classes

```javascript
class SpecifyError extends Error {
  constructor(message, exitCode = 1, details = null) {
    super(message);
    this.name = 'SpecifyError';
    this.exitCode = exitCode;
    this.details = details;
  }
}

const ExitCode = {
  SUCCESS: 0,
  GENERAL_ERROR: 1,
  MISSING_DEPENDENCY: 2,
  INVALID_ARGUMENT: 3,
  NETWORK_ERROR: 4,
  FILE_SYSTEM_ERROR: 5,
};
```

### SIGINT Handling

```javascript
process.on('SIGINT', () => {
  console.log('\n' + chalk.yellow('Operation cancelled'));
  process.exit(130);
});
```

---

## Cross-Platform Behavior

### Default Script Type

```javascript
function getDefaultScriptType() {
  return process.platform === 'win32' ? 'ps' : 'sh';
}
```

### Path Handling

- Use `path.join()` for all path construction
- Use forward slashes in display/config (normalize for output)
- Use `os.homedir()` for home directory

### Line Endings

- Write files with LF (`\n`) endings
- Scripts should use appropriate line endings for their type:
  - `.sh` files: LF
  - `.ps1` files: CRLF (optional, PowerShell handles both)

### Environment Variables

```javascript
// Checked by CLI
process.env.GH_TOKEN       // GitHub token
process.env.GITHUB_TOKEN   // GitHub token (fallback)

// Checked by scripts
process.env.SPECIFY_FEATURE  // Override branch detection
```

---

## File Structure After Init

```
project/
├── .specify/
│   ├── memory/
│   │   └── constitution.md
│   ├── templates/
│   │   ├── spec-template.md
│   │   ├── plan-template.md
│   │   ├── tasks-template.md
│   │   └── checklist-template.md
│   └── scripts/
│       ├── bash/
│       │   ├── common.sh
│       │   ├── create-new-feature.sh
│       │   ├── setup-plan.sh
│       │   ├── check-prerequisites.sh
│       │   └── update-agent-context.sh
│       └── powershell/
│           ├── common.ps1
│           ├── create-new-feature.ps1
│           ├── setup-plan.ps1
│           ├── check-prerequisites.ps1
│           └── update-agent-context.ps1
├── .vscode/
│   └── settings.json
├── {agent-dir}/           # e.g., .github/, .claude/, etc.
│   └── {commands-dir}/    # e.g., agents/, commands/, etc.
│       ├── analyze.md
│       ├── clarify.md
│       ├── implement.md
│       ├── plan.md
│       ├── specify.md
│       ├── tasks.md
│       └── ...
└── .git/                  # Unless --no-git
```

---

*This specification is derived from the test suite and source code analysis.*
*Version: 0.0.22*
