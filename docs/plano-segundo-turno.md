# Plano · site vira para o 2º turno (22/10/2026)

> Rumo escolhido pelo Bera em 22/10 (clique "Virar para o 2º turno"). **Prazo duro: no ar até
> sábado 24/10**; domingo 25/10 é dia de eleição (Lei 9.504, art. 39, §5º, IV) e o cron não publica.
> Regra da edição mantida: conteúdo novo valida LOCAL com o Bera antes do deploy.

## Diagnóstico (por que parou)

Último deploy: rodada manual 63 (04/10). Rodadas 64 a 80 (05/10 a 21/10) reprovaram:

| Período | Gate | Causa | Estado |
|---|---|---|---|
| 05 a 14/10 | `test_lista_parcial.py` §2 | piso de massa ausente (15%) medido no dado do dia; a PRES de 12/09 caiu para 14,4% com as pesquisas novas | **corrigido** (piso no `6d5eba3`; erro plantado reprova) |
| 15 a 21/10 | `check_volume.py` | 10 corridas perderam todo o `segundo_turno`: PE CE MT DF GO PB BA MA AL MS | aberto |

Leitura da 2ª causa (não confirmada: a Wikipédia está bloqueada no ambiente da nuvem): 9 estados
decidiram no 1º turno e os editores apagaram os cenários hipotéticos (perda legítima). O **DF tem
2º turno** (Celina x Grass) e perdeu as 40, o que é cara de reestruturação de página (classe do
incidente de 18/09). Tem de ser conferido antes de liberar com `VOLUME_OK=1`.

**Problema de fundo:** o motor não sabe que o 1º turno aconteceu. Destravar o cron sem mudar nada
publicaria probabilidade de 1º turno para eleição já apurada.

## O que muda

### 1. Resultado do 1º turno como dado versionado
`data/eleicoes/resultado_1t.json` (novo), fonte TSE, uma entrada por corrida:
```json
{"GOV-DF": {"status": "segundo_turno", "finalistas": [sqA, sqB], "votos_validos": {"sqA": 0.41, ...}},
 "GOV-PE": {"status": "decidida", "eleitos": [sq], "votos_validos": {...}},
 "SEN-SP": {"status": "decidida", "eleitos": [sq1, sq2], "votos_validos": {...}}}
```
Captura: o TSE barra fora de navegador (Akamai), então baixa-se no navegador (resultados.tse.jus.br
ou a totalização do DivulgaCandContas) e um script OFFLINE monta o JSON, com gate: 55 corridas,
todo sq existe na structure, Σvotos_validos ≈ 1, `decidida` com 1 eleito (2 no Senado) e
`segundo_turno` só em corrida `two_round` com o 1º colocado < 50%.

### 2. Motor (`eleicoes_model.py`), mudança mínima
- Corrida `decidida`: eleito = 1 para quem ganhou, sem Monte Carlo.
- Corrida `segundo_turno`: par FIXO = finalistas; P(vitória) vem das pesquisas de 2T do par
  (`runoff_prob_from_polls`, já existe); sem pesquisa do par, repasse a partir dos votos válidos do
  1º turno + `RUNOFF_PP` (também já existe). t2 = 1 para os dois, t1_win = 0.
- Sem `resultado_1t.json`, comportamento de hoje (os testes do harness com dado antigo seguem iguais).
- Invariantes continuam valendo (Σeleito = vagas, Σt2 = 2 − Σt1_win, eleito ≤ t2).

### 3. Páginas (`build_eleicoes.py`)
- Presidencial: "2º turno · Flávio Bolsonaro x Lula", barra do 1º turno apurado (oficial) + P(vence) e
  pesquisas de 2T do par. Somem as colunas de 1º turno projetado.
- UF: governador decidido = selo "Eleito no 1º turno · X%"; com 2º turno = par + P(vence). Senado =
  "Eleitos" com %.
- Faixa no topo: "1º turno apurado pelo TSE em 04/10; o modelo agora projeta só o 2º turno (25/10)".

### 4. Gates e alarmes
- `check_movimento` vai disparar (probabilidades vão a 0/1): liberar UMA vez com `ALARME_OK=1` na
  rodada local de validação, com o diff lido.
- `check_volume`: conferir o DF na Wikipédia; se for reestruturação, corrigir o ingest (como em
  18/09); se legítimo, `VOLUME_OK=1` uma vez. O commit dessa rodada vira a nova base do alarme.
- Teste novo `test_segundo_turno.py`: decidida não sorteia; par fixo; sem o JSON nada muda;
  erro plantado (finalista fora do par) reprova.

### 5. Fora de escopo (anotado)
Brier do 1º turno no leaderboard (agora dá para medir), Inflexões pós-1T, santinho.

## Sequência e pausas

| # | Passo | Onde | Quem |
|---|---|---|---|
| 1 | Fix do `test_lista_parcial` | branch | feito |
| 2 | Motor + páginas + teste, com fixture | branch, nuvem | Claude |
| 3 | Baixar resultado do 1º turno (navegador) | Mac | **Bera** |
| 4 | Ingestão + conferir DF na Wikipédia + pipeline completo | Mac (ou nuvem com rede liberada) | Bera/Claude |
| 5 | **Validação local das páginas** | Mac | **Bera (pausa dura)** |
| 6 | Merge na main + `workflow_dispatch` com `force_deploy` | GitHub | Bera |
| 7 | Conferir no ar (`/ficha-do-jogo/`, presidencial, uf-df, uf-pe) | | Claude |
| 8 | Cron diário segue até 24/10; 25/10 não publica | | automático |
