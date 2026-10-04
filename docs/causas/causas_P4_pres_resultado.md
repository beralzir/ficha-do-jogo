# Cruzamento com notícias · P4 (24/09 a 04/10/2026) · corrida PRES · resultado

Gerado em 2026-10-04 (dia do 1º turno) a partir do dossiê `causas_P4.md`, do dado local (`data/eleicoes/inflexoes.json` as_of 2026-10-02, `data/live/polls.json`, `data/eleicoes/eventos.json`, `data/eleicoes/hipoteses.json`) e de buscas e acessos web em português. Escopo: SÓ a corrida presidencial (escopo nacional). As corridas estaduais (GOV-AM, GOV-DF, GOV-RJ, SEN-*) ficam com o outro agente. Nada no repositório foi modificado além deste arquivo.

Regra seguida: só entra no JSON evento cuja matéria foi de fato aberta (WebFetch com sucesso). Manchete de feed (Google Notícias RSS) sem matéria aberta vai para a seção 5. O conhecimento interno do modelo vai até junho de 2026: todo fato datado de setembro e outubro abaixo vem das fontes listadas na seção 1.

**Achado principal: o debate da Globo de 01/10 NÃO aconteceu.** Lula recusou o convite em 30/09, Flávio Bolsonaro desistiu na noite de 01/10 e a Globo cancelou o debate minutos antes do horário, alegando insegurança jurídica depois de duas decisões judiciais no mesmo dia (TSE, ministra Estela Aranha, e STF, ministro Gilmar Mendes). Detalhes e fontes na seção 2a.

---

## 1. Fontes abertas (URL, data de publicação, acesso em 2026-10-04)

### Locais (só leitura)
- `data/eleicoes/inflexoes.json` (as_of 2026-10-02): destaques PRES de 18/09 a 02/10, z, disparador e corroboração.
- `data/live/polls.json`: séries por instituto de Lula, Flávio, Cury, Caiado, Renan e Zema desde 10/09, com campo_ini e campo_fim (usadas para saber que eventos caem dentro do campo de cada pesquisa disparadora).
- `data/eleicoes/eventos.json` e `data/eleicoes/hipoteses.json` (h-2026-09-25-13 e 14).
- `docs/causas/causas_P3_resultado.md` e `causas_sintese.json` (eventos de 18 a 24/09 já propostos em P3).

### Web, matérias abertas com sucesso
| # | Veículo e URL | Publicação | Uso |
|---|---|---|---|
| A1 | Poder360, https://www.poder360.com.br/poder-eleicoes-2026/lula-confirma-que-nao-ira-ao-debate-da-tv-globo/ | 30/09, 14h46 | Lula informa à Globo que não vai. Confirmados: Cury, Flávio, Caiado, Zema |
| A2 | Diário do Nordeste, https://diariodonordeste.verdesmares.com.br/pontopoder/lula-nao-participara-de-debate-da-tv-globo-nesta-quinta-feira-1-1.3795139 | 30/09, 14h57 | Idem, Lula no Flow no mesmo horário |
| A3 | Gazeta do Povo, https://www.gazetadopovo.com.br/eleicoes/2026/saiba-quem-confirmou-presenca-no-debate-da-globo/ | 30/09, 15h30 | Flávio confirma ("Vamos no debate da Globo"), Zema incluído por Nunes Marques |
| A4 | Congresso em Foco, https://www.congressoemfoco.com.br/noticia/122773/missao-aciona-tse-para-pedir-participacao-de-renan-no-debate-da-globo | 30/09, 16h55 | Missão pede ao TSE inclusão de Renan, relator Nunes Marques |
| A5 | Poder360, https://www.poder360.com.br/poder-eleicoes-2026/debate-presidencial-da-globo-sera-nesta-5a-leia-regras-e-quem-vai/ | 01/10, 13h59 | Regras, 4 confirmados, Nunes Marques nega Renan, Cármen Lúcia rejeita recurso no STF |
| A6 | Metrópoles (Igor Gadelha), https://www.metropoles.com/colunas/igor-gadelha/tse-decide-que-globo-nao-podera-exibir-pulpito-vazio-de-lula-em-debate | 01/10, 18h15 | Estela Aranha (TSE), a pedido do PT, proíbe púlpito vazio de Lula e perguntas ao ausente |
| A7 | CNN Brasil, https://www.cnnbrasil.com.br/eleicoes/flavio-bolsonaro-diz-que-nao-ira-mais-para-debate-da-tv-globo/ | 01/10, 19h26 (atualizada 21h31) | Flávio desiste, "em função da censura imposta ao evento pelo TSE". Renan incluído por Gilmar |
| A8 | CartaCapital, https://www.cartacapital.com.br/politica/gilmar-mendes-manda-globo-incluir-renan-santos-em-debate/ | 01/10, 20h00 | Liminar de Gilmar Mendes incluindo Renan (fundamentos) |
| A9 | Exame, https://exame.com/brasil/sem-lula-e-flavio-e-com-renan-entenda-quem-vai-participar-do-debate-da-globo/ | 01/10, 20h19 | Debate ainda previsto com Cury, Caiado, Zema e Renan |
| A10 | O Tempo, https://www.otempo.com.br/eleicoes/2026/presidentes/2026/10/1/tv-globo-cancela-debate | 01/10, 20h44 | Globo cancela. Nota: "sucessivas decisões judiciais tomadas momentos antes da realização do debate causam insegurança jurídica" |
| A11 | Agência Lupa, https://www.agencialupa.org/checagem/2026/10/01/ao-vivo-checagem-da-live-de-flavio-bolsonaro/ | 01/10, 22h10 (atualizada 02/10, 01h32) | Checagem da live de Flávio no horário do debate (15 alegações, várias falsas) |
| A12 | Poder360, https://www.poder360.com.br/poder-eleicoes-2026/renan-zema-caiado-e-cury-criticam-cancelamento-de-debate-da-globo/ | 02/10, 07h00 | Confirma o cancelamento e reações de Renan, Zema, Caiado e Cury |
| A13 | Gazeta do Povo, https://www.gazetadopovo.com.br/eleicoes/2026/perfil-estela-aranha-ministra-tse-que-provocou-cancelamento-debate-globo/ | 02/10, 12h56 | Liminar de Estela Aranha "a pedido da coligação de Lula" |
| A14 | O Liberal, https://www.oliberal.com/eleicoes/tse-manda-incluir-zema-e-candidatos-do-novo-nos-debates-eleitorais-1.1174895 | 29/09, 19h47 | Nunes Marques, a pedido do Novo, manda incluir candidatos do Novo nos debates (bancada atual de 5 deputados) |
| A15 | iMirante, https://m.imirante.com/noticias/brasil/2026/09/29/ipolitica-nunes-marques-determina-inclusao-de-candidatos-em-debates | 29/09, 19h18 | Mesma decisão. A extração trouxe nomes inconsistentes (ver seção 6), usado só para a data |
| A16 | Times Brasil, https://timesbrasil.com.br/brasil/decisao-2026-lula-eleva-tom-de-ataques-a-rival-e-flavio-recebe-apoio-de-marcal-veja-o-dia-dos-candidatos-ao-planalto/ | 29/09 | Resumo do dia: Marçal com Flávio, Cury admite "perdão presidencial para todos" (sabatina RedeTV!), Caiado "Eu não recuo", Zema "Irei até o último minuto" |
| A17 | O Hoje, https://ohoje.com/2026/09/29/flavio-bolsonaro-anuncia-pablo-marcal-como-novo-colaborador-da-campanha/ | 29/09, 21h59 | Marçal com Flávio em SP, 29/09 |
| A18 | Correio da Manhã, https://www.correiodamanha.com.br/politica/2026/09/323307-pablo-marcal-anuncia-apoio-e-entra-na-campanha-de-flavio-bolsonaro.html | 30/09, 11h49 | Idem, com frases de Marçal e o indeferimento do registro dele |
| A19 | Seu Dinheiro, https://www.seudinheiro.com/2026/politica/desistencia-no-senado-de-sp-reconfigura-aliancas-a-menos-de-uma-semana-do-1o-turno-confira-o-dia-na-politica-ccgg/ | 28/09 | Salles desiste do Senado-SP, Tarcísio pede "gestos de união" a Zema e Caiado, AIJE de Flávio contra Lula |
| A20 | O Hoje, https://ohoje.com/2026/09/28/romeu-zema-avalia-desistir-da-disputa-presidencial-a-poucos-dias-da-eleicao/ | 28/09, 16h47 | Zema avalia desistir (pesquisas internas abaixo de 5%), pressão do Novo |
| A21 | Tribuna do Planalto, https://tribunadoplanalto.com.br/caiado-descarta-desistencia-para-apoiar-flavio-bolsonaro-eu-nao-recuo/ | 29/09, 16h09 | Caiado, noite de 28/09, a O Popular: "Eu não recuo em nada na minha vida" |
| A22 | Money Times, https://www.moneytimes.com.br/pesquisa-datafolha-24-de-setembro-gaep/ | 24/09, 19h01 | Datafolha 22 a 24/09 (BR-00304/2026): 1º e 2º turno |
| A23 | Diario de Pernambuco, https://www.diariodepernambuco.com.br/politica/2026/09/11724944-augusto-cury-diz-que-pesquisas-sao-enviesadas-e-que-eleitores-podem-ter-surpresa.html | 25/09, 17h13 | Cury reage ao Datafolha: "pesquisas enviesadas" |
| A24 | Portal de Prefeitura, https://portaldeprefeitura.com.br/bastidores-da-politica/pesquisa-quaest-lula-tem-39-e-flavio-bolsonaro-34-no-1o-turno/632993/ | 28/09, 10h39 | Quaest 24 a 27/09 (BR-06520/2026, Globo): Cury 4, Caiado 4, 2º turno 42 a 42 |
| A25 | Agência Lupa, https://www.agencialupa.org/eleicoes/2026/09/29/lula-nao-defendeu-nem-normalizou-a-pedofilia-em-discurso-no-para/ | 29/09 | Corte de discurso de Lula em Belém (28/09), FALSO |
| A26 | Agência Lupa, https://www.agencialupa.org/verificacao/2026/10/03/e-falso-o-video-que-usa-imagem-de-william-waack-para-sugerir-que-pt-nao-aceitara-derrota-nas-urnas-post-e-deepfake/ | 03/10, 17h52 | Deepfake com William Waack contra o PT, FALSO |
| A27 | Agência Lupa, https://www.agencialupa.org/checagem/ | listagem | Checagens do período: entrevista de Lula no Flow (01/10), live de Flávio (01/10), debate no Flow (21/09) |

### Abertas mas sem uso (fora do período ou inválidas)
- Lupa, Lente nas Eleições #8 (agencialupa.substack.com/p/13512680_lente-nas-elei-es-8): é de 2022, descartada.
- Wikipédia PT, Eleição presidencial no Brasil em 2026: a extração não trouxe a seção de debates (texto truncado). Não usada.
- SBT News (Toffoli libera campanha de Renan, 01/09), DGABC 4344286 (31/08) e 4344133 (30/08), Money Times sobre Renan (junho): fora do período, já cobertos por `renan-restricao-toffoli-2026-08-31`.

### Falharam (403, não abertas)
- Revista Oeste, "Augusto Cury também desiste de participar do debate" (data e debate não confirmados).
- Jornal Opção, Quaest 28/09, e Jornal Opção, "Marçal pode estar por trás do crescimento de Cury".

### Feeds de manchetes (Google Notícias RSS, não são matérias abertas)
- `"Augusto Cury"` de 23/09 a 04/10 (54 manchetes), `Caiado presidente` de 20/09 a 04/10 (50), `"Renan Santos"` de 17/09 a 04/10 (cerca de 60), `Tarcísio Flávio primeiro turno Caiado Zema desistir` de 20/09 a 02/10 (17). URLs no formato `https://news.google.com/rss/search?q=...&hl=pt-BR&gl=BR&ceid=BR%3Apt-419`.

---

## 2. Tabela data → evento(s) candidato(s)

Convenção: o raio é de 0 a 7 dias antes da data. "Campo" é o período de campo da pesquisa disparadora em `polls.json`: um evento só pode explicar a data se cair dentro ou antes do campo.

| Data | Destaque (PRES) | Disparador · campo · lote | Evento(s) candidato(s) no raio | Leitura |
|---|---|---|---|---|
| **25/09** | Cury, Δ −0,28 pp, z −8,3 | Veritá, campo 20 a 25/09, lote de 5 corridas (GOV-RO, GOV-TO, PRES, SEN-RO, SEN-TO). Veritá: Cury 5,4 (19/09) → 4,2 (25/09) | (a) `datafolha-empate-2t-2026-09-24` (novo, só o último dia do campo). (b) Já propostos em P3 e fora do `eventos.json` (não re-registrados aqui para não duplicar a proposta): `debate-flow-2026-09-21`, `folha-empresa-filha-cury-2026-09-22`, `nexus-btg-caiado-empate-2t-2026-09-21`. Contexto de P3: morte do conselheiro de campanha de Cury e suspensão de agenda (22/09) | Queda real e lenta de Cury em todas as casas (seção 6), sem salto datável. A data é da chegada do lote Veritá. Evento novo de força: nenhum dentro do campo |
| **25/09** | Renan, Δ 0,00 pp, z −6,2 | Veritá, mesmo lote. Veritá: Renan 2,9 → 2,3 | **Sem evento plausível encontrado.** Procurado: feed "Renan Santos" de 17/09 a 04/10. Entre 18 e 25/09 só há a ação de Renan no TSE contra o reajuste do Bolsa Família (17/09, manchete G1, já em P3) e proposta de cortes na Previdência (19/09, Agência Brasil, manchete) | Efeito-casa: Veritá dá Renan 2,3, Palver dá 8 e AtlasIntel 4,5 a 5,2. Δ nulo, não é inflexão de nível |
| **28/09** | Cury, Δ −0,18 pp, z −6,4 | AtlasIntel (campo 23 a 28/09, lote de 8) e Palver (24 a 28/09, só PRES). Corroboram Vox Brasil (26 a 28/09), PoderData, Veritá | (a) `datafolha-empate-2t-2026-09-24` (dentro do raio e antes do campo). (b) Quaest de 28/09 (Cury 6 → 4, 2º turno 42 a 42), publicada no último dia de campo, contexto. (c) `tarcisio-uniao-direita-2026-09-28`, tarde de 28/09, último dia de campo, alvo direto Zema e Caiado, não Cury | Narrativa de "empate técnico" entre os líderes e de união da direita no 1º turno: mecanismo de voto útil, compatível com a direção. A data, porém, coincide com chegada de lotes de casas de indecisos baixos (AtlasIntel 2,1, Palver 2) |
| **28/09** | Caiado, Δ −0,03 pp, z −4,2 | Palver (24 a 28/09), corrobora AtlasIntel | `tarcisio-uniao-direita-2026-09-28` (mesmo dia, depois de quase todo o campo). `datafolha-empate-2t-2026-09-24` | Δ quase nulo. Palver dá Caiado 1, AtlasIntel 1,8 contra 3 a 5 nas outras casas: resíduo de casa. O evento de pressão é do mesmo dia e não pode ter entrado no campo inteiro. Direção escrita depois de olhar |
| **01/10** | Cury, Δ −0,06 pp, z −4,2 | Vox Brasil, campo 29/09 a 01/10, só PRES. Vox: Cury 2,2 → 1,2 | `marcal-entra-campanha-flavio-2026-09-29`, `tse-zema-debates-2026-09-29`, Lula recusa o debate (30/09, parte do desfecho do `debate-globo-pres-2026-10-01`), Cury admite "perdão presidencial para todos" na sabatina da RedeTV! (29/09, A16, contexto sem tipo no schema). Desinformação contra Lula (`desinfo-lula-pedofilia-2026-09-29`), alvo fora do movimento | Nenhum evento novo tem Cury como alvo direto com direção negativa clara. Leitura mais forte: continuação da compressão da terceira via (seção 6) |
| **02/10** | Cury, Δ −0,02 pp, z −5,1 | PoderData, campo 30/09 a 02/10, só PRES. PoderData: Cury 6 → 3 | Desfecho do `debate-globo-pres-2026-10-01` (cancelado na noite de 01/10, dentro do campo). Feed: Estadão 02/10 sobre 13 empresas de Cury (manchete, seção 5). Cury protesta no STF e fala em pedir adiamento da eleição (02/10, manchetes, seção 5) | O cancelamento tira de Cury a última vitrine gratuita. Mesma classe de `debate-record-cancelado-2026-09-23` e `consorcio-cancela-debate-2026-09-08` (direção "-"). Δ de nível muito pequeno |
| sem inflexão | Lula | nenhum destaque corroborado no período (25/09 +3,4 e 28/09 −3,1, ambos de uma casa só) | `desinfo-lula-pedofilia-2026-09-29`, `desinfo-waack-deepfake-2026-09-29`. Contexto: AIJE da campanha de Flávio pedindo cassação de Lula e Alckmin (28/09, A19, só citada em resumo) | Sem inflexão associada |
| sem inflexão | Flávio | nenhum destaque no período (último: 22/09, não corroborado) | `marcal-entra-campanha-flavio-2026-09-29` | Sem inflexão associada, apesar de Flávio subir em várias casas (seção 6) |
| sem inflexão | Zema | 28/09 z +6,9 (Ideia, não corroborado, não relevante) | `tse-zema-debates-2026-09-29`, `tarcisio-uniao-direita-2026-09-28` | Sem inflexão associada |

### 2a. Desfecho do debate pré-especificado `debate-globo-pres-2026-10-01`: NÃO HOUVE DEBATE

Cronologia conferida em fonte aberta:

1. **29/09, noite.** O presidente do TSE, Kassio Nunes Marques, a pedido do Novo, manda incluir candidatos do Novo nos debates, contando a bancada atual de 5 deputados (A14, 19h47). Zema entra no debate da Globo. A Globo havia convidado Lula, Flávio, Caiado e Cury (A3, A1).
2. **30/09, tarde.** Lula informa à Globo que não vai (A1, 14h46, A2, 14h57). Motivo relatado: a campanha avalia que ele viraria alvo dos candidatos de direita (A1, A3). No horário do debate, Lula daria entrevista ao Flow (A2, A5). Flávio confirma presença (A3). O Missão aciona o TSE para incluir Renan (A4, 16h55).
3. **01/10, até 13h59.** Nunes Marques nega o pedido de Renan e Cármen Lúcia rejeita recurso no STF (A5). Confirmados: Cury, Flávio, Zema e Caiado.
4. **01/10, fim da tarde.** A ministra Estela Aranha (TSE), em liminar pedida pelo PT/coligação de Lula, proíbe o púlpito vazio identificado de Lula e as perguntas dirigidas ao ausente (A6, 18h15, A13).
5. **01/10, antes de 19h26.** Gilmar Mendes (STF) concede liminar mandando a Globo incluir Renan na vaga de Lula, nas mesmas condições (A7, A8, A9).
6. **01/10, 19h26.** Flávio anuncia que não vai "em função da censura imposta ao evento pelo TSE" (A7). Em vez do debate, faz live, checada pela Lupa (A11).
7. **01/10, até 20h44.** A Globo cancela o debate: "as sucessivas decisões judiciais tomadas momentos antes da realização do debate causam insegurança jurídica" (A10). Confirmado em 02/10 pelo Poder360 (A12).

**Presenças:** nenhuma, porque o debate não ocorreu. Estavam escalados, no momento do cancelamento, Cury, Caiado, Zema e Renan (A9, A10, A12). Lula e Flávio se recusaram (A1, A7).

**Correção ao registro de 25/09:** as notas de `debate-globo-pres-2026-10-01` citavam a Wikipédia com "Lula, Caiado e Cury presentes e Flávio ausente". O desfecho real é o inverso nos dois líderes até 30/09 (Lula ausente, Flávio confirmado) e, no fim, nenhum debate. A tabela da Wikipédia não foi conferida nesta rodada (extração truncada).

**Consequência para as hipóteses (para a curadoria do Bera, não aplicada):**
- **h-2026-09-25-13** (Lula E Flávio no palco): condição falsa. Fecha como **não testável**, como ela mesma prevê.
- **h-2026-09-25-14** (nem Lula nem Flávio): a condição literal se cumpriu (os dois faltaram), mas o mecanismo dela é a exposição no palco, e o debate foi cancelado. Recomendo fechar como **não testável por ausência do tratamento**. Se o Bera preferir testar ao pé da letra, o conferido até o as_of de 02/10 é: nenhum destaque positivo de Cury ou Caiado em 02/10, e Cury tem destaque NEGATIVO corroborado em 02/10 (PoderData, z −5,1). O dia 03/10 ainda não está no dado. As implicações cruzadas das duas hipóteses ("Renan e Zema não convidados") também ficaram falsas: Zema foi incluído pelo TSE e Renan pelo STF.
- O que sobra testável é a classe "debate cancelado" (mesma de `debate-record-cancelado-2026-09-23`): direção "-" para os pequenos que perdem a vitrine. Sugestão de curadoria: anotar o desfecho no próprio `debate-globo-pres-2026-10-01` em vez de criar evento novo, como pede o dossiê.

---

## 3. Eventos (JSON)

```json
[
  {
    "id": "datafolha-empate-2t-2026-09-24",
    "data": "2026-09-24",
    "registrado_em": "2026-10-04",
    "tipo": "pesquisa_bomba",
    "alvo": [280002551547, 280002551932],
    "direcao_esperada": "-",
    "escopo": "nacional",
    "fonte": {
      "url": "https://www.moneytimes.com.br/pesquisa-datafolha-24-de-setembro-gaep/",
      "veiculo": "Money Times, 24/09/2026 19h01 (aberta): Datafolha 22 a 24/09, registro BR-00304/2026, n=2.002",
      "acesso": "2026-10-04"
    },
    "notas": "EXPLORATÓRIO. Direção escrita DEPOIS de olhar o movimento. Datafolha: 1º turno Lula 40 (+1), Flávio 36 (=), Cury 5 (-1), Caiado 4 (=), Renan 3, Zema 1 (-1). 2º turno Lula 47 x Flávio 45, 'empate no limite da margem'. Mecanismo de voto útil: a leitura de disputa apertada entre os líderes empurra o eleitor da terceira via para um dos dois. Ressalva de circularidade: a própria pesquisa está no dado (Datafolha 24/09), então só pode explicar pesquisas com campo depois de 24/09 (AtlasIntel, Palver e Vox de 28/09, Vox de 01/10, PoderData de 02/10), e o Veritá de 25/09 só no último dia de campo. Sinal ambíguo: o mesmo Datafolha tem cenário Lula 46 x Cury 43 (Diario de Pernambuco, 25/09), argumento de elegibilidade a favor de Cury. A Quaest de 28/09 (2º turno 42 a 42) reforça a narrativa, mas foi publicada no último dia de campo das casas de 28/09."
  },
  {
    "id": "tarcisio-uniao-direita-2026-09-28",
    "data": "2026-09-28",
    "registrado_em": "2026-10-04",
    "tipo": "candidatura",
    "alvo": [280002551932, 280002539826],
    "direcao_esperada": "-",
    "escopo": "nacional",
    "fonte": {
      "url": "https://www.seudinheiro.com/2026/politica/desistencia-no-senado-de-sp-reconfigura-aliancas-a-menos-de-uma-semana-do-1o-turno-confira-o-dia-na-politica-ccgg/",
      "veiculo": "Seu Dinheiro, 28/09/2026 (aberta), também O Hoje 28/09 16h47 (Zema avalia desistir) e Tribuna do Planalto 29/09 16h09 (resposta de Caiado), ambas abertas",
      "acesso": "2026-10-04"
    },
    "notas": "EXPLORATÓRIO. Direção escrita DEPOIS de olhar. Em 28/09 Ricardo Salles (Novo-SP) desiste do Senado em ato com Tarcísio, que defende a união da direita em torno de Flávio já no 1º turno e pede 'gestos de união' a Zema e Caiado. No mesmo dia o Novo discute a saída de Zema (O Hoje, com Marina Helena e Marco Antônio Superman pedindo gesto parecido) e Caiado responde na noite de 28/09: 'Eu não recuo em nada na minha vida'. Em 29/09 Zema diz que vai 'até o último minuto' (Times Brasil). Mecanismo: sinal público de que a candidatura é inviável estimula o voto útil contra o candidato pressionado. Ressalva de tempo: o evento é da tarde de 28/09, último dia do campo de AtlasIntel, Palver e Vox, então quase não entra nas pesquisas que geraram o destaque de Caiado em 28/09."
  },
  {
    "id": "marcal-entra-campanha-flavio-2026-09-29",
    "data": "2026-09-29",
    "registrado_em": "2026-10-04",
    "tipo": "candidatura",
    "alvo": [280002551544],
    "direcao_esperada": "+",
    "escopo": "nacional",
    "fonte": {
      "url": "https://www.correiodamanha.com.br/politica/2026/09/323307-pablo-marcal-anuncia-apoio-e-entra-na-campanha-de-flavio-bolsonaro.html",
      "veiculo": "Correio da Manhã, 30/09/2026 11h49 (aberta), também O Hoje, 29/09 21h59 (aberta)",
      "acesso": "2026-10-04"
    },
    "notas": "EXPLORATÓRIO. Direção escrita antes de conferir o dado de Flávio. Em 29/09, em agenda numa academia de jiu-jítsu em São Paulo, Pablo Marçal (registro presidencial indeferido pelo TSE em setembro, ver marcal-tse-cassa-registro-2026-09-11) anuncia apoio e entra na campanha de Flávio, que diz que ele vai colaborar em 'empreendedorismo e mobilidade social'. Marçal: 'Chegou a hora de aposentar o Lula'. NÃO CONFIRMADO: O Hoje afirma que Marçal tinha declarado apoio público a Cury antes. Nenhuma outra fonte aberta confirma, e manchetes de InfoMoney, SBT News e DGABC (não abertas, datas não conferidas) falam de apoio de Marçal à pré-candidatura de Flávio, o que faria do 29/09 uma entrada formal na campanha, não um primeiro apoio. Se o apoio a Cury for confirmado, o evento ganha um ramo '-' para Cury (sq 280002551547) dentro do raio de 01 e 02/10."
  },
  {
    "id": "tse-zema-debates-2026-09-29",
    "data": "2026-09-29",
    "registrado_em": "2026-10-04",
    "tipo": "decisao_judicial",
    "alvo": [280002539826],
    "direcao_esperada": "+",
    "escopo": "nacional",
    "fonte": {
      "url": "https://www.oliberal.com/eleicoes/tse-manda-incluir-zema-e-candidatos-do-novo-nos-debates-eleitorais-1.1174895",
      "veiculo": "O Liberal, 29/09/2026 19h47 (aberta), também Gazeta do Povo 30/09 e Poder360 01/10 (abertas)",
      "acesso": "2026-10-04"
    },
    "notas": "EXPLORATÓRIO. Direção escrita antes de conferir o dado de Zema. Nunes Marques, presidente do TSE, a pedido do Novo, decide que a regra de 5 parlamentares (art. 46 da Lei das Eleições) usa a bancada ATUAL, não só a eleita em 2022, e manda incluir candidatos do Novo nos debates. Beneficia Zema (Globo, 01/10) e, nos estados, André Marinho (GOV-RJ) e Kiko Caputo (GOV-DF), corridas do outro agente. Mecanismo: acesso ao debate de maior audiência. O tratamento não se realizou, porque o debate presidencial foi cancelado em 01/10: sobra só a exposição no noticiário. Sem inflexão associada no PRES."
  },
  {
    "id": "desinfo-lula-pedofilia-2026-09-29",
    "data": "2026-09-29",
    "registrado_em": "2026-10-04",
    "tipo": "peca_desinformacao",
    "alvo": [280002542548],
    "direcao_esperada": "-",
    "escopo": "nacional",
    "fonte": {
      "url": "https://www.agencialupa.org/eleicoes/2026/09/29/lula-nao-defendeu-nem-normalizou-a-pedofilia-em-discurso-no-para/",
      "veiculo": "Agência Lupa, 29/09/2026 (aberta), classificação FALSO",
      "acesso": "2026-10-04"
    },
    "notas": "EXPLORATÓRIO. Direção pela classe (peça falsa contra o alvo), escrita antes de conferir o dado de Lula. Corte de discurso de Lula em comício em Belém (28/09) sobre exames preventivos de próstata, divulgado como se ele 'normalizasse a pedofilia', em Facebook, Instagram, Threads, X e TikTok. Um post no Facebook passou de 151 mil visualizações. Compartilhado pelos deputados Nikolas Ferreira (PL-MG) e Mário Frias (PL-SP). Em 01/10, na live que substituiu o debate, Flávio e aliados voltaram a associar Lula à pedofilia (Lupa, 01/10). Data do evento = data da checagem, porque o dia do primeiro post não foi confirmado (não antes de 28/09). Sem inflexão associada."
  },
  {
    "id": "desinfo-waack-deepfake-2026-09-29",
    "data": "2026-09-29",
    "registrado_em": "2026-10-04",
    "tipo": "peca_desinformacao",
    "alvo": [280002542548],
    "direcao_esperada": "-",
    "escopo": "nacional",
    "fonte": {
      "url": "https://www.agencialupa.org/verificacao/2026/10/03/e-falso-o-video-que-usa-imagem-de-william-waack-para-sugerir-que-pt-nao-aceitara-derrota-nas-urnas-post-e-deepfake/",
      "veiculo": "Agência Lupa, 03/10/2026 17h52 (aberta), classificação FALSO (deepfake)",
      "acesso": "2026-10-04"
    },
    "notas": "EXPLORATÓRIO. Deepfake com a imagem de William Waack (CNN Brasil) dizendo que o PT armou, com Flávio Dino, um inquérito para anular a eleição se Flávio Bolsonaro vencer. A CNN desmentiu o vídeo em 29/09 (segundo a Lupa), por isso a data do evento é 29/09, a primeira em que a circulação está confirmada. Alcance pequeno: 9.600 visualizações no Facebook até 03/10, 14h. Registrado pela regra de curadoria (peça checada pela Lupa), não por plausibilidade de efeito. Sem inflexão associada."
  }
]
```

---

## 4. Mecanismo, implicações cruzadas e fonte, por evento

### 4.1 `datafolha-empate-2t-2026-09-24`
1. **Mecanismo.** [fato] O Datafolha de 22 a 24/09 mostrou Lula 47 x Flávio 45 no 2º turno, empate no limite da margem, e Cury caindo de 6 para 5 no 1º turno (A22). [inferência] Disputa apertada entre os dois líderes é o gatilho clássico de voto útil, que drena a terceira via. [hipótese] Esse efeito explica parte da queda de Cury nas pesquisas com campo depois de 24/09.
2. **Implicações cruzadas.** Poderia explicar: Cury em 28/09 (AtlasIntel, Palver, Vox, campo depois de 24/09), 01/10 (Vox) e 02/10 (PoderData). Caiado em 28/09 só se Palver e AtlasIntel forem lidas ao pé da letra, mas o Δ é −0,03 pp. Deveria ter se movido e o detector não pegou: **Flávio e Lula para cima**. No dado cru os dois sobem em quase todas as casas entre a última rodada antes de 24/09 e a primeira depois (Datafolha Lula 40 → 42, Flávio 36 → 38, PoderData 41 → 42 e 39 → 41, Real Time 41 → 43 e 37 → 39, Vox Flávio 37,8 → 41,2), e nenhum dos dois tem destaque corroborado no período: o detector não registra a outra metade do mecanismo. Renan não cai de forma corroborada depois de 25/09, o que vai contra um voto útil geral. NÃO explica Cury e Renan em 25/09 (campo Veritá 20 a 25/09, quase todo antes).
3. **Fonte.** Money Times, 24/09/2026 (A22), acesso 2026-10-04. Fonte primária (Folha/Datafolha) não aberta: "número conferido em fonte secundária".

### 4.2 `tarcisio-uniao-direita-2026-09-28`
1. **Mecanismo.** [fato] Em 28/09 Salles desistiu do Senado-SP e Tarcísio pediu "gestos de união" a Zema e Caiado para concentrar votos em Flávio no 1º turno (A19). Zema avaliou desistir (A20) e Caiado negou na mesma noite (A21). [inferência] Pressão pública de aliados sinaliza ao eleitor que o candidato não tem chance. [hipótese] Isso reduz Caiado e Zema nas pesquisas de campo posterior a 28/09.
2. **Implicações cruzadas.** Poderia explicar: Caiado em 28/09 só marginalmente (evento da tarde do último dia de campo). Teste conferível agora: Caiado e Zema deveriam cair em 29/09 a 02/10. Conferido: **nenhum destaque de Caiado ou Zema de 29/09 a 02/10** no `inflexoes.json`. No dado cru, Caiado fica estável ou oscila (Datafolha 4 → 3, PoderData 2 → 2, Real Time 2 → 3, Vox 3,8 → 3,3, Gerp 3 → 3) e Zema fica em 0 a 1,8. Leitura: o evento não deixou marca detectável, ou a marca é menor que a resolução do detector nesse nível de share. Quem se moveria por tabela: Flávio para cima (sobe no dado cru, sem destaque).
3. **Fonte.** Seu Dinheiro, 28/09 (A19), O Hoje, 28/09 (A20), Tribuna do Planalto, 29/09 (A21), acesso 2026-10-04. A matéria original de O Popular com a fala de Caiado não foi aberta.

### 4.3 `marcal-entra-campanha-flavio-2026-09-29`
1. **Mecanismo.** [fato] Marçal, com registro indeferido, anuncia apoio e entra na campanha de Flávio em 29/09 (A17, A18). [inferência] Transfere parte do eleitorado antissistema e digital que Marçal mobilizou em 2024. [hipótese] Se Marçal tinha antes sinalizado apoio a Cury (O Hoje, não confirmado), a troca tira de Cury um eleitorado de perfil parecido com o que o fez crescer em agosto.
2. **Implicações cruzadas.** Poderia explicar: no ramo Cury (não confirmado), as quedas de 01/10 (Vox, campo 29/09 a 01/10) e 02/10 (PoderData). Para Flávio: deveria haver destaque positivo depois de 29/09. Conferido: **nenhum destaque de Flávio no período**, embora ele suba no dado cru (Vox 37,8 → 41,2, PoderData 39 → 41, Futura 40,4 → 42,2). Renan, que disputa o mesmo eleitorado digital de direita, não se move de forma corroborada depois de 25/09.
3. **Fonte.** Correio da Manhã, 30/09 (A18), O Hoje, 29/09 (A17), Times Brasil, 29/09 (A16), acesso 2026-10-04. Apoio anterior de Marçal a Cury: **não confirmado**.

### 4.4 `tse-zema-debates-2026-09-29`
1. **Mecanismo.** [fato] O TSE mandou incluir o Novo nos debates contando a bancada atual (A14). [inferência] Acesso ao maior debate da campanha daria exposição a um candidato com 1%. [fato] O debate presidencial foi cancelado (A10), então o tratamento não aconteceu.
2. **Implicações cruzadas.** Não explica nenhuma inflexão PRES (Zema não tem destaque relevante no período). Por tabela, a decisão vale para Marinho (GOV-RJ) e Kiko Caputo (GOV-DF): o outro agente pode cruzar com as inflexões negativas de André Marinho em 28/09 e 30/09 (a decisão é de 29/09 à noite, depois do destaque de 28/09).
3. **Fonte.** O Liberal, 29/09 (A14), acesso 2026-10-04. Decisão do TSE (fonte primária) não aberta.

### 4.5 `desinfo-lula-pedofilia-2026-09-29`
1. **Mecanismo.** [fato] Corte fora de contexto de discurso de Lula em Belém (28/09) viralizou como "normalização da pedofilia", com post acima de 151 mil visualizações e compartilhamento por deputados do PL (A25). [fato] Flávio repetiu a associação na live de 01/10 (A11). [hipótese] Efeito negativo sobre Lula entre eleitores religiosos indecisos.
2. **Implicações cruzadas.** Deveria aparecer como queda de Lula em pesquisas com campo depois de 28/09. Conferido: **nenhum destaque corroborado de Lula** de 29/09 a 02/10, e o dado cru mostra Lula estável ou em alta (Datafolha 40 → 42, PoderData 41 → 42, Real Time 41 → 43, Vox 41 → 40,4). Não explica nenhuma inflexão do período.
3. **Fonte.** Agência Lupa, 29/09 (A25) e 01/10 (A11), acesso 2026-10-04.

### 4.6 `desinfo-waack-deepfake-2026-09-29`
1. **Mecanismo.** [fato] Deepfake com Waack acusando o PT de planejar anular a eleição, desmentido pela CNN em 29/09 e checado pela Lupa em 03/10 (A26). [inferência] Alcance pequeno (9.600 visualizações) torna efeito agregado implausível. [hipótese] Serve como peça da narrativa de fraude a ser medida depois da apuração, não como causa de inflexão.
2. **Implicações cruzadas.** Não explica nenhuma inflexão. Lula sem destaque corroborado no período.
3. **Fonte.** Agência Lupa, 03/10 (A26), acesso 2026-10-04.

### 4.7 Desfecho de `debate-globo-pres-2026-10-01` (evento já registrado, sem JSON novo)
1. **Mecanismo.** [fato] O debate foi cancelado depois de Lula (30/09) e Flávio (01/10) desistirem e de duas liminares no mesmo dia (seção 2a). [inferência] Para Cury, Caiado, Zema e Renan, é a perda da última vitrine gratuita antes do 1º turno, a mesma classe dos cancelamentos de 08/09 e 23/09. [hipótese] Direção "-" para os quatro, com a ressalva de que a cobertura do cancelamento deu exposição a Renan (que fez da desistência de Flávio um mote, "medo" e "fuga", A12) e a Cury (protesto no STF em 02/10, manchetes).
2. **Implicações cruzadas.** Poderia explicar: Cury em 02/10 (PoderData, campo 30/09 a 02/10, inclui a noite de 01/10). Teste: Caiado, Zema e Renan deveriam cair em 02 e 03/10. Conferido até o as_of de 02/10: só Cury tem destaque (negativo). Caiado, Zema e Renan sem destaque. 03/10 e 04/10 ainda não estão no dado.
3. **Fonte.** A1 a A13, acesso 2026-10-04.

---

## 5. Pendentes, só manchete (fora do JSON)

Manchetes do Google Notícias RSS, matéria NÃO aberta. Data é a do feed.

| Data | Veículo | Manchete | Por que importa |
|---|---|---|---|
| 26/09 | PlatôBR | "O que Caiado e Kassab farão em eventual segundo turno entre Lula e Flávio" | contexto da pressão sobre Caiado |
| 27/09 | O Globo | "A chance de Caiado fazer campanha para Flávio Bolsonaro no 2º turno" | idem |
| 28/09 | Folha (Painel) | "Zema avalia desistir de candidatura em meio à pressão de aliados" | reforça `tarcisio-uniao-direita-2026-09-28` |
| 28/09 | O Globo | "Quaest: Flávio 'herdaria' a maior parte dos votos de Cury, Caiado, Renan e Zema em eventual 2º turno" | narrativa de voto útil |
| 28/09 | CNN Brasil | "Nexus/BTG: Lula tem 46% no 2º turno, Flávio, 44%, há empate técnico" | mesma classe de `datafolha-empate-2t-2026-09-24` |
| 29/09 | CartaCapital e Revista Fórum | "Campanha de Flávio Bolsonaro pressiona rivais da direita a desistir antes do 1º turno" | idem |
| 29/09 | CNN Brasil | "Flávio liga para Zema e aguarda definição sobre desistência" | idem |
| 29/09 | Folha | "Justiça confirma dívidas de Renan Santos e frustra tentativa de sigilo sobre cobranças de impostos" | candidata a `denuncia` contra Renan, sem inflexão depois de 25/09 |
| 28/09 | Seu Dinheiro (só citação em resumo aberto) | AIJE da campanha de Flávio pedindo cassação de Lula e Alckmin | candidata a `denuncia`, sem matéria própria aberta |
| 30/09 | CNN Brasil | "Vice de Augusto Cury diz que candidato ficará neutro no segundo turno" | posicionamento de Cury |
| 30/09 | CNN Brasil | "Meio/Ideia: No 2º turno, Lula herda 56,6% de Cury, Flávio, 82,2% de Renan" | perfil do eleitor de Cury (mais próximo de Lula), útil para ler o ramo Marçal |
| 30/09 | G1 | "Augusto Cury diz que Flávio Bolsonaro 'não é tanto de direita'..." | contexto |
| 01/10 | CNN Brasil | "Campanha de Flávio Bolsonaro apela a Caiado e fala em ministério" | pressão sobre Caiado |
| 01/10 | Brasil de Fato | "Renan acusa Flávio Bolsonaro de ameaça" | conflito Renan x Flávio |
| 01/10 | G1 | "Datafolha: Lula, 42%, Flávio Bolsonaro, 38%, Cury, 4%, Caiado, 3%, Renan, 3%, Zema, 1%" | pesquisa já no dado |
| 02/10 | Estadão | "Propostas de Cury têm relação com atividades de 13 empresas que têm o candidato como sócio" | candidata a `denuncia` contra Cury (data 02/10, mesmo dia do último destaque) |
| 02/10 | CNN, Poder360, InfoMoney, Correio Braziliense | Cury protesta no STF e fala em pedir adiamento da eleição | reação de Cury ao cancelamento |
| 02/10 | Valor | "Análise: Decisão de Flávio, atribuída à 'censura', só aconteceu depois da imposição de Renan no debate" | leitura do motivo real da desistência de Flávio |
| 02/10 | CNN Brasil | "PT atribui desistência de Flávio à ida de Renan Santos, PL aponta 'censura'" | idem |
| 03/10 | G1, CNN, Valor | "Caiado nega que tenha cogitado desistir e apoiar Flávio no 1º turno" | fecha o episódio da pressão |
| 03/10 | Poder360 | "Renan desafia Flávio a debate em troca de apoio no 1º turno" | contexto |
| 01/10 | Agência Lupa (listagem aberta, matéria não) | "No Flow, Lula repete erro sobre PIB e ao falar de Flávio Bolsonaro" | checagem da entrevista que substituiu o debate |

Não encontrado: nenhuma checagem do Aos Fatos sobre os presidenciáveis no período apareceu nas buscas (só a página de lançamento da cobertura de 2026). Nenhuma decisão do TSE sobre direito de resposta ou propaganda presidencial no período apareceu nas buscas (os resultados eram de 2022). Nenhum outro debate presidencial realizado entre 24/09 e 04/10 foi encontrado (o da Record de 27/09 já estava cancelado).

---

## 6. O que não dá para afirmar

- **Nenhum evento acima causou nada.** Todos nascem exploratórios (registrados em 04/10, depois do movimento), e as direções de `datafolha-empate-2t-2026-09-24` e `tarcisio-uniao-direita-2026-09-28` foram escritas depois de olhar o dado.
- **A queda de Cury é lenta e geral, não um salto datável.** Entre a rodada de meados de setembro e a de fim de setembro ou início de outubro, Cury cai em todas as casas do `polls.json`: Datafolha 6 → 5 → 4, Quaest 7 → 6 → 4, PoderData 8 → 6 → 3, Real Time 6 → 3, CNT/MDA 6,0 → 3,1, Gerp 7 → 5 → 4, Futura 5,6 → 3,8, DataTrends 6 → 4, Vox 2,2 → 1,2. As quatro datas de Cury no P4 (25/09, 28/09, 01/10, 02/10) coincidem com a chegada de lotes de Veritá, AtlasIntel, Palver, Vox e PoderData, e os Δ de nível são pequenos (−0,28 a −0,02 pp). Leitura dominante: tendência real mais calendário de pesquisas, não evento pontual.
- **Caiado e Renan em 25 e 28/09 são resíduo de casa.** Δ de nível de 0,00 e −0,03 pp. As casas disparadoras dão Caiado 1 a 2 e Renan 2,3 (Veritá) ou 8 (Palver), contra 3 a 5 e 3 a 4 nas casas de referência.
- **O detector não vê a outra metade do voto útil.** Lula e Flávio sobem juntos no dado cru no fim de setembro e não têm destaque corroborado. Qualquer hipótese de "compressão da terceira via" precisa olhar o share dos líderes, não só os destaques dos pequenos.
- **Ordem exata das liminares de 01/10.** As fontes concordam que Estela Aranha decidiu no fim da tarde (Metrópoles às 18h15) e Gilmar antes das 19h26 (CNN), mas o Poder360 de 02/10 lista as decisões em outra ordem. A manchete de Revista Oeste ("levou 2 horas para decidir", assinatura às 17h52) não foi aberta. A CartaCapital diz que a liminar de Gilmar veio em ação "do Solidariedade", enquanto Gazeta do Povo e outras falam em pedido do candidato ou do Missão: não confirmado.
- **Extração do iMirante (A15) não é confiável** para nomes: trouxe "Kiko Celeguim (PT)" e "Marinho (PL)", enquanto O Liberal (A14) traz Kiko Caputo e André Marinho, do Novo. Usei só a data.
- **Apoio prévio de Marçal a Cury:** não confirmado (uma fonte só, O Hoje).
- **Revista Oeste, "Augusto Cury também desiste de participar do debate":** não aberta (403). Não sei de qual debate se trata nem a data. Não usei.
- **Efeito do dia 03/10 e da véspera:** o dado está em as_of 02/10. Qualquer conferência das janelas 02 a 03/10 das hipóteses h-13 e h-14 está incompleta até a próxima rodada.
