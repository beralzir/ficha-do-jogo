# Dossiê de causas · período P1: 2026-08-01 a 2026-08-31

Gerado em 2026-09-25 do dado publicado (as_of 2026-09-24). Detector M2 do Ficha do Jogo (bera.ia.br/ficha-do-jogo): |z|>3 no filtro de Kalman do competidor v2, corroborado por 2+ institutos, share>=2%. MAGNITUDE SUBESTIMADA POR CONSTRUÇÃO (passeio em logit calibrado a 50%): confie na DATA, desconfie do tamanho.

## CONTRATO DE SAÍDA (leia antes de tudo)

Tarefa: para cada DATA de inflexão do período, procurar na imprensa e em fontes primárias o que aconteceu no raio de 0 a 7 dias ANTES dela que possa ser causa candidata do movimento, e devolver EVENTOS no schema exato do registro do projeto, mais as três pernas de teste. Não é para confirmar causa: é para registrar causa candidata de forma testável. Data sem evento plausível: diga "sem evento plausível encontrado" e liste o que procurou.

Schema de evento (exato; o validador do projeto recusa fora disso):
{"id":"<slug>-<AAAA-MM-DD>","data":"AAAA-MM-DD","registrado_em":"2026-09-25","tipo":"debate|decisao_judicial|denuncia|peca_desinformacao|economico|pesquisa_bomba","alvo":[sq,...],"direcao_esperada":"+|-|?","escopo":"nacional|UF","fonte":{"url":"...","veiculo":"...","acesso":"2026-09-25"},"notas":"..."}
- `alvo` só com sq da lista abaixo (o candidato que o evento atinge, não quem se moveu por tabela).
- `direcao_esperada` é a direção que o MECANISMO prevê para o alvo, escrita antes de olhar o movimento; se você só consegue escrever depois de olhar, diga isso em `notas`.
- Evento passado registrado hoje nasce EXPLORATÓRIO pela regra do projeto (registrado_em > data). Evento FUTURO (agenda: debate, decisão marcada, divulgação de pesquisa) nasce pré-especificado: registre os que encontrar.

Para cada evento, além do JSON, escreva:
1. Mecanismo, em 1 a 3 frases, cada uma marcada [fato] / [inferência] / [hipótese].
2. Inflexões que ele poderia explicar (data, corrida, candidato) e as que ele NÃO explica (quem mais deveria ter se movido e não se moveu, ou vice-versa): são as IMPLICAÇÕES CRUZADAS, conferíveis no dado do site agora.
3. Replicação para a frente: a próxima ocorrência da mesma classe de evento até 04/10 (ou o 2º turno), com a direção prevista para quem, pré-especificada.
4. Fonte com URL e data de acesso; se não conseguir abrir a fonte primária, diga "não confirmado" e não invente.

Fontes de curadoria da casa: Agência Lupa, Aos Fatos, decisões do TSE (propaganda, representações, registros), agenda oficial de debates, indicadores econômicos (IBGE, BC), e imprensa nacional/regional com URL. Português do Brasil, sem travessão espaçado (" — "): vírgula, dois-pontos ou parênteses. Declare seu corte de conhecimento no início.

Saída: seções fixas, nesta ordem: (1) corte de conhecimento e fontes abertas (URL, data); (2) tabela data -> evento(s) candidato(s) ou "sem evento plausível"; (3) bloco JSON (array) dos eventos; (4) para cada evento, os itens 1 a 4 acima; (5) o que não dá para afirmar. Grave o resultado completo em /private/tmp/claude-501/-Users-beralzir-Projetos-ficha-do-jogo--claude-worktrees-exciting-khorana-550dba/51aa27e1-edf2-42df-bbe5-4d7e4c7a616d/scratchpad/causas_<PERIODO>_resultado.md e devolva-o na íntegra.

## Datas de inflexão do período (16 datas, 26 destaques)

### 2026-08-10 · cluster ±1 dia: 1 candidatos em 1 corridas {'SEN-MA': 1}
- SEN-MA · LAHESIO BONFIM (NOVO, sq 100002548011) · Δ nível -0.42pp em 3 dias · z -4.4 · disparou: IPPI · corroborou: Véritas · hoje share 17.6% P(eleito) 38.3%

### 2026-08-11 · cluster ±1 dia: 1 candidatos em 1 corridas {'SEN-MA': 1}
- SEN-MA · LAHESIO BONFIM (NOVO, sq 100002548011) · Δ nível -0.32pp em 3 dias · z -3.5 · disparou: Véritas · corroborou: IPPI · hoje share 17.6% P(eleito) 38.3%

### 2026-08-15 · cluster ±1 dia: 2 candidatos em 2 corridas {'GOV-DF': 1, 'GOV-PA': 1}
- GOV-DF · CELINA LEÃO (PP, sq 70002553055) · Δ nível -0.75pp em 3 dias · z -3.9 · disparou: IGAPE · corroborou: Real Time Big Data · hoje share 43.7% P(eleito) 100.0%
- GOV-PA · ARACELI (PSOL, sq 140002542386) · Δ nível -0.06pp em 3 dias · z -3.4 · disparou: Doxa · corroborou: AtlasIntel · hoje share 3.3% P(eleito) 0.0%

### 2026-08-17 · cluster ±1 dia: 2 candidatos em 2 corridas {'GOV-GO': 1, 'GOV-DF': 1}
- GOV-GO · LUIS CESAR BUENO (PT, sq 90002545476) · Δ nível +0.13pp em 3 dias · z -3.1 · disparou: Paraná Pesquisas · corroborou: Brasmarket/Jovem Pan News · hoje share 8.5% P(eleito) 0.0%

### 2026-08-18 · cluster ±1 dia: 3 candidatos em 3 corridas {'GOV-GO': 1, 'GOV-DF': 1, 'GOV-PA': 1}
- GOV-DF · CELINA LEÃO (PP, sq 70002553055) · Δ nível -0.29pp em 3 dias · z -3.0 · disparou: Real Time Big Data · corroborou: IGAPE · hoje share 43.7% P(eleito) 100.0%

### 2026-08-19 · cluster ±1 dia: 2 candidatos em 2 corridas {'GOV-DF': 1, 'GOV-PA': 1}
- GOV-PA · ARACELI (PSOL, sq 140002542386) · Δ nível -0.04pp em 3 dias · z -3.4 · disparou: AtlasIntel · corroborou: Doxa · hoje share 3.3% P(eleito) 0.0%

### 2026-08-21 · cluster ±1 dia: 4 candidatos em 3 corridas {'SEN-RJ': 2, 'GOV-GO': 1, 'SEN-BA': 1}
- SEN-RJ · MARCELO CRIVELLA (REPUBLICANOS, sq 190002550184) · Δ nível -0.54pp em 3 dias · z -5.0 · disparou: Datafolha · corroborou: Veritá · hoje share 13.0% P(eleito) 16.3%
- GOV-GO · LUIS CESAR BUENO (PT, sq 90002545476) · Δ nível +0.22pp em 3 dias · z -3.8 · disparou: Brasmarket/Jovem Pan News · corroborou: Paraná Pesquisas · hoje share 8.5% P(eleito) 0.0%
- SEN-RJ · WAGUINHO (REPUBLICANOS, sq 190002550182) · Δ nível -0.20pp em 3 dias · z -3.6 · disparou: Datafolha · corroborou: Veritá · hoje share 5.5% P(eleito) 0.1%

### 2026-08-22 · cluster ±1 dia: 4 candidatos em 3 corridas {'SEN-RJ': 2, 'GOV-GO': 1, 'SEN-BA': 1}
- SEN-BA · ANGELO CORONEL (REPUBLICANOS, sq 50002533124) · Δ nível +0.06pp em 3 dias · z -4.2 · disparou: Opnus/BNews · corroborou: Quaest · hoje share 21.7% P(eleito) 31.3%

### 2026-08-24 · cluster ±1 dia: 4 candidatos em 4 corridas {'SEN-MS': 1, 'GOV-SC': 1, 'SEN-RJ': 1, 'SEN-MA': 1}
- SEN-MS · SORAYA (PSB, sq 120002547434) · Δ nível +0.35pp em 3 dias · z +3.1 · disparou: Quaest · corroborou: Ranking Brasil · hoje share 13.3% P(eleito) 0.1%
- SEN-RJ · PEDRO PAULO (PSD, sq 190002548145) · Δ nível -0.02pp em 3 dias · z -3.1 · disparou: Quaest · corroborou: Veritá · hoje share 11.8% P(eleito) 9.4%

### 2026-08-25 · cluster ±1 dia: 6 candidatos em 6 corridas {'SEN-MS': 1, 'GOV-SC': 1, 'PRES': 1, 'SEN-MA': 1, 'SEN-BA': 1, 'SEN-RJ': 1}
- GOV-SC · GELSON MERÍSIO (PSB, sq 240002548628) · Δ nível +0.34pp em 3 dias · z +3.2 · disparou: Neokemp/OCP · corroborou: Veritá · hoje share 13.9% P(eleito) 0.0%
- SEN-MA · DR.HILTON GONÇALO (MOBILIZA, sq 100002550418) · Δ nível +0.28pp em 3 dias · z +6.2 · disparou: Qualitativa · corroborou: IPSensus · hoje share 6.8% P(eleito) 1.6%

### 2026-08-26 · cluster ±1 dia: 5 candidatos em 5 corridas {'SEN-MS': 1, 'GOV-SC': 1, 'PRES': 1, 'SEN-MA': 1, 'SEN-BA': 1}
- PRES · ESCRITOR AUGUSTO CURY (AVANTE, sq 280002551547) · Δ nível +1.38pp em 3 dias · z +4.2 · disparou: PoderData · corroborou: AtlasIntel, Futura, Nexus/BTG, Quaest, Real Time Big Data, Vox Brasil · hoje share 6.9% P(eleito) 0.0%
- SEN-BA · ANGELO CORONEL (REPUBLICANOS, sq 50002533124) · Δ nível +0.40pp em 3 dias · z -3.6 · disparou: Quaest · corroborou: Opnus/BNews · hoje share 21.7% P(eleito) 31.3%

### 2026-08-27 · cluster ±1 dia: 6 candidatos em 4 corridas {'SEN-MS': 1, 'SEN-RJ': 3, 'PRES': 1, 'SEN-BA': 1}
- PRES · ESCRITOR AUGUSTO CURY (AVANTE, sq 280002551547) · Δ nível +1.51pp em 3 dias · z +3.1 · disparou: Vox Brasil · corroborou: AtlasIntel, Futura, Nexus/BTG, PoderData, Quaest, Real Time Big Data · hoje share 6.9% P(eleito) 0.0%
- SEN-MS · SORAYA (PSB, sq 120002547434) · Δ nível -0.15pp em 3 dias · z +5.8 · disparou: Ranking Brasil · corroborou: Quaest · hoje share 13.3% P(eleito) 0.1%

### 2026-08-28 · cluster ±1 dia: 6 candidatos em 4 corridas {'SEN-MS': 1, 'SEN-RJ': 3, 'PRES': 1, 'SEN-MA': 1}
- SEN-RJ · MARCELO CRIVELLA (REPUBLICANOS, sq 190002550184) · Δ nível -0.29pp em 3 dias · z -7.9 · disparou: Veritá · corroborou: Datafolha · hoje share 13.0% P(eleito) 16.3%
- SEN-RJ · PEDRO PAULO (PSD, sq 190002548145) · Δ nível +0.26pp em 3 dias · z -5.6 · disparou: Veritá · corroborou: Quaest · hoje share 11.8% P(eleito) 9.4%
- SEN-RJ · WAGUINHO (REPUBLICANOS, sq 190002550182) · Δ nível -0.10pp em 3 dias · z -7.3 · disparou: Veritá · corroborou: Datafolha · hoje share 5.5% P(eleito) 0.1%

### 2026-08-29 · cluster ±1 dia: 5 candidatos em 3 corridas {'SEN-RJ': 3, 'PRES': 1, 'SEN-MA': 1}
- SEN-MA · DR.HILTON GONÇALO (MOBILIZA, sq 100002550418) · Δ nível +0.04pp em 3 dias · z +6.5 · disparou: IPSensus · corroborou: Qualitativa · hoje share 6.8% P(eleito) 1.6%

### 2026-08-30 · cluster ±1 dia: 3 candidatos em 3 corridas {'SEN-MA': 1, 'SEN-PB': 1, 'PRES': 1}
- PRES · ESCRITOR AUGUSTO CURY (AVANTE, sq 280002551547) · Δ nível +0.93pp em 3 dias · z +19.2 · disparou: AtlasIntel, Nexus/BTG · corroborou: AtlasIntel, Futura, Nexus/BTG, PoderData, Quaest, Real Time Big Data, Veritá, Vox Brasil · hoje share 6.9% P(eleito) 0.0%

### 2026-08-31 · cluster ±1 dia: 5 candidatos em 4 corridas {'GOV-SC': 1, 'GOV-RJ': 1, 'SEN-PB': 1, 'PRES': 2}
- PRES · ESCRITOR AUGUSTO CURY (AVANTE, sq 280002551547) · Δ nível +0.56pp em 3 dias · z +8.0 · disparou: Real Time Big Data · corroborou: AtlasIntel, Futura, Nexus/BTG, PoderData, Quaest, Veritá, Vox Brasil · hoje share 6.9% P(eleito) 0.0%
- SEN-PB · DR. MARCELO QUEIROGA (PL, sq 150002538459) · Δ nível -0.24pp em 3 dias · z -3.5 · disparou: TDL · corroborou: Anova · hoje share 9.9% P(eleito) 0.3%

## Já registrado (não duplicar)
- eventos.json: cury-viral-2026-08-26 (2026-08-26, denuncia, alvo [280002551547], direção +)
- hipoteses.json (de tendência, 25/09): h-2026-09-25-01 Cury devolve mais 1 pp até a urna; h-2026-09-25-02 Flávio sobe 1 pp no agregado até 04/10; h-2026-09-25-03 P(eleito) de Flávio segue subindo no 2º turno; h-2026-09-25-04 A próxima AtlasIntel derruba os nanicos no detector; h-2026-09-25-05 Lote da Veritá vira choque comum, com sinal negativo em 'outros'; h-2026-09-25-06 Kalil perde mais 1 pp em MG; h-2026-09-25-07 O choque de 17 a 19/09 persiste nos sete que caíram; h-2026-09-25-08 Calil sobe 1 pp com a chapa de Vilela em GO; h-2026-09-25-09 Jordy fecha o 1º turno como favorito à 2ª vaga no RJ; h-2026-09-25-10 Debate da Globo não rende inflexão positiva a Cury; h-2026-09-25-11 A urna dá a Flávio mais do que o agregado final; h-2026-09-25-12 A urna dá a Cury menos do que o agregado final

## Calendário
- 1º turno 2026-10-04 · 2º turno 2026-10-25 · debate Globo 01/10 (único restante do 1º turno, segundo a imprensa) · horário eleitoral desde 28/08 (não reconferido).
