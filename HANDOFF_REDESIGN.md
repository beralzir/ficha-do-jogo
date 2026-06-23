# HANDOFF — Redesign de UI (sessão nova) · criado 2026-06-10 (tarde)

> ✅ **STATUS (2026-06-10): REDESIGN + white-label PUBLICADOS** em bera.ia.br/ficha-do-jogo (Version ID f917bd2a).
> Os 8 itens + dedup + 6 ajustes pós-revisão entregues e auditados. Detalhe em [`REDESIGN_PROGRESS.md`](REDESIGN_PROGRESS.md).
> **Novos arquivos:** `src/shell.py`, `src/predcards.py`, `src/dossie.py`. Itens abaixo = **histórico do que foi pedido**.

> **Sessão nova (contexto zero):** leia `CLAUDE.md` → **este arquivo** → `HANDOFF_PROXIMA_SESSAO.md`
> (operação na Copa) → `HANDOFF.md` (modelo). Trabalhe no estilo do Bera: **uma pergunta/decisão por vez,
> em box (AskUserQuestion) quando for escolha**; `daquele-jeito` (plan-first, auditoria 4-eixos).
> **Skills:** o Bera autorizou nominalmente **`huashu-design`** + **`frontend-design`** para este redesign —
> carregue as duas. (Fora deste escopo, `huashu-design` segue MANUAL-ONLY.)

---

## 0. Por que esta sessão existe
Em 2026-06-10 fechamos um **white-label** (esconder o método/“segredo”) + remoção de palpite pessoal, e
**verificamos tudo** — mas **NÃO publicamos** (o Bera quis revisar). Na revisão ele pediu um **redesign de UI**
de 8 itens. Como o redesign precisa das skills de design e o contexto da sessão anterior estava cheio, paramos e
passamos pra cá. **O deploy de TUDO (white-label + redesign) acontece junto, no fim, com OK do Bera.**

## 1. ESTADO ATUAL — o que já está feito no código (PRESERVAR no redesign)
Tudo abaixo já está nos builders em `src/` e nas saídas `dist/` (não republicado). **Não desfazer:**

**White-label “modelo proprietário” (camada de view; motor NÃO tocado → invariantes/determinismo intactos):**
- Renames nas views: **Mercado/de-vig → Odds** · **Opta+Elo → Opta** (Elo some como input nomeado) ·
  **modelo próprio → “modelo proprietário”** · **Sherman Kent → “Escala probabilística”**.
- `build_dashboard.py`: prosa de metodologia e Fontes sanitizadas (sem Elo/de-vig/eloratings/World Football/
  SLOPE/Monte Carlo); `elo` removido do JSON `DATA` embutido; gaveta mostra **Proprietário/Odds/Opta** e rating
  sem “(Elo …)”; rodapé “Modelo preditivo proprietário” (sem dump de params); seção de prêmios = **“favoritos
  pelas odds”**. **Quadro-receita** novo na Metodologia (`<details>` “Pipeline e pesos — modelo proprietário”):
  `Odds 45 + Opta 35 + Qualitativo 20 → rating proprietário → 50k sims → probabilidade`. CSS: `.recipe/.rcol/
  .rchip/.rarr/.rout`. **Scrub de “Elo” do texto curado dos dossiês** via helper `_wl()` (2 dossiês citavam “Elo
  alto”/“Elo/inexperiência” → “rating …”).
- `build_bolao.py`: **reescrito** — só “Próximos · o que preencher” com placar de maior **pts esp.** (recomendação
  do modelo pro bolão real). Removidos: `my_picks`, `award_picks`, “Modelo vs você”, previsto×real, prêmios·palpite,
  STRIP. Imports/CSS mortos removidos. Nome/arquivo “Bolão” mantido.
- `build_comparativo.py`: **3 dimensões** (Calibração do modelo · Placar previsto×real **só do modelo** · Fase
  previsto×real). Removidos “Modelo×você” e “Prêmios·palpite”. Grades `.prh/.pr` viraram 3 colunas; CSS morto removido.
- `build_index.py`: descrição do card Bolão reescrita (sem “seu desempenho vs. o modelo”).
- `make_generic.py`: **reescrito** — agora é a variante **maximamente anônima** (tira até “Opta”/“Poisson”); o
  `dashboard.html` principal já é o público semi-anônimo. (Generico provavelmente **redundante** agora — candidato a
  aposentar; decisão do Bera, sem pressa.)
- **Verificado:** invariantes (Σtítulo=100%…Σavançar=3200%, 0 violações; motor não rodado), baseline md5
  `b14b315173e54656d1f816d668130b3e` inalterada, zero-dep nas 7 saídas, `node --check` OK, **0 termos do segredo**
  em qualquer página, caminho **populado** do comparativo testado com estado-demo.

**Deixado de propósito (não é bug):** “mercado” minúsculo conversacional nos **dossiês** (“o mercado supervaloriza
X”) e no idiom dos Limites (“ganha do mercado”) — não revela a receita. Resíduo de doc: `state.py`/
`state.example.json`/`HANDOFF.md §5` ainda documentam `my_picks`/`award_picks` (agora ignorados pelas views) —
limpar quando der.

## 2. O REDESIGN — 8 itens pedidos pelo Bera (2026-06-10)
1. **Crédito + licença em TODAS as páginas (footer discreto).** **DECIDIDO:** crédito “© 2026 Renato Beralzir” +
   **CC BY-NC-ND 4.0** (link `https://creativecommons.org/licenses/by-nc-nd/4.0/`). Aplicar nos 5 footers
   (dashboard/bolão/comparativo/resultados/index) — e no generico/artifact.
2. **Disclosure/drill-down ruim.** Os `<details>` colapsados são difíceis de perceber onde clicar. Locais:
   dashboard (“Grupos B–L” em jogos de grupo; rodadas do mata-mata pós-32avos), bolão (gavetas por dia / “+N dias”).
   Bera quer **opções melhores, talvez no estilo da página Resultados** (abas/acordeões mais claros). → design.
3. **Toggle de tema.** Hoje é só `prefers-color-scheme` (segue o SO), **sem botão**. Bera não acha como trocar
   dark/light. Precisa de um toggle fácil. ⚠️ Decisão de arquitetura: páginas zero-JS (bolão/comparativo/resultados/
   index) — fazer CSS-only (checkbox/`:has()` hack, mantém zero-JS) ou aceitar micro-JS de toggle? (dashboard já tem JS).
4. **Diferenciar visualmente 3 coisas hoje parecidas:** botão que **muda de página** vs âncora da **mesma página**
   vs **tag de modelagem** (pills). Hoje são todas pílulas iguais. **Dashboard é a mais afetada (muito longa)** →
   **avaliar QUEBRAR a Dashboard em mais páginas** pra melhorar navegação. → design + arquitetura de informação.
5. **Nav moderna / microinterações.** Bera pediu explicitamente usar **`huashu-design` + `frontend-design`** pra
   modernizar navegação e tweaks de usabilidade.
6. **Hierarquia do título.** Hoje o `<h1>` do dashboard é a descrição inteira (“Copa do Mundo 2026 — Probabilidade
   por seleção, por fase e por jogo”). Correto: **título = “Ficha do Jogo”** · subtítulo **“Copa do Mundo 2026”**
   (tamanho/peso menor) · depois a **descrição** “Probabilidade por seleção, por fase e por jogo”. Aplicar a marca em
   **todas as páginas** (consistência).
7. **Desktop de verdade.** bolão/comparativo/resultados/index são **só-mobile** (`max-width:560px`). Mobile é o
   acesso principal, MAS desktop deve aproveitar a tela (mais densidade/colunas, melhor organização). Dashboard já é
   responsiva (1280px). → tornar as 4 responsivas.
8. **Calculadora:** mover pra **ANTES da “Matriz completa”** no dashboard + dar **mais destaque** (“ficou muito legal”).

## 3. Decisões de design a fechar NA sessão (uma por vez, em box)
- **Toggle de tema:** CSS-only (mantém zero-JS) vs micro-JS? E onde fica o controle (header)?
- **Quebrar a Dashboard?** Em quais páginas (ex.: “Probabilidades/Matriz” · “Jogos & Mata-mata” · “Calculadora” ·
  “Metodologia”)? Ou manter única com nav-âncora bem diferenciada? Afeta #4, #6, #8.
- **Padrão de disclosure (#2):** abas? acordeão sempre-visível? cards expansíveis? (ver o que a **Resultados** usa.)
- **Linguagem visual da nav (#4):** como distinguir página/âncora/tag (forma, cor, ícone, posição).
- **Breakpoints desktop (#7):** grid de quantas colunas por página.

## 4. Restrições que continuam valendo (CLAUDE.md)
Estático-primeiro (renderiza sem JS) · **zero dependência externa** (0 CDN/fonte remota/lib — tudo inline) ·
mobile-first · invariantes de dados + contrato model↔build · determinismo. **O toggle de tema e qualquer “tweak
moderno” NÃO podem furar zero-dep** e, idealmente, não quebram o static-first.

## 5. Pointers / como rodar
- **Design system (fonte única):** `src/theme.py` (tokens dark+light) + `DARK_BODY`/`LIGHT_BODY`/`TIERS_*` em
  `build_dashboard.py`. Dark = verde-floresta `#0f1b13` + accent gold `#f3b03c`; Light = cream `#f5f2e6` + accent
  verde `#1a7a43` (accent muda por tema — deliberado). **Regra de ouro:** accent só cromo; verde é a cor do DADO.
- **Builders:** `build_dashboard.py` (único com JS; ~520 linhas), `build_bolao.py`, `build_comparativo.py`,
  **`build_resultados.py` (LER — é a referência de disclosure que o Bera quer imitar)**, `build_index.py`,
  `make_generic.py`.
- **Build (sem motor, ~3s):** `for b in dashboard bolao comparativo resultados index; do python3 src/build_$b.py; done && python3 src/make_generic.py`
- **Verificação:** ver §8 do `HANDOFF_PROXIMA_SESSAO.md` (somas/monotonicidade, zero-dep, `node --check`).
- **Screenshots (auditoria mobile+desktop):** Playwright via cache do npx (memória `playwright-sem-instalar` —
  symlink `node_modules` no dir do script; NÃO instalar nada) ou MCP `Claude_Preview`. Viewport mobile 390×844 e
  desktop ~1280×800, dark+light. Limpar `.claude/shots/` ao fim.

## 6. Operação da Copa segue ativa em paralelo
O agendamento **`copa2026-preparo-resultados`** (07:17/dia) continua: confirma placares → `./atualizar.sh` →
Bera autoriza `--deploy`. **Cuidado:** se algum jogo acontecer durante o redesign, o fluxo de resultados e o
redesign vão querer rebuildar/publicar — coordene com o Bera. (Hoje 10/jun: 0 jogos; estreia 11/jun à noite;
1º update real = 12/jun manhã.)

## 7. Deploy
**PARADA.** Publicar só no FIM do redesign, com OK do Bera, via `./atualizar.sh --deploy` (re-sim no-op com estado
vazio → rebuild → checa 200). O white-label já feito vai junto.
