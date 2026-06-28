# GitHub Copilot setup for keystone

This folder makes the same agents and conventions used in Claude Code available to
**GitHub Copilot in VS Code**, for teams in the closed LSEG ecosystem that have
Copilot but not Claude Code. The `.claude/` and `.github/` copies are kept in sync
by hand — **edit both** when a convention changes.

## What maps to what

| Claude Code (`.claude/`)            | GitHub Copilot (`.github/`)                          | How it activates |
|-------------------------------------|------------------------------------------------------|------------------|
| `CLAUDE.md`                         | `copilot-instructions.md`                            | Auto-included in every Copilot chat for this repo |
| `skills/*/SKILL.md`                 | `instructions/*.instructions.md`                     | Auto-applied when an edited file matches the `applyTo` glob |
| `agents/*.md` (subagents)           | `chatmodes/*.chatmode.md` (custom chat modes)        | Pick from the Chat **mode dropdown** |

### Instructions (skill equivalents) — `instructions/`
- `keystone-architecture.instructions.md` — applies to `src/keystone/**`, `scripts/**`, `tests/**`
- `market-data-cleaning.instructions.md` — applies to cleaning/ingestion paths
- `python-patterns.instructions.md` — applies to all `*.py`
- `python-testing.instructions.md` — applies to test files

### Chat modes (subagent equivalents) — `chatmodes/`
`code-reviewer`, `test-writer`, `documentor`, `migration-engineer`,
`reconciliation-checker`. Open Copilot Chat, choose the mode from the dropdown,
and it adopts that persona + tool set.

> Tool names in the `tools:` frontmatter are VS Code Copilot tool sets
> (`codebase`, `search`, `editFiles`, `runCommands`, …) — the analogue of the
> Claude Code `tools:` line. The model is left unset so it uses whatever the user
> has selected.

## Enabling (VS Code)
Custom instructions and chat modes are on by default in current VS Code + Copilot.
This repo also sets the relevant flags in `.vscode/settings.json`:
- `github.copilot.chat.codeGeneration.useInstructionFiles: true`
- `chat.promptFiles: true`

If chat modes don't appear, update the GitHub Copilot Chat extension and reload.
