# Dossiê para o Bola de Cristal · inflexões da campanha 2026

Gerado em 2026-09-25 a partir de dado PUBLICADO (as_of 2026-09-24). Fonte: agregador de pesquisas do Ficha do Jogo (site bera.ia.br/ficha-do-jogo), detector de inflexão M2 (resíduo padronizado do filtro de Kalman do competidor v2_estado; |z|>3, corroborado por 2+ institutos, share>=2%).

## CONTRATO DE SAÍDA (leia antes de tudo)

Você NÃO vai explicar os saltos passados. Coincidir com evento não é causa, e explicação retroativa é racionalização (o registro de eventos do projeto proíbe isso por desenho). O que se pede são HIPÓTESES PRÉ-ESPECIFICADAS e FALSIFICÁVEIS sobre as PRÓXIMAS rodadas (26/09 até o 1º turno em 04/10/2026, ou a janela do 2º turno até 25/10), registradas hoje, para que as rodadas seguintes as testem e o estudo de evento (com placebo, depois da apuração) julgue.

Regras:
1. Cada hipótese nomeia corrida, alvo (sq do candidato, da lista abaixo), direção esperada (+ ou -), métrica (share, P(eleito) ou "inflexão detectada"), janela (datas) e um critério de falsificação MENSURÁVEL no dado do site (ex.: "share de X cai >=1,0pp entre 26/09 e 04/10 no agregado publicado").
2. Mecanismo em 1 a 3 frases, marcado [fato] / [inferência] / [hipótese]. Se não tiver como confirmar algo, escreva "não confirmado" em vez de supor.
3. Probabilidade em palavra da Escala de Sherman Kent (quase certo, provável, chances iguais, improvável, quase impossível) e um número aproximado.
4. Entre 6 e 12 hipóteses. Prefira as que saem dos CHOQUES COMUNS (vários candidatos, corridas diferentes, mesmo dia): são as que sugerem mecanismo nacional, não ruído local.
5. Português do Brasil, SEM travessão espaçado (" — "): use vírgula, dois-pontos ou parênteses.
6. Declare seu corte de conhecimento e cite fonte com URL e data para qualquer fato externo que use.

Formato de saída: um bloco JSON (array) com este esquema EXATO por item, seguido de uma justificativa curta por hipótese:
{"id":"h-2026-09-25-NN","registrado_em":"2026-09-25","titulo":"...","hipotese":"...","mecanismo":"...","origem":{"tipo":"choque_comum|destaque","datas":["2026-09-18"],"corridas":["PRES"]},"corrida":"PRES","alvo":[280002542548],"direcao_esperada":"+","metrica":"share|eleito|inflexao","janela":{"inicio":"2026-09-26","fim":"2026-10-04"},"limiar_pp":1.0,"falsificacao":"...","probabilidade":{"kent":"provável","aprox":0.65},"status":"aberta"}

## Calendário
- 1º turno: 2026-10-04 · 2º turno: 2026-10-25 · o site atualiza todo dia (cron).
- Registro de eventos hoje: 1 evento(s), 0 pré-especificado(s): cury-viral-2026-08-26 (2026-08-26, denuncia, direção +, EXPLORATÓRIO)

## Choques comuns (dias ±1 com 3+ candidatos em destaque, corridas diferentes) · 32 no total

### 2026-09-18 · 9 candidatos · corridas {'SEN-DF': 1, 'GOV-MG': 3, 'SEN-RJ': 1, 'PRES': 3, 'SEN-GO': 1}
- GOV-MG · ALEXANDRE KALIL (PDT, sq 130002539775) · movimento de nível -0.42pp em 3 dias (z -3.1, 2 institutos) · hoje: share 11.2% (sd 3.3) · P(eleito) 0.0%
- GOV-MG · MATEUS SIMÕES (PSD, sq 130002541911) · movimento de nível -0.12pp em 3 dias (z -5.6, 2 institutos) · hoje: share 8.0% (sd 5.0) · P(eleito) 0.0%
- GOV-MG · GABRIEL (MDB, sq 130002549557) · movimento de nível -0.11pp em 3 dias (z -5.1, 3 institutos) · hoje: share 3.4% (sd 3.0) · P(eleito) 0.0%
- PRES · RENAN SANTOS (MISSÃO, sq 280002540694) · movimento de nível -0.11pp em 3 dias (z -4.8, 3 institutos) · hoje: share 4.7% (sd 3.0) · P(eleito) 0.0%
- PRES · ESCRITOR AUGUSTO CURY (AVANTE, sq 280002551547) · movimento de nível -0.39pp em 3 dias (z -7.4, 3 institutos) · hoje: share 6.9% (sd 3.6) · P(eleito) 0.0%
- PRES · RONALDO CAIADO (PSD, sq 280002551932) · movimento de nível -0.05pp em 3 dias (z -5.2, 3 institutos) · hoje: share 3.5% (sd 3.0) · P(eleito) 0.0%
- SEN-DF · SEBASTIÃO COELHO (NOVO, sq 70002548624) · movimento de nível -0.08pp em 3 dias (z -3.1, 2 institutos) · hoje: share 4.8% (sd 3.2) · P(eleito) 0.0%
- SEN-GO · DR. ZACHARIAS CALIL (MDB, sq 90002546974) · movimento de nível +0.30pp em 3 dias (z +6.7, 3 institutos) · hoje: share 16.9% (sd 5.9) · P(eleito) 20.1%
- SEN-RJ · CARLOS JORDY (PL, sq 190002542888) · movimento de nível +0.10pp em 3 dias (z +6.5, 2 institutos) · hoje: share 17.7% (sd 7.7) · P(eleito) 45.0%

### 2026-09-17 · 8 candidatos · corridas {'GOV-MG': 3, 'SEN-RJ': 1, 'PRES': 3, 'SEN-GO': 1}
- GOV-MG · ALEXANDRE KALIL (PDT, sq 130002539775) · movimento de nível -0.42pp em 3 dias (z -3.1, 2 institutos) · hoje: share 11.2% (sd 3.3) · P(eleito) 0.0%
- GOV-MG · MATEUS SIMÕES (PSD, sq 130002541911) · movimento de nível -0.12pp em 3 dias (z -5.6, 2 institutos) · hoje: share 8.0% (sd 5.0) · P(eleito) 0.0%
- GOV-MG · GABRIEL (MDB, sq 130002549557) · movimento de nível -0.11pp em 3 dias (z -5.1, 3 institutos) · hoje: share 3.4% (sd 3.0) · P(eleito) 0.0%
- PRES · RENAN SANTOS (MISSÃO, sq 280002540694) · movimento de nível -0.11pp em 3 dias (z +4.2, 2 institutos) · hoje: share 4.7% (sd 3.0) · P(eleito) 0.0%
- PRES · ESCRITOR AUGUSTO CURY (AVANTE, sq 280002551547) · movimento de nível -0.67pp em 3 dias (z -4.3, 3 institutos) · hoje: share 6.9% (sd 3.6) · P(eleito) 0.0%
- PRES · RONALDO CAIADO (PSD, sq 280002551932) · movimento de nível -0.18pp em 3 dias (z -3.5, 3 institutos) · hoje: share 3.5% (sd 3.0) · P(eleito) 0.0%
- SEN-GO · DR. ZACHARIAS CALIL (MDB, sq 90002546974) · movimento de nível +0.30pp em 3 dias (z +6.7, 3 institutos) · hoje: share 16.9% (sd 5.9) · P(eleito) 20.1%
- SEN-RJ · CARLOS JORDY (PL, sq 190002542888) · movimento de nível +0.10pp em 3 dias (z +6.5, 2 institutos) · hoje: share 17.7% (sd 7.7) · P(eleito) 45.0%

### 2026-09-01 · 7 candidatos · corridas {'GOV-RJ': 1, 'GOV-PB': 1, 'SEN-PB': 1, 'SEN-CE': 1, 'PRES': 2, 'GOV-SC': 1}
- GOV-PB · CÍCERO LUCENA (MDB, sq 150002544133) · movimento de nível -0.84pp em 3 dias (z -3.6, 2 institutos) · hoje: share 24.6% (sd 6.6) · P(eleito) 0.0%
- GOV-RJ · ANDRÉ MARINHO (NOVO, sq 190002537524) · movimento de nível -0.03pp em 3 dias (z -3.9, 2 institutos) · hoje: share 2.0% (sd 3.0) · P(eleito) 0.0%
- GOV-SC · GELSON MERÍSIO (PSB, sq 240002548628) · movimento de nível +0.25pp em 3 dias (z +3.6, 2 institutos) · hoje: share 13.9% (sd 3.4) · P(eleito) 0.0%
- PRES · ESCRITOR AUGUSTO CURY (AVANTE, sq 280002551547) · movimento de nível +0.56pp em 3 dias (z +8.0, 8 institutos) · hoje: share 6.9% (sd 3.6) · P(eleito) 0.0%
- PRES · RONALDO CAIADO (PSD, sq 280002551932) · movimento de nível -0.20pp em 3 dias (z -5.1, 4 institutos) · hoje: share 3.5% (sd 3.0) · P(eleito) 0.0%
- SEN-CE · GUILHERME THEOPHILO (NOVO, sq 60002539687) · movimento de nível -0.03pp em 3 dias (z -4.2, 2 institutos) · hoje: share 1.9% (sd 3.0) · P(eleito) 0.0%
- SEN-PB · DR. MARCELO QUEIROGA (PL, sq 150002538459) · movimento de nível -0.24pp em 3 dias (z -3.5, 2 institutos) · hoje: share 9.9% (sd 4.0) · P(eleito) 0.3%

### 2026-09-08 · 7 candidatos · corridas {'GOV-PB': 2, 'GOV-RJ': 1, 'PRES': 1, 'GOV-TO': 1, 'SEN-RN': 1, 'SEN-CE': 1}
- GOV-PB · CÍCERO LUCENA (MDB, sq 150002544133) · movimento de nível -0.34pp em 3 dias (z -3.2, 2 institutos) · hoje: share 24.6% (sd 6.6) · P(eleito) 0.0%
- GOV-PB · LUCAS RIBEIRO (PP, sq 150002551789) · movimento de nível +0.57pp em 3 dias (z +3.7, 2 institutos) · hoje: share 52.9% (sd 8.6) · P(eleito) 100.0%
- GOV-RJ · ANDRÉ MARINHO (NOVO, sq 190002537524) · movimento de nível -0.04pp em 3 dias (z -3.7, 2 institutos) · hoje: share 2.0% (sd 3.0) · P(eleito) 0.0%
- GOV-TO · ATAIDES DE OLIVEIRA (NOVO, sq 270002548412) · movimento de nível -0.09pp em 3 dias (z -3.6, 2 institutos) · hoje: share 5.6% (sd 3.0) · P(eleito) 0.0%
- PRES · RONALDO CAIADO (PSD, sq 280002551932) · movimento de nível -0.10pp em 3 dias (z -5.6, 4 institutos) · hoje: share 3.5% (sd 3.0) · P(eleito) 0.0%
- SEN-CE · GUILHERME THEOPHILO (NOVO, sq 60002539687) · movimento de nível -0.05pp em 3 dias (z -4.1, 2 institutos) · hoje: share 1.9% (sd 3.0) · P(eleito) 0.0%
- SEN-RN · SAMANDA DE LULA (PT, sq 200002533841) · movimento de nível +0.06pp em 3 dias (z +3.7, 2 institutos) · hoje: share 14.5% (sd 3.9) · P(eleito) 3.6%

### 2026-09-19 · 7 candidatos · corridas {'SEN-GO': 1, 'SEN-RJ': 1, 'GOV-MG': 1, 'PRES': 3, 'SEN-DF': 1}
- GOV-MG · ALEXANDRE KALIL (PDT, sq 130002539775) · movimento de nível -0.14pp em 3 dias (z -3.6, 2 institutos) · hoje: share 11.2% (sd 3.3) · P(eleito) 0.0%
- PRES · RENAN SANTOS (MISSÃO, sq 280002540694) · movimento de nível -0.11pp em 3 dias (z -4.8, 3 institutos) · hoje: share 4.7% (sd 3.0) · P(eleito) 0.0%
- PRES · ESCRITOR AUGUSTO CURY (AVANTE, sq 280002551547) · movimento de nível -0.39pp em 3 dias (z -7.4, 3 institutos) · hoje: share 6.9% (sd 3.6) · P(eleito) 0.0%
- PRES · RONALDO CAIADO (PSD, sq 280002551932) · movimento de nível -0.05pp em 3 dias (z -5.2, 3 institutos) · hoje: share 3.5% (sd 3.0) · P(eleito) 0.0%
- SEN-DF · SEBASTIÃO COELHO (NOVO, sq 70002548624) · movimento de nível -0.08pp em 3 dias (z -3.1, 2 institutos) · hoje: share 4.8% (sd 3.2) · P(eleito) 0.0%
- SEN-GO · DR. ZACHARIAS CALIL (MDB, sq 90002546974) · movimento de nível -0.08pp em 3 dias (z +3.6, 3 institutos) · hoje: share 16.9% (sd 5.9) · P(eleito) 20.1%
- SEN-RJ · CARLOS JORDY (PL, sq 190002542888) · movimento de nível +0.10pp em 3 dias (z +6.5, 2 institutos) · hoje: share 17.7% (sd 7.7) · P(eleito) 45.0%

### 2026-08-25 · 6 candidatos · corridas {'PRES': 1, 'SEN-MA': 1, 'SEN-BA': 1, 'SEN-MS': 1, 'GOV-SC': 1, 'SEN-RJ': 1}
- GOV-SC · GELSON MERÍSIO (PSB, sq 240002548628) · movimento de nível +0.34pp em 3 dias (z +3.2, 2 institutos) · hoje: share 13.9% (sd 3.4) · P(eleito) 0.0%
- PRES · ESCRITOR AUGUSTO CURY (AVANTE, sq 280002551547) · movimento de nível +1.38pp em 3 dias (z +4.2, 7 institutos) · hoje: share 6.9% (sd 3.6) · P(eleito) 0.0%
- SEN-BA · ANGELO CORONEL (REPUBLICANOS, sq 50002533124) · movimento de nível +0.40pp em 3 dias (z -3.6, 2 institutos) · hoje: share 21.7% (sd 7.1) · P(eleito) 31.3%
- SEN-MA · DR.HILTON GONÇALO (MOBILIZA, sq 100002550418) · movimento de nível +0.28pp em 3 dias (z +6.2, 2 institutos) · hoje: share 6.8% (sd 5.7) · P(eleito) 1.6%
- SEN-MS · SORAYA (PSB, sq 120002547434) · movimento de nível +0.35pp em 3 dias (z +3.1, 2 institutos) · hoje: share 13.3% (sd 3.5) · P(eleito) 0.1%
- SEN-RJ · PEDRO PAULO (PSD, sq 190002548145) · movimento de nível -0.02pp em 3 dias (z -3.1, 2 institutos) · hoje: share 11.8% (sd 5.1) · P(eleito) 9.4%

### 2026-08-27 · 6 candidatos · corridas {'PRES': 1, 'SEN-RJ': 3, 'SEN-BA': 1, 'SEN-MS': 1}
- PRES · ESCRITOR AUGUSTO CURY (AVANTE, sq 280002551547) · movimento de nível +1.51pp em 3 dias (z +3.1, 7 institutos) · hoje: share 6.9% (sd 3.6) · P(eleito) 0.0%
- SEN-BA · ANGELO CORONEL (REPUBLICANOS, sq 50002533124) · movimento de nível +0.40pp em 3 dias (z -3.6, 2 institutos) · hoje: share 21.7% (sd 7.1) · P(eleito) 31.3%
- SEN-MS · SORAYA (PSB, sq 120002547434) · movimento de nível -0.15pp em 3 dias (z +5.8, 2 institutos) · hoje: share 13.3% (sd 3.5) · P(eleito) 0.1%
- SEN-RJ · PEDRO PAULO (PSD, sq 190002548145) · movimento de nível +0.26pp em 3 dias (z -5.6, 2 institutos) · hoje: share 11.8% (sd 5.1) · P(eleito) 9.4%
- SEN-RJ · WAGUINHO (REPUBLICANOS, sq 190002550182) · movimento de nível -0.10pp em 3 dias (z -7.3, 2 institutos) · hoje: share 5.5% (sd 3.3) · P(eleito) 0.1%
- SEN-RJ · MARCELO CRIVELLA (REPUBLICANOS, sq 190002550184) · movimento de nível -0.29pp em 3 dias (z -7.9, 2 institutos) · hoje: share 13.0% (sd 6.2) · P(eleito) 16.3%

### 2026-08-28 · 6 candidatos · corridas {'PRES': 1, 'SEN-RJ': 3, 'SEN-MS': 1, 'SEN-MA': 1}
- PRES · ESCRITOR AUGUSTO CURY (AVANTE, sq 280002551547) · movimento de nível +1.51pp em 3 dias (z +3.1, 7 institutos) · hoje: share 6.9% (sd 3.6) · P(eleito) 0.0%
- SEN-MA · DR.HILTON GONÇALO (MOBILIZA, sq 100002550418) · movimento de nível +0.04pp em 3 dias (z +6.5, 2 institutos) · hoje: share 6.8% (sd 5.7) · P(eleito) 1.6%
- SEN-MS · SORAYA (PSB, sq 120002547434) · movimento de nível -0.15pp em 3 dias (z +5.8, 2 institutos) · hoje: share 13.3% (sd 3.5) · P(eleito) 0.1%
- SEN-RJ · PEDRO PAULO (PSD, sq 190002548145) · movimento de nível +0.26pp em 3 dias (z -5.6, 2 institutos) · hoje: share 11.8% (sd 5.1) · P(eleito) 9.4%
- SEN-RJ · WAGUINHO (REPUBLICANOS, sq 190002550182) · movimento de nível -0.10pp em 3 dias (z -7.3, 2 institutos) · hoje: share 5.5% (sd 3.3) · P(eleito) 0.1%
- SEN-RJ · MARCELO CRIVELLA (REPUBLICANOS, sq 190002550184) · movimento de nível -0.29pp em 3 dias (z -7.9, 2 institutos) · hoje: share 13.0% (sd 6.2) · P(eleito) 16.3%

### 2026-09-02 · 6 candidatos · corridas {'PRES': 2, 'GOV-RJ': 1, 'GOV-PB': 1, 'GOV-SC': 1, 'SEN-CE': 1}
- GOV-PB · CÍCERO LUCENA (MDB, sq 150002544133) · movimento de nível -0.84pp em 3 dias (z -3.6, 2 institutos) · hoje: share 24.6% (sd 6.6) · P(eleito) 0.0%
- GOV-RJ · ANDRÉ MARINHO (NOVO, sq 190002537524) · movimento de nível -0.03pp em 3 dias (z -3.9, 2 institutos) · hoje: share 2.0% (sd 3.0) · P(eleito) 0.0%
- GOV-SC · GELSON MERÍSIO (PSB, sq 240002548628) · movimento de nível +0.25pp em 3 dias (z +3.6, 2 institutos) · hoje: share 13.9% (sd 3.4) · P(eleito) 0.0%
- PRES · ESCRITOR AUGUSTO CURY (AVANTE, sq 280002551547) · movimento de nível +0.37pp em 3 dias (z +7.1, 8 institutos) · hoje: share 6.9% (sd 3.6) · P(eleito) 0.0%
- PRES · RONALDO CAIADO (PSD, sq 280002551932) · movimento de nível -0.20pp em 3 dias (z -5.1, 4 institutos) · hoje: share 3.5% (sd 3.0) · P(eleito) 0.0%
- SEN-CE · GUILHERME THEOPHILO (NOVO, sq 60002539687) · movimento de nível -0.03pp em 3 dias (z -4.2, 2 institutos) · hoje: share 1.9% (sd 3.0) · P(eleito) 0.0%

### 2026-09-04 · 6 candidatos · corridas {'PRES': 2, 'GOV-PB': 1, 'GOV-MG': 1, 'SEN-PB': 1, 'SEN-RN': 1}
- GOV-MG · MATEUS SIMÕES (PSD, sq 130002541911) · movimento de nível +0.02pp em 3 dias (z -4.5, 2 institutos) · hoje: share 8.0% (sd 5.0) · P(eleito) 0.0%
- GOV-PB · LUCAS RIBEIRO (PP, sq 150002551789) · movimento de nível +1.08pp em 3 dias (z +4.4, 2 institutos) · hoje: share 52.9% (sd 8.6) · P(eleito) 100.0%
- PRES · ESCRITOR AUGUSTO CURY (AVANTE, sq 280002551547) · movimento de nível -0.17pp em 3 dias (z +6.1, 6 institutos) · hoje: share 6.9% (sd 3.6) · P(eleito) 0.0%
- PRES · RONALDO CAIADO (PSD, sq 280002551932) · movimento de nível -0.13pp em 3 dias (z -3.2, 5 institutos) · hoje: share 3.5% (sd 3.0) · P(eleito) 0.0%
- SEN-PB · DR. MARCELO QUEIROGA (PL, sq 150002538459) · movimento de nível -0.08pp em 3 dias (z -3.3, 2 institutos) · hoje: share 9.9% (sd 4.0) · P(eleito) 0.3%
- SEN-RN · SAMANDA DE LULA (PT, sq 200002533841) · movimento de nível +0.47pp em 3 dias (z +3.2, 2 institutos) · hoje: share 14.5% (sd 3.9) · P(eleito) 3.6%

### 2026-09-09 · 6 candidatos · corridas {'PRES': 1, 'GOV-MG': 1, 'GOV-SE': 1, 'SEN-RN': 1, 'SEN-CE': 1, 'GOV-TO': 1}
- GOV-MG · MATEUS SIMÕES (PSD, sq 130002541911) · movimento de nível -0.09pp em 3 dias (z -3.1, 3 institutos) · hoje: share 8.0% (sd 5.0) · P(eleito) 0.0%
- GOV-SE · RICARDO MARQUES (PL, sq 260002549466) · movimento de nível -0.18pp em 3 dias (z -3.8, 3 institutos) · hoje: share 7.4% (sd 4.0) · P(eleito) 0.0%
- GOV-TO · ATAIDES DE OLIVEIRA (NOVO, sq 270002548412) · movimento de nível -0.09pp em 3 dias (z -3.6, 2 institutos) · hoje: share 5.6% (sd 3.0) · P(eleito) 0.0%
- PRES · RONALDO CAIADO (PSD, sq 280002551932) · movimento de nível -0.10pp em 3 dias (z -5.6, 4 institutos) · hoje: share 3.5% (sd 3.0) · P(eleito) 0.0%
- SEN-CE · GUILHERME THEOPHILO (NOVO, sq 60002539687) · movimento de nível -0.05pp em 3 dias (z -4.1, 2 institutos) · hoje: share 1.9% (sd 3.0) · P(eleito) 0.0%
- SEN-RN · SAMANDA DE LULA (PT, sq 200002533841) · movimento de nível +0.06pp em 3 dias (z +3.7, 2 institutos) · hoje: share 14.5% (sd 3.9) · P(eleito) 3.6%

### 2026-09-10 · 6 candidatos · corridas {'PRES': 1, 'GOV-MG': 1, 'GOV-SE': 1, 'SEN-CE': 1, 'GOV-DF': 1, 'SEN-RN': 1}
- GOV-DF · ARRUDA (PSD, sq 70002552586) · movimento de nível -0.67pp em 3 dias (z -3.0, 2 institutos) · hoje: share 23.0% (sd 5.9) · P(eleito) 0.0%
- GOV-MG · MATEUS SIMÕES (PSD, sq 130002541911) · movimento de nível -0.09pp em 3 dias (z -3.1, 3 institutos) · hoje: share 8.0% (sd 5.0) · P(eleito) 0.0%
- GOV-SE · RICARDO MARQUES (PL, sq 260002549466) · movimento de nível -0.18pp em 3 dias (z -3.8, 3 institutos) · hoje: share 7.4% (sd 4.0) · P(eleito) 0.0%
- PRES · RONALDO CAIADO (PSD, sq 280002551932) · movimento de nível -0.10pp em 3 dias (z -5.6, 4 institutos) · hoje: share 3.5% (sd 3.0) · P(eleito) 0.0%
- SEN-CE · GUILHERME THEOPHILO (NOVO, sq 60002539687) · movimento de nível -0.05pp em 3 dias (z -4.1, 2 institutos) · hoje: share 1.9% (sd 3.0) · P(eleito) 0.0%
- SEN-RN · SAMANDA DE LULA (PT, sq 200002533841) · movimento de nível +0.06pp em 3 dias (z +3.7, 2 institutos) · hoje: share 14.5% (sd 3.9) · P(eleito) 3.6%

## Os 30 maiores movimentos de nível (entre 122 destaques)

| corrida | candidato | partido | sq | dia | Δ nível 3d | z | inst | hoje |
|---|---|---|---|---|---|---|---|---|
| PRES | FLAVIO BOLSONARO | PL | 280002551544 | 2026-05-15 | -1.89pp | -3.3 | 3 | share 39.6% (sd 3.7) · P(eleito) 51.3% |
| PRES | ESCRITOR AUGUSTO CURY | AVANTE | 280002551547 | 2026-08-27 | +1.51pp | +3.1 | 7 | share 6.9% (sd 3.6) · P(eleito) 0.0% |
| PRES | ESCRITOR AUGUSTO CURY | AVANTE | 280002551547 | 2026-08-26 | +1.38pp | +4.2 | 7 | share 6.9% (sd 3.6) · P(eleito) 0.0% |
| GOV-PB | LUCAS RIBEIRO | PP | 150002551789 | 2026-09-05 | +1.08pp | +4.4 | 2 | share 52.9% (sd 8.6) · P(eleito) 100.0% |
| GOV-AM | PROFESSORA MARIA DO CARMO | PL | 40002541626 | 2026-05-18 | -0.99pp | -5.0 | 2 | share 23.5% (sd 4.8) · P(eleito) 1.2% |
| PRES | ESCRITOR AUGUSTO CURY | AVANTE | 280002551547 | 2026-08-30 | +0.93pp | +19.2 | 8 | share 6.9% (sd 3.6) · P(eleito) 0.0% |
| GOV-PB | CÍCERO LUCENA | MDB | 150002544133 | 2026-09-02 | -0.84pp | -3.6 | 2 | share 24.6% (sd 6.6) · P(eleito) 0.0% |
| SEN-GO | DR. ZACHARIAS CALIL | MDB | 90002546974 | 2026-09-15 | +0.80pp | +3.2 | 3 | share 16.9% (sd 5.9) · P(eleito) 20.1% |
| SEN-RJ | CARLOS JORDY | PL | 190002542888 | 2026-09-12 | +0.77pp | +3.3 | 2 | share 17.7% (sd 7.7) · P(eleito) 45.0% |
| GOV-DF | CELINA LEÃO | PP | 70002553055 | 2026-08-15 | -0.75pp | -3.9 | 2 | share 43.7% (sd 5.1) · P(eleito) 100.0% |
| GOV-AM | PROFESSORA MARIA DO CARMO | PL | 40002541626 | 2026-05-27 | -0.72pp | -3.5 | 2 | share 23.5% (sd 4.8) · P(eleito) 1.2% |
| PRES | ESCRITOR AUGUSTO CURY | AVANTE | 280002551547 | 2026-09-16 | -0.67pp | -4.3 | 3 | share 6.9% (sd 3.6) · P(eleito) 0.0% |
| GOV-DF | ARRUDA | PSD | 70002552586 | 2026-09-11 | -0.67pp | -3.0 | 2 | share 23.0% (sd 5.9) · P(eleito) 0.0% |
| GOV-PB | LUCAS RIBEIRO | PP | 150002551789 | 2026-09-07 | +0.57pp | +3.7 | 2 | share 52.9% (sd 8.6) · P(eleito) 100.0% |
| PRES | ESCRITOR AUGUSTO CURY | AVANTE | 280002551547 | 2026-08-31 | +0.56pp | +8.0 | 8 | share 6.9% (sd 3.6) · P(eleito) 0.0% |
| SEN-RJ | MARCELO CRIVELLA | REPUBLICANOS | 190002550184 | 2026-08-21 | -0.54pp | -5.0 | 2 | share 13.0% (sd 6.2) · P(eleito) 16.3% |
| GOV-DF | ARRUDA | PSD | 70002552586 | 2026-09-12 | -0.50pp | -3.9 | 2 | share 23.0% (sd 5.9) · P(eleito) 0.0% |
| SEN-RN | SAMANDA DE LULA | PT | 200002533841 | 2026-09-05 | +0.47pp | +3.2 | 2 | share 14.5% (sd 3.9) · P(eleito) 3.6% |
| GOV-AM | PROFESSORA MARIA DO CARMO | PL | 40002541626 | 2026-05-22 | -0.46pp | -3.6 | 3 | share 23.5% (sd 4.8) · P(eleito) 1.2% |
| GOV-SE | RICARDO MARQUES | PL | 260002549466 | 2026-04-20 | -0.46pp | -3.5 | 2 | share 7.4% (sd 4.0) · P(eleito) 0.0% |
| SEN-MA | LAHESIO BONFIM | NOVO | 100002548011 | 2026-08-10 | -0.42pp | -4.4 | 2 | share 17.6% (sd 4.6) · P(eleito) 38.3% |
| GOV-MG | ALEXANDRE KALIL | PDT | 130002539775 | 2026-09-17 | -0.42pp | -3.1 | 2 | share 11.2% (sd 3.3) · P(eleito) 0.0% |
| SEN-BA | ANGELO CORONEL | REPUBLICANOS | 50002533124 | 2026-08-26 | +0.40pp | -3.6 | 2 | share 21.7% (sd 7.1) · P(eleito) 31.3% |
| PRES | ESCRITOR AUGUSTO CURY | AVANTE | 280002551547 | 2026-09-18 | -0.39pp | -7.4 | 3 | share 6.9% (sd 3.6) · P(eleito) 0.0% |
| PRES | ESCRITOR AUGUSTO CURY | AVANTE | 280002551547 | 2026-09-01 | +0.37pp | +7.1 | 8 | share 6.9% (sd 3.6) · P(eleito) 0.0% |
| GOV-RN | CADU DE LULA | PT | 200002534001 | 2026-04-04 | +0.35pp | +5.4 | 2 | share 26.0% (sd 5.1) · P(eleito) 0.0% |
| GOV-GO | WILDER MORAIS | PL | 90002551791 | 2026-05-29 | +0.35pp | +4.7 | 2 | share 20.9% (sd 5.0) · P(eleito) 0.0% |
| SEN-MS | SORAYA | PSB | 120002547434 | 2026-08-24 | +0.35pp | +3.1 | 2 | share 13.3% (sd 3.5) · P(eleito) 0.1% |
| GOV-SC | GELSON MERÍSIO | PSB | 240002548628 | 2026-08-25 | +0.34pp | +3.2 | 2 | share 13.9% (sd 3.4) · P(eleito) 0.0% |
| GOV-PB | CÍCERO LUCENA | MDB | 150002544133 | 2026-09-07 | -0.34pp | -3.2 | 2 | share 24.6% (sd 6.6) · P(eleito) 0.0% |

## Contexto das corridas mais envolvidas (quadro publicado hoje)

### PRES · 40 destaques · 159 pesquisas usáveis · dado: ok · 2 vagas: não
- LULA (PT, sq 280002542548) · share 42.7% ± 3.0 · P(eleito) 48.7% · P(2ºT) 100.0%
- FLAVIO BOLSONARO (PL, sq 280002551544) · share 39.6% ± 3.7 · P(eleito) 51.3% · P(2ºT) 99.8%
- ESCRITOR AUGUSTO CURY (AVANTE, sq 280002551547) · share 6.9% ± 3.6 · P(eleito) 0.0% · P(2ºT) 0.0%
- RENAN SANTOS (MISSÃO, sq 280002540694) · share 4.7% ± 3.0 · P(eleito) 0.0% · P(2ºT) 0.0%
- RONALDO CAIADO (PSD, sq 280002551932) · share 3.5% ± 3.0 · P(eleito) 0.0% · P(2ºT) 0.0%

### GOV-MG · 11 destaques · 30 pesquisas usáveis · dado: ok · 2 vagas: não
- CLEITINHO AZEVEDO (REPUBLICANOS, sq 130002552296) · share 46.0% ± 6.3 · P(eleito) 100.0% · P(2ºT) 100.0%
- PATRUS ANANIAS (PT, sq 130002550464) · share 22.7% ± 6.2 · P(eleito) 0.0% · P(2ºT) 81.7%
- ALEXANDRE KALIL (PDT, sq 130002539775) · share 11.2% ± 3.3 · P(eleito) 0.0% · P(2ºT) 2.8%
- MATEUS SIMÕES (PSD, sq 130002541911) · share 8.0% ± 5.0 · P(eleito) 0.0% · P(2ºT) 2.1%
- FLÁVIO ROSCOE (PL, sq 130002550834) · share 6.8% ± 3.0 · P(eleito) 0.0% · P(2ºT) 0.2%

### SEN-RJ · 8 destaques · 17 pesquisas usáveis · dado: ok · 2 vagas: sim
- BENEDITA DA SILVA (PT, sq 190002548141) · share 27.1% ± 5.0 · P(eleito) 94.9%
- CARLOS JORDY (PL, sq 190002542888) · share 17.7% ± 7.7 · P(eleito) 45.0%
- CARLOS PORTINHO (PL, sq 190002535142) · share 16.1% ± 7.0 · P(eleito) 33.6%
- MARCELO CRIVELLA (REPUBLICANOS, sq 190002550184) · share 13.0% ± 6.2 · P(eleito) 16.3%
- PEDRO PAULO (PSD, sq 190002548145) · share 11.8% ± 5.1 · P(eleito) 9.4%

### SEN-RN · 6 destaques · 47 pesquisas usáveis · dado: ok · 2 vagas: sim
- STYVENSON VALENTIM (PODE, sq 200002534448) · share 34.7% ± 5.8 · P(eleito) 99.8%
- ZENAIDE MAIA (PSD, sq 200002535507) · share 25.3% ± 4.6 · P(eleito) 93.9%
- SAMANDA DE LULA (PT, sq 200002533841) · share 14.5% ± 3.9 · P(eleito) 3.6%
- RAFAEL MOTTA (PDT, sq 200002533843) · share 13.2% ± 3.9 · P(eleito) 1.8%
- CORONEL HÉLIO (PL, sq 200002534447) · share 12.3% ± 3.5 · P(eleito) 0.9%

### GOV-SE · 5 destaques · 39 pesquisas usáveis · dado: ok · 2 vagas: não
- FÁBIO (PSD, sq 260002542491) · share 52.6% ± 6.8 · P(eleito) 98.7% · P(2ºT) 98.8%
- VALMIR DE FRANCISQUINHO (REPUBLICANOS, sq 260002532010) · share 40.0% ± 6.2 · P(eleito) 1.4% · P(2ºT) 44.1%
- RICARDO MARQUES (PL, sq 260002549466) · share 7.4% ± 4.0 · P(eleito) 0.0% · P(2ºT) 0.0%
- DR. HELTON (PSOL, sq 260002547415) · share 0.0% ± 3.0 · P(eleito) 0.0% · P(2ºT) 0.0%
- TATY  CRISTINA DE JESUS (DC, sq 260002550683) · share 0.0% ± 3.0 · P(eleito) 0.0% · P(2ºT) 0.0%

### GOV-RN · 5 destaques · 56 pesquisas usáveis · dado: ok · 2 vagas: não
- ALLYSON (UNIÃO, sq 200002535255) · share 45.1% ± 6.2 · P(eleito) 99.8% · P(2ºT) 99.8%
- ÁLVARO DIAS (PL, sq 200002534442) · share 28.9% ± 4.9 · P(eleito) 0.2% · P(2ºT) 62.3%
- CADU DE LULA (PT, sq 200002534001) · share 26.0% ± 5.1 · P(eleito) 0.0% · P(2ºT) 33.0%
- DÁRIO BARBOSA (PSTU, sq 200002542481) · share 0.0% ± 3.0 · P(eleito) 0.0% · P(2ºT) 0.0%
- RODRIGO DE BOLSONARO (AGIR, sq 200002546756) · share 0.0% ± 3.0 · P(eleito) 0.0% · P(2ºT) 0.0%

### GOV-PB · 4 destaques · 24 pesquisas usáveis · dado: ok · 2 vagas: não
- LUCAS RIBEIRO (PP, sq 150002551789) · share 52.9% ± 8.6 · P(eleito) 100.0% · P(2ºT) 100.0%
- CÍCERO LUCENA (MDB, sq 150002544133) · share 24.6% ± 6.6 · P(eleito) 0.0% · P(2ºT) 27.6%
- EFRAIM FILHO (PL, sq 150002538692) · share 22.6% ± 5.3 · P(eleito) 0.0% · P(2ºT) 15.5%
- YURI EZEQUIEL (UP, sq 150002540204) · share 0.0% ± 3.0 · P(eleito) 0.0% · P(2ºT) 0.0%
- PEDRO COUTINHO (DC, sq 150002551911) · share 0.0% ± 3.0 · P(eleito) 0.0% · P(2ºT) 0.0%

### GOV-DF · 4 destaques · 21 pesquisas usáveis · dado: ok · 2 vagas: não
- CELINA LEÃO (PP, sq 70002553055) · share 43.7% ± 5.1 · P(eleito) 100.0% · P(2ºT) 100.0%
- ARRUDA (PSD, sq 70002552586) · share 23.0% ± 5.9 · P(eleito) 0.0% · P(2ºT) 60.6%
- LEANDRO GRASS (PT, sq 70002552496) · share 20.5% ± 5.0 · P(eleito) 0.0% · P(2ºT) 35.1%
- PAULA BELMONTE (PSDB, sq 70002552965) · share 6.5% ± 3.0 · P(eleito) 0.0% · P(2ºT) 0.0%
- CAPPELLI (PSB, sq 70002551557) · share 3.7% ± 3.0 · P(eleito) 0.0% · P(2ºT) 0.0%

### SEN-MA · 4 destaques · 13 pesquisas usáveis · dado: ok · 2 vagas: sim
- ROSEANA SARNEY (MDB, sq 100002549583) · share 25.5% ± 5.5 · P(eleito) 90.6%
- FUFUCA (PP, sq 100002542867) · share 18.2% ± 3.1 · P(eleito) 42.4%
- LAHESIO BONFIM (NOVO, sq 100002548011) · share 17.6% ± 4.6 · P(eleito) 38.3%
- WEVERTON ROCHA (PDT, sq 100002537338) · share 16.3% ± 4.1 · P(eleito) 24.4%
- ELIZIANE GAMA (PT, sq 100002541459) · share 12.4% ± 3.2 · P(eleito) 2.6%

### GOV-GO · 4 destaques · 39 pesquisas usáveis · dado: ok · 2 vagas: não
- DANIEL VILELA (MDB, sq 90002540993) · share 46.6% ± 5.6 · P(eleito) 100.0% · P(2ºT) 100.0%
- MARCONI PERILLO (PSDB, sq 90002543463) · share 24.0% ± 7.2 · P(eleito) 0.0% · P(2ºT) 53.0%
- WILDER MORAIS (PL, sq 90002551791) · share 20.9% ± 5.0 · P(eleito) 0.0% · P(2ºT) 25.7%
- LUIS CESAR BUENO (PT, sq 90002545476) · share 8.5% ± 3.7 · P(eleito) 0.0% · P(2ºT) 0.1%
- LUCIANA AMORIM (UP, sq 90002550707) · share 0.0% ± 3.0 · P(eleito) 0.0% · P(2ºT) 0.0%

## Ressalvas do detector (viajam com o dado)
- CANDIDATO a inflexão, não inflexão confirmada: o resíduo padronizado não separa salto de nível de pesquisa fora da curva.
- MAGNITUDE SUBESTIMADA POR CONSTRUÇÃO, e isto foi medido. O passeio é gaussiano em LOGIT com SIGMA_RW constante, calibrado num 2º turno em que os dois candidatos estavam perto de 50%. Como d(share)/d(logit) = p(1-p), o mesmo passeio vale 0,33 p.p./dia para quem está em 50% e 0,06 p.p./dia para quem está em 5%. O memo atribui a Cury +3,0 p.p. num dia com share de ~5%: para este filtro aceitar isso, SIGMA_RW teria de ser 48x o calibrado. Aqueles números vêm do ajuste bayesiano com cauda de Student, em que o salto é parâmetro próprio, e esse ajuste NÃO entra no repo (zero-dep). Conclusão prática: confie na DATA, desconfie da magnitude.
- A data, essa, confere: o episódio de Cury que o plano cita em 27/08 aparece aqui em 26/08 e 27/08, corroborado por instituto diferente.
- delta_dia_pp e delta_janela_pp são escalas diferentes: salto do nível no dia contra variação do nível na janela seguinte.
- Coincidir com um evento NÃO é causa. A atribuição é o M3, e depende de direção pré-especificada e de janela placebo.
- Corrida com poucas pesquisas produz resíduo instável: olhe corroborado e institutos antes de acreditar.