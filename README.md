# claude-project-init

CLI tool to scaffold [Claude Projects](https://claude.ai) with optimized structure, semantic versioning, and session management.

Turns a blank Claude Project into a structured workspace with inline session commands, naming conventions, and artifact versioning — in seconds.

## Why?

Claude Projects are powerful but start empty. Every time you create one, you repeat the same setup: write instructions, define commands, establish naming conventions, figure out session continuity.

`claude-project-init` generates all of that from a template, locally, and gives you a step-by-step to paste into the UI.

## Features

- **Scaffold new projects** with instructions, description, and README
- **Inline session commands** — all commands live in INSTRUCOES.md, no separate metaprompt files needed (v2.0.0)
- **Import existing projects** into a local registry for tag management
- **Migrate projects** to best practices with guided checklists
- **Session management** via `[RESUMO]`, `[RETOMAR]`, `[INICIAR]`, `[CHECKPOINT]`
- **SemVer artifacts** with standardized headers and naming
- **Tag registry** — tracks all projects locally, auto-populates cross-references
- **glow integration** — renders markdown beautifully if [glow](https://github.com/charmbracelet/glow) is installed

## Install

### Via [mise](https://mise.jdx.dev) (recommended)

```fish
mise use -g github:epoch-chrono/claude-project-init
```

### Manual

```fish
git clone https://github.com/epoch-chrono/claude-project-init.git ~/.local/share/claude-project-init
ln -s ~/.local/share/claude-project-init/bin/claude-project-init ~/bin/claude-project-init
```

### Requirements

- [Fish shell](https://fishshell.com/) 3.5+
- Python 3.8+ (stdlib only, no pip dependencies)
- Optional: [glow](https://github.com/charmbracelet/glow) for rich markdown rendering

## Quick Start

```fish
# Create a new project (interactive)
claude-project-init

# Create with all options
claude-project-init "Home/RaspberryPi" \
  --role "embedded systems engineer" \
  --stack "Python, Ansible, RPi OS"

# Import existing projects into the registry
claude-project-init --import

# Migrate an existing project to best practices
claude-project-init --migrate "Home/BenjiBot"
```

## Usage

```
claude-project-init                           # interactive mode
claude-project-init "Category/Name"           # quick create
claude-project-init "Cat/Name" --role "..." --stack "..."  # full create

Options:
  --role <role>       Role for the AI assistant
  --stack <stack>     Technologies/stack
  --output <dir>      Output directory (default: .)
  --tag <tag>         Custom tag (default: extracted from name)
  --dry-run           Preview without creating files

Project management:
  --import            Register existing project(s) in local registry
  --migrate <name>    Generate migration files for best practices
  --remove <name>     Remove project from local registry
  --list              List registered projects
  completion <shell>  Generate shell completions (fish, bash, zsh)

Info:
  --version           Show version
  --help              Show help
```

## What It Generates

```
Home-RaspberryPi/
├── README.md          # Setup instructions for the UI
├── DESCRICAO.txt      # Text for the "Description" field
└── INSTRUCOES.md      # Content for the "Instructions" field (includes all commands)
```

> **v2.0.0**: Session commands (`[RESUMO]`, `[RETOMAR]`, etc.) are now inline in INSTRUCOES.md. No separate metaprompt files — reduces context overhead by ~82%.

### Setup Flow

1. Run `claude-project-init "Category/Name"`
2. Create a project in [claude.ai](https://claude.ai) → Projects → New Project
3. Paste `DESCRICAO.txt` into the Description field
4. Paste `INSTRUCOES.md` into the Instructions field (edit the CONTEXTO section)
5. Start a conversation and type `[INICIAR]`

## Commands (inside Claude)

| Command        | What it does                              |
|----------------|-------------------------------------------|
| `[INICIAR]`    | Start session with project briefing       |
| `[RESUMO]`     | Generate comprehensive session summary    |
| `[RETOMAR]`    | Resume from a previous session's context  |
| `[CHECKPOINT]` | Consolidated snapshot of entire project   |
| `[TAG]`        | Suggest formatted conversation title      |
| `[ARTEFATOS]`  | List and version session artifacts        |
| `[VERSIONAR]`  | Analyze changes, suggest SemVer bumps     |

## Project Registry

All projects are tracked locally at `~/.config/claude-project-init/registry.json`. Tags from existing projects are automatically included in new project instructions for cross-referencing.

```fish
# List all registered projects
claude-project-init --list

# Import projects you already have in Claude
claude-project-init --import "Work/API" --tag "API"
claude-project-init --import   # interactive, multiple at once
```

## Architecture

```
bin/claude-project-init    # Fish CLI — handles UX, colors, interactivity
lib/cpi_engine.py          # Python engine — templates, registry, file generation
```

Fish handles what it's good at (shell UX, colors, interactive prompts). Python handles what Fish is bad at (multiline templates, JSON, string manipulation). No external dependencies beyond Python stdlib.

## Migrating from v1.x

If you have projects created with v1.x (with separate metaprompt files):

1. Run `claude-project-init --migrate "Category/Name"` to generate a migration checklist
2. In the Claude UI: remove the 4 metaprompt files from Project Knowledge
3. Replace INSTRUCOES.md content with the new template (commands are now inline)
4. No functionality is lost — all commands work the same way

## Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Test locally: `make test`
4. Commit with [Conventional Commits](https://www.conventionalcommits.org/)
5. Open a PR

## License

[MIT](LICENSE)
