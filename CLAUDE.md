# CLAUDE.md — contexto do projeto (leia antes de editar)

> **ESTADO ATUAL (29/08/2026, noite):** a edição **ELEIÇÕES 2026 está ATIVA na raiz** (`/`,
> `/presidencial`, `/uf-xx`, `/modelos`), publicada após validação local do Bera (Fase B B0-B7).
> A **Copa 2026** segue arquivada em `/ficha-do-jogo/copa2026/` (snapshot congelado; não
> regenerar; slugs antigos da raiz dão 301 pro arquivo). **Pipeline da edição:**
> `src/ingest_polls.py` (Wikipédia + âncora TSE; decisão em `docs/fontes-eleicoes.md`) →
> `src/eleicoes_model.py` (agregador+MC, invariantes no run) → `src/build_eleicoes.py`
> (30 páginas) · harness `eleicoes_run_models.py`/`eleicoes_compare.py` (freezes + leaderboard;
> métrica pré-especificada) · schemas em `docs/handoff-eleicoes.md`. **REGRA mantida:** conteúdo
> NOVO de Eleições valida LOCAL com o Bera antes de deploy; correção do arquivo Copa publica
> direto. Crons da Copa off; `health` ativo; cron `atualizar-eleicoes` = etapa B8.

Projeto: modelo probabilístico da Copa do Mundo 2026 + dashboard HTML. Stack: **Python 3 (só stdlib)**
para o modelo/build; **HTML/CSS/JS puro** (zero dependências, zero CDN) para a saída.
Origem: bolão de trabalho; objetivo de pesquisa: testar modelagem probabilística em esporte e seu uso em apostas.

## Mapa rápido
- `src/wc2026_model.py` — motor Monte Carlo. Lê `data/worldcup2026_structure.json`, escreve `data/wc2026_results.json`.
- `src/build_dashboard.py` — gera `dist/copa2026_dashboard.html` (dark) e `copa2026_artifact.html` (light) a partir de `data/*.json`.
- `src/make_generic.py` — pós-processa o dashboard em versão white-label (`dist/..._generico.html`). Rode por último.
- **Harness multi-modelo (pesquisa):** `data/model_configs.json` (registro de modelos) · `src/models.py` (loader) · `src/learn.py` (modelos que aprendem com os jogos, walk-forward) · `src/run_models.py` (congela forecasts → `data/models/<id>.json`) · `src/compare.py` (leaderboard de calibração → `data/model_scores.json`) · `src/build_modelos.py` (página "Modelos"). Rodam no `atualizar.sh` (passo 2/5; pule com `SKIP_MODELS=1`).
- **Automação (atualização hands-off):** `src/ingest.py` (puxa placares de football-data.org + ESPN com gates/quorum → `data/live/state.json`), `src/test_ingest.py` (15 testes offline), `.github/workflows/atualizar-copa.yml` (cron → ingest → re-simula → gate → deploy Cloudflare). Setup e operação: `docs/automacao-setup.md`. Segredos via env/GitHub Secrets — NUNCA no repo (`.dev.vars`, `docs/Football-data.md`, `.api_cache/` são gitignored).
- `data/` — entrada (structure, dossiers, model_configs) e saída (results, models/, model_scores).
- **Arquivo da edição (pós-Copa):** `dist/copa2026/` = edição CONGELADA, servida em `/ficha-do-jogo/copa2026/`
  (gerada por `src/make_snapshot.py` + `src/build_retro.py`; NÃO regenerar em build normal). A medição foi
  fechada por `src/finalize_scores.py` (`model_scores.json` com `measurement_complete: true`; `compare.py`
  recusa sobrescrever). Retrospectiva técnica: `docs/retrospectiva-copa2026.md`.
- `HANDOFF.md` — detalhes de arquitetura, modelo e limitações. `ROADMAP.md` — o trabalho a fazer. `docs/DESIGN_BASELINE.md` — UI atual.

## Como rodar / regenerar tudo
```bash
cd src && python3 wc2026_model.py && python3 build_dashboard.py && python3 make_generic.py
```
~10s no total. Determinístico (`random.seed(42)` + iterações de set ordenadas). Sem instalar nada.

## Parâmetros do modelo (em `wc2026_model.py`)
- Pesos do ensemble: **mercado 45% / modelos (Opta+Elo) 35% / qualitativo 20%**.
- `SLOPE=56` (separação de favoritos), `QUALK=110` (peso do ajuste qualitativo, ±~22 Elo),
  `HA=30` (vantagem de anfitrião), `GOAL_DIV=130` e `MU=2.65` (modelo de gols), `N=50000`.
- Todos sobrescrevíveis por env var (`SLOPE=… HA=… NFINAL=… python3 wc2026_model.py`).

## INVARIANTES — não quebrar (são testados/visíveis)
1. **Coerência de somas** na saída: Σtítulo=100%, Σfinal=200%, Σsemi=400%, Σquartas=800%,
   Σoitavas=1600%, Σavançar=3200%, Σvencer-grupo=1200%.
2. **Monotonicidade** por seleção: campeão ≤ final ≤ semi ≤ quartas ≤ oitavas ≤ avançar.
3. **HTML estático-primeiro**: a página renderiza conteúdo COM JavaScript desativado
   (tabela, KPIs e gráfico são pré-renderizados em Python; o JS só adiciona busca/ordenação/filtro/dossiê/calculadora).
4. **Zero dependência externa** (com 1 exceção aprovada — GTM): nada de CDN, fontes remotas ou libs;
   tudo inline. (Requisito do usuário porque o visualizador embutido bloqueia scripts externos.)
   **Exceção:** o tagueamento GA4 via **GTM** carrega `googletagmanager.com` — a *única* dep externa,
   **só nas 5 páginas live** (dashboard, resultados, placares, modelos, index — injetado em `shell.HEAD`/`shell.GTM_NOSCRIPT`/`shell.TRACK`). O `track.js`
   é **inline** (`shell.TRACK`), não arquivo, de propósito: o gate `_ext` do `atualizar.sh` reprova
   `<script src=…>` mesmo same-origin. `artifact.html` (light) e `..._generico.html` (white-label)
   continuam **zero-dep** — o GTM é removido na build dessas variantes (`build_dashboard.py` na light,
   `make_generic.py` no generico). O gate `_ext` libera `googletagmanager.com` (além do link CC).
   NÃO trate o GTM como bug a remover. Detalhes: `docs/ga4-setup.md` · `site.config.json`.
5. **Contrato de dados** entre `wc2026_model.py` e `build_dashboard.py` (schema de `wc2026_results.json` — ver HANDOFF.md §Schemas). Se mudar o schema, atualize os dois lados.
6. **Determinismo**: qualquer iteração sobre `set`/`dict` que afete resultado deve ser ordenada (`sorted(...)`); não confie em ordem de hash.

## Convenções
- Nomes de seleção em **inglês** como chave canônica (ex.: "United States", "Ivory Coast", "Czechia");
  a tradução PT-BR e a bandeira ficam no `PT` map em `build_dashboard.py`.
- Probabilidades sempre em fração [0,1] no JSON; formatação (%) só na camada de view.
- O dossiê (`data/wc2026_dossiers.json`) é texto curado à mão por seleção — não é gerado.

## Verificação antes de declarar "feito"
```bash
# somas/monotonicidade
python3 - <<'PY'
import json;d=json.load(open('data/wc2026_results.json'))['teams']
s=lambda k:sum(d[t][k] for t in d)
print({k:round(s(k),2) for k in ['champion','final','sf','qf','r16','advance','group_win']})
print('monotonic viol:',sum(1 for t in d if any(d[t][a]+1e-9<d[t][b] for a,b in
 [('advance','r16'),('r16','qf'),('qf','sf'),('sf','final'),('final','champion')])))
PY
# sintaxe do JS embutido
node --check <(python3 -c "import re;print(re.findall(r'<script>(.*?)</script>',open('dist/copa2026_dashboard.html').read(),re.S)[-1])")
```

## Notas de honestidade (não vender além do que entrega)
- O mercado de apostas é o melhor preditor único; o modelo o reproduz/integra, não o supera de forma confiável.
- Modelo de gols = Poisson **independente** (bom p/ 1X2 e xG; subestima placares correlacionados como 1-1).
- Mercado e Opta não são independentes (Opta usa odds como insumo) — evite dupla contagem ao mexer nos pesos.
- Alocação dos 8 melhores terceiros usa os **conjuntos de grupos permitidos do Anexo C** + pareamento determinístico; não replica o critério de desempate canônico exato da FIFA (impacto desprezível no agregado).
