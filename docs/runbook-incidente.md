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

### 🔴 Dado errado publicado (placar) · **edição COPA (arquivada)**
> ⚠️ **Esta seção é da edição Copa.** Os gates citados abaixo são do `src/ingest.py`, que
> serve a Copa. A edição ATIVA (Eleições 2026) usa `src/ingest_polls.py` e tem gates
> próprios: veja "Edição Eleições 2026" mais abaixo. Até 31/08/2026 esta divergência era
> um risco real, o runbook prometia proteção que a edição no ar não tinha (achado do
> `docs/plano-risco-eleicoes.md`).

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

## Edição Eleições 2026 (ATIVA) · o que protege e o que fazer

> Escrito em 31/08/2026 a partir do `docs/plano-risco-eleicoes.md`. A edição ativa lê a
> **Wikipédia**, que qualquer pessoa edita, e o cron publica sem humano no meio. As duas
> camadas abaixo existem por causa disso.

**Camada 1, entrada (`src/ingest_polls.py`).** Roda só nas pesquisas NOVAS; o histórico já
publicado não é reescrito.
- **Sanidade absoluta:** pct fora de [0,100], amostra fora de [100, 100.000], soma acima do
  teto da base. Vale para toda pesquisa.
- **Desvio vs consenso:** 25pp no modo estrito (cenário compatível) e 40pp no modo
  interseção re-normalizada, com no mínimo 3 candidatos em comum. Limiares **calibrados** no
  dado real, não chutados: reprovam 1,36% no pior caso.
- **Quarentena:** o que reprova sai de `polls.json` e vai para `data/eleicoes/quarentena.json`
  com o motivo. Mais de 3 numa rodada = `exit 4`, porque isso é quebra da fonte ou ataque.
- **Diff-before-write:** `data/eleicoes/ingest_diff.txt` mostra o que o run mudou.
- **Limite conhecido:** uma forjadura que encolhe a lista para 2 candidatos não é bloqueada
  (a re-normalização sobre 2 nomes é ruidosa demais). Ela sai marcada `corroborada: false`,
  e é a Camada 2 que a pega. Comportamento travado por teste em `src/test_ingest_polls_gate.py`.

**Camada 2, saída (`src/check_movimento.py`).** Compara o forecast novo com o último
publicado e reprova (`exit 5`) movimento acima de 10pp em share ou 20pp em P(eleito).
Referência real: entre 27/08 e 29/08 o movimento máximo foi 2,11pp. Cobre justamente as
corridas pouco pesquisadas (em GOV-RR/SEN-RR uma pesquisa vale 67,9% do agregado), onde a
Camada 1 é mais fraca.

### 🔴 Pesquisa forjada ou dado errado no ar (Eleições)
1. Olhe `data/eleicoes/quarentena.json` e `data/eleicoes/ingest_diff.txt` do run.
2. Identifique o commit: `git log --oneline -- data/live/polls.json`.
3. **Reverta:** `git revert <commit>`, ou remova a pesquisa e rode `python3 src/ingest_polls.py`.
4. Republique: `./atualizar_eleicoes.sh` (roda motor, alarme, gates) e depois `wrangler deploy`.
5. Se o número errado já circulou publicamente, rollback silencioso não basta: registre a
   correção no site. Em contexto eleitoral, um print sobrevive ao rollback.

### 🔴 A fonte mudou de estrutura e o dado sumiu em silêncio (Eleições)

**Aconteceu de verdade em 18/09/2026.** Vale a pena ler o mecanismo, porque a classe de
falha é traiçoeira: nada quebra, nada dá erro, e o alarme de completude continua verde.

**O que aconteceu.** Entre 31/08 e 18/09 a corrida presidencial caiu de 510 para 58
pesquisas estimuladas de 1º turno (menos 89%), e ninguém percebeu por 18 dias.

**Causa.** Os editores da Wikipédia quebraram o 1º turno em subpáginas:
`.../Primeiro Turno/2026/Janeiro a Agosto` e `.../Primeiro Turno/2023-2025`. Na página-mãe
sobrou só Setembro, mais Agosto **por transclusão** (um excerto da subpágina). O ingest lia
só a página-mãe, então passou a enxergar a janela 02/08 a 16/09 e mais nada. O 2º turno não
foi quebrado, e por isso não perdeu nada: a perda foi cirúrgica numa corrida e num cenário.

**Por que os alarmes existentes não pegaram.**
1. O alarme de completude do B8 (`scripts/resumo_eleicoes.py`) checa `data_quality == "ok"`,
   que mede **FRESCOR**, não **VOLUME**. A presidencial continuava recebendo pesquisa nova
   (30 em setembro), então seguiu "ok" todo dia. Perder 88% do histórico é invisível para
   um alarme de frescor enquanto sobrar uma pesquisa recente.
2. O total da base **subiu** no período (3.388 para 3.509), porque o ganho das outras 54
   corridas cobriu a perda da presidencial. Alarme sobre o total nunca pegaria: tem de ser
   **por corrida**. É esse o alarme do `src/check_volume.py`.
3. O alarme de movimento (`check_movimento.py`) também não pegaria, e corretamente: o
   agregador pondera por recência (meia-vida de 21 dias), então as 483 pesquisas perdidas
   valiam 10,4% do peso, e o forecast se moveu menos de 1pp. **O número publicado estava
   quase certo pelo motivo errado.** O estrago visível foi o gráfico, que caiu de 8 meses
   para 2 pontos.

**Correção (em `src/ingest_polls.py`).** Duas, somadas:
- o `PageWalker` passou a ler título de bloco recolhível (`{{hidden begin|title=...}}`) como
  contexto, porque é ali que mora o ano na subpágina 2023-2025;
- o ingest segue hatnote (`Ver artigo principal`, `Esta seção é um excerto de`) quando o
  alvo é **subpágina da própria página** (prefixo `Pai/Filho`). O prefixo é a trava: sem
  ele, seguir hatnote puxaria artigo alheio para dentro da corrida.
Como a página-mãe transclui um excerto da subpágina, a mesma pesquisa chega duas vezes, e o
ingest deduplica por **assinatura de conteúdo**, nunca por `id` (o `id` não é único de
propósito: variantes de cenário do mesmo instituto e data compartilham id).

**Achado de tabela junto, e ele era pior.** Ler o recolhível revelou que no GOV-SP os blocos
`{{hidden begin|title=2025}}` e `2024` vinham DEPOIS das seções de 2026 e herdavam o
`=== 2026 ===` obsoleto. Resultado: 26 pesquisas de 2025 estavam publicadas com data de 2026,
incluindo 4 do AtlasIntel de 2025-09-03 lidas como 2026-09-03, ou seja, entrando no agregado
como se tivessem 15 dias, com peso quase máximo. A correção do walker resolve isso junto.

**Se acontecer de novo.**
1. `python3 src/check_volume.py` aponta qual corrida encolheu e quanto.
2. `python3 src/ingest_polls.py --cache /tmp/wiki` guarda o HTML para inspeção sem refazer rede.
3. Compare a árvore de seções da página com o que o ingest enxerga: hatnote novo, seção
   renomeada, ano dentro de recolhível, tabela que deixou de ter classe `wikitable`.
4. **Backfill:** quando a correção traz de volta centenas de pesquisas antigas, o gate de
   plausibilidade as trata como NOVAS e quarentena em massa (foram 21 em 18/09, todas
   falso-positivo de cenário de pré-candidatura). Como pesquisa quarentenada não entra no
   `polls.json`, ela voltaria a ser "nova" todo dia e o pipeline reprovaria para sempre.
   O certo é **semear**: monte um `polls.json` provisório com a união do atual e do
   histórico recuperado, rode o ingest uma vez (o `prev_ids` sai desse arquivo) e deixe o
   gate ver só o que é genuinamente novo. Não eleve `GATE_MAX_QUAR` para fugir disso.

### 🟠 Alarme de movimento disparou, mas o movimento é legítimo
Renúncia, evento de campanha ou entrada de candidato movem muito e são reais. Depois de
conferir a origem em `ingest_diff.txt`, libere com `ALARME_OK=1 ./atualizar_eleicoes.sh`.
Nunca libere sem olhar o diff: o alarme só serve enquanto não virar carimbo.

## 🛑 Kill switch (parar o robô agora)

Em ordem de rapidez. Os dois primeiros não perdem dado.

1. **Desligar o cron:** GitHub → repo → aba **Actions** → workflow **atualizar-eleicoes** →
   menu `···` → **Disable workflow**. Efeito imediato, reversível no mesmo lugar.
2. **Tirar o poder de publicar, mantendo a coleta:** GitHub → **Settings** → *Secrets and
   variables* → *Actions* → apagar `CLOUDFLARE_API_TOKEN`. O preflight passa a encerrar sem
   erro (`run=0`), sem spam de e-mail.
3. **Revogar a credencial na origem:** painel Cloudflare → *My Profile* → *API Tokens* →
   revogar o token. Use este quando suspeitar de vazamento, não só para pausar.
4. **Tirar o site do ar** (último recurso): `wrangler rollback` volta à versão anterior do
   Worker; o dashboard da Cloudflare lista as versões publicadas.

Para religar: reative o workflow e recoloque o secret. O primeiro run seguinte republica do
estado atual do repo.

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
