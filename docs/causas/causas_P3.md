# Dossiê de causas · período P3: 2026-09-16 a 2026-09-24

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

## Datas de inflexão do período (7 datas, 23 destaques)

### 2026-09-16 · cluster ±1 dia: 6 candidatos em 3 corridas {'GOV-MG': 3, 'PRES': 2, 'SEN-GO': 1}
- PRES · ESCRITOR AUGUSTO CURY (AVANTE, sq 280002551547) · Δ nível -0.67pp em 3 dias · z -4.3 · disparou: AtlasIntel · corroborou: Palver, Veritá · hoje share 6.9% P(eleito) 0.0%
- PRES · RONALDO CAIADO (PSD, sq 280002551932) · Δ nível -0.18pp em 3 dias · z -3.5 · disparou: AtlasIntel · corroborou: Palver, Veritá · hoje share 3.5% P(eleito) 0.0%

### 2026-09-17 · cluster ±1 dia: 8 candidatos em 4 corridas {'SEN-RJ': 1, 'GOV-MG': 3, 'PRES': 3, 'SEN-GO': 1}
- GOV-MG · ALEXANDRE KALIL (PDT, sq 130002539775) · Δ nível -0.42pp em 3 dias · z -3.1 · disparou: Veritá · corroborou: AtlasIntel · hoje share 11.2% P(eleito) 0.0%
- SEN-GO · DR. ZACHARIAS CALIL (MDB, sq 90002546974) · Δ nível +0.30pp em 3 dias · z +6.7 · disparou: Veritá · corroborou: DataPop, Goiás Pesquisas/Mais Goiás · hoje share 16.9% P(eleito) 20.1%
- GOV-MG · MATEUS SIMÕES (PSD, sq 130002541911) · Δ nível -0.12pp em 3 dias · z -5.6 · disparou: Veritá · corroborou: Datafolha · hoje share 8.0% P(eleito) 0.0%
- GOV-MG · GABRIEL (MDB, sq 130002549557) · Δ nível -0.11pp em 3 dias · z -5.1 · disparou: Veritá · corroborou: DataTempo, F5 · hoje share 3.4% P(eleito) 0.0%

### 2026-09-18 · cluster ±1 dia: 9 candidatos em 5 corridas {'SEN-RJ': 1, 'GOV-MG': 3, 'PRES': 3, 'SEN-GO': 1, 'SEN-DF': 1}
- PRES · ESCRITOR AUGUSTO CURY (AVANTE, sq 280002551547) · Δ nível -0.39pp em 3 dias · z -7.4 · disparou: Palver · corroborou: AtlasIntel, Veritá · hoje share 6.9% P(eleito) 0.0%
- PRES · RENAN SANTOS (MISSÃO, sq 280002540694) · Δ nível -0.11pp em 3 dias · z +4.2 · disparou: Palver · corroborou: Real Time Big Data · hoje share 4.7% P(eleito) 0.0%
- SEN-RJ · CARLOS JORDY (PL, sq 190002542888) · Δ nível +0.10pp em 3 dias · z +6.5 · disparou: Veritá · corroborou: Real Time Big Data · hoje share 17.7% P(eleito) 45.0%
- PRES · RONALDO CAIADO (PSD, sq 280002551932) · Δ nível -0.05pp em 3 dias · z -5.2 · disparou: Palver · corroborou: AtlasIntel, Veritá · hoje share 3.5% P(eleito) 0.0%

### 2026-09-19 · cluster ±1 dia: 7 candidatos em 5 corridas {'SEN-RJ': 1, 'PRES': 3, 'SEN-GO': 1, 'SEN-DF': 1, 'GOV-MG': 1}
- PRES · ESCRITOR AUGUSTO CURY (AVANTE, sq 280002551547) · Δ nível -0.26pp em 3 dias · z -6.6 · disparou: Veritá · corroborou: AtlasIntel, Palver · hoje share 6.9% P(eleito) 0.0%
- PRES · RENAN SANTOS (MISSÃO, sq 280002540694) · Δ nível -0.11pp em 3 dias · z -4.8 · disparou: Veritá · corroborou: AtlasIntel, Nexus/BTG · hoje share 4.7% P(eleito) 0.0%
- SEN-GO · DR. ZACHARIAS CALIL (MDB, sq 90002546974) · Δ nível -0.08pp em 3 dias · z +3.6 · disparou: DataPop · corroborou: Goiás Pesquisas/Mais Goiás, Veritá · hoje share 16.9% P(eleito) 20.1%
- SEN-DF · SEBASTIÃO COELHO (NOVO, sq 70002548624) · Δ nível -0.08pp em 3 dias · z -3.1 · disparou: Correio/Opinião · corroborou: Quaest · hoje share 4.8% P(eleito) 0.0%
- PRES · RONALDO CAIADO (PSD, sq 280002551932) · Δ nível -0.00pp em 3 dias · z -6.1 · disparou: Veritá · corroborou: AtlasIntel, Palver · hoje share 3.5% P(eleito) 0.0%

### 2026-09-20 · cluster ±1 dia: 6 candidatos em 4 corridas {'PRES': 3, 'SEN-DF': 1, 'GOV-MG': 1, 'SEN-GO': 1}
- GOV-MG · ALEXANDRE KALIL (PDT, sq 130002539775) · Δ nível -0.14pp em 3 dias · z -3.6 · disparou: AtlasIntel · corroborou: Veritá · hoje share 11.2% P(eleito) 0.0%

### 2026-09-22 · cluster ±1 dia: 4 candidatos em 2 corridas {'PRES': 3, 'SEN-DF': 1}
- PRES · ESCRITOR AUGUSTO CURY (AVANTE, sq 280002551547) · Δ nível -0.07pp em 3 dias · z -5.5 · disparou: AtlasIntel · corroborou: Palver, Veritá · hoje share 6.9% P(eleito) 0.0%
- SEN-DF · SEBASTIÃO COELHO (NOVO, sq 70002548624) · Δ nível -0.04pp em 3 dias · z -3.1 · disparou: Quaest · corroborou: Correio/Opinião · hoje share 4.8% P(eleito) 0.0%
- PRES · RONALDO CAIADO (PSD, sq 280002551932) · Δ nível +0.02pp em 3 dias · z -3.8 · disparou: AtlasIntel · corroborou: Palver, Veritá · hoje share 3.5% P(eleito) 0.0%
- PRES · RENAN SANTOS (MISSÃO, sq 280002540694) · Δ nível -0.01pp em 3 dias · z -3.0 · disparou: AtlasIntel · corroborou: Veritá · hoje share 4.7% P(eleito) 0.0%

### 2026-09-23 · cluster ±1 dia: 4 candidatos em 2 corridas {'PRES': 3, 'SEN-DF': 1}
- PRES · ESCRITOR AUGUSTO CURY (AVANTE, sq 280002551547) · Δ nível -0.02pp em 3 dias · z -4.4 · disparou: Palver · corroborou: AtlasIntel, Veritá · hoje share 6.9% P(eleito) 0.0%
- PRES · RONALDO CAIADO (PSD, sq 280002551932) · Δ nível +0.02pp em 3 dias · z -3.7 · disparou: Futura, Palver · corroborou: AtlasIntel, Veritá · hoje share 3.5% P(eleito) 0.0%
- PRES · RENAN SANTOS (MISSÃO, sq 280002540694) · Δ nível +0.00pp em 3 dias · z +3.8 · disparou: Real Time Big Data · corroborou: Palver · hoje share 4.7% P(eleito) 0.0%

## Já registrado (não duplicar)
- eventos.json: cury-viral-2026-08-26 (2026-08-26, denuncia, alvo [280002551547], direção +)
- hipoteses.json (de tendência, 25/09): h-2026-09-25-01 Cury devolve mais 1 pp até a urna; h-2026-09-25-02 Flávio sobe 1 pp no agregado até 04/10; h-2026-09-25-03 P(eleito) de Flávio segue subindo no 2º turno; h-2026-09-25-04 A próxima AtlasIntel derruba os nanicos no detector; h-2026-09-25-05 Lote da Veritá vira choque comum, com sinal negativo em 'outros'; h-2026-09-25-06 Kalil perde mais 1 pp em MG; h-2026-09-25-07 O choque de 17 a 19/09 persiste nos sete que caíram; h-2026-09-25-08 Calil sobe 1 pp com a chapa de Vilela em GO; h-2026-09-25-09 Jordy fecha o 1º turno como favorito à 2ª vaga no RJ; h-2026-09-25-10 Debate da Globo não rende inflexão positiva a Cury; h-2026-09-25-11 A urna dá a Flávio mais do que o agregado final; h-2026-09-25-12 A urna dá a Cury menos do que o agregado final

## Calendário
- 1º turno 2026-10-04 · 2º turno 2026-10-25 · debate Globo 01/10 (único restante do 1º turno, segundo a imprensa) · horário eleitoral desde 28/08 (não reconferido).
