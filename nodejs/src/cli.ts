#!/usr/bin/env node
/**
 * Specify CLI - Main entry point
 * Ported from Python specify_cli/__init__.py
 */

import { Command } from 'commander';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { init } from './commands/init.js';
import { check } from './commands/check.js';
import { version as versionCmd } from './commands/version.js';
import { showBanner } from './lib/ui/banner.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load package.json for version
let packageVersion = '0.0.1';
try {
  const pkgPath = join(__dirname, '..', 'package.json');
  const pkg = JSON.parse(readFileSync(pkgPath, 'utf-8')) as { version: string };
  packageVersion = pkg.version;
} catch {
  // Use default version
}

const program = new Command();

program
  .name('specify')
  .description('Setup tool for Specify spec-driven development projects')
  .version(packageVersion);

program
  .command('init [project-name]')
  .description('Initialize a new Specify project from the latest template')
  .option('--ai <assistant>', 'AI assistant to use: claude, gemini, copilot, cursor-agent, qwen, opencode, codex, windsurf, kilocode, auggie, codebuddy, roo, q, amp, or shai')
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
  console.log("Run 'specify --help' for usage information\n");
} else {
  program.parse();
}
