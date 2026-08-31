# SESSION.md · checkpoint (portas-em-automatico)

**Sessão:** 29/08/2026 · **Missão:** Fase B da edição Eleições 2026 (checklist B0-B8 de
`docs/plano-fase-b-eleicoes.md`, aprovado pelo Bera nesta sessão: clique "Aprovar e soltar").
Branch `eleicoes-2026` (draft PR #6), worktree `objective-euler-a7e1e4`.

## Regras da edição (não deixar decair)

- **NADA de Eleições vai ao ar sem validação LOCAL do Bera** (`wrangler dev` porta 8787 via
  `.claude/launch.json`); deploy/push/merge do PR #6 = pausas duras do portas.
- Rebase sobre origin/main antes de qualquer push.
- Pergunta com até ~4 opções → `AskUserQuestion` (clicável), UMA decisão por vez.
- PT-BR sem travessão espaçado " — " (vírgula/dois-pontos/parênteses).
- Skills manual-only: re-anunciar no momento do uso (risca-de-giz usada no B1 com re-anúncio;
  frontend-design autorizada para B6; cão-guia e tags-bera só na Fase C).

## Estado da Fase B

- [x] **B0 setup:** `wrangler dev` ok na 8787 (launch.json já existia no worktree); 6 rotas 200
      (/, /dashboard, /copa2026/, /copa2026/retrospectiva, /modelos, /resultados); dist/ do
      worktree byte-idêntico ao live.
- [x] **B1 schema da marca:** `~/Workspaces/design-schemas/ficha-do-jogo.md` criado via
      risca-de-giz (37 tokens com procedência, 6 guardrails; dark verde-floresta + cromo dourado
      fixo, light por toggle; theme.py segue sendo a fonte de build). Gate `check_schema.py`
      exit 0. **Bera aprovou por leitura; o COMMIT no repo design-schemas é dele** (clique:
      "Aprovar; commit fica comigo").
- [x] **B2 fontes de pesquisas:** decisão do Bera (clique): **Wikipédia PT primária (27/27
      corridas confirmadas, gov+Senado) + âncora PesqEle/TSE (existência+completude) +
      candidaturas TSE (SQ_CANDIDATO; status no arquivo COMPLEMENTAR) + conferência Gazeta**.
      Tudo documentado com evidências em `docs/fontes-eleicoes.md`. Fatos críticos: TSE não
      publica percentuais estruturados; 403 Akamai fora de navegador (testar do CI na B8);
      Senado 2 votos com base de divulgação mista (re-normalizar por pesquisa); CSV TSE
      latin1/`;`/aspas; DF só no BRASIL.csv.
- [x] **B3 estrutura de dados:** `data/eleicoes2026_structure.json` REAL (55 corridas, 529
      candidatos; chave = SQ_CANDIDATO) gerado por `src/build_eleicoes_structure.py` a partir
      de `data/live/candidatos_raw.json` (dump da API DivulgaCandContas capturado via
      navegador; TSE dá 403 Akamai p/ scripts; transferência por form POST local com SHA-256
      conferido). Gate `src/test_eleicoes_structure.py` VERDE (contagens 13/198/318 = zip
      oficial; determinismo; 4 warns reais de registro sub judice declarados). Schema
      polls.json v1 + handoff da edição em `docs/handoff-eleicoes.md`.
- [x] **B4 motor:** `src/ingest_polls.py` (Wikipédia → polls.json: 3.358 pesquisas, 55/55
      corridas, datas 99,6%, base do Senado detectada, aliases curados; fix crítico: partido
      por igualdade exata, PSD caía no pool do PSDB) + `src/eleicoes_model.py` (agregador
      recência/amostra/house-effect + MC 20k: indecisos, choque nacional por bloco, 2º turno
      condicional por par, Senado top-2; invariantes no run; prior declarado). 6,6s, seed 42.
      Sanidade revisada (RS: líder do 1ºT perde o condicional, mecanismo correto).
- [x] **B5 harness:** model_configs (baseline + 4 variantes + slots fundamentos/synths),
      `eleicoes_run_models.py` (freezes diários idempotentes; 5 gravados de 2026-08-27),
      `eleicoes_compare.py` (métrica PRÉ-especificada: MAE share vs próxima pesquisa <=14d;
      Brier no fim; measurement_complete trava). Comparador provado retroativamente (51
      corridas, MAE 4,2pp).
- [x] **B6 páginas:** `src/build_eleicoes.py` → 30 páginas (index fichas, presidencial com
      gráfico SVG, 27 UFs com Senado 2 vagas, Modelos). Shell/theme reusados; assinaturas:
      banda de incerteza listrada + chips de qualidade. Gates zero-dep/js verdes; light e
      mobile verificados no navegador (bug real corrigido: faltava body{background} e o
      title-case comia siglas JHC/ACM).
- [x] **B7-staging:** virada aplicada LOCAL (worker.js: raiz=eleições, /presidencial,
      /uf-xx, /modelos; Copa 301 → /copa2026/*; .html → canônico). Matriz de 12 rotas ok;
      invariantes da Copa intactas. Roteiro de QA: `docs/qa-virada-eleicoes.md`.
- [x] **B7 PUBLICADO (29/08, noite):** Bera validou local e clicou "Validei; autorizo
      publicar". Rebase sobre origin/main (1 conflito SESSION.md, resolvido pró-branch) →
      push → PR #6 ready → merge (9bcdf05) → `wrangler deploy` (versão 0141810d) →
      verificação live 100% (11 rotas, 301s, no-store na raiz, 1h no arquivo, CSP).
      **bera.ia.br/ficha-do-jogo é a edição Eleições 2026.**
- [x] **B8 automação:** workflow `atualizar-eleicoes` (cron diário 10:37 UTC até 01/11;
      sonda TSE em observação: CI recebeu 403 como esperado; alarme de completude no
      summary) + `atualizar_eleicoes.sh` (motor+harness+build+gates; deploy é parada) +
      `health` com step próprio de /presidencial. Ciclo hands-off no CI: ingest achou
      pesquisa nova, as_of avançou p/ 28/08, 5 freezes novos, LEADERBOARD COM COMPARAÇÕES
      REAIS (baseline mae 1,1pp; recencia_curta 2,25pp), gates verdes (após fix do
      node--check via arquivo temporário: process substitution não roda no Linux).
      **RESOLVIDO em 31/08:** Bera rotacionou o CLOUDFLARE_API_TOKEN (e removeu o
      FOOTBALL_DATA_TOKEN sem uso); run 33386479504 fechou o 1º CICLO HANDS-OFF COMPLETO:
      ingest (2 pesquisas novas) -> gates -> deploy -> commit automático b293405 -> site
      live atualizado pelo robô (as_of 29/08, 3.360 pesquisas). FASE B 100% ENCERRADA.

## Decisões do Bera nesta sessão

1. Checklist B0-B8 aprovado como proposto, execução em portas-em-automatico.
2. Schema da marca v0.1.0 aprovado por leitura; commit do design-schemas fica com ele.

## Fatos úteis

- Datas: 1º turno 04/10/2026 · 2º turno 25/10/2026 · registro de candidaturas fechou 15/08/2026.
- Senado 2026: 2 vagas por UF (54 no total), sem 2º turno.
- `[assumido]` do plano: mercados de previsão FORA da v1 do motor.
- dist/ é versionado; builders não limpam dist/; push NÃO dispara deploy; CI é a fonte dos bytes.
