# QA local da virada Copa → Eleições (etapa B7)

> Roteiro para o Bera validar a edição Eleições 2026 ANTES de qualquer deploy
> (regra da edição: nada vai ao ar sem esta validação). Estado: branch
> `eleicoes-2026`, virada JÁ aplicada em staging local (worker + páginas).
> Suba com `wrangler dev` (porta 8787) e navegue em http://localhost:8787/

## Rotas (2 min)

- [ ] `/` abre a **Eleições 2026** (index com ficha presidencial + 27 UFs)
- [ ] `/presidencial`, `/uf-rs`, `/uf-sp`, `/modelos` abrem as páginas novas
- [ ] `/dashboard`, `/resultados`, `/placares` dão **301 para /copa2026/...** (a Copa arquivada)
- [ ] `/copa2026/` e `/copa2026/retrospectiva` continuam intactos
- [ ] um caminho inválido dá 404 amigável

## Conteúdo e honestidade (5 min)

- [ ] Index: banda LISTRADA de incerteza visível nas barras; chips de qualidade
      (dado fresco/defasado) fazem sentido; 3.345 pesquisas na base; 38 dias para o 1º turno
- [ ] Presidencial: KPIs (Lula eleito ~66%, 2º turno Lula × Flávio ~99%), matriz com
      ±desvio, gráfico de evolução com 4 linhas, pares de 2º turno, accordion de método
- [ ] RS: caso-teste do 2º turno condicional: Zucco lidera o share do 1º turno mas
      tem P(eleito) MENOR que Juliana Brizola (pesquisas de par mandam nisso; conferir se a
      leitura está clara na página)
- [ ] Uma UF pequena (AC ou TO): Senado com 2 vagas, nota "eleitor vota em DOIS nomes",
      P(vaga) somando ~200% na corrida
- [ ] Modelos: leaderboard com 5 variantes e "sem dado ainda" (certo: a série começou hoje)

## Design e a11y (3 min)

- [ ] Toggle de tema: dark verde-floresta (padrão) ↔ light cream; nada ilegível nos dois
- [ ] Mobile (largura ~375px): cards empilham, tabelas rolam sem quebrar a página
- [ ] Tab percorre: skip-link, abas, cards, accordion abre com Enter

## Decisões desta virada (veto aqui se discordar)

1. Slugs novos: `/presidencial`, `/uf-xx`; **`/modelos` passa a ser da edição Eleições**
   (a página da Copa segue em `/copa2026/modelos`; sem 301 entre elas).
2. Raiz servida pelo worker direto de `eleicoes_index.html` (o arquivo `index.html` da
   Copa fica órfão no dist, inalterado; o arquivo congelado tem a cópia dele).
3. OG image segue a `og-cover.png` da marca (genérica); arte específica da edição fica
   para depois.
4. GA4/GTM: mesmas tags das páginas live; `data-page` novos (`eleicoes_*`).

## Depois do seu OK (pausas duras, nesta ordem)

1. rebase sobre origin/main + push da branch (PR #6 sai de draft)
2. merge do PR
3. `wrangler deploy` + verificação live (rotas, 301s, cache no-store na raiz)
4. B8: workflow `atualizar-eleicoes` (cron diário) + health nas páginas novas
