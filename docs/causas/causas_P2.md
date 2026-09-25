# Dossiê de causas · período P2: 2026-09-01 a 2026-09-15

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

## Datas de inflexão do período (13 datas, 32 destaques)

### 2026-09-01 · cluster ±1 dia: 7 candidatos em 6 corridas {'GOV-SC': 1, 'GOV-RJ': 1, 'SEN-PB': 1, 'PRES': 2, 'SEN-CE': 1, 'GOV-PB': 1}
- PRES · ESCRITOR AUGUSTO CURY (AVANTE, sq 280002551547) · Δ nível +0.37pp em 3 dias · z +7.1 · disparou: Futura, Quaest · corroborou: AtlasIntel, Futura, Nexus/BTG, PoderData, Quaest, Real Time Big Data, Veritá, Vox Brasil · hoje share 6.9% P(eleito) 0.0%
- GOV-SC · GELSON MERÍSIO (PSB, sq 240002548628) · Δ nível +0.25pp em 3 dias · z +3.6 · disparou: Veritá · corroborou: Neokemp/OCP · hoje share 13.9% P(eleito) 0.0%
- PRES · RONALDO CAIADO (PSD, sq 280002551932) · Δ nível -0.20pp em 3 dias · z -5.1 · disparou: Quaest · corroborou: Palver, PoderData, Veritá · hoje share 3.5% P(eleito) 0.0%
- GOV-RJ · ANDRÉ MARINHO (NOVO, sq 190002537524) · Δ nível -0.03pp em 3 dias · z -3.9 · disparou: Real Time Big Data · corroborou: Quaest · hoje share 2.0% P(eleito) 0.0%

### 2026-09-02 · cluster ±1 dia: 6 candidatos em 5 corridas {'GOV-SC': 1, 'GOV-RJ': 1, 'SEN-CE': 1, 'PRES': 2, 'GOV-PB': 1}
- GOV-PB · CÍCERO LUCENA (MDB, sq 150002544133) · Δ nível -0.84pp em 3 dias · z -3.6 · disparou: AtlasIntel · corroborou: Data Ranking/Fonte83 · hoje share 24.6% P(eleito) 0.0%
- PRES · RONALDO CAIADO (PSD, sq 280002551932) · Δ nível -0.16pp em 3 dias · z -3.7 · disparou: PoderData · corroborou: AtlasIntel, Palver, Quaest, Veritá · hoje share 3.5% P(eleito) 0.0%
- SEN-CE · GUILHERME THEOPHILO (NOVO, sq 60002539687) · Δ nível -0.03pp em 3 dias · z -4.2 · disparou: AtlasIntel/Focus · corroborou: Veritá · hoje share 1.9% P(eleito) 0.0%

### 2026-09-04 · cluster ±1 dia: 6 candidatos em 5 corridas {'GOV-PB': 1, 'SEN-PB': 1, 'GOV-MG': 1, 'PRES': 2, 'SEN-RN': 1}
- PRES · ESCRITOR AUGUSTO CURY (AVANTE, sq 280002551547) · Δ nível -0.17pp em 3 dias · z +6.1 · disparou: Veritá · corroborou: AtlasIntel, Futura, Nexus/BTG, Quaest, Real Time Big Data · hoje share 6.9% P(eleito) 0.0%
- PRES · RONALDO CAIADO (PSD, sq 280002551932) · Δ nível -0.13pp em 3 dias · z -3.2 · disparou: Veritá · corroborou: AtlasIntel, Palver, PoderData, Quaest · hoje share 3.5% P(eleito) 0.0%
- GOV-MG · MATEUS SIMÕES (PSD, sq 130002541911) · Δ nível +0.02pp em 3 dias · z -4.5 · disparou: AtlasIntel · corroborou: Datafolha · hoje share 8.0% P(eleito) 0.0%

### 2026-09-05 · cluster ±1 dia: 6 candidatos em 5 corridas {'GOV-PB': 1, 'SEN-PB': 1, 'GOV-MG': 1, 'PRES': 2, 'SEN-RN': 1}
- GOV-PB · LUCAS RIBEIRO (PP, sq 150002551789) · Δ nível +1.08pp em 3 dias · z +4.4 · disparou: Anova · corroborou: Data Ranking/Fonte83 · hoje share 52.9% P(eleito) 100.0%
- SEN-RN · SAMANDA DE LULA (PT, sq 200002533841) · Δ nível +0.47pp em 3 dias · z +3.2 · disparou: Seta · corroborou: Real Time Big Data · hoje share 14.5% P(eleito) 3.6%
- SEN-PB · DR. MARCELO QUEIROGA (PL, sq 150002538459) · Δ nível -0.08pp em 3 dias · z -3.3 · disparou: Anova · corroborou: TDL · hoje share 9.9% P(eleito) 0.3%

### 2026-09-07 · cluster ±1 dia: 5 candidatos em 4 corridas {'GOV-RJ': 1, 'GOV-PB': 2, 'GOV-TO': 1, 'PRES': 1}
- GOV-PB · LUCAS RIBEIRO (PP, sq 150002551789) · Δ nível +0.57pp em 3 dias · z +3.7 · disparou: Data Ranking/Fonte83 · corroborou: Anova · hoje share 52.9% P(eleito) 100.0%
- GOV-PB · CÍCERO LUCENA (MDB, sq 150002544133) · Δ nível -0.34pp em 3 dias · z -3.2 · disparou: Data Ranking/Fonte83 · corroborou: AtlasIntel · hoje share 24.6% P(eleito) 0.0%
- PRES · RONALDO CAIADO (PSD, sq 280002551932) · Δ nível -0.09pp em 3 dias · z -5.4 · disparou: Palver · corroborou: AtlasIntel, PoderData, Quaest, Veritá · hoje share 3.5% P(eleito) 0.0%
- GOV-RJ · ANDRÉ MARINHO (NOVO, sq 190002537524) · Δ nível -0.04pp em 3 dias · z -3.7 · disparou: Quaest · corroborou: Real Time Big Data · hoje share 2.0% P(eleito) 0.0%

### 2026-09-08 · cluster ±1 dia: 7 candidatos em 6 corridas {'GOV-RJ': 1, 'GOV-PB': 2, 'SEN-CE': 1, 'GOV-TO': 1, 'PRES': 1, 'SEN-RN': 1}
- GOV-TO · ATAIDES DE OLIVEIRA (NOVO, sq 270002548412) · Δ nível -0.09pp em 3 dias · z -3.6 · disparou: Correio do Povo · corroborou: Paraná Pesquisas · hoje share 5.6% P(eleito) 0.0%

### 2026-09-09 · cluster ±1 dia: 6 candidatos em 6 corridas {'GOV-MG': 1, 'GOV-TO': 1, 'SEN-CE': 1, 'GOV-SE': 1, 'PRES': 1, 'SEN-RN': 1}
- PRES · RONALDO CAIADO (PSD, sq 280002551932) · Δ nível -0.10pp em 3 dias · z -5.6 · disparou: AtlasIntel · corroborou: Palver, PoderData, Veritá · hoje share 3.5% P(eleito) 0.0%
- SEN-RN · SAMANDA DE LULA (PT, sq 200002533841) · Δ nível +0.06pp em 3 dias · z +3.7 · disparou: Real Time Big Data · corroborou: Seta · hoje share 14.5% P(eleito) 3.6%
- SEN-CE · GUILHERME THEOPHILO (NOVO, sq 60002539687) · Δ nível -0.05pp em 3 dias · z -4.1 · disparou: Veritá · corroborou: AtlasIntel/Focus · hoje share 1.9% P(eleito) 0.0%

### 2026-09-10 · cluster ±1 dia: 6 candidatos em 6 corridas {'GOV-DF': 1, 'GOV-MG': 1, 'SEN-CE': 1, 'GOV-SE': 1, 'PRES': 1, 'SEN-RN': 1}
- GOV-SE · RICARDO MARQUES (PL, sq 260002549466) · Δ nível -0.18pp em 3 dias · z -3.8 · disparou: IFP · corroborou: INOR, IPP · hoje share 7.4% P(eleito) 0.0%
- GOV-MG · MATEUS SIMÕES (PSD, sq 130002541911) · Δ nível -0.09pp em 3 dias · z -3.1 · disparou: Datafolha · corroborou: AtlasIntel, Veritá · hoje share 8.0% P(eleito) 0.0%

### 2026-09-11 · cluster ±1 dia: 5 candidatos em 4 corridas {'SEN-RJ': 1, 'GOV-DF': 1, 'GOV-MG': 2, 'GOV-SE': 1}
- GOV-DF · ARRUDA (PSD, sq 70002552586) · Δ nível -0.67pp em 3 dias · z -3.0 · disparou: Datafolha · corroborou: IGAPE · hoje share 23.0% P(eleito) 0.0%

### 2026-09-12 · cluster ±1 dia: 5 candidatos em 5 corridas {'SEN-RJ': 1, 'GOV-DF': 1, 'PRES': 1, 'GOV-SE': 1, 'GOV-MG': 1}
- SEN-RJ · CARLOS JORDY (PL, sq 190002542888) · Δ nível +0.77pp em 3 dias · z +3.3 · disparou: Real Time Big Data · corroborou: Veritá · hoje share 17.7% P(eleito) 45.0%
- GOV-DF · ARRUDA (PSD, sq 70002552586) · Δ nível -0.50pp em 3 dias · z -3.9 · disparou: IGAPE · corroborou: Datafolha · hoje share 23.0% P(eleito) 0.0%
- GOV-MG · GABRIEL (MDB, sq 130002549557) · Δ nível -0.19pp em 3 dias · z -4.2 · disparou: DataTempo, F5 · corroborou: DataTempo, F5, Veritá · hoje share 3.4% P(eleito) 0.0%
- GOV-SE · RICARDO MARQUES (PL, sq 260002549466) · Δ nível -0.11pp em 3 dias · z -3.9 · disparou: IPP · corroborou: IFP, INOR · hoje share 7.4% P(eleito) 0.0%

### 2026-09-13 · cluster ±1 dia: 6 candidatos em 6 corridas {'SEN-RJ': 1, 'GOV-DF': 1, 'PRES': 1, 'GOV-TO': 1, 'GOV-SE': 1, 'GOV-MG': 1}
- PRES · RENAN SANTOS (MISSÃO, sq 280002540694) · Δ nível -0.18pp em 3 dias · z -3.5 · disparou: Nexus/BTG · corroborou: Veritá · hoje share 4.7% P(eleito) 0.0%
- GOV-SE · RICARDO MARQUES (PL, sq 260002549466) · Δ nível -0.04pp em 3 dias · z -3.2 · disparou: INOR · corroborou: IFP, IPP · hoje share 7.4% P(eleito) 0.0%

### 2026-09-14 · cluster ±1 dia: 4 candidatos em 4 corridas {'SEN-GO': 1, 'PRES': 1, 'GOV-TO': 1, 'GOV-SE': 1}
- GOV-TO · ATAIDES DE OLIVEIRA (NOVO, sq 270002548412) · Δ nível -0.05pp em 3 dias · z -3.6 · disparou: Paraná Pesquisas · corroborou: Correio do Povo · hoje share 5.6% P(eleito) 0.0%

### 2026-09-15 · cluster ±1 dia: 4 candidatos em 3 corridas {'SEN-GO': 1, 'PRES': 2, 'GOV-TO': 1}
- SEN-GO · DR. ZACHARIAS CALIL (MDB, sq 90002546974) · Δ nível +0.80pp em 3 dias · z +3.2 · disparou: Goiás Pesquisas/Mais Goiás · corroborou: DataPop, Veritá · hoje share 16.9% P(eleito) 20.1%

## Já registrado (não duplicar)
- eventos.json: cury-viral-2026-08-26 (2026-08-26, denuncia, alvo [280002551547], direção +)
- hipoteses.json (de tendência, 25/09): h-2026-09-25-01 Cury devolve mais 1 pp até a urna; h-2026-09-25-02 Flávio sobe 1 pp no agregado até 04/10; h-2026-09-25-03 P(eleito) de Flávio segue subindo no 2º turno; h-2026-09-25-04 A próxima AtlasIntel derruba os nanicos no detector; h-2026-09-25-05 Lote da Veritá vira choque comum, com sinal negativo em 'outros'; h-2026-09-25-06 Kalil perde mais 1 pp em MG; h-2026-09-25-07 O choque de 17 a 19/09 persiste nos sete que caíram; h-2026-09-25-08 Calil sobe 1 pp com a chapa de Vilela em GO; h-2026-09-25-09 Jordy fecha o 1º turno como favorito à 2ª vaga no RJ; h-2026-09-25-10 Debate da Globo não rende inflexão positiva a Cury; h-2026-09-25-11 A urna dá a Flávio mais do que o agregado final; h-2026-09-25-12 A urna dá a Cury menos do que o agregado final

## Calendário
- 1º turno 2026-10-04 · 2º turno 2026-10-25 · debate Globo 01/10 (único restante do 1º turno, segundo a imprensa) · horário eleitoral desde 28/08 (não reconferido).
