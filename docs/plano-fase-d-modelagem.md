# Handoff de modelagem para o projeto (Fase D, sugestão)

> Escrito em 21/09/2026 a partir da revisão em `memo_modelagem_eleicoes_2026.md` (v3).
> **13 dias para o 1º turno (04/10) e 34 para o 2º (25/10).** A coluna "quando" de cada
> item leva isso em conta: há coisa que só faz sentido depois da apuração.
> Formato deliberadamente igual ao dos `docs/plano-fase-*.md` para poder ser colado como
> `docs/plano-fase-d-modelagem.md` e lido pelo Claude Code sem tradução.

---

## 1. Ponto de partida

O que o repo já tem, e que este documento **não** propõe refazer:

- agregador com house effect, incerteza por candidato e Monte Carlo por corrida, com
  invariantes testados no run;
- harness multi-modelo com freezes diários, métrica pré-especificada e leaderboard
  walk-forward (19 freezes, 824 comparações em 21/09);
- três camadas de defesa na entrada: gate de plausibilidade, alarme de movimento e, desde o
  incidente, alarme de volume por corrida;
- separação fail-closed entre pesquisa real e sintética, provada por teste.

O que a revisão mostrou que falta, em uma frase cada:

| # | lacuna | evidência |
|---|---|---|
| L1 | O agregador não distingue **nível** de **tendência** | v1 dá Lula 51,6% e o espaço de estados dá 45,8% lendo as mesmas pesquisas; a diferença é o nível caindo 2,4 p.p. desde julho |
| L2 | As variantes do harness **não discriminam** | MAE de 0,0357 a 0,0360 entre os cinco modelos: são o mesmo modelo com parafusos diferentes |
| L3 | Não há **datação de movimento** | o site mostra o nível, não responde "quando mudou e quanto" |
| L4 | Não há **atribuição** | nada liga movimento a evento, que é a pergunta original do projeto |
| L5 | O parâmetro mais importante do forecast **não é estimado** | o erro sistemático no dia da eleição é chute em todos os modelos, inclusive no meu |
| L6 | Instituto com 1 pesquisa pesa quase como Datafolha | não há prior de reputação |
| L7 | P(eleito) é métrica de alarme ruim num empate | 1 p.p. de share vira ~12 pontos de probabilidade |

---

## 2. Catálogo priorizado

Custo em **tempo de execução de sessão**, na convenção adotada em 31/08.

### M1 · Competidor `v2_estado`: Kalman de nível local com efeitos por instituto

| | |
|---|---|
| **resolve** | L1, L2 |
| **quando** | antes do 1º turno; é o único item desta lista que muda o número publicado |
| **entrada** | `data/live/polls.json`, nada novo |
| **saída** | `data/eleicoes/models/freeze-<as_of>-v2_estado.json`, schema atual do harness |
| **custo** | ~40 min (o esqueleto está pronto e validado, ver §5) |

Estado escalar em logit por candidato: `mu_t = mu_{t-1} + w_t` (passeio aleatório),
`y_it = mu_t + d_j + v_it`. Viés de casa `d_j` por ponto fixo com encolhimento; variância da
observação vinda da binomial com efeito de desenho mais ruído não amostral. Suavizador RTS
para a série completa.

**Já validei que a versão stdlib reproduz a bayesiana** (NUTS, numpyro), no 2º turno
Lula × Flávio com 133 pesquisas:

| comparação | resultado |
|---|---|
| nível latente hoje | Kalman 49,58% vs NUTS 49,73% (**0,15 p.p.**) |
| série inteira (253 dias) | erro médio absoluto **0,16 p.p.**, máximo 1,21 |
| viés de casa, 19 institutos | correlação **0,997** |

Ou seja: a restrição stdlib do repo não custa precisão aqui. Custa a cauda pesada (ver M2).

**Critério de pronto:** freeze gerado com invariantes verdes; leaderboard roda com o
competidor; `test_synths_gate` continua verde (o novo modelo nasce com `POLL_SOURCE: real`).

**Risco declarado:** o modelo tem um parâmetro livre (`SIGMA_RW`) que não se estima bem com
n pequeno. Calibrei fora, com o ajuste bayesiano: 0,0132 em logit/dia no 2º turno. Isso deve
ser **recalibrado uma vez por mês**, não a cada rodada, e o valor usado vai no `params` do
freeze (o harness já grava isso).

### M2 · Detector de salto por resíduo padronizado

| | |
|---|---|
| **resolve** | L3 |
| **quando** | junto com M1, sai quase de graça |
| **entrada** | os resíduos que o filtro do M1 já produz |
| **saída** | `data/eleicoes/inflexoes.json`: `[{corrida, sq, data, z, delta_pp}]` |
| **custo** | ~15 min sobre o M1 |

Resíduo padronizado da inovação `(y - previsão)/sqrt(S)`; `|z| > 3` marca candidato a ponto
de inflexão. É o que os agregadores clássicos fazem. Testado no 2º turno, acha **16/05 com
z = 5,0**, que é exatamente o salto que o modelo de cauda pesada estimou em +4,7 p.p. na
janela de 10 dias; acha também 17/01 (z = −3,0) e 28/02 (z = −4,0), episódios menores.

**Limitação honesta:** o resíduo padronizado detecta o salto, mas não separa "houve um salto
de X p.p." de "houve uma pesquisa fora da curva". A versão bayesiana com t de Student faz
essa separação porque o salto vira parâmetro com IC. Se o detector der falso positivo em
corrida pequena, o remédio é exigir `|z| > 3` **em duas pesquisas seguidas** de institutos
diferentes, não baixar o limiar.

### M3 · Registro de eventos pré-especificado + estudo de evento

| | |
|---|---|
| **resolve** | L4, que é a pergunta original do projeto |
| **quando** | o registro começa **agora** (é retroativo e perde valor a cada dia); a análise, depois do 1º turno |
| **entrada** | curadoria: agências de checagem (Lupa, Aos Fatos), decisões do TSE sobre propaganda e representações por desinformação, agenda de debates |
| **saída** | `data/eleicoes/eventos.json` + seção no relatório |
| **custo** | ~30 min o schema e o primeiro preenchimento; a curadoria é contínua |

```
{ "schema_version": 1,
  "eventos": [ {
    id: "debate-band-2026-09-28",
    data: "2026-09-28",              // data do FATO, não da divulgação
    tipo: "debate"|"decisao_judicial"|"denuncia"|"peca_desinformacao"|"economico"|"pesquisa_bomba",
    alvo: [sq, ...],                 // candidato(s) afetado(s)
    direcao_esperada: "+"|"-"|"?",   // PREENCHER ANTES DE OLHAR O EFEITO
    fonte: {url, veiculo, acesso},
    escopo: "nacional"|"UF",
    notas: str
  } ] }
```

O campo `direcao_esperada` é o único que importa metodologicamente: com ~50 eventos no ano e
um detector que acha 3 saltos, sempre haverá "um evento perto". A pré-especificação é o que
separa análise de racionalização, e é a mesma disciplina do §5.4 da retrospectiva da Copa
("espaço de medição definido ANTES de medir").

**Estudo de evento** (depois do 1º turno): efeito = `mu(t_e + h) − mu(t_e − 1)` para
h = 3, 7, 14, com banda vinda da variância do suavizador. Janela placebo com datas sorteadas
sem evento dá a distribuição nula. Só declara efeito se o salto coincide **e** o placebo não
reproduz a magnitude.

**A assinatura que interessa:** desinformação viral, se funciona, produz **impulso com
decaimento** (efeito no dia, meia-vida de 1 a 3 semanas); economia e fadiga produzem
**deriva**. O caso de Cury é o exemplo já observado: salto de +3,0 p.p. no dia 27/08
(P = 0,63), nível +5,9 p.p. entre 20/ago e 05/set, e reversão gradual de −2,7 p.p. em
setembro sem segundo salto. Modelar o impulso com dois parâmetros (tamanho e meia-vida) e
comparar com o passeio puro é um teste formal. Atenção ao rótulo: salto diário e variação de
nível entre datas são escalas diferentes, e a segunda é cerca do dobro da primeira aqui.

### M4 · Calibrar o erro sistemático com 2018 e 2022

| | |
|---|---|
| **resolve** | L5, o parâmetro mais importante e o único não estimado |
| **quando** | antes do 1º turno se der tempo; é o de maior retorno por hora |
| **entrada** | pesquisas da última semana de 2018 e 2022 (as mesmas páginas da Wikipédia, o ingest já sabe ler) + resultado oficial do TSE |
| **saída** | `data/eleicoes/calibracao_erro.json` com o desvio por instituto e o agregado |
| **custo** | ~45 min |

Para cada instituto, em cada uma das quatro rodadas (2018 1T/2T, 2022 1T/2T): erro = share
previsto na última pesquisa menos share apurado. A distribuição desses erros dá (a) o desvio
sistemático do agregado, que hoje é chute de 2,5 p.p. em todos os modelos, e (b) um prior por
instituto que alimenta o M5.

**Por que importa mais do que parece:** esse parâmetro sozinho decide se o site publica
"46% contra 54%" ou "empate técnico". Com 2,5 p.p., P(Lula) dá 45,8%; com 1,5 p.p. daria algo
perto de 42%; com 3,5 p.p., perto de 47%. É o parâmetro com maior alavanca sobre o número
publicado e o único que ninguém estimou.

**Critério de pronto:** o número usado no modelo tem origem documentada em dado brasileiro,
não em literatura americana nem em chute.

### M5 · Prior de reputação por instituto

| | |
|---|---|
| **resolve** | L6 |
| **quando** | depois do M4, que o alimenta |
| **entrada** | `calibracao_erro.json` do M4 |
| **saída** | campo `prior_vies` por instituto em `data/eleicoes/aliases.json` |
| **custo** | ~20 min sobre o M4 |

Hoje o encolhimento do viés de casa usa só o n da rodada atual. Com histórico, o instituto
entra com média a priori e o encolhimento passa a ser para **o viés histórico dele**, não
para zero. Efeito prático: uma pesquisa nova de instituto desconhecido para de mover o
agregado tanto quanto uma de Datafolha.

### M6 · Cortes por segmento

| | |
|---|---|
| **resolve** | mecanismo (onde o movimento acontece), complementa M3 |
| **quando** | depois da eleição, salvo se aparecer evento grande na reta final |
| **entrada** | Quaest, Datafolha e AtlasIntel publicam cortes por região, renda, escolaridade, religião, gênero e idade |
| **saída** | campo `segmento` em `numeros[]` do `polls.json`; o motor roda por segmento sem mudança |
| **custo** | ~1h (o ingest precisa aprender a ler as tabelas de corte) |

Um evento que move o agregado 2 p.p. mas move evangélicos 6 e católicos 0 conta uma história;
um que move todos os cortes igualmente conta outra. É a camada com melhor razão
informação/custo depois do M3, e é o ponto de encontro natural com as 5 fichas de público:
elas geram a hipótese, o corte real testa.

### M7 · Trocar P(eleito) por share no alarme da presidencial

| | |
|---|---|
| **resolve** | L7 |
| **quando** | agora, é de uma linha |
| **custo** | ~10 min com o teste |

`check_movimento.py` dispara em 20 p.p. de P(eleito). Numa corrida empatada isso equivale a
~1,7 p.p. de share, e numa corrida decidida pode ser movimento de 10 p.p. de share que não
dispara nada. O gatilho estável é o share. Medida do próprio repo que ilustra: recuperar 483
pesquisas moveu **0,0 p.p. em P(eleito)**; três semanas de pesquisa nova moveram **15 pontos**.

### M8 · Correlação 1º turno → par de 2º turno

| | |
|---|---|
| **resolve** | limitação já declarada no `eleicoes_model.py` ("prob de 2T por par é constante entre sims") |
| **quando** | entre os turnos, se houver 2º turno |
| **custo** | ~30 min |

Hoje a probabilidade do par é pré-computada das pesquisas de 2T e não correlaciona com a
força sorteada no 1T na mesma simulação. Candidato que sorteia um 1T forte deveria entrar no
2T um pouco mais forte. Implementação barata: regredir a margem de 2T na margem de 1T nas
pesquisas que têm os dois cenários no mesmo campo, e usar o coeficiente como ajuste dentro
da simulação.

### M9 · Fechar a medição com Brier depois da apuração

| | |
|---|---|
| **resolve** | o objetivo declarado do harness desde a B5 |
| **quando** | 05/10 e 26/10 |
| **custo** | ~30 min (o `finalize_scores.py` da Copa é o molde) |

Brier de P(eleito) por corrida contra o resultado oficial, mais acerto do par presidencial e
**curva de calibração**: separar os candidatos em faixas de probabilidade prevista e comparar
com a frequência observada. Com 55 corridas há n suficiente para uma curva grosseira, o que
a Copa não teve. É o único momento em que se descobre se as bandas estavam certas.

---

## 3. O que NÃO levar para o repo

- **numpyro/JAX/NUTS.** Quebra o "só stdlib", e o M1 mostra que não é preciso: 0,16 p.p. de
  diferença. O ajuste bayesiano fica fora do repo, como ferramenta de calibração mensal dos
  hiperparâmetros (`SIGMA_RW`, `S_EXTRA`, `TAU_HOUSE`). Se quiser rastreabilidade, versione o
  JSON de saída da calibração, não o ambiente.
- **Pesquisa sintética no oficial.** A regra dura já existe e o gate já prova. Nada aqui
  muda isso: o M6 usa os públicos para gerar hipótese, e quem testa é o corte real.
- **Modelo que aprende sozinho os hiperparâmetros a cada rodada.** Com uma eleição só, isso
  é overfitting com passos extras. Calibração mensal, valor congelado no freeze.
- **Mais variantes de ponderação do agregador atual.** O leaderboard já respondeu: 0,3
  milésimo de MAE entre cinco delas. Variante nova só se for estruturalmente diferente.

---

## 4. Ordem sugerida

**Antes do 1º turno (13 dias):** M7 (10 min) → M1 + M2 (~55 min) → M4 (45 min) → começar o
registro do M3.
Justificativa: M7 é correção de um gatilho errado; M1+M2 dão o competidor que o leaderboard
precisa e a datação que a página de inflexões vai usar; M4 tem a maior alavanca sobre o
número publicado. O registro do M3 é retroativo e perde valor a cada dia que passa.

**Entre os turnos:** M5, M8, e a página "Inflexões" (nível latente com banda em SVG gerado em
Python, faixas nos saltos do M2 e a linha do tempo do M3 embaixo; o leitor vê "aqui o modelo
detectou movimento, aqui houve evento, coincidem ou não", sem afirmar causa).

**Depois da apuração:** M9 primeiro (enquanto o resultado é notícia), depois M3 completo
(estudo de evento com placebo) e M6.

**Regra da casa preservada:** nada disso vai ao ar sem validação local. M1 muda o número
publicado se virar oficial, então a recomendação é entrar **como competidor** e só ser
promovido depois de o walk-forward mostrar vantagem, que é exatamente para isso que o harness
existe.

---

## 5. Anexo: esqueleto do M1

`eleicoes_model_v2.py` acompanha este documento: 257 linhas, só stdlib, determinístico,
sem rede. Roda hoje no `polls.json` do repo (testei na cópia de leitura) e imprime a
presidencial. Não é commit: é código para ler o diff e decidir.

Contém: filtro de Kalman escalar com suavizador RTS, estimação do viés de casa por ponto fixo
com encolhimento, previsão por Monte Carlo com semente do modelo, e o detector de salto do
M2. Os defaults vêm da calibração bayesiana e estão documentados linha a linha no topo do
arquivo, com a ressalva de qual deles é chute (`ERRO_ELEICAO`) e qual foi estimado.

O que falta para virar commit, e que deixei de propósito para quem conhece as convenções:
o wrapper `--freeze` no schema exato do harness, a entrada no `model_configs.json`, e o
teste de invariantes no formato do `test_eleicoes_structure.py`.

---

## 6. Uma coisa que eu não faria

Pular o M4 e continuar publicando probabilidade com erro sistemático chutado. Hoje o site
publica 51,6% para Lula e o meu modelo publica 45,8%; os dois leem as mesmas pesquisas, e
boa parte da diferença está num parâmetro que ninguém mediu. Num projeto cuja premissa é
"modelagem probabilística honesta", esse é o buraco mais desconfortável, e é o mais barato
de tapar: são quatro rodadas de eleição brasileira, dado público, uma tarde.

---

# Verificação antes de executar (Claude Code, 21/09/2026)

> Este bloco foi acrescentado no repo, depois de conferir o pacote contra o código real em
> vez de aceitar o texto. **Leia antes de começar: três coisas do pacote não se confirmaram
> como escritas, e uma delas é um bug que precisa ser corrigido antes do commit.**

## O que confere

| afirmação | veredito |
|---|---|
| `eleicoes_model_v2.py` é stdlib puro, sem rede | **confere**: 262 linhas, 5 imports (`datetime`, `json`, `math`, `os`, `sys`), zero ocorrências de rede |
| determinístico | **confere**: duas execuções byte-idênticas |
| reaproveita `em.usable_polls` do motor oficial | **confere**: import adiado dentro de `main()`, herda `MATCH_MIN` e a separação real/sintético |
| os CSV de `dados/` vêm do nosso `polls.json` | **confere**: 542 linhas contra 543 PRES estimuladas reais hoje (1 pesquisa nova desde a geração) |
| roda contra o `polls.json` do repo | **confere**: Lula 41,08% · Flávio 38,96% em 21/09 |

## O que NÃO confere, e precisa de correção

1. **O docstring do `eleicoes_model_v2.py` anuncia `--freeze` na seção de uso, e o `--freeze`
   não existe.** O `main()` não lê `argv`. Rodar com a flag imprime a tabela e não grava nada.
   O README do pacote diz corretamente que o wrapper falta; o docstring do arquivo, não.
   **Corrigir os dois juntos:** implementar e deixar o docstring verdadeiro.

2. **BUG: o `as_of` do v2 não respeita `POLL_SOURCE`.** Linha ~249:
   `max(p["campo_fim"] for p in polls_doc["polls"] if p["campo_fim"] and not p.get("sintetico"))`.
   O filtro `not sintetico` está cravado em vez de derivar das pesquisas VISÍVEIS àquele
   modelo. **É a mesma classe de bug que o C3 corrigiu no motor oficial em 31/08**, quando
   descobrimos que o oficial não lia dado sintético mas herdava o `as_of` dele (o gate não
   pegou; o diff byte a byte pegou). Um competidor com `POLL_SOURCE` sintético nasceria com
   `as_of` errado. Corrigir antes do commit, derivando o `as_of` do mesmo conjunto que o
   modelo enxerga.

3. **M7 está descrito de forma incompleta.** O texto diz que o `check_movimento.py` "dispara
   em 20 p.p. de P(eleito)". O gatilho real é `d_share > 10 OU d_eleito > 20`, ou seja, já
   existe trigger de share. "Trocar P(eleito) por share" REMOVERIA um gatilho, e com ele a
   detecção de movimento grande de probabilidade em corrida não empatada.

   **Evidência nova, do run de 21/09 deste repo**, que o pacote não tinha. Os 4 alarmes reais:

   | corrida | Δshare | ΔP(eleito) | disparou por |
   |---|---|---|---|
   | SEN-MG | 40,73pp | 19,73pp | share |
   | SEN-MG | 15,67pp | 34,44pp | ambos |
   | SEN-ES | **5,97pp** | 28,36pp | **só P(eleito)** |
   | SEN-PR | **6,61pp** | 23,94pp | **só P(eleito)** |

   Metade dos alarmes veio de P(eleito) sozinho com share pequeno, que é exatamente o falso
   positivo que o M7 quer matar. **Forma recomendada:** manter os dois gatilhos e exigir um
   PISO de share junto do de P(eleito), em vez de apagar. Calibrar nesses 4 casos: os dois
   de baixo têm de silenciar, os dois de cima têm de continuar disparando.

## Onde está o resto do pacote

`/Users/beralzir/Downloads/ficha-do-jogo-modelagem.zip`. Contém `src/eleicoes_model_v2.py`,
os CSV de `dados/`, as figuras e os scripts de `pesquisa/` (esses últimos precisam de
numpyro/JAX e **não vão para o repo**, por decisão do próprio pacote e pela regra zero-dep).

## Regras da casa que valem aqui

- **Nada de Eleições vai ao ar sem validação local do Bera.** Merge na `main` equivale a
  autorizar publicação, porque o cron publica sozinho no ciclo seguinte.
- O v2 entra como **competidor**, nunca promovido a oficial sem o walk-forward mostrar
  vantagem. É para isso que o harness existe.
- Gate novo só vale **validado com erro plantado** (ver `test_ingest_polls_gate.py`,
  `test_synths_gate.py` e `test_volume_gate.py` como referência).
- Pergunta com até ~4 opções vai por `AskUserQuestion`, clicável, UMA por vez.
- PT-BR sem travessão espaçado.
- Rebase sobre `origin/main` antes de qualquer push: o robô publica sozinho às 10:37 UTC.
