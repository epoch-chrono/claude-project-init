# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-02-10

### Changed
- **BREAKING**: Removed separate metaprompt files (metaprompt-resumo.md, metaprompt-retomar.md, metaprompt-iniciar.md, metaprompt-checkpoint.md)
- All session commands ([RESUMO], [RETOMAR], [INICIAR], [CHECKPOINT], [TAG], [ARTEFATOS], [VERSIONAR]) are now inline in INSTRUCOES.md
- Project scaffold reduced from 7 files to 3 files (README.md, DESCRICAO.txt, INSTRUCOES.md)
- Context overhead per project reduced by ~82% (~5,000 → ~900 tokens)
- [CHECKPOINT] now includes memory export step: lists project-scoped memory edits, exports as artifacts, suggests cleanup of global memories

### Removed
- `gen_metaprompt_resumo()`, `gen_metaprompt_retomar()`, `gen_metaprompt_iniciar()`, `gen_metaprompt_checkpoint()` from engine
- Metaprompt file generation from both `create` and `migrate` flows
- Upload instructions for metaprompt files in README template and CLI output

### Migration
- Run `claude-project-init --migrate "Category/Name"` for guided checklist
- Remove 4 metaprompt files from Project Knowledge in Claude UI
- Replace INSTRUCOES.md with new inline version — no functionality lost

## [1.4.1] - 2025-02-07

### Fixed
- `make test` now cleans Test/* entries from registry after smoke tests
- `make clean` also purges test entries from registry

## [1.4.0] - 2025-02-07

### Added
- Migration status indicator in `--list`: `[✔]` migrated, `[ ]` pending
- `registry_set_migrated` operation in Python engine
- Both `create` and `--migrate` now mark projects as migrated in registry

### Changed
- Registry schema: new optional `migrated` field (backward compatible)

## [1.3.1] - 2025-02-07

### Fixed
- Makefile release target: use dynamic branch (`git branch --show-current`) instead of hardcoded branch name

## [1.3.0] - 2025-02-07

### Added
- `[CHECKPOINT]` metaprompt — consolidated snapshot of entire project state
- `metaprompt-checkpoint.md` generated in both `create` and `--migrate` flows
- CHECKPOINT command listed in INSTRUCOES.md, DESCRICAO.txt, and README.md templates

### Changed
- `--migrate` now generates DESCRICAO.txt (was missing in v1.2.0)
- File count: 6 → 7 files per project (added metaprompt-checkpoint.md)

## [1.2.0] - 2025-02-07

### Added
- `--remove` command to delete projects from local registry
- `--remove` interactive mode (shows list, asks which to remove)
- `completion` subcommand generating shell completions for Fish, Bash, and Zsh
- `completion --names` internal helper for dynamic completions
- `registry_remove` and `registry_names` operations in Python engine

## [1.1.0] - 2025-02-07

### Added
- `--import` command to register existing Claude Projects in local registry
- `--import` interactive mode for bulk import of multiple projects
- `--migrate` command to generate best-practices migration files
- Migration checklist (`MIGRACAO-CHECKLIST.md`) for guided project migration
- [glow](https://github.com/charmbracelet/glow) integration for rich markdown rendering
- Auto-render README after project creation (glow if available, fallback to colored terminal)
- Auto-render migration checklist after `--migrate`
- Hint to install glow when not available

### Changed
- Split architecture: Fish CLI wrapper + Python engine (replaces monolithic Fish script)
- Improved template generation reliability (no more Fish heredoc escaping issues)

## [1.0.0] - 2025-02-07

### Added
- Interactive and non-interactive project creation
- Template generation: INSTRUCOES.md, DESCRICAO.txt, 3 metaprompts, README.md
- `--dry-run` preview mode
- `--list` to show registered projects
- Local registry at `~/.config/claude-project-init/registry.json`
- Cross-project tag references in generated instructions
- SemVer artifact naming convention with standardized headers
- Session management metaprompts: `[RESUMO]`, `[RETOMAR]`, `[INICIAR]`
- Conversation title convention: `(Tag)(YYYYMMDD-HHMM)-Description`
