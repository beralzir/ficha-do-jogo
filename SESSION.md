# SESSION.md · checkpoint (portas-em-automatico)

**Sessão:** 31/08/2026 · **Missão:** Fase C da edição Eleições 2026 (públicos, synths,
medição), plano em `docs/plano-fase-c-eleicoes.md`, aprovado pelo Bera nesta sessão
(clique "Aprovar e soltar em automático"). Branch `eleicoes-fase-c`.

> A Fase B (B0-B8) está 100% ENCERRADA e no ar. Histórico dela: `git log` e
> `docs/plano-fase-b-eleicoes.md`. Este checkpoint cobre só a Fase C.

## Formatos-âncora (não deixar decair, mesmo em sessão longa)

- **Pergunta com até ~4 opções vai por `AskUserQuestion` (clicável), UMA por vez.**
  O Bera responde longe do teclado; pergunta inline trava ele.
- PT-BR **sem travessão espaçado " — "** (vírgula, dois-pontos, parênteses).
- **NADA de Eleições vai ao ar sem validação LOCAL do Bera.** Merge e deploy = pausa dura.
- Rebase sobre `origin/main` antes de qualquer push. O robô commita `data` e `dist` na main,
  então conflito em `dist/` é esperado: resolve rebuildando, nunca escolhendo lado a mão.
- Skills manual-only: re-anunciar no momento do uso.

## Decisões do Bera nesta sessão (cliques, 31/08)

1. **Escopo C:** espinha synths (C1 fichas + C2 survey no vox + C3 leaderboard). tags-bera/GA4 fica para depois.
2. **Competidor:** DOIS modelos, `synths_solo` e `synths_mix`.
3. **Fichas:** aba própria "Públicos", índice + 5 fichas, fonte = JSON + PPTX com gate cruzado.
4. **vox vs Synth:** trilhas separadas. vox mede voto basal e compete; Synth mede efeito de
   peça e entra em linha própria, nunca somada nem tratada como confirmação (não-independência:
   mesmo lastro TGI).
5. **Imagem generativa:** abstrato + símbolos de contexto, **sem figura humana**.
6. **Design:** `/risca-de-giz` decide e roteia, depois `/huashu-design`, `/pasteleiro` +
   Higgsfield, `/cao-guia` como portão. Autorizados nominalmente pelo Bera.
7. **Emenda C0-c aprovada:** os 5 quick wins do para-raios entram antes do C1.
8. **Estimativas** passam a ser tempo de execução real de sessão, não dias-homem (a Fase B
   inteira levou 1h13, e o plano dela dizia 10-12 dias).
9. **Licença TGI (pausa nova, não estava no plano):** o repo é privado, mas o SITE é público
   e o TGI é dado licenciado da Kantar Ibope via Almap. Bera escolheu **publicar só o
   derivado, sem as tabelas cruas de percentual e afinidade linha a linha**. O dado bruto
   fica no repo privado alimentando o C2.
10. **Atribuição:** as páginas descrevem a NATUREZA da fonte **sem nomeá-la**: "painel
   sindicalizado de consumo de mídia, base 2025". Nunca escrever TGI, Ibope, Kantar ou
   Almap em página pública. A ressalva "não é amostra do eleitorado" CONTINUA obrigatória,
   é ela que impede o leitor de ler as fichas como pesquisa eleitoral.

## Estado da Fase C

- [x] **C0 blindagem:** branch `eleicoes-fase-c`; plano commitado (`7f15841`); verificado que
      o cron usa `actions/checkout@v4` sem `ref`, logo sempre `main`, logo a branch é invisível
      para ele.
- [x] **C0-b para-raios:** `docs/plano-risco-eleicoes.md` (T1 + extensões agênticas). Placar
      NIST: 6 Sim, 3 Não, 2 incertezas, 1 parcial. **Achado central medido:** o
      `ingest_polls.py` não tinha NENHUMA validação, e uma entrada forjada valia 67,9% do
      agregado em GOV-RR/SEN-RR, 4,4% na presidencial (18,8pp com 5 entradas). Runbook
      prometia gates que só existiam na edição Copa. Bera leu o memo e aprovou a emenda.
- [x] **C0-c hardening (emenda):**
      - `src/ingest_polls.py`: gate de plausibilidade (sanidade absoluta + desvio vs consenso
        25pp no modo estrito / 40pp no modo interseção com mín. 3 candidatos em comum) +
        quarentena + diff-before-write + teto de 3 quarentenas por rodada (`exit 4`).
        **Limiares calibrados no dado real, não chutados.**
      - `src/test_ingest_polls_gate.py`: 6 blocos, todos verdes. Erro plantado obrigatório.
        **Limite conhecido e travado por teste:** forjadura que encolhe a lista para 2
        candidatos não é bloqueada (com 2 nomes a re-normalização leva o falso positivo de
        2,3% para 8,7%); sai marcada `corroborada: false` e quem pega é a camada 2.
      - `src/check_movimento.py`: alarme de saída (10pp share / 20pp P(eleito), contra 2,11pp
        de movimento real observado entre 27 e 29/08). Validado com erro plantado: pegou
        26,82pp em GOV-RR, `exit 5`; `ALARME_OK=1` libera.
      - `atualizar_eleicoes.sh`: virou 5 etapas (alarme entre motor e harness; teste do gate
        nos gates finais).
      - `docs/runbook-incidente.md`: seção da edição Eleições com as duas camadas, e **kill
        switch** em 4 níveis. A seção da Copa ficou marcada como arquivada.
      - Regressão: pipeline completo rodou e **não alterou um byte** de `data/` nem `dist/`.
- [x] **C1a extrator dos públicos:** `src/build_publicos.py` (PPTX → `data/publicos/audiencias.json`,
      5 públicos × 10 dimensões + universo + renda + %trabalha + resumo curado e definição do
      deck) e `src/test_publicos.py` (gate cruzado VERDE: todos os números do export conferem
      com o PPTX; 6 warns declarados). Determinismo byte-idêntico. **NÃO entra no CI**: o PPTX
      vive no iCloud, que o runner não acessa; o JSON versionado é o que o build de páginas lê.
      Achados: o PPTX tem typo ("u sempre procuro" sem o E, slide 14, conferido no XML) e
      `lifeStages` é recorte diferente nos dois lados (3 grupos em inglês vs 5 em português).
- [ ] **C1b direção visual** (risca-de-giz → huashu-design → pasteleiro/Higgsfield → cão-guia)
      · **PAUSA: Bera aprova a direção**
- [ ] **C1c páginas** (índice + 5 fichas, rotas, NAV, 3 ressalvas TGI visíveis na página)
- [ ] **C2 survey no vox** · **PAUSA DURA antes do campo** (precisa de subagente, e o **D6 do
      vox segue aberto**: todo `claude -p` da conta expõe o e-mail do dono)
- [ ] **C3 synths no leaderboard** (schema v2 com flag sintética obrigatória, `poll_source`,
      `synths_solo` + `synths_mix`, slot `synth_almap`, gate anti-vazamento com erro plantado)
- [ ] **merge + deploy** · **PAUSA DURA**

## Pendências que dependem só do Bera

1. **Escopo do `CLOUDFLARE_API_TOKEN`** não verificável daqui. Se for token de conta ampla em
   vez de "Edit Cloudflare Workers", o raio de dano de um vazamento passa muito além do site.
2. **Norma eleitoral do TSE sobre IA em 2026:** `[a verificar]`, e é **o único item que pode
   bloquear o C2**. O site não é propaganda eleitoral, o que provavelmente o deixa fora do
   escopo, mas publicar pesquisa sintética em campanha pede a leitura da norma vigente.
3. **Resultado do Synth** chega nesta sessão; pode gerar emenda em C2/C3 (formato do slot,
   prioridade do vox). C0, C0-b, C0-c e C1 são imunes.
4. **D6 e D7 abertos no vox** desde 19/08, mais a dívida da "sonda zero".

## Fatos úteis

- Datas: 1º turno 04/10/2026 · 2º turno 25/10/2026. **34 dias para o 1º turno.**
- Fichas TGI: `~/Library/Mobile Documents/com~apple~CloudDocs/Almap/Projetos/Eleições 2026/`
  (5 `audiencia-*.json` + `audiencias-eleitorais.json` + o PPTX, que tem 6 dimensões a mais).
- **Não usar a regionalização do TGI:** o slide 2 põe 69% dos Lulistas no Sudeste e só 2,86M
  no Nordeste. É viés de cobertura do painel; ligar público a UF por aí seria erro grave.
- `purchaseReasons` no JSON são **prioridades de voto**, não motivo de compra.
- Dívida fora de escopo: 275 nomes sem match no ingest, crescendo sozinhos.
- Dívida cosmética: `docs/runbook-incidente.md` tem 10 travessões espaçados pré-existentes
  (versão antiga, anterior à regra). Não corrigidos para não virar drive-by; oferecidos ao Bera.
