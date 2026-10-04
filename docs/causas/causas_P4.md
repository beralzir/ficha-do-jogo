# Dossiê de causas · período P4: 2026-09-24 a 2026-10-04

Gerado em 2026-10-04 do dado publicado (inflexoes.json, as_of 2026-10-02). Detector M2 do Ficha do Jogo (bera.ia.br/ficha-do-jogo): |z|>3 no filtro de Kalman do competidor v2, corroborado por 2+ institutos, share>=2%. MAGNITUDE SUBESTIMADA POR CONSTRUÇÃO (passeio em logit calibrado a 50%): confie na DATA, desconfie do tamanho. Mesmo contrato dos P1 a P3 (25/09), com o tipo `candidatura` já aceito.

## CONTRATO DE SAÍDA (leia antes de tudo)

Tarefa: para cada DATA de inflexão do período, procurar na imprensa e em fontes primárias o que aconteceu no raio de 0 a 7 dias ANTES dela que possa ser causa candidata do movimento, e devolver EVENTOS no schema exato do registro do projeto, mais as três pernas de teste. Não é para confirmar causa: é para registrar causa candidata de forma testável. Data sem evento plausível: diga "sem evento plausível encontrado" e liste o que procurou. Além das datas, registre os eventos GRANDES de campanha do período nas corridas listadas (debates, decisões do TSE/TRE, denúncias, desistências, apoios formais) mesmo sem inflexão perto, marcando-os "sem inflexão associada".

Schema de evento (exato; o validador do projeto recusa fora disso):
{"id":"<slug>-<AAAA-MM-DD>","data":"AAAA-MM-DD","registrado_em":"2026-10-04","tipo":"debate|decisao_judicial|denuncia|peca_desinformacao|economico|pesquisa_bomba|candidatura","alvo":[sq,...],"direcao_esperada":"+|-|?","escopo":"nacional|UF","fonte":{"url":"...","veiculo":"...","acesso":"2026-10-04"},"notas":"..."}
- `alvo` só com sq da lista de candidatos abaixo (o candidato que o evento atinge, não quem se moveu por tabela).
- `direcao_esperada` é a direção que o MECANISMO prevê para o alvo; como você já viu o movimento, diga em `notas` se a direção foi escrita depois de olhar.
- Todo evento deste período nasce EXPLORATÓRIO (registrado_em 2026-10-04 > data). Não registre eventos futuros (2º turno): os finalistas só se conhecem depois da apuração.
- Regra de curadoria da casa (decisão do Bera, 25/09): só entra evento com FONTE ABERTA que você de fato abriu, número conferido ou tabela da Wikipédia. Evento só de manchete de feed vai para uma lista separada "pendentes, só manchete", fora do JSON. Nunca invente URL, número ou data.

Para cada evento, além do JSON, escreva:
1. Mecanismo, em 1 a 3 frases, cada uma marcada [fato] / [inferência] / [hipótese].
2. Implicações cruzadas: inflexões que ele poderia explicar (data, corrida, candidato) e as que ele NÃO explica (quem mais deveria ter se movido e não se moveu), conferíveis no dado.
3. Fonte com URL e data de acesso; se não conseguir abrir a fonte primária, diga "não confirmado".

Fontes de curadoria da casa: Agência Lupa, Aos Fatos, decisões do TSE/TRE (propaganda, representações, registros), agenda oficial de debates, imprensa nacional/regional com URL, Wikipédia PT (cite a revisão quando possível). Português do Brasil, sem travessão espaçado (" — "): vírgula, dois-pontos ou parênteses. Evite ponto e vírgula.

Saída: seções fixas, nesta ordem: (1) fontes abertas (URL, data); (2) tabela data -> evento(s) candidato(s) ou "sem evento plausível"; (3) bloco ```json (array) dos eventos; (4) para cada evento, os itens 1 a 3; (5) pendentes, só manchete; (6) o que não dá para afirmar.

## Datas de inflexão do período (9 datas, 30 destaques)

### 2026-09-24
- GOV-DF · LEANDRO GRASS (sq 70002552496) · Δ nível +1.04pp em 3 dias · z +4.4 · disparou: Veritá · corroborou: Correio/Opinião, IGAPE
- SEN-RN · RAFAEL MOTTA (sq 200002533843) · Δ nível +0.03pp em 3 dias · z -3.2 · disparou: Seta · corroborou: Média/O Potengi

### 2026-09-25
- PRES · ESCRITOR AUGUSTO CURY (sq 280002551547) · Δ nível -0.28pp em 3 dias · z -8.3 · disparou: Veritá · corroborou: AtlasIntel, Palver, PoderData, Vox Brasil
- PRES · RENAN SANTOS (sq 280002540694) · Δ nível +0.00pp em 3 dias · z -6.2 · disparou: Veritá · corroborou: AtlasIntel

### 2026-09-26
- GOV-DF · CELINA LEÃO (sq 70002553055) · Δ nível +1.91pp em 3 dias · z +3.3 · disparou: IGAPE · corroborou: Correio/Opinião, Real Time Big Data

### 2026-09-27
- GOV-AM · DAVID ALMEIDA (sq 40002536086) · Δ nível -0.41pp em 3 dias · z -3.4 · disparou: Viva Voz · corroborou: Real Time Big Data

### 2026-09-28
- GOV-DF · CELINA LEÃO (sq 70002553055) · Δ nível +1.10pp em 3 dias · z +4.2 · disparou: Correio/Opinião, Real Time Big Data · corroborou: Correio/Opinião, IGAPE, Real Time Big Data
- GOV-DF · LEANDRO GRASS (sq 70002552496) · Δ nível +0.46pp em 3 dias · z +3.0 · disparou: Correio/Opinião · corroborou: IGAPE, Veritá
- GOV-DF · PAULA BELMONTE (sq 70002552965) · Δ nível +0.23pp em 3 dias · z +3.3 · disparou: Correio/Opinião, Real Time Big Data · corroborou: Correio/Opinião, IGAPE, Real Time Big Data
- GOV-RJ · ANDRÉ MARINHO (sq 190002537524) · Δ nível -0.05pp em 3 dias · z -3.5 · disparou: Quaest · corroborou: Gerp
- PRES · ESCRITOR AUGUSTO CURY (sq 280002551547) · Δ nível -0.18pp em 3 dias · z -6.4 · disparou: AtlasIntel, Palver · corroborou: AtlasIntel, Palver, PoderData, Veritá, Vox Brasil
- PRES · RONALDO CAIADO (sq 280002551932) · Δ nível -0.03pp em 3 dias · z -4.2 · disparou: Palver · corroborou: AtlasIntel
- SEN-DF · SEBASTIÃO COELHO (sq 70002548624) · Δ nível -0.16pp em 3 dias · z -3.9 · disparou: Quaest, Real Time Big Data · corroborou: Exata GO, IGAPE
- SEN-MG · DOMINGOS SÁVIO (sq 130002551786) · Δ nível +0.36pp em 3 dias · z +3.4 · disparou: Quaest · corroborou: Real Time Big Data
- SEN-MG · MARCO ANTÔNIO SUPERMAN (sq 130002551284) · Δ nível +0.13pp em 3 dias · z +3.8 · disparou: Quaest · corroborou: Real Time Big Data
- SEN-RJ · WAGUINHO (sq 190002550182) · Δ nível -0.11pp em 3 dias · z -3.0 · disparou: Quaest · corroborou: Gerp, Real Time Big Data

### 2026-09-29
- GOV-DF · CELINA LEÃO (sq 70002553055) · Δ nível +0.59pp em 3 dias · z +3.2 · disparou: IGAPE · corroborou: Correio/Opinião, Real Time Big Data
- GOV-DF · LEANDRO GRASS (sq 70002552496) · Δ nível +0.21pp em 3 dias · z +3.0 · disparou: IGAPE · corroborou: Correio/Opinião, Veritá
- GOV-DF · PAULA BELMONTE (sq 70002552965) · Δ nível +0.11pp em 3 dias · z +4.0 · disparou: IGAPE · corroborou: Correio/Opinião, Real Time Big Data
- SEN-DF · SEBASTIÃO COELHO (sq 70002548624) · Δ nível -0.16pp em 3 dias · z -5.8 · disparou: IGAPE · corroborou: Exata GO, Quaest
- SEN-RJ · WAGUINHO (sq 190002550182) · Δ nível -0.06pp em 3 dias · z -3.4 · disparou: Real Time Big Data · corroborou: Gerp, Quaest
- SEN-RO · ACIR GURGACZ (sq 220002541490) · Δ nível -0.04pp em 3 dias · z -3.6 · disparou: Real Time Big Data · corroborou: Quaest

### 2026-09-30
- GOV-RJ · ANDRÉ MARINHO (sq 190002537524) · Δ nível -0.02pp em 3 dias · z -3.0 · disparou: Gerp · corroborou: Quaest
- SEN-RJ · WAGUINHO (sq 190002550182) · Δ nível -0.03pp em 3 dias · z -3.2 · disparou: Gerp · corroborou: Quaest, Real Time Big Data

### 2026-10-01
- GOV-AM · DAVID ALMEIDA (sq 40002536086) · Δ nível -0.08pp em 3 dias · z -4.0 · disparou: Real Time Big Data · corroborou: Viva Voz
- PRES · ESCRITOR AUGUSTO CURY (sq 280002551547) · Δ nível -0.06pp em 3 dias · z -4.2 · disparou: Vox Brasil · corroborou: AtlasIntel, Palver, PoderData, Veritá

### 2026-10-02
- PRES · ESCRITOR AUGUSTO CURY (sq 280002551547) · Δ nível -0.02pp em 3 dias · z -5.1 · disparou: PoderData · corroborou: AtlasIntel, Palver, Veritá, Vox Brasil
- SEN-DF · SEBASTIÃO COELHO (sq 70002548624) · Δ nível -0.03pp em 3 dias · z -5.5 · disparou: Exata GO · corroborou: IGAPE, Quaest
- SEN-MG · DOMINGOS SÁVIO (sq 130002551786) · Δ nível +0.10pp em 3 dias · z +3.3 · disparou: Real Time Big Data · corroborou: Quaest
- SEN-MG · MARCO ANTÔNIO SUPERMAN (sq 130002551284) · Δ nível +0.03pp em 3 dias · z +5.0 · disparou: Real Time Big Data · corroborou: Quaest

## Candidatos das corridas do período (use estes sq no `alvo`)

- **GOV-AM**: GILBERTO VASCONCELOS (PSTU, sq 40002535267); ISAEL MUNDURUKU (REDE, sq 40002550776); PROFESSORA MARIA DO CARMO (PL, sq 40002541626); CABO DACIOLO (MOBILIZA, sq 40002551740); ROBERTO CIDADE (UNIÃO, sq 40002541741); OMAR AZIZ (PSD, sq 40002532272); DAVID ALMEIDA (AVANTE, sq 40002536086)
- **GOV-DF**: CELINA LEÃO (PP, sq 70002553055); LEANDRO GRASS (PT, sq 70002552496); PROFESSOR ROBSON (PSTU, sq 70002535930); RICO PINHEIRO (PRTB, sq 70002553982); EXPEDITO MENDONÇA (PCO, sq 70002552341); KIKO CAPUTO (NOVO, sq 70002547775); ELISSON (AGIR, sq 70002551298); CAPPELLI (PSB, sq 70002551557); PAULA BELMONTE (PSDB, sq 70002552965); PROFESSORA SAMARA MINEIRO (UP, sq 70002537111)
- **GOV-RJ**: GAROTINHO (REPUBLICANOS, sq 190002550196); CORONEL BUSNELLO (MISSÃO, sq 190002544120); CYRO GARCIA (PSTU, sq 190002540198); DOUGLAS RUAS (PL, sq 190002542887); LUAN MONTEIRO (PCO, sq 190002552513); ANDRÉ MARINHO (NOVO, sq 190002537524); WILLIAM SIRI (PSOL, sq 190002536162); EDUARDO PAES (PSD, sq 190002543380); JULIETE (UP, sq 190002547272)
- **PRES**: LULA (PT, sq 280002542548); RENAN SANTOS (MISSÃO, sq 280002540694); HERTZ DIAS (PSTU, sq 280002541457); EDMILSON COSTA (PCB, sq 280002551975); FLAVIO BOLSONARO (PL, sq 280002551544); CLARIANA BARAO (DC, sq 280002552484); RUI COSTA PIMENTA (PCO, sq 280002552487); ZEMA (NOVO, sq 280002539826); VETERINÁRIO WILSON GRASSI (DEMOCRATA, sq 280002548139); RONALDO CAIADO (PSD, sq 280002551932); ESCRITOR AUGUSTO CURY (AVANTE, sq 280002551547); SAMARA (UP, sq 280002538811)
- **SEN-DF**: LEILA DO VÔLEI (PDT, sq 70002552492); ERIKA KOKAY (PT, sq 70002552490); ZANATA (PSTU, sq 70002536445); MICHELLE BOLSONARO (PL, sq 70002552936); BIA KICIS (PL, sq 70002552934); DAVID HORN (PCO, sq 70002551426); SEBASTIÃO COELHO (NOVO, sq 70002548624); TIAGO (AGIR, sq 70002551323); GUTO FELÍCIO DOS SANTOS (PSDB, sq 70002553296); MARLEY (AVANTE, sq 70002552582); PROFESSOR GUILHERME AMORIM (UP, sq 70002537112)
- **SEN-MG**: MARCELO ARO (PP, sq 130002548381); MARÍLIA CAMPOS (PT, sq 130002550560); MANOEL CARVALHO (MDB, sq 130002552299); ARCANJO PIMENTA (MDB, sq 130002552302); JORDANO METALÚRGICO (PSTU, sq 130002551929); VICTÓRIA MELLO VIC (PSTU, sq 130002551930); DOMINGOS SÁVIO (PL, sq 130002551786); JUÍZ RAMON MOREIRA (DC, sq 130002551265); TIÃO PESSOA (PCO, sq 130002552311); MARCO ANTÔNIO SUPERMAN (NOVO, sq 130002551284); AÉCIO NEVES (PSDB, sq 130002554332); ÁUREA CAROLINA (PSOL, sq 130002550557); CARLOS VIANA (PSD, sq 130002545590); CARLIN MOURA (AVANTE, sq 130002552186); FIDÉLIS ALCÂNTARA (UP, sq 130002547882); ANA LUIZA DO MLB (UP, sq 130002547884)
- **SEN-RJ**: MARCELO CRIVELLA (REPUBLICANOS, sq 190002550184); WAGUINHO (REPUBLICANOS, sq 190002550182); BENEDITA DA SILVA (PT, sq 190002548141); HELIO SECCO (MISSÃO, sq 190002543961); PAULA FALCÃO (PSTU, sq 190002539827); MARCOS DIAS (PODE, sq 190002545553); CARLOS JORDY (PL, sq 190002542888); CARLOS PORTINHO (PL, sq 190002535142); LUCIANO MATTOS (PRTB, sq 190002552083); LUIZ EUGENIO (PCO, sq 190002552521); Ó CLEMENTE (DEMOCRATA, sq 190002550190); MONICA BENICIO (PSOL, sq 190002536164); PEDRO PAULO (PSD, sq 190002548145); MICHELLY XAVIER (UP, sq 190002548589); VINICIUS BENEVIDES (UP, sq 190002548590)
- **SEN-RN**: RAFAEL MOTTA (PDT, sq 200002533843); SAMANDA DE LULA (PT, sq 200002533841); LUCIANA MANDU (PSTU, sq 200002542484); ROSÁLIA FERNANDES (PSTU, sq 200002542483); STYVENSON VALENTIM (PODE, sq 200002534448); CORONEL HÉLIO (PL, sq 200002534447); GARI WENDELL BATISTA (AGIR, sq 200002549133); CLÓVIS COSTA DO COLETIVO NÓS (AGIR, sq 200002548115); TÉRCIO TINÔCO (UNIÃO, sq 200002535511); SANDRO PIMENTEL (PSOL, sq 200002546792); SONIA GODEIRO (PSOL, sq 200002546795); ZENAIDE MAIA (PSD, sq 200002535507); PROFESSOR GUILHERME (UP, sq 200002550541)
- **SEN-RO**: MARIANA CARVALHO (REPUBLICANOS, sq 220002547310); SÍLVIA CRISTINA (PP, sq 220002547309); ACIR GURGACZ (PDT, sq 220002541490); LUCIANA OLIVEIRA (PT, sq 220002551948); ENGENHEIRO THULIO (MISSÃO, sq 220002541944); DR. FERNANDO MÁXIMO (PL, sq 220002539996); BRUNO SCHEID (PL, sq 220002539995); NEIDINHA (PSB, sq 220002550928); AIRES MOTA (PV, sq 220002551946); LUIS FERNANDO (PSD, sq 220002539771)

## Já registrado no eventos.json (não duplicar)

- canella-desiste-senado-rj-2026-08-03 (2026-08-03, candidatura, alvo [190002550182, 190002550184], direção ?)
- convencao-avante-cury-2026-08-03 (2026-08-03, candidatura, alvo [280002551547], direção +)
- jordy-confirmado-pl-senado-rj-2026-08-04 (2026-08-04, candidatura, alvo [190002550184, 190002550182, 190002535142], direção -)
- debate-band-2026-08-23 (2026-08-23, debate, alvo [280002551547, 280002540694], direção +)
- cury-viral-2026-08-26 (2026-08-26, denuncia, alvo [280002551547], direção +)
- debate-redeita-gov-pb-2026-08-26 (2026-08-26, debate, alvo [150002544133], direção +)
- pesquisa-bomba-cury-2026-08-30 (2026-08-30, pesquisa_bomba, alvo [280002551547], direção +)
- debate-arapuan-sen-pb-2026-08-31 (2026-08-31, debate, alvo [150002538459], direção +)
- renan-restricao-toffoli-2026-08-31 (2026-08-31, decisao_judicial, alvo [280002540694], direção -)
- quaest-caiado-1pct-2026-09-01 (2026-09-01, pesquisa_bomba, alvo [280002551932], direção -)
- debate-tmc-tvsim-gov-mg-2026-09-02 (2026-09-02, debate, alvo [130002549557], direção +)
- consorcio-cancela-debate-2026-09-08 (2026-09-08, debate, alvo [280002551547, 280002540694, 280002551932], direção -)
- marcal-tse-cassa-registro-2026-09-11 (2026-09-11, decisao_judicial, alvo [280002553884], direção -)
- quaest-cury-7pct-2026-09-14 (2026-09-14, pesquisa_bomba, alvo [280002551547], direção -)
- debate-inteligencia-metropoles-2026-09-18 (2026-09-18, debate, alvo [280002551547], direção +)
- datapop-calil-2a-vaga-2026-09-22 (2026-09-22, pesquisa_bomba, alvo [90002546974], direção +)
- debate-record-cancelado-2026-09-23 (2026-09-23, debate, alvo [280002551547, 280002551932, 280002540694], direção -)
- arruda-tse-confirma-indeferimento-2026-09-24 (2026-09-24, decisao_judicial, alvo [70002552586], direção -)
- debate-cabobranco-gov-pb-2026-09-29 (2026-09-29, debate, alvo [150002544133], direção +)
- debate-globo-gov-mg-2026-09-29 (2026-09-29, debate, alvo [130002541911, 130002549557], direção +)
- debate-globo-pres-2026-10-01 (2026-10-01, debate, alvo [280002551547, 280002551932], direção -)

Atenção especial: três eventos de agenda foram PRÉ-ESPECIFICADOS em 25/09 e precisam do DESFECHO conferido em fonte (não crie evento novo para eles, só relate na seção 2): debate-globo-pres-2026-10-01 (quem compareceu: Lula? Flávio? Cury? Caiado? Zema? Renan?), debate-globo-gov-mg-2026-09-29 (Simões e Gabriel foram convidados e foram?), debate-cabobranco-gov-pb-2026-09-29 (Cícero foi convidado e foi?). A presença decide qual ramo das hipóteses h-2026-09-25-13/14 fica testável.

## Calendário
- 1º turno 2026-10-04 (hoje) · 2º turno 2026-10-25. Pesquisa eleitoral pode ser divulgada até a véspera.
