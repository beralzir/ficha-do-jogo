# SESSION — execução autônoma (portas em automático)

## Sessão 2026-06-30 — Revisão de 6 pontos (EM EXECUÇÃO · daquele-jeito + portas-em-automatico)
Pedido do Bera: revisão de 6 pontos (cache stale; cards do KO sem data + fora de ordem; datas
divergentes entre páginas; Ousado sem empate no mata-mata; manter só Baseline+Odds na Placares;
registro automático de mudanças). Varredura por 5 subagentes + leitura própria. Plano aprovado.
- **Decisão Bera (KO datas):** usar API football-data.org (`FOOTBALL_DATA_TOKEN` — NÃO está no
  ambiente local) + validar na FIFA. Premissas: datas com rótulo duplo "forecast X · dados até Y";
  goleada segue pelo selo "goleada %".
- **Plano (4 fases):** F1 infra (cache worker.js · só Baseline+Odds · datas unificadas) ·
  F2 Ousado KO aceita empate (bolao.py score_dist_ko) · F3 datas do KO (precisa token) ·
  F4 doc de revisão + checagens de regressão + rebuild/auditoria/deploy(sob OK).
- **Regra confirmada (relevante p/ F2):** dacopa KO = placar ao fim da prorrogação (90+30),
  pênaltis NÃO contam → empate na prorrogação é placar VÁLIDO exibido (avança nos pênaltis sem somar gol).
- **Progresso:**
  - [x] F1.1 — worker.js HTML `no-cache`→`no-store` + drop ETag/Last-Modified (header "antes" ao vivo confirmou no-cache+etag; "depois" só pós-deploy).
  - [x] F1.2 — build_bolao.py MODELS = só Baseline+Odds; copy "4→2 modelos" (tip/meta/hero/glossário + card do index). Leaderboard intacto.
  - [x] F1.3 — datas unificadas: helper `shell.updated_line(generated, as_of)` → "forecast 29/jun · dados até 28/jun" idêntico em dashboard/index/placares/resultados. `meta.state.as_of` já está no results.json (não precisou ler state). MO órfã removida do resultados.
  - **Auditoria F1:** py_compile OK · Σ exatas (1/2/4/8/16/32/12) · 0 viol monotonia · JS OK · artifact light 0 GTM · deps = só GTM/CC/same-origin.
  - [x] F2 (Ousado KO) — **Decisão Bera (revisada):** manter `score_dist_ko` fim-da-prorrogação (NÃO mudar p/ 90'); surfacer empate/goleada por SELO. Implementado: `bolao.draw_prob()` + `recommend["draw"]`; em build_bolao card_multi selo "pênaltis XX%" (KO, ≥0.13 — calibrado: modelo limita P(pênaltis) a ~14%) e "goleada XX%" (≥0.20). Split limpo (0 overlap). Glossário + título KO atualizados. Self-test verde.
  - [ ] F3 (datas KO) — **BLOQUEADO: precisa FOOTBALL_DATA_TOKEN** (ausente local). Plano: pedir ao Bera p/ criar `.dev.vars` com o token (gitignored) → `source .dev.vars` → fetch `/v4/competitions/WC/matches` → mapear match 73–104 → date/kickoff_brt em fixtures.json → validar na FIFA → build_bolao mostra data + ordena KO cronologicamente.
  - [ ] F4 (doc revisão + checagens regressão no CLAUDE.md + rebuild/auditoria/deploy sob OK).
- **Arquivos tocados até agora:** worker.js · src/{shell,build_dashboard,build_index,build_resultados,build_bolao,bolao}.py. results.json/motor NÃO tocados.
- **Cross-checks ativos:** deploy/push só com OK do Bera; não alargar busca; não sobrescrever baseline.


## Sessão 2026-06-22 (cont.) — Placares: Ousado de volta (toggle Leitura) + ponteiro p/ Modelos (✓ FEITO · ✓ PUBLICADO)
Pedido do Bera: o Ousado sumiu (quando a Placares virou "1 placar cada"); quer de volta p/ comparar, pois os Seguros de todos os modelos ficam parecidos (sem empate/goleada).
- **Diagnóstico (confirmado):** o Seguro (maior EV) é estruturalmente enviesado — **0 empates** nos 32 próximos jogos; o **Ousado (modal) tem 16**. Logo, comparar modelos pelo placar Seguro engana (fica tudo parecido); o diferenciador rigoroso é calibração, não placar.
- **`src/build_bolao.py`:** 2º toggle **Leitura (Seguro/Ousado)** ao lado do toggle de Modelo. Cada card mostra modelo×leitura (1 placar por vez), e a linha de comparação dos 4 + os cards "já jogados (previsto×real)" respeitam a leitura ativa. Default Seguro+baseline (JS off OK). `pv`/chips/`resl` ganharam `data-r`; CSS esconde a leitura não-ativa (`html:not([data-bold]) [data-r=bold]…`).
- **Ponteiro pro "principal":** tip + glossário agora dizem explícito que o placar é uma leitura grosseira e que a comparação RIGOROSA ("qual modelo acerta mais") é a **calibração (Brier/log-loss) em Modelos**.
- **Verificação:** build OK · 2 toggles (4 modelos + 2 leituras) · zero-dep (http:3) · JS válido · static-first (default Seguro/baseline) · Ousado 0→16 empates.
- **✓ PUBLICADO** (Bera autorizou) — Version `e3817850`; 200 nas 5 páginas.

## Sessão 2026-06-22 (cont.) — Placares = comparativo de 4 modelos + remoção do Comparativo (✓ FEITO · ✓ PUBLICADO)
Pedido do Bera: adicionar os outros modelos na Placares (usar como comparativo), toggle de 4 opções (1 placar cada); e — vendo que Placares e Comparativo encostaram — remover o Comparativo migrando o que é único.
- **`src/build_bolao.py` (reescrito):** Placares virou comparativo por jogo — toggle de **4 MODELOS** (Baseline · Aprende/Elo k40 · Mais merc./w_mkt85 · Odds/market_only), cada um = 1 placar recomendado. O modelo ativo aparece (placar/barras/xG via CSS `html[data-model]`); cada card tem linha `.cmp` comparando os 4 (ativo destacado). Default baseline (JS off OK). Revisão adversarial: pass-com-notas (estático-primeiro/zero-dep/a11y OK). Divergência real: 25% dos próximos (8/32) têm placar diferente entre os 4.
- **Consolidação (remover Comparativo):** calibração já estava em **Modelos**; **jogo-a-jogo previsto×real** → migrado p/ seção "Já jogados · previsto × real" da Placares (baseline, ✓/~/✗ + pts — único com snapshot pré-jogo honesto); **Fase · avanço previsto×real** → migrada p/ **Resultados** (aguardando 72 grupos). Página Comparativo REMOVIDA: aba (`shell.PAGES`), card (`build_index`), build + 200-check (`atualizar.sh`), `src/build_comparativo.py` deletado. `/copa2026_comparativo.html` agora é **redirect** → Placares (zero-dep, gerado por `build_index`). Docs: CLAUDE.md 6→5 páginas live.
- **Verificação:** `atualizar.sh` completo (5/5, gates verdes) · placares/resultados JS válido · zero-dep incl. redirect · baseline byte-idêntico (`8c609df9`) · 40 cards previsto×real na Placares · Fase em Resultados.
- **✓ PUBLICADO** (Bera autorizou) — Version `99c28ee4`; 200 nas 5 páginas; `/copa2026_comparativo.html` responde 200 e redireciona p/ Placares.

## Sessão 2026-06-22 (cont.) — Follow-up: Comparativo com calibração por modelo + Elo explicado (✓ PUBLICADO)
Pedido do Bera: "coloque na aba comparativo os resultados segundo o novo modelo" + "o que significa Elo".
- **`src/build_comparativo.py`:** novo bloco "Calibração por modelo · previsto × real" na seção Pontuação — **baseline + dynamic_k40 (aprende) + w_mkt85 (mais mercado)** (escolha do Bera: os dois novos), lido de `data/model_scores.json` (walk-forward, consistente com /Modelos), 👑 no menor Brier, ressalva de ruído + link p/ /Modelos. Estático, zero-dep, JS válido; números conferem com o leaderboard.
- **Elo explicado** (texto): rating onde a DIFERENÇA vira P(vitória) (~400 pts = 10×, `1/(1+10^(-Δ/400))`); no projeto aparece em 2 lugares — (1) input World Football Elo (componente do bloco "modelos"), (2) mecanismo de atualização da Fase C (sobe/desce por jogo, zero-soma, por surpresa+saldo). R_cal está em escala Elo.
- **✓ PUBLICADO** — Version `67642be2`; 200 nas 6 páginas. Baseline byte-idêntico (`8c609df9`) mantido.

## Sessão 2026-06-22 (cont.) — Fase D: UI de comparação de modelos (✓ FEITO · verificado · ✓ PUBLICADO)
Página pública "Modelos" (laboratório), estático-primeiro + zero-dep, no estilo das outras páginas. Deploy = PARADA.
- **`src/build_modelos.py`** (novo) -> `dist/copa2026_modelos.html`: (a) caixa de RESSALVAS (de `model_scores.json["caveats"]`, em destaque ANTES das conclusões); (b) **narrativa de atribuição auto-gerada** dos números ("o que funcionou, pra quê, por quê"); (c) **leaderboard de calibração** (tabela ranqueada por Brier, 👑 no melhor); (d) **odds de título por modelo** (top-8 × baseline/market_only/w_mkt85/dynamic_k40) com **selo de conditioning** (pré-torneio vs ao vivo) + nota "não compare maçã com laranja"; (e) acordeão de metodologia. Usa shell.HEAD (vira a 6ª página live, com GTM).
- **Nav/índice:** aba "Modelos" em `shell.py PAGES`; card 🧪 em `build_index.py`.
- **`atualizar.sh`:** novo passo `2/5` roda `run_models` + `compare` (escape `SKIP_MODELS=1`); `modelos` entra no rebuild e no 200-check; comentário de privacidade/palpites obsoleto removido. **Pipeline inteiro testado de ponta a ponta: gates verdes (somas OK · 0 viol · dep externas nenhuma), para antes do deploy.**
- **Verificação:** `atualizar.sh` completo (5/5, gates verdes) · página zero-dep (só GTM+CC) · JS válido · render com JS off. **Workflow adversarial 2-lentes: exatidão PASS** (números batem 100% com model_scores.json; render estático; edge cases), **honestidade pass_with_notes** (3 major de enquadramento).
- **Correções de honestidade aplicadas:** (a) label `market_only` → "Consenso de odds do mercado (já contém Opta)" (removido o enganoso "agrega valor sobre as odds"); (b) marca **†** + nota nas linhas learning ("diferença vs baseline dentro do ruído"); (c) tabela de título **separada em duas** (pré-torneio vs ao-vivo, comparáveis só dentro de cada). + bug `fc`→`PRE/LIVE_COLS` no print (pego pelo re-run completo do `atualizar.sh`).
- **Docs sincronizados:** CLAUDE.md (5→6 páginas live · mapa do harness).
- **✓ PUBLICADO** (Bera autorizou) via `atualizar.sh --deploy` — Version `fe718802`; 200 nas 6 páginas (incl. nova `/copa2026_modelos.html`). Este deploy levou ao ar as Fases A+B+C+D de uma vez. Motor byte-idêntico (`8c609df9`) → `results.json` inalterado, snapshot dedupou (sem snapshot novo).

## Sessão 2026-06-22 (cont.) — Fase C: modelos que aprendem (✓ FEITO · verificado · NÃO publicado)
Modelos que reagem à Copa + grade de pesos, no harness. Deploy = PARADA.
- **`src/learn.py`** (novo): aprendizado WALK-FORWARD (previsão do jogo G usa só jogos anteriores). `dynamic_R_timeline` = atualiza a **força blendada R** estilo Elo (zero-soma, K + saldo) a cada resultado em ordem de data; `poisson_form_timeline` = multiplicadores ataque/defesa online dos gols (taxa η). `lams_provider(cfg,fx,state)` = interface única `f(match,home,away)->(la,lb)` (estático=constante, learning=véspera). `final_strength` p/ forecast dynamic. `load_squad` (sinal de elenco dormente). Self-test: sem look-ahead (jogo 1 = R0), vencedor sobe/perdedor desce, determinístico.
- **`src/wc2026_model.py`**: `build_strengths(cfg, qual=None)` + `run_model(..., R=None, qual=None)` ganharam overrides (força aprendida / sinal de elenco). Defaults None => **baseline byte-idêntico mantido** (`8c609df9`).
- **`src/compare.py`** (reescrito): pontua direto dos CONFIGS via `lams_provider` (walk-forward). Estáticos reproduzem a Fase B EXATAMENTE (baseline 0.5720, market_only 0.5354, models_only 0.5930).
- **`src/run_models.py`** (reescrito): forecast por tipo — estático=pré-torneio; dynamic=ao-vivo reagido (R final + Monte Carlo condicionado); poisson_form=pulado (calibração-only).
- **`data/model_configs.json`**: 10 modelos (3 da Fase B + dynamic_k20/k40 + poisson_form + grade w_mkt30/70/85 + qual_heavy). `data/live/squad_signal.json` (hook vazio/dormente).
- **ACHADO (preliminar, n=40):** Brier — market_only 0.5354 < **w_mkt85 0.5557 < w_mkt70 0.5638** < dynamic_k40 0.5715 ≈ dynamic_k20 0.5716 < baseline 0.5720 < poisson_form 0.5731 < qual_heavy 0.5876 < w_mkt30 0.5893 < models_only 0.5930. Leitura honesta: **mais peso no mercado calibra melhor**; **aprender com a Copa dá empurrão fracionário (dentro do ruído)**; mais modelo/qualitativo piora. Forecasts dynamic rebaixam quem rendeu abaixo do esperado (Espanha 22.8%→18.4% no k40).
- **Verificação:** py_compile OK · baseline byte-idêntico (`8c609df9`) · determinismo md5 (compare + run_models) · invariantes/modelo OK · zero deps novas. **Workflow adversarial 3-lentes: 0 blocker, 0 bug** — sem-look-ahead PASS (before[m1]==R0; jogo G não usa resultado de G nem posteriores), matemática PASS (Elo zero-soma + margem; condicionamento dynamic = update bayesiano sem dupla contagem; estáticos reproduzem a Fase B), integração/honestidade pass_with_notes.
- **Correções pós-review (nits):** (a) ordenação walk-forward por `(kickoff, match)` — independe da ordem do `state.json`; (b) caveat explícito "ganho do learning (~0,0005) < erro-padrão (~0,008) = ruído" (caveats agora 6); (c) `load_squad` marcado dormente; (d) flag `has_forecast` (poisson_form=false) p/ a Fase D. Leaderboard inalterado após as correções.
- **Deferido p/ Fase D (flag):** distinguir visualmente conditioning `pre-tournament` (estáticos) vs `live-reacted` (dynamic) — senão "champion% por modelo" vira maçã vs laranja.

## Sessão 2026-06-22 (cont.) — Fase B: harness multi-modelo (✓ FEITO · verificado · NÃO publicado)
Fundação reutilizável p/ rodar e comparar N modelagens ao longo da Copa. Sem UI (isso é Fase D). Deploy = PARADA.
- **`data/model_configs.json`** (novo, editável à mão): registro de modelos. Pesos MECÂNICOS na escala Elo (`w_market`+`w_models` convexos, `opta_in_models`, `QUALK` aditivo, `SLOPE/HA/GOAL_DIV/MU`). Configs: `baseline` (45/35/20 atual), `market_only` (régua), `models_only`. Baseline guarda 0.5625/0.4375/0.65 p/ reproduzir a fórmula histórica bit-a-bit.
- **`src/models.py`** (novo): loader (`load_configs`/`get`/`with_env`). `with_env` aplica overrides de env (HA/SLOPE/QUALK) só no run default.
- **`src/wc2026_model.py`** (REFATORADO): extraídas `to_strength(pm,slope)`, `build_strengths(cfg)`, `run_model(cfg,n,generated,with_state)`; execução movida p/ `if __name__=="__main__"`. **Byte-idêntico provado**: md5 `8c609df9` antes==depois (com `GENERATED` fixo). `(1-0.65)==0.35` exato (Sterbenz) → zero risco ULP. `random.seed(42)` dentro de `run_model` → cada modelo independente/reproduzível.
- **`src/run_models.py`** (novo): roda todos os configs PRÉ-TORNEIO (zera `M.FIXED_GROUP/FIXED_KO`) → `data/models/<id>.json`; valida somas/monotonicidade por modelo. Determinístico (md5 idêntico em 2 rodadas).
- **`src/compare.py`** (novo): pontua cada modelo vs realidade (40 jogos) reusando `metrics` → `data/model_scores.json` + leaderboard. Brier/log-loss 1X2 (grupos), pts Seguro/Ousado, cravada exata, `value_vs_market`.
- **ACHADO (n=40, ressalva de amostra pequena):** `market_only` Brier **0.5354** < `baseline` 0.5720 < `models_only` 0.5930 → nesta amostra o **mercado puro calibra melhor que o ensemble**; misturar Opta/Elo/qual piorou. Confirma a nota de honestidade do projeto ("mercado é o melhor preditor único"). Cravada exata 1–2/40 (teto baixo).
- **Verificação:** py_compile OK · baseline default byte-idêntico (`8c609df9`) · `wc2026_results.json` intocado · zero deps novas · determinismo md5. **Workflow adversarial 4-lentes** (determinismo/scorer-math/backtest-honestidade/integração): **0 blocker, 0 bug** — lentes 1-2 PASS (Brier/log-loss/dacopa/isolamento conferidos contra cálculo manual), lentes 3-4 pass_with_notes.
- **Correções pós-review aplicadas:** (a) framing honesto do `market_only` = **consenso de odds com Opta embutido** (odds 5-9/jun pós-Opta 1/jun, corr ~0,98), NÃO 'mercado puro' — não refuta Opta/Elo; (b) ressalvas (n=40 dentro do ruído; ranking PRELIMINAR só-grupos; medição incompleta; pesos pré-especificados) emitidas em `model_scores.json["caveats"]` + impressas; (c) `print` de estado movido p/ `__main__` (sem ruído ao importar o motor); (d) stub `strength_as_of(team,date,cfg)` p/ a Fase C; (e) `with_env` cobre MU/GOAL_DIV.
- **Deferido p/ Fase D (flag):** caveats na UI (header PRELIMINAR + sem decidir aposta de finalista); doc central de honestidade; integração opcional de run_models/compare no `atualizar.sh` (hoje são pipeline de pesquisa standalone, de propósito).
- **Artefatos:** `data/models/{baseline,market_only,models_only}.json` (pré-torneio congelado) + `data/model_scores.json`. **Achado preliminar:** market_only Brier 0.5354 < baseline 0.5720 < models_only 0.5930.

## Sessão 2026-06-22 — Fase A: de-personalização + reframe "Placares" (✓ FEITO · NÃO publicado)
Plano aprovado (daquele-jeito + portas-em-automatico). Projeto pivota p/ pesquisa: **(1) remover dado pessoal de bolão**; (2) [próximas fases] harness multi-modelo + novas modelagens + UI de comparação. Deploy = PARADA.
- **Removido o dado pessoal:** camada "Você" (palpites próprios × real) do Comparativo + `award_picks` (chutes de prêmio). `my_picks`/`award_picks` saíram do schema (`state.py`), do `state.json`/`state.example.json`, das métricas (`metrics.py`: `match_reports`/`summarize` sem `my_*`/`_on_mine`; `award_report` morto removido) e da view (`build_comparativo.py`: KPI/via "Você" + CSS `.kpv/.fair` mortos removidos). **Mantido factual/modelo:** `results.awards` (vencedor real) + `awards.py`/`wc2026_awards.json` (previsão de prêmio do modelo, de-vig de mercado).
- **Reframe Bolão → "Placares"** (decisão do Bera: manter re-enquadrada): nav/card = **"Placares"**, h1 = **"Placar previsto"**; copy de "seu bolão/pra você preencher" → "placar previsto do modelo". **Rota/filename `copa2026_bolao.html` mantidos** (sem mexer em worker/deploy). Labels Seguro/Ousado mantidos (vocabulário do modelo, comum ao Comparativo). Index sub "+ bolão" removido.
- **Docs:** schema canônico atualizado (`HANDOFF.md §5`, `README.md`); logs históricos preservados. **Pendência (flag p/ Bera):** seção "Privacidade" do `README` + comentário do `atualizar.sh` ficaram obsoletos (não há mais palpite pessoal a proteger).
- **Auditoria 4-eixos:** py_compile OK · 5 páginas + generic rebuildadas · somas exatas (1/2/4/8/16/32/12) · 0 viol monotonia · 0 dep externa (3 http = CC+GTM) · artifact/generico sem GTM · `node --check` dashboard+placares OK · **0 artefato pessoal no HTML** (grep `>Você<`/`seu bolão`/`my_pick`/`award_pick` vazio). **Motor NÃO rodado** (`results.json` inalterado — Fase A é só view/schema). **NÃO publicado.**

## Sessão 2026-06-15 — Comparativo: 2º modelo (Ousado) → 3 vias (✓ FEITO · PUBLICADO)
Pedido do Bera: o bolão dele já não bate com o modelo ("e tudo bem"); quer que o **Comparativo** compare **os 2 modelos** — adicionar o **Ousado** ao lado do Seguro. Decisão dele (1 pergunta, box): **3 vias = Seguro × Ousado × Você** (mantém a via pessoal `my_picks` pronta, mesmo vazia hoje).
- **`src/metrics.py` (aditivo, retrocompatível):** `match_reports` agora calcula também `bold_pick`/`bold_pts` (palpite Ousado = `rec["bold_pick"]`) por jogo; `summarize` ganhou `bold_pts` e `bold_pts_on_mine` (versão justa nos jogos palpitados). Chaves antigas (`model_pick/model_pts`) intactas → único consumidor é `build_comparativo.py`.
- **`src/build_comparativo.py`:** resumo com **3 KPIs** (Seguro/Ousado/Você); lista jogo-a-jogo virou **mini-cards** (`.mc/.via`) mostrando o que cada via cravou (✓ cravou · ~ acertou parte · ✗ zerou); linha **"comparação justa nos seus N palpites"** quando a cobertura é parcial; legenda + rodapé reescritos. Removidos CSS/markup da tabela antiga (`.prh/.pr/.psc/.ppt`).
- **Nota de honestidade (no rodapé + linha de calibração):** Seguro e Ousado **não são 2 modelos probabilísticos** — saem da **mesma** distribuição de placar (`score_dist`), mudam só a estratégia de palpite (maior EV × placar modal); por isso a calibração 1X2 (Brier/log-loss) é **comum** às duas.
- **Via "Você":** hoje `my_picks=[]` → KPI mostra "—" + aviso "registre seus palpites pra ativar"; mini-cards mostram 2 vias. Testado com estado-demo (6 palpites em `/tmp`): 3ª via acende, comparação justa confere (Seguro 37 · Ousado 75 · Você 77 nos 6).
- **Achado:** com a 1ª rodada cheia de empates, **Ousado lidera 110 × 71 do Seguro** (o modal crava empates tipo Canadá 1-1 Bósnia, onde o Seguro zera).
- **Auditoria:** somas exatas · 0 viol monotonia · 0 dep externa (3 http = CC+GTM já existentes) · `node --check` nos 5 blocos JS OK · conteúdo renderiza com JS off (mini-cards/KPIs são Python) · screenshots dark real+demo (mobile 390px + desktop 900px).
- **Deploy (autorizado pelo Bera):** mudança **só de view** → publicado **SEM re-rodar o motor** (padrão da sessão 06-11): rebuild das 5 páginas + generic, gates do `atualizar.sh` replicados, `wrangler deploy`. `results.json` md5 **inalterado** (`edcc8f3…`), **nenhum snapshot novo** (segue 5: 03/10/12/13/14), `generated=2026-06-15` preservado. Version `967039f9`; 200 nas 5 páginas; comparativo live confere (KPIs Seguro 71 · Ousado 110 · Você —).

## Sessão 2026-06-13 — F1 (risco no bolão) + F2 (poll tracker) — EM EXECUÇÃO (portas em automático)
Plano aprovado: `~/.claude/plans/agora-como-fa-o-para-reactive-pie.md`. daquele-jeito (plano) + portas-em-automatico (execução). Deploy = PARADA.
- **F1 ✓ FEITO + auditado (NÃO publicado):** camada de risco SÓ no bolão (motor intacto).
  - `src/bolao.py`: Dixon-Coles (τ, ρ=−0.13 via `DC_RHO`) + sobredispersão Binomial Negativa (`NB_SIZE`=8) nas dists; corrige empate baixo (0-0:7,1→10,6% · 1-1:11,9→12,1%). **Mean-variance (κ·DP) DESCARTADO** — degenerado (o pick de maior EV é também o de maior DP). **Emenda aprovada pelo Bera:** Ousado = **placar mais provável (modal)** → crava ou zera; devolve empates (Brasil×Marrocos: Seguro 2-1 / Ousado 1-1). `recommend` agora dá `ev_pick`+`bold_pick`+`bold_prob`+`goleada`. `goleada_prob` (dif≥3) só informativo.
  - `src/build_bolao.py`: cada card mostra os 2 palpites (spans `.pv` safe/bold), toggle global Seguro/Ousado (`.modebar`, `html[data-bold]`, localStorage `fdj-bold`, prepaint no head), linha `.picks`, goleada% (≥25%), glossário+nota de método honesta (cita Dixon-Coles + "EV≠ganhar bolão").
  - Auditoria: bolao.py self-test OK; 7/7 + 5/5/5 node-check; somas exatas; 0 viol monotonia; 0 dep externa; artifact/generico sem GTM; metrics.py compatível (usa só ev_pick).
- **F2 ✓ FEITO + auditado (NÃO publicado):** poll tracker na página Resultados (frontend-design no visual).
  - `src/flags.py`: mapa `ISO3` (códigos FIFA: BRA/ESP/KSA/RSA/COD/CUW...) + `code3()`; auto-teste estende cobertura (48, 3-letras-maiúsculas, sem colisão).
  - `src/poll_tracker.py` (novo): lê todos os snapshots → série temporal; SVG inline gerado em Python (zero-dep, `<use href=#fl>`, sem xmlns/http); 3 métricas alternáveis (Avançar/Título/Oitavas); **default=Título** (favoritos amontoam no topo em "Avançar"); escala Y adaptativa+ticks redondos; seletor de chips (Brasil FIXO + até 5); **lápide** SVG quando a métrica plotada zera após ter sido >0,05% (validada via dados sintéticos: África do Sul cai 36→0 → pedra+bandeira+RSA); chip bandeira+sigla na ponta com dodge vertical; cores de linha por tema (`--ln-br`/`--ln1..5`); JS espelha render_svg (re-render ao trocar métrica/seleção; persiste em localStorage `fdj-tk-*`). `__main__` gera teste em /tmp (não polui dist).
  - `src/build_resultados.py`: import + `TRACKER=poll_tracker.section()`; CSS + seção `data-scene=tracker` (entre Classificação e Mata-mata) + JS.
  - Auditoria: flags+poll_tracker self-test OK; screenshots dark+light desktop+mobile + lápide + interatividade (Playwright do cache npx); somas exatas; 0 viol; 0 dep externa; node-check 7 páginas (resultados 6 scripts) OK; SVG sem xmlns/xlink.
- **✓ PUBLICADO** (Bera autorizou) via `./atualizar.sh --deploy` — Version `9c1423d3`. Motor no-op (state idêntico → results.json igual → snapshot dedupou, segue 4 snapshots, generated=2026-06-13). 200 nas 5 páginas; live confere: bolão com modebar+Dixon-Coles, resultados com tracker+lápide+alternador.
- **Novos parâmetros (env, bolao.py):** `DC_RHO`=-0.13 (Dixon-Coles), `NB_SIZE`=8 (sobredispersão). **Limitação honesta:** não ajustados aos nossos dados (defaults de literatura). Lápide do tracker é POR MÉTRICA (zera após >0,05%); no mata-mata (julho) revisar o sinal de eliminação se necessário.

## Sessão 2026-06-12 — 1ª atualização da Copa: resultados de 11/jun (✓ PUBLICADO)
Fluxo "preparo assistido" (HANDOFF_PROXIMA_SESSAO §7-B) disparado manualmente pelo Bera ("atualize o site").
- **Placares (≥2 fontes ESPN/FIFA/Sky/Flashscore, confirmados 1 a 1 pelo Bera):** match 1 México 2×0 África do Sul · match 2 Coreia do Sul 2×1 Tchéquia. Gravados em `data/live/state.json` (`as_of=2026-06-12`; **sem** `my_picks` — escopo só resultados+análise, /bolao* segue sem dado pessoal).
- **`./atualizar.sh`** (sem deploy) → re-sim condicional + 5 builders + generic. Verificação: somas exatas, 0 viol monotonia, 0 dep externa, JS node-check OK, `generated=2026-06-12`. Movimentos sensatos: avançar Coreia 69→94%, Tchéquia 71→58%, África do Sul 36→25%, México 94→99%; "O que mudou" comparando vs 10/jun (título sem movimento ≥0,5pp).
- **Deploy autorizado pelo Bera** → `--deploy` (Version `c4db1a0c`), 200 nas 5 páginas; conteúdo live conferido (gerado em 12/jun, +23pp Coreia, standings A). Snapshot `2026-06-12.json` arquivado no run do deploy (design: arquiva-antes-de-sobrescrever; no 1º run o 06-10 já estava arquivado → no-op correto).
- Próximos jogos (12/jun): match 3 Canadá×Bósnia 16h BRT · match 4 EUA×Paraguai 22h BRT → entram na atualização de amanhã.

## Sessão 2026-06-11 — 3 ajustes de UI (✓ FEITO · PUBLICADO)
**Aprovado pelo Bera** (daquele-jeito p/ planejar + portas-em-automatico p/ executar). Deploy = PARADA, como sempre.
- **(1) Bandeiras no Windows:** emojis 🇧🇷 não renderizam no Windows (sem fonte de bandeira de país). Troca por **set SVG inline** (escolha do Bera vs. fonte Twemoji). `src/flags.py` = `ISO` (48 + ENG/SCO) · `ref(name)`→`<svg class="fi"><use href="#fl-xx"/></svg>` · `SPRITE` (48 `<symbol>`). **CONSTRAINT DURA:** sem `xmlns`/`xlink`/`http` (o verificador zero-dep do `atualizar.sh` rejeita qualquer `https?://` que não seja a licença CC) — só fragmento `#fl-xx`, igual ao logo do shell. Artwork via **huashu-design**, simplificado p/ ~18px.
- **(2) Plug no PT:** `PT[k][0]=flags.ref(k)` em `pt.py` + no PT inline de `build_dashboard.py` (os 2 mapas; duplicação **mantida**, só sincronizo). Propaga p/ as 6 páginas.
- **(3) Sprite + CSS:** sprite 1×/página (após topbar) nas 4 c/ bandeira; CSS `.fi` no `shell.CSS`.
- **(4) Clicáveis no dashboard (tarefa 1):** `.kpi`/`.crow`/`.mvrow` → `openDrawer` (role/tabindex/Enter). Prêmios FORA (linha é de jogador, não seleção).
- **(5) Destaque (tarefa 2):** KPIs `byCh[:4]` → **top-3 + Brasil** (Espanha/França/Argentina/Brasil; Inglaterra sai).
- **(6) Regen + auditoria:** fluxo do `atualizar.sh` sem deploy + 4 eixos + screenshot Windows-like.
- **✓ RESULTADO:** `src/flags.py` criado (48 bandeiras SVG simplificadas via huashu-design; sprite ~20KB; `ISO`/`ref`/`SPRITE`/`CSS`; auto-teste de cobertura+zero-dep). Plugado em `pt.py` (canônico) e no PT inline do `build_dashboard.py` via `for t: PT[t][0]=flags.ref(t)`. Sprite injetado após topbar nos 4 builders com bandeira (dashboard/resultados/bolão/comparativo); index ficou de fora (usa emoji de **ícone**, não bandeira). CSS `.fi` anexado a `shell.CSS` (chega a todas via `{shell.CSS}`). Dashboard: helper `clk()` acessível (onclick+onkeydown Enter/Espaço, role/tabindex) em `.kpi`/`.crow`/`.mvrow`; KPIs trocados p/ `byCh[:3]+["Brazil"]` (robusto a dedupe). **Auditoria:** somas exatas (1/2/4/8/16/32/12), 0 viol monotonia, 0 dep-externa, **0 emoji-bandeira restante** nas 7 páginas, node-check 3/3 blocos OK, DATA JSON 48 ok, click-test KPI-Brasil/gráfico-Portugal/mvrow abre dossiê (0 pageerror), conferido visual em dark+light(artifact)+resultados. **Motor NÃO rodado** (mudança só de view; results.json intacto — respeita a parada do drift 1e-17). Regen futuro: `./atualizar.sh` ou o loop dos builders já inclui tudo. **PUBLICADO** 2026-06-11 (Version `a88051b3`) via `~/.npm-global/bin/wrangler deploy` do `dist/` verificado — deliberadamente SEM `--deploy`/re-rodar o motor (preserva `generated=2026-06-10`, evita re-stamp da data e snapshot novo). 200 OK nas 5 páginas; conteúdo ao vivo confere (sprite presente, 0 emoji-bandeira, KPIs=Esp/Fra/Arg/Bra, clicável).

## Sessão 2026-06-10 (tarde) — white-label "modelo proprietário" + pedido de redesign
- **Feito + verificado, NÃO publicado** (Bera quis revisar antes): white-label do método nas views — Mercado/de-vig→**Odds**, Opta+Elo→**Opta** (Elo escondido, inclusive scrub de "Elo" em 2 dossiês via `_wl()`), modelo→**"modelo proprietário"**, Sherman Kent→**"Escala probabilística"**; rodapé/Fontes/params sanitizados; **quadro-receita** na Metodologia (`Odds 45 + Opta 35 + Qualitativo 20 → rating proprietário → 50k sims`). **Bolão** reescrito = só recomendações (pts esp., sem `my_picks`/`award_picks`/"Modelo vs você"). **Comparativo** = 3 dimensões (Calibração · Placar prev×real do modelo · Fase; sem "Modelo×você"/prêmios). `make_generic` reescrito (variante max-anônima). Auditoria 4-eixos: invariantes intactos (motor não rodado), baseline md5 igual, zero-dep, `node --check` OK, 0 termos do segredo, comparativo populado testado.
- **Na revisão, Bera pediu REDESIGN de UI (8 itens)** → tudo em **`HANDOFF_REDESIGN.md`**: crédito + licença **CC BY-NC-ND 4.0** (© Renato Beralzir); disclosure melhor (estilo Resultados); **toggle de tema**; diferenciar botão-página/âncora/tag + **talvez quebrar o Dashboard**; nav moderna via **huashu-design + frontend-design** (autorizados nominalmente); hierarquia "Ficha do Jogo" > "Copa 2026" > descrição; **desktop responsivo** (bolão/comparativo/resultados/index hoje são só-mobile); **calculadora antes da Matriz** + destaque. **Decisão: executar em sessão NOVA** (contexto desta cheio + precisa das skills de design carregadas).
- **Deploy segue PARADA** — white-label + redesign publicam juntos no fim, com OK do Bera.

## Sessão 2026-06-10 — refresh de dados + prêmios individuais (T1+T2 do HANDOFF_PROXIMA_SESSAO)
- **T1 ✓** Snapshots: `src/snapshot.py` (dedupe md5, `SNAP_DIR`), hook no motor; `data/snapshots/{2026-06-03,2026-06-10}.json`.
  Refresh completo do `T`: **Elo REAL do eloratings.net/World.tsv — CORREÇÃO DE FONTE** (valores antigos eram
  aproximações, divergiam até ±160pts; documentado no cabeçalho do T); mkt = consenso de-vig de 6 casas completas
  (FanDuel/DK/bet365/Pinnacle/Unibet/Betfred, 5–9/jun); Opta 1/jun (rev 5/jun) com piso 0,02 nos 5 zerados;
  qual re-curado do noticiário 4–9/jun (19 mudanças, aprovadas pelo Bera 1 a 1 em tabela). Re-run: somas exatas,
  0 viol, 2×md5 idêntico. **Espanha 20→22,8% título.** `generated=2026-06-10`; "Coletado 9/jun/2026"
  (dossiês seguem curadoria 1–3/jun — anotado no Fontes). Seção **"O que mudou"** no dashboard (condicional
  via `snapshot.find_previous`; some sem histórico; sem tokens banidos → sem REP novo).
- **T2 ✓** `data/wc2026_awards.json` (Golden Boot 20 / Golden Glove 12; odds de-vigged; boot cruza com Kalshi ~15%
  Mbappé) + `src/awards.py` (devig/load/validate, auto-teste). Dashboard: seção "Prêmios" (top 10/8, barra verde
  de dado). Bolão: palpite de prêmio (**não pontua** — decisão Bera) + favoritos do mercado. Comparativo:
  acerto/erro (✓/✗/pendente). Schema estado: `award_picks` + `results.awards` (`state.py` valida; HANDOFF §5 +
  `state.example.json` atualizados; retrocompatível).
- `make_generic`: sentinela do regex agora "Coletado 9/jun/2026."; BANNED += bet365/Unibet/Betfred/BettingOdds.
- **T4 ✓** Auditoria de design (huashu-design, critique 5D; 16 cenários 390px dark+light vazio+demo).
  Nota 7,9/10. Achados aplicados (aprovados pelo Bera): **(1)⚠️** Prêmios estava na tela ~23/26 → movido p/ após
  "O que mudou" + Grupos B–L e rodadas KO pós-32avos colapsados em `<details>` nativo (renderiza sem JS) →
  dashboard **25,9 → 15,2 telas**; **(2)⚡** board Modelo×Você justa (modelo restrito aos jogos COM palpite quando
  cobertura parcial; `metrics.summarize` ganhou `model_pts_on_mine`); **(3)⚡** paths de arquivo removidos da UI
  pública do bolão; **(4)⚡** touch targets da nav 26-30px → ~38px (5 páginas); quick win: "(EV)" fora do index.
  NÃO aplicados (documentados): 💡 resultados pré-torneio 4,3 telas zeradas (janela de 1 dia); 💡 "100%" no
  comparativo-fase (arredondar ">99%"). Bateria completa re-passou (JS ok, 0 dep, 0 banidos, invariantes).
- Deploy feito 2026-06-10 (Version f995d971); site no ar = forecast 9/jun + seções novas + fixes da auditoria.

## Sessão 2026-06-10 (cont.) — itens B+C do HANDOFF_PROXIMA_SESSAO
- **B ✓ (Fase 4 do PLANO):** `atualizar.sh` na raiz (re-sim condicional → 5 builders + make_generic →
  verificação invariantes/zero-dep → **para antes do deploy**; flag `--deploy` publica+checa 200). **Fix de raiz
  do gotcha da data:** `wc2026_model.py` carimba `generated` automaticamente (`time.strftime`, override
  `GENERATED=` p/ teste) e o dashboard deriva "gerado em" de `meta.generated` (DRY, helper `_ptdate` module-level).
  README ganhou seção "Operação durante a Copa" + aviso de privacidade + árvore de arquivos atualizada. Fase 4.2
  (snapshot/run) já vinha pronta; 4.1+4.3 fechadas. Testado ponta-a-ponta sem deploy: results.json idêntico,
  snapshot não duplicou, baseline intacta.
- **C ✓ (💡 da auditoria):** Comparativo·Fase usa `pct1()` → `>99%`/`<1%` em vez de "100%/0%" enganoso (barras
  seguem com width real). Resultados pré-torneio: composição compacta em 2 colunas + chave colapsada quando 0 jogos
  → **4,3 → 1,7 telas**. Auditoria 4-eixos: invariantes ok, 0 viol, JS ok, 0 dep, 0 banidos, determinismo md5 igual.
- **Publicado** (Version e00acf77): site no ar com B+C.

## Sessão 2026-06-10 (cont.) — agendamento das atualizações da Copa
- **Pergunta do Bera:** automatizar as atualizações de madrugada via routines. **Achado honesto comunicado:**
  publicação 100% automática NÃO é viável/segura aqui — (1) sem fonte de dados ao vivo (placares entram à mão;
  placar invertido home/away é indetectável por máquina); (2) routines/cron rodam o *agente* na máquina local e só
  com o app aberto (não é cron de servidor; cron de sessão expira em 7d); (3) deploy=parada + privacidade. Insight:
  o melhor horário é **manhã** (não madrugada), pois a validação+deploy são do humano.
- **Decisões do Bera (1 a 1):** modelo de operação = **preparo assistido** (não publicação automática); escopo =
  **só resultados+análise** (sem palpites pessoais ⇒ item A não bloqueia).
- **Criado:** scheduled task durável **`copa2026-preparo-resultados`** (07:17 diário). Cada disparo: detecta jogo
  novo (no-op em dia sem jogo — robusto a remarcação/folga, NÃO hardcoda datas), busca placares em ≥2 fontes,
  PARA p/ confirmação humana (home/away+placar), aplica + `atualizar.sh` sem deploy, PARA p/ autorizar `--deploy`.
  Nunca grava/publica/toca baseline sozinho. **Remover após 19/jul** (ele avisa). Lógica no-op validada (hoje/11-jun
  manhã = 0 jogos; 12-jun manhã = 2 jogos da estreia). Calendário grupos: jogos todo dia 11–27/jun; KO datas a
  confirmar na fonte. Doc no HANDOFF_PROXIMA_SESSAO §7-B.

**Goal:** Frente 2 hospedada — ver `PLANO_EXECUCAO.md`. Modo `/portas-em-automatico` desde 2026-06-08.

## Estado atual
- **Fase 0 ✓** — baseline congelada; `fixtures.json` (72+32) cross-validado 0 erros; schema de estado.
- **Fase 1 ✓** — 1.1 estado/DataSource · 1.2 re-sim condicional · 1.3 recomendador EV · 1.4 métricas prev×real.
- **Próximo: Fase 2 — MODO COLABORATIVO, NÃO automático** (decisão do Bera 2026-06-08: a visualização pode impactar a camada de dados; então design-first → listar necessidades de dado → ajustar dados se preciso → build → revisão). portas-em-automatico segue armado p/ Fases 3–4.
  Build multipágina (index + bolão + comparativo), mobile-first, estático+zero-dep.

## Fase 2 — arquitetura (build_dashboard.py já entendido)
- Builder single-file: motor analítico `lams/grid_wdl/match_calc` (espelha o sim); pré-renderiza matriz 48×, KPIs, chart, 72 jogos, KO, Kent; 1 template + `<script>` (busca/sort/drawer/calculadora); 2 paletas dark/light → 2 arquivos.
- Plano: emitir SITE em `dist/site/` — `index.html` (dashboard atual + nav p/ as outras), `bolao.html` (lean: próximos jogos + EV-pick + EV · pontuação modelo-vs-eu · resumo prev×real), `comparativo.html` (4 dimensões de metrics.py). CSS/paleta/nav compartilhados; reusar `bolao.py`/`metrics.py` no build-time (estático-primeiro).
- Com estado vazio (pré-torneio): bolão mostra próximos jogos + EV-picks; comparativo fica "aguardando jogos"; vão preenchendo conforme a Copa anda.

## Fase 2 — progresso
- ✓ `src/bracket.py` — resolvedor da chave KO (testado: R32 com Anexo C 0 violações, 8 melhores 3ºs, progressão R16).
- ✓ `src/pt.py` — mapa bandeira/nome extraído de build_dashboard (provisório até unificar na 2.1).
- ✓ `src/build_bolao.py` → `dist/copa2026_bolao.html` — 72 próximos com EV-pick, 0 JS, 0 cdn, mobile-first. **AGUARDANDO REVISÃO do Bera.**
- DESIGN (huashu acionado pelo Bera): 3 variações → escolheu **B · esportivo condensado** (accent teal #2dd4bf, barras V/E/D, ícones ✓/~/✗, densidade organizada tipo sofascore) = **sistema do site**. `build_bolao.py` reescrito em B (produção, 72 próximos, herói + acordeão por dia, glossário, 0 JS/0 dep). EV renomeado p/ "pts esp.".
- Nits a polir no bolão: "1 jogos"→"1 jogo" (singular); subir "Modelo vs você" pro topo (Foco 2 fica enterrado abaixo de ~17 dias durante a Copa).
- ✓ **Comparativo** (`build_comparativo.py`, B, 4 dimensões: modelo×você · calibração · placar prev×real · fase; demo populado aprovado).
- ✓ **Bolão** (B, polido: singular + faixa de placar no topo).
- ✓ **Dashboard** re-skin em B: matriz 48× → **lista densa ordenável** (sem scroll lateral; flag/nome/grupo/tier + %título teal + 7 células heatmap; sort via select); accent teal; nav entre páginas; **JS preservado** (busca/sort/filtro/dossiê/calculadora), node-check OK; invariantes intactos (dados não mudaram). Backup: `src/.build_dashboard_v1.bak`.
- Pendências: tema **light** (artifact) ainda no azul antigo (adiar — site dark por ora); seções secundárias (jogos/KO/calc/gaveta) herdaram teal mas sem polimento profundo de B (opcional).
- ✓ **FASE 2 FECHADA**: 3 páginas em B (bolão, comparativo, dashboard), nav cruzada, tokens em `src/theme.py`, make_generic ok, invariantes ok, 0 CDN, JS do dashboard ok (node-check). Backup do dashboard removido.
- Pendências deferidas: tema **light** em todo o site; polimento profundo das seções secundárias do dashboard; (futuro/Frente 3) página "Resultados/Tabelas" clean separada.
- **Próximo: Fase 2.5 — REVISÃO de design/layout** (decisão do Bera): auditoria técnica + elementos úteis (refs fotmob/sofascore) + decidir todo o design via perguntas-guia. **Documento auto-contido pra sessão nova: `HANDOFF_FASE_2.5.md`.** O design "B" atual está aberto pra revisão.
- DEPOIS da 2.5: Fase 3 — deploy Cloudflare (wrangler + login do Bera; outward-facing, com paradas: login, config de acesso, deploy) → Fase 4 — ação de update.

## Fase 2.5 — progresso (design system + nova página)
**Tarefa 1 — auditoria mobile (✓):** screenshots das 3 páginas (vazio + demo populado) + crítica 5-dimensões. Achados ⚠️ críticos corrigidos: (1) jogos de grupo cortavam o visitante no mobile → reescritos no formato inline do mata-mata; (2) gaveta de dossiê transbordava (Opta/rating/bandas Kent cortados) → full-width no mobile + banda Kent abaixo do %.
**Tarefa 2 — refs fotmob/sofascore (✓):** inventário (2 subagentes). Decisão: **adicionar** página Resultados/Tabelas (standings+bracket, Foco 1, maior lacuna) + primitivos CSS-only (abas/acordeões, form guide W/E/D); **manter** matriz-heatmap/Kent/cor semântica; **remover/não buscar** shotmap/heatmap/ratings (sem dado honesto).
**Tarefa 3 — sistema de design DECIDIDO (✓):** tipografia **system-sans**; **dark** = fundo **verde-floresta `#0f1b13`** (trocado do morno `#16110b` em 2026-06-09 a pedido do Bera, pra dar mais contraste com o gold; aplicado em theme.py `_DARK` + dashboard `DARK_BODY`, re-deploy feito) + accent **gold `#f3b03c`**; **light** = cream `#f5f2e6` + accent **verde `#1a7a43`** (escolha deliberada: accent muda por tema — noite gold / dia verde); semânticas (V/E/D, Kent) **var-izadas** (mesmo significado, tom por tema, escurecidas no light); regra **accent = só cromo** (rótulos/bordas/chip/links), nunca em barra de dado (verde é a cor do DADO). Tema via **`prefers-color-scheme`** (auto). Tokens unificados em `src/theme.py` (fonte única); o dashboard usa o mesmo conjunto (DARK_BODY/LIGHT_BODY).
**Execução — APLICADO (✓):** 4 páginas reskinhadas dark+light (`dashboard.html` adaptativo; `artifact.html` light forçado); **nova `src/build_resultados.py`** → `dist/copa2026_resultados.html` (standings parcial por grupo c/ forma+zona, bracket real via `bracket.resolve_bracket` ou esqueleto de slots; aceita `STATE_FILE`/`OUT_FILE`); **nav cruzado** nas 4. ⚡ **Retrofit** (primitivos Tarefa 2 nas páginas antigas): bolão sobe "Modelo vs você" pro topo + colapsa a parede de dias numa gaveta; comparativo "ver todos" (`<details>`) no lugar do texto morto "+N"; **nav sticky** nas 4 (dashboard com topnav combinado page+âncoras). Teal antigo zerado. Tudo zero-dep, JS do dashboard node-check OK, invariantes intactos (motor NÃO rodado), `make_generic` 0 nomes próprios, `state.json` restaurado bit-a-bit a cada demo.
**Sequência de build ATUAL** (sem rodar o motor; ~3s): `for b in dashboard bolao comparativo resultados; do python3 src/build_$b.py; done && python3 src/make_generic.py`.
**Polimento — FEITO (✓):** tiers num ramo QUENTE (favorito gold → completando cinza-quente; fim do azul/teal frio); banda Kent dos KPIs **neutralizada** (não mais vermelho de "alarme" no favorito — texto em tom mut); topnav do dashboard **135→78px** (1 linha por nav, scroll horizontal, scrollbar oculta); accent gold **mantido `#f3b03c`** (testados A/B/C, Bera ficou no atual). **Aceito como está (menor/inerente, Bera ok):** tons Kent claros (lime/amarelo) lavam um pouco no light; matriz fica green-heavy no light (o heatmap É verde por design). Só `build_dashboard.py` mexido nesta onda; theme.py inalterado.

## Fase 3 — deploy (✓ NO AR, 2026-06-09)
**Site público:** **https://bera.ia.br/ficha-do-jogo/** — **sem senha** (decisão Bera; `state.json` vazio ⇒ 0 dado pessoal). ⚠️ **Re-proteger `/bolao*`+comparativo antes de palpites reais.**
- **Hospedagem:** Cloudflare **Workers static assets**. `wrangler` instalado **user-global** (`~/.npm-global`, PATH no `~/.zshrc`; vale pra Fase 4). Login OAuth (beralzir@gmail.com, conta `a79fcd8cefe300c4d36f6175cec7d8a4`).
- **Arquivos novos (root):** `worker.js` (roteador: tira `/ficha-do-jogo`, `/`→index, serve via `env.ASSETS`); `wrangler.toml` (`[assets]` dir=`./dist`, `run_worker_first=true`, **`html_handling="none"`**, rota `bera.ia.br/ficha-do-jogo/*`, account_id fixo). `src/build_index.py` → `dist/index.html` (landing das 4 páginas, sistema 2.5).
- **Gotcha (resolvido):** com `html_handling` default, `.html` dava 307→URL-limpa e o Location **perdia o prefixo** → 522. `html_handling="none"` (serve a `.html` exata) + worker tratando `/`→index resolveu. Verificado: 200 nas 4 + index, 404 em inexistente.
- **Re-deploy / update:** do root do projeto, `~/.npm-global/bin/wrangler deploy` (após `build_index.py` + os builders). É a base da **Fase 4 (ação de update unificada)**.

## Arquivos da Fase 0–1
- `data/baseline/{forecast_pretorneio.json, PROVENANCE.md}`, `data/fixtures.json`, `data/live/{state.json,state.example.json}`
- `src/build_fixtures.py` · `src/state.py` · `src/bolao.py` · `src/metrics.py`
- `src/wc2026_model.py` (re-sim condicional: FIXED_GROUP/FIXED_KO; overrides STATE_FILE/OUT_FILE)
- docs: `HANDOFF.md` §5, `PLANO_EXECUCAO.md`

## Regras dacopa (confirmadas com o Bera)
- Placar exato 25 · venc+gols-venc 18 · venc+saldo 15 · venc+gols-perd 12 · só venc 10 · nada 0. **KO = x2.**
- **KO:** vale placar ao fim da prorrogação (90+30); **pênaltis não contam**.
- **Empate real:** só o placar exato pontua (0 nos demais).

## Verificações Fase 1
- Estado vazio → simulação **bit-idêntica** à baseline (RNG-neutral). T2 (Brasil eliminado) → 0% à frente.
- Recomendador: pontuação 11/11; EV-ótimo == força-bruta; EV-pick difere do +provável em jogos equilibrados.
- Métricas: placar+pts, modelo-vs-eu, Brier/log-loss, avanço (32) — ok com estados sintéticos.

## Pendências/limitações anotadas (não bloqueiam)
- baseline/results diferem ~1e-17 em mkt/consensus (pré-existente, cosmético; NÃO regenerar — parada).
- ko_t fixado assume input consistente com a chave; phase_advance só nível "avanço" (rounds KO depois).
- Recomendador usa R_cal (1 casa) — λ ~1e-3 de imprecisão, irrelevante.

## Como testar sem tocar no real
`STATE_FILE=... OUT_FILE=... NFINAL=5000 python3 src/wc2026_model.py` (caminhos ABSOLUTOS; CWD pode estar em src/).

## Frente 2 — fonte de dados ao vivo: api-futebol.com.br (avaliado 2026-06-09, subagente)
- Fit técnico bom (REST/JSON/Bearer/IDs estáveis) → encaixa no `DataSource`. Cobre Copa 2026 + endpoint ao-vivo.
- MAS: ao vivo (placar/minuto/eventos/escalações) é **PAGO**; sem xG/stats avançadas; só polling.
- NÃO verificado (site bloqueia leitura automática): preço BRL, limites do grátis, **ToS (cláusula apostas/bolão = MAIOR RISCO)**, nomes exatos (provável PT → precisa de-para PT→EN, invertendo o pt.py).
- **Recomendação: MANTER manual agora** (já basta, custo zero, zero risco ToS). API = adaptador futuro opcional, só se o Bera ler ToS logado + achar tier ao-vivo acessível. Plano e páginas atuais INALTERADOS.

## Paradas obrigatórias ativas
sobrescrever baseline · login/deploy (Fase 3) · integrar fonte de dados ao vivo. (fetch público = liberado.)
