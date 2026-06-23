# PLANO DE EXECUÇÃO — Ficha do Jogo (hospedado)

> Fonte de verdade da implementação em curso. Estruturado para `/portas-em-automatico`
> (paradas e checkpoints marcados) e como hierarquia de metas (Objetivo → Fases → Passos com *done*).
> Aprovado em 2026-06-08. Status vivo: marque `[x]` ao concluir cada passo (com auditoria 4-eixos).

## Objetivo
Publicar em `bera.ia.br/ficha-do-jogo` um **site estático multipágina** que (a) preserva o forecast
probabilístico, (b) **re-simula condicionalmente** conforme os jogos acontecem, (c) **recomenda o placar
ótimo do bolão** (EV pela tabela dacopa) e (d) compara **previsto × realizado** — com **baseline congelada**,
deploy via `wrangler`, e atualização por **uma ação local**.

## Decisões travadas (log)
- **Sequência:** Frentes 2 → 3 → 1 → 4 (do ROADMAP). Este plano é a Frente 2 + camada de produto/hospedagem,
  puxando o miolo da 3 e semeando a 1.
- **Entrada de dados / atualização:** *build local + deploy estático*. Python segue motor autoritativo local;
  estado em JSON versionado; camada de estado abstraída para um backend de nuvem ser drop-in futuro. Sem relaxar zero-dep.
- **Baseline:** congelar o `results.json` pré-torneio (imutável) + toda re-simulação futura fica timestampada.
- **Bolão (dacopa):** palpite = **placar exato por jogo**; trava **no apito inicial de cada jogo**.
  Pontuação (grupos): exato 25 · venc+gols-venc 18 · venc+saldo 15 · venc+gols-perd 12 · só venc 10 · nada 0.
  **Mata-mata = x2.** Recomendador escolhe o placar que **maximiza pontos esperados** (não o mais provável).
- **Previsto × realizado (4 dimensões):** placar prev vs real + pts bolão · prob de fase vs avanço real ·
  calibração temporal (Brier/log-loss) · modelo vs **meus palpites reais**.
- **Página do bolão (lean, mobile-first):** próximos jogos + placar + EV · minha pontuação/ranking · resumo prev×real.
- **Hospedagem:** Cloudflare. Domínio `bera.ia.br` já está na CF (522, sem origin). Deploy via **`wrangler`**
  (MCP da CF tem só KV/D1; Workers/R2 dão 403 → não deploya pelo MCP). Via: **Workers static assets**.
  URL: `bera.ia.br/ficha-do-jogo/*` (fallback subdomínio `ficha-do-jogo.bera.ia.br`).
- **Privacidade (revisado 2026-06-09):** **tudo público, sem senha, por enquanto** (decisão do Bera).
  Hoje o `state.json` está vazio ⇒ nenhum dado pessoal exposto. ⚠️ **Re-proteger `/bolao*` + comparativo
  (Cloudflare Access / basic-auth) ANTES de inserir palpites reais** durante a Copa. Site segue 100% estático.
- **Fuso:** America/Sao_Paulo (BRT) para horários de corte.

## Fases

### Fase 0 — Fundação & baseline
- [x] **0.1** Congelar `results.json` → `data/baseline/forecast_pretorneio.json` (imutável + provenance). *Done:* somas batem; provenance escrita. ✓
- [x] **0.2** `data/fixtures.json` — 72 jogos de grupo (pares de `GROUPS` + datas/horários BRT) + 32 slots KO. *Done:* 72 válidos (cross-val 0 erros), 48×3 jogos, janela 11–27/jun. ✓
- [x] **0.3** Schema `data/live/state.json` (jogos ocorridos + meus palpites) + doc no HANDOFF §5. *Done:* schema validado com exemplo. ✓

### Fase 1 — Motor condicional + recomendador
- [x] **1.1** Camada `StateStore`/`DataSource` mínima; `ManualSource` lê arquivo local; abstrata p/ backend futuro. *Done:* `src/state.py` (load/validate/build_fixed); validação negativa pega 5/5 erros. ✓
- [x] **1.2** Re-simulação condicional em `sim_once` (fixa grupo por par, KO por nº; simula o resto). *Done:* estado vazio reproduz a simulação bit-a-bit; T2 (Brasil eliminado) → 0% à frente; somas coerentes; 0 viol. ✓
- [x] **1.3** Recomendador de placar EV-ótimo (`src/bolao.py`; tabela dacopa; KO=fim da prorrogação; empate só no exato). *Done:* pontuação 11/11; EV-ótimo == força-bruta; dist. somam 1; EV-pick difere do +provável em jogos equilibrados. ✓
- [x] **1.4** Métricas prev×real (`src/metrics.py`: placar+pts · modelo vs eu · Brier/log-loss · avanço por fase). *Done:* verificadas com estado parcial e grupos completos (32 avançam). ✓

### Fase 2 — Páginas multipágina (estático-primeiro + zero-dep)
- [x] **2.1** Site multipágina: `build_dashboard` + `build_bolao` + `build_comparativo`, nav cruzada, tokens B compartilhados em `theme.py`. *Done:* 3 páginas geram, nav funciona, renderizam com JS off. ✓
- [x] **2.2** Página Bolão (B · esportivo condensado): herói + acordeão por dia + faixa de placar + prev×real + glossário. *Done:* 72 próximos, 0 JS/dep, mobile, screenshot aprovado. ✓
- [x] **2.3** Página Comparativo (B; 4 dimensões: modelo×você · calibração · placar prev×real · fase prev×real). *Done:* demo populado aprovado, mobile, 0 JS/dep. ✓
- [x] **2.4** `make_generic` (white-label) funciona no dashboard re-skinhado (0 nomes próprios de método/fonte). Bolão (protegido) e Comparativo (pessoal) não precisam de genérico público. *Done:* generico OK; 0 CDN. ✓

### Fase 3 — Deploy Cloudflare *(outward-facing)*
- [x] **3.1** Instalar/configurar `wrangler` (user-global em `~/.npm-global`, PATH no `~/.zshrc`); login OAuth. *Done:* `wrangler whoami` = beralzir@gmail.com (conta a79fcd8…). ✓
- [x] **3.2** Worker static-assets (`worker.js` tira o prefixo; `wrangler.toml`: `run_worker_first` + `html_handling="none"`) + rota `bera.ia.br/ficha-do-jogo/*`. *Done:* 200 nas 4 páginas + index, 404 em inexistente. ✓
- [~] **3.3** ~~Acesso Cloudflare Access em `/bolao*`~~ — **DROPADO por ora** (tudo público sem senha; decisão Bera 2026-06-09). ⚠️ Religar antes de palpites reais. **[parada quando reativar]**
- [x] **3.4** Primeiro deploy. *Done:* **`https://bera.ia.br/ficha-do-jogo/` NO AR** (público, sem auth; 2026-06-09). Gotcha resolvido: `html_handling` default fazia 307 `.html`→URL-limpa e perdia o prefixo → 522; `html_handling="none"` corrige. ✓

### Fase 4 — Ação de update unificada
- [ ] **4.1** ⏸️ Script `atualizar` (placares + palpites → estado → re-sim → rebuild → re-deploy). *Done:* ponta-a-ponta em teste. **[parada no re-deploy]**
- [ ] **4.2** Snapshot timestampado por run (histórico do forecast). *Done:* 2 runs = 2 snapshots, baseline intacta.
- [ ] **4.3** Doc de operação no README. *Done:* passo-a-passo testável.

## Paradas obrigatórias (`/portas-em-automatico`) — revisado 2026-06-08
- Sobrescrever a baseline congelada.
- Login/credenciais, instalar dependências/pacotes, executar código remoto ou binários.
- Integrar **fonte de dados ao vivo** (escolha de provedor, ToS/bet, chave de API, cadastro).
- **Todo deploy/re-deploy** e configuração de acesso (outward-facing).

**Liberado sem parar — política de fetch (GET/leitura):** fontes públicas e reputáveis de referência
(calendário/resultados de futebol — Wikipédia, FIFA, placares conhecidos — e documentação técnica).
Sem auth, sem enviar/publicar dados, sem baixar/instalar/executar nada.

**Guardrail (continua exigindo confirmação):** domínios suspeitos/não-reputados; qualquer login, dado
pessoal/privado ou pagamento; envio/publicação de dados; download de binários/scripts para execução;
instalação de dependências.

## Checkpoints
Ao fim de cada Fase: resumo + estado salvo + revalidação de invariantes antes de seguir.

## Invariantes a preservar (de CLAUDE.md)
Estático-primeiro · zero dependência externa no HTML · somas/monotonicidade · determinismo
(reprodutível dado o mesmo `state.json`) · contrato de dados model↔build.

## Suposições abertas (marcadas)
- `[assumido]` Placar-KO do bolão = 90 min (regulamentar) — confirmar nas regras dacopa na 1.3.
- `[assumido]` Acesso = Cloudflare Access por caminho; basic-auth como fallback — fechar na 3.3.
- `[assumido]` Forças `R` estáticas durante a Copa (melhoria do modelo = Frente 1, depois).

## Schemas novos/alterados (atualizar HANDOFF §5 ao tocar)
- `data/baseline/forecast_pretorneio.json` — cópia imutável do `results.json` pré-torneio.
- `data/fixtures.json` — calendário (match#, grupo/rodada, home, away, kickoff BRT).
- `data/live/state.json` — resultados ocorridos + meus palpites + `as_of`.
- `data/snapshots/<timestamp>.json` — histórico de forecasts condicionais.
- `wc2026_results.json` — + `bolao_pick` por jogo, métricas prev×real, bloco de estado `as_of`.
