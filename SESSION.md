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
- [ ] B3 estrutura de dados (`data/eleicoes2026_structure.json` + schema polls.json + validador).
- [ ] B4 motor (`src/eleicoes_model.py`: agregador → Monte Carlo; invariantes; prior declarado).
- [ ] B5 harness multi-modelo (model_configs da edição, freezes, leaderboard walk-forward).
- [ ] B6 páginas (index cards, dashboard presidencial, template UF, Modelos; frontend-design).
- [ ] B7 validação do Bera + virada (merge PR #6, redirects, deploy = PAUSA DURA).
- [ ] B8 automação (`atualizar-eleicoes`, health, alarme de completude).

## Decisões do Bera nesta sessão

1. Checklist B0-B8 aprovado como proposto, execução em portas-em-automatico.
2. Schema da marca v0.1.0 aprovado por leitura; commit do design-schemas fica com ele.

## Fatos úteis

- Datas: 1º turno 04/10/2026 · 2º turno 25/10/2026 · registro de candidaturas fechou 15/08/2026.
- Senado 2026: 2 vagas por UF (54 no total), sem 2º turno.
- `[assumido]` do plano: mercados de previsão FORA da v1 do motor.
- dist/ é versionado; builders não limpam dist/; push NÃO dispara deploy; CI é a fonte dos bytes.
