# Hipóteses pré-especificadas das inflexões (Bola de Cristal, 25/09/2026)

> Relatório do agente `bola-de-cristal` sobre o dossiê de inflexões (as_of 24/09/2026), reproduzido na íntegra (entidades HTML desfeitas). O JSON aqui é a fonte de `data/eleicoes/hipoteses.json`, validado por `src/test_hipoteses.py`. Leitura da seção 2 é EXPLORATÓRIA; só o bloco 3 é pré-especificado. Esclarecimento sobre a seção 5: RUNOFF_CORR=0 nos params publicados está certo por desenho (chave desligada no oficial por decisão de 24/09; o competidor v3_runoff a usa). Achado fora de escopo registrado: o quadro publicado ainda lista Pablo Marçal, cuja substituição (Leonardo Avalanche, PRTB) a imprensa noticiou; o structure.json vem de captura de 29/08.

---

# Bola de Cristal · Hipóteses pré-especificadas para as próximas rodadas · registro de 2026-09-25

Insumos: `dossie_bdc.md` / `dossie_bdc.json` (as_of 2026-09-24); quadro publicado `data/eleicoes2026_results.json`; detector `data/eleicoes/inflexoes.json` e série `inflexoes_series.json`; pesquisas brutas `data/live/polls.json`; `calibracao_erro.json`; `eventos.json`; `docs/memo-modelagem-v3.md`; `docs/plano-fase-d-modelagem.md` (desenho do M3). Nada foi modificado no repositório.

Escala de probabilidade (palavras do contrato do dossiê, número central e faixa): quase certo (0,90; 0,85 a 0,95) · provável (0,70; 0,60 a 0,80) · chances iguais (0,50; 0,40 a 0,60) · improvável (0,25; 0,15 a 0,35) · quase impossível (0,07; até 0,10).

Convenções de leitura: "publicação de 25/09" = quadro com as_of 2026-09-24 (baseline de todas as hipóteses); "publicação de 04/10" = quadro com as_of 2026-10-03, ou a última publicação anterior à apuração. `share` é a fração publicada em `races[corrida].candidates[sq].share` (convertida em pontos percentuais); `eleito` é `candidates[sq].eleito`; "destaque corroborado" é registro de `inflexoes.json` com `corroborado = true` e `relevante = true` (o que a página Inflexões mostra).

## 1. Corte de conhecimento e fontes externas

- Corte de conhecimento do modelo: junho de 2026. Registro feito em 2026-09-25 sobre dado publicado com as_of 2026-09-24. Tudo o que é posterior a junho de 2026 vem do dado do site ou das fontes abaixo.
- Budget de web da sessão (2 WebSearch + 6 WebFetch) esgotado. Páginas abertas e usadas como fonte:
  1. Exame, "Debate para presidente nas eleições 2026: veja calendário, datas e regras", publicada em 09/08/2026, acesso em 25/09/2026, https://exame.com/brasil/debate-para-presidente-nas-eleicoes-2026-veja-calendario-datas-e-regras/ . Calendário do 1º turno: Band 23/08 (20h), Consórcio 14/09 (22h), Record 27/09 (21h), Globo 01/10 (após o Jornal Nacional); "quatro candidatos têm espaço garantido": Lula, Flávio Bolsonaro, Ronaldo Caiado e Augusto Cury; critério de convite: representação mínima no Congresso.
  2. Correio Braziliense, "Quando será o próximo debate presidencial da eleição 2026?", publicada em 23/09/2026, acesso em 25/09/2026, https://www.correiobraziliense.com.br/mundo/2026/09/7506724-quando-sera-o-proximo-debate-presidencial-da-eleicao-2026.html . Globo 01/10 é o único debate ainda confirmado; Record cancelou o de 27/09; Flávio "só participa de debates em que Lula estiver presente"; a campanha de Lula "avalia comparecer"; na Band (23/08) foram Caiado, Cury e Renan; o consórcio de 14/09 foi cancelado porque os dois líderes não iriam; o registro de Pablo Marçal foi rejeitado pelo TSE e o PRTB o substituiu por Leonardo Avalanche; 13 candidatos registrados.
  3. Gazeta do Povo, ficha da pesquisa Datafolha de setembro, publicada em 03/09/2026, acesso em 25/09/2026, https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/datafolha-presidente-setembro-2026/ . Metodologia: campo de 1 a 3/09, 2.002 entrevistas, margem de 2 pp, registro TSE BR-03669/2026, contratantes Folha e Globo. Estimulada com Marçal: Lula 39, Flávio 32, Cury 7, Renan 4, Caiado 4, Zema 2, Marçal 2, Samara 1, brancos/nulos 6, indecisos 3. Segundo turno: Lula 46 x Flávio 44.
- Tentadas e não obtidas: calendário eleitoral do TSE (https://www.tse.jus.br/eleicoes/eleicoes-2026/calendario-eleitoral , HTTP 403) e Lei 9.504/1997 no Planalto (https://www.planalto.gov.br/ccivil_03/leis/l9504.htm , duas falhas de conexão). Consequência: o período do horário eleitoral gratuito (art. 47: "35 dias anteriores à antevéspera", o que dá 28/08 a 01/10) fica como [fato legal não reconferido nesta sessão]; presença de Lula e de Flávio no debate da Globo: não confirmada em 25/09.
- Resultados de busca listados e NÃO abertos (não usados como fonte): Band, Terra, Jota, Ranking dos Políticos, Wikipédia EN.

## 2. Leitura curta dos choques comuns

1. [fato] Há 32 choques comuns; em 13 deles um único instituto responde por 50% ou mais dos disparos do dia. Em toda a série, os maiores disparadores de destaque corroborado são Veritá (19), AtlasIntel (16), Quaest (11), Real Time Big Data (8) e Palver (6). O bloco de 16 a 20/09, que contém os três maiores choques (8 a 9 candidatos), é Veritá + Palver + AtlasIntel: a Veritá publicou lotes de 7 e 8 corridas estaduais com campo terminando em 17/09 e 19/09.
2. [fato] A contagem de destaques corroborados acompanha a densidade do fluxo: 26 em agosto, 55 em setembro (até 24/09). A presidencial teve 4, 7, 6, 10, 16, 11 e 7 pesquisas estimuladas por semana ISO desde meados de agosto (semana 39 parcial).
3. [fato] Desde 15/08 os 79 destaques corroborados têm sinal assimétrico: candidatos que hoje têm share abaixo de 10% receberam 42 sinais negativos e 10 positivos; na faixa de 10 a 25%, 12 contra 11; acima de 25%, 2 contra 2. Por bloco, candidatos fora do PL e da esquerda ("outros") receberam 45 negativos e 15 positivos, e o sinal negativo em "outros" domina nos disparos de cinco casas de desenho diferente (Veritá, AtlasIntel, Palver, Quaest, Datafolha).
4. [inferência] Dois mecanismos coexistem. (i) Lote de instituto: uma casa publica muitas corridas no mesmo dia e o seu efeito-casa cruza a tolerância do passeio em logit calibrado perto de 50% (0,06 pp/dia para quem tem 5%), o que produz vários "saltos" simultâneos que são artefato de desenho, não movimento do país. (ii) Compressão nacional dos não polarizados: a assimetria de sinal não sai do detector (simétrico) nem de uma casa só; é compatível com o eleitor de terceira via e de centro migrando para os polos desde o início da campanha (16/08) e do horário eleitoral (28/08).
5. [inferência] Ressalva de sobrevivência: a faixa de share é medida hoje, então quem caiu tende a estar abaixo de 10% hoje. Para o trio da presidencial isso não é circular: Cury, Renan e Caiado começaram setembro acima do valor atual (nível latente 7,5 / 4,4 / 3,8 em 03/09 contra 5,4 / 3,8 / 3,4 em 24/09).
6. [fato] Efeito-casa aproximado na presidencial (desvio de cada pesquisa contra as demais casas em ±7 dias, desde 10/08, sem ponderação): Flávio mede +6,6 pp na Veritá, +5,3 na Palver, +3,5 na Gerp e +3,2 na AtlasIntel; −2,3 na Datafolha, −3,6 na Real Time Big Data e −5,2 na Quaest. Cury mede −3,8 na Palver e −1,4 na AtlasIntel; +1,5 a +2,2 em PoderData, Veritá e Real Time Big Data. As casas de indecisos baixos (AtlasIntel e Palver, 1 a 2%) inflam os dois líderes e deflacionam os pequenos quando o share é normalizado.
7. [hipótese] As próximas rodadas mostrarão as duas coisas ao mesmo tempo: artefatos de lote nos dias de Veritá, AtlasIntel e Palver (h-04, h-05) e persistência da compressão (h-01, h-06, h-07), com a enxurrada da última semana elevando a contagem de destaques independentemente de movimento real. Para o M3, isso obriga a sortear datas placebo pareadas por densidade de pesquisas, não datas uniformes.
8. [fato] Contexto externo até 23/09: o debate da Globo de 01/10 é o único que resta no 1º turno; a Record cancelou o de 27/09; Flávio condiciona presença à de Lula, que "avalia comparecer". Datafolha de 1 a 3/09: Lula 39, Flávio 32, Cury 7. [declaração de veículo, não confirmada no TSE] O registro de Marçal foi rejeitado e o PRTB o substituiu por Leonardo Avalanche; o quadro publicado do site ainda lista "PABLO MARÇAL" com 0,4%.

## 3. Bloco JSON (12 hipóteses)

Nota de esquema: h-05 e h-07 atravessam corridas e usam `"corrida": "MULTI"` com `origem.corridas` listando as corridas; se o julgador exigir corrida única, dividir o item por corrida mantendo o id com sufixo. Nas hipóteses de métrica `inflexao`, `limiar_pp` é 0 porque o critério é o do próprio detector (|z| > 3, corroborado por 2+ institutos, share ≥ 2%).

```json
[
  {
    "id": "h-2026-09-25-01",
    "registrado_em": "2026-09-25",
    "titulo": "Cury devolve mais 1 pp até a urna",
    "hipotese": "O share publicado de Augusto Cury na presidencial cai pelo menos 1,0 pp entre a publicação de 25/09 (as_of 24/09: 6,9%) e a publicação de 04/10 (as_of 03/10, ou a última antes da apuração), fechando em 5,9% ou menos.",
    "mecanismo": "[fato] O nível latente do detector já está em 5,4% (24/09) enquanto o agregado publicado (meia-vida de 21 dias) ainda carrega as pesquisas de fim de agosto com Cury em 8 a 10%; desde 05/09 os cinco destaques corroborados de Cury são negativos. [inferência] Conforme essas pesquisas decaem e a enxurrada final entra em 5 a 6% nas casas de referência (Datafolha 5, Quaest 6, PoderData 6, Futura 5,6) e em 2% nas de indecisos baixos, o agregado converge para baixo. [hipótese] O fim do horário eleitoral em 01/10 e o voto útil aceleram a devolução.",
    "origem": {"tipo": "choque_comum", "datas": ["2026-09-16", "2026-09-17", "2026-09-18", "2026-09-19"], "corridas": ["PRES", "GOV-MG", "SEN-DF", "SEN-GO", "SEN-RJ"]},
    "corrida": "PRES",
    "alvo": [280002551547],
    "direcao_esperada": "-",
    "metrica": "share",
    "janela": {"inicio": "2026-09-26", "fim": "2026-10-04"},
    "limiar_pp": 1.0,
    "falsificacao": "Falsa se races.PRES.candidates[sq=280002551547].share na publicação de 04/10 (as_of 03/10) for >= 6,0%.",
    "probabilidade": {"kent": "provável", "aprox": 0.75},
    "status": "aberta"
  },
  {
    "id": "h-2026-09-25-02",
    "registrado_em": "2026-09-25",
    "titulo": "Flávio sobe 1 pp no agregado até 04/10",
    "hipotese": "O share publicado de Flávio Bolsonaro sobe pelo menos 1,0 pp entre a publicação de 25/09 (39,6%) e a de 04/10, fechando em 40,6% ou mais.",
    "mecanismo": "[fato] Nas casas de referência a série de setembro é ascendente (Datafolha 32 para 36, Quaest 31 para 33, PoderData 36 para 39, Futura 33,6 para 40,4) e o nível latente foi de 37,4% em 03/09 a 41,8% em 24/09; o agregado publicado (39,6%) ainda pesa pesquisas de fim de agosto em que Flávio media 32 a 35. [inferência] Com share normalizado, a compressão dos pequenos (h-01) redistribui mecanicamente 1 a 2 pp para os dois líderes. [hipótese] A devolução de Cury fluiu mais para Flávio do que para Lula em setembro (memo v3: Flávio +2,4 pp [0,1; 4,9] entre 01/09 e 19/09) e continua. Risco declarado: a última semana é mais pesada em Datafolha e Quaest, casas em que Flávio mede 2 a 5 pp abaixo das demais.",
    "origem": {"tipo": "destaque", "datas": ["2026-09-12", "2026-09-22"], "corridas": ["PRES"]},
    "corrida": "PRES",
    "alvo": [280002551544],
    "direcao_esperada": "+",
    "metrica": "share",
    "janela": {"inicio": "2026-09-26", "fim": "2026-10-04"},
    "limiar_pp": 1.0,
    "falsificacao": "Falsa se races.PRES.candidates[sq=280002551544].share na publicação de 04/10 for <= 40,5%.",
    "probabilidade": {"kent": "provável", "aprox": 0.60},
    "status": "aberta"
  },
  {
    "id": "h-2026-09-25-03",
    "registrado_em": "2026-09-25",
    "titulo": "P(eleito) de Flávio segue subindo no 2º turno",
    "hipotese": "A P(eleito) publicada de Flávio Bolsonaro sobe pelo menos 2,0 pontos entre a publicação de 25/09 (51,3%) e a de 04/10, fechando em 53,3% ou mais.",
    "mecanismo": "[fato] Nas pesquisas de 2º turno Lula x Flávio desde 07/09 a margem média é de cerca de 1 pp para Flávio (Datafolha é a principal exceção: +2 para Lula em 11, 16 e 24/09); o memo v3 descreve erosão gradual de Lula no 2º turno desde julho (−2,4 pp em 11 semanas, sem salto). [inferência] Perto de 50%, 2 pontos de P(eleito) correspondem a um deslocamento pequeno da margem ponderada (da ordem de 0,3 pp), então o teste é se a deriva continua, não se ela é grande. [hipótese] A deriva continua até o 1º turno.",
    "origem": {"tipo": "destaque", "datas": ["2026-09-22"], "corridas": ["PRES"]},
    "corrida": "PRES",
    "alvo": [280002551544],
    "direcao_esperada": "+",
    "metrica": "eleito",
    "janela": {"inicio": "2026-09-26", "fim": "2026-10-04"},
    "limiar_pp": 2.0,
    "falsificacao": "Falsa se races.PRES.candidates[sq=280002551544].eleito na publicação de 04/10 for <= 0,532. Leitura simétrica registrada: valor <= 0,493 indica reversão da deriva, não só ausência de continuidade.",
    "probabilidade": {"kent": "chances iguais", "aprox": 0.50},
    "status": "aberta"
  },
  {
    "id": "h-2026-09-25-04",
    "registrado_em": "2026-09-25",
    "titulo": "A próxima AtlasIntel derruba os nanicos no detector",
    "hipotese": "A primeira pesquisa presidencial da AtlasIntel com campo terminando entre 26/09 e 03/10 (cadência semanal recente: 30/08, 09/09, 16/09, 22/09) gera destaque corroborado com sinal negativo, datado no campo_fim, para pelo menos dois entre Cury, Renan Santos e Caiado.",
    "mecanismo": "[fato] A AtlasIntel publica 1 a 2% de indecisos com cerca de 5 mil entrevistas, o que normaliza os líderes em 43 a 46% e os pequenos em 1 a 4% (Cury 2,1 e Caiado 1,3 em 22/09), 1,4 a 3,8 pp abaixo das demais casas; desde 15/08 os seus disparos na presidencial foram 8 negativos em pequenos e 1 positivo (Flávio). [fato] Para quem tem 3 a 5% o passeio tolera 0,06 pp/dia, então um desvio de casa de 2 pp vale |z| de 4 a 6. [inferência] A corroboração virá de Palver ou Veritá (mesmo desenho de indecisos baixos) em até 7 dias, o que não é evidência independente de movimento.",
    "origem": {"tipo": "choque_comum", "datas": ["2026-09-18", "2026-09-19", "2026-09-22"], "corridas": ["PRES"]},
    "corrida": "PRES",
    "alvo": [280002551547, 280002540694, 280002551932],
    "direcao_esperada": "-",
    "metrica": "inflexao",
    "janela": {"inicio": "2026-09-26", "fim": "2026-10-04"},
    "limiar_pp": 0.0,
    "falsificacao": "Falsa se, para a data de campo_fim dessa pesquisa AtlasIntel, inflexoes.json (até a publicação de 04/10) trouxer menos de dois registros com corrida PRES, sq no trio, z < 0, corroborado = true e relevante = true. Não testável se não houver pesquisa AtlasIntel na janela.",
    "probabilidade": {"kent": "quase certo", "aprox": 0.85},
    "status": "aberta"
  },
  {
    "id": "h-2026-09-25-05",
    "registrado_em": "2026-09-25",
    "titulo": "Lote da Veritá vira choque comum, com sinal negativo em 'outros'",
    "hipotese": "Cada lote estadual da Veritá (3 ou mais corridas com o mesmo campo_fim) com campo terminando entre 26/09 e 01/10 produz, no dia ±1, um choque comum de pelo menos 3 destaques corroborados em 2 ou mais corridas, com a Veritá como instituto disparador em pelo menos metade deles e maioria de sinal negativo entre candidatos fora do PL e da esquerda. Sentinelas (critério secundário): pelo menos 3 dos 9 candidatos do choque de 18/09 são marcados de novo com o mesmo sinal.",
    "mecanismo": "[fato] A Veritá publicou lotes de 6 a 8 corridas em 09, 10, 12, 17 e 19/09 e é a maior disparadora de destaques corroborados (19); nos choques de 16 a 20/09 respondeu por 50 a 62% dos disparos; desde 15/08 os seus destaques corroborados em candidatos 'outros' foram 10 negativos e 2 positivos. [inferência] O efeito-casa aplicado a dezenas de candidatos de uma vez cruza o limiar em vários ao mesmo tempo, e a corroboração vem de casas com viés parecido. [hipótese] Sem mudança no desenho da Veritá, o padrão se repete na última semana.",
    "origem": {"tipo": "choque_comum", "datas": ["2026-09-16", "2026-09-17", "2026-09-18", "2026-09-19", "2026-09-20"], "corridas": ["GOV-MG", "SEN-GO", "SEN-RJ", "PRES", "SEN-DF"]},
    "corrida": "MULTI",
    "alvo": [130002539775, 130002541911, 130002549557, 280002540694, 280002551547, 280002551932, 70002548624, 90002546974, 190002542888],
    "direcao_esperada": "-",
    "metrica": "inflexao",
    "janela": {"inicio": "2026-09-26", "fim": "2026-10-01"},
    "limiar_pp": 0.0,
    "falsificacao": "Falsa se algum lote da Veritá na janela (polls.json: instituto Veritá, >= 3 corridas estaduais com o mesmo campo_fim) não tiver em inflexoes.json >= 3 destaques corroborados datados no campo_fim ±1 em >= 2 corridas, ou se a Veritá constar em 'institutos' em menos da metade deles, ou se os sinais entre candidatos 'outros' não forem majoritariamente negativos. Não testável se não houver lote na janela.",
    "probabilidade": {"kent": "provável", "aprox": 0.70},
    "status": "aberta"
  },
  {
    "id": "h-2026-09-25-06",
    "registrado_em": "2026-09-25",
    "titulo": "Kalil perde mais 1 pp em MG",
    "hipotese": "O share publicado de Alexandre Kalil (GOV-MG) cai pelo menos 1,0 pp entre a publicação de 25/09 (11,2%) e a de 04/10, fechando em 10,2% ou menos.",
    "mecanismo": "[fato] O nível latente de Kalil caiu de 13,6% (03/09) para 11,6% (24/09), com destaques negativos corroborados em 17/09 (Veritá, corroborado por AtlasIntel) e 20/09 (AtlasIntel, corroborado por Veritá); Cleitinho tem 46,0% e Patrus 22,7%, com 19,3% de indecisos. [inferência] É o mesmo mecanismo da compressão nacional: corrida polarizada (Republicanos x PT) espreme o terceiro quando o indeciso decide. [hipótese] A queda de 0,67 pp/semana persiste até a urna. Checagem secundária de mecanismo: a perda de Kalil aparece em Patrus (voto útil ao 2º) ou em Cleitinho (manada ao 1º).",
    "origem": {"tipo": "choque_comum", "datas": ["2026-09-17", "2026-09-18", "2026-09-19", "2026-09-20"], "corridas": ["GOV-MG", "PRES", "SEN-DF", "SEN-GO", "SEN-RJ"]},
    "corrida": "GOV-MG",
    "alvo": [130002539775],
    "direcao_esperada": "-",
    "metrica": "share",
    "janela": {"inicio": "2026-09-26", "fim": "2026-10-04"},
    "limiar_pp": 1.0,
    "falsificacao": "Falsa se races.GOV-MG.candidates[sq=130002539775].share na publicação de 04/10 for >= 10,3%.",
    "probabilidade": {"kent": "chances iguais", "aprox": 0.50},
    "status": "aberta"
  },
  {
    "id": "h-2026-09-25-07",
    "registrado_em": "2026-09-25",
    "titulo": "O choque de 17 a 19/09 persiste nos sete que caíram",
    "hipotese": "Dos sete candidatos marcados com sinal negativo no choque comum de 17 a 19/09 (Kalil, Mateus Simões e Gabriel em GOV-MG; Renan Santos, Cury e Caiado na presidencial; Sebastião Coelho em SEN-DF), pelo menos cinco terão share publicado em 04/10 menor do que em 25/09 por 0,2 pp ou mais.",
    "mecanismo": "[fato] Sob a nula de que o choque foi artefato de lote, a direção não persiste no agregado publicado (média entre casas, que não depende da Veritá), e a chance de 5 em 7 caírem por acaso é de cerca de 23%. [inferência] Se a compressão nacional é real, a direção persiste. [hipótese] Persistência parcial: forte no trio presidencial e em Kalil, fraca em Simões, Gabriel e Coelho, cujo nível latente hoje está acima do share publicado (9,3 contra 8,0; 4,4 contra 3,4; 5,8 contra 4,8).",
    "origem": {"tipo": "choque_comum", "datas": ["2026-09-17", "2026-09-18", "2026-09-19"], "corridas": ["GOV-MG", "PRES", "SEN-DF"]},
    "corrida": "MULTI",
    "alvo": [130002539775, 130002541911, 130002549557, 280002540694, 280002551547, 280002551932, 70002548624],
    "direcao_esperada": "-",
    "metrica": "share",
    "janela": {"inicio": "2026-09-26", "fim": "2026-10-04"},
    "limiar_pp": 0.2,
    "falsificacao": "Falsa se, na publicação de 04/10, menos de cinco dos sete tiverem share <= (share de 25/09 − 0,2 pp); baselines de 25/09 na ordem do alvo: 11,2 / 8,0 / 3,4 / 4,7 / 6,9 / 3,5 / 4,8. Registrar também o nível latente (inflexoes_series.json) como leitura secundária.",
    "probabilidade": {"kent": "chances iguais", "aprox": 0.45},
    "status": "aberta"
  },
  {
    "id": "h-2026-09-25-08",
    "registrado_em": "2026-09-25",
    "titulo": "Calil sobe 1 pp com a chapa de Vilela em GO",
    "hipotese": "O share publicado de Dr. Zacharias Calil (SEN-GO) sobe pelo menos 1,0 pp entre a publicação de 25/09 (16,9%) e a de 04/10, fechando em 17,9% ou mais.",
    "mecanismo": "[fato] O nível latente de Calil subiu de 15,1% (03/09) para 17,6% (24/09), com destaques positivos corroborados em 15/09 (Goiás Pesquisas), 17/09 (Veritá) e 19/09 (DataPop), três casas diferentes; Daniel Vilela (MDB) lidera GOV-GO com 46,6% e P(eleito) de 100%; SEN-GO tem 27,6% de indecisos e 2 vagas. [hipótese] Efeito de chapa: o indeciso que decide pelo governador leva junto o senador do mesmo partido, e o segundo nome da aliança ganha do terceiro. A composição das alianças em Goiás não foi confirmada nesta sessão.",
    "origem": {"tipo": "choque_comum", "datas": ["2026-09-15", "2026-09-17", "2026-09-19"], "corridas": ["SEN-GO", "PRES", "GOV-MG", "SEN-RJ", "SEN-DF"]},
    "corrida": "SEN-GO",
    "alvo": [90002546974],
    "direcao_esperada": "+",
    "metrica": "share",
    "janela": {"inicio": "2026-09-26", "fim": "2026-10-04"},
    "limiar_pp": 1.0,
    "falsificacao": "Falsa se races.SEN-GO.candidates[sq=90002546974].share na publicação de 04/10 for <= 17,8%. Leitura secundária: P(eleito) >= 25% (hoje 20,1%).",
    "probabilidade": {"kent": "chances iguais", "aprox": 0.55},
    "status": "aberta"
  },
  {
    "id": "h-2026-09-25-09",
    "registrado_em": "2026-09-25",
    "titulo": "Jordy fecha o 1º turno como favorito à 2ª vaga no RJ",
    "hipotese": "A P(eleito) publicada de Carlos Jordy (SEN-RJ) sobe pelo menos 5,0 pontos entre a publicação de 25/09 (45,0%) e a de 04/10, fechando em 50,0% ou mais.",
    "mecanismo": "[fato] O nível latente de Jordy subiu de 15,8% (03/09) para 17,9% (24/09), com destaques positivos corroborados em 12/09 e 18/09 (Veritá e Real Time Big Data); Portinho (PL) tem 16,1% e foi marcado com +7,8 pela Veritá em 18/09 sem corroboração; Benedita (PT) tem a 1ª vaga com 94,9%. [hipótese] A subida de Flávio no estado de origem do PL levanta os dois candidatos do partido, e a 2ª vaga vira disputa interna decidida por voto útil bolsonarista para quem aparece à frente (Jordy). [fato] Corrida com 17 pesquisas usáveis e sd de 7,7 pp: uma Datafolha ou Quaest sozinha move a P(eleito) vários pontos.",
    "origem": {"tipo": "choque_comum", "datas": ["2026-09-17", "2026-09-18", "2026-09-19"], "corridas": ["SEN-RJ", "PRES", "GOV-MG", "SEN-GO", "SEN-DF"]},
    "corrida": "SEN-RJ",
    "alvo": [190002542888],
    "direcao_esperada": "+",
    "metrica": "eleito",
    "janela": {"inicio": "2026-09-26", "fim": "2026-10-04"},
    "limiar_pp": 5.0,
    "falsificacao": "Falsa se races.SEN-RJ.candidates[sq=190002542888].eleito na publicação de 04/10 for <= 0,499.",
    "probabilidade": {"kent": "chances iguais", "aprox": 0.45},
    "status": "aberta"
  },
  {
    "id": "h-2026-09-25-10",
    "registrado_em": "2026-09-25",
    "titulo": "Debate da Globo não rende inflexão positiva a Cury",
    "hipotese": "Se o debate da Globo de 01/10 ocorrer com Lula e Flávio no palco, Cury não recebe destaque corroborado positivo datado em 02/10 ou 03/10, e o seu share publicado em 04/10 é menor ou igual ao da publicação de 02/10. Direção pré-especificada para Cury: negativa. Se o debate não ocorrer ou um dos dois líderes faltar, a hipótese resolve em 'não testável' (condição registrada antes do fato).",
    "mecanismo": "[fato] É o único debate restante do 1º turno (Correio Braziliense, 23/09); no debate da Band de 23/08 só Caiado, Cury e Renan compareceram, e os destaques positivos de Cury estão datados em 26 e 27/08 (datas apenas; nenhuma atribuição de causa aqui). [hipótese] Com os dois líderes no palco e a cobertura concentrada neles, o pequeno perde a exposição relativa que teve na Band, e o eleitor de terceira via que ainda não decidiu tende a escolher um polo. [fato] Presença de Lula e de Flávio não confirmada em 25/09.",
    "origem": {"tipo": "destaque", "datas": ["2026-08-26", "2026-08-27"], "corridas": ["PRES"]},
    "corrida": "PRES",
    "alvo": [280002551547],
    "direcao_esperada": "-",
    "metrica": "inflexao",
    "janela": {"inicio": "2026-10-01", "fim": "2026-10-04"},
    "limiar_pp": 0.0,
    "falsificacao": "Falsa se inflexoes.json trouxer registro com corrida PRES, sq 280002551547, data 2026-10-02 ou 2026-10-03, z > 0, corroborado = true e relevante = true; ou se o share publicado de Cury em 04/10 for maior que o da publicação de 02/10. Sugestão para eventos.json (fora deste registro): id debate-globo-2026-10-01, tipo debate, alvo Cury, Renan e Caiado, direção negativa, escopo nacional, registrado antes do fato.",
    "probabilidade": {"kent": "provável", "aprox": 0.70},
    "status": "aberta"
  },
  {
    "id": "h-2026-09-25-11",
    "registrado_em": "2026-09-25",
    "titulo": "A urna dá a Flávio mais do que o agregado final",
    "hipotese": "O share oficial de Flávio Bolsonaro no 1º turno (votos válidos, TSE) supera o share publicado na última publicação antes da apuração (as_of 03/10) em pelo menos 1,5 pp.",
    "mecanismo": "[fato] Na calibração do próprio projeto (calibracao_erro.json: janela de 7 dias, share normalizado entre os top-4), o agregado subestimou o candidato do bloco de direita em 3,49 pp (2018) e 3,17 pp (2022) no 1º turno e superestimou o centro (+2,59 pp em média); n = 4 rodadas, universo e não amostra. [inferência] O agregado de 2026 fica entre dois clusters de casas (AtlasIntel, Veritá e Palver com Flávio 3 a 7 pp acima; Datafolha e Quaest 2 a 5 pp abaixo), e o padrão histórico diz que a urna ficou do lado de cima. [hipótese] O padrão de 2018 e 2022 se repete.",
    "origem": {"tipo": "destaque", "datas": ["2026-09-12", "2026-09-22"], "corridas": ["PRES"]},
    "corrida": "PRES",
    "alvo": [280002551544],
    "direcao_esperada": "+",
    "metrica": "share",
    "janela": {"inicio": "2026-10-03", "fim": "2026-10-04"},
    "limiar_pp": 1.5,
    "falsificacao": "Falsa se (share oficial de Flávio em votos válidos) − (share publicado com as_of 03/10) < 1,5 pp; medido pelo harness (Brier/MAE contra o resultado oficial no fim) e pela página de resultados após a apuração.",
    "probabilidade": {"kent": "provável", "aprox": 0.65},
    "status": "aberta"
  },
  {
    "id": "h-2026-09-25-12",
    "registrado_em": "2026-09-25",
    "titulo": "A urna dá a Cury menos do que o agregado final",
    "hipotese": "O share oficial de Augusto Cury no 1º turno (votos válidos, TSE) fica pelo menos 1,0 pp abaixo do share publicado na última publicação antes da apuração (as_of 03/10).",
    "mecanismo": "[fato] Em 2018 e 2022 o agregado superestimou o terceiro e o quarto colocados nos três casos medidos (Alckmin +3,99; Ciro +2,90; Tebet +1,19). [inferência] O voto útil dos últimos dois dias acontece depois do campo das últimas pesquisas e não entra em agregado nenhum. [hipótese] Repete-se em 2026 com Cury, que já vem devolvendo o pico de agosto.",
    "origem": {"tipo": "destaque", "datas": ["2026-09-16", "2026-09-18", "2026-09-19"], "corridas": ["PRES"]},
    "corrida": "PRES",
    "alvo": [280002551547],
    "direcao_esperada": "-",
    "metrica": "share",
    "janela": {"inicio": "2026-10-03", "fim": "2026-10-04"},
    "limiar_pp": 1.0,
    "falsificacao": "Falsa se (share publicado com as_of 03/10) − (share oficial de Cury em votos válidos) < 1,0 pp.",
    "probabilidade": {"kent": "provável", "aprox": 0.70},
    "status": "aberta"
  }
]
```

## 4. Justificativa por hipótese

- **h-01 (Cury −1,0 pp; provável, 0,75).** Taxa-base: pico de terceira via que não fixa costuma devolver, e o memo v3 já mediu −2,7 pp entre 01/09 e 19/09. Driver mecânico: o agregado publicado está 1,5 pp acima do nível latente, e só a decadência das pesquisas de agosto fecha parte da diferença. Sinal: cinco destaques negativos corroborados entre 16 e 23/09 (AtlasIntel, Palver, Veritá), com Datafolha e Quaest em 5 a 6%. Não é "quase certo" porque uma Datafolha final com Cury em 7 segura o agregado.
- **h-02 (Flávio +1,0 pp; provável, 0,60).** Drivers: tendência ascendente em quatro casas de referência, redistribuição mecânica da compressão dos pequenos e decadência das pesquisas de agosto em que ele media 32 a 35. Freio: o mix da última semana é mais pesado em Datafolha e Quaest, onde ele mede menos, e não sei quanto o HOUSE = 1 do motor compensa. Fica na borda inferior de "provável".
- **h-03 (P(eleito) de Flávio +2 pontos; chances iguais, 0,50).** A deriva do 2º turno é o dado mais estável do memo v3 (11 semanas sem salto) e as pesquisas de 2º turno desde 07/09 dão margem média de cerca de 1 pp para Flávio. Mas o limiar equivale a um deslocamento de margem menor que o ruído de mix entre casas, e a Datafolha (+2 Lula) entra pelo menos duas vezes na última semana. É a aposta mais próxima de uma moeda, registrada por ser o número-manchete do site.
- **h-04 (AtlasIntel derruba os nanicos; quase certo, 0,85).** É a hipótese mais segura porque testa o detector, não o eleitor: um desvio de casa de 2 pp num candidato de 3% vale |z| de 4 a 6 sob o SIGMA_RW calibrado a 50%. A cadência semanal da AtlasIntel torna quase certa uma pesquisa na janela, e Palver e Veritá, de mesmo desenho, corroboram em até 7 dias. O resíduo é a AtlasIntel mudar o tratamento de indecisos ou não publicar.
- **h-05 (lote da Veritá vira choque comum; provável, 0,70).** O padrão se repetiu em cinco lotes de setembro e a Veritá é a maior disparadora da série. A incerteza é de calendário (se haverá lote com campo até 01/10, deixando tempo para corroboração) e de sinal (10 a 2 negativos em "outros" desde 15/08, mas num lote pequeno a maioria pode empatar).
- **h-06 (Kalil −1,0 pp; chances iguais, 0,50).** Momentum de −0,67 pp/semana no nível latente e mecanismo plausível (polarização Cleitinho x Patrus com 19% de indecisos). Contra: o share publicado (11,2) já está abaixo do nível (11,6), então a decadência das pesquisas antigas não ajuda, e o −1,0 exige que a tendência continue inteira nos nove dias.
- **h-07 (persistência do choque de 17 a 19/09; chances iguais, 0,45).** É o teste direto de "mecanismo nacional contra artefato de lote", com nula explícita (23% sob acaso). Pesa contra: três dos sete têm nível latente acima do share publicado, o que empurra o agregado para cima. O valor está no registro da nula, não na aposta.
- **h-08 (Calil +1,0 pp; chances iguais, 0,55).** Três casas diferentes em cinco dias marcaram Calil para cima, e o nível está 0,7 pp acima do publicado (a decadência ajuda). Contra: a dobradinha é hipótese não confirmada e a Quaest de 23/09 marcou outros candidatos da corrida, não Calil.
- **h-09 (Jordy P(eleito) ≥ 50%; chances iguais, 0,45).** Momentum corroborado (+2,1 pp de nível em três semanas) e mecanismo de arrasto do PL no Rio. Contra: 17 pesquisas usáveis, sd de 7,7 pp, Portinho subindo na mesma casa e uma P(eleito) de 2 vagas que uma pesquisa só desloca.
- **h-10 (Globo não rende inflexão positiva a Cury; provável, 0,70).** É registro de direção antes do evento, que é o que o M3 pede; a condição (presença dos dois líderes) é observável e resolve em "não testável" se falhar. Taxa-base: debates brasileiros movem pouco os líderes, e a exposição dos pequenos depende de os grandes faltarem, como na Band.
- **h-11 (urna dá a Flávio +1,5 pp sobre o agregado; provável, 0,65).** Dois de dois ciclos com viés de 3 pp ou mais contra o candidato de direita no 1º turno, medidos pelo mesmo método que o site usa. Contra: n = 2, elenco diferente (Flávio não é Jair Bolsonaro) e institutos que ajustaram métodos depois de 2022.
- **h-12 (urna dá a Cury −1,0 pp sobre o agregado; provável, 0,70).** Três de três terceiros e quartos colocados superestimados, mecanismo temporal claro (voto útil depois do campo) e Cury já em devolução. Contra: se a devolução completar antes de 03/10, a diferença até a urna pode ficar abaixo de 1 pp.

## 5. O que NÃO dá para afirmar com este material

- **Magnitude dos saltos passados.** O detector mede em logit com SIGMA_RW calibrado perto de 50%, então subestima por construção o tamanho dos saltos dos pequenos (0,06 pp/dia a 5%): o "movimento de nível −0,11 pp" de Renan em 3 dias não é a magnitude real de nada. Confie na DATA (26 e 27/08 de Cury conferem entre institutos), desconfie da magnitude. Por isso as hipóteses usam o share publicado e a P(eleito) como métrica, não o delta do detector.
- **Causa dos choques.** Nada aqui atribui salto a evento. A assimetria de sinal é compatível com compressão nacional, mas também com uma mudança de desenho comum a várias casas (por exemplo, todas passando a estimular o cenário de 13 nomes depois do registro). Distinguir exige o placebo do M3 pareado por densidade de pesquisas.
- **Lula.** Não há destaque corroborado para Lula em toda a série (os 4 registros dele são de instituto único) nem série de nível na página de inflexões, então não há base para hipótese direcional sobre Lula além do que h-02 implica pela normalização.
- **Efeito-casa.** Os desvios que calculei são aproximações (contra pares em ±7 dias, sem ponderação, desde 10/08) e não sei o quanto o HOUSE = 1 do motor os remove. Se remover bem, h-02 fica mais forte; h-04 e h-05 seguem valendo porque o detector opera na outra ponta.
- **Corridas com dado ralo.** GOV-PB (4 pesquisas em setembro, última em 21/09) e SEN-RN (última em 17/09) não recebem hipótese porque podem não ter rodada nova antes de 04/10; SEN-RJ recebe uma com a ressalva do sd de 7,7 pp.
- **Sobrevivência nas faixas de share.** A faixa é medida hoje; a inferência de compressão vale com segurança para o trio presidencial (que começou setembro acima), não para toda a lista.
- **Calibração histórica.** n = 4 rodadas (8 erros de 1º turno); Alckmin e Tebet como "centro" é decisão de código; a taxa-base de h-11 e h-12 é sugestiva, não estatística.
- **2º turno.** O RUNOFF_CORR nos params publicados aparece como 0, enquanto runoff_corr.json diz "usar: true, beta 0,30" para PRES; não verifiquei qual vale no motor, e isso muda como a P(eleito) reage a movimento no 1º turno.
- **Fatos externos.** Presença de Lula e de Flávio na Globo, a substituição Marçal/Avalanche no dado do site (o quadro ainda lista Marçal com 0,4%) e o texto do art. 47 não foram confirmados nesta sessão; debates e Datafolha vieram de veículos de imprensa, não de fonte primária.
- **Proveniência.** Nada aqui é sintético e nada desta lista deve virar [FATO] antes de a rodada correspondente ser publicada e o M3 julgar com placebo; até lá cada linha é [hipótese] com data de registro, e a Escala Sherman Kent aplica-se à hipótese, não ao detector.
