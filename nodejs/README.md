# Specify CLI - Node.js Port

This directory contains the Node.js/TypeScript port of the Specify CLI.

## Overview

The original Python implementation is in `../src/specify_cli/`. This port provides identical functionality using Node.js and TypeScript.

## Current Status

**127 tests passing** across 8 test files.

### Implemented Features

- ✅ **Configuration**: AGENT_CONFIG (15 agents), SCRIPT_TYPE_CHOICES, CLAUDE_LOCAL_PATH
- ✅ **GitHub Integration**: Token handling, rate limit parsing/formatting
- ✅ **UI Components**: StepTracker, ASCII banner, console utilities
- ✅ **Template Processing**: Deep merge JSON files
- ✅ **Tool Detection**: Check for CLI tools (git, claude, code, etc.)
- ✅ **Git Operations**: Detect git repos, initialize with commit
- ✅ **CLI Commands**: `check`, `version`, `init` (basic)

### In Progress

- 🔄 **Template Download**: Download ZIP from GitHub releases
- 🔄 **Template Extraction**: Unzip and merge with project directory
- 🔄 **Script Permissions**: Set chmod on Unix .sh files
- 🔄 **Interactive Selection**: Arrow key navigation menu

## Getting Started

```bash
# Install dependencies
npm install

# Build the project
npm run build

# Run tests
npm test

# Run the CLI locally
node bin/specify.js --help
node bin/specify.js check
node bin/specify.js version
node bin/specify.js init my-project --ai copilot --no-git
```

## Project Structure

```
nodejs/
├── src/
│   ├── index.ts            # Main exports
│   ├── cli.ts              # CLI wiring with Commander
│   ├── commands/           # CLI commands (init, check, version)
│   ├── lib/
│   │   ├── config.ts       # AGENT_CONFIG and constants
│   │   ├── errors.ts       # Error classes and exit codes
│   │   ├── github/         # GitHub API integration
│   │   ├── template/       # Template download/extract
│   │   ├── tools/          # Tool detection and git ops
│   │   └── ui/             # Banner, tracker, select
│   └── types/              # TypeScript interfaces
├── tests/                  # Vitest test files
├── bin/                    # Executable entry point
├── package.json
├── tsconfig.json
└── vitest.config.ts
```

## Development

See the [Implementation Checklist](../docs/implementation-checklist.md) for detailed progress tracking.

## Testing

Tests are ported from the Python acceptance tests in `../tests/acceptance/`. Run with:

```bash
npm test                    # Run all tests
npm run test:watch          # Watch mode
npm run test:coverage       # With coverage report
```

## Reference

- [Original Python Source](../src/specify_cli/__init__.py)
- [Copilot Instructions](../.github/copilot-instructions.md)
- [Implementation Checklist](../docs/implementation-checklist.md)
