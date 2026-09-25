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
  acusa duplicatas. NÃO é gate e NÃO escreve no repo: a curadoria final é humana. Rodar com
  `CAUSAS_DIR=<pasta com os resultados> python3 docs/causas/sintese_causas.py`.

Os resultados dos três agentes (lançados na sessão de 25/09) caem em
`/private/tmp/claude-501/-Users-beralzir-Projetos-ficha-do-jogo--claude-worktrees-exciting-khorana-550dba/51aa27e1-edf2-42df-bbe5-4d7e4c7a616d/scratchpad/causas_P{1,2,3}_resultado.md`.
Se essa pasta não existir mais, relançar os três a partir dos dossiês daqui (prompt no
`SESSION.md`, bloco HANDOFF).
