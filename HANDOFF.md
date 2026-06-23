# HANDOFF — Copa do Mundo 2026 (modelo + dashboard)

Documento de transferência para evolução no Claude Code. Cobre **o que existe**, **como funciona**,
**os contratos de dados** e **as limitações**. O trabalho a fazer está no `ROADMAP.md`.

---

## 1. Propósito e contexto
- **Origem:** bolão de futebol entre colegas de trabalho.
- **Objetivo de pesquisa:** testar modelagem probabilística aplicada a esporte e regras de torneio, e
  avaliar o potencial da abordagem para **apostas (bet)**.
- **Entregável atual:** dashboard HTML estático e interativo com, para as 48 seleções: probabilidade
  por fase (vencer grupo → avançar → oitavas → quartas → semi → final → título), **resultado e gols
  de cada jogo** (1X2, xG, placar provável), confrontos prováveis do mata-mata, calculadora de confronto
  e dossiê qualitativo por seleção.
- **Snapshot:** dados coletados 1–3/jun/2026 (pré-torneio). Torneio: 11/jun–19/jul/2026.

---

## 2. Arquitetura e fluxo de dados

```
                 (curado à mão)                 (motor)                  (view)
data/worldcup2026_structure.json ─┐
data/  (T dict embutido no .py) ──┼─►  src/wc2026_model.py  ──►  data/wc2026_results.json ──┐
                                  │       Monte Carlo 50k                                   │
                                  │                                                         ▼
data/wc2026_dossiers.json ────────┴──────────────────────────►  src/build_dashboard.py ──► dist/*.html
                                                                       (estático-primeiro)   │
                                                                                             ▼
                                                                  src/make_generic.py ──► dist/..._generico.html
```

- **3 estágios desacoplados**: (1) simular → `results.json`; (2) renderizar → HTML; (3) white-label.
  Cada um roda sozinho; o contrato entre eles é o JSON.
- **Sem build system, sem deps**: só `python3` (stdlib) e um navegador.

---

## 3. O modelo (`wc2026_model.py`) em detalhe

### 3.1 Entradas por seleção
Hardcoded no dict `T` (48 entradas), mais o `data/worldcup2026_structure.json`:
- `elo` — World Football Elo (eloratings.net), jun/2026.
- `mkt` — probabilidade de título implícita do **mercado**, já **de-vigged** (margem removida), consenso de casas BR/EUA/EU.
- `opta` — probabilidade de título do **supercomputador Opta**.
- `qual` — sinal qualitativo em **[-0.20, +0.20]** (curado da síntese de jornalismo: lesões, forma, técnico, momento; + = subvalorizado pelo mercado, − = supervalorizado).

### 3.2 Rating de força (ensemble 45/35/20)
Tudo é levado à escala Elo e combinado:
```
S_mkt[t]  = MEAN_ELO + SLOPE * (ln(mkt[t])  − média(ln mkt))
S_opta[t] = MEAN_ELO + SLOPE * (ln(opta[t]) − média(ln opta))
R[t] = 0.5625*S_mkt[t]  +  0.4375*(0.65*S_opta[t] + 0.35*elo[t])  +  QUALK*qual[t]
```
- `0.5625 = 45/80` e `0.4375 = 35/80` (mercado vs modelos, dentro da parcela não-qualitativa).
- `SLOPE=56` controla quanto as odds de título separam as forças; `QUALK=110` → o qualitativo desloca ±~22 Elo.
- Converter prob. de título (log-linear) em força é uma aproximação: ver §6 (limitações).

### 3.3 Modelo de partida (Poisson)
```
d   = (R_a + HA·[a é anfitrião]) − (R_b + HA·[b é anfitrião])
λ_a = max(0.15, MU/2 + (d/GOAL_DIV)/2)      λ_b = max(0.15, MU/2 − (d/GOAL_DIV)/2)
gols ~ Poisson(λ) independentes
```
`HA=30`, `GOAL_DIV=130`, `MU=2.65`. Anfitriões: EUA, México, Canadá (mando em todos os jogos).
Mata-mata: 90' → se empate, prorrogação (λ×0.34) → se empate, pênaltis `p = clamp(0.5 + (R_a−R_b)/4000, .2, .8)`.

### 3.4 Simulação da chave (Monte Carlo, N=50.000)
Por simulação: 72 jogos de grupo → classificação (desempate **pontos, saldo, gols pró, aleatório**) →
**8 melhores terceiros** (ranqueados por pontos/saldo/gols) → alocação aos 32-avos pelos **conjuntos
de grupos permitidos do Anexo C** (pareamento por caminho aumentante, determinístico) → mata-mata
até a final, seguindo o mapeamento de `structure.json`. Conta-se, por seleção, a frequência de
alcançar cada fase, gols pró/contra e jogos; e a frequência de cada **confronto** por jogo 73–104.

### 3.5 Saída
`data/wc2026_results.json` (ver §5). Numbers determinísticos (seed 42 + iterações ordenadas).
Snapshot atual (топ): Espanha ~20% · França ~14% · Argentina ~10% · Inglaterra ~9% · Portugal ~8% · Brasil ~6%.

---

## 4. A view (`build_dashboard.py`)
- **Estático-primeiro**: a tabela (48×fases, heatmap), os KPIs, o gráfico de título (barras CSS),
  os 72 jogos de grupo, os confrontos do mata-mata e a tabela Kent são **pré-renderizados em Python**
  e gravados no HTML. O `<script>` final só liga interatividade (busca, ordenação, filtros, gaveta de
  dossiê, calculadora de confronto). **Funciona com JS desligado.**
- **Calculadora**: reimplementa o motor de partida em JS (mesmas fórmulas/params) para qualquer par de seleções.
- **Duas paletas**: dark (`copa2026_dashboard.html`) e light (`copa2026_artifact.html`), via CSS vars.
- **Sherman Kent**: cada probabilidade recebe uma banda verbal (Quase certo ≥93% … Remoto <7%) — camada de comunicação, não fonte de dado.
- `make_generic.py` remove nomes de método/fonte (Opta, Elo, Sherman Kent, Poisson, Monte Carlo, casas, veículos) preservando números e layout.

---

## 5. Contratos de dados (schemas)

### `data/worldcup2026_structure.json`
```
groups: {A..L: [4 nomes]}            host_slots: {Mexico:A1, Canada:B1, United States:D1}
r32: [{match, home, away, third_from?}]   third_slot_match_order: [...]
r16/qf/sf: [{match, home:"W##", away:"W##"}]   final: {...}
```
`home`/`away` são slots: `"1A"` (1º grupo A), `"2B"` (2º grupo B), `"3rd"`+`third_from:[grupos]`, `"W74"` (vencedor do jogo 74).

### `data/wc2026_dossiers.json`  (curado à mão)
`{ <Nome EN>: {tier, coach, stars, inj, form, hist, edge, risk, read} }` — strings PT-BR.

### `data/wc2026_results.json`  (SAÍDA do modelo)
```
teams: { <Nome EN>: {
   group, group_win, advance, r16, qf, sf, final, champion,   # frações [0,1]
   g_for, g_ag, mp,                                            # gols pró/contra e jogos esperados
   mkt, opta, consensus, elo, R_cal, qual } }
matchups: { "<match#>": [[timeA, timeB, freq], ... top 8] }
meta: { N, weights, generated, HA, SLOPE, QUALK, GOAL_DIV, MU }
```

### `data/fixtures.json`  (calendário — gerado por `src/build_fixtures.py`)
```
tz: "America/Sao_Paulo"
group:    [ {match, stage:"group", group, home, away, city, date, kickoff_et, kickoff_brt} ]   # 72
knockout: [ {match, stage:"R32|R16|QF|SF|Final|3rd", home, away, third_from?} ]                 # 32 slots
```
Confrontos de grupo são DERIVADOS de `structure.json` (autoritativos) e cross-validados contra o calendário
oficial (ESPN, 2026-06-08). `home`/`away` no grupo é cosmético (vantagem de anfitrião vale p/ EUA/MEX/CAN
em qualquer ordem). KO é slot-based (`"1A"`, `"2B"`, `"3rd"`, `"W74"`) até os grupos fecharem. `BRT = ET + 1h`.

### `data/live/state.json`  (estado ao vivo — entrada manual)
```
as_of: "YYYY-MM-DD"    tz: "America/Sao_Paulo"
results: {
  group:    [ {match, hg, ag} ]                                       # gols de home/away conforme fixtures.json
  knockout: [ {match, home, away, hg, ag, winner, decided_by:"reg|et|pens"} ]  # times reais; hg/ag = placar que conta no bolão = FIM DA PRORROGAÇÃO (pênaltis NÃO contam); winner fixa a chave
  awards:   { golden_boot?: {player, team}, golden_glove?: {player, team} }    # prêmio CONHECIDO (preencher só ao fim do torneio); team = chave EN canônica
}
```
Estado vazio (`results` sem jogos) ⇒ re-sim condicional = forecast completo (≈ baseline). Ver `state.example.json`.

---

## 6. Limitações conhecidas (atacáveis no roadmap)
1. **Poisson independente** — não modela correlação entre placares (subestima 0-0/1-1, superestima goleadas); 1X2 e xG ficam bons, placares exatos nem tanto. → Dixon-Coles / Poisson bivariado.
2. **Título→força via log-linear** — converter prob. de título (que já embute a chave) em "força" e re-simular embute leve dupla contagem do sorteio; mitigado pela calibração de `SLOPE`, mas não é limpo. → usar **odds de partida** reais, não só de título.
3. **Mercado × Opta correlacionados** — Opta usa odds como insumo; os 45%+35% não são independentes.
4. **`qual` curado à mão** — subjetivo e estático; não escala nem se atualiza.
5. **Sem ataque/defesa separados** — um único rating por seleção; perde nuance (time que faz e leva muitos gols).
6. **Terceiros**: usa conjuntos permitidos do Anexo C + pareamento determinístico, não a tabela canônica exata da FIFA (impacto agregado desprezível).
7. **Dados estáticos** (1–3/jun) — sem atualização ao vivo (frente 2 do roadmap).
8. **Sem backtesting/calibração formal** — não há medição de Brier/log-loss contra torneios passados.

---

## 7. Validação já feita
- Somas coerentes (Σtítulo=100%, Σfinal=200%, …, Σavançar=3200%) e **0 violações de monotonicidade**/48.
- Reprodutibilidade: duas execuções → `results.json` idêntico (md5).
- 72 jogos de grupo: V+E+D = 100% em todos (checado analiticamente).
- JS embutido: `node --check` OK; harness com DOM stub exercita tabela/gaveta/calculadora sem erro.
- HTML sem dependências externas (0 referências a CDN).

---

## 8. Como rodar
```bash
cd src
python3 wc2026_model.py        # -> data/wc2026_results.json (~10s, determinístico)
python3 build_dashboard.py     # -> dist/copa2026_dashboard.html + copa2026_artifact.html
python3 make_generic.py        # -> dist/copa2026_dashboard_generico.html
```
Python 3.8+; nenhuma instalação. `node` é opcional (só para o check de sintaxe do JS).
