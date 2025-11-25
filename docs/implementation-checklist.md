# Implementation Checklist: Test-Driven Node.js Port of Specify CLI

**Objective:** Port the Python Specify CLI (~1,360 lines) to a pure Node.js/TypeScript npm package using existing acceptance tests as behavioral contracts.

**Approach:** Test-Driven Development - port all tests first, then implement modules to pass them.

> **IMPORTANT:** All Node.js/TypeScript code MUST be placed in the `nodejs/` folder at the project root. This keeps the Python source intact while developing the port.

---

## Quick Reference

| Metric | Value |
|--------|-------|
| Python source lines | ~1,360 |
| Acceptance tests | 586 (29 test files) |
| Target Node.js version | ≥18.0.0 |
| Estimated effort | ~17 days |

---

## Phase 0: Project Setup

### 0.1 Package Initialization

- [ ] Create `nodejs/` directory at project root
- [ ] Run `npm init -y` in `nodejs/` folder
- [ ] Update `nodejs/package.json` with:
  - [ ] `"name": "@specify/cli"`
  - [ ] `"version": "0.0.1"`
  - [ ] `"type": "module"`
  - [ ] `"main": "dist/index.js"`
  - [ ] `"types": "dist/index.d.ts"`
  - [ ] `"bin": { "specify": "./bin/specify.js" }`
  - [ ] `"engines": { "node": ">=18.0.0" }`
  - [ ] All npm scripts (build, dev, test, test:watch, test:coverage, lint, format, typecheck)

### 0.2 Install Dependencies

- [ ] Production dependencies:
  - [ ] `commander@^12.1.0` - CLI framework
  - [ ] `chalk@^5.3.0` - Terminal colors
  - [ ] `ora@^8.0.1` - Spinners
  - [ ] `@inquirer/prompts@^5.0.0` - Interactive prompts
  - [ ] `cli-table3@^0.6.5` - Table output
  - [ ] `node-fetch@^3.3.2` - HTTP client
  - [ ] `adm-zip@^0.5.14` - ZIP extraction
  - [ ] `fs-extra@^11.2.0` - Enhanced fs operations
  - [ ] `execa@^9.3.0` - Better child_process
  - [ ] `env-paths@^3.0.0` - Platform directories

- [ ] Dev dependencies:
  - [ ] `typescript@^5.5.0`
  - [ ] `@types/node@^20.14.0`
  - [ ] `@types/fs-extra@^11.0.4`
  - [ ] `@types/adm-zip@^0.5.5`
  - [ ] `vitest@^1.6.0`
  - [ ] `@vitest/coverage-v8@^1.6.0`
  - [ ] `eslint@^9.5.0`
  - [ ] `@typescript-eslint/eslint-plugin@^7.13.0`
  - [ ] `@typescript-eslint/parser@^7.13.0`
  - [ ] `prettier@^3.3.2`
  - [ ] `tsx@^4.15.0`

### 0.3 Configuration Files

- [ ] Create `nodejs/tsconfig.json`:
  ```json
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
      "resolveJsonModule": true,
      "isolatedModules": true
    },
    "include": ["src/**/*"],
    "exclude": ["node_modules", "dist", "tests"]
  }
  ```

- [ ] Create `nodejs/vitest.config.ts`:
  ```typescript
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

- [ ] Create `nodejs/.eslintrc.json`
- [ ] Create `nodejs/.prettierrc`
- [ ] Create `nodejs/.gitignore` (add node_modules, dist, coverage)

### 0.4 Directory Structure

- [ ] Create `nodejs/src/` directory
- [ ] Create `nodejs/src/types/` directory
- [ ] Create `nodejs/src/lib/` directory
- [ ] Create `nodejs/src/lib/github/` directory
- [ ] Create `nodejs/src/lib/template/` directory
- [ ] Create `nodejs/src/lib/tools/` directory
- [ ] Create `nodejs/src/lib/ui/` directory
- [ ] Create `nodejs/src/commands/` directory
- [ ] Create `nodejs/tests/` directory
- [ ] Create `nodejs/tests/lib/` directory
- [ ] Create `nodejs/tests/lib/github/` directory
- [ ] Create `nodejs/tests/lib/template/` directory
- [ ] Create `nodejs/tests/lib/tools/` directory
- [ ] Create `nodejs/tests/lib/ui/` directory
- [ ] Create `nodejs/tests/commands/` directory
- [ ] Create `nodejs/bin/` directory

### 0.5 Entry Points

- [ ] Create `nodejs/bin/specify.js`:
  ```javascript
  #!/usr/bin/env node
  import '../dist/cli.js';
  ```

- [ ] Create `nodejs/tests/setup.ts` with mock utilities

### 0.6 Verification

- [ ] Run `cd nodejs && npm install` - succeeds
- [ ] Run `npm run typecheck` - succeeds (empty src)
- [ ] Run `npm test` - succeeds (no tests yet)

### 0.7 Git Checkpoint

- [ ] `git add .`
- [ ] `git commit -m "chore: initialize Node.js project structure"`
- [ ] `git push origin main`

---

## Phase 1: Port Tests to Vitest

### 1.1 Test Setup (nodejs/tests/setup.ts)

- [ ] Create test setup file with:
  - [ ] `vi.clearAllMocks()` in beforeEach
  - [ ] `vi.unstubAllEnvs()` in beforeEach
  - [ ] `vi.restoreAllMocks()` in afterEach
  - [ ] `mockEnv()` helper function
  - [ ] `clearEnv()` helper function

### 1.2 Port test_agent_config.py → nodejs/tests/lib/config.test.ts

Python tests to port:
- [ ] `test_agent_config_has_15_agents` - exactly 15 agents
- [ ] `test_all_keys_are_lowercase` - all keys lowercase
- [ ] `test_each_agent_has_4_fields` - name, folder, installUrl, requiresCli
- [ ] `test_copilot_exact_values` - copilot config values
- [ ] `test_claude_exact_values` - claude config values
- [ ] `test_gemini_exact_values` - gemini config values
- [ ] `test_cursor_agent_exact_values` - cursor-agent config values
- [ ] `test_qwen_exact_values` - qwen config values
- [ ] `test_opencode_exact_values` - opencode config values
- [ ] `test_codex_exact_values` - codex config values
- [ ] `test_windsurf_exact_values` - windsurf config values
- [ ] `test_kilocode_exact_values` - kilocode config values
- [ ] `test_auggie_exact_values` - auggie config values (folder is .augment/)
- [ ] `test_codebuddy_exact_values` - codebuddy config values
- [ ] `test_roo_exact_values` - roo config values
- [ ] `test_q_exact_values` - q config values (folder is .amazonq/)
- [ ] `test_amp_exact_values` - amp config values (folder is .agents/)
- [ ] `test_shai_exact_values` - shai config values
- [ ] `test_ide_agents_no_cli` - copilot, cursor-agent, windsurf, kilocode, roo have requiresCli=false
- [ ] `test_cli_agents_require_cli` - claude, gemini, qwen, opencode, codex, auggie, codebuddy, q, amp, shai have requiresCli=true
- [ ] `test_all_folders_start_with_dot` - all folders match /^\./
- [ ] `test_all_folders_end_with_slash` - all folders match /\/$/
- [ ] `test_folders_mostly_unique` - at least 12 unique folders
- [ ] `test_all_15_keys_present` - exact set of keys

### 1.3 Port test_script_types.py → nodejs/tests/lib/config.test.ts

- [ ] `test_script_type_choices_has_two` - sh and ps
- [ ] `test_sh_description_exact` - "POSIX Shell (bash/zsh)"
- [ ] `test_ps_description_exact` - "PowerShell"
- [ ] `test_all_values_are_strings`

### 1.4 Port test_claude_path.py → nodejs/tests/lib/config.test.ts

- [ ] `test_claude_local_path_ends_correctly` - ends with .claude/local/claude
- [ ] `test_claude_local_path_is_absolute` - starts with / or ~ or drive letter
- [ ] `test_claude_local_path_from_homedir` - starts with os.homedir()

### 1.5 Port test_github_token.py → nodejs/tests/lib/github/token.test.ts

- [ ] `test_cli_token_takes_precedence` - CLI arg wins over env
- [ ] `test_gh_token_fallback` - GH_TOKEN when no CLI arg
- [ ] `test_github_token_fallback` - GITHUB_TOKEN when no GH_TOKEN
- [ ] `test_no_token_returns_undefined` - undefined when nothing set
- [ ] `test_trims_whitespace_cli` - trims CLI token
- [ ] `test_trims_whitespace_env` - trims env token
- [ ] `test_strips_newlines` - strips \n and \r\n
- [ ] `test_empty_string_undefined` - "" returns undefined
- [ ] `test_whitespace_only_undefined` - "   " returns undefined
- [ ] `test_auth_headers_empty_no_token` - {} when no token
- [ ] `test_auth_headers_bearer_format` - "Bearer {token}"
- [ ] `test_auth_headers_cli_precedence` - CLI token in headers

### 1.6 Port test_rate_limit_parsing.py → nodejs/tests/lib/github/rate-limit.test.ts

- [ ] `test_parses_limit_header` - X-RateLimit-Limit
- [ ] `test_parses_remaining_header` - X-RateLimit-Remaining
- [ ] `test_parses_reset_header` - X-RateLimit-Reset (epoch to Date)
- [ ] `test_parses_retry_after_header` - Retry-After seconds
- [ ] `test_handles_missing_headers` - graceful when headers absent
- [ ] `test_handles_invalid_values` - graceful on non-numeric

### 1.7 Port test_rate_limit_error.py → nodejs/tests/lib/github/rate-limit.test.ts

- [ ] `test_formats_status_code` - includes status code
- [ ] `test_formats_url` - includes URL
- [ ] `test_includes_rate_limit_info` - includes limit/remaining/reset
- [ ] `test_includes_troubleshooting_tips` - includes GH_TOKEN suggestion
- [ ] `test_mentions_5000_vs_60` - mentions authenticated rate limit

### 1.8 Port test_step_tracker.py → nodejs/tests/lib/ui/tracker.test.ts

- [ ] `test_init_accepts_title` - title stored
- [ ] `test_init_steps_empty` - steps array empty
- [ ] `test_status_order_defined` - 5 statuses
- [ ] `test_add_creates_step` - correct structure {key, label, status, detail}
- [ ] `test_add_same_key_noop` - no duplicate keys
- [ ] `test_add_maintains_order` - insertion order preserved
- [ ] `test_start_sets_running` - status = "running"
- [ ] `test_complete_sets_done` - status = "done"
- [ ] `test_error_sets_error` - status = "error"
- [ ] `test_skip_sets_skipped` - status = "skipped"
- [ ] `test_start_with_detail` - detail set
- [ ] `test_complete_with_detail` - detail set
- [ ] `test_update_creates_if_missing` - auto-creates step
- [ ] `test_attach_refresh_stores_callback` - callback stored
- [ ] `test_callback_triggered_on_add` - callback called
- [ ] `test_callback_triggered_on_status_change` - callback called
- [ ] `test_callback_exception_ignored` - errors swallowed
- [ ] `test_render_returns_string` - string output
- [ ] `test_render_includes_title` - title in output
- [ ] `test_done_uses_filled_circle` - ● symbol
- [ ] `test_pending_uses_dim_circle` - ○ symbol (dim)
- [ ] `test_running_uses_cyan_circle` - ○ symbol (cyan)
- [ ] `test_error_uses_red_circle` - ● symbol (red)
- [ ] `test_skipped_uses_yellow_circle` - ○ symbol (yellow)
- [ ] `test_detail_in_parentheses` - (detail) format
- [ ] `test_empty_detail_no_parentheses` - no () when empty

### 1.9 Port test_json_merge.py → nodejs/tests/lib/template/merge.test.ts

- [ ] `test_deep_merge_returns_object`
- [ ] `test_adds_new_keys`
- [ ] `test_preserves_existing_keys`
- [ ] `test_overwrites_existing_keys`
- [ ] `test_nested_objects_merged`
- [ ] `test_deeply_nested_merge`
- [ ] `test_arrays_replaced_not_merged`
- [ ] `test_null_values_merged`
- [ ] `test_boolean_values_merged`
- [ ] `test_numeric_values_merged`
- [ ] `test_empty_base_returns_update`
- [ ] `test_empty_update_preserves_base`
- [ ] `test_nonexistent_file_returns_update`
- [ ] `test_invalid_json_returns_update`
- [ ] `test_vscode_prompt_recommendations_merged`
- [ ] `test_vscode_terminal_auto_approve_merged`

### 1.10 Port test_banner.py → nodejs/tests/lib/ui/banner.test.ts

- [ ] `test_banner_has_6_lines` - ASCII art has 6 lines
- [ ] `test_banner_contains_specify` - "SPECIFY" appears
- [ ] `test_tagline_exact` - "GitHub Spec Kit - Spec-Driven Development Toolkit"
- [ ] `test_show_banner_no_error` - function runs without error

### 1.11 Port test_tool_detection.py → nodejs/tests/lib/tools/detect.test.ts

- [ ] `test_detects_git` - git found (CI)
- [ ] `test_detects_node` - node found
- [ ] `test_nonexistent_tool_returns_false` - fake tool not found
- [ ] `test_claude_special_path_checked` - ~/.claude/local/claude checked first
- [ ] `test_tracker_updated_on_found` - tracker.complete() called
- [ ] `test_tracker_updated_on_not_found` - tracker.error() called

### 1.12 Port test_git_operations.py → nodejs/tests/lib/tools/git.test.ts

- [ ] `test_is_git_repo_true` - true in git repo
- [ ] `test_is_git_repo_false` - false in non-repo
- [ ] `test_init_git_repo_creates_repo` - git init succeeds
- [ ] `test_init_git_repo_commits` - initial commit made
- [ ] `test_init_git_repo_returns_success` - (true, null) on success
- [ ] `test_init_git_repo_returns_error` - (false, error) on failure

### 1.13 Port test_template_download.py → nodejs/tests/lib/template/download.test.ts

- [ ] `test_fetches_release_info` - calls GitHub API
- [ ] `test_finds_matching_asset` - pattern spec-kit-template-{ai}-{script}
- [ ] `test_downloads_zip` - writes file to disk
- [ ] `test_returns_metadata` - filename, size, release, assetUrl
- [ ] `test_handles_rate_limit` - throws RateLimitError
- [ ] `test_handles_404` - handles missing release
- [ ] `test_respects_github_token` - Authorization header sent

### 1.14 Port test_template_extraction.py → nodejs/tests/lib/template/extract.test.ts

- [ ] `test_extracts_to_new_directory`
- [ ] `test_flattens_nested_directory` - single top-level dir flattened
- [ ] `test_merges_into_existing_directory` - --here mode
- [ ] `test_merges_vscode_settings` - settings.json merged not replaced
- [ ] `test_removes_zip_after_extraction` - cleanup

### 1.15 Port test_script_permissions.py → nodejs/tests/lib/template/permissions.test.ts

- [ ] `test_sets_execute_bit_on_unix` - chmod on .sh files
- [ ] `test_skips_on_windows` - no-op on Windows
- [ ] `test_only_processes_sh_files` - .sh extension only
- [ ] `test_checks_shebang` - only files starting with #!
- [ ] `test_handles_missing_scripts_dir` - graceful when no scripts

### 1.16 Port test_interactive_selection.py → nodejs/tests/lib/ui/select.test.ts

- [ ] `test_returns_selected_key`
- [ ] `test_default_key_preselected`
- [ ] `test_up_arrow_navigation`
- [ ] `test_down_arrow_navigation`
- [ ] `test_enter_confirms`
- [ ] `test_escape_exits`
- [ ] `test_ctrl_c_raises_interrupt`

### 1.17 Port test_check_command.py → nodejs/tests/commands/check.test.ts

- [ ] `test_shows_banner`
- [ ] `test_checks_git`
- [ ] `test_checks_each_cli_agent` - claude, gemini, qwen, etc.
- [ ] `test_skips_ide_agents` - copilot, cursor-agent, windsurf, etc.
- [ ] `test_checks_vscode`
- [ ] `test_uses_step_tracker`

### 1.18 Port test_version_command.py → nodejs/tests/commands/version.test.ts

- [ ] `test_shows_cli_version` - from package.json
- [ ] `test_shows_template_version` - from GitHub API
- [ ] `test_shows_node_version`
- [ ] `test_shows_platform`
- [ ] `test_shows_architecture`

### 1.19 Port test_init_command.py → nodejs/tests/commands/init.test.ts

- [ ] `test_creates_project_directory`
- [ ] `test_downloads_template`
- [ ] `test_extracts_template`
- [ ] `test_initializes_git` - unless --no-git
- [ ] `test_here_flag_current_dir` - --here uses cwd
- [ ] `test_dot_as_here` - "." treated as --here
- [ ] `test_force_skips_confirmation` - --force on non-empty
- [ ] `test_ai_option_selects_agent` - --ai copilot
- [ ] `test_script_option_selects_type` - --script sh/ps
- [ ] `test_shows_completion_message`
- [ ] `test_codex_home_message` - special message for codex
- [ ] `test_branch_name_limit_244` - truncates at 244 bytes

### 1.20 Port test_exit_codes.py → nodejs/tests/commands/exit-codes.test.ts

- [ ] `test_success_is_0`
- [ ] `test_general_error_is_1`
- [ ] `test_missing_dependency_is_2`
- [ ] `test_invalid_argument_is_3`
- [ ] `test_network_error_is_4`
- [ ] `test_filesystem_error_is_5`
- [ ] `test_user_cancelled_is_130`

### 1.21 Port test_error_messages.py → nodejs/tests/lib/errors.test.ts

- [ ] `test_error_includes_message`
- [ ] `test_error_includes_code`
- [ ] `test_network_error_includes_status`
- [ ] `test_rate_limit_error_includes_reset_time`

### 1.22 Port test_platform_compat.py → nodejs/tests/platform.test.ts

- [ ] `test_windows_default_script_ps`
- [ ] `test_unix_default_script_sh`
- [ ] `test_uses_where_on_windows` - where instead of which
- [ ] `test_uses_which_on_unix`

### 1.23 Port test_tls_handling.py → nodejs/tests/lib/github/tls.test.ts

- [ ] `test_uses_system_certificates`
- [ ] `test_skip_tls_option` - --skip-tls flag

### 1.24 Port Shell Script Tests (keep as reference only)

These test the shell scripts that remain in the template:
- [ ] Verify `test_shell_common.py` documents common.sh behavior
- [ ] Verify `test_shell_check_prereqs.py` documents check-prerequisites.sh behavior
- [ ] Verify `test_shell_create_feature.py` documents create-new-feature.sh behavior
- [ ] Verify `test_shell_setup_plan.py` documents setup-plan.sh behavior
- [ ] Verify `test_shell_update_agent.py` documents update-agent-context.sh behavior

### 1.25 Verification

- [ ] Run `npm test` - all tests fail (RED)
- [ ] Count total test cases - should be ~586

### 1.26 Git Checkpoint

- [ ] `git add .`
- [ ] `git commit -m "test: port all acceptance tests to Vitest (RED phase)"`
- [ ] `git push origin main`

---

## Phase 2: Implement Core Config

### 2.1 Create Types (nodejs/src/types/index.ts)

- [ ] Define `AgentConfig` interface:
  ```typescript
  interface AgentConfig {
    name: string;
    folder: string;
    installUrl: string | null;
    requiresCli: boolean;
  }
  ```
- [ ] Define `AgentKey` type (union of all 15 keys)
- [ ] Define `ScriptType` type: `'sh' | 'ps'`
- [ ] Define `StepStatus` type: `'pending' | 'running' | 'done' | 'error' | 'skipped'`
- [ ] Define `Step` interface
- [ ] Define `ErrorCode` const object
- [ ] Export all types

### 2.2 Create Config (nodejs/src/lib/config.ts)

- [ ] Export `AGENT_CONFIG` with all 15 agents (use `as const`):
  - [ ] copilot: { name: "GitHub Copilot", folder: ".github/", installUrl: null, requiresCli: false }
  - [ ] claude: { name: "Claude Code", folder: ".claude/", installUrl: "https://docs.anthropic.com/en/docs/claude-code/setup", requiresCli: true }
  - [ ] gemini: { name: "Gemini CLI", folder: ".gemini/", installUrl: "https://github.com/google-gemini/gemini-cli", requiresCli: true }
  - [ ] cursor-agent: { name: "Cursor", folder: ".cursor/", installUrl: null, requiresCli: false }
  - [ ] qwen: { name: "Qwen Code", folder: ".qwen/", installUrl: "https://github.com/QwenLM/qwen-code", requiresCli: true }
  - [ ] opencode: { name: "opencode", folder: ".opencode/", installUrl: "https://opencode.ai", requiresCli: true }
  - [ ] codex: { name: "Codex CLI", folder: ".codex/", installUrl: "https://github.com/openai/codex", requiresCli: true }
  - [ ] windsurf: { name: "Windsurf", folder: ".windsurf/", installUrl: null, requiresCli: false }
  - [ ] kilocode: { name: "Kilo Code", folder: ".kilocode/", installUrl: null, requiresCli: false }
  - [ ] auggie: { name: "Auggie CLI", folder: ".augment/", installUrl: "https://docs.augmentcode.com/cli/setup-auggie/install-auggie-cli", requiresCli: true }
  - [ ] codebuddy: { name: "CodeBuddy", folder: ".codebuddy/", installUrl: "https://www.codebuddy.ai/cli", requiresCli: true }
  - [ ] roo: { name: "Roo Code", folder: ".roo/", installUrl: null, requiresCli: false }
  - [ ] q: { name: "Amazon Q Developer CLI", folder: ".amazonq/", installUrl: "https://aws.amazon.com/developer/learning/q-developer-cli/", requiresCli: true }
  - [ ] amp: { name: "Amp", folder: ".agents/", installUrl: "https://ampcode.com/manual#install", requiresCli: true }
  - [ ] shai: { name: "SHAI", folder: ".shai/", installUrl: "https://github.com/ovh/shai", requiresCli: true }

- [ ] Export `SCRIPT_TYPE_CHOICES`:
  ```typescript
  export const SCRIPT_TYPE_CHOICES = {
    sh: 'POSIX Shell (bash/zsh)',
    ps: 'PowerShell',
  } as const;
  ```

- [ ] Export `CLAUDE_LOCAL_PATH`:
  ```typescript
  import { homedir } from 'node:os';
  import { join } from 'node:path';
  export const CLAUDE_LOCAL_PATH = join(homedir(), '.claude', 'local', 'claude');
  ```

- [ ] Export `BANNER` (6-line ASCII art)
- [ ] Export `TAGLINE` ("GitHub Spec Kit - Spec-Driven Development Toolkit")

### 2.3 Verification

- [ ] Run `npm test -- nodejs/tests/lib/config.test.ts`
- [ ] All 47+ config tests pass (GREEN)

### 2.4 Git Checkpoint

- [ ] `git add .`
- [ ] `git commit -m "feat: implement core config module"`
- [ ] `git push origin main`

---

## Phase 3: Implement GitHub Module

### 3.1 Token Handling (nodejs/src/lib/github/token.ts)

- [ ] Implement `getGitHubToken(cliToken?: string): string | undefined`
  - [ ] Return cliToken if non-empty after trim
  - [ ] Fall back to process.env.GH_TOKEN
  - [ ] Fall back to process.env.GITHUB_TOKEN
  - [ ] Return undefined if all empty
  - [ ] Trim and strip newlines

- [ ] Implement `getAuthHeaders(cliToken?: string): Record<string, string>`
  - [ ] Return `{}` if no token
  - [ ] Return `{ Authorization: 'Bearer {token}' }` if token exists

### 3.2 Rate Limit (nodejs/src/lib/github/rate-limit.ts)

- [ ] Implement `RateLimitInfo` interface
- [ ] Implement `parseRateLimitHeaders(headers: Headers): RateLimitInfo`
  - [ ] Parse X-RateLimit-Limit
  - [ ] Parse X-RateLimit-Remaining
  - [ ] Parse X-RateLimit-Reset (epoch → Date)
  - [ ] Parse Retry-After

- [ ] Implement `formatRateLimitError(status: number, headers: Headers, url: string): string`
  - [ ] Include status code and URL
  - [ ] Include rate limit info if available
  - [ ] Include troubleshooting tips
  - [ ] Mention 5,000 vs 60 rate limit difference

### 3.3 API Client (nodejs/src/lib/github/client.ts)

- [ ] Implement `GitHubRelease` interface
- [ ] Implement `ReleaseAsset` interface
- [ ] Implement `fetchLatestRelease(options?: { token?: string }): Promise<GitHubRelease>`
- [ ] Implement `findTemplateAsset(release: GitHubRelease, ai: string, script: string): ReleaseAsset | null`

### 3.4 Verification

- [ ] Run `npm test -- nodejs/tests/lib/github/`
- [ ] All 45+ GitHub tests pass (GREEN)

### 3.5 Git Checkpoint

- [ ] `git add .`
- [ ] `git commit -m "feat: implement GitHub API module (token, rate-limit, client)"`
- [ ] `git push origin main`

---

## Phase 4: Implement Template Module

### 4.1 Download (nodejs/src/lib/template/download.ts)

- [ ] Implement `DownloadOptions` interface
- [ ] Implement `DownloadResult` interface
- [ ] Implement `downloadTemplate(ai: string, script: string, destDir: string, options?: DownloadOptions): Promise<DownloadResult>`
  - [ ] Fetch release info from GitHub API
  - [ ] Find matching asset
  - [ ] Download ZIP with streaming
  - [ ] Return { zipPath, metadata }
  - [ ] Handle rate limiting
  - [ ] Support progress callback

### 4.2 Extraction (nodejs/src/lib/template/extract.ts)

- [ ] Implement `ExtractOptions` interface
- [ ] Implement `extractTemplate(zipPath: string, destPath: string, options?: ExtractOptions): Promise<void>`
  - [ ] Extract ZIP contents
  - [ ] Flatten nested directory if single top-level
  - [ ] Merge existing directories in --here mode
  - [ ] Call merge for .vscode/settings.json
  - [ ] Clean up ZIP after extraction

### 4.3 JSON Merge (nodejs/src/lib/template/merge.ts)

- [ ] Implement `deepMerge<T>(base: T, update: T): T`
  - [ ] Add new keys
  - [ ] Preserve existing keys not in update
  - [ ] Overwrite existing keys from update
  - [ ] Recursively merge nested objects
  - [ ] Replace arrays (not merge)

- [ ] Implement `mergeJsonFiles(existingPath: string, newContent: object): Promise<object>`
  - [ ] Read existing file
  - [ ] Handle missing/invalid file
  - [ ] Call deepMerge
  - [ ] Return merged content

### 4.4 Permissions (nodejs/src/lib/template/permissions.ts)

- [ ] Implement `ensureExecutableScripts(projectPath: string, tracker?: StepTracker): Promise<void>`
  - [ ] Skip on Windows (os.platform() === 'win32')
  - [ ] Find .sh files under .specify/scripts/
  - [ ] Check for shebang (#!)
  - [ ] Set execute bit (chmod)
  - [ ] Update tracker if provided

### 4.5 Verification

- [ ] Run `npm test -- nodejs/tests/lib/template/`
- [ ] All 58+ template tests pass (GREEN)

### 4.6 Git Checkpoint

- [ ] `git add .`
- [ ] `git commit -m "feat: implement template module (download, extract, merge, permissions)"`
- [ ] `git push origin main`

---

## Phase 5: Implement UI Module

### 5.1 Banner (nodejs/src/lib/ui/banner.ts)

- [ ] Export `BANNER` constant (6-line ASCII art)
- [ ] Export `TAGLINE` constant
- [ ] Export `COLORS` array for gradient
- [ ] Implement `showBanner(): void`
  - [ ] Apply gradient colors to banner lines
  - [ ] Center text in terminal
  - [ ] Display tagline in yellow italic

### 5.2 StepTracker (nodejs/src/lib/ui/tracker.ts)

- [ ] Implement `StepTracker` class:
  ```typescript
  class StepTracker {
    title: string;
    steps: Step[];
    
    constructor(title: string);
    attachRefresh(cb: () => void): void;
    add(key: string, label: string): void;
    start(key: string, detail?: string): void;
    complete(key: string, detail?: string): void;
    error(key: string, detail?: string): void;
    skip(key: string, detail?: string): void;
    render(): string;
  }
  ```
- [ ] Implement status symbols:
  - [ ] done: green ●
  - [ ] pending: dim ○
  - [ ] running: cyan ○
  - [ ] error: red ●
  - [ ] skipped: yellow ○
- [ ] Implement detail formatting (parentheses)
- [ ] Handle callback exceptions silently

### 5.3 Interactive Selection (nodejs/src/lib/ui/select.ts)

- [ ] Implement `SelectOptions` interface
- [ ] Implement `selectWithArrows<T>(options: Record<T, string>, prompt: string, defaultKey?: T): Promise<T>`
  - [ ] Display options with current selection highlighted
  - [ ] Handle up/down arrow keys
  - [ ] Handle Enter to confirm
  - [ ] Handle Escape to cancel
  - [ ] Handle Ctrl+C as KeyboardInterrupt

### 5.4 Console Utilities (nodejs/src/lib/ui/console.ts)

- [ ] Export chalk wrappers for consistent styling
- [ ] Implement `centerText(text: string): string`
- [ ] Implement `panel(content: string, title?: string): void`

### 5.5 Verification

- [ ] Run `npm test -- nodejs/tests/lib/ui/`
- [ ] All 65+ UI tests pass (GREEN)

### 5.6 Git Checkpoint

- [ ] `git add .`
- [ ] `git commit -m "feat: implement UI module (banner, tracker, select, console)"`
- [ ] `git push origin main`

---

## Phase 6: Implement Tools Module

### 6.1 Tool Detection (nodejs/src/lib/tools/detect.ts)

- [ ] Implement `checkTool(tool: string, tracker?: StepTracker): boolean`
  - [ ] Special handling for Claude: check CLAUDE_LOCAL_PATH first
  - [ ] Use `which` on Unix, `where` on Windows
  - [ ] Update tracker if provided

- [ ] Implement `runCommand(cmd: string[], options?: RunOptions): Promise<string | null>`
  - [ ] Execute command via execa
  - [ ] Optionally capture output
  - [ ] Handle errors

### 6.2 Git Operations (nodejs/src/lib/tools/git.ts)

- [ ] Implement `isGitRepo(path?: string): boolean`
  - [ ] Run `git rev-parse --is-inside-work-tree`
  - [ ] Return true/false based on exit code

- [ ] Implement `initGitRepo(projectPath: string, quiet?: boolean): Promise<[boolean, string | null]>`
  - [ ] Run `git init`
  - [ ] Run `git add .`
  - [ ] Run `git commit -m "Initial commit from Specify template"`
  - [ ] Return [success, errorMessage]

### 6.3 Verification

- [ ] Run `npm test -- nodejs/tests/lib/tools/`
- [ ] All 41+ tools tests pass (GREEN)

### 6.4 Git Checkpoint

- [ ] `git add .`
- [ ] `git commit -m "feat: implement tools module (detect, git)"`
- [ ] `git push origin main`

---

## Phase 7: Implement Commands

### 7.1 Check Command (nodejs/src/commands/check.ts)

- [ ] Implement `checkCommand(): Promise<void>`
  - [ ] Show banner
  - [ ] Create StepTracker
  - [ ] Check git
  - [ ] Check each CLI agent (claude, gemini, qwen, opencode, codex, auggie, codebuddy, q, amp, shai)
  - [ ] Skip IDE agents (copilot, cursor-agent, windsurf, kilocode, roo)
  - [ ] Check VS Code (code, code-insiders)
  - [ ] Render tracker

### 7.2 Version Command (nodejs/src/commands/version.ts)

- [ ] Implement `versionCommand(): Promise<void>`
  - [ ] Read CLI version from package.json
  - [ ] Fetch template version from GitHub API
  - [ ] Display Node.js version
  - [ ] Display platform and architecture

### 7.3 Init Command (nodejs/src/commands/init.ts)

- [ ] Implement `InitOptions` interface
- [ ] Implement `initCommand(projectName?: string, options?: InitOptions): Promise<void>`
  - [ ] Show banner
  - [ ] Validate project name
  - [ ] Handle --here flag and "." as project name
  - [ ] Check for non-empty directory (--force to skip)
  - [ ] Interactive AI selection if not specified
  - [ ] Check agent CLI if requiresCli
  - [ ] Interactive script type selection
  - [ ] Create StepTracker
  - [ ] Download template
  - [ ] Extract template
  - [ ] Set script permissions (Unix)
  - [ ] Initialize git (unless --no-git)
  - [ ] Show completion panel
  - [ ] Special Codex CODEX_HOME message
  - [ ] Truncate branch name at 244 bytes

### 7.4 Verification

- [ ] Run `npm test -- nodejs/tests/commands/`
- [ ] All 93+ command tests pass (GREEN)

### 7.5 Git Checkpoint

- [ ] `git add .`
- [ ] `git commit -m "feat: implement CLI commands (check, version, init)"`
- [ ] `git push origin main`

---

## Phase 8: CLI Wiring & Integration

### 8.1 CLI Setup (nodejs/src/cli.ts)

- [ ] Create Commander program
- [ ] Configure `specify` command name
- [ ] Add `init` subcommand with all options:
  - [ ] `[project-name]` argument
  - [ ] `--ai <assistant>` option
  - [ ] `--script <type>` option
  - [ ] `--no-git` flag
  - [ ] `--here` flag
  - [ ] `--force` flag
  - [ ] `--ignore-agent-tools` flag
  - [ ] `--skip-tls` flag
  - [ ] `--debug` flag
  - [ ] `--github-token <token>` option
- [ ] Add `check` subcommand
- [ ] Add `version` subcommand
- [ ] Show banner when no subcommand
- [ ] Handle errors and exit codes

### 8.2 Package Entry (nodejs/src/index.ts)

- [ ] Export all public APIs
- [ ] Export types
- [ ] Export commands for programmatic use

### 8.3 Executable Wrapper (nodejs/bin/specify.js)

- [ ] Add shebang
- [ ] Import and run CLI

### 8.4 Build & Test

- [ ] Run `npm run build` - succeeds
- [ ] Run `npm test` - all 586 tests pass
- [ ] Run `npm run typecheck` - no errors
- [ ] Run `npm run lint` - no errors

### 8.5 Smoke Tests

- [ ] `cd nodejs && npx . --help` - shows help
- [ ] `npx . init --help` - shows init help
- [ ] `npx . check` - runs check command
- [ ] `npx . version` - shows version info
- [ ] `npx . init test-project --ai copilot --script sh --no-git` - creates project

### 8.6 Git Checkpoint

- [ ] `git add .`
- [ ] `git commit -m "feat: wire CLI entry points and complete integration"`
- [ ] `git push origin main`

---

## Phase 9: Documentation & Polish

### 9.1 Update Documentation

- [ ] Update README.md with Node.js installation
- [ ] Update README.md with npx usage
- [ ] Add CHANGELOG.md entry for 0.0.1
- [ ] Update CONTRIBUTING.md for TypeScript development

### 9.2 Package Validation

- [ ] Run `npm pack` - creates tarball
- [ ] Inspect tarball contents
- [ ] Verify all files included
- [ ] Test local installation: `npm install ./specify-cli-0.0.1.tgz`

### 9.3 Cross-Platform Testing

- [ ] Test on Windows (PowerShell)
- [ ] Test on macOS (zsh)
- [ ] Test on Linux (bash)
- [ ] Verify script permissions work correctly

### 9.4 Final Verification

- [ ] All 586 tests pass
- [ ] TypeScript strict mode: no errors
- [ ] ESLint: no errors
- [ ] Prettier: all files formatted
- [ ] Package builds successfully
- [ ] CLI runs on all platforms

### 9.5 Git Checkpoint (Release)

- [ ] `git add .`
- [ ] `git commit -m "docs: update documentation for v0.0.1 release"`
- [ ] `git tag v0.0.1`
- [ ] `git push origin main --tags`

---

## Success Criteria

- [ ] All 586 acceptance tests ported and passing
- [ ] All Python functionality replicated
- [ ] Pure ESM package
- [ ] TypeScript strict mode
- [ ] Cross-platform (Windows, macOS, Linux)
- [ ] `npm pack` creates valid package
- [ ] `npx @specify/cli init my-project --ai copilot` works

---

## Appendix: Python → TypeScript Dependency Mapping

| Python | TypeScript | Notes |
|--------|------------|-------|
| `typer` | `commander` | CLI framework |
| `rich.Console` | `chalk` | Terminal colors |
| `rich.Panel` | custom | Box around content |
| `rich.Progress` | `ora` | Spinners/progress |
| `rich.Table` | `cli-table3` | Table output |
| `rich.Tree` | custom | Tree rendering |
| `rich.Live` | custom | Live updating |
| `readchar` | `@inquirer/prompts` | Keyboard input |
| `httpx` | `node-fetch` | HTTP client |
| `zipfile` | `adm-zip` | ZIP handling |
| `shutil` | `fs-extra` | File operations |
| `subprocess` | `execa` | Shell commands |
| `platformdirs` | `env-paths` | Platform paths |
| `truststore` | native Node.js TLS | System certificates |

---

## Appendix: Error Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Missing dependency |
| 3 | Invalid argument |
| 4 | Network error |
| 5 | File system error |
| 130 | User cancelled (Ctrl+C) |

---

## Appendix: Test Files Mapping

| Python Test File | TypeScript Test File |
|------------------|---------------------|
| `test_agent_config.py` | `tests/lib/config.test.ts` |
| `test_banner.py` | `tests/lib/ui/banner.test.ts` |
| `test_check_command.py` | `tests/commands/check.test.ts` |
| `test_claude_path.py` | `tests/lib/config.test.ts` |
| `test_error_messages.py` | `tests/lib/errors.test.ts` |
| `test_exit_codes.py` | `tests/commands/exit-codes.test.ts` |
| `test_github_token.py` | `tests/lib/github/token.test.ts` |
| `test_git_operations.py` | `tests/lib/tools/git.test.ts` |
| `test_init_command.py` | `tests/commands/init.test.ts` |
| `test_interactive_selection.py` | `tests/lib/ui/select.test.ts` |
| `test_json_merge.py` | `tests/lib/template/merge.test.ts` |
| `test_platform_compat.py` | `tests/platform.test.ts` |
| `test_rate_limit_error.py` | `tests/lib/github/rate-limit.test.ts` |
| `test_rate_limit_parsing.py` | `tests/lib/github/rate-limit.test.ts` |
| `test_script_permissions.py` | `tests/lib/template/permissions.test.ts` |
| `test_script_types.py` | `tests/lib/config.test.ts` |
| `test_step_tracker.py` | `tests/lib/ui/tracker.test.ts` |
| `test_template_download.py` | `tests/lib/template/download.test.ts` |
| `test_template_extraction.py` | `tests/lib/template/extract.test.ts` |
| `test_template_files.py` | `tests/lib/template/files.test.ts` |
| `test_tls_handling.py` | `tests/lib/github/tls.test.ts` |
| `test_tool_detection.py` | `tests/lib/tools/detect.test.ts` |
| `test_version_command.py` | `tests/commands/version.test.ts` |
