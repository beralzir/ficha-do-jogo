# Plano da Fase B — Ficha do Jogo · Eleições 2026 (fundação)

> **PROPOSTA para validação do Bera na sessão de implementação** (daquele-jeito §1.4). Escrito em
> 29/08/2026 pela sessão que fechou a Copa, com o contexto completo da retrospectiva
> ([docs/retrospectiva-copa2026.md](retrospectiva-copa2026.md), de-para Copa→Eleições na §8).
> Executar com portas-em-automatico após aprovação. **Regra da edição: tudo roda local
> (`wrangler dev`); nenhum deploy sem validação explícita do Bera.** Trabalho nesta branch
> (`eleicoes-2026`); rebase sobre origin/main antes de qualquer push.

**Decisões já tomadas pelo Bera (29/08, cliques):** escopo = presidencial + 27 governos +
54 vagas de Senado (2 por UF; Senado não tem 2º turno), entrando no ar em ondas (presidencial
primeiro); 5 públicos com ficha completa ficam na Fase C; pesquisas sintéticas (vox) entram só
como **modelo competidor** no leaderboard; documentação no repo + página.
**Datas:** 1º turno 04/10/2026 · 2º turno (presidente/governadores) 25/10/2026.

## B0 · Setup [~meio dia]
Branch `eleicoes-2026` (este PR) + `wrangler dev` local (config `.claude/launch.json`, porta 8787).
**Feito quando:** as páginas atuais rodam localmente e o ambiente está pronto.

## B1 · Schema da marca via risca-de-giz [~meio dia]
Criar `~/Workspaces/design-schemas/ficha-do-jogo.md` a partir do **site live** (paleta atual
verde+dourado, logo radar; `docs/DESIGN_BASELINE.md` descreve a paleta antiga azul, usar só como
histórico) + `src/shell.py`/`src/theme.py`; rodar `scripts/check_schema.py` (gate); o commit do
schema é do Bera. Direção registrada: mesmo design, conteúdo eleições.
**Feito quando:** gate verde e Bera aprovou o schema por leitura.

## B2 · Fontes de pesquisas [~1 dia, investigação]
Avaliar na hora, com os critérios do ROADMAP F2 adaptados: **cobertura estadual** (o gargalo
real), registro TSE como âncora de existência, agregadores públicos, custo/ToS, formato/IDs,
latência. Trade-off real (ex.: API paga vs agregador público) vira pergunta clicável ao Bera.
**Feito quando:** `docs/fontes-eleicoes.md` com a decisão, evidências e o de-para de nomes.

## B3 · Estrutura de dados [~1 dia]
`data/eleicoes2026_structure.json`: 29 corridas majoritárias + Senado (presidência, 27 governos,
27 corridas de Senado com 2 vagas), candidatos registrados (registro TSE fechou em 15/08; dados
reais disponíveis), calendário e regra por cargo. Chave canônica por candidato (id TSE); nome de
exibição na camada de view (padrão PT map da Copa). Schema de pesquisa
(`data/live/polls.json`): instituto, datas de campo, amostra, universo, números por cenário.
**Feito quando:** schemas documentados (HANDOFF novo) + validador offline verde.

## B4 · Motor probabilístico [~2-3 dias]
`src/eleicoes_model.py`: agregador de pesquisas (ponderação por recência, amostra e instituto +
house effect básico) → distribuição por corrida → Monte Carlo (incerteza entre institutos,
indecisos, correlação nacional↔UF simples, 2º turno condicional por par de candidatos).
Invariantes: Σ P(eleito) = 100% por corrida; P(eleito) ≤ P(chega ao 2º turno) onde houver 2º
turno; determinismo (seed 42, iterações ordenadas); **espaço de medição definido ANTES de medir**
(aprendizado da Copa). Corrida sem pesquisa recebe prior de alta incerteza DECLARADO, nunca
50/50 silencioso.
**Feito quando:** gate de invariantes verde + sanidade por corrida revisada.

## B5 · Harness multi-modelo desde o dia 1 [~1 dia]
`data/model_configs.json` da edição: baseline agregador puro + variantes de ponderação (+ slots
para fundamentos e para o modelo synths da Fase C). Freezes diários + leaderboard walk-forward
(métrica pré-especificada: erro vs próxima pesquisa por corrida durante a campanha + Brier vs
resultado no fim). Caveats viajam no JSON, como na Copa.
**Feito quando:** freezes gravados e o compare de eleições roda com ressalvas nos dados.

## B6 · Páginas no design atual [~2-3 dias]
Raiz nova "Ficha do Jogo · Eleições 2026": index (cards por corrida), dashboard presidencial
(matriz candidato × 1º turno/2º turno/eleito, gráfico, dossiês), template de página por UF
(28 corridas), página Modelos. Reusar `shell.py`/`theme.py`/`flags` (bandeiras → siglas de
partido/UF). Apoio de layout de página nova: skill `frontend-design` (autorizada no plano macro).
**Feito quando:** tudo navegável no `wrangler dev`, gates estático-primeiro/zero-dep verdes.

## B7 · Validação do Bera e virada [meio dia + a critério dele]
Roteiro de QA local → ajustes → **só então**: merge do PR, redirects da raiz Copa (301 dos slugs
antigos `/dashboard` etc. → `/copa2026/*`), canonical/OG novos, deploy (**pausa dura do portas**).
**Feito quando:** Bera valida localmente e autoriza o deploy com todas as letras.

## B8 · Automação da edição [~1 dia, pós-virada]
Workflow `atualizar-eleicoes` (cron: ingest de pesquisas com quorum/gates → re-simula → gate →
deploy só com dado novo aprovado). `health` passa a cobrir as páginas novas. Completude com
alarme (aprendizado do jogo 103 perdido na Copa).
**Feito quando:** 1 ciclo hands-off completo com gate verde.

## Riscos declarados
- Pesquisas estaduais escassas e irregulares → banda de incerteza honesta por corrida, declarada na UI.
- Senado sub-pesquisado (2 vagas/UF) → prior + rótulo de qualidade do dado por corrida.
- Prazo: ~5 semanas até o 1º turno → ondas (presidencial primeiro no ar; UFs na sequência).
- `[assumido]` Mercados de previsão (ex.: Polymarket) ficam FORA da v1 do motor; se entrarem um
  dia, entram como competidor no leaderboard, nunca direto no oficial.

## Fase C (não detalhar aqui)
Fichas dos 5 públicos (`audiencia-*.json` da pasta iCloud como fonte canônica), personas no vox
(`~/Workspaces/vox`; modo survey v2 é stub a construir), modelo synths competidor, portões
cão-guia (a11y) e tags-bera (GA4) com re-anúncio no momento do uso. Detalhar quando a B fechar.
