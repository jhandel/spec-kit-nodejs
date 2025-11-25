# Plan: Approach 3 - Test-Driven Hybrid Port

**TL;DR:** Use the 586 acceptance tests as behavioral contracts. Port tests to Vitest first (creating the specification), then implement each module to pass its tests. This ensures behavioral parity with the Python implementation.

---

## Phase 0: Project Setup (Day 1)

**Goal:** Establish project foundation with all tooling configured.

### 0.1 Initialize Package

```json
// package.json
{
  "name": "@specify/cli",
  "version": "0.0.1",
  "description": "Specify CLI - GitHub Spec Kit for Spec-Driven Development",
  "type": "module",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "bin": {
    "specify": "./bin/specify.js"
  },
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js"
    }
  },
  "files": ["dist", "bin"],
  "scripts": {
    "build": "tsc",
    "dev": "tsx src/cli.ts",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "lint": "eslint src tests --ext .ts",
    "format": "prettier --write 'src/**/*.ts' 'tests/**/*.ts'",
    "typecheck": "tsc --noEmit",
    "prepublishOnly": "npm run build"
  },
  "engines": {
    "node": ">=18.0.0"
  },
  "keywords": ["cli", "specification", "spec-driven-development", "sdd", "ai-coding"],
  "author": "GitHub",
  "license": "MIT",
  "dependencies": {
    "commander": "^12.1.0",
    "chalk": "^5.3.0",
    "ora": "^8.0.1",
    "@inquirer/prompts": "^5.0.0",
    "cli-table3": "^0.6.5",
    "node-fetch": "^3.3.2",
    "adm-zip": "^0.5.14",
    "fs-extra": "^11.2.0",
    "execa": "^9.3.0",
    "env-paths": "^3.0.0"
  },
  "devDependencies": {
    "typescript": "^5.5.0",
    "@types/node": "^20.14.0",
    "@types/fs-extra": "^11.0.4",
    "@types/adm-zip": "^0.5.5",
    "vitest": "^1.6.0",
    "@vitest/coverage-v8": "^1.6.0",
    "eslint": "^9.5.0",
    "@typescript-eslint/eslint-plugin": "^7.13.0",
    "@typescript-eslint/parser": "^7.13.0",
    "prettier": "^3.3.2",
    "tsx": "^4.15.0"
  }
}
```

### 0.2 TypeScript Configuration

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "resolveJsonModule": true,
    "isolatedModules": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

### 0.3 Vitest Configuration

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['tests/**/*.test.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['src/**/*.ts'],
      exclude: ['src/types/**', 'src/**/*.d.ts'],
    },
    setupFiles: ['tests/setup.ts'],
  },
});
```

### 0.4 Directory Structure

```
spec-kit-nodejs/
├── src/
│   ├── cli.ts                    # Commander CLI setup
│   ├── index.ts                  # Package entry point (exports)
│   ├── types/
│   │   └── index.ts              # All TypeScript interfaces
│   ├── lib/
│   │   ├── config.ts             # AGENT_CONFIG, SCRIPT_TYPE_CHOICES, etc.
│   │   ├── github/
│   │   │   ├── token.ts          # Token handling
│   │   │   ├── rate-limit.ts     # Rate limit parsing
│   │   │   └── client.ts         # API client
│   │   ├── template/
│   │   │   ├── download.ts       # Download from GitHub
│   │   │   ├── extract.ts        # ZIP extraction
│   │   │   └── merge.ts          # JSON deep merge
│   │   ├── tools/
│   │   │   ├── detect.ts         # Tool detection (which/where)
│   │   │   └── git.ts            # Git operations
│   │   └── ui/
│   │       ├── banner.ts         # ASCII banner
│   │       ├── tracker.ts        # StepTracker class
│   │       ├── select.ts         # Interactive selection
│   │       └── console.ts        # Chalk wrappers
│   └── commands/
│       ├── init.ts               # specify init
│       ├── check.ts              # specify check
│       └── version.ts            # specify version
├── tests/
│   ├── setup.ts                  # Test setup (mocks, globals)
│   ├── lib/
│   │   ├── config.test.ts
│   │   ├── github/
│   │   │   ├── token.test.ts
│   │   │   ├── rate-limit.test.ts
│   │   │   └── client.test.ts
│   │   ├── template/
│   │   │   ├── download.test.ts
│   │   │   ├── extract.test.ts
│   │   │   └── merge.test.ts
│   │   ├── tools/
│   │   │   ├── detect.test.ts
│   │   │   └── git.test.ts
│   │   └── ui/
│   │       ├── banner.test.ts
│   │       ├── tracker.test.ts
│   │       └── select.test.ts
│   └── commands/
│       ├── init.test.ts
│       ├── check.test.ts
│       └── version.test.ts
├── bin/
│   └── specify.js                # Executable wrapper
├── package.json
├── tsconfig.json
├── vitest.config.ts
├── .eslintrc.json
├── .prettierrc
└── README.md
```

---

## Phase 1: Port Tests to Vitest (Days 2-4)

**Goal:** Convert all 586 Python acceptance tests to Vitest TypeScript tests.

### 1.1 Test Setup File

```typescript
// tests/setup.ts
import { vi, beforeEach, afterEach } from 'vitest';

// Reset mocks between tests
beforeEach(() => {
  vi.clearAllMocks();
  vi.unstubAllEnvs();
});

afterEach(() => {
  vi.restoreAllMocks();
});

// Global test utilities
export function mockEnv(vars: Record<string, string>): void {
  for (const [key, value] of Object.entries(vars)) {
    vi.stubEnv(key, value);
  }
}

export function clearEnv(...keys: string[]): void {
  for (const key of keys) {
    vi.stubEnv(key, '');
  }
}
```

### 1.2 Port test_agent_config.py → tests/lib/config.test.ts

```typescript
// tests/lib/config.test.ts
import { describe, it, expect } from 'vitest';
import { AGENT_CONFIG, SCRIPT_TYPE_CHOICES, CLAUDE_LOCAL_PATH } from '../../src/lib/config.js';

describe('AGENT_CONFIG', () => {
  describe('Structure', () => {
    it('has exactly 15 agents', () => {
      expect(Object.keys(AGENT_CONFIG)).toHaveLength(15);
    });

    it('all keys are lowercase strings', () => {
      for (const key of Object.keys(AGENT_CONFIG)) {
        expect(key).toBe(key.toLowerCase());
        expect(typeof key).toBe('string');
      }
    });

    it('each agent has exactly 4 fields', () => {
      for (const config of Object.values(AGENT_CONFIG)) {
        expect(Object.keys(config)).toHaveLength(4);
        expect(config).toHaveProperty('name');
        expect(config).toHaveProperty('folder');
        expect(config).toHaveProperty('installUrl');
        expect(config).toHaveProperty('requiresCli');
      }
    });
  });

  describe('Exact Values', () => {
    it('copilot has correct values', () => {
      expect(AGENT_CONFIG.copilot).toEqual({
        name: 'GitHub Copilot',
        folder: '.github/',
        installUrl: null,
        requiresCli: false,
      });
    });

    it('claude has correct values', () => {
      expect(AGENT_CONFIG.claude).toEqual({
        name: 'Claude Code',
        folder: '.claude/',
        installUrl: 'https://docs.anthropic.com/en/docs/claude-code/setup',
        requiresCli: true,
      });
    });

    it('gemini has correct values', () => {
      expect(AGENT_CONFIG.gemini).toEqual({
        name: 'Gemini CLI',
        folder: '.gemini/',
        installUrl: 'https://github.com/google-gemini/gemini-cli',
        requiresCli: true,
      });
    });

    it('cursor-agent has correct values', () => {
      expect(AGENT_CONFIG['cursor-agent']).toEqual({
        name: 'Cursor',
        folder: '.cursor/',
        installUrl: null,
        requiresCli: false,
      });
    });

    it('qwen has correct values', () => {
      expect(AGENT_CONFIG.qwen).toEqual({
        name: 'Qwen Code',
        folder: '.qwen/',
        installUrl: 'https://github.com/QwenLM/qwen-code',
        requiresCli: true,
      });
    });

    it('opencode has correct values', () => {
      expect(AGENT_CONFIG.opencode).toEqual({
        name: 'opencode',
        folder: '.opencode/',
        installUrl: 'https://opencode.ai',
        requiresCli: true,
      });
    });

    it('codex has correct values', () => {
      expect(AGENT_CONFIG.codex).toEqual({
        name: 'Codex CLI',
        folder: '.codex/',
        installUrl: 'https://github.com/openai/codex',
        requiresCli: true,
      });
    });

    it('windsurf has correct values', () => {
      expect(AGENT_CONFIG.windsurf).toEqual({
        name: 'Windsurf',
        folder: '.windsurf/',
        installUrl: null,
        requiresCli: false,
      });
    });

    it('kilocode has correct values', () => {
      expect(AGENT_CONFIG.kilocode).toEqual({
        name: 'Kilo Code',
        folder: '.kilocode/',
        installUrl: null,
        requiresCli: false,
      });
    });

    it('auggie has correct values', () => {
      expect(AGENT_CONFIG.auggie).toEqual({
        name: 'Auggie CLI',
        folder: '.augment/',
        installUrl: 'https://docs.augmentcode.com/cli/setup-auggie/install-auggie-cli',
        requiresCli: true,
      });
    });

    it('codebuddy has correct values', () => {
      expect(AGENT_CONFIG.codebuddy).toEqual({
        name: 'CodeBuddy',
        folder: '.codebuddy/',
        installUrl: 'https://www.codebuddy.ai/cli',
        requiresCli: true,
      });
    });

    it('roo has correct values', () => {
      expect(AGENT_CONFIG.roo).toEqual({
        name: 'Roo Code',
        folder: '.roo/',
        installUrl: null,
        requiresCli: false,
      });
    });

    it('q has correct values', () => {
      expect(AGENT_CONFIG.q).toEqual({
        name: 'Amazon Q Developer CLI',
        folder: '.amazonq/',
        installUrl: 'https://aws.amazon.com/developer/learning/q-developer-cli/',
        requiresCli: true,
      });
    });

    it('amp has correct values', () => {
      expect(AGENT_CONFIG.amp).toEqual({
        name: 'Amp',
        folder: '.agents/',
        installUrl: 'https://ampcode.com/manual#install',
        requiresCli: true,
      });
    });

    it('shai has correct values', () => {
      expect(AGENT_CONFIG.shai).toEqual({
        name: 'SHAI',
        folder: '.shai/',
        installUrl: 'https://github.com/ovh/shai',
        requiresCli: true,
      });
    });
  });

  describe('Folder Naming Mismatches', () => {
    it('auggie folder is .augment/ not .auggie/', () => {
      expect(AGENT_CONFIG.auggie.folder).toBe('.augment/');
    });

    it('q folder is .amazonq/ not .q/', () => {
      expect(AGENT_CONFIG.q.folder).toBe('.amazonq/');
    });

    it('amp folder is .agents/ not .amp/', () => {
      expect(AGENT_CONFIG.amp.folder).toBe('.agents/');
    });

    it('copilot folder is .github/ not .copilot/', () => {
      expect(AGENT_CONFIG.copilot.folder).toBe('.github/');
    });
  });

  describe('Categorization', () => {
    it('IDE-based agents do not require CLI', () => {
      const ideAgents = ['copilot', 'cursor-agent', 'windsurf', 'kilocode', 'roo'] as const;
      for (const key of ideAgents) {
        expect(AGENT_CONFIG[key].requiresCli).toBe(false);
      }
    });

    it('CLI-based agents require CLI', () => {
      const cliAgents = [
        'claude', 'gemini', 'qwen', 'opencode', 'codex',
        'auggie', 'codebuddy', 'q', 'amp', 'shai'
      ] as const;
      for (const key of cliAgents) {
        expect(AGENT_CONFIG[key].requiresCli).toBe(true);
      }
    });
  });

  describe('Folder Format', () => {
    it('all folders start with dot', () => {
      for (const config of Object.values(AGENT_CONFIG)) {
        expect(config.folder).toMatch(/^\./);
      }
    });

    it('all folders end with slash', () => {
      for (const config of Object.values(AGENT_CONFIG)) {
        expect(config.folder).toMatch(/\/$/);
      }
    });

    it('all folders are unique', () => {
      const folders = Object.values(AGENT_CONFIG).map(c => c.folder);
      const uniqueFolders = new Set(folders);
      // Note: Some agents share folders (AGENTS.md)
      expect(uniqueFolders.size).toBeGreaterThanOrEqual(12);
    });
  });

  describe('Complete List', () => {
    it('all 15 agent keys are present', () => {
      const expectedKeys = new Set([
        'copilot', 'claude', 'gemini', 'cursor-agent', 'qwen',
        'opencode', 'codex', 'windsurf', 'kilocode', 'auggie',
        'codebuddy', 'roo', 'q', 'amp', 'shai',
      ]);
      const actualKeys = new Set(Object.keys(AGENT_CONFIG));
      expect(actualKeys).toEqual(expectedKeys);
    });
  });
});

describe('SCRIPT_TYPE_CHOICES', () => {
  it('has exactly two script types', () => {
    expect(Object.keys(SCRIPT_TYPE_CHOICES)).toHaveLength(2);
  });

  it('sh description is exact', () => {
    expect(SCRIPT_TYPE_CHOICES.sh).toBe('POSIX Shell (bash/zsh)');
  });

  it('ps description is exact', () => {
    expect(SCRIPT_TYPE_CHOICES.ps).toBe('PowerShell');
  });

  it('all values are strings', () => {
    for (const value of Object.values(SCRIPT_TYPE_CHOICES)) {
      expect(typeof value).toBe('string');
    }
  });
});

describe('CLAUDE_LOCAL_PATH', () => {
  it('ends with .claude/local/claude', () => {
    expect(CLAUDE_LOCAL_PATH).toMatch(/\.claude[\/\\]local[\/\\]claude$/);
  });

  it('is an absolute path', () => {
    expect(CLAUDE_LOCAL_PATH).toMatch(/^[\/~]|^[A-Z]:\\/);
  });

  it('starts from home directory', () => {
    const { homedir } = require('node:os');
    expect(CLAUDE_LOCAL_PATH.startsWith(homedir())).toBe(true);
  });
});
```

### 1.3 Port test_github_token.py → tests/lib/github/token.test.ts

```typescript
// tests/lib/github/token.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { getGitHubToken, getAuthHeaders } from '../../../src/lib/github/token.js';

describe('getGitHubToken', () => {
  beforeEach(() => {
    vi.unstubAllEnvs();
  });

  describe('Precedence', () => {
    it('returns CLI token when provided', () => {
      vi.stubEnv('GH_TOKEN', 'env-gh-token');
      vi.stubEnv('GITHUB_TOKEN', 'env-github-token');
      expect(getGitHubToken('cli-token')).toBe('cli-token');
    });

    it('falls back to GH_TOKEN when CLI token is empty', () => {
      vi.stubEnv('GH_TOKEN', 'env-gh-token');
      vi.stubEnv('GITHUB_TOKEN', 'env-github-token');
      expect(getGitHubToken('')).toBe('env-gh-token');
      expect(getGitHubToken(undefined)).toBe('env-gh-token');
    });

    it('falls back to GITHUB_TOKEN when GH_TOKEN is unset', () => {
      vi.stubEnv('GH_TOKEN', '');
      vi.stubEnv('GITHUB_TOKEN', 'env-github-token');
      expect(getGitHubToken()).toBe('env-github-token');
    });

    it('returns undefined when no token source is available', () => {
      vi.stubEnv('GH_TOKEN', '');
      vi.stubEnv('GITHUB_TOKEN', '');
      expect(getGitHubToken()).toBeUndefined();
    });
  });

  describe('Sanitization', () => {
    it('trims whitespace from CLI token', () => {
      expect(getGitHubToken('  token-with-spaces  ')).toBe('token-with-spaces');
    });

    it('trims whitespace from env token', () => {
      vi.stubEnv('GH_TOKEN', '  env-token  ');
      expect(getGitHubToken()).toBe('env-token');
    });

    it('strips newlines', () => {
      expect(getGitHubToken('token\n')).toBe('token');
      expect(getGitHubToken('token\r\n')).toBe('token');
    });

    it('empty string returns undefined', () => {
      expect(getGitHubToken('')).toBeUndefined();
    });

    it('whitespace only returns undefined', () => {
      expect(getGitHubToken('   ')).toBeUndefined();
    });

    it('env empty string returns undefined', () => {
      vi.stubEnv('GH_TOKEN', '');
      vi.stubEnv('GITHUB_TOKEN', '');
      expect(getGitHubToken()).toBeUndefined();
    });
  });
});

describe('getAuthHeaders', () => {
  beforeEach(() => {
    vi.unstubAllEnvs();
  });

  it('returns empty object when no token available', () => {
    vi.stubEnv('GH_TOKEN', '');
    vi.stubEnv('GITHUB_TOKEN', '');
    expect(getAuthHeaders()).toEqual({});
  });

  it('returns Bearer header with token', () => {
    const headers = getAuthHeaders('my-token');
    expect(headers).toHaveProperty('Authorization');
    expect(headers.Authorization).toBe('Bearer my-token');
  });

  it('uses Bearer format exactly', () => {
    const headers = getAuthHeaders('test');
    expect(headers.Authorization).toMatch(/^Bearer /);
  });

  it('passes CLI token to token function', () => {
    vi.stubEnv('GH_TOKEN', 'env-token');
    expect(getAuthHeaders('cli-token').Authorization).toBe('Bearer cli-token');
  });
});

describe('Environment Variables', () => {
  it('GH_TOKEN env var name is correct', () => {
    vi.stubEnv('GH_TOKEN', 'test-value');
    expect(process.env.GH_TOKEN).toBe('test-value');
  });

  it('GITHUB_TOKEN env var name is correct', () => {
    vi.stubEnv('GITHUB_TOKEN', 'test-value');
    expect(process.env.GITHUB_TOKEN).toBe('test-value');
  });
});
```

### 1.4 Port test_step_tracker.py → tests/lib/ui/tracker.test.ts

```typescript
// tests/lib/ui/tracker.test.ts
import { describe, it, expect, vi } from 'vitest';
import { StepTracker, StepStatus } from '../../../src/lib/ui/tracker.js';

describe('StepTracker', () => {
  describe('Initialization', () => {
    it('accepts title string', () => {
      const tracker = new StepTracker('Test Title');
      expect(tracker.title).toBe('Test Title');
    });

    it('steps starts empty', () => {
      const tracker = new StepTracker('Test');
      expect(tracker.steps).toHaveLength(0);
    });

    it('status order is defined', () => {
      const statuses: StepStatus[] = ['pending', 'running', 'done', 'error', 'skipped'];
      expect(statuses).toHaveLength(5);
    });
  });

  describe('Add Step', () => {
    it('add creates step with correct structure', () => {
      const tracker = new StepTracker('Test');
      tracker.add('key1', 'Label 1');
      
      expect(tracker.steps).toHaveLength(1);
      expect(tracker.steps[0]).toEqual({
        key: 'key1',
        label: 'Label 1',
        status: 'pending',
        detail: '',
      });
    });

    it('add same key is noop', () => {
      const tracker = new StepTracker('Test');
      tracker.add('key1', 'Label 1');
      tracker.add('key1', 'Different Label');
      
      expect(tracker.steps).toHaveLength(1);
      expect(tracker.steps[0].label).toBe('Label 1');
    });

    it('add multiple steps maintains order', () => {
      const tracker = new StepTracker('Test');
      tracker.add('first', 'First');
      tracker.add('second', 'Second');
      tracker.add('third', 'Third');
      
      expect(tracker.steps.map(s => s.key)).toEqual(['first', 'second', 'third']);
    });
  });

  describe('Status Transitions', () => {
    it('start sets status to running', () => {
      const tracker = new StepTracker('Test');
      tracker.add('key', 'Label');
      tracker.start('key');
      
      expect(tracker.steps[0].status).toBe('running');
    });

    it('complete sets status to done', () => {
      const tracker = new StepTracker('Test');
      tracker.add('key', 'Label');
      tracker.complete('key');
      
      expect(tracker.steps[0].status).toBe('done');
    });

    it('error sets status to error', () => {
      const tracker = new StepTracker('Test');
      tracker.add('key', 'Label');
      tracker.error('key');
      
      expect(tracker.steps[0].status).toBe('error');
    });

    it('skip sets status to skipped', () => {
      const tracker = new StepTracker('Test');
      tracker.add('key', 'Label');
      tracker.skip('key');
      
      expect(tracker.steps[0].status).toBe('skipped');
    });

    it('start with detail sets detail', () => {
      const tracker = new StepTracker('Test');
      tracker.add('key', 'Label');
      tracker.start('key', 'Starting...');
      
      expect(tracker.steps[0].detail).toBe('Starting...');
    });

    it('complete with detail sets detail', () => {
      const tracker = new StepTracker('Test');
      tracker.add('key', 'Label');
      tracker.complete('key', 'Done!');
      
      expect(tracker.steps[0].detail).toBe('Done!');
    });
  });

  describe('Auto Create', () => {
    it('update creates step if not exists', () => {
      const tracker = new StepTracker('Test');
      tracker.complete('new-key', 'auto-created');
      
      expect(tracker.steps).toHaveLength(1);
      expect(tracker.steps[0].key).toBe('new-key');
      expect(tracker.steps[0].status).toBe('done');
    });
  });

  describe('Refresh Callback', () => {
    it('attachRefresh stores callback', () => {
      const tracker = new StepTracker('Test');
      const callback = vi.fn();
      tracker.attachRefresh(callback);
      
      tracker.add('key', 'Label');
      expect(callback).toHaveBeenCalled();
    });

    it('callback triggered on add', () => {
      const tracker = new StepTracker('Test');
      const callback = vi.fn();
      tracker.attachRefresh(callback);
      
      tracker.add('key', 'Label');
      expect(callback).toHaveBeenCalledTimes(1);
    });

    it('callback triggered on status change', () => {
      const tracker = new StepTracker('Test');
      const callback = vi.fn();
      tracker.add('key', 'Label');
      tracker.attachRefresh(callback);
      
      tracker.start('key');
      expect(callback).toHaveBeenCalledTimes(1);
    });

    it('callback exception is ignored', () => {
      const tracker = new StepTracker('Test');
      const callback = vi.fn().mockImplementation(() => {
        throw new Error('Callback error');
      });
      tracker.attachRefresh(callback);
      
      // Should not throw
      expect(() => tracker.add('key', 'Label')).not.toThrow();
    });
  });

  describe('Render', () => {
    it('render returns tree-like structure', () => {
      const tracker = new StepTracker('Test');
      tracker.add('key', 'Label');
      
      const output = tracker.render();
      expect(typeof output).toBe('string');
      expect(output).toContain('Test');
    });

    it('render includes title', () => {
      const tracker = new StepTracker('My Title');
      const output = tracker.render();
      expect(output).toContain('My Title');
    });
  });

  describe('Status Symbols', () => {
    it('done uses green filled circle', () => {
      const tracker = new StepTracker('Test');
      tracker.add('key', 'Label');
      tracker.complete('key');
      const output = tracker.render();
      // Green ● for done
      expect(output).toContain('●');
    });

    it('pending uses dim circle', () => {
      const tracker = new StepTracker('Test');
      tracker.add('key', 'Label');
      const output = tracker.render();
      // Dim ○ for pending
      expect(output).toContain('○');
    });

    it('running uses cyan circle', () => {
      const tracker = new StepTracker('Test');
      tracker.add('key', 'Label');
      tracker.start('key');
      const output = tracker.render();
      // Cyan ○ for running
      expect(output).toContain('○');
    });

    it('error uses red filled circle', () => {
      const tracker = new StepTracker('Test');
      tracker.add('key', 'Label');
      tracker.error('key');
      const output = tracker.render();
      // Red ● for error
      expect(output).toContain('●');
    });

    it('skipped uses yellow circle', () => {
      const tracker = new StepTracker('Test');
      tracker.add('key', 'Label');
      tracker.skip('key');
      const output = tracker.render();
      // Yellow ○ for skipped
      expect(output).toContain('○');
    });
  });

  describe('Detail Formatting', () => {
    it('detail shown in parentheses', () => {
      const tracker = new StepTracker('Test');
      tracker.add('key', 'Label');
      tracker.complete('key', 'details here');
      const output = tracker.render();
      expect(output).toContain('(details here)');
    });

    it('empty detail shows no parentheses', () => {
      const tracker = new StepTracker('Test');
      tracker.add('key', 'Label');
      tracker.complete('key');
      const output = tracker.render();
      expect(output).not.toContain('()');
    });

    it('pending shows dim text', () => {
      const tracker = new StepTracker('Test');
      tracker.add('key', 'Label');
      // Pending status should render label in dim
      const output = tracker.render();
      expect(output).toContain('Label');
    });
  });
});
```

### 1.5 Port test_json_merge.py → tests/lib/template/merge.test.ts

```typescript
// tests/lib/template/merge.test.ts
import { describe, it, expect } from 'vitest';
import { writeFile, readFile, rm, mkdir } from 'node:fs/promises';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { mergeJsonFiles, deepMerge } from '../../../src/lib/template/merge.js';

describe('deepMerge', () => {
  describe('Basic Operations', () => {
    it('returns object', () => {
      const result = deepMerge({}, {});
      expect(typeof result).toBe('object');
    });

    it('adds new keys', () => {
      const result = deepMerge({ existing: 'value' }, { new: 'value' });
      expect(result.existing).toBe('value');
      expect(result.new).toBe('value');
    });

    it('preserves existing keys not in update', () => {
      const result = deepMerge({ keep: 'me' }, { other: 'value' });
      expect(result.keep).toBe('me');
    });

    it('overwrites existing keys from update', () => {
      const result = deepMerge({ key: 'old' }, { key: 'new' });
      expect(result.key).toBe('new');
    });
  });

  describe('Deep Merge', () => {
    it('nested objects are merged', () => {
      const result = deepMerge(
        { outer: { existing: 'value' } },
        { outer: { new: 'value' } }
      );
      expect(result.outer.existing).toBe('value');
      expect(result.outer.new).toBe('value');
    });

    it('deeply nested merge works', () => {
      const result = deepMerge(
        { a: { b: { c: { existing: 'value' } } } },
        { a: { b: { c: { new: 'value' } } } }
      );
      expect(result.a.b.c.existing).toBe('value');
      expect(result.a.b.c.new).toBe('value');
    });
  });

  describe('Arrays', () => {
    it('arrays are replaced not merged', () => {
      const result = deepMerge({ items: [1, 2, 3] }, { items: [4, 5] });
      expect(result.items).toEqual([4, 5]);
    });
  });

  describe('Value Types', () => {
    it('null values can be merged over', () => {
      const result = deepMerge({ key: null }, { key: 'value' });
      expect(result.key).toBe('value');
    });

    it('boolean values merged', () => {
      const result = deepMerge({ enabled: true }, { enabled: false });
      expect(result.enabled).toBe(false);
    });

    it('numeric values merged', () => {
      const result = deepMerge({ count: 42 }, { count: 100 });
      expect(result.count).toBe(100);
    });
  });

  describe('Edge Cases', () => {
    it('empty base returns update', () => {
      const result = deepMerge({}, { new: 'value' });
      expect(result).toEqual({ new: 'value' });
    });

    it('empty update preserves base', () => {
      const result = deepMerge({ existing: 'value' }, {});
      expect(result).toEqual({ existing: 'value' });
    });
  });
});

describe('mergeJsonFiles', () => {
  const testDir = join(tmpdir(), 'specify-test-' + Date.now());

  beforeAll(async () => {
    await mkdir(testDir, { recursive: true });
  });

  afterAll(async () => {
    await rm(testDir, { recursive: true, force: true });
  });

  it('nonexistent file returns update', async () => {
    const result = await mergeJsonFiles(
      join(testDir, 'nonexistent.json'),
      { new: 'value' }
    );
    expect(result).toEqual({ new: 'value' });
  });

  it('invalid JSON file returns update', async () => {
    const path = join(testDir, 'invalid.json');
    await writeFile(path, 'not valid json {{{');
    
    const result = await mergeJsonFiles(path, { new: 'value' });
    expect(result).toEqual({ new: 'value' });
  });

  describe('VS Code Settings Merge', () => {
    it('chat.promptFilesRecommendations merged', async () => {
      const path = join(testDir, 'settings1.json');
      await writeFile(path, JSON.stringify({
        'chat.promptFilesRecommendations': { existing: true }
      }));
      
      const result = await mergeJsonFiles(path, {
        'chat.promptFilesRecommendations': { 'speckit.constitution': true }
      });
      
      expect(result['chat.promptFilesRecommendations'].existing).toBe(true);
      expect(result['chat.promptFilesRecommendations']['speckit.constitution']).toBe(true);
    });

    it('chat.tools.terminal.autoApprove merged', async () => {
      const path = join(testDir, 'settings2.json');
      await writeFile(path, JSON.stringify({
        'chat.tools.terminal.autoApprove': { 'existing/path/': true }
      }));
      
      const result = await mergeJsonFiles(path, {
        'chat.tools.terminal.autoApprove': { '.specify/scripts/bash/': true }
      });
      
      expect(result['chat.tools.terminal.autoApprove']['existing/path/']).toBe(true);
      expect(result['chat.tools.terminal.autoApprove']['.specify/scripts/bash/']).toBe(true);
    });
  });
});
```

### 1.6 Continue Porting All Other Test Files

Follow the same pattern for all remaining test files:

| Python Test | TypeScript Test | Priority |
|-------------|-----------------|----------|
| `test_banner.py` | `tests/lib/ui/banner.test.ts` | P1 |
| `test_rate_limit_parsing.py` | `tests/lib/github/rate-limit.test.ts` | P1 |
| `test_rate_limit_error.py` | `tests/lib/github/rate-limit.test.ts` | P1 |
| `test_tool_detection.py` | `tests/lib/tools/detect.test.ts` | P1 |
| `test_git_operations.py` | `tests/lib/tools/git.test.ts` | P1 |
| `test_template_download.py` | `tests/lib/template/download.test.ts` | P1 |
| `test_template_extraction.py` | `tests/lib/template/extract.test.ts` | P1 |
| `test_interactive_selection.py` | `tests/lib/ui/select.test.ts` | P2 |
| `test_init_command.py` | `tests/commands/init.test.ts` | P2 |
| `test_check_command.py` | `tests/commands/check.test.ts` | P2 |
| `test_version_command.py` | `tests/commands/version.test.ts` | P2 |
| `test_script_permissions.py` | `tests/lib/template/permissions.test.ts` | P2 |
| `test_exit_codes.py` | `tests/commands/exit-codes.test.ts` | P2 |
| `test_error_messages.py` | `tests/lib/errors.test.ts` | P3 |
| `test_platform_compat.py` | `tests/platform.test.ts` | P3 |
| `test_tls_handling.py` | `tests/lib/github/tls.test.ts` | P3 |

---

## Phase 2: Implement Core Config (Day 5)

**Goal:** Pass all config tests.

**Files to create:**
- `src/types/index.ts` - All TypeScript interfaces
- `src/lib/config.ts` - AGENT_CONFIG, SCRIPT_TYPE_CHOICES, CLAUDE_LOCAL_PATH, BANNER

**Validation:** `npm test -- tests/lib/config.test.ts` - must pass all 47 tests

---

## Phase 3: Implement GitHub Module (Days 6-7)

**Goal:** Pass all GitHub-related tests.

**Files to create:**
- `src/lib/github/token.ts` - Token handling
- `src/lib/github/rate-limit.ts` - Rate limit parsing and error formatting
- `src/lib/github/client.ts` - API client for releases

**Validation:** 
- `npm test -- tests/lib/github/` - must pass all 45 tests

---

## Phase 4: Implement Template Module (Days 8-9)

**Goal:** Pass all template tests.

**Files to create:**
- `src/lib/template/download.ts` - Download from GitHub releases
- `src/lib/template/extract.ts` - ZIP extraction with nested directory handling
- `src/lib/template/merge.ts` - JSON deep merge
- `src/lib/template/permissions.ts` - Unix script permissions

**Validation:** 
- `npm test -- tests/lib/template/` - must pass all 58 tests

---

## Phase 5: Implement UI Module (Days 10-11)

**Goal:** Pass all UI tests.

**Files to create:**
- `src/lib/ui/banner.ts` - ASCII banner display
- `src/lib/ui/tracker.ts` - StepTracker class
- `src/lib/ui/select.ts` - Interactive arrow-key selection
- `src/lib/ui/console.ts` - Chalk wrappers for consistent styling

**Validation:** 
- `npm test -- tests/lib/ui/` - must pass all 65 tests

---

## Phase 6: Implement Tools Module (Day 12)

**Goal:** Pass all tool detection tests.

**Files to create:**
- `src/lib/tools/detect.ts` - Tool detection (which/where, Claude special path)
- `src/lib/tools/git.ts` - Git operations (is_git_repo, init_git_repo)

**Validation:** 
- `npm test -- tests/lib/tools/` - must pass all 41 tests

---

## Phase 7: Implement Commands (Days 13-15)

**Goal:** Pass all command tests.

**Files to create:**
- `src/commands/check.ts` - `specify check` command
- `src/commands/version.ts` - `specify version` command
- `src/commands/init.ts` - `specify init` command (largest, most complex)

**Validation:** 
- `npm test -- tests/commands/` - must pass all 93 tests

---

## Phase 8: CLI Wiring & Integration (Day 16)

**Goal:** Wire everything together.

**Files to create:**
- `src/cli.ts` - Commander program definition
- `src/index.ts` - Package exports
- `bin/specify.js` - Executable wrapper

**Validation:** 
- `npm test` - all 586 tests pass
- Manual smoke tests of all commands

---

## Phase 9: Documentation & Polish (Day 17)

**Goal:** Ship-ready package.

**Tasks:**
- Update README.md with Node.js usage
- Add CHANGELOG.md entry
- Verify npm publish works
- Cross-platform testing (Windows, macOS, Linux)

---

## Test-First Workflow Summary

```
For each module:
1. Port Python tests to Vitest TypeScript
2. Run tests (all fail - red)
3. Implement module to pass tests
4. Run tests (all pass - green)
5. Refactor if needed
6. Move to next module
```

---

## Estimated Timeline

| Phase | Days | Cumulative |
|-------|------|------------|
| 0. Setup | 1 | 1 |
| 1. Port Tests | 3 | 4 |
| 2. Config | 1 | 5 |
| 3. GitHub | 2 | 7 |
| 4. Template | 2 | 9 |
| 5. UI | 2 | 11 |
| 6. Tools | 1 | 12 |
| 7. Commands | 3 | 15 |
| 8. CLI Wiring | 1 | 16 |
| 9. Polish | 1 | 17 |

**Total: ~17 working days (3.5 weeks)**

---

## Success Criteria

1. ✅ All 586 tests ported to Vitest TypeScript
2. ✅ All tests pass with Node.js implementation
3. ✅ `npm pack` creates valid package
4. ✅ `npx @specify/cli init my-project --ai copilot` works
5. ✅ Cross-platform: Windows, macOS, Linux
6. ✅ TypeScript strict mode with no errors
7. ✅ ESLint and Prettier pass
