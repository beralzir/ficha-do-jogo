# SESSION.md · checkpoint (portas-em-automatico)

**Sessão:** 18/09/2026 · **Missão:** incidente da presidencial (perda de 89% das
estimuladas de 1º turno) + atualização e comparações. Plano D0-D4 em
`docs/plano-incidente-presidencial.md`, **aprovado pelo Bera em 18/09** (clique
"Aprovar D0 a D4, sem o bola-de-cristal"). Worktree `sharp-kare-601a7b`, branch de
trabalho `trabalho-incidente` (a `eleicoes-fase-c` está checada no checkout principal,
por isso o nome diferente; são os mesmos 17 commits rebaseados).

> A Fase B está encerrada e no ar. A Fase C está completa na branch, pendente do QA
> local do Bera (`docs/qa-fase-c.md`). O registro da Fase C está preservado abaixo.

## Formatos-âncora (não deixar decair, mesmo em sessão longa)

- **Pergunta com até ~4 opções vai por `AskUserQuestion` (clicável), UMA por vez.**
  O Bera responde longe do teclado; pergunta inline trava ele.
- PT-BR **sem travessão espaçado " — "** (vírgula, dois-pontos, parênteses).
- **NADA de Eleições vai ao ar sem validação LOCAL do Bera.** Merge na `main` equivale a
  autorizar publicação, porque o cron publica sozinho no ciclo seguinte. Pausa dura.
- Rebase sobre `origin/main` antes de qualquer push; o robô roda durante a sessão.
- Conflito em `dist/` e nos JSON gerados: **resolve rebuildando, nunca escolhendo lado**.
- Gate novo só vale depois de **validado com erro plantado**.
- `wrangler dev` na 8787 por `preview_start` (config `ficha-do-jogo`), nunca por Bash.

## Estado do incidente (D0-D4)

- [x] **D0 sincronizar e medir.** Rebase 17/17 limpo sobre `origin/main` (ca3684b).
      `polls.json` reconstruído pela regra do pipeline (3.509 reais do robô migradas para
      v2 + 1 synth mock do C3 = 3.510), porque o `-X theirs` tinha mesclado os dois lados
      num arquivo sem sentido (4.150 linhas, 723 ids repetidos).
      **IMPACTO MEDIDO, e ele contraria a suposição do plano:** recuperar as 483 pesquisas
      move Lula -0,3pp e Flávio -0,7pp no share, e **0,0pp em P(eleito)**. Motivo: as
      recuperadas valem só **10,4% do peso** do agregador (meia-vida de recência = 21 dias).
      **O alarme de movimento do C0-c NÃO vai disparar** (limiar 10pp/20pp).
      O estrago visível é o GRÁFICO: a série da presidencial no ar caiu de 8 meses
      (jan-ago) para 2 pontos (ago, set).
- [x] **D1 causa raiz (ACHADA).** Os editores da Wikipédia quebraram o 1º turno em
      **subpáginas**: `.../Primeiro Turno/2026/Janeiro a Agosto` e
      `.../Primeiro Turno/2023-2025`. A página principal ficou só com Setembro mais
      Agosto **por transclusão** (excerto), que é exatamente a janela 02/08 a 16/09 que
      sobrou. O 2º turno não foi quebrado, e por isso não perdeu nada.
      Dois defeitos do ingest se somam:
      1. ele não segue hatnote de subpágina ("Ver artigo principal");
      2. o walker só lê `h2/h3/h4`, e na subpágina 2023-2025 o ano está num
         `{{hidden begin|title=2025}}` (div `hidden-title`), invisível para ele. Sem isso,
         `year_from_context(['Primeiro turno','2023 - 2025',None])` devolve **2023** e o
         filtro `>= 2025` derruba a seção inteira.
      Perdas por ano: 282 de 2025 + 228 de 2026 = as 510 originais.
- [ ] **D2 alarme de volume por corrida** (o gate que faltou; validar com erro plantado).
- [ ] **D3 atualizar tudo e rodar comparações** · **PAUSA: Bera lê o relatório.**
      Não liberar `ALARME_OK=1` por conta própria.
- [ ] **D4 QA e publicação** · **PAUSA DURA.**

## Achados fora de escopo (declarar, não corrigir de carona)

- `atualizar_eleicoes.sh` não roda `synths_para_polls.py`, e o ingest **sobrescreve
  `polls.json` inteiro**. Logo o synth do C3 some a cada ingest. Hoje é inofensivo (é mock),
  mas quando o campo real rodar vira perda silenciosa.
- No 2º turno, os pares sob "Hipóteses com Lula" também vivem em `hidden-title`, então
  `par_segundo_turno` sai `None` para todos eles. Pré-existente.
- `id` do ingest NÃO é chave única (variantes de cenário compartilham id): 625 ids repetidos
  no dado do robô. Por assinatura completa só há 4 duplicatas reais em 3.510.
- SEN-AC está com `data_quality: pesquisa_velha` (1 pesquisa). Pré-existente, alheio à PRES.

---

# Registro anterior · Fase C (31/08)

## Decisões do Bera em 31/08 (Fase C)

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

## Estado da Fase C (preservado)

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
- [x] **C1b direção visual:** risca-de-giz (schema v0.1.0, gate exit 0) roteou para
      huashu-design, que produziu 3 direções em HTML hi-fi com dado real (Stat block,
      Carta, Dossiê). **Bera escolheu "B · Carta"** por clique. Pasteleiro/Higgsfield NÃO
      foram usados: a direção escolhida não pediu imagem gerada.
- [x] **C1c páginas:** `src/build_publicos.py` → 6 páginas (índice com as 5 cartas + 5
      fichas). Rotas `/publicos` e `/publico-<slug>` no worker.js; aba "Públicos" no NAV
      (as 30 páginas antigas mudaram SÓ nisso, diff conferido). Escaping por padrão
      (quick win #4 do para-raios). CSS base herdado do build_eleicoes em vez de duplicado.
      **Portão cão-guia: AA nos dois temas**, axe 0 violations, relatório em
      `docs/a11y-publicos.md`. 4 correções aplicadas (eixo 9,5px→12px; reflow 320px com
      SVG responsivo; colisão de 3 classes CSS; tipografia serifada). 1 achado
      PRÉ-EXISTENTE não corrigido: link "CC BY-NC-ND 4.0" do rodapé tem 99×14px e reprova
      WCAG 2.5.8; vem do shell.py e afeta o site inteiro, então é decisão própria do Bera.
      Schema da marca atualizado para **v0.2.0** (padrão ficha de público + 3 guardrails
      novos + tokens de gráfico). **O commit no repo design-schemas é do Bera.**
- [~] **C2 survey no vox: INSTRUMENTO PRONTO, CAMPO NÃO RODOU (pausa dura AGORA).**
      Feito em `~/Workspaces/vox` (repo PRIVADO, confirmado), **nada commitado lá**: a
      convenção da casa é o Bera ler o diff antes.
      - `modos/survey.md` saiu do stub: os 7 compromissos viraram procedimento executável.
      - `fabrica/gerar_painel_quotas.py`: quotas por MAIOR-RESTO (não sorteio, que erra a
        marginal com n=30), condicional declarada no config, e **restrição de combinações
        por TROCA entre pessoas**, que preserva as marginais por construção.
      - `estudos/eleicoes-2026/`: quotas.json + estudo.md + roteiro-campo.md +
        termos-vetados.txt + painel (150 pessoas, 5x30, seed 42).
      - **As marginais TGI NÃO foram copiadas para o vox**: `quotas.json` aponta para o
        audiencias.json daqui (`marginais_de`). Uma fonte só, sem cópia que divirja.
      - Verificado POR FORA (não pela mensagem do próprio script, que mentiu uma vez):
        0 combinações implausíveis, 6 marginais preservadas dentro de ±1 pessoa,
        determinismo por md5 em duas execuções.
      - Bug real achado e corrigido: `montar_grupos` não propagava as proibições, então o
        script dizia "0 implausíveis" enquanto havia 3.
      - **D6 RESOLVIDO (decisão do Bera: migrar o canal, não aceitar o risco):**
        `fabrica/canal_api.py`, canal por Messages API direta em stdlib. A requisição
        carrega só modelo, system e mensagens: sem CLI, sem sessão, sem conta com nome,
        sem CLAUDE.md de diretório, sem MCP. A classe de vazamento deixa de existir em
        vez de ser filtrada por prompt. `gate_isolamento` ganhou canários de identidade
        de conta; `claude -p` virou **proibido como canal de campo** no CLAUDE.md do vox.
        Efeito colateral bom: o campo agora é um script HTTP, **não precisa mais de
        subagente do harness**.
      - **NÃO PROVADO, e digo em vez de esconder:** a sonda de isolamento não rodou
        contra o canal novo porque `ANTHROPIC_API_KEY` não está no ambiente desta sessão
        (e eu não peço credencial). O D6 está **resolvido por desenho, não confirmado por
        sonda**. Comando para fechar isso está no estudo.md.
      - Modelo: persona no econômico (`claude-haiku-4-5`), síntese no forte, conforme a
        regra do instituto. Trocar isso cria outra condição experimental.
      - Desvio declarado: usei `urllib` em vez do SDK `anthropic` porque o vox é
        stdlib-only por arquitetura e o SDK não está instalado. Se um dia precisar de
        streaming, tool use ou batches, o certo é adotar o SDK, não crescer o arquivo.
- [x] **C3 synths no leaderboard (FECHADO, com mock):**
      - `polls.json` **v2**: flag `sintetico` OBRIGATÓRIA e **fail-closed** (pesquisa sem a
        flag DERRUBA o motor, em vez de virar "real" por omissão). 3.373 migradas.
      - `POLL_SOURCE` (`real`|`sintetico`|`ambos`) nos DEFAULTS, default `real`: modelo novo
        que esqueça de declarar nasce limpo. Todas as 5 variantes declaram `real`.
      - `synths_solo` (só sintético) e `synths_mix` (sintético como mais um instituto) no
        registro; slot `synth_almap` declarado **com a nota de não-independência** (mesmo
        lastro TGI = eco, não confirmação).
      - `src/synths_para_polls.py`: ponte vox->polls, ÚNICO lugar autorizado a escrever
        `sintetico: true`. Pondera por universo (personas são 30 por grupo, universo não é),
        e deixa `amostra: null` de propósito (sintético não tem erro amostral; preencher
        daria peso de pesquisa real, porque o peso usa sqrt(amostra)).
      - `src/test_synths_gate.py`: gate anti-vazamento, **erro plantado em 3 frentes**
        (sintética presente com oficial cego · pesquisa sem flag · POLL_SOURCE inválido).
        Ligado no `atualizar_eleicoes.sh`.
      - Página Modelos: selo SINTÉTICO permanente, vindo do registro (modelo sintético novo
        nasce rotulado) + parágrafo explicando que nada disso entra no forecast.
      - **VAZAMENTO SUTIL ACHADO E CORRIGIDO:** o oficial não lia o dado sintético mas
        herdava o `as_of` dele (29/08 -> 31/08). O gate não pegou; o diff byte a byte pegou.
        `as_of` agora sai só das pesquisas visíveis àquele modelo.
      - Regressão: `races` do forecast oficial **idênticas** antes/depois.
      - a11y do selo: dark 15,01 · light 13,59 (texto), borda 9,34 / 4,79. AA nos dois.
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
5. **Commitar `~/Workspaces/design-schemas/ficha-do-jogo.md` v0.2.0** (regra da B1: o commit
   daquele repo é dele).
6. **Alvo de toque de 24×24 no rodapé** (WCAG 2.5.8): afeta o site inteiro, decisão dele.

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
- **Dívida de design system (achada no C3):** `--ac` no tema CLARO dá 3,9:1 sobre o card,
  abaixo do 4,5:1 que texto pequeno exige. O selo novo contornou separando texto (`--ink`)
  de identidade (borda `--ac`), mas outros usos de `--ac` como TEXTO no light merecem uma
  passada do cão-guia. Não é do C3, é do design system.
- A pesquisa sintética hoje no `polls.json` é **MOCK** (`vox-BR-2026-08-31-presidente-mock`,
  campo `mock: true`, instituto "vox (MOCK)"). Serve para provar o encanamento. Quando o
  campo real rodar, `synths_para_polls.py --respostas` a substitui, e ele RECUSA sobrescrever
  pesquisa não-mock com mock.
