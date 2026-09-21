# Ficha do Jogo · Eleições 2026: modelagem probabilística e pontos de inflexão

**Versão 3, 21/09/2026.** Revisão completa sobre o repo atualizado (`origin/main` f77ffdd).
Substitui a v2 de 19/09, que rodava sobre a Wikipédia lida direto e sobre um `polls.json`
com o histórico presidencial quebrado.

Fonte dos dados agora: `data/live/polls.json` do próprio repo (schema v2, `as_of 2026-09-20`,
4.094 pesquisas, SQ do TSE já casado). Modelo v2: `modelo_eleitoral.py`, ambiente `eleicoes`
(numpyro/JAX). Tabelas e figuras listadas no §7.

---

## 0. O que mudou desde 19/09

### 0.1 No repo (18 commits, 18 a 21/09)

| frente | o que entrou |
|---|---|
| **Incidente da presidencial** | Causa raiz achada e corrigida (`6a1ea19`): a Wikipédia quebrou o 1º turno em subpáginas e o ingest não seguia hatnote; além disso o walker só lia `h2/h3/h4` e perdia o ano em bloco `{{hidden begin}}`. Foi exatamente o bug que apontei na v2, com um segundo defeito somado que eu não tinha visto. |
| **Alarme de volume** | `src/check_volume.py` + `src/test_volume_gate.py`: compara volume por (corrida, cenário) com o run anterior, reprova queda > 20% E ≥ 5 pesquisas, validado com o incidente real lido do histórico do git. É a terceira camada (entrada, saída, **existência**). |
| **Allowlist de subpáginas** | `ec0d57c`, fail-closed em fonte nova: seguir hatnote abriu uma porta, e a porta ficou com tranca. |
| **Harness fail-closed** | Modelo com `POLL_SOURCE` sintético só congela se houver pesquisa sintética; sem isso o leaderboard publicaria histórico de acerto de um competidor que nunca rodou. |
| **Achado de 21/09** | A Wikipédia desfez a quebra em subpáginas, mas deixou os blocos `hidden begin` de 2023-2025 dentro da seção `=== 2026 ===`: 173 pesquisas de 2025 estavam no ar datadas como 2026. |

Nada disso muda o método do agregador. Muda a **confiabilidade da entrada**, que é a metade
do problema que eu tinha tratado como resolvida.

### 0.2 Uma correção à v2, medida pelo próprio repo

Na v2 eu escrevi que o número publicado (Lula 67%) estava "14 pontos defasado" e que
re-rodar o pipeline resolveria. A primeira parte está certa; a atribuição, não. O D0 do
plano de incidente mediu: **recuperar as 483 pesquisas perdidas move Lula −0,3 p.p. de share
e 0,0 p.p. em P(eleito)**, porque as recuperadas valem 10,4% do peso do agregador (meia-vida
de 21 dias). A queda de 67% para 51,6% é **movimento real do eleitorado em três semanas**, não
efeito do bug. O bug estragou o gráfico e o walk-forward, não o número.

### 0.3 Nos números

| | v2 (19/09, Wikipédia, campo até 16/09) | v3 (21/09, repo, campo até 20/09) |
|---|---|---|
| 2T, Lula % do voto Lula+Flávio em 25/10 | 49,7 [44,7; 54,5] | 49,7 [44,4; 55,2] |
| P(Lula vence o 2T) | 45,4% | **45,8%** |
| 1T, Lula / Flávio / Cury (% válidos, 04/10) | 42,2 / 38,4 / 7,0 | **42,9 / 39,2 / 6,0** |
| P(haver 2º turno) | 99,7% | 99,2% |
| Inflexão de maio (2T) | +3,8 p.p., P > 0,99 | **+4,7 p.p., P = 0,998** |
| 27/ago (1T, Cury): salto no dia | +5,7 p.p.\* | **+3,0 p.p. (P = 0,63)** |
| 27/ago (1T, Cury): nível 20/ago → 05/set | — | **+5,9 p.p.** |
| Viés de casa extremos | Veritá −3,5 / Gerp −3,2 / CNT-MDA +3,4 | Gerp −3,1 / Veritá −3,0 / CNT-MDA +3,4 |

\* A v2 reportava só a variação de janela. As conclusões sobreviveram à troca de fonte (Wikipédia direta → pipeline do repo), ao
aumento da amostra (123 → 133 pesquisas de 2T) e a quatro dias de campo novo. Isso é o
teste de robustez que a v2 não tinha.

**O que é novo em setembro:** no 1º turno, Cury **devolve** 2,7 p.p. [−4,6; −1,0] entre
01/09 e 19/09 e Flávio ganha 2,4 p.p. [0,1; 4,9]. Sem salto detectado: é deriva, não evento.
A terceira via de agosto não se sustentou.

**Nota sobre as duas escalas.** Salto e variação de nível são medidas diferentes e o texto as
separa daqui em diante: o **salto** é a mudança estimada num único dia (`inflexoes_1turno.csv`);
a **variação de nível** é a diferença entre duas datas (`variacao_janela_1turno.csv`), que
soma o salto ao movimento dos dias vizinhos. Para Cury em agosto: +3,0 p.p. no dia 27,
+5,9 p.p. entre 20/ago e 05/set.

---

## 1. O site hoje

Rodei `src/eleicoes_model.py` numa cópia de leitura e **reproduzi bit a bit** o
`eleicoes2026_results.json` publicado. O site está atualizado e correto:

| Presidencial, modelo oficial v1 | 30/08 (o que a v2 viu no ar) | 20/09 (no ar hoje) |
|---|---|---|
| Lula, share 1T / P(eleito) | 43,8% / 67,1% | 42,5% / **51,6%** |
| Flávio, share 1T / P(eleito) | 37,0% / 32,9% | 39,0% / **48,4%** |
| Cury, share 1T | 3,1% | 7,1% |
| P(2º turno Lula × Flávio) | 98,9% | 99,6% |
| pesquisas usadas / institutos | 121 / 20 | 150 / 22 |

Uma observação de calibração: o v1 dá 51,6% para Lula e o v2 dá 45,8%. Os dois leem as
mesmas pesquisas. A diferença tem duas causas identificáveis, e nenhuma é erro:

1. **Tendência.** O v1 é uma média ponderada por recência: ele estima o nível médio das
   últimas ~3 semanas. O v2 é um passeio aleatório: ele estima o nível **de hoje** e o
   projeta. Com o nível caindo 2,4 p.p. desde 1º de julho, estimar "a média recente" e
   estimar "onde está agora" dão respostas diferentes.
2. **Erro no dia da eleição.** O v2 soma 2,5 p.p. de erro sistemático que não encolhe com
   mais pesquisas; o v1 usa `TIMEPP·√(dias/35)`, que hoje vale ~1,5 p.p. Banda maior com
   nível abaixo de 50 empurra a probabilidade para baixo.

Nenhum dos dois está "certo". A leitura defensável é **empate técnico**, e é por isso que o
§4 recomenda publicar share com banda como métrica principal.

---

## 2. Modelo v2: espaço de estados com viés de casa e saltos

O agregador v1 (média ponderada por recência × √n, house effect encolhido, desvio empírico)
confunde três coisas que a pergunta "o que mexeu a opinião?" exige separar:

| fonte de variação nas pesquisas | v1 | v2 |
|---|---|---|
| erro amostral (~1/√n) | implícito no peso √n | explícito, com efeito de desenho DEFF = 1,6 |
| viés de casa | desvio médio vs consenso, shrink 0,5 | parâmetro por instituto, soma zero, estimado junto |
| ruído não amostral | dentro da dispersão | `sigma_extra` próprio |
| movimento real | meia-vida de 21 dias | passeio aleatório latente diário, cauda pesada (t de Student, 4 g.l.) |
| erro sistemático no dia da eleição | `TIMEPP·√(dias/35)` | termo fixo de 2,5 p.p. que não diminui com mais pesquisas |

A cauda pesada nas inovações é o que transforma o agregador num **detector de inflexão**:
o modelo pode explicar um dia com um salto grande em vez de espalhar a mudança por semanas,
e a posteriori dá, para cada dia, P(|salto| > 0,5 p.p.) com intervalo de credibilidade.

### 2.1 Segundo turno Lula × Flávio (133 pesquisas, 19 institutos, jan–set/26)

Convergência limpa (R-hat 1,00–1,01). Desvio diário do passeio 0,0132 em logit
(≈ 0,33 p.p./dia); escala do viés de casa 0,070 (≈ 1,7 p.p.).

Viés de casa, na participação de Lula no voto Lula+Flávio (`house_effects_2turno.csv`):

| instituto | viés (p.p.) | IC 90% | n |
|---|---|---|---|
| Gerp | −3,1 | [−3,9; −2,3] | 12 |
| Veritá | −3,0 | [−3,9; −2,0] | 4 |
| Futura/Apex | −1,6 | [−2,4; −0,8] | 12 |
| Palver | −1,3 | [−2,3; −0,3] | 3 |
| PoderData | −0,6 | [−1,4; 0,2] | 9 |
| Nexus/BTG, Vox Brasil, Paraná, RealTimeBigData | entre 0,0 e +0,3 | incluem zero | 3–15 |
| AtlasIntel | +0,7 | [0,1; 1,3] | 17 |
| Datafolha | +0,7 | [−0,1; 1,5] | 10 |
| Quaest | +0,8 | [0,1; 1,6] | 12 |
| Meio/Ideia | +1,1 | [0,1; 2,0] | 9 |
| Indexa | +1,3 | [0,2; 2,3] | 5 |
| CNT/MDA | +3,4 | [2,1; 4,6] | 4 |

A amplitude entre os extremos é de 6,5 p.p.: uma semana em que saem Gerp e Veritá parece
"Flávio abriu"; uma em que sai CNT/MDA parece "Lula reagiu". Nenhuma das duas é movimento.

Nível latente de Lula (% do voto Lula+Flávio), mediana e IC 90%:

| data | nível | IC 90% |
|---|---|---|
| 15/jan | 51,6 | [50,2; 53,1] |
| 01/mai | 49,5 | [48,1; 50,9] |
| 25/mai | 52,0 | [50,9; 53,0] |
| 01/jul | 52,1 | [50,9; 53,3] |
| 15/ago | 51,1 | [50,0; 52,3] |
| 19/set | 49,7 | [48,4; 51,2] |

**Previsão** (`previsao_v2_resumo.json`), projetando a 25/10: Lula 49,7% [44,4; 55,2],
**P(Lula) = 45,8%**, P(Flávio) = 54,2%.

### 2.2 Primeiro turno (108 pesquisas com os 6 principais, mai–set/26)

Passeio aleatório multinomial no simplex (K−1 log-razões) com Dirichlet-multinomial para
superdispersão. α₀ estimado ≈ 216: **cada pesquisa vale, em informação, cerca de 216
entrevistas i.i.d., não as 2.000 da ficha técnica.** Esse número é o tamanho real do ruído
não amostral, e é a razão pela qual o desvio-padrão declarado pelos institutos subestima a
incerteza por um fator de ~3.

Previsão para 04/10 (`previsao_1turno_2026-10-04.csv`):

| candidato | % válidos | IC 90% | P(top-2) |
|---|---|---|---|
| Lula | 42,9 | [38,2; 47,5] | 1,00 |
| Flávio | 39,2 | [34,4; 44,1] | 1,00 |
| Cury | 6,0 | [1,7; 10,6] | 0,00 |
| Renan | 4,4 | [0,4; 8,2] | 0,00 |
| Caiado | 3,8 | [0,0; 7,5] | 0,00 |
| Zema | 1,7 | [0,0; 5,2] | 0,00 |

P(Lula vence no 1º turno) = 0,8%. P(haver 2º turno) = 99,2%.

### 2.3 Pontos de inflexão

**Três regimes distintos**, e a distinção é o achado metodológico mais útil para o site:

| período | tipo | magnitude | leitura |
|---|---|---|---|
| **5–21 mai** (pico 14–16/mai) | **salto** no 2T | +4,7 p.p. na janela de 10 dias, P = 0,998 | Único choque abrupto do ano na disputa direta. Lula sai de 49,5 para 52,0 e fica lá por dois meses. |
| **27 ago** | **salto** no 1T | no dia: Cury +3,0 p.p., Lula −1,3, Flávio −1,2, com P(salto) = 0,63 para Cury. Acumulado do nível entre 20/ago e 05/set: Cury +5,9 [4,9; 7,0]; Lula −2,9 [−4,7; −1,1]; Flávio −0,9 [−2,6; +1,2] | A terceira via emergiu pagando sobretudo pelo eleitor de Lula: no acumulado, o IC de Lula exclui zero e o de Flávio não. |
| **jul → set** | **erosão gradual** no 2T | −2,4 p.p. em 11 semanas, nenhum dia com P(salto) > 0,25 | Não é evento, é deriva. Combina com desidratação lenta, não com escândalo pontual. |
| **set (novo)** | **reversão gradual** no 1T | Cury −2,7 [−4,6; −1,0]; Flávio +2,4 [0,1; 4,9] | O salto de agosto se desfez sem um segundo salto. Voto de terceira via que não fixou. |

O detector continua **não** encontrando salto no 2T em fim de agosto: o movimento de Cury no
1T não se traduziu em movimento abrupto na disputa direta, e a reversão de setembro tampouco.

**O que o modelo não diz:** a causa. Ele data o salto e mede o tamanho. A atribuição é o
passo seguinte (§3).

### 2.4 Cuidado com P(eleito) num empate

Com o share 2T em 49,7 ± 2,7, P(vitória) é quase uma função-degrau: 1 p.p. de share move
~12 pontos de probabilidade. Matematicamente correto, comunicacionalmente perigoso. A página
deveria mostrar **share latente com banda** como métrica principal e P(eleito) como derivada;
e o `check_movimento.py` deveria usar share, não P(eleito), como gatilho na PRES. O próprio
incidente ilustra: recuperar 483 pesquisas moveu 0,0 p.p. em P(eleito) e o alarme ficaria
mudo de qualquer forma, enquanto três semanas de pesquisa nova moveram 15 pontos.

---

## 3. De "quando" para "por quê": desenho para identificar o que mexe o voto

Pesquisa de intenção de voto sozinha entrega a data e o tamanho do movimento. Para chegar ao
mecanismo (a peça de desinformação, o debate, a decisão do STF) é preciso um desenho de
atribuição. Quatro camadas, em ordem de custo:

### 3.1 Registro de eventos datado e pré-especificado

`data/eleicoes/eventos.json` com data, tipo (debate, decisão judicial, denúncia, peça viral,
evento econômico, pesquisa-bomba), alvo, fonte e `direcao_esperada` preenchida **antes** de
ver o efeito. A pré-especificação é o que separa análise de racionalização: com 50 eventos no
ano e um detector que acha 3 saltos, sempre haverá "um evento perto". A retrospectiva da Copa
(§5.4, "espaço de medição definido antes de medir") já tem essa disciplina.

Fontes para popular sem esforço manual: agências de checagem (Lupa, Aos Fatos) publicam
feeds datados por tema e alvo; o TSE publica decisões sobre propaganda irregular e
representações por desinformação; a agenda de debates é fixa.

### 3.2 Estudo de evento sobre o nível latente

Para cada evento *e*: efeito = μ(t_e + h) − μ(t_e − 1) para h = 3, 7, 14 dias, com IC vindo
direto das amostras posteriores. Uma janela placebo com datas sem evento dá a distribuição
nula. Só se declara efeito se o salto detectado coincide com o evento **e** o placebo não
reproduz a magnitude.

Aqui entra a distinção salto × erosão: desinformação viral, se funciona, deve produzir
**impulso com decaimento** (efeito no dia, meia-vida de 1–3 semanas), enquanto economia e
fadiga produzem **deriva**. Modelar o salto como impulso com decaimento exponencial (dois
parâmetros) e comparar com o passeio puro é um teste formal, não uma impressão. O caso de
Cury é o exemplo pronto: salto em 27/ago seguido de reversão gradual em setembro é
exatamente a assinatura de impulso que decai.

### 3.3 Heterogeneidade por segmento

Quaest, Datafolha e AtlasIntel publicam cortes por região, renda, escolaridade, religião,
gênero e idade. Um evento que move o agregado 2 p.p. mas move evangélicos 6 p.p. e católicos
0 conta uma história; um que move todos os cortes igualmente conta outra. É a camada com
melhor razão informação/custo, e o `numeros[]` do `polls.json` só precisa ganhar um campo
`segmento`. O v2 roda por segmento sem mudança (cada corte é uma série com n menor).

Ligação com a Fase C: os 5 públicos do painel de mídia são os candidatos naturais a segmentos
de acompanhamento. Se a pesquisa sintética serve para algo, é para gerar **hipóteses de
mecanismo por público** que depois se testam nos cortes reais, não para substituir pesquisa.

### 3.4 Séries exógenas como covariáveis do passeio

μ_t = μ_{t−1} + β·x_t + ε_t, com x_t = volume de checagens sobre o candidato, buscas por
termos-chave, menções em rádio e TV, índice de preços de alimentos. β com IC diz se aquela
série antecipa movimento. Aviso honesto: com uma eleição só, há poucos "experimentos"; β sai
largo. O valor está em descartar hipóteses, não em confirmá-las.

### 3.5 O que não fazer

- Atribuir causa a salto único sem placebo e sem pré-registro.
- Somar sintético com real.
- Tratar 46% vs 54% como diferença: é a mesma coisa dentro do erro.
- Datar evento pela pesquisa de divulgação mais recente: o ponto de referência é o **meio do
  campo**, e o efeito só entra nas pesquisas 3 a 7 dias depois.

---

## 4. O que o leaderboard já diz (e é um argumento)

Com 19 freezes e 824 comparações walk-forward, o `model_scores.json` mostra:

| modelo | MAE de share |
|---|---|
| baseline | 0,0357 |
| incerteza_alta | 0,0357 |
| recencia_longa | 0,0358 |
| recencia_curta | 0,0360 |
| sem_house | 0,0360 |

Cinco variantes, **0,3 milésimo de diferença entre a melhor e a pior**. O harness está
funcionando: ele mediu, e a medida diz que mexer em meia-vida, piso de incerteza e house
effect não muda nada relevante. Isso não é fracasso do harness, é informação: as variantes
são o mesmo modelo com parafusos diferentes. Para o leaderboard discriminar, o competidor
precisa ser **estruturalmente** diferente, e é isso que o Kalman com efeitos por instituto
oferece (§ handoff). Se ele também empatar, aprende-se que o teto do share de pesquisa a 14
dias é esse, o que também é resultado.

---

## 5. Limitações desta rodada

- Fonte única (Wikipédia, via pipeline do repo). Latência de 1 a 3 dias e depende de editores.
- Institutos com 1 a 3 pesquisas têm viés de casa mal identificado (IC largo); o modelo os
  encolhe para zero, que é o comportamento correto, mas significa que uma pesquisa nova de
  instituto desconhecido pesa quase tanto quanto uma de Datafolha. Um prior informativo por
  histórico 2018/2022 resolveria.
- O erro sistemático de 2,5 p.p. é chute calibrado no histórico brasileiro, não estimado. É o
  parâmetro mais importante do modelo e o único não estimado dos dados.
- O 1T usa só pesquisas de maio em diante (antes, Cury não era testado) e só os 6 principais.
- Previsão de 2T condicional ao par Lula × Flávio (P = 99,6% no v1).
- Não avaliei: a hipótese de passeio aleatório contra alternativas (reversão à média,
  tendência local linear), nem calibração fora da amostra do próprio v2.

## 6. Próximo passo

O documento `handoff_modelagem_claude_code.md` traduz tudo isto em trabalho executável no
repo, no formato dos planos de fase, com o esqueleto stdlib do competidor.

## 7. Arquivos

- `modelo_eleitoral.py`: módulo v2 (preparar / ajustar / detectar / prever, 1T e 2T)
- `pesquisas_1turno_2026.csv`, `pesquisas_2turno_lula_flavio.csv`: dados limpos do `polls.json`
- `serie_latente_2turno.csv`, `serie_latente_1turno.csv`: nível diário com IC e P(salto)
- `inflexoes_2turno_top.csv`, `inflexoes_1turno.csv` (salto diário), `variacao_janela_1turno.csv`
  (variação de nível entre datas), `house_effects_2turno.csv`,
  `previsao_1turno_2026-10-04.csv`, `previsao_v2_resumo.json`
- `eleicoes2026_results_reprocessado_2026-09-20.json`: saída do v1 reproduzida
- `fig_2turno_inflexoes.png`, `fig_1turno_trajetorias.png`
