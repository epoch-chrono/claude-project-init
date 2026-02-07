# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
