# SESSION.md · checkpoint (portas-em-automatico)

**Sessão:** 29/08/2026 · **Missão:** Fase A do plano "Copa → Eleições 2026" (aprovado pelo Bera).

## Plano aprovado (resumo)

- **Fase A (em execução):** fechar a Copa — sync, tag `copa2026-final`, leaderboard final,
  snapshot em `/copa2026`, retrospectiva (docs + página), deploy, desligar cron `atualizar-copa`.
- **Fase B:** Ficha do Jogo · Eleições 2026 na raiz (presidencial + 27 governos + 54 vagas de
  Senado, entrando em ondas), mesmo design; agregador de pesquisas + Monte Carlo; harness
  multi-modelo desde o dia 1; redirects da Copa na virada; cron novo.
- **Fase C:** fichas dos 5 públicos (fonte canônica: `audiencia-*.json` do iCloud Eleições 2026);
  personas + modo survey no vox (`~/Workspaces/vox`); synths como MODELO COMPETIDOR no leaderboard
  (nunca no oficial sem vencer); rotulagem SINTÉTICO sempre. Portões: cão-guia (a11y) e tags-bera
  (GA4), re-anunciar antes de usar.

## Estado da Fase A

- [x] A1 sync: main == origin/main (`f1e49bf`).
- [x] A2 tag: `copa2026-final` criada local (push junto com A7).
- [x] A3 leaderboard final: `src/finalize_scores.py` (novo) → `data/model_scores.json`
      `measurement_complete=true`; 103 jogos (72G+31KO; jogo 103/3º lugar não ingerido — declarado);
      fase/título pela véspera do KO (freeze `e5d934f`); trajetória por freeze diário.
      Continuidade dos Briers de grupo verificada; determinístico (2 runs idênticos).
      compare.py agora recusa sobrescrever o final; atualizar.sh pula o passo 2/5 nesse caso.
      **Resultados-chave:** market_only vence 1X2 geral (0,4599); no KO isolado models_only vence
      (0,3416 vs 0,3843 do mercado); FASE: dinâmicos vencem (0,0442/0,0448 vs ~0,055) → reagir à
      Copa ajudou a ler o mata-mata; Espanha campeã: modelos davam 26%, mercado 16% na véspera do KO.
- [x] A4 snapshot `/copa2026`: make_snapshot.py (7 páginas + 3 assets, banner, canonical/OG →
      /copa2026, white-label com banner neutro) + worker.js (rotas copa2026, 301 legados, cache 1h)
      + build_modelos.py em modo FINAL. Gates verdes (somas, monotonicidade, zero-dep incl. subdir).
      Fatos úteis: links internos RELATIVOS; builders não limpam dist/; push NÃO dispara deploy;
      float difere no último dígito entre CI Linux e macOS (CI = fonte dos bytes; ruído revertido).
- [x] A5 `docs/retrospectiva-copa2026.md` (10 seções, de-para Copa→Eleições) + 5 handoffs → docs/arquivo/.
- [x] A6 `dist/copa2026/retrospectiva.html` (build_retro.py; bug de colisão .bar→.tbar achado no
      visual check e corrigido; slug retrospectiva no worker; link no banner do arquivo).
- [⏸] A7 push+deploy e A8 desligar cron: **SEGURADOS pelo Bera (29/08)** para revisão do commit
      local `3e6c50d` (tag copa2026-final local). NADA publicado. Para liberar:
      `git fetch origin && git rebase origin/main && git push origin main copa2026-final`
      → `./atualizar.sh --deploy` (ou `wrangler deploy`) → `gh workflow disable atualizar-copa`.
- [x] A9 auditoria 4 eixos entregue na conversa (test_ingest bloco B falha por .api_cache local
      desatualizado, pré-existente; módulos tocados não são importados pela suíte).

## Próximo passo quando o Bera liberar

Publicar A7/A8 (acima) e detalhar o checklist da Fase B (Eleições: fontes de pesquisas por
critérios, schema da marca via risca-de-giz, estrutura de dados, motor agregador + Monte Carlo,
harness dia 1, dashboard raiz, redirects, cron novo). Fase C depois (públicos + vox + synths).

## Âncoras de formato (não deixar decair)

- Pergunta com até ~4 opções → `AskUserQuestion` (clicável), UMA decisão por vez.
- PT-BR sem travessão espaçado " — " (usar vírgula/dois-pontos/parênteses).
- Deploy/push/desligar-cron = pausas do portas; anunciar antes; nada irreversível sem cross-check.
- Skills manual-only (huashu, cão-guia, tags-bera): re-anunciar no momento do uso mesmo com plano aprovado.

## Decisões do Bera nesta sessão

Escopo v2 = Pres+Gov+Senado · públicos = ficha completa por grupo · synths = modelo competidor ·
docs = repo + página no site · plano aprovado com execução em portas-em-automatico.
