# Copilot Instructions: Port Specify CLI from Python to Node.js

## Project Overview

You are porting **Specify CLI** - part of **GitHub Spec Kit** - from Python to Node.js/TypeScript. Spec Kit is a toolkit for Spec-Driven Development (SDD) that bootstraps projects with templates, scripts, and AI agent integrations.

> **IMPORTANT:** All Node.js/TypeScript ported code MUST be placed in the `nodejs/` folder at the project root. This keeps the Python source intact while developing the port.

### What Specify CLI Does

1. **`specify init <project-name>`** - Initialize a new project with SDD templates
2. **`specify check`** - Verify required tools are installed
3. **`specify version`** - Display version and system information

The CLI downloads template packages from GitHub releases, extracts them, sets up directory structures, and optionally initializes git repositories.

---

## Architecture Mapping: Python → Node.js

### Core Technology Stack

| Python Component | Node.js Equivalent | Notes |
|------------------|-------------------|-------|
| `typer` | `commander` or `yargs` | CLI framework with subcommands |
| `rich` | `chalk` + `cli-spinners` + `cli-table3` | Terminal formatting, colors, tables, progress |
| `httpx` | `node-fetch` or `axios` | HTTP client for GitHub API |
| `readchar` | `readline` + `keypress` or `inquirer` | Interactive keyboard input |
| `zipfile` | `adm-zip` or `extract-zip` | ZIP extraction |
| `platformdirs` | `env-paths` | Platform-specific directories |
| `truststore` | Native Node.js TLS | SSL/TLS handling |
| `shutil` | `fs-extra` | File system operations |
| `subprocess` | `child_process` / `execa` | Running shell commands |
| `json` | Native JSON | JSON parsing (built-in) |
| `pathlib.Path` | `path` + `fs` | Path manipulation |

### Recommended Node.js Dependencies

```json
{
  "dependencies": {
    "commander": "^12.0.0",
    "chalk": "^5.3.0",
    "ora": "^8.0.0",
    "cli-table3": "^0.6.3",
    "inquirer": "^9.2.0",
    "node-fetch": "^3.3.0",
    "adm-zip": "^0.5.10",
    "fs-extra": "^11.2.0",
    "execa": "^8.0.0",
    "env-paths": "^3.0.0",
    "semver": "^7.6.0"
  },
  "devDependencies": {
    "typescript": "^5.4.0",
    "@types/node": "^20.0.0",
    "vitest": "^1.4.0",
    "eslint": "^9.0.0",
    "@typescript-eslint/eslint-plugin": "^7.0.0",
    "prettier": "^3.2.0"
  }
}
```

---

## File Structure for Node.js Port

> **All ported code goes in the `nodejs/` folder at the project root.**

```
spec-kit-nodejs/
├── nodejs/                     # <-- ROOT FOLDER FOR ALL NODE.JS CODE
│   ├── src/
│   │   ├── index.ts            # Main entry point & CLI setup
│   │   ├── cli.ts              # CLI wiring with Commander
│   │   ├── commands/
│   │   │   ├── init.ts         # 'specify init' command
│   │   │   ├── check.ts        # 'specify check' command
│   │   │   └── version.ts      # 'specify version' command
│   │   ├── lib/
│   │   │   ├── config.ts       # AGENT_CONFIG and constants
│   │   │   ├── errors.ts       # Error classes and exit codes
│   │   │   ├── github/
│   │   │   │   ├── token.ts    # GitHub token handling
│   │   │   │   ├── rate-limit.ts # Rate limit parsing & errors
│   │   │   │   └── client.ts   # GitHub API client
│   │   │   ├── template/
│   │   │   │   ├── download.ts # Template download from releases
│   │   │   │   ├── extract.ts  # ZIP extraction
│   │   │   │   ├── merge.ts    # JSON deep merge
│   │   │   │   └── permissions.ts # Script chmod handling
│   │   │   ├── tools/
│   │   │   │   ├── detect.ts   # Tool detection (which/where)
│   │   │   │   └── git.ts      # Git operations
│   │   │   └── ui/
│   │   │       ├── banner.ts   # ASCII banner display
│   │   │       ├── select.ts   # Arrow key selection menu
│   │   │       ├── tracker.ts  # Step tracker (progress display)
│   │   │       └── console.ts  # Console utilities (chalk wrappers)
│   │   └── types/
│   │       └── index.ts        # TypeScript interfaces & types
│   ├── tests/
│   │   ├── setup.ts            # Test setup with mock utilities
│   │   ├── lib/
│   │   │   ├── config.test.ts
│   │   │   ├── errors.test.ts
│   │   │   ├── github/
│   │   │   │   ├── token.test.ts
│   │   │   │   └── rate-limit.test.ts
│   │   │   ├── template/
│   │   │   │   ├── download.test.ts
│   │   │   │   ├── extract.test.ts
│   │   │   │   ├── merge.test.ts
│   │   │   │   └── permissions.test.ts
│   │   │   ├── tools/
│   │   │   │   ├── detect.test.ts
│   │   │   │   └── git.test.ts
│   │   │   └── ui/
│   │   │       ├── banner.test.ts
│   │   │       ├── select.test.ts
│   │   │       └── tracker.test.ts
│   │   ├── commands/
│   │   │   ├── check.test.ts
│   │   │   ├── version.test.ts
│   │   │   ├── init.test.ts
│   │   │   └── exit-codes.test.ts
│   │   └── platform.test.ts
│   ├── bin/
│   │   └── specify.js          # Executable entry point
│   ├── package.json
│   ├── tsconfig.json
│   ├── vitest.config.ts
│   ├── .eslintrc.json
│   ├── .prettierrc
│   └── README.md
├── src/                        # Original Python source (keep intact)
│   └── specify_cli/
│       └── __init__.py
├── tests/                      # Original Python tests (reference)
│   └── acceptance/
└── docs/
    └── implementation-checklist.md
```

---

## Critical Data Structures to Port

### 1. AGENT_CONFIG (src/lib/config.ts)

```typescript
interface AgentConfig {
  name: string;
  folder: string;
  installUrl: string | null;
  requiresCli: boolean;
}

const AGENT_CONFIG: Record<string, AgentConfig> = {
  copilot: {
    name: "GitHub Copilot",
    folder: ".github/",
    installUrl: null,
    requiresCli: false,
  },
  claude: {
    name: "Claude Code",
    folder: ".claude/",
    installUrl: "https://docs.anthropic.com/en/docs/claude-code/setup",
    requiresCli: true,
  },
  gemini: {
    name: "Gemini CLI",
    folder: ".gemini/",
    installUrl: "https://github.com/google-gemini/gemini-cli",
    requiresCli: true,
  },
  "cursor-agent": {
    name: "Cursor",
    folder: ".cursor/",
    installUrl: null,
    requiresCli: false,
  },
  qwen: {
    name: "Qwen Code",
    folder: ".qwen/",
    installUrl: "https://github.com/QwenLM/qwen-code",
    requiresCli: true,
  },
  opencode: {
    name: "opencode",
    folder: ".opencode/",
    installUrl: "https://opencode.ai",
    requiresCli: true,
  },
  codex: {
    name: "Codex CLI",
    folder: ".codex/",
    installUrl: "https://github.com/openai/codex",
    requiresCli: true,
  },
  windsurf: {
    name: "Windsurf",
    folder: ".windsurf/",
    installUrl: null,
    requiresCli: false,
  },
  kilocode: {
    name: "Kilo Code",
    folder: ".kilocode/",
    installUrl: null,
    requiresCli: false,
  },
  auggie: {
    name: "Auggie CLI",
    folder: ".augment/",
    installUrl: "https://docs.augmentcode.com/cli/setup-auggie/install-auggie-cli",
    requiresCli: true,
  },
  codebuddy: {
    name: "CodeBuddy",
    folder: ".codebuddy/",
    installUrl: "https://www.codebuddy.ai/cli",
    requiresCli: true,
  },
  roo: {
    name: "Roo Code",
    folder: ".roo/",
    installUrl: null,
    requiresCli: false,
  },
  q: {
    name: "Amazon Q Developer CLI",
    folder: ".amazonq/",
    installUrl: "https://aws.amazon.com/developer/learning/q-developer-cli/",
    requiresCli: true,
  },
  amp: {
    name: "Amp",
    folder: ".agents/",
    installUrl: "https://ampcode.com/manual#install",
    requiresCli: true,
  },
  shai: {
    name: "SHAI",
    folder: ".shai/",
    installUrl: "https://github.com/ovh/shai",
    requiresCli: true,
  },
};

const SCRIPT_TYPE_CHOICES: Record<string, string> = {
  sh: "POSIX Shell (bash/zsh)",
  ps: "PowerShell",
};
```

### 2. StepTracker Class (src/lib/ui/tracker.ts)

```typescript
type StepStatus = "pending" | "running" | "done" | "error" | "skipped";

interface Step {
  key: string;
  label: string;
  status: StepStatus;
  detail: string;
}

class StepTracker {
  private title: string;
  private steps: Step[] = [];
  private refreshCallback?: () => void;

  constructor(title: string) {
    this.title = title;
  }

  attachRefresh(cb: () => void): void {
    this.refreshCallback = cb;
  }

  add(key: string, label: string): void {
    if (!this.steps.find(s => s.key === key)) {
      this.steps.push({ key, label, status: "pending", detail: "" });
      this.maybeRefresh();
    }
  }

  start(key: string, detail = ""): void {
    this.update(key, "running", detail);
  }

  complete(key: string, detail = ""): void {
    this.update(key, "done", detail);
  }

  error(key: string, detail = ""): void {
    this.update(key, "error", detail);
  }

  skip(key: string, detail = ""): void {
    this.update(key, "skipped", detail);
  }

  private update(key: string, status: StepStatus, detail: string): void {
    const step = this.steps.find(s => s.key === key);
    if (step) {
      step.status = status;
      if (detail) step.detail = detail;
    } else {
      this.steps.push({ key, label: key, status, detail });
    }
    this.maybeRefresh();
  }

  private maybeRefresh(): void {
    this.refreshCallback?.();
  }

  render(): string {
    // Implement tree-style rendering with chalk
    // Green ● for done, cyan ○ for running, dim ○ for pending, red ● for error, yellow ○ for skipped
  }
}
```

---

## Command Implementation Guides

### 1. `specify init` Command

**Key behaviors to replicate:**

1. **Banner display** - ASCII art with gradient colors
2. **Project path validation** - Check if directory exists, handle `--here` flag
3. **Interactive AI selection** - Arrow key navigation menu
4. **Script type selection** - sh vs ps based on OS
5. **GitHub release download** - Fetch latest release, download asset ZIP
6. **ZIP extraction** - Handle nested directories, merge with existing files
7. **Git initialization** - Optional, check if already a repo
8. **Progress tracking** - Live-updating step tracker

**Critical edge cases:**

- Handle `project_name == "."` as `--here` flag
- Merge `.vscode/settings.json` instead of overwriting
- Set executable permissions on .sh scripts (non-Windows)
- Support `--force` to skip confirmation for non-empty directories
- Validate branch name length (GitHub 244-byte limit)

```typescript
// src/commands/init.ts - Key function signatures
interface InitOptions {
  ai?: string;
  script?: string;
  ignoreAgentTools?: boolean;
  noGit?: boolean;
  here?: boolean;
  force?: boolean;
  skipTls?: boolean;
  debug?: boolean;
  githubToken?: string;
}

async function init(projectName: string | undefined, options: InitOptions): Promise<void> {
  // 1. Show banner
  // 2. Validate project name and path
  // 3. Select AI assistant (interactive or from option)
  // 4. Check agent CLI if required
  // 5. Select script type
  // 6. Initialize step tracker
  // 7. Download and extract template
  // 8. Set executable permissions (Unix)
  // 9. Initialize git (if not --no-git)
  // 10. Show completion panel with next steps
}
```

### 2. `specify check` Command

**Key behaviors:**

1. Display banner
2. Check for each tool in AGENT_CONFIG (only if `requiresCli: true`)
3. Check for git, code, code-insiders
4. Use StepTracker to show results
5. Special handling for Claude CLI at `~/.claude/local/claude`

```typescript
// src/commands/check.ts
async function check(): Promise<void> {
  showBanner();
  
  const tracker = new StepTracker("Check Available Tools");
  
  // Check git
  tracker.add("git", "Git version control");
  const gitOk = await checkTool("git", tracker);
  
  // Check each agent
  for (const [key, config] of Object.entries(AGENT_CONFIG)) {
    tracker.add(key, config.name);
    if (config.requiresCli) {
      await checkTool(key, tracker);
    } else {
      tracker.skip(key, "IDE-based, no CLI check");
    }
  }
  
  // Check VS Code
  tracker.add("code", "Visual Studio Code");
  await checkTool("code", tracker);
  
  console.log(tracker.render());
}
```

### 3. `specify version` Command

**Key behaviors:**

1. Get CLI version from package.json
2. Fetch latest template version from GitHub releases API
3. Display system info (Node.js version, platform, architecture)

---

## GitHub API Integration

### Rate Limit Handling

The Python code has sophisticated rate limit handling. Replicate this:

```typescript
// src/lib/github.ts
interface RateLimitInfo {
  limit?: string;
  remaining?: string;
  resetEpoch?: number;
  resetTime?: Date;
  retryAfterSeconds?: number;
}

function parseRateLimitHeaders(headers: Headers): RateLimitInfo {
  const info: RateLimitInfo = {};
  
  if (headers.has("X-RateLimit-Limit")) {
    info.limit = headers.get("X-RateLimit-Limit")!;
  }
  if (headers.has("X-RateLimit-Remaining")) {
    info.remaining = headers.get("X-RateLimit-Remaining")!;
  }
  if (headers.has("X-RateLimit-Reset")) {
    const epoch = parseInt(headers.get("X-RateLimit-Reset")!, 10);
    if (epoch) {
      info.resetEpoch = epoch;
      info.resetTime = new Date(epoch * 1000);
    }
  }
  if (headers.has("Retry-After")) {
    const retryAfter = headers.get("Retry-After")!;
    const parsed = parseInt(retryAfter, 10);
    if (!isNaN(parsed)) {
      info.retryAfterSeconds = parsed;
    }
  }
  
  return info;
}

function formatRateLimitError(status: number, headers: Headers, url: string): string {
  const info = parseRateLimitHeaders(headers);
  
  let message = `GitHub API returned status ${status} for ${url}\n\n`;
  
  if (Object.keys(info).length > 0) {
    message += "Rate Limit Information:\n";
    if (info.limit) message += `  • Rate Limit: ${info.limit} requests/hour\n`;
    if (info.remaining) message += `  • Remaining: ${info.remaining}\n`;
    if (info.resetTime) message += `  • Resets at: ${info.resetTime.toLocaleString()}\n`;
    if (info.retryAfterSeconds) message += `  • Retry after: ${info.retryAfterSeconds} seconds\n`;
    message += "\n";
  }
  
  message += "Troubleshooting Tips:\n";
  message += "  • Use a GitHub token via --github-token or GH_TOKEN/GITHUB_TOKEN env var\n";
  message += "  • Authenticated requests: 5,000/hour vs 60/hour for unauthenticated\n";
  
  return message;
}

function getGitHubToken(cliToken?: string): string | undefined {
  return (cliToken || process.env.GH_TOKEN || process.env.GITHUB_TOKEN || "").trim() || undefined;
}

function getAuthHeaders(cliToken?: string): Record<string, string> {
  const token = getGitHubToken(cliToken);
  return token ? { Authorization: `Bearer ${token}` } : {};
}
```

### Template Download

```typescript
// src/lib/template.ts
interface TemplateMetadata {
  filename: string;
  size: number;
  release: string;
  assetUrl: string;
}

async function downloadTemplateFromGitHub(
  aiAssistant: string,
  downloadDir: string,
  options: {
    scriptType?: string;
    verbose?: boolean;
    showProgress?: boolean;
    debug?: boolean;
    githubToken?: string;
  }
): Promise<{ zipPath: string; metadata: TemplateMetadata }> {
  const repoOwner = "github";
  const repoName = "spec-kit";
  const apiUrl = `https://api.github.com/repos/${repoOwner}/${repoName}/releases/latest`;
  
  // 1. Fetch release info
  // 2. Find matching asset (spec-kit-template-{ai}-{script}-{version}.zip)
  // 3. Download with progress reporting
  // 4. Return path and metadata
}
```

---

## Interactive Selection Menu

The Python code uses `readchar` for cross-platform keyboard input. In Node.js, use `inquirer` or a custom implementation:

```typescript
// src/lib/ui/select.ts
import inquirer from 'inquirer';

async function selectWithArrows<T extends string>(
  options: Record<T, string>,
  prompt: string,
  defaultKey?: T
): Promise<T> {
  const choices = Object.entries(options).map(([key, description]) => ({
    name: `${key} (${description})`,
    value: key,
    short: key,
  }));
  
  const { selection } = await inquirer.prompt([
    {
      type: 'list',
      name: 'selection',
      message: prompt,
      choices,
      default: defaultKey,
      loop: false,
    },
  ]);
  
  return selection as T;
}
```

---

## Platform-Specific Considerations

### 1. Tool Detection

```typescript
// src/lib/tools.ts
import { execSync } from 'child_process';
import { existsSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

// Special path for Claude CLI after `claude migrate-installer`
const CLAUDE_LOCAL_PATH = join(homedir(), '.claude', 'local', 'claude');

function checkTool(tool: string, tracker?: StepTracker): boolean {
  // Special handling for Claude CLI
  if (tool === 'claude') {
    if (existsSync(CLAUDE_LOCAL_PATH)) {
      tracker?.complete(tool, 'available');
      return true;
    }
  }
  
  try {
    // Use 'where' on Windows, 'which' on Unix
    const cmd = process.platform === 'win32' ? `where ${tool}` : `which ${tool}`;
    execSync(cmd, { stdio: 'ignore' });
    tracker?.complete(tool, 'available');
    return true;
  } catch {
    tracker?.error(tool, 'not found');
    return false;
  }
}
```

### 2. Script Permissions (Unix Only)

```typescript
// src/lib/template.ts
import { chmodSync, statSync, readFileSync } from 'fs';
import { join } from 'path';
import { readdirSync } from 'fs';

function ensureExecutableScripts(projectPath: string, tracker?: StepTracker): void {
  if (process.platform === 'win32') return; // Skip on Windows
  
  const scriptsRoot = join(projectPath, '.specify', 'scripts');
  if (!existsSync(scriptsRoot)) return;
  
  let updated = 0;
  const failures: string[] = [];
  
  // Recursively find .sh files
  function processDir(dir: string) {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      const fullPath = join(dir, entry.name);
      if (entry.isDirectory()) {
        processDir(fullPath);
      } else if (entry.isFile() && entry.name.endsWith('.sh')) {
        try {
          // Check if file starts with shebang
          const content = readFileSync(fullPath);
          if (content.slice(0, 2).toString() !== '#!') continue;
          
          const stat = statSync(fullPath);
          const mode = stat.mode;
          
          // Skip if already executable
          if (mode & 0o111) continue;
          
          // Add execute permissions
          let newMode = mode;
          if (mode & 0o400) newMode |= 0o100; // Owner read -> owner execute
          if (mode & 0o040) newMode |= 0o010; // Group read -> group execute
          if (mode & 0o004) newMode |= 0o001; // Others read -> others execute
          if (!(newMode & 0o100)) newMode |= 0o100; // Ensure owner can execute
          
          chmodSync(fullPath, newMode);
          updated++;
        } catch (err) {
          failures.push(`${entry.name}: ${err}`);
        }
      }
    }
  }
  
  processDir(scriptsRoot);
  
  if (tracker) {
    const detail = `${updated} updated${failures.length ? `, ${failures.length} failed` : ''}`;
    tracker.add('chmod', 'Set script permissions recursively');
    if (failures.length) {
      tracker.error('chmod', detail);
    } else {
      tracker.complete('chmod', detail);
    }
  }
}
```

### 3. Default Script Type Detection

```typescript
function getDefaultScriptType(): 'sh' | 'ps' {
  return process.platform === 'win32' ? 'ps' : 'sh';
}
```

---

## JSON Merging for .vscode/settings.json

```typescript
// src/lib/template.ts
import { readFileSync, writeFileSync, existsSync } from 'fs';

function deepMerge(base: Record<string, any>, update: Record<string, any>): Record<string, any> {
  const result = { ...base };
  
  for (const [key, value] of Object.entries(update)) {
    if (key in result && typeof result[key] === 'object' && typeof value === 'object' 
        && !Array.isArray(result[key]) && !Array.isArray(value)) {
      result[key] = deepMerge(result[key], value);
    } else {
      result[key] = value;
    }
  }
  
  return result;
}

function handleVscodeSettings(
  sourcePath: string,
  destPath: string,
  verbose = false
): void {
  try {
    const newSettings = JSON.parse(readFileSync(sourcePath, 'utf-8'));
    
    if (existsSync(destPath)) {
      const existingSettings = JSON.parse(readFileSync(destPath, 'utf-8'));
      const merged = deepMerge(existingSettings, newSettings);
      writeFileSync(destPath, JSON.stringify(merged, null, 4) + '\n');
      if (verbose) console.log(`Merged: ${destPath}`);
    } else {
      copyFileSync(sourcePath, destPath);
      if (verbose) console.log(`Copied: ${destPath}`);
    }
  } catch (err) {
    // Fall back to copy on error
    copyFileSync(sourcePath, destPath);
    if (verbose) console.warn(`Warning: Could not merge, copying instead: ${err}`);
  }
}
```

---

## ASCII Banner

```typescript
// src/lib/ui/banner.ts
import chalk from 'chalk';

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

export function showBanner(): void {
  const lines = BANNER.trim().split('\n');
  
  const coloredBanner = lines.map((line, i) => COLORS[i % COLORS.length](line)).join('\n');
  
  console.log(centerText(coloredBanner));
  console.log(centerText(chalk.italic.yellowBright(TAGLINE)));
  console.log();
}

function centerText(text: string): string {
  const terminalWidth = process.stdout.columns || 80;
  return text.split('\n').map(line => {
    const padding = Math.max(0, Math.floor((terminalWidth - stripAnsi(line).length) / 2));
    return ' '.repeat(padding) + line;
  }).join('\n');
}
```

---

## Error Handling Patterns

### Structured Exit Codes

```typescript
// src/lib/errors.ts
export enum ExitCode {
  SUCCESS = 0,
  GENERAL_ERROR = 1,
  MISSING_DEPENDENCY = 2,
  INVALID_ARGUMENT = 3,
  NETWORK_ERROR = 4,
  FILE_SYSTEM_ERROR = 5,
}

export class SpecifyError extends Error {
  constructor(
    message: string,
    public exitCode: ExitCode = ExitCode.GENERAL_ERROR,
    public details?: string
  ) {
    super(message);
    this.name = 'SpecifyError';
  }
}
```

### Graceful Shutdown

```typescript
// src/index.ts
process.on('SIGINT', () => {
  console.log('\n' + chalk.yellow('Operation cancelled'));
  process.exit(130);
});
```

---

## Testing Strategy

### Unit Tests with Vitest

```typescript
// tests/lib/github.test.ts
import { describe, it, expect, vi } from 'vitest';
import { parseRateLimitHeaders } from '../src/lib/github';

describe('parseRateLimitHeaders', () => {
  it('should extract rate limit info from headers', () => {
    const headers = new Headers({
      'X-RateLimit-Limit': '5000',
      'X-RateLimit-Remaining': '4999',
      'X-RateLimit-Reset': '1700000000',
    });
    
    const info = parseRateLimitHeaders(headers);
    
    expect(info.limit).toBe('5000');
    expect(info.remaining).toBe('4999');
    expect(info.resetEpoch).toBe(1700000000);
  });
});
```

### Integration Tests

```typescript
// tests/commands/check.test.ts
import { describe, it, expect, vi } from 'vitest';
import { check } from '../src/commands/check';

describe('specify check', () => {
  it('should detect installed git', async () => {
    // Mock execSync to simulate git being available
    vi.spyOn(child_process, 'execSync').mockImplementation((cmd) => {
      if (cmd.includes('git')) return Buffer.from('/usr/bin/git');
      throw new Error('not found');
    });
    
    await check();
    // Assert output includes git check passed
  });
});
```

---

## Scripts to Port

The bash/PowerShell scripts in `scripts/` should remain as-is since they're part of the template that gets deployed to user projects. However, you may want to create Node.js equivalents for development:

| Script | Purpose | Port Priority |
|--------|---------|---------------|
| `common.sh` / `common.ps1` | Shared utilities | Keep as-is (template) |
| `create-new-feature.sh/.ps1` | Create feature branches | Keep as-is (template) |
| `setup-plan.sh/.ps1` | Initialize planning artifacts | Keep as-is (template) |
| `check-prerequisites.sh/.ps1` | Verify prerequisites | Keep as-is (template) |
| `update-agent-context.sh/.ps1` | Update agent config files | Keep as-is (template) |

---

## CLI Entry Point Setup

### package.json Configuration

```json
{
  "name": "specify-cli",
  "version": "0.0.22",
  "description": "Specify CLI - GitHub Spec Kit for Spec-Driven Development",
  "type": "module",
  "main": "dist/index.js",
  "bin": {
    "specify": "bin/specify.js"
  },
  "scripts": {
    "build": "tsc",
    "dev": "tsx src/index.ts",
    "test": "vitest",
    "test:coverage": "vitest --coverage",
    "lint": "eslint src --ext .ts",
    "format": "prettier --write src/**/*.ts"
  },
  "engines": {
    "node": ">=18.0.0"
  },
  "keywords": ["cli", "specification", "spec-driven-development", "sdd", "ai-coding"],
  "author": "GitHub",
  "license": "MIT"
}
```

### Executable Wrapper (nodejs/bin/specify.js)

```javascript
#!/usr/bin/env node
import '../dist/cli.js';
```

### Main Entry Point (nodejs/src/cli.ts)

```typescript
#!/usr/bin/env node
import { Command } from 'commander';
import { init } from './commands/init.js';
import { check } from './commands/check.js';
import { version as versionCmd } from './commands/version.js';
import { showBanner } from './lib/ui/banner.js';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const pkg = JSON.parse(readFileSync(join(__dirname, '../package.json'), 'utf-8'));

const program = new Command();

program
  .name('specify')
  .description('Setup tool for Specify spec-driven development projects')
  .version(pkg.version)
  .hook('preAction', (thisCommand) => {
    // Show banner before any command if no subcommand
    if (!thisCommand.args.length) {
      showBanner();
    }
  });

program
  .command('init [project-name]')
  .description('Initialize a new Specify project from the latest template')
  .option('--ai <assistant>', 'AI assistant to use')
  .option('--script <type>', 'Script type: sh or ps')
  .option('--ignore-agent-tools', 'Skip checks for AI agent CLI tools')
  .option('--no-git', 'Skip git repository initialization')
  .option('--here', 'Initialize in current directory')
  .option('--force', 'Skip confirmation for non-empty directories')
  .option('--skip-tls', 'Skip TLS verification (not recommended)')
  .option('--debug', 'Show verbose debug output')
  .option('--github-token <token>', 'GitHub token for API requests')
  .action(init);

program
  .command('check')
  .description('Check that all required tools are installed')
  .action(check);

program
  .command('version')
  .description('Display version and system information')
  .action(versionCmd);

// Show banner when no command provided
if (process.argv.length <= 2) {
  showBanner();
  console.log('Run \'specify --help\' for usage information\n');
} else {
  program.parse();
}
```

---

## Key Behavioral Requirements

### 1. Must Match Python Behavior Exactly

- Same exit codes
- Same error messages (content can differ, structure should match)
- Same file outputs
- Same interactive prompts
- Same progress display

### 2. Cross-Platform Compatibility

- Windows (PowerShell default)
- macOS (bash default)
- Linux (bash default)

### 3. Performance Requirements

- CLI startup: < 500ms
- Template download: Show progress for files > 1MB
- Git operations: Timeout after 30 seconds

### 4. Error Recovery

- Network failures: Clear error with retry suggestion
- Missing files: Clear error with fix suggestion
- Permission errors: Clear error with platform-specific fix

---

## Validation Checklist

Before considering the port complete, verify:

- [ ] `specify init my-project --ai copilot` creates identical directory structure
- [ ] `specify init --here` works in empty and non-empty directories
- [ ] `specify check` correctly detects all supported tools
- [ ] `specify version` shows correct CLI and template versions
- [ ] GitHub rate limiting is handled gracefully
- [ ] Interactive selection works with keyboard navigation
- [ ] Progress tracking displays correctly in terminal
- [ ] Git initialization is optional and works correctly
- [ ] Template extraction handles nested ZIPs correctly
- [ ] `.vscode/settings.json` is merged, not overwritten
- [ ] Script permissions are set correctly on Unix systems
- [ ] Codex-specific `CODEX_HOME` message is shown when needed
- [ ] All error messages include actionable guidance
- [ ] Banner displays correctly in terminals of different widths

---

## Resources

- [Original Python Source](./src/specify_cli/__init__.py) - Keep this intact as reference
- [Node.js Port](./nodejs/) - All ported code goes here
- [Implementation Checklist](./docs/implementation-checklist.md) - Track progress
- [Agent Configuration Guide](./AGENTS.md)
- [Spec-Driven Development Methodology](./spec-driven.md)
- [Project README](./README.md)

---

## Development Workflow

1. **Work in nodejs/ folder** - All new code goes in the `nodejs/` directory
2. **Start with types** - Define all TypeScript interfaces first (`nodejs/src/types/`)
3. **Port tests first (TDD)** - Port Python acceptance tests to Vitest (`nodejs/tests/`)
4. **Build lib modules** - GitHub client, template handler, UI components (`nodejs/src/lib/`)
5. **Implement commands** - Start with `check` (simplest), then `version`, then `init`
6. **Polish UI** - Ensure terminal output matches Python version
7. **Cross-platform testing** - Test on Windows, macOS, and Linux

### Running the Node.js Port

```bash
cd nodejs
npm install
npm run build
npm test

# Run CLI locally
npx . --help
npx . check
npx . init my-project --ai copilot --script sh --no-git
```

---

*This instruction file was generated from deep analysis of the Specify CLI Python codebase. Use it as your primary reference when implementing the Node.js port.*
