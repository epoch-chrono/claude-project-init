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

VERSION = "1.3.1"
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


def registry_list():
    data = load_registry()
    projects = sorted(data["projects"], key=lambda x: x["name"])
    if not projects:
        print("__EMPTY__")
        return
    for p in projects:
        print(f"  {p['name']:<35} ({p['tag']})")
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

Estrutura: Instruções (contexto, papel, comandos, versionamento) |
Arquivos (metaprompts, templates, documentação) | Memórias (automático).
Comandos: [RESUMO] [RETOMAR] [INICIAR] [CHECKPOINT] [TAG] [ARTEFATOS] [VERSIONAR].
Versionamento: SemVer (vMAIOR.MENOR.PATCH) com timestamp no nome.
Role: {role}
Stack: {stack}
"""


def gen_instructions(name, tag, role, stack):
    tag_list = _get_tag_list_str()
    return f"""# File: INSTRUCOES.md
# Version: v1.0.0
# Created: {_iso()}
# Purpose: Instruções do projeto {name}

# INSTRUÇÕES DO PROJETO: {name}

## CONTEXTO

[TODO: Descreva o objetivo principal do projeto em 2-3 frases.]
[Inclua escopo, estado atual e tecnologias envolvidas.]
Stack: {stack}

## PAPEL

Atue como {role}. Forneça:
- Código e soluções técnicas
- Arquitetura e boas práticas
- Divisão de tarefas complexas em etapas com confirmações

## VERSIONAMENTO SEMÂNTICO

Todos os artefatos devem usar SemVer:

Formato do nome: `nome.vMAIOR.MENOR.PATCH.YYYYMMDD-HHMM.ext`

- MAIOR: breaking changes, refatoração completa
- MENOR: novas funcionalidades compatíveis
- PATCH: correções de bugs, ajustes menores

Cabeçalho obrigatório (quando o formato aceitar comentários):

```
# File: nome.vX.Y.Z.YYYYMMDD-HHMM.ext
# Version: vX.Y.Z
# Created: YYYY-MM-DD HH:MM
# Last Updated: YYYY-MM-DD HH:MM
# Purpose: [descrição breve]
# Changes:
#   vX.Y.Z - [tipo]: [descrição]
```

## COMANDOS DE CONTROLE

- `[RESUMO]` → Resumo completo da sessão (metaprompt-resumo.md)
- `[RETOMAR]` → Preparação para retomar sessão anterior (metaprompt-retomar.md)
- `[INICIAR]` → Início de nova sessão com contexto (metaprompt-iniciar.md)
- `[CHECKPOINT]` → Snapshot consolidado do projeto inteiro (metaprompt-checkpoint.md)
- `[TAG]` → Apenas sugerir título formatado para a conversa
- `[ARTEFATOS]` → Listar e versionar todos os artefatos da sessão
- `[VERSIONAR]` → Analisar mudanças e sugerir novas versões SemVer

## TAGS E TÍTULOS

Formato: `(Tag)(YYYYMMDD-HHMM)-Descrição concisa (máx 8 palavras)`

Tags de projetos conhecidos:
{tag_list}
- {name} -> ({tag})

Para POCs/spikes: `(Home/Spike)` ou `(Home/POC)`
Para cross-project: use tag do projeto principal (>70% do conteúdo)

## DIRETRIZES DE QUALIDADE

- Cabeçalho versionado em todo artefato
- Configurações sensíveis via variáveis de ambiente (nunca hardcoded)
- Ao final de cada sessão, sugerir: "Deseja que eu execute [RESUMO]?"
"""


def gen_metaprompt_resumo():
    return f"""# File: metaprompt-resumo.md
# Version: v1.0.0
# Created: {_iso()}
# Purpose: Metaprompt para resumir sessão de trabalho
# Gatilho: Usuário digita [RESUMO]

# METAPROMPT: RESUMO DE SESSÃO

Gatilho: `[RESUMO]`

## INSTRUÇÕES

Leia toda a conversa atual. Pense ordenadamente, um passo de cada vez.
Produza um resumo detalhado que permita retomar o trabalho em outra sessão
com todo o contexto necessário, sem redundâncias, com artefatos versionados.

O resumo NÃO pode ser raso. Ele precisa ser suficiente para recomeçar
em outra sessão sem perda de informação.

---

### PASSO 1: CONTEXTO DA SESSÃO
- Qual foi a primeira solicitação/objetivo desta sessão?
- Qual era o estado do projeto antes de começar?
- Qual foi o planejamento proposto?

### PASSO 2: PROGRESSO REALIZADO
- O que foi implementado (código, configurações, testes)
- Comandos executados e outputs relevantes
- Decisões tomadas e suas justificativas
- O que foi refeito/corrigido (com motivo da correção)

### PASSO 3: ESTADO ATUAL
- O que está funcionando agora
- O que NÃO está funcionando
- Configurações ativas (URLs, portas, paths, parâmetros)
- Bloqueios ou dependências externas

### PASSO 4: DORES E PROBLEMAS PENDENTES
Liste problemas não resolvidos, dúvidas técnicas, riscos identificados.

### PASSO 5: VERSIONAMENTO DE ARTEFATOS
Para CADA artefato mencionado ou criado nesta sessão:
1. Verifique se já existe versão anterior
2. Se sim: incremente (PATCH/MENOR/MAIOR conforme SemVer)
3. Se não: inicie em v1.0.0
4. Nome: `nome.vX.Y.Z.YYYYMMDD-HHMM.ext`
5. Adicione cabeçalho com metadados (se formato suportar)
6. Inclua o conteúdo COMPLETO do artefato
7. Valide sintaxe e boas práticas

### PASSO 6: PRÓXIMOS PASSOS
Numere por prioridade (máximo 5).

### PASSO 7: TÍTULO DA CONVERSA
1. Extraia 3-5 palavras-chave
2. Escolha tag baseada nos projetos existentes (ver Instruções)
3. Formato: `(Tag)(YYYYMMDD-HHMM)-Descrição concisa`

### PASSO 8: PREPARAÇÃO PARA PRÓXIMA SESSÃO
Sugira: "Continuar do resumo [nome]. Estado: [1 frase]. Próxima tarefa: [passo 1]."

---

## FORMATO DE SAÍDA
1. Resumo consolidado (Passos 1-6)
2. Artefatos versionados (blocos de código separados)
3. Título sugerido (uma linha)
4. Prompt para próxima sessão (uma linha)

Salvar como: `resumo-sessao-YYYYMMDD-HHMM.v1.0.0.md`

## CHECKLIST FINAL
- [ ] Todas as informações capturadas?
- [ ] Sem redundância?
- [ ] Artefatos com versão e cabeçalho?
- [ ] Próximos passos acionáveis?
- [ ] Prompt de continuação suficiente?
"""


def gen_metaprompt_retomar():
    return f"""# File: metaprompt-retomar.md
# Version: v1.0.0
# Created: {_iso()}
# Purpose: Metaprompt para retomar sessão anterior
# Gatilho: Usuário digita [RETOMAR]

# METAPROMPT: RETOMAR SESSÃO

Gatilho: `[RETOMAR]`

## INSTRUÇÕES

### PASSO 1: LOCALIZAR CONTEXTO
Procure nos Arquivos do projeto:
- Resumo mais recente (`resumo-sessao-*.md`)
- Artefatos versionados relevantes
- CHANGELOG.md (se existir)
Se o usuário anexou um arquivo de resumo, use esse.

### PASSO 2: RECONSTRUIR ESTADO
- Onde paramos (última ação/decisão)
- O que está funcionando / não funcionando
- Configurações ativas
- Artefatos disponíveis (nome, versão, descrição)
- Próximos passos pendentes

### PASSO 3: VALIDAÇÃO
"Esse é o estado correto? Mudou algo?
Começar pelo próximo passo [N] ou outra prioridade?"

### PASSO 4: RETOMAR
Após confirmação: carregue artefato e execute.

---

## CASO: NENHUM RESUMO ENCONTRADO
"Não encontrei resumo anterior. Tem arquivo para anexar
ou prefere descrever onde paramos?"

## CASO: MÚLTIPLOS RESUMOS
Liste com datas e pergunte qual usar.
"""


def gen_metaprompt_iniciar():
    return f"""# File: metaprompt-iniciar.md
# Version: v1.0.0
# Created: {_iso()}
# Purpose: Metaprompt para iniciar nova sessão
# Gatilho: Usuário digita [INICIAR]

# METAPROMPT: INICIAR SESSÃO

Gatilho: `[INICIAR]`

## INSTRUÇÕES

### PASSO 1: INVENTÁRIO DO PROJETO
1. Resumo mais recente (`resumo-sessao-*.md`): existe? data?
2. Artefatos existentes: quais, em que versão?
3. CHANGELOG.md: existe?
4. Instruções: contexto/escopo definido?

### PASSO 2: BRIEFING INICIAL
- Projeto: [Nome]
- Objetivo: [das Instruções]
- Última sessão: [data e 1 frase, ou "primeira sessão"]
- Artefatos disponíveis
- Pendências do resumo anterior

### PASSO 3: DEFINIR OBJETIVO
"O que quer abordar nesta sessão?"
Sugira opções baseadas nas pendências.

### PASSO 4: PLANO DE SESSÃO
1. Quebre em etapas (máx. 5)
2. Identifique artefatos a modificar
3. Comece a executar

---

## CASO: PRIMEIRO USO
Confirme escopo, proponha estrutura, comece pelo fundamental.

## CASO: MUITAS SESSÕES
Use apenas o resumo mais recente.
"""


def gen_metaprompt_checkpoint():
    return f"""# File: metaprompt-checkpoint.md
# Version: v1.0.0
# Created: {_iso()}
# Purpose: Metaprompt para checkpoint consolidado do projeto
# Gatilho: Usuário digita [CHECKPOINT]

# METAPROMPT: CHECKPOINT DO PROJETO

Gatilho: `[CHECKPOINT]`

## OBJETIVO

Produzir um snapshot consolidado do PROJETO INTEIRO — não de uma sessão.
Diferença fundamental:
- `[RESUMO]` → foto de UMA sessão
- `[CHECKPOINT]` → foto do PROJETO (estado da arte acumulado)

O checkpoint permite:
1. Limpar/arquivar conversas antigas sem perder contexto
2. Consolidar informação fragmentada em múltiplas sessões
3. Eliminar redundâncias e decisões obsoletas
4. Criar ponto de restart limpo para o projeto

---

## INSTRUÇÕES

Pense ordenadamente. Leia TODAS as fontes disponíveis antes de produzir o checkpoint.

### PASSO 1: VARREDURA COMPLETA

Consulte todas as fontes de contexto do projeto:
1. **Instruções do projeto** — escopo, papel, stack, convenções
2. **Arquivos no Knowledge** — resumos anteriores, artefatos, docs
3. **Conversas recentes** — use busca para encontrar decisões e contexto
4. **Memórias do projeto** — informações acumuladas automaticamente

### PASSO 2: INVENTÁRIO DE ARTEFATOS

Para CADA artefato que ainda é relevante:
1. Nome e versão mais recente
2. Onde está (Knowledge, conversa, repositório externo)
3. Status: ativo | deprecado | substituído
4. Se deprecado/substituído: indicar pelo quê

Produzir tabela:
```
| Artefato | Versão | Status | Localização | Notas |
```

### PASSO 3: DECISÕES VIGENTES

Listar decisões arquiteturais e técnicas que AINDA valem:
- O que foi decidido
- Justificativa (1 frase)
- Quando (conversa/data aproximada)

Excluir: decisões revertidas, experimentos abandonados, tentativas que falharam.
Se uma decisão foi substituída, registrar apenas a versão atual.

### PASSO 4: ESTADO ATUAL DO PROJETO

- O que está funcionando (features, integrações, deploys)
- O que NÃO está funcionando (bugs conhecidos, limitações)
- Configurações ativas (URLs, parâmetros, versões)
- Dependências externas e seus estados

### PASSO 5: PROBLEMAS E DÍVIDA TÉCNICA

- Bugs conhecidos não resolvidos
- Dívida técnica acumulada
- Riscos identificados
- Perguntas em aberto

### PASSO 6: PRÓXIMOS PASSOS

Numere por prioridade (máximo 7).
Separe em:
- **Imediato** (próxima sessão)
- **Curto prazo** (próximas 3-5 sessões)
- **Backlog** (quando houver tempo)

---

## FORMATO DE SAÍDA

Produzir UM arquivo consolidado:

```markdown
# CHECKPOINT: [Nome do Projeto]
# Data: YYYY-MM-DD HH:MM
# Cobre: [data início] até [data fim]
# Conversas consolidadas: [quantidade]

## 1. VISÃO GERAL
[Estado do projeto em 3-5 frases]

## 2. ARTEFATOS VIGENTES
[Tabela do Passo 2 — apenas ativos]

## 3. DECISÕES VIGENTES
[Lista do Passo 3]

## 4. ESTADO ATUAL
[Passo 4]

## 5. PROBLEMAS E DÍVIDA TÉCNICA
[Passo 5]

## 6. PRÓXIMOS PASSOS
[Passo 6]

## 7. CONTEXTO PARA CONTINUAÇÃO
[Tudo que a próxima sessão precisa saber pra começar sem perguntar]
```

Salvar como: `checkpoint-YYYYMMDD-HHMM.v1.0.0.md`

## PÓS-CHECKPOINT

Após gerar o checkpoint, sugerir:
1. "Faça upload do checkpoint nos Arquivos do projeto"
2. "Remova resumos antigos que foram consolidados"
3. "Conversas anteriores ao checkpoint podem ser arquivadas/deletadas"
4. "Próxima sessão: use [INICIAR] — o checkpoint será detectado automaticamente"

## CHECKLIST FINAL
- [ ] Todas as fontes foram consultadas?
- [ ] Nenhum artefato ativo foi omitido?
- [ ] Decisões obsoletas foram excluídas (não apenas marcadas)?
- [ ] O checkpoint é autossuficiente (não depende de conversas anteriores)?
- [ ] Próximos passos são acionáveis?
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

### 3. Upload de Arquivos (Project Knowledge)
Arrastar para "Arquivos" do projeto:
1. `metaprompt-resumo.md`
2. `metaprompt-retomar.md`
3. `metaprompt-iniciar.md`
4. `metaprompt-checkpoint.md`

### 4. Primeira Conversa
- Nova conversa no projeto → `[INICIAR]`

### 5. Ao Finalizar
- `[RESUMO]` → upload do resumo nos Arquivos → renomear conversa

## COMANDOS

| Comando       | Função                                  |
|---------------|-----------------------------------------|
| `[RESUMO]`      | Resumo completo da sessão               |
| `[RETOMAR]`     | Reconstroi contexto anterior            |
| `[INICIAR]`     | Briefing e definição de objetivo        |
| `[CHECKPOINT]`  | Snapshot consolidado do projeto inteiro |
| `[TAG]`         | Sugere título formatado                 |
| `[ARTEFATOS]`   | Lista e versiona artefatos              |
| `[VERSIONAR]`   | Analisa mudanças, sugere versões SemVer |

## TÍTULOS
Formato: `({tag})({ts})-Descrição concisa`
"""


def gen_migration_checklist(name, tag):
    return f"""# CHECKLIST DE MIGRAÇÃO: {name}

Gerado em {_iso()}.

## PRÉ-MIGRAÇÃO
- [ ] Abrir projeto "{name}" na UI
- [ ] Listar conversas (títulos e datas)
- [ ] Listar Arquivos atuais
- [ ] Identificar artefatos nas conversas

## LIMPEZA
- [ ] Remover arquivos obsoletos/duplicados
- [ ] Mover conversas de outro projeto
- [ ] Trazer conversas avulsas
- [ ] Renomear projeto (Categoria/Nome)

## APLICAR TEMPLATE
- [ ] Editar `INSTRUCOES.md` com contexto real
- [ ] Colar em "Instruções"
- [ ] Upload metaprompts:
  - [ ] metaprompt-resumo.md
  - [ ] metaprompt-retomar.md
  - [ ] metaprompt-iniciar.md
  - [ ] metaprompt-checkpoint.md

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
        "metaprompt_resumo": gen_metaprompt_resumo,
        "metaprompt_retomar": gen_metaprompt_retomar,
        "metaprompt_iniciar": gen_metaprompt_iniciar,
        "metaprompt_checkpoint": gen_metaprompt_checkpoint,
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
    elif cmd == "registry_names":
        registry_names()
    elif cmd == "generate":
        # generate <filepath> <template> <name> <tag> [role] [stack]
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
