# Pesquisa de causas das inflexões (25/09/2026)

Insumos e ferramenta da pesquisa "por que as inflexões aconteceram", pedida pelo Bera em 25/09
depois de recusar as 12 hipóteses de tendência ("as hipóteses devem ser o porquê, não as
inflexões em si; precisa de cruzamento com notícias e outras fontes").

- `dossie_bdc.md`: dossiê original das inflexões (122 destaques, 32 choques comuns, as_of 24/09).
- `causas_P1.md`, `causas_P2.md`, `causas_P3.md`: dossiês por período (agosto; 1 a 15/09; 16 a
  24/09) com o CONTRATO DE SAÍDA dentro: evento candidato no schema do `eventos.json` (fonte
  com URL, veículo, data de acesso), mecanismo marcado [fato]/[inferência]/[hipótese], e as
  três pernas de teste (placebo no M3; implicações cruzadas conferíveis agora; replicação para
  a frente, pré-especificada).
- `sintese_causas.py`: extrai os blocos JSON dos `causas_P*_resultado.md`, valida cada evento
  com `eleicoes_eventos.valida(doc, sqs_validos)`, separa exploratório de pré-especificado e
  acusa duplicatas. NÃO é gate e NÃO toca o `eventos.json`: só escreve `causas_sintese.json`
  na pasta dos resultados; a curadoria final é humana. Rodar com
  `python3 docs/causas/sintese_causas.py` (ou `CAUSAS_DIR=<outra pasta>` para resultados fora
  do repo).
- `causas_P1_resultado.md`, `causas_P2_resultado.md`, `causas_P3_resultado.md`: os RESULTADOS
  dos três agentes (bola-de-cristal, 25/09, ~25 a 30 min cada, 2 buscas + 6 acessos web por
  agente, orçamento esgotado nos três). Cada um traz: fontes com URL e data de acesso, tabela
  data → evento candidato ou "sem evento plausível" (com o que foi procurado), bloco JSON no
  schema do `eventos.json`, mecanismo e implicações cruzadas por evento, e a seção "o que não
  dá para afirmar".
- `causas_sintese.json`: saída de `sintese_causas.py` sobre os três resultados (rodado em
  25/09): 29 eventos extraídos, 26 válidos pelo validador, 3 recusados.

## O que a rodada de 25/09 trouxe (para a curadoria)

- **Nenhum evento causou nada**, por construção: todos os passados nascem exploratórios
  (registrados em 25/09); só 5 registros nascem pré-especificados (Globo presidencial 01/10,
  Globo Minas 29/09, Cabo Branco PB 29/09, e as cópias do Globo em P1 e P3).
- **Três famílias de duplicata**, a resolver à mão antes de entrar no `eventos.json`: o debate
  da Globo de 01/10 aparece três vezes com DIREÇÃO DIVERGENTE (P2 prevê "+" por exposição; P1 e
  P3 preveem "-" condicional à presença de Lula e Flávio, com ramo "+" se os líderes faltarem);
  a cassação de Marçal em 11/09 (P1 e P2); o cancelamento do debate do consórcio em 08/09 (P2 e P3).
- **Três eventos recusados** pelo validador só por tipo: classe "candidatura" (desistência de
  Canella e confirmação de Jordy no Senado-RJ, convenção do Avante), que não existe em `TIPOS`
  de `src/eleicoes_eventos.py`. É a classe que domina agosto (mês do registro). Decisão do Bera:
  estender `TIPOS` ou deixar de fora. Tipos também ausentes, citados como drivers: tempo de TV,
  propaganda, atos de campanha.
- **Leitura convergente dos três**: a maioria das DATAS dos destaques é chegada de lote
  (Veritá com 7 e 9 corridas no mesmo campo_fim) ou casa de indecisos baixos (AtlasIntel,
  Palver, Veritá); as TENDÊNCIAS reais (Cury sobe até 04/09 e devolve; Kalil, Jordy e
  Portinho, Calil) são lentas e sem salto datável. Só duas famílias têm evento com fonte
  primária aberta: presidencial (Band 23/08, Toffoli x Renan 31/08, Quaest 01/09, consórcio
  08/09, Marçal 11/09) e DF (Arruda indeferido, TSE 24/09; data do TRE-DF NÃO confirmada).
- **Achados de dado, sem mexer no repo** (candidatos a correção na ingestão): aliases
  contaminados por linha de nota da Wikipédia nas pesquisas do DF de 17 a 19/07 (fabricam as
  inflexões de Celina em 01, 15 e 18/08; chip `task_410cc639`; a mesma classe contamina as
  quatro pesquisas de SEN-MG de agosto, com as 7 colunas casadas no sq de Gustavo Galassi, que o
  site publicava com 55% de share); linha Ranking Brasil 23 a 27/08 no MS com Soraya 32,2
  (conferir na fonte primária).
- **Registros Veritá de lista parcial: CONFERIDOS NA FONTE E CORRIGIDOS NO MOTOR (25/09,
  sessão seguinte).** `verit-sen-go-2026-09-17` e `verit-sen-rj-2026-09-18` são assim na
  Wikipédia (revisões 73047276 e 73048530: travessão nas outras cinco colunas; a citação é um
  post de Instagram "Intenção de voto para Senador, votos válidos", só o top-3). Não é
  truncamento da extração. `verit-pres-2026-09-12` é 1º turno estimulado com os outros 11
  candidatos somados em "Outros" 14,5% (nota [c] da tabela, revisão 73050701), não 2º turno.
  Mecanismo: o share normalizado entre os casados infla quem está numa lista que deixa de
  fora candidatos com massa (1,56x no SEN-GO, 1,17x na PRES), e o filtro lê salto simultâneo
  de todos os listados. Correção em `src/eleicoes_model.py` (`COBERTURA_MIN=0,9`, reaproveita
  o 0,9 do `MATCH_MIN`; `MIN_CASADOS` por candidato distinto), gate `src/test_lista_parcial.py`.
  Efeito medido nos destaques (as_of 24/09): os 8 registros-alvo somem; 122 -> 106 destaques;
  SEN-RJ 8 -> 0, SEN-GO 3 -> 2 (Calil fica com 04 e 10/09, corroborados por listas cheias);
  a inflexão de Celina em 15 e 18/08 (GOV-DF) também some, porque a pesquisa Paraná de 19/07
  cai por cobertura (m=37%), mas a causa raiz dos aliases do DF segue no chip.
- **Lacunas por orçamento** (não é "não existe"): imprensa regional de MA, SC, MS, PB, GO, PA,
  BA, RN, SE, TO, CE; Lupa e Aos Fatos; TSE (representações); data do TRE-DF no caso Arruda.
  Cada resultado lista, na seção 5, a próxima sessão de discovery em ordem de prioridade.

## Curadoria de 25/09 (tarde): o que entrou no registro, por decisão do Bera

Decisões por clique, uma por vez, na sessão de retomada:

1. **Critério de entrada:** entram os eventos com fonte primária aberta, número conferido no
   `polls.json` ou tabela da Wikipédia (17). Ficam de fora, pendentes aqui, os 5 conhecidos só
   por manchete de feed do Google News (IPTU de Kalil 18/09, debate do Flow 21/09, Record MG sem
   Kalil 21/09, Nexus/BTG com Caiado no 2º turno 21/09, Folha sobre a empresa da filha de Cury
   22/09): entram quando uma sessão abrir os artigos.
2. **Classe `candidatura`:** passa a existir em `TIPOS` (validador) e em `_tipos` (arquivo), e os
   3 eventos dela entram como exploratórios (Canella 03/08, Jordy 04/08, convenção do Avante
   03/08). O gate `test_eventos.py` exige que as duas listas casem.
3. **Debate da Globo de 01/10:** um só registro (`debate-globo-pres-2026-10-01`, direção "-" no
   ramo provável, os dois líderes no palco) e os dois ramos em `hipoteses.json`
   (h-2026-09-25-13 e 14; a de condição falsa fecha como `nao_testavel`).

Duplicatas fundidas: Globo 01/10 (3 registros), cassação de Marçal 11/09 (2), cancelamento do
consórcio 08/09 (2). Resultado: **21 eventos** no registro (o do Cury de 21/09 mais 20 novos), 3
pré-especificados (Globo Minas 29/09, Cabo Branco PB 29/09, Globo 01/10).

`hipoteses.json` v2: 8 hipóteses de CAUSA (h-2026-09-25-13 a 20), cada uma ligada por
`origem.evento_id` a um evento do registro e com as três pernas de teste (placebo no M3,
implicações cruzadas com `conferido`, replicação para a frente ou `disponivel: false` com
motivo). `python3 src/eleicoes_hipoteses.py --conferir` imprime o que o detector publicado diz
hoje sobre cada implicação. As 12 de tendência ficam no arquivo e fora da página.

Achados de dado que NÃO foram tocados (candidatos a tarefa própria na ingestão): aliases
contaminados do DF (17 a 19/07); registros Veritá de 3 nomes em base bruta
(`verit-sen-go-2026-09-17`, `verit-sen-rj-2026-09-18`) e `verit-pres-2026-09-12` com só Lula e
Flávio como estimulada de 1º turno; linha Ranking Brasil 23 a 27/08 no MS com Soraya 32,2;
"Véritas" e "Veritá" no MA sem alias. Pendência à parte: `structure.json` (captura de 29/08)
ainda lista Marçal como concorrendo e não tem Avalanche.
