# HANDOFF — Próxima sessão (operação durante a Copa + pendências)

> ✅ **2026-06-10 (noite): REDESIGN de UI (8 itens + 6 ajustes) + white-label "modelo proprietário" PUBLICADOS** em bera.ia.br/ficha-do-jogo (Version ID f917bd2a).
> Novos arquivos: `src/shell.py` (marca/nav/toggle/acordeão/favicon), `src/predcards.py` (previsões de jogo), `src/dossie.py` (painel do time, clicável em todas as páginas). Tema = ESCURO por padrão + toggle p/ claro. Detalhe em [`REDESIGN_PROGRESS.md`](REDESIGN_PROGRESS.md).

> **Para a sessão nova (contexto zero):** leia, nesta ordem, `CLAUDE.md` → **este arquivo** → `SESSION.md`
> → `PLANO_EXECUCAO.md` → `HANDOFF.md` (arquitetura/modelo). Os handoffs antigos
> (`HANDOFF_FASE_2.5.md`) são histórico — só se precisar de detalhe do redesign. `docs/DESIGN_BASELINE.md`
> está **DESATUALIZADO** (descreve o design azul/teal antigo); o sistema visual ATUAL está em `src/theme.py`
> + `src/build_dashboard.py` (`DARK_BODY`/`LIGHT_BODY`).
> Trabalhe no estilo da §6 (**uma pergunta por vez!**). `daquele-jeito` costuma estar ativo (plan-first).

---

## 0. ESTADO ATUAL — tudo no ar (atualizado 2026-06-10)
O site está **publicado e atualizado**: **https://bera.ia.br/ficha-do-jogo/** (Cloudflare Workers, público,
sem senha). O forecast vigente é de **coleta 9/jun**, `generated=2026-06-10`. **A Copa começa 11/jun.**
Top-5 título hoje: **Espanha 22,8% · França 12,9% · Argentina 11,5% · Inglaterra 9,4% · Portugal 8,7%**.

A sessão de 2026-06-10 fechou as 3 tarefas do handoff anterior (refresh de dados + prêmios individuais +
auditoria de design) e fez deploy. **Detalhe completo do que mudou: bloco "Sessão 2026-06-10" no `SESSION.md`.**

## 1. O que é o projeto (resumo)
Modelo probabilístico da Copa 2026 (48 seleções; sede EUA/MEX/CAN) + **site estático multipágina**, nascido de
um **bolão de trabalho**. Stack: **Python 3 stdlib** (motor/build) e **HTML/CSS/JS puro, zero dependência**
(saída). Objetivo de pesquisa: modelagem probabilística em esporte e seu uso em apostas.

## 2. Páginas (em `dist/`, estáticas, mobile-first + DESKTOP responsivo; tema ESCURO padrão + toggle p/ claro)
**Shell compartilhado** (`src/shell.py`) em todas: marca "Ficha do Jogo" (logo radar) + **abas** de página + **toggle de tema** (☾/☀, localStorage) + favicon + acordeão `.acc`. Todas têm `<script>` inline agora (pré-paint do tema + toggle + dossiê); o conteúdo renderiza sem JS. Zero dependência externa (única URL é o link da licença CC).
- `index.html` — landing (4 cards, grid no desktop). `build_index.py` (também escreve `favicon.svg` + copia `apple-touch-icon.png`).
- `copa2026_dashboard.html` — análise: matriz 48×7 (heatmap, busca/ordena/filtra), KPIs, gráfico de título, **"O que mudou"**, **"Prêmios"** (favoritos pelas odds), **calculadora em destaque (antes da Matriz)**, metodologia (acordeão), **dossiê** (gaveta ao clicar um time). `build_dashboard.py`. (+ `copa2026_artifact.html` = light forçado; `..._generico.html` = white-label máximo via `make_generic.py`.)
- `copa2026_resultados.html` — **HUB**: standings por grupo + bracket REAIS, e as **previsões do modelo** (72 jogos de grupo · confrontos prováveis do mata-mata) em acordeão; dossiê clicável. `build_resultados.py` (usa `predcards.py`).
- `copa2026_bolao.html` — "Próximos · o que preencher": placar de maior pts esperados por jogo; gavetas por dia (2 abertas) + glossário; dossiê clicável. `build_bolao.py`.
- `copa2026_comparativo.html` — previsto × real em 3 dimensões: calibração (Brier/log-loss) · placar do modelo · fase; dossiê clicável. `build_comparativo.py`.

**White-label nas views** (motor NÃO tocado): Mercado→**Odds**, Opta+Elo→**Opta**, modelo próprio→**"proprietário"**, Sherman Kent→**"escala probabilística"**; o `generico` remove até Opta/Poisson. (A dedup tirou jogos/mata-mata do dashboard → foram pro hub Resultados; o bolão/comparativo já não têm "Modelo×você"/palpite de prêmios — removidos no white-label.)

## 3. Arquitetura / mapa (`src/`)
**Motor/dados:** `wc2026_model.py` (Monte Carlo + dict `T`, ~linha 58; re-sim condicional) · `snapshot.py` ·
`awards.py` (de-vig prêmios) · `bolao.py` (recomendador EV) · `metrics.py` (previsto×real) · `bracket.py` (chave KO) ·
`state.py` (DataSource/validação) · `build_fixtures.py` · `pt.py` (bandeira+nome PT).
**Camada de view (redesign 2026-06-10):** `theme.py` (tokens dark+light, fonte única; agora com overrides `[data-theme]` do toggle) ·
**`shell.py`** (marca/nav-3-níveis/toggle/acordeão/favicon — shell compartilhado; expõe `topbar()`, `accordion()`, `CSS`, `HEAD`, `JS`, `FAVICON_SVG`) ·
**`predcards.py`** (motor analítico de partida + cartões de previsão de jogo — usado pela Resultados; saiu do dashboard na dedup) ·
**`dossie.py`** (DATA + drawer + JS do dossiê, clicável em todas via `tlink()`; o dashboard mantém o próprio — duplicação conhecida) ·
`build_*.py` (5 builders) · `make_generic.py`.
**Root:** `worker.js` + `wrangler.toml` — deploy: `~/.npm-global/bin/wrangler deploy` publica `./dist`.
**Assets não-HTML (em `dist/`):** `favicon.svg` (de `shell.FAVICON_SVG`) + `apple-touch-icon.png` (copiado de `assets/`, gerado do logo via Playwright). Só existem se `build_index.py` rodar.
**Dados:** `data/wc2026_awards.json` · `data/snapshots/{...}.json`.

### Sequência de build (sem rodar o motor; ~3s)
```bash
for b in dashboard bolao comparativo resultados index; do python3 src/build_$b.py; done && python3 src/make_generic.py
```
**Rodar o motor** (re-sim quando os DADOS ou o ESTADO mudam): `python3 src/wc2026_model.py` (≈11s,
determinístico, reescreve `data/wc2026_results.json`; gera snapshot automático antes do write).
⚠️ **NÃO sobrescrever `data/baseline/`** (forecast pré-torneio congelado = parada).

## 4. Restrições INEGOCIÁVEIS (não quebrar)
1. **Estático-primeiro** (renderiza com JS off) · **2. Zero dependência externa** (0 CDN/fonte remota/lib) ·
   **3. Mobile-first** (~390px) · **4. Dark+light como tokens** (accent = só "cromo", **nunca** em barra de dado) ·
   **5. Invariantes de dados** (Σtítulo=100% … Σavançar=3200%, monotonicidade) e contrato model↔build ·
   **6. Determinismo** (`random.seed(42)` + iterações ordenadas).
7. **🔴 PRIVACIDADE (mais crítico agora):** site **público sem senha**. Hoje `state.json` está VAZIO ⇒ 0 dado
   pessoal. **ANTES de inserir QUALQUER palpite real** (placar OU prêmio) no `state.json`, **re-proteger
   `/bolao*` + `/comparativo*`** com Cloudflare Access ou basic-auth. Isto é a primeira parada da §7.

## 5. Sistema de design (fonte única: `src/theme.py` + `DARK_BODY`/`LIGHT_BODY` no dashboard)
- Tipografia system-sans; números `tabular-nums`. **Dark:** fundo verde-floresta `#0f1b13` + accent gold `#f3b03c`.
  **Light:** cream `#f5f2e6` + accent verde `#1a7a43` (accent muda por tema — deliberado).
- Semânticas var-izadas (V/E/D, Kent). **Regra de ouro:** accent só em rótulo/borda/chip/link; **verde é a cor do DADO**
  (barras, heatmap, setas de delta). As seções novas (O que mudou ▲▼ `#22c55e`/`#ef4444`; barras de prêmio `#22c55e`)
  seguem isso.

## 5b. Deploy (Cloudflare) — como republicar
- `wrangler` user-global (`~/.npm-global/bin/wrangler`; PATH no `~/.zshrc`). Login OAuth feito (beralzir@gmail.com).
- **Republicar** (do root, após buildar): `~/.npm-global/bin/wrangler deploy`. Verificar 200:
  `curl -s -o /dev/null -w "%{http_code}" -L https://bera.ia.br/ficha-do-jogo/copa2026_dashboard.html`.
- `wrangler.toml` tem `html_handling="none"` (não remover — sem ele dá 522). ⚠️ **Todo deploy = parada (pedir OK).**

## 6. Como o Bera quer trabalhar (CRÍTICO)
- **UMA pergunta/decisão por vez**, em **box (AskUserQuestion)** quando for escolha; nunca agrupar
  (memória: `ask-one-question-at-a-time.md`). Workflow `daquele-jeito` (plan-first, auditoria 4-eixos).
- `huashu-design` é **MANUAL-ONLY** (sugerir, esperar OK). `Claude_Preview`/Playwright p/ screenshots
  (receita §8; instalar deps é parada — usar cache do npx, memória `playwright-sem-instalar.md`).
- Honestidade: placeholder honesto > dado falso; não vender além do que entrega.

---

## 7. O QUE FAZER NA PRÓXIMA SESSÃO (em ordem de prioridade)

### 🔴 A — Re-proteger /bolao* + comparativo (ANTES de qualquer palpite real) — **PARADA**
Decidir com o Bera: Cloudflare Access (e-mail/OTP) ou basic-auth no `worker.js`. Hoje as 2 páginas com dado
pessoal estão públicas; só não vazam porque `state.json` está vazio. **No minuto em que você for inserir um
resultado/palpite real, isto tem que estar feito.** (Dashboard e Resultados podem seguir públicos.)

### 🟢 B — Operação durante a Copa (o uso principal agora) — fluxo recorrente
Conforme os jogos acontecem (estreia 11/jun):
1. Editar `data/live/state.json` (schema em `HANDOFF.md §5`): `results.group [{match,hg,ag}]` ·
   quando os grupos fecharem, `results.knockout` (com `winner`/`decided_by`). `hg`/`ag` = gols do **home/away
   conforme `fixtures.json`** (não esquerda/direita da TV — erro mais comum e indetectável por máquina).
   *(Decisão 2026-06-10: o site reflete **só resultados+análise**; `my_picks`/`award_picks` não são preenchidos
   por ora — por isso o item 🔴 A não bloqueia.)*
2. **`./atualizar.sh`** — re-simula (condicional) + rebuilda as 5 páginas + verifica invariantes/zero-dep, e
   **para antes de publicar**. Depois **`./atualizar.sh --deploy`** publica + checa 200. (Fase 4 do PLANO ✓.)
   ✅ **Gotcha da data resolvido:** `generated` é auto-carimbado a cada run e o dashboard deriva "gerado em" dele;
   não precisa mais editar datas à mão. (A *data de coleta* "Coletado 9/jun" é outro conceito, estático na Copa.)

**🤖 Agendamento ativo — `copa2026-preparo-resultados`** (scheduled task durável, criado 2026-06-10, dispara
**07:17 todo dia**): em cada disparo checa se há jogo novo (compara `fixtures.json` × `state.json`; **no-op em dia
sem jogo**), busca os placares em ≥2 fontes, **PARA p/ você confirmar** home/away+placar, aplica + roda
`atualizar.sh` (sem deploy), e **PARA de novo p/ você autorizar o `--deploy`**. Não grava/publica sozinho, não
toca baseline/palpites. Gerencie em "Scheduled" na sidebar. **⚠️ Remover após a final (19/jul)** — ele mesmo
avisa quando a data passar. (Detalhe e racional: por que automação total não é viável aqui — ver `SESSION.md`.)

### 🔵 C — Pendências menores (não urgentes)
- **Datas de coleta** (só se **re-coletar dados de mercado/Elo** — raro; ratings são estáticos na Copa): a string
  "Coletado 9/jun" fica em `build_dashboard.py` (bloco Fontes), `build_index.py` e `make_generic.py` (regex casa a
  data — atualizar junto). A data de *geração* já é automática.
- `docs/DESIGN_BASELINE.md` desatualizado (descreve design antigo) — atualizar ou marcar como histórico.
- *(Já feito 2026-06-10: 💡 da auditoria — resultados pré-torneio compacto + `>99%` no Comparativo·Fase.)*

---

## 8. Ferramentas e receitas
**Verificação (somas/monotonicidade + zero-dep + JS):**
```bash
python3 - <<'PY'
import json;d=json.load(open('data/wc2026_results.json'))['teams']
s=lambda k:round(sum(d[t][k] for t in d),2)
print({k:s(k) for k in ['champion','final','sf','qf','r16','advance','group_win']})
print('viol:',sum(1 for t in d if any(d[t][a]+1e-9<d[t][b] for a,b in
 [('advance','r16'),('r16','qf'),('qf','sf'),('sf','final'),('final','champion')])))
PY
# zero-dep + JS do dashboard
python3 -c "import re,glob;[print(f.split('/')[-1],'http',len(re.findall(r'https?://',open(f).read())),'cdn',open(f).read().count('cdnjs')) for f in glob.glob('dist/*.html')]"
node --check <(python3 -c "import re;print(re.findall(r'<script>(.*?)</script>',open('dist/copa2026_dashboard.html').read(),re.S)[-1])")
python3 src/awards.py   # auto-teste: Σp=1 por mercado, times válidos
md5 -q data/baseline/forecast_pretorneio.json   # b14b315173e54656d1f816d668130b3e (inalterado)
```
**Screenshots mobile (auditoria):** Playwright via cache do npx (memória `playwright-sem-instalar.md`) ou MCP
`Claude_Preview`. Viewport 390×844, `colorScheme dark|light`, demo populado via `STATE_FILE`/backup-bit-a-bit
do `state.json`. Limpar workspace ao fim.

**Demo populado (Foco 2 com dados):** gerar `state.json` de meio-torneio (72 grupos + my_picks + award_picks)
e buildar com `STATE_FILE=...` (comparativo/resultados aceitam direto; **bolão lê `data/live/state.json` —
troca temporária com backup+restauração bit a bit**).

> **Notas de honestidade:** mercado é o melhor preditor único; o modelo integra, não supera. Gols = Poisson
> independente. Prêmios (artilheiro/luvas) **vêm do mercado**, não do motor (nível-seleção). O Elo virou valor
> REAL do eloratings.net nesta sessão (correção de fonte). Dossiês seguem curadoria de 1–3/jun (anotado no Fontes).

---

## 9. Abertura da próxima sessão (copiar/colar)

**Bloco padrão (retomada / desenvolvimento):**
```
/daquele-jeito

Retomar o projeto "Ficha do Jogo" (modelo + site da Copa 2026), em /Users/beralzir/Projetos/ficha-do-jogo.
1. Leia, nesta ordem: CLAUDE.md → HANDOFF_PROXIMA_SESSAO.md → SESSION.md → PLANO_EXECUCAO.md → HANDOFF.md.
2. Me dê um resumo curto do estado atual + pendências.
3. Só então proponha o próximo passo. Uma pergunta/decisão por vez (em box quando for escolha).
Skills: huashu-design é MANUAL-ONLY — não auto-invoque; sugira e espere meu OK. Sem outras obrigatórias.
Contexto: o agendamento "copa2026-preparo-resultados" (07:17/dia) cuida das atualizações durante a Copa —
siga o fluxo dele (confirmo placares → ./atualizar.sh → autorizo --deploy), sem publicar sem meu OK.
```

**Variante curta (já sei a tarefa):**
```
/daquele-jeito <tarefa>. Antes, leia HANDOFF_PROXIMA_SESSAO.md (e o que ele apontar). Uma pergunta por vez.
```
