# HANDOFF — Fase 2.5: Revisão de Design & Layout

> **Para a sessão nova (contexto zero):** leia, nesta ordem, `CLAUDE.md` → este arquivo → `SESSION.md` → `PLANO_EXECUCAO.md` → `HANDOFF.md` (arquitetura/modelo) → `docs/DESIGN_BASELINE.md`. Depois execute as **3 tarefas iniciais** da §6. Trabalhe no estilo da §5 (uma pergunta por vez!).
> Criado ao fim de uma sessão que entregou as Fases 0–2. O design atual ("B · esportivo condensado") está **inteiro aberto pra revisão** nesta fase.

---

## 1. O que é o projeto (resumo)
Modelo probabilístico da Copa do Mundo 2026 (48 seleções, sede EUA/MEX/CAN) + **site estático multipágina**. Nasceu de um **bolão de trabalho**; objetivo de pesquisa: modelagem probabilística em esporte e seu uso em apostas. Stack: **Python 3 stdlib** (motor/build) e **HTML/CSS/JS puro, zero dependência** (saída). Vai ser hospedado em `bera.ia.br/ficha-do-jogo/` (deploy = Fase 3, ainda não feita).

## 2. Estado atual do design (o que existe pra revisar)
Três páginas geradas por Python, em `dist/`, todas **dark, mobile-first, estático-primeiro**:
- **Dashboard** (`copa2026_dashboard.html`, builder `src/build_dashboard.py`): matriz 48 seleções × 7 fases (hoje uma **lista densa ordenável** com células heatmap), KPIs dos favoritos, gráfico de título (modelo×mercado×Opta), 72 jogos de grupo, mata-mata provável, **calculadora de confronto**, **gaveta de dossiê** por seleção, metodologia. Tem `<script>` inline (busca/ordenação/filtro/dossiê/calculadora) — é o único com JS; ainda assim renderiza sem JS.
- **Bolão** (`copa2026_bolao.html`, `src/build_bolao.py`): próximos jogos com **placar recomendado (EV-ótimo)** + V/E/D + xG; *Modelo vs você*; *Previsto × real*; glossário. Zero JS.
- **Comparativo** (`copa2026_comparativo.html`, `src/build_comparativo.py`): 4 dimensões previsto×real (modelo×você · calibração Brier/log-loss · placar prev×real · fase prev×real). Zero JS.

**Sistema visual atual ("B"):** accent **teal `#2dd4bf`**; paleta dark (tokens em `src/theme.py` para bolão/comparativo; o dashboard tem sua própria `PAL_DARK` com o mesmo accent); **fontes do sistema** (`-apple-system, system-ui, ...` — NÃO há fonte remota, por causa do zero-dep); semântica de cor fixa (verde=vitória/acerto, âmbar=empate/atenção, vermelho=derrota/erro); ícones `✓ ~ ✗`; barras V/E/D; `tabular-nums`. **Tudo isso está aberto pra reconsiderar nesta fase.**

> ⚠️ **Pré-torneio (estado vazio):** o **Foco 2** aparece "aguardando os jogos" (bolão: *Modelo vs você* e *Previsto×real* vazios; comparativo inteiro vazio). Pra auditar o layout *com dados*, gere um **demo populado** (ver §7).

## 3. Restrições INEGOCIÁVEIS (de `CLAUDE.md` — não quebrar)
1. **Estático-primeiro:** a página renderiza com JS desativado (conteúdo pré-renderizado em Python).
2. **Zero dependência externa:** nada de CDN, fontes remotas ou libs — tudo inline. (É requisito real do usuário; o visualizador embutido bloqueia scripts externos.)
3. **Mobile-first:** o uso principal é no celular (~390px).
4. **Dark/light como tokens** (hoje só dark existe — light é pendência).
5. **Invariantes de dados** (somas/monotonicidade) e o **contrato model↔build**: não mexer no motor sem necessidade; design não deve alterar dados.

## 4. Preferências de design já declaradas pelo Bera (respeitar)
- **Dois focos distintos:** (1) **dados principais** (resultados, tabelas) — design CLEAN, foco no dado, não na análise; (2) **estatísticas/análises** — densas porém BEM organizadas, com **cor e ícone guiando a leitura** (a "riqueza sem bagunça" do sofascore).
- **Referências que ele curtiu** (analisar a organização da informação):
  - **fotmob** — https://www.fotmob.com/leagues/77/overview/world-cup — *clean, foco no principal* → bom pro Foco 1.
  - **sofascore** — https://www.sofascore.com/pt/football/tournament/world/world-championship/16 — *muita info sem virar bagunça* → bom pro Foco 2. (Ignorar a propaganda dele; aqui não terá.)
- **Evitar textos redundantes** — foco em resultados e análises.
- **Glossário** dos termos. Ex.: **"EV" foi renomeado pra "pts esperados"** = valor esperado de pontos pela tabela do bolão (NÃO é "Estimated Victory").
- **Sem apego à versão anterior**; o design "B" atual também está aberto.
- **Bolão** é a página de maior valor pro usuário e é **protegida/privada** (dados pessoais); Dashboard é público; Comparativo tem dados pessoais.

## 5. Como o Bera quer trabalhar (CRÍTICO — ler antes de perguntar qualquer coisa)
- **UMA pergunta/decisão por vez**, em **box de respostas (AskUserQuestion)** quando for escolha; e **mesmo quando a resposta for por escrito, ainda uma por vez**. **Nunca agrupar perguntas.** Uma resposta pode interferir/cancelar a próxima. *(Já está na memória do projeto: `ask-one-question-at-a-time.md`.)*
- Workflow **`daquele-jeito`** (plan-first, rodada de perguntas, auditoria 4 eixos, progresso visível) — global, normalmente já ativo.
- **`huashu-design` é MANUAL-ONLY**: **NUNCA** auto-invocar. Só quando o Bera pedir nominalmente ("use o huashu-design", "/huashu-design"). **Mas** para esta fase de design ele provavelmente VAI querer — se achar útil, **sugira em texto e espere o OK**. (Regra global do usuário.)
- Mostre opções visuais quando fizer sentido ("ver é melhor que descrever"): gere variações e tire screenshot mobile (ver §7).

## 6. As 3 TAREFAS INICIAIS desta fase (o Bera pediu começar por elas, nesta ordem)

### Tarefa 1 — Auditoria técnica de layout / prioridade de informação / navegação mobile
Objetivo: identificar **tecnicamente** o que pode melhorar. Sugestão de método:
- Primeiro **veja as páginas renderizadas** (screenshot mobile 375px — §7), inclusive um **demo populado** (senão o Foco 2 está vazio).
- Audite por eixos: **hierarquia visual** (o que é herói vs ruído), **prioridade de informação** (o que o usuário busca primeiro vs o que está enterrado), **navegação mobile** (nav entre páginas, acordeões, comprimento de scroll, alvos de toque, a matriz-lista).
- Achados já conhecidos pra confirmar/aprofundar: no Bolão, *Modelo vs você* fica enterrado abaixo de ~17 dias de jogos (durante a Copa) — hoje há uma "faixa de placar" no topo como paliativo; a matriz do dashboard é longa; o Comparativo pode ter muita linha (72 jogos / 48 seleções) e precisa de paginação/limite/aba.
- Entregar: lista priorizada de problemas (severidade) + recomendação por item. (Se o Bera pedir, `huashu-design` tem um `critique-guide` de 5 dimensões.)

### Tarefa 2 — Elementos e funcionalidades úteis pro projeto (usando as referências)
- Analisar **fotmob** e **sofascore** (§4) e mapear elementos/funcionalidades que servem ao propósito (bolão + análise): ex. **standings por grupo**, **bracket/chave**, cards de jogo, página de seleção, busca, favoritos, filtros por fase, detalhes de jogo.
- Cruzar com os **2 focos** do Bera e decidir o que **adicionar / manter / remover**. Nota: hoje falta uma visão limpa de **Resultados/Tabelas (standings + bracket ao vivo)** — é a **Frente 3** do `ROADMAP.md`, ainda não feita, e encaixa no Foco 1.
- Entregar: lista de elementos recomendados (com justificativa e a que foco/página pertencem).

### Tarefa 3 — Decidir TODO o design do site via sequência de perguntas-guia
- Conduzir o Bera por **perguntas-guia, uma de cada vez** (§5), pra fechar o **sistema de design**: tipografia (dentro do zero-dep — stacks de sistema: serif/sans/mono? quais?), **cores/paleta e accent** (manter teal ou mudar?), densidade/espaçamento, dark **e** light, iconografia, grid, componentes.
- Provavelmente é aqui que o Bera vai querer acionar o **`huashu-design`** (sugira; não auto-invoque). Mostre variações visuais quando útil.
- Entregar: **design system documentado** (tokens) que vira fonte única e propaga pras 3 páginas (consolidar no `src/theme.py` — hoje ele só tem a paleta dark do bolão/comparativo; o dashboard tem paleta própria a unificar).

> Sequência sugerida: Tarefa 1 (audita o que tem) → Tarefa 2 (decide o que deve ter) → Tarefa 3 (define como vai parecer) → então redesenhar as páginas. Mas siga o ritmo do Bera.

## 7. Ferramentas e receitas úteis
**Regenerar tudo** (a partir de `src/`; ~10s; determinístico). ⚠️ O `CLAUDE.md` lista uma versão antiga — a sequência ATUAL completa é:
```bash
cd src && python3 wc2026_model.py && python3 build_fixtures.py \
  && python3 build_dashboard.py && python3 build_bolao.py \
  && python3 build_comparativo.py && python3 make_generic.py
```
(Obs.: `build_fixtures.py` e o motor já rodaram; `fixtures.json`/`results.json` existem. Rodar o motor reescreve `results.json` com diferença ~1e-17 só em mkt/consensus — irrelevante. NÃO sobrescrever `data/baseline/` — é parada obrigatória.)

**Preview mobile (screenshot) — recipe usada nesta sessão:**
1. `mkdir -p .claude/preview && cp dist/<pagina>.html .claude/preview/index.html`
2. Criar `.claude/launch.json` com um server `python3 -m http.server <porta> --directory <abs>/.claude/preview`.
3. MCP Claude_Preview: `preview_start` → `preview_resize` (preset `mobile`, colorScheme `dark`) → `preview_screenshot`. Para ver as 3 lado a lado, um `index.html` com 3 `<iframe>` 380px e `preview_resize` custom ~1260×1260.
4. Limpar `.claude/preview` e `.claude/launch.json` depois. (Alternativa simples: `open dist/<pagina>.html`.)

**Demo populado (pra auditar o Foco 2 com dados):** `build_bolao.py`/`build_comparativo.py` aceitam env `STATE_FILE` (estado alternativo) e o comparativo aceita `OUT_FILE`. Gere um `state.json` de meio-de-torneio (72 grupos + alguns `my_picks`) e rode com `STATE_FILE=...`. (O `wc2026_model.py` também aceita `STATE_FILE`/`OUT_FILE`/`NFINAL` p/ testes sem tocar no real.) Schema do estado: ver `HANDOFF.md` §5.

**Mapa de arquivos (`src/`):** `wc2026_model.py` (motor Monte Carlo, re-sim condicional) · `bolao.py` (recomendador EV) · `metrics.py` (previsto×real) · `bracket.py` (resolve a chave KO do estado) · `state.py` (DataSource/validação do estado) · `build_fixtures.py` (calendário) · `pt.py` (bandeira+nome PT por seleção) · `theme.py` (tokens B) · `build_dashboard.py` / `build_bolao.py` / `build_comparativo.py` (builders) · `make_generic.py` (white-label do dashboard).

## 8. Pendências e decisões em aberto (entram no escopo da 2.5 ou logo após)
- **Tema light** em todo o site (hoje só dark; precisa virar tokens light também).
- **Polimento profundo** das seções secundárias do dashboard (jogos/KO/calculadora/gaveta herdaram o teal mas sem re-skin completo de B).
- **Página Resultados/Tabelas** (standings + bracket ao vivo, mobile-first) = Frente 3 do ROADMAP — encaixa no Foco 1; ainda não existe.
- **A matriz como "lista densa"** foi a escolha atual, mas está aberta pra revisão (cards? abas por fase?).
- **Unificar a paleta** do dashboard com `theme.py` (hoje separadas).
- **API `api-futebol.com.br`**: avaliada — bom fit técnico, mas ao-vivo é pago e o **ToS (cláusula de apostas) não pôde ser verificado** (site bloqueia leitura automática). Decisão adiada: o Bera precisa ler o ToS logado + conferir preço. Fluxo manual segue valendo. (Detalhe no `SESSION.md`.)
- Depois da 2.5: **Fase 3 (deploy Cloudflare)** e **Fase 4 (ação de update)** — ver `PLANO_EXECUCAO.md`.

## 9. Como começar a sessão nova (sugestão de primeira mensagem do Bera)
> "Leia HANDOFF_FASE_2.5.md e comece a Fase 2.5. Tarefa 1: auditoria de layout/prioridade/navegação mobile — pode tirar screenshots das páginas. Uma pergunta por vez."
