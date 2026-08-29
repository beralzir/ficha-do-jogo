# REDESIGN — checkpoint de execução (portas-em-automático)

> Estado vivo fora do contexto. Atualizado a cada ~5 passos. Sessão iniciada 2026-06-10.

## Objetivo
Fase 3 do redesign de UI do "Ficha do Jogo" (plano aprovado). Implementar o shell compartilhado
nos builders reais, depois dedup / desktop / calculadora; Fase 4 = footers + auditoria + deploy (com OK).

## Decisões travadas (Fases 1–2)
1. IA — **dedup**: jogos+mata-mata saem do Dashboard → **Resultados vira hub**; Dashboard = probabilidades + calculadora + metodologia.
2. Disclosure — **acordeão único** (`.acc` em shell.py) em todas.
3. Nav (#4) — **forma+papel**: aba sublinhada (página) · âncora com ↓ (mesma página) · selo chato (metadado, não-clicável).
4. Tema (#3) — **micro-JS inline** persistente (localStorage, auto/escuro/claro), pré-paint sem flash.
5. Desktop (#7) — **grid responsivo por página** (~1100–1280px), mobile 1 coluna.
6. Marca (#6) — **logo travado**: radar de atributos (hexágono gold + polígono de stats verde), SVG inline theme-adaptável (`--logo-frame`/`--logo-bar`). Wordmark "Ficha do Jogo". Favicon SVG data-URI.
- #1 footer: © 2026 Renato Beralzir · CC BY-NC-ND 4.0. #8 calculadora antes da Matriz + destaque.

## Paradas duras (cross-checks)
- DEPLOY = parada (só com OK). · FORK previsão×real na Resultados = parada (perguntar em box). ·
  não tocar data/baseline/. · jogo da Copa no meio = coordenar. · quebra de invariante = parar.

## Feito
- `src/shell.py` — marca/topbar/nav-3-níveis/toggle/acordeão + favicon.
- `src/theme.py` — tokens +rowhov/logo-frame/logo-bar; PALETTE com overrides [data-theme]. 4 páginas rebuildam ok (http:0).
- **Dashboard wired + verificado**: header novo (#6 marca+hero, #4 abas/âncoras↓/selos, #3 toggle+favicon), metodologia→.acc (#2), tokens+tiers data-theme, CSS morto removido, make_generic.py em lockstep (selo .tag). Build ok · http:0/cdn:0 · 3 scripts node --check ok · 0 termos do segredo · somas/monotonic ok. Screens dark/light/mobile/meta ok.
- GATE "mostrar antes de propagar" → OK do Bera.
- **index/bolão/comparativo wired + verificados**: shell (marca/abas/toggle/favicon) + desktop (#7: index 2col · bolão cards 2col + gavetas .acc · comparativo dimensões 2col). http:0/cdn:0, 2 scripts node-check ok cada. Screens ok.

## CONCLUÍDO — Fases 3 e 4 (8/8 itens)
- previsão×real: Bera escolheu "real é o palco, previsão em acordeão".
- `predcards.py` (motor + cartões). Resultados = HUB: tabela/chave REAIS + previsões em .acc; shell + desktop.
  Dedup: jogos+mata-mata saíram do dashboard (atalho p/ Resultados no lugar); motor Python/MUS/math removidos.
- #8: calculadora antes da Matriz, card destaque (.calc-hero), funcionando.
- #1: © 2026 Renato Beralzir + CC BY-NC-ND 4.0 nos 5 footers (+ artifact/generico).
- disclosure unificado em .acc (metodologia, gavetas do bolão, rodadas do bracket).

## VERIFICAÇÃO FINAL (toda OK)
- zero-dep: única URL = licença CC (hyperlink), 0 recursos carregados, nas 7 saídas.
- node --check: 17 scripts OK · make_generic: 0 nomes de método · dashboard/generico: 0 termos do segredo.
- somas 100/200/400/800/1600/3200/1200%, 0 viol. monotonic · baseline md5 b14b31… inalterado · crédito nas 7.

## AJUSTES (2026-06-10, pós-revisão) — todos feitos + verificados
1. Toggle = 2 estados (ESCURO padrão fixo ↔ claro); sem "auto"/prefers-color-scheme na página (favicon mantém o seu). Botão ☾/☀.
2. Âncoras "Nesta página" viraram chips com cara de botão (`.anchors` em shell.py).
3. Removida a linha de selos "Como o modelo pesa" do dashboard (pesos seguem na Metodologia/rodapé); make_generic REP[0] removido em lockstep.
4. **Dossiê do time** abre clicando o time em Resultados/Bolão/Comparativo (dashboard já tinha) — novo `src/dossie.py` (DATA+drawer+JS+tlink) + dica "toque num time". NÃO mexi no dashboard (tem o próprio) → duplicação conhecida com dossie.py (unificar depois, se quiser).
5. Letra do grupo na Matriz centralizada (`.grp` text-align:center).
6. Bolão: removido "+N dias"; abre exatamente os 2 primeiros dias com jogos (is_open=idx<2).
- Re-verificado: zero-dep (http=licença CC), 20 scripts node-check OK, 0 termos do segredo, somas/monotonic OK, baseline inalterado. Cliques do dossiê testados (Resultados, Bolão).

## CONCLUÍDO — DEPLOY FEITO (2026-06-10, OK do Bera)
- Publicado via `wrangler deploy` (Version ID f917bd2a); 6 páginas 200 OK; baseline md5 inalterado (motor não rodado).
- **Fix do favicon (pós-deploy):** estava em branco — o SVG usava `var()`/`@media`, que favicon de aba NÃO renderiza. Agora cores FIXAS no arquivo `dist/favicon.svg` (gerado por `build_index.py`; `shell.FAVICON_SVG`), linkado `<link rel=icon href="favicon.svg">` em todas. Re-deploy (Version ID 947918f7); favicon.svg 200 + render conferido (radar gold+verde).
- **Ícone de atalho de tela (iOS/Chrome):** `apple-touch-icon` 180×180 PNG (radar no fundo verde-floresta #0f1b13), gerado do logo via Playwright e commitado em `assets/apple-touch-icon.png`; `build_index.py` copia pro `dist/` (shutil) e linka `<link rel=apple-touch-icon>` em todas. NÃO é PWA (não precisa — iOS/Chrome usam apple-touch-icon). Re-deploy (Version ID 86ae75b6), 200 OK.
- ⚠️ **Assets não-HTML** agora no `dist/`: `favicon.svg` (de `shell.FAVICON_SVG`) e `apple-touch-icon.png` (copiado de `assets/`). Ambos só aparecem se `build_index.py` rodar — a sequência de build e o `atualizar.sh` sempre rodam.
- `atualizar.sh`: check de zero-dep corrigido p/ permitir o link da licença CC (senão a automação das 07:17 reprovaria http>0).
- `.claude/shots/` limpo · memória da marca salva · handoffs atualizados.
- resíduos menores (inofensivos): token `--pillbg` órfão; CSS gm/ko parcialmente morto (parte reusada por Prêmios/calc); dossiê duplicado dashboard×`dossie.py` (unificar se quiser).

## Resíduo conhecido
- Token `--pillbg` ficou sem uso no dashboard (inofensivo) — limpar se sobrar tempo.

## Scratch a limpar no fim
`.claude/shots/` (proofs do logo + shell).
