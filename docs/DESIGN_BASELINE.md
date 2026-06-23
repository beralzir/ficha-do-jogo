# DESIGN BASELINE — UI atual (ponto de partida para o redesign)

Spec do dashboard atual (`dist/copa2026_dashboard.html`), para alimentar o redesign com
`huashu-design` / `open-design`. Tudo vive inline em `build_dashboard.py` (CSS no `<style>`,
componentes pré-renderizados em Python, interatividade num `<script>`). **Não há framework.**

> Objetivo do redesign (ver ROADMAP Frente 4): mobile-first, acessibilidade AA, manter dark/light
> como tokens, preservar estático-primeiro e zero dependências.

---

## 1. Design tokens — cor (CSS custom properties)

Duas paletas via `:root`. O build injeta `PALETTE` (dark no dashboard, light no artifact).

| Token | Papel | Dark | Light |
|---|---|---|---|
| `--bg` | fundo da página | `#0b0f17` | `#f6f8fb` |
| `--card` | superfície de card | `#121826` | `#ffffff` |
| `--card2` | superfície da gaveta | `#0e1422` | `#ffffff` |
| `--line` | bordas | `#1f2a3d` | `#dbe3ee` |
| `--tx` | texto principal | `#e6edf6` | `#0f1c2e` |
| `--mut` | texto secundário | `#8aa0bd` | `#5b6b80` |
| `--ac` | acento / links / títulos | `#38bdf8` | `#0284c7` |
| `--box` | caixas internas (th, notas) | `#0e1626` | `#f1f5fa` |
| `--rowline` | linha de tabela | `#161f30` | `#e8edf4` |
| `--rowhov` | hover de linha | `#101a2e` | `#eef4fb` |
| `--chipbg`/`--chiptx` | chip de grupo | `#1b2942` / `#cfe0f5` | `#e3ebf5` / `#28415e` |
| `--notetx` | texto de nota | `#cdd9ea` | `#243447` |
| `--kpia`/`--kpib` | gradiente do KPI | `#13203a`→`#0e1422` | `#eef4ff`→`#fff` |
| `--pillbg` | fundo de pill | `#0e1a2b` | `#eef3f9` |
| `--gd` | verde "vantagem" | `#22c55e` | `#15803d` |

**Cores semânticas fixas (não trocam por tema):**
- Resultado de jogo: vitória `#22c55e` · empate `#64748b` · derrota `#ef4444`.
- Comparação de título: Modelo `#22c55e` · Mercado `#38bdf8` · Modelo externo/Opta `#a78bfa`.
- **Tiers**: t0 Favorito `#7c2d12/#fdba74` · t1 Candidato `#1e3a8a/#bfdbfe` · t2 Azarão `#134e4a/#5eead4` · t3 Aposta externa `#3f3f46/#d4d4d8` · t4 Completando `#27272a/#a1a1aa` (dark; há equivalentes claros).
- **Escala Sherman Kent** (banda → cor): Quase certo `#16a34a` · Muito provável `#22c55e` · Provável `#84cc16` · Chances iguais `#eab308` · Pouco provável `#f97316` · Improvável `#ef4444` · Remoto `#991b1b`.
- **Heatmap das células de probabilidade**: `rgba(34,197,94, 0.10 + 0.82*sqrt(p))` — verde com opacidade ∝ √probabilidade.

---

## 2. Tipografia e espaçamento
- Família: stack de sistema (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`).
- Escala: base `14px`, linha `1.45`; `h1 23px`, `h2 17px` (com barra de acento à esquerda), `h3 14px` (uppercase, tracking), rótulos `10.5–12px`.
- Números: `font-variant-numeric: tabular-nums` (alinhamento de colunas).
- Raios: pills `999px`, cards `12–14px`, células/inputs `6–8px`.
- Container: `max-width 1280px`, padding `20px`.

---

## 3. Componentes
1. **Nav sticky** — pills de âncora (Matriz, Jogos, Mata-mata, Calculadora, Metodologia).
2. **Pills de metodologia** — chips informativos (pesos do ensemble, escala).
3. **KPI cards** (×4) — top favoritos: nome+bandeira, % título, banda Kent colorida.
4. **Gráfico de título** — barras horizontais CSS (sem lib), 3 séries (modelo/mercado/externo), top 16.
5. **Matriz 48×fases** — tabela com cabeçalho sticky, ordenável por coluna, células heatmap, chip de grupo, badge de tier. Linha clicável → gaveta. Busca + filtros (grupo, tier).
6. **Jogos de grupo** (72) — grid 2 col; por jogo: barra V/E/D, xG, placar mais provável.
7. **Mata-mata** — por rodada, células com confrontos mais prováveis + prob. de classificação + xG.
8. **Calculadora de confronto** — 2 selects + modo (grupo/mata-mata) → 1X2, xG, classificação, top-5 placares.
9. **Gaveta de dossiê** (slide-in 430px à direita) — comparação modelo/mercado/Opta, gols esperados, caminho por fase com bandas Kent, e campos do dossiê (técnico, craques, lesões, forma, histórico, trunfo, risco, leitura).
10. **Acordeões de metodologia** (`<details>`) + tabela da escala Kent.

---

## 4. Breakpoints e responsividade (estado atual)
- `@media (max-width: 900px)`: grids de jogos/mata-mata viram 1 coluna.
- `@media (max-width: 760px)`: KPIs 2 colunas; coluna "Tier" some (`.hidecol`); rótulos do gráfico encolhem.
- **Limitação mobile conhecida:** a matriz 48× rola horizontalmente (10 colunas) e a gaveta de 430px é larga
  para telas pequenas. É o principal alvo do redesign mobile-first (ver Frente 3).

---

## 5. Estados e interações
- `th:hover` clareia; `tr:hover` usa `--rowhov`; ordenação alterna asc/desc por coluna.
- Gaveta: `.drawer.open` aplica `transform: none` (entra da direita, 0.25s); fecha por × ou tecla **Esc**.
- `<details>` "Achado central" abre por padrão; demais fechados.
- Sem estados de foco/ARIA dedicados hoje → **lacuna de acessibilidade** a corrigir no redesign.

---

## 6. O que preservar
- **Estático-primeiro** (renderiza sem JS) e **zero dependências externas**.
- As duas paletas como **tokens** (dark/light).
- O significado das cores semânticas (resultado, comparação, tiers, Kent, heatmap) — são parte da leitura dos dados.
