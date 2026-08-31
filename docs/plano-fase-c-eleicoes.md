# Plano da Fase C, Ficha do Jogo · Eleições 2026 (públicos, synths, medição)

> **APROVADO pelo Bera em 31/08/2026** (daquele-jeito v2 + portas-em-automatico, clique
> "Aprovar e soltar em automático"). Escrito na sessão que abriu a Fase C, com a Fase B
> 100% encerrada (B0-B8, robô publicando sozinho desde 31/08).
> **Regra da edição mantida:** conteúdo NOVO de Eleições valida LOCAL com o Bera antes de
> qualquer deploy. Trabalho na branch `eleicoes-fase-c`; merge e deploy são pausa dura.

## Decisões do Bera nesta sessão (cliques, 31/08)

1. **Escopo:** espinha synths primeiro (C1 fichas + C2 survey no vox + C3 leaderboard).
   Os portões restantes (tags-bera/GA4) ficam para a rodada seguinte.
2. **Desenho do competidor:** DOIS modelos, `synths_solo` (forecast só do sintético,
   responde "sintético substitui pesquisa?") e `synths_mix` (sintético como mais um
   instituto no agregador, responde "sintético agrega valor?").
3. **Forma das fichas:** aba própria "Públicos", índice + 5 fichas completas. Fonte
   canônica passa a ser JSON + PPTX extraído por script auditável, com gate cruzado.
4. **vox vs Synth:** trilhas separadas com papel declarado. O vox mede intenção basal e
   compete no leaderboard; o Synth mede efeito de peça e entra em linha própria, nunca
   somada ao vox nem tratada como confirmação dele.
5. **Imagem generativa:** abstrato + símbolos de contexto (sem figura humana).
6. **`/para-raios`** entra como bloco próprio (C0-b), cedo, não como sub-item do C0.

## Por que o para-raios entrou

Verificação feita nesta sessão: **`src/ingest_polls.py` não tem uma única validação de
sanidade**. Sem quorum, sem detecção de outlier, sem limite de plausibilidade. O caminho
completo é: Wikipédia (editável por qualquer pessoa) → ingest sem checagem → motor →
build → `wrangler deploy` automático, sem humano no meio, todo dia às 10:37 UTC. Em ano
eleitoral, com forecast presidencial assinado pelo Bera. A Fase C piora a superfície
(conteúdo de LLM entrando no mesmo fluxo, personas sintéticas em site público), então o
mapa de risco vem antes do desenho dos gates, não depois.

## Como ler as estimativas

São **tempo de execução real de sessão**, não dias-homem. Referência empírica: a Fase B
inteira (B2 a B8) levou 1h13min, do commit `c4a4117` (29/08 15:39) ao `ab8f9f5` (16:52).
O plano da Fase B estimava 10 a 12 dias, e essa métrica foi descartada por não descrever
nada útil.

## Checklist

### C0 · Blindar o deploy automático [~5 min, sem pausa]
Branch `eleicoes-fase-c`; este plano commitado; conferido que o cron não arrasta trabalho
em curso (o workflow usa `actions/checkout@v4` sem `ref`, logo sempre `main`).
**Feito quando:** branch criada, plano no repo, blindagem verificada por leitura do YAML.

### C0-b · /para-raios [~25 min, PAUSA: Bera lê o memo]
Plano de risco e segurança de IA sobre o sistema REAL (cron autônomo + fonte editável por
terceiros + LLM entrando no fluxo + personas públicas em ano eleitoral). NIST CSF, OWASP
Top 10 for LLM/Agentic, MITRE ATLAS, checagem de transparência, memo priorizado.
**Feito quando:** tabela + memo entregues e lidos pelo Bera; achados críticos viram emenda
ao plano em vez de ficarem para depois.

### C1a · Extrator dos públicos [~15 min, sem pausa]
`src/build_publicos.py` extrai o PPTX (`Perfil de grupos de eleitores.pptx`, TGI BR 2025
R3) para `data/publicos/audiencias.json` (schema v1: 15 dimensões + universo nacional +
renda média). Gate cruzado em `src/test_publicos.py`: todo campo presente nos
`audiencia-*.json` do Bera tem que bater EXATAMENTE com o extraído do PPTX; divergência
falha o build, não vira warn.
**Feito quando:** gate verde, 5 públicos completos, determinismo conferido.

### C1b · Direção visual [~30 min, PAUSA: Bera aprova a direção]
`/risca-de-giz` decide a direção e carrega o schema da marca (`~/Workspaces/design-schemas/
ficha-do-jogo.md`, criado por ela na B1), e roteia: `/huashu-design` produz variantes de
layout da ficha; `/pasteleiro` + Higgsfield geram texturas, fundos e símbolos de hábito de
mídia (sem figura humana, decisão 5); `/cao-guia` é o portão de a11y.
**Feito quando:** Bera escolhe uma direção entre as variantes apresentadas.

### C1c · Páginas dos públicos [~20 min, sem pausa]
6 páginas (índice comparativo + 5 fichas), rotas `/publicos` e `/publico-<slug>` no
`worker.js`, NAV com a aba "Públicos". Reusa `shell.py`/`theme.py` como a B6.
**Ressalvas obrigatórias, visíveis na página e não só no JSON:**
1. TGI é painel de consumo de mídia, não amostra do eleitorado.
2. A regionalização do TGI fica FORA da entrega (o slide 2 põe 69% dos Lulistas no
   Sudeste e só 2,86M no Nordeste; é viés de cobertura do painel, e usar isso para ligar
   público a UF seria erro grave).
3. `purchaseReasons` vira "prioridades de voto" na camada de view (o nome do campo mente
   sobre o conteúdo).
**Feito quando:** gates zero-dep e `node --check` verdes, light e mobile conferidos.

### C2 · Survey sintético no vox [~40 min até a pausa, PAUSA DURA: campo]
- `modos/survey.md` sai do stub, implementando os 7 compromissos já firmados lá.
- Painel determinístico: quotas sobre as marginais TGI com correlações explícitas (estágio
  de vida condicionado à idade), seed fixa, script reprodutível.
- `estudos/eleicoes-2026/estudo.md` + roteiro cego de intenção estimulada, com a lista real
  de candidatos do `structure.json`, + termos vetados.
- **PAUSA DURA antes do campo:** precisa de subagentes, e a decisão **D6 do vox segue
  aberta** (todo `claude -p` da conta expõe o e-mail do dono ao processo).
- Gates do vox (vazamento, língua, citação, campo) + estabilidade medida (2 respostas por
  persona; instável é reportado como instável) → agregação ponderada por universo.
**Feito quando:** gates verdes e a pesquisa sintética existe em disco com lastro declarado.

### C3 · Synths no leaderboard [~30 min, sem pausa]
- `polls.json` v2: flag `sintetico` OBRIGATÓRIA (estrutural, não convenção) + `fonte.tipo`
  novo. Migração compatível com as 3.373 pesquisas atuais.
- `model_configs` ganha `poll_source` (`real` | `sintetico` | `ambos`); nascem
  `synths_solo` e `synths_mix`; fica declarado o slot `synth_almap` para a pesquisa do
  Synth, **com nota de não-independência** (mesmo lastro TGI, concordância não é
  confirmação; anti-circularidade do vox).
- `eleicoes_model.py` respeita `poll_source`; freezes e leaderboard rodam; a página Modelos
  mostra a linha com rotulagem SINTÉTICO permanente.
- **Gate anti-vazamento:** teste que prova que o modelo oficial NUNCA vê pesquisa
  sintética, validado com erro plantado antes de qualquer uso real.
**Feito quando:** os dois competidores aparecem no leaderboard com comparações reais e o
gate anti-vazamento reprova o erro plantado.

### Fim · merge e deploy [PAUSA DURA]
Rebase sobre `origin/main` (o robô commita `data` e `dist` na main, então conflito em
`dist/` é esperado e se resolve rebuildando, nunca escolhendo lado a mão), validação local
do Bera no `wrangler dev`, e só então merge + deploy.

## Assunções declaradas

- `[assumido]` synths cobre só a corrida presidencial (as fichas são nacionais e a
  regionalização do TGI é enviesada).
- `[assumido]` os vídeos de estímulo da pasta iCloud (Lula, Flávio Bolsonaro, Caiado,
  Cury) ficam fora desta rodada: são peças de campanha e não passam no gate de estímulo
  verificado do vox (que exige texto ipsis litteris ou anexo conferido).
- `[assumido]` 30 personas por público, alocação igual entre os 5 e ponderação por
  universo só na agregação (melhora a precisão nos grupos menores).
- `[assumido]` persona e moderador em modelo econômico, auditoria e síntese em modelo
  forte, declarado no `estudo.md` (trocar modelo de papel cria outra condição
  experimental).
- `[assumido]` o restante do C4 (tags-bera/GA4) fica para a rodada seguinte; o cão-guia
  entra antes, via roteamento da risca-de-giz.

## Riscos declarados

- **vox com pendências:** D6 (canal de subagente expõe o e-mail) e D7 (gate de leitura do
  consolidado) seguem abertos desde 19/08, e a "sonda zero" continua sem conserto. Pode
  travar o C2.
- **Prazo:** 34 dias até o 1º turno (04/10). Se o C2 escorregar, o synths perde janela de
  walk-forward e o leaderboard não discrimina.
- **Synth:** o primeiro resultado chega nesta sessão. Pode gerar emenda em C2/C3 (formato
  do slot, prioridade relativa do vox). C0, C0-b e C1 são imunes.
- **Dívida fora de escopo:** 275 nomes sem match aguardando alias no ingest, crescendo
  sozinhos.
- **Achado do para-raios:** se a ausência de validação no ingest for classificada como
  crítica, a correção entra como emenda a esta Fase, não fica para depois.
