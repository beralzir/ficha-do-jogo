# Runbook de incidente — Ficha do Jogo

> Plano curto de resposta a incidentes do pipeline autônomo e do site. Criado como prática aplicada
> do plano de risco (NIST CSF — funções **Responder** e **Recuperar**). Objetivo: detectar rápido,
> reverter com segurança e registrar a lição. Projeto de autor único — o "responsável" é o dono (Bera).

## O que conta como incidente
| Tipo | Exemplo | Gravidade |
|---|---|---|
| **Site fora do ar** | `bera.ia.br/ficha-do-jogo/` retorna 5xx/timeout | Alta |
| **Dado errado publicado** | placar incorreto/divergente entrou no `state.json` e foi ao ar | Alta |
| **Vazamento de credencial** | `FOOTBALL_DATA_TOKEN` ou `CLOUDFLARE_API_TOKEN` exposto | Crítica |
| **Saída do modelo anômala** | probabilidades quebradas (somas/monotonicidade) publicadas | Média |
| **Pipeline travado** | workflow falhando repetidamente, sem publicar | Baixa |

## Detecção (como você fica sabendo)
1. **E-mail de falha do GitHub Actions** — gate reprovado/divergência faz o run falhar e o GitHub avisa.
2. **Monitor de saúde** (`.github/workflows/health.yml`) — curl periódico no site; falha → e-mail.
3. **Manual** — você abre o site e vê algo errado.

## Resposta por tipo

### 🔴 Site fora do ar
1. Cheque o status do Cloudflare e se foi um deploy recente que quebrou (veja o último run do Actions).
2. **Rollback rápido:** `wrangler rollback` (volta à versão anterior do Worker) **ou** reimplante o último
   bom: `git checkout <commit-bom> -- dist && ./atualizar.sh --deploy`.
3. Confirme: recarregue o site e cheque HTTP 200 + conteúdo.

### 🔴 Dado errado publicado (placar)
> Os gates de `ingest.py` (quorum de 2 fontes, validação de nomes, plausibilidade, diff-before-write,
> append-only) existem justamente para isto **não** acontecer silenciosamente. Se mesmo assim entrou:
1. Identifique o commit que escreveu o dado errado: `git log --oneline -- data/live/state.json`.
2. **Reverta:** `git revert <commit>` (ou edite `state.json` corrigindo o jogo) — o estado é versionado.
3. Re-simule e republique: `./atualizar.sh --deploy` (re-roda motor + gate de saída antes de publicar).
4. Confirme o dado correto no site.

### 🔴 Vazamento de credencial — CRÍTICO, aja primeiro
1. **Rotacione já** o token vazado: gere um novo em football-data.org / Cloudflare.
2. Atualize **GitHub Secrets** (`FOOTBALL_DATA_TOKEN` / `CLOUDFLARE_API_TOKEN`) e o `.dev.vars` local.
3. Revogue o antigo. Se vazou em commit, considere o histórico comprometido (o segredo já rotacionado).
4. Rode um deploy para confirmar que o pipeline opera com a credencial nova.

### 🟠 Saída do modelo anômala
> O gate de saída do `atualizar.sh` (somas de probabilidade, monotonicidade, zero-dep) deve barrar isto
> antes de publicar. Se foi ao ar:
1. Republique a partir do **baseline congelado** (`data/baseline/`, imutável) ou do último snapshot bom
   (`data/snapshots/`).
2. `./atualizar.sh --deploy` e confirme as invariantes.

### 🟡 Pipeline travado
1. Veja o log do run no GitHub Actions; rode `python3 src/ingest.py` local (dry-run) para reproduzir.
2. Se for divergência de fonte, é o comportamento esperado (fail-closed) — resolva o dado, não force.

## Mecanismos de recuperação disponíveis (inventário)
- **Tudo versionado em git** (estado + saída commitados = trilha de auditoria) → `git revert` + redeploy.
- **Baseline pré-torneio congelado e imutável** (`data/baseline/`).
- **Snapshots por run** (`data/snapshots/`).
- **Deploy idempotente/reproduzível** (`atualizar.sh --deploy`).
- **Cloudflare mantém versões do deploy** (`wrangler rollback` / dashboard).

## Comunicação
- **Hoje (autor único):** o "quem notificar" é o próprio dono, via e-mail de falha do GitHub + monitor.
- **Se houver colaboradores/usuários:** definir 1 canal (ex.: e-mail/WhatsApp) e, se o site tiver público
  dependente, uma nota de status. *(A definir quando/se o projeto ganhar equipe ou usuários críticos.)*

## Pós-incidente (Recuperar → melhorar)
Depois de resolver, registre em `SESSION.md` (ou num post-mortem curto): **o que aconteceu**, **causa-raiz**,
**como foi resolvido** e **que gate/checagem teria pego** — e implemente esse gate. O ciclo de lição
aprendida é o que fecha a função **Recuperar** do NIST CSF.
