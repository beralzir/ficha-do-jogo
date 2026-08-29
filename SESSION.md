# SESSION.md · ponto de retomada

**Atualizado:** 29/08/2026, no fechamento da sessão que virou Copa→Eleições.
**Missão da próxima sessão: FASE B, fundação da edição Eleições 2026.**

## Comece por aqui (sessão nova)

1. `git fetch origin && git checkout eleicoes-2026` — a branch da fase; o draft **PR #6** é o
   container do trabalho (merge só depois da validação local do Bera).
2. Ler `docs/plano-fase-b-eleicoes.md` (checklist B0-B8, PROPOSTA) e
   `docs/retrospectiva-copa2026.md` §8 (o de-para Copa→Eleições).
3. daquele-jeito: apresentar o checklist ao Bera (clicável) e, aprovado, executar com
   portas-em-automatico.

## Estado herdado

- **Fase A publicada em 29/08:** arquivo `/copa2026` live (+ `/copa2026/retrospectiva`), medição
  final protegida (`finalize_scores.py`; `compare.py` recusa sobrescrever), tag `copa2026-final`,
  workflows `atualizar-copa` e `Fetch WC schedule` desabilitados, `health` ativo.
  Commits: `99abf3a` (fechamento) · `ec52729` (registro).
- **Decisões do Bera (29/08):** escopo Pres + 27 Gov + 54 Senado, no ar em ondas (presidencial
  primeiro) · 5 públicos com ficha completa (Fase C) · synths (vox) só como modelo competidor no
  leaderboard · documentação no repo + página.
- **REGRA DA EDIÇÃO:** conteúdo de Eleições só sobe após validação LOCAL do Bera
  (`wrangler dev`, config em `.claude/launch.json`, porta 8787; arquivo é gitignored, recriar se
  faltar). Correções do arquivo Copa podem publicar direto.
- **Material externo:** pasta iCloud `Almap/Projetos/Eleições 2026/` (brief Synths, PPT dos 5
  grupos e os `audiencia-*.json` CANÔNICOS) · instituto vox em `~/Workspaces/vox` (modo survey
  v2 é stub, construir na Fase C) · memória do projeto (`eleicoes-2026-plano`,
  `eleicoes-validar-antes-de-deploy`).

## Âncoras de formato (não deixar decair)

- Pergunta com até ~4 opções → `AskUserQuestion` (clicável), UMA decisão por vez.
- PT-BR **sem travessão espaçado** " — " (vírgula, dois-pontos ou parênteses).
- Rebase sobre origin/main antes de push. Deploy e ações externas = pausas do portas.
- Skills manual-only (risca-de-giz, cão-guia, tags-bera): re-anunciar no momento do uso,
  mesmo já citadas em plano aprovado.
