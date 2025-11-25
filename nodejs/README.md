# Specify CLI - Node.js Port

This directory contains the Node.js/TypeScript port of the Specify CLI.

## Overview

The original Python implementation is in `../src/specify_cli/`. This port aims to provide identical functionality using Node.js and TypeScript.

## Getting Started

```bash
# Install dependencies
npm install

# Build the project
npm run build

# Run tests
npm test

# Run the CLI locally
npx . --help
npx . check
npx . init my-project --ai copilot --script sh --no-git
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
