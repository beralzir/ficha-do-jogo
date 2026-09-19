# Plano · incidente da presidencial + atualização e comparações

> **APROVADO pelo Bera em 18/09/2026** (clique "Aprovar D0 a D4, sem o bola-de-cristal").
> Executar em sessão nova, com `/daquele-jeito` e `/portas-em-automatico`.
> **16 dias para o 1º turno (04/10).**

## O incidente, medido

Comparação entre a branch `eleicoes-fase-c` (dado de 31/08) e `origin/main` (hoje):

| | 31/08 | 18/09 | |
|---|---|---|---|
| **PRES, estimuladas** | **510** | **58** | **perdeu 89%** |
| PRES, total | 1.278 | 937 | perdeu 341 |
| PRES, 2º turno | 768 | 879 | ganhou (normal) |
| Outras 54 corridas | | | **ganharam 462** (normal) |
| Base total | 3.388 | 3.509 | subiu, o que MASCARA a perda |

A perda é **exclusiva da corrida presidencial** e **só nas estimuladas** (1º turno). O 2º
turno e as 54 outras corridas seguem crescendo normalmente. Isso aponta para mudança na
estrutura da página da Wikipédia da eleição presidencial, não para falha geral do ingest.

O que sobrou em PRES estimulada: 58 pesquisas, janela 02/08 a 16/09 (28 em agosto, 30 em
setembro). Ou seja, **o histórico anterior a agosto desapareceu inteiro**.

### Por que ninguém percebeu (a parte que mais importa)

`scripts/resumo_eleicoes.py` tem o "alarme de completude" do B8, e ele checa
`data_quality == "ok"`, que mede **FRESCOR**, não **VOLUME**. A presidencial continua
recebendo pesquisas novas, então continua marcada "ok" todo dia. **Perder 88% do histórico
de uma corrida é invisível para o alarme enquanto sobrar uma pesquisa recente.**

O total da base ainda subiu (3.388 → 3.509), porque o ganho das 54 outras corridas cobriu a
perda da presidencial. Um alarme sobre o total nunca pegaria isso: tem de ser **por corrida**.

## Estado do repositório

- Branch `eleicoes-fase-c`: **16 commits não mergeados** (toda a Fase C), pendente do QA
  local do Bera. Roteiro em `docs/qa-fase-c.md`.
- `origin/main`: **17 commits novos** do robô (01/09 a 18/09), um por dia.
- A main roda o código ANTIGO: `polls.json` lá ainda é **schema v1**, sem a flag
  `sintetico` e sem os gates do C0-c. Rebase vai exigir remigrar, como em 31/08.
- **Conta do `gh`:** estava ativa em `bera-omc`, que não enxerga o repo. Troquei para
  `beralzir` em 18/09. Se algo falhar com "Repository not found", é isso. Reverter com
  `gh auth switch -u bera-omc`.

## Checklist

### D0 · Sincronizar e medir o estrago [~10 min, sem pausa]
Rebase da `eleicoes-fase-c` sobre `origin/main` (17 commits). Conflitos esperados em
`dist/` e nos JSON gerados: **resolver rebuildando, nunca escolhendo lado a mão**, e
remigrar o `polls.json` para v2 (as pesquisas novas do robô chegam sem a flag `sintetico`,
e o motor é fail-closed, então vai reclamar, o que é o comportamento certo).
Depois: **medir** o quanto o forecast presidencial mudou por causa da perda, rodando o
motor com a base de 31/08 e com a de hoje.
**Feito quando:** o impacto está em pontos percentuais medidos, não estimado.

### D1 · Causa raiz na presidencial [~25 min, sem pausa]
Descobrir o que mudou na página `Pesquisas de opinião para a eleição presidencial no Brasil
em 2026`: seção renomeada, tabela dividida por período, página nova para o 1º turno, mudança
de classe CSS da wikitable, ou seção de ano fora do filtro `>= 2025` do ingest.
Ferramenta útil: `python3 src/ingest_polls.py --cache DIR` guarda o HTML para inspeção sem
refazer a rede.
**Feito quando:** o ingest volta a ler a ordem de 500 estimuladas de PRES, e a causa está
escrita (não só corrigida), para o alarme do D2 cobrir a classe certa de falha.

### D2 · Alarme de volume, o gate que faltou [~15 min, sem pausa]
Gate novo que compara o volume de pesquisas **por corrida** com o run anterior e reprova
queda acima de um limiar. Calibrar no dado real, como foi feito no C0-c, e **validar com
erro plantado** (plantar uma queda de 88% numa corrida e exigir que o gate reprove).
Ligar em `atualizar_eleicoes.sh` e no `resumo_eleicoes.py`.
**Feito quando:** o gate reprova a queda plantada e passa no dado real.

### D3 · Atualizar tudo e rodar as comparações [~20 min, PAUSA: Bera lê o relatório]
Ingest completo, motor, harness e leaderboard. Com 18 dias de freezes acumulados, o
walk-forward finalmente tem n para discriminar os modelos, que era o objetivo do harness
desde a B5.
Entregar um relatório curto com: o que mudou no forecast desde 31/08, o leaderboard com as
comparações reais, e quais corridas se moveram mais.
**Feito quando:** o relatório está na mão do Bera.

### D4 · QA e publicação [PAUSA DURA]
A Fase C continua pendente de validação local (`docs/qa-fase-c.md`), e agora soma a correção
do incidente. **Nada vai ao ar sem o "autorizo publicar" do Bera, com todas as letras.**
Lembrar: merge na `main` equivale a autorizar a publicação, porque o cron publica sozinho no
ciclo seguinte.

## Fora de escopo, decidido

- **bola-de-cristal:** verificado em 18/09 que a base dele são 5.107 chunks de consumo,
  mídia, marcas e tendências de mercado (McKinsey, Ipsos Flair, Nielsen, GWI, Foresight
  Factory), **sem nenhum lastro político ou eleitoral**. Para "cenário político" ele
  forecastaria sem base, que é o pior resultado possível aqui. O uso legítimo dele seria
  leitura de MÍDIA por público (como a mensagem chega a cada perfil, dado o consumo de
  mídia do TGI), e isso ficou de fora desta rodada por decisão do Bera.
- Campo do survey sintético (C2): segue aguardando `ANTHROPIC_API_KEY`.
- Os 275+ aliases sem match no ingest.

## Riscos

- **Prazo:** 16 dias para o 1º turno. O forecast presidencial está publicado com 11% do
  dado, então D1 é urgente, não importante.
- **A correção pode mover muito o forecast.** Recuperar 450 pesquisas vai mexer no número
  publicado, e o alarme de movimento do C0-c vai disparar (corretamente). Não é para
  liberar com `ALARME_OK=1` no automático: é para o Bera ver o tamanho do movimento.
- **O robô continua rodando** durante a sessão, então pode publicar de novo no meio. Rebase
  de novo antes de qualquer push.
