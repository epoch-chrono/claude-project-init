#!/usr/bin/env python3
"""
claude-project-init engine
Handles: templates, registry, file generation
Called by the Fish CLI wrapper.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

VERSION = "2.0.0"
CONFIG_DIR = Path.home() / ".config" / "claude-project-init"
REGISTRY = CONFIG_DIR / "registry.json"


def ensure_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not REGISTRY.exists():
        REGISTRY.write_text('{"projects":[]}')


def load_registry():
    ensure_config()
    return json.loads(REGISTRY.read_text())


def save_registry(data):
    REGISTRY.write_text(json.dumps(data, indent=2))


# ─── Registry Operations ─────────────────────────────────────────────────────

def registry_add(name, tag):
    data = load_registry()
    ts = datetime.now().isoformat(timespec="seconds")
    for p in data["projects"]:
        if p["name"] == name:
            p["tag"] = tag
            p["updated"] = ts
            save_registry(data)
            return
    data["projects"].append({"name": name, "tag": tag, "created": ts, "updated": ts})
    save_registry(data)


def registry_set_migrated(name):
    data = load_registry()
    for p in data["projects"]:
        if p["name"] == name:
            p["migrated"] = True
            p["updated"] = datetime.now().isoformat(timespec="seconds")
            save_registry(data)
            print("ok")
            return
    print("not_found")


def registry_list():
    data = load_registry()
    projects = sorted(data["projects"], key=lambda x: x["name"])
    if not projects:
        print("__EMPTY__")
        return
    for p in projects:
        migrated = "✔" if p.get("migrated") else " "
        print(f"  [{migrated}] {p['name']:<35} ({p['tag']})")
    print(f"__COUNT__{len(projects)}")


def registry_get_tags():
    data = load_registry()
    for p in sorted(data["projects"], key=lambda x: x["name"]):
        print(f"{p['name']} -> ({p['tag']})")


def registry_count():
    print(len(load_registry()["projects"]))


def registry_exists(name):
    data = load_registry()
    print("yes" if any(p["name"] == name for p in data["projects"]) else "no")


def registry_remove(name):
    data = load_registry()
    before = len(data["projects"])
    data["projects"] = [p for p in data["projects"] if p["name"] != name]
    if len(data["projects"]) == before:
        print("not_found")
    else:
        save_registry(data)
        print("ok")


def registry_names():
    """List just project names, one per line — used for completions."""
    data = load_registry()
    for p in sorted(data["projects"], key=lambda x: x["name"]):
        print(p["name"])


# ─── Tag List Helper ──────────────────────────────────────────────────────────

def _get_tag_list_str():
    data = load_registry()
    lines = []
    for p in sorted(data["projects"], key=lambda x: x["name"]):
        lines.append(f"- {p['name']} -> ({p['tag']})")
    return "\n".join(lines)


# ─── Templates ────────────────────────────────────────────────────────────────

def _ts():
    return datetime.now().strftime("%Y%m%d-%H%M")


def _iso():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def gen_description(name, role, stack):
    return f"""{name} — Projeto Claude com organização otimizada.

Estrutura: Instruções (contexto, papel, comandos inline, versionamento) | Memórias (automático).
Comandos: [RESUMO] [RETOMAR] [INICIAR] [CHECKPOINT] [TAG] [ARTEFATOS] [VERSIONAR].
Versionamento: SemVer (vMAIOR.MENOR.PATCH) com timestamp no nome.
Role: {role}
Stack: {stack}
"""


def gen_instructions(name, tag, role, stack):
    tag_list = _get_tag_list_str()
    return f"""# File: INSTRUCOES.md
# Version: v2.0.0
# Created: {_iso()}
# Purpose: Instruções do projeto {name}

# INSTRUÇÕES DO PROJETO: {name}

## CONTEXTO

[TODO: Objetivo principal em 2-3 frases. Escopo, estado atual, tecnologias.]
Stack: {stack}

## PAPEL

Atue como {role}.

## COMANDOS DE SESSÃO

Todos os comandos abaixo são acionados pelo usuário digitando o gatilho entre colchetes.

### [INICIAR]
Faça inventário do projeto (resumos, artefatos, pendências). Apresente briefing de 5-8 linhas: nome, objetivo, última sessão, pendências. Pergunte o foco desta sessão e proponha plano em até 5 etapas. Se for primeiro uso, confirme escopo e comece pelo fundamental.

### [RESUMO]
Leia toda a conversa e produza resumo **autossuficiente** para retomar em outra sessão. Deve conter: objetivo original, o que foi feito (com decisões e justificativas), estado atual (funciona/não funciona/configs), problemas pendentes, artefatos com versão, próximos passos (máx 5 priorizados), e prompt de continuação em 1 linha. Salvar como `resumo-sessao-YYYYMMDD-HHMM.v1.0.0.md`.

### [RETOMAR]
Localize resumo mais recente (arquivo anexo ou Knowledge). Reconstrua estado: onde paramos, o que funciona, configs ativas, pendências. Valide com o usuário antes de prosseguir. Se não encontrar resumo, peça contexto.

### [CHECKPOINT]
Diferente de RESUMO (1 sessão), CHECKPOINT é snapshot do **projeto inteiro**. Consulte todas as fontes (instruções, knowledge, conversas, memórias). Produza arquivo consolidado com: visão geral, artefatos vigentes (tabela), decisões vigentes, estado atual, dívida técnica, próximos passos (imediato/curto/backlog). Deve ser autossuficiente — não depender de conversas anteriores. Incluir seção final "Memórias": listar memory edits em escopo do projeto, exportar cada uma como artefato separado, e perguntar ao usuário quais podem ser removidas das memórias globais (já que ficaram registradas no checkpoint). Salvar como `checkpoint-YYYYMMDD-HHMM.v1.0.0.md`. Após gerar, sugerir limpeza de resumos antigos e memórias consolidadas.

### [TAG]
Sugerir título: `({tag})(YYYYMMDD-HHMM)-Descrição concisa (máx 8 palavras)`

### [ARTEFATOS]
Listar todos os artefatos da sessão com nome, versão e status.

### [VERSIONAR]
Analisar mudanças nos artefatos e sugerir bump SemVer (MAIOR/MENOR/PATCH).

## VERSIONAMENTO

Nome: `nome.vMAIOR.MENOR.PATCH.YYYYMMDD-HHMM.ext`
Cabeçalho (quando formato aceitar comentários):
```
# File: nome.vX.Y.Z.YYYYMMDD-HHMM.ext
# Version: vX.Y.Z
# Created/Updated: YYYY-MM-DD HH:MM
# Purpose: [descrição breve]
```

## TAGS

Formato: `(Tag)(YYYYMMDD-HHMM)-Descrição concisa`
Tags conhecidas:
{tag_list}
- {name} -> ({tag})

## DIRETRIZES

- Credenciais via env vars ou secret managers, nunca hardcoded
- Ao final de cada sessão, sugerir `[RESUMO]`
"""


def gen_readme(name, tag):
    ts = _ts()
    return f"""# SETUP: {name}

Gerado por `claude-project-init` v{VERSION} em {_iso()}.

## PASSOS PARA CONFIGURAR NA UI (claude.ai)

### 1. Criar Projeto
- claude.ai → Projects → New Project
- Nome: **{name}**
- Descrição: copiar de `DESCRICAO.txt`

### 2. Configurar Instruções
- Campo "Instruções" → colar conteúdo de `INSTRUCOES.md`
- ⚠️ EDITE a seção "CONTEXTO" com detalhes do seu projeto

### 3. Primeira Conversa
- Nova conversa no projeto → `[INICIAR]`

### 4. Ao Finalizar
- `[RESUMO]` → upload do resumo nos Arquivos → renomear conversa

## COMANDOS

| Comando         | Função                                  |
|-----------------|-----------------------------------------|
| `[RESUMO]`      | Resumo completo da sessão               |
| `[RETOMAR]`     | Reconstroi contexto anterior            |
| `[INICIAR]`     | Briefing e definição de objetivo        |
| `[CHECKPOINT]`  | Snapshot consolidado do projeto inteiro |
| `[TAG]`         | Sugere título formatado                 |
| `[ARTEFATOS]`   | Lista e versiona artefatos              |
| `[VERSIONAR]`   | Analisa mudanças, sugere versões SemVer |

## TÍTULOS
Formato: `({tag})({ts})-Descrição concisa`

## NOTA v2.0.0
Comandos de sessão agora são inline no INSTRUCOES.md.
Não é mais necessário fazer upload de metaprompts no Knowledge.
"""


def gen_migration_checklist(name, tag):
    return f"""# CHECKLIST DE MIGRAÇÃO: {name}

Gerado em {_iso()}.

## PRÉ-MIGRAÇÃO
- [ ] Abrir projeto "{name}" na UI
- [ ] Listar conversas (títulos e datas)
- [ ] Listar Arquivos atuais
- [ ] Identificar artefatos nas conversas

## LIMPEZA v2.0.0
- [ ] Remover metaprompts antigos do Knowledge:
  - [ ] metaprompt-resumo.md
  - [ ] metaprompt-retomar.md
  - [ ] metaprompt-iniciar.md
  - [ ] metaprompt-checkpoint.md
- [ ] Remover arquivos obsoletos/duplicados
- [ ] Mover conversas de outro projeto
- [ ] Trazer conversas avulsas
- [ ] Renomear projeto (Categoria/Nome)

## APLICAR TEMPLATE v2
- [ ] Editar `INSTRUCOES.md` com contexto real
- [ ] Colar em "Instruções" (comandos já estão inline)
- [ ] NÃO fazer upload de metaprompts (eliminados na v2)

## REVISAR MEMÓRIAS
- [ ] Verificar memórias globais em escopo deste projeto
- [ ] Mover para instruções do projeto ou remover

## VERSIONAR ARTEFATOS
- [ ] Sem versão → v1.0.0
- [ ] Renomear: `nome.v1.0.0.YYYYMMDD-HHMM.ext`
- [ ] Cabeçalho padrão
- [ ] Upload novo, remover antigo

## RENOMEAR CONVERSAS
- [ ] `({tag})(YYYYMMDD-HHMM)-Descrição concisa`

## VALIDAÇÃO
- [ ] Nova conversa → `[INICIAR]`
- [ ] Briefing OK? → Migração completa ✔
"""


# ─── File Generator ───────────────────────────────────────────────────────────

def generate_file(filepath, template, name="", tag="", role="", stack=""):
    generators = {
        "description": lambda: gen_description(name, role, stack),
        "instructions": lambda: gen_instructions(name, tag, role, stack),
        "readme": lambda: gen_readme(name, tag),
        "migration": lambda: gen_migration_checklist(name, tag),
    }
    if template not in generators:
        print(f"Unknown template: {template}", file=sys.stderr)
        sys.exit(1)
    Path(filepath).write_text(generators[template]())


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: cpi_engine.py <command> [args...]", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "registry_add":
        registry_add(sys.argv[2], sys.argv[3])
    elif cmd == "registry_list":
        registry_list()
    elif cmd == "registry_get_tags":
        registry_get_tags()
    elif cmd == "registry_count":
        registry_count()
    elif cmd == "registry_exists":
        registry_exists(sys.argv[2])
    elif cmd == "registry_remove":
        registry_remove(sys.argv[2])
    elif cmd == "registry_set_migrated":
        registry_set_migrated(sys.argv[2])
    elif cmd == "registry_names":
        registry_names()
    elif cmd == "generate":
        # generate <filepath> <template> <n> <tag> [role] [stack]
        filepath = sys.argv[2]
        template = sys.argv[3]
        name = sys.argv[4] if len(sys.argv) > 4 else ""
        tag = sys.argv[5] if len(sys.argv) > 5 else ""
        role = sys.argv[6] if len(sys.argv) > 6 else ""
        stack = sys.argv[7] if len(sys.argv) > 7 else ""
        generate_file(filepath, template, name, tag, role, stack)
    elif cmd == "version":
        print(VERSION)
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
