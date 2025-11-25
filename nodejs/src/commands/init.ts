/**
 * Init command - initialize a new Specify project
 * Ported from Python specify_cli/__init__.py
 */

import { existsSync, readdirSync, mkdirSync } from 'fs';
import { join, resolve, basename } from 'path';
import chalk from 'chalk';
import { showBanner } from '../lib/ui/banner.js';
import { StepTracker } from '../lib/ui/tracker.js';
import { AGENT_CONFIG, SCRIPT_TYPE_CHOICES, getDefaultScriptType } from '../lib/config.js';
import { checkTool } from '../lib/tools/detect.js';
import { initGitRepo, isGitRepo } from '../lib/tools/git.js';
import type { InitOptions } from '../types/index.js';

/**
 * Initialize a new Specify project from the latest template.
 */
export async function init(
  projectName: string | undefined,
  options: InitOptions
): Promise<void> {
  showBanner();

  // Handle "." as --here flag
  if (projectName === '.') {
    options.here = true;
    projectName = undefined;
  }

  // Determine project path
  let projectPath: string;
  if (options.here) {
    projectPath = process.cwd();
    projectName = basename(projectPath);
  } else if (projectName) {
    projectPath = resolve(projectName);
  } else {
    console.log(chalk.red('Error:') + ' Please provide a project name or use --here');
    console.log('');
    console.log('Usage: specify init <project-name>');
    console.log('       specify init --here');
    process.exit(1);
  }

  // Validate project directory
  if (!options.here && existsSync(projectPath)) {
    const contents = readdirSync(projectPath);
    if (contents.length > 0 && !options.force) {
      console.log(chalk.yellow('Warning:') + ` Directory '${projectPath}' is not empty.`);
      console.log('Use --force to proceed anyway, or choose a different directory.');
      process.exit(1);
    }
  }

  // Create project directory if needed
  if (!existsSync(projectPath)) {
    mkdirSync(projectPath, { recursive: true });
  }

  // Determine AI assistant
  let selectedAi = options.ai;
  if (!selectedAi) {
    // In the full implementation, this would be interactive selection
    // For now, default to copilot
    selectedAi = 'copilot';
    console.log(chalk.cyan('Note:') + ' Defaulting to copilot. Use --ai <name> to specify an AI assistant.');
  }

  // Validate AI assistant
  if (!AGENT_CONFIG[selectedAi]) {
    console.log(chalk.red('Error:') + ` Unknown AI assistant '${selectedAi}'.`);
    console.log('Valid options: ' + Object.keys(AGENT_CONFIG).join(', '));
    process.exit(1);
  }

  const agentConfig = AGENT_CONFIG[selectedAi]!;

  // Check if agent CLI is required
  if (agentConfig.requiresCli && !options.ignoreAgentTools) {
    if (!checkTool(selectedAi)) {
      console.log(chalk.yellow('Warning:') + ` ${agentConfig.name} CLI is not installed.`);
      if (agentConfig.installUrl) {
        console.log(`Install from: ${agentConfig.installUrl}`);
      }
      console.log('Use --ignore-agent-tools to proceed anyway.');
      process.exit(1);
    }
  }

  // Determine script type
  let scriptType: string = options.script || getDefaultScriptType();

  // Validate script type
  if (!SCRIPT_TYPE_CHOICES[scriptType]) {
    console.log(chalk.red('Error:') + ` Unknown script type '${scriptType}'.`);
    console.log('Valid options: ' + Object.keys(SCRIPT_TYPE_CHOICES).join(', '));
    process.exit(1);
  }

  // Initialize step tracker
  const tracker = new StepTracker(`Initialize ${projectName}`);

  tracker.add('download', 'Download template');
  tracker.add('extract', 'Extract files');
  if (process.platform !== 'win32' && scriptType === 'sh') {
    tracker.add('chmod', 'Set script permissions');
  }
  if (!options.noGit) {
    tracker.add('git', 'Initialize git repository');
  }

  console.log();
  console.log(chalk.cyan('Project Configuration:'));
  console.log(`  Name: ${chalk.green(projectName)}`);
  console.log(`  Path: ${chalk.green(projectPath)}`);
  console.log(`  AI Assistant: ${chalk.green(agentConfig.name)}`);
  console.log(`  Script Type: ${chalk.green(SCRIPT_TYPE_CHOICES[scriptType])}`);
  console.log();

  // Download template
  tracker.start('download', 'fetching from GitHub');
  try {
    // TODO: Implement actual template download from GitHub releases
    // For now, simulate the process
    tracker.complete('download', 'done');
  } catch (error) {
    tracker.error('download', String(error));
    console.log(tracker.render());
    process.exit(1);
  }

  // Extract files
  tracker.start('extract', 'extracting to project');
  try {
    // TODO: Implement actual ZIP extraction
    tracker.complete('extract', 'done');
  } catch (error) {
    tracker.error('extract', String(error));
    console.log(tracker.render());
    process.exit(1);
  }

  // Set script permissions (Unix only)
  if (process.platform !== 'win32' && scriptType === 'sh') {
    tracker.start('chmod', 'setting permissions');
    try {
      // TODO: Implement chmod for .sh files
      tracker.complete('chmod', 'done');
    } catch (error) {
      tracker.error('chmod', String(error));
    }
  }

  // Initialize git repository
  if (!options.noGit) {
    tracker.start('git', 'initializing repository');
    if (isGitRepo(projectPath)) {
      tracker.skip('git', 'already a git repository');
    } else {
      const result = initGitRepo(projectPath, true);
      if (result.success) {
        tracker.complete('git', 'done');
      } else {
        tracker.error('git', result.error || 'failed');
      }
    }
  }

  console.log(tracker.render());
  console.log();

  // Success message
  console.log(chalk.green('✓') + ' Project initialized successfully!');
  console.log();
  console.log('Next steps:');
  console.log(`  ${chalk.cyan('cd')} ${projectName}`);
  console.log(`  ${chalk.cyan('code')} .`);
  console.log();
}
