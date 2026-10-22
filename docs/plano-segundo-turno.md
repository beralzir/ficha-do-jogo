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
| 1 | Fix do `test_lista_parcial` | branch | **feito** (`e861a4b`) |
| 2 | Motor + páginas + teste, com fixture | branch, nuvem | **feito** (`8d96183`, `b81e396`, conversor do TSE) |
| 3 | Baixar resultado do 1º turno (navegador) | Mac | **Bera** |
| 4 | Ingestão + conferir DF na Wikipédia + pipeline completo | Mac (ou nuvem com rede liberada) | Bera/Claude |
| 5 | **Validação local das páginas** | Mac | **Bera (pausa dura)** |
| 6 | Merge na main + `workflow_dispatch` com `force_deploy` | GitHub | Bera |
| 7 | Conferir no ar (`/ficha-do-jogo/`, presidencial, uf-df, uf-pe) | | Claude |
| 8 | Cron diário segue até 24/10; 25/10 não publica | | automático |

## Estado em 22/10/2026 (fim da sessão na nuvem)

Na branch `claude/cool-sagan-qkivlu`, com pipeline completo verde e `dist/` idêntico ao
publicado quando não há `resultado_1t.json` (diff só de 2 regras de CSS):

- `src/eleicoes_model.py`: `valida_resultado_1t` + `anexa_resultado_1t` + apuração no
  `simulate()` (decidida sem sorteio; par da urna; horizonte do 2T medido até 25/10).
- `src/build_eleicoes.py`: modo apuração (index, presidencial, 27 UFs).
- `src/test_segundo_turno.py` no gate (erro plantado no motor: 5 falhas).
- `scripts/build_resultado_1t.py`: JSON "dados simplificados" do TSE (ou CSV manual) ->
  `data/eleicoes/resultado_1t.json`, com o mesmo gate do motor. Provado com arquivos no formato
  do TSE gerados de uma apuração FICTÍCIA (não versionada); erro plantado reprova sem escrever.
  **Risco declarado:** o formato de 2026 do TSE não pôde ser visto da nuvem (rede bloqueada).
  O parser procura `sqcand`/`pvap`/`st` em qualquer nível; se o TSE mudou os nomes, usar o CSV.

## Passos que faltam (Mac do Bera, onde Wikipédia e TSE abrem)

```bash
git fetch origin && git checkout claude/cool-sagan-qkivlu
# 1. resultado do 1º turno: baixar no navegador os JSON de presidente (BR) e de governador e
#    senador das 27 UFs em resultados.tse.jus.br para uma pasta, ex. ~/Downloads/tse-1t/
python3 scripts/build_resultado_1t.py ~/Downloads/tse-1t/
# 2. pesquisas novas + conferir o alarme de volume ANTES de liberar
python3 src/ingest_polls.py
python3 src/check_volume.py      # GOV-DF segundo_turno 40 -> 0? abrir a página do DF na Wikipédia
#    DF tem 2º turno (Celina x Grass): se as pesquisas mudaram de seção/subpágina, é bug de ingest
#    (classe do incidente de 18/09), corrigir antes; os 9 estados decididos perdem o 2T hipotético
#    de forma legítima.
# 3. pipeline com os dois alarmes reconhecidos UMA vez (o motor muda de regime)
VOLUME_OK=1 ALARME_OK=1 ./atualizar_eleicoes.sh
# 4. validação local das páginas (pausa dura): index, presidencial, uf-df, uf-pe, uf-sp
# 5. commit de data/ + dist/ + resultado_1t.json na branch, merge na main (vira a base dos alarmes)
# 6. Actions > atualizar-eleicoes > Run workflow com force_deploy=true; até 24/10 o cron segue sozinho
```

## Execução em 22/10/2026 (tarde), com o runner do GitHub

O Bera autorizou um workflow temporário na branch (sem deploy, sem segredo) porque a nuvem do
Claude não acessa Wikipédia nem TSE. Três rodadas (39813701299, a 2ª cancelada por timeout do TSE,
e a 3ª); workflow e pasta `diag/` removidos depois.

- **Causa real do alarme de volume (corrige a leitura acima):** NENHUMA das 10 perdas era legítima.
  As páginas de GOV dos 10 estados foram reestruturadas para `Governador > Primeiro turno /
  Segundo turno`; o `section_kind` lia só o topo e jogava o 2T no 1T (DF 0 -> 48 listas de 2 nomes
  como estimuladas). Fix no `ingest_polls.py`; com ele o alarme de volume fica VERDE contra a main
  sem `VOLUME_OK`.
- **Apuração:** `resultados.tse.jus.br/oficial/ele2026/{6257,6259}/dados/<uf>/<uf>-c000N-e00XXXX-u.json`
  (55/55), cru em `data/live/tse_resultado_1t/`. 2º turno: PRES (Flávio 47,03 x Lula 45,16) e GOV
  AC AM DF ES RN TO. PR (Moro 50,10%) e RJ decididos no 1º turno (a imprensa divergia).
- **Pesquisas até 21/10** (299 novas desde a última base), 2T pós-apuração em todos os 7 pares.
- Dois gates com a mesma doença do dado do dia, corrigidos: `test_movimento_gate` (piso "0" ainda
  exigia d_share > 0; pares com share idêntico entre freezes) e `test_propostas_link` (regra da
  linha passa a vir do voto oficial no modo apuração).
- `./atualizar_eleicoes.sh` completo: **GATES VERDES**, alarme de movimento verde sem `ALARME_OK`.

Falta: validação do Bera (pausa dura), merge na main e `workflow_dispatch` com `force_deploy=true`.
