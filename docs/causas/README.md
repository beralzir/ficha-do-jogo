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
  inflexões de Celina em 01, 15 e 18/08; chip `task_410cc639`); registros Veritá com 3 nomes em
  base bruta (`verit-sen-go-2026-09-17`, `verit-sen-rj-2026-09-18`) e `verit-pres-2026-09-12`
  com só Lula e Flávio marcado como estimulada de 1º turno (provável 2º turno); linha Ranking
  Brasil 23 a 27/08 no MS com Soraya 32,2 (conferir na fonte primária).
- **Lacunas por orçamento** (não é "não existe"): imprensa regional de MA, SC, MS, PB, GO, PA,
  BA, RN, SE, TO, CE; Lupa e Aos Fatos; TSE (representações); data do TRE-DF no caso Arruda.
  Cada resultado lista, na seção 5, a próxima sessão de discovery em ordem de prioridade.
