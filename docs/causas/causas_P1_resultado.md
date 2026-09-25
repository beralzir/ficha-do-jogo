# Cruzamento com notícias · P1: 2026-08-01 a 2026-08-31 · resultado

Gerado em 2026-09-25 a partir do dossiê `causas_P1.md` (dado publicado as_of 2026-09-24), do dado local do projeto e de 8 acessos web (2 buscas + 6 páginas, o teto da casa; orçamento esgotado nesta sessão). Nada aqui afirma que um evento causou um movimento: o que se entrega é causa candidata testável, com a direção que o mecanismo prevê, mais o diagnóstico de quais inflexões do período são, com alta probabilidade, artefato de medição e não pedem evento nenhum.

Resumo em três linhas:
1. Das 16 datas, só duas famílias têm evento candidato com fonte: a presidencial (debate da Band de 23/08, com Cury e Renan Santos no palco e os líderes ausentes, seguido da amplificação já registrada em `cury-viral-2026-08-26`) e o Senado-RJ (desistência de Márcio Canella em 03/08 e confirmação de Carlos Jordy pelo PL em 04/08, que muda a composição da disputa; a Datafolha de 18 a 21/08 é a primeira pesquisa com Jordy).
2. As inflexões de GOV-DF (15 e 18/08) são artefato de ingestão confirmado localmente (aliases contaminados por linha de nota da Wikipédia nas pesquisas de 17 a 19/07); as de SEN-MA (10 e 11/08), SEN-BA (22 e 26/08), GOV-GO (17 e 21/08), GOV-PA (15 e 19/08), SEN-PB (31/08) e SEN-RJ (28/08) têm a assinatura de efeito de casa (correção após outlier de um instituto, ou lote da Veritá), não de evento.
3. Três movimentos parecem reais e ficaram SEM causa encontrada porque o orçamento de web acabou antes da imprensa regional: Hilton Gonçalo no MA (IPSensus 3,5 para 16,4 dentro da própria casa, 20 a 29/08), Merísio em SC (5,6 para 14 a 20, 23/08 a 09/09, três casas) e Soraya em MS (10 a 13 para 17 a 19, 23 a 27/08, duas casas). São as lacunas prioritárias para uma nova sessão de discovery.

O evento mais importante do período é de uma classe que o schema não tem: entrada e saída de candidato (convenção, desistência, confirmação, registro). Agosto é o mês do registro (prazo 15/08), então essa classe domina; os eventos dessa classe estão em bloco separado, fora do array validável, com proposta de extensão de `_tipos`.

---

## (1) Corte de conhecimento e fontes abertas

**Corte de conhecimento do modelo: junho de 2026.** Nenhum fato de agosto de 2026 vem de memória. Tudo o que é datado depois do corte veio, nesta sessão (25/09/2026), de fonte aberta com URL ou do dado local do projeto. Fatos anteriores ao corte usados aqui (texto da Lei 9.504/1997; que Márcio Canella sucedeu Waguinho na prefeitura de Belford Roxo em 2024) estão marcados como "conhecimento anterior ao corte, não reconferido".

**Orçamento usado:** 2 WebSearch + 6 WebFetch (teto por sessão). Esgotado. Não foram consultados: Agência Lupa, Aos Fatos, TSE (representações, DivulgaCand, registro de pesquisas), Band (site oficial do debate), Correio Braziliense, imprensa regional de MA, SC, MS, PB, GO, PA e BA.

**Páginas abertas (URL · acesso 2026-09-25):**

| # | Fonte | URL | O que rendeu |
|---|---|---|---|
| W1 | Wikipédia PT, "Eleição presidencial no Brasil em 2026" | https://pt.wikipedia.org/wiki/Elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2026 | Tabela de debates (Band 23/08: participantes Renan Santos e Augusto Cury; ausentes Lula, Flávio Bolsonaro, Zema, Caiado; Samara não convidada. Globo 01/10: mediador César Tralli; página lista Lula, Caiado e Cury como convidados e Flávio e Zema como "não convidados", ver ressalva na seção 5. Debate CNN/SBT de 14/09 cancelado). Cronologia: 01/08 convenções PCB e PCO; 02/08 PT oficializa Lula; 03/08 Avante oficializa Cury (vice Júlio Delgado); 05/08 Agir apoia Cury, PSDB-Cidadania e Podemos neutros, PSOL-Rede apoia Lula; 11/09 registro de Pablo Marçal cassado (unânime), Leonardo Avalanche confirmado pelo PRTB. Sobre Cury: "após a participação no debate eleitoral em 23 de agosto" teve o maior crescimento de seguidores no Instagram e em buscas no Google; desempenho associado a crescimento não orgânico "possivelmente motivado por Pablo Marçal"; marqueteiro e vice negaram contratação de influenciadores. 13 candidatos registrados; 1º turno 04/10, 2º turno 25/10. |
| W2 | Poder360, "PL terá chapa puro-sangue para o Senado no RJ", 04/08/2026 20h37 | https://www.poder360.com.br/poder-eleicoes-2026/pl-tera-chapa-puro-sangue-para-o-senado-no-rj/ | Jordy escolhido pelo PL; "a decisão foi chancelada depois de a federação União Brasil-PP declarar neutralidade no Estado e inviabilizar uma chapa mista"; ganhou força com a desistência de Márcio Canella (União Brasil), "então favorito da coligação", que recuou para a Alerj "depois de ser alvo de uma operação policial e chegar a ser detido por porte ilegal de arma de fogo". Sem menção a Crivella, Waguinho, Pedro Paulo ou datas de convenção. |
| W3 | Wikipédia PT, pesquisas RJ 2026 | https://pt.wikipedia.org/wiki/Pesquisas_eleitorais_para_a_elei%C3%A7%C3%A3o_estadual_de_2026_no_Rio_de_Janeiro | Linhas de anotação: Senado 28/05 Cláudio Castro desiste; 03/08 "Márcio Canella (UNIÃO) desiste oficialmente da pré-candidatura ao Senado Federal"; 04/08 "Partido Liberal confirma candidatura de Carlos Jordy como senador". Governador: 01/08 Witzel desiste; 11/09 "Anthony Garotinho (Republicanos) tem sua candidatura indeferida pelo TRE-RJ". Jordy aparece pela primeira vez na Datafolha 18 a 21/08; última de Canella: Prefab 24 a 29/07. (Os percentuais extraídos por essa leitura divergem do polls.json em Datafolha e Prefab; não usados, ver seção 5.) |
| W4 | Wikipédia PT, pesquisas MA 2026 | https://pt.wikipedia.org/wiki/Pesquisas_eleitorais_para_a_elei%C3%A7%C3%A3o_estadual_de_2026_no_Maranh%C3%A3o | Linhas de anotação do Senado: 20/07 Pedro Lucas Fernandes desiste; 22 a 30/07 Roberto Rocha sai do Novo para o PRTB; 27/07 Avante retira Duarte Júnior; 30/07 Roberto Rocha desiste do Senado. Nada entre 01/08 e 10/09. "Veritá" e "Véritas" aparecem como registros separados. Sem nota de contratante ou registro TSE para IPSensus 24 a 29/08 e Qualitativa 19 a 25/08. |
| W5 | Wikipédia PT, pesquisas SC 2026 | https://pt.wikipedia.org/wiki/Pesquisas_eleitorais_para_a_elei%C3%A7%C3%A3o_estadual_de_2026_em_Santa_Catarina | Nenhuma linha de anotação entre 15/07 e 15/09. Contratantes: Quaest 20 a 23/08 = NSC Comunicação; Neokemp/OCP 24 a 25/08 = OCP News. Merísio: 3,4 (Mapa/JP 22/07), 8,2 (Neokemp 24/07), 4,0 (Quaest 23/08), 12,3 (Neokemp/OCP 25/08), 11,8 (Veritá 01/09), 17,6 (Atlas 09/09), 8,0 (RTBD 16/09). Os três principais aparecem em todas. |
| W6 | Wikipédia PT, pesquisas MS 2026 | https://pt.wikipedia.org/wiki/Pesquisas_eleitorais_para_a_elei%C3%A7%C3%A3o_estadual_de_2026_em_Mato_Grosso_do_Sul | Linhas de anotação do Senado: 24/06 PL oficializa Azambuja e Contar; 31/07 Nelsinho Trad (PSD) desiste e vira suplente de Azambuja. Nada em agosto. A linha Ranking Brasil 23 a 27/08 traz Soraya 32,2 na página (não é erro de transcrição do repo); a extração automática leu a coluna de 20,2 como "Nelsinho Trad", o que é incompatível com a desistência dele em 31/07: a linha pede conferência humana na fonte primária. |

**Vistas só no resultado de busca (título e URL; conteúdo NÃO aberto):** CartaCapital, "Debate na 'Band' aponta diferentes caminhos para prováveis fracassos de Caiado, Renan e Cury" (https://www.cartacapital.com.br/opiniao/debate-na-band-aponta-diferentes-caminhos-para-provaveis-fracassos-de-caiado-renan-e-cury/); YouTube, "DEBATE PRESIDENCIAL 2026 NA BAND | 23/08/2026 | Augusto Cury" (https://www.youtube.com/watch?v=Il2A00945EA); Wikipédia EN, "Augusto Cury" (convenção do Avante em 03/08, vice Júlio Delgado); Revista Fórum, "PL lança Carlos Jordy ao Senado após perder aliados no Rio de Janeiro" (https://revistaforum.com.br/revista-forum/flavio-chapa-rio/); Congresso em Foco, "Rio de Janeiro tem 16 candidatos em disputa por vagas no Senado"; CNN Brasil, O Tempo e Gazeta do Povo (perfis de Jordy); Wikipédia EN, "2026 Rio de Janeiro general election".

**Fonte legal (texto estável, NÃO reconferido nesta sessão):** Lei 9.504/1997, https://www.planalto.gov.br/ccivil_03/leis/l9504.htm: art. 11 (registro de candidaturas até 15/08), art. 36 (propaganda eleitoral a partir de 16/08), art. 47 (rádio e TV nos 35 dias anteriores à antevéspera: 28/08 para eleição em 04/10). Conferir no calendário do TSE numa sessão com orçamento.

**Dado local (só leitura):** `data/live/polls.json` (updated_at 2026-09-25), `data/eleicoes/inflexoes.json` (as_of 2026-09-24), `data/eleicoes2026_results.json`, `data/eleicoes/hipoteses.json` (25/09), `data/eleicoes/eventos.json`, `docs/plano-fase-d-modelagem.md` (M3), `src/eleicoes_model.py` (regra de deduplicação por (corrida, instituto, campo_fim) ficando o cenário com mais casados, e normalização do share entre os casados), `src/eleicoes_eventos.py` (validador: TIPOS, ESCOPOS = "nacional" ou "UF", alvo como lista de sq válidos, `pre_especificado` derivado).

Todos os shares citados abaixo como "normalizado" são a série que o filtro de fato vê: share entre os candidatos casados, recomputado aqui com a mesma regra do modelo.

---

## (2) Tabela: data → evento(s) candidato(s) ou "sem evento plausível"

Status possíveis: **evento candidato** (com fonte), **artefato candidato** (o dado cru explica a inflexão sem evento), **sem evento plausível encontrado** (procurei e não achei; o que procurei está na última coluna), **não pesquisado** (o orçamento acabou antes; só o dado local foi olhado).

| Data | Corrida · candidato (z, casa que disparou) | O que o filtro viu (share normalizado) | Status e causa candidata (janela 0 a 7 dias antes) | O que foi procurado |
|---|---|---|---|---|
| 10/08 | SEN-MA · Lahesio Bonfim (z -4,4, IPPI) | Veritá 25 a 29/07 deu 35,8; INOP 16/07 18,8; IPPI 06 a 10/08 17,5; IPSensus 20/08 19,9; Quaest 23/08 16,4. Só a Veritá o vê acima de 20 (26,0 de novo em 01/09). | **Artefato candidato**: correção do outlier de casa da Veritá, não queda. Janela 03 a 10/08 sem evento no MA. | W4 (linhas de anotação: eventos só em 20, 27 e 30/07, saídas de Pedro Lucas Fernandes, Duarte Júnior e Roberto Rocha, fora da janela mas definindo a lista que as pesquisas de agosto usam). Imprensa do MA: não pesquisada. |
| 11/08 | SEN-MA · Lahesio Bonfim (z -3,5, Véritas) | Véritas 08 a 11/08: 15,0. | **Artefato candidato**: mesma correção. Se "Véritas" e "Veritá" forem a mesma casa (a página lista como registros distintos), há uma reversão de 39,5 para 9,7 no bruto dentro da própria casa em 13 dias, o que pediria evento: nenhum encontrado. | W4; `prior_institutos.json` (só "Instituto Veritá" mapeia para "Veritá"; "Véritas" não tem alias). |
| 15/08 | GOV-DF · Celina Leão (z -3,9, IGAPE) · GOV-PA · Araceli (z -3,4, Doxa) | DF: IGAPE 10 a 15/08 43,3, igual a Correio 01/08 (43,3) e IGAPE 22/08 (43,1). O nível vinha inflado: nas pesquisas IGAPE e Paraná de 17 a 19/07 só 3 de 6 candidatos casaram sq (aliases com o texto "Izalci Lucas (PL) desiste oficialmente da pré-candidatura" colado; Arruda ficou sem sq) e Celina saiu com 66 a 71 normalizado. PA: Doxa 2,1 contra Quaest 8,8 (25/07) e RTBD 6,2 (03/08); share de 2 a 3 pontos, ruído de casa. | DF: **artefato de ingestão, confirmado localmente**; não é evento (o fato de fundo, Izalci desistir, é de março de 2026, data exata não conferida; bug registrado como tarefa separada). PA: **não pesquisado**; a inflexão é de 0,06 pp e some dentro da dispersão entre casas. | DF: `polls.json` (aliases e casamento), `src/eleicoes_model.py` (normalização), `inflexoes.json` (Celina também marcada em 01/08, z -4,49, pela Correio/Opinião: mesma cadeia). PA: só dado local. |
| 17/08 | GOV-GO · Luis Cesar Bueno (z -3,1, Paraná Pesquisas) | Paraná 2,7 e Brasmarket 2,4 são as duas casas mais baixas; Veritá 9,9 a 13,9, Atlas 11,8, Goiás Pesquisas 10,7 a 10,9, DataRD 11,1, Quaest 4,2 a 5,5. Δ do nível é positivo (+0,13 pp) apesar do z negativo. | **Artefato candidato**: duas casas baixas em sequência. | Só dado local. Imprensa de GO: **não pesquisada**. |
| 18/08 | GOV-DF · Celina Leão (z -3,0, Real Time Big Data) | RTBD 14 a 18/08: Celina 35,8, Arruda 33,7 (a casa dá Arruda 32 no bruto; IGAPE dá 23,7). | **Artefato**: mesma cadeia de 15/08, somada ao viés de casa da RTBD pró-Arruda. | Idem 15/08. |
| 19/08 | GOV-PA · Araceli (z -3,4, AtlasIntel) | Atlas 14 a 19/08: 1,5. Série: 4,5 · 8,8 · 6,2 · 2,1 · 1,5 · 3,4 · 2,5 · 5,4 · 3,3. | **Não pesquisado**; Δ de 0,04 pp, ruído. | Só dado local. |
| 21/08 | SEN-RJ · Marcelo Crivella (z -5,0) e Waguinho (z -3,6), Datafolha 18 a 21/08 · GOV-GO · Bueno (z -3,8, Brasmarket) | RJ: a Datafolha é a primeira pesquisa com Carlos Jordy (PL). Dentro de cada casa, julho contra agosto: Quaest Crivella 24,3 para 15,4 e Waguinho 10,8 para 5,1; Paraná 24,1 para 19,7 e 8,7 para 8,6; RTBD 26,8 para 17,9 e 12,7 para 10,3; Prefab 20,7 para 20,4 e 14,0 para 9,3. Jordy entra com 10 a 18. Portinho (PL) não cai (Quaest 10,8 para 12,8; Paraná 8,7 para 10,0; Prefab 5,8 para 7,7). Datafolha e Quaest são casas baixas para Crivella (11 a 15) contra Paraná, Prefab e RTBD (16 a 20). GO: casa baixa de novo. | RJ: **evento candidato, FORA do schema** (classe "candidatura"): 03/08 Canella (UNIÃO) desiste; 04/08 PL confirma Jordy, chapa pura Jordy e Portinho, depois da neutralidade da federação União-PP (W2, W3). Direção prevista pelo mecanismo: "-" para Crivella e Waguinho (mesma faixa bolsonarista fora do PL), "?" para Portinho. Parte do z de 21/08 é casa (Datafolha baixa). GO: **artefato candidato**. | W2, W3, busca 2, `polls.json` (composição por pesquisa). |
| 22/08 | SEN-BA · Angelo Coronel (z -4,2, Opnus/BNews) | Veritá 15 a 19/08 deu 29,0 (e 33,1 em 09/09); Opnus 11,8 e Quaest 9,6 a 12,0 são as casas baixas; Paraná, Atlas, RTBD e DataTrends ficam em 17 a 21 o tempo todo. Δ do nível é positivo (+0,06 pp). | **Artefato candidato**: correção do outlier da Veritá por uma casa baixa. | Só dado local. Imprensa da BA: **não pesquisada**. |
| 24/08 | SEN-MS · Soraya (z +3,1, Quaest) · SEN-RJ · Pedro Paulo (z -3,1, Quaest) | MS: Quaest 21 a 24/08 17,7 contra IPR 13,1 (23/08) e Ranking 10,2 (12/08); depois Ranking 27/08 19,4, IPEMS 09/09 17,5, mas Ranking 09/09 volta a 11,3 e RTBD 12,8. RJ: Quaest dá Pedro Paulo 7,7 (10,8 em julho); Paraná 15,4 e Prefab 11,7 quase parados: efeito de composição pela entrada de Jordy mais casa. | MS: **sem evento plausível encontrado** (busca incompleta): a página não tem anotação em agosto; a única de julho (Nelsinho Trad desiste em 31/07, vira suplente de Azambuja) já estava refletida na Ranking de 07 a 12/08. RJ: mesmo evento de 21/08 (composição). | W6; imprensa de MS **não pesquisada**. |
| 25/08 | GOV-SC · Gelson Merísio (z +3,2, Neokemp/OCP) · SEN-MA · Dr. Hilton Gonçalo (z +6,2, Qualitativa) | SC: Quaest 23/08 5,6 (contratante NSC); Neokemp/OCP 25/08 14,1 (contratante OCP); Veritá 01/09 13,5; Atlas 09/09 20,0; Neokemp 11/09 16,6; RTBD 16/09 dá 8. Três casas veem subida. MA: Qualitativa 19 a 25/08 14,4 e, DENTRO da IPSensus, 3,5 (15 a 20/08) para 16,4 (24 a 29/08) e 16,5 (05 a 10/09); Quaest 8,2, Veritá 6,1, IPPI 5,3, RTBD 1,2 não veem. A IPSensus de 24 a 29/08 muda de formato (sem Cidônio, sem indecisos publicados; soma dos candidatos 84,4 contra 95,8 na anterior), e Roseana, Fufuca e Lahesio caem enquanto Hilton sobe 10 pontos no bruto. | SC: **sem evento plausível encontrado** (busca incompleta): nenhuma linha de anotação na página; a alternância de contratante (NSC, OCP) é pista de casa, não de evento. MA: **não pesquisado na imprensa**; o salto dentro de uma casa e a mudança de formato da mesma casa pedem, nesta ordem: (i) registro no TSE das duas pesquisas (contratante), (ii) imprensa do MA de 19 a 29/08. Horário eleitoral (28/08) não explica: o campo termina em 29/08 e a Qualitativa fecha em 25/08. | W5, W4; `polls.json` (composição IPSensus). |
| 26/08 | PRES · Augusto Cury (z +4,2, PoderData) · SEN-BA · Coronel (z -3,6, Quaest) | PRES: PoderData 23 a 26/08 4,3 (3,3 em 12/08); Vox 27/08 2,9; a série de 12 a 25/08 estava em 0 a 3,3. BA: Quaest 9,6, casa baixa. | PRES: **evento candidato (schema)**: debate da Band em 23/08, com Cury e Renan Santos no palco e Lula, Flávio, Zema e Caiado ausentes (W1), seguido do episódio já registrado `cury-viral-2026-08-26` (não duplicado). BA: **artefato candidato**. | W1, busca 1 (CartaCapital e YouTube só no resultado). |
| 27/08 | PRES · Cury (z +3,1, Vox Brasil) · SEN-MS · Soraya (z +5,8, Ranking Brasil) | MS: Ranking 23 a 27/08 traz Soraya 32,2 no bruto (19,4 normalizado) contra 17,0 e 18,3 da própria casa em 12/08 e 09/09; a página da Wikipédia mostra o mesmo 32,2 (W6), então não é erro do repo; a leitura automática atribuiu os 20,2 da mesma linha a Nelsinho Trad (desistente em 31/07), sinal de linha com colunas suspeitas. | PRES: mesmo evento de 26/08. MS: **não confirmado na fonte primária**: pode ser transcrição trocada na Wikipédia ou número da própria Ranking; conferir no release e no registro TSE. | W6. |
| 28/08 | SEN-RJ · Crivella (z -7,9), Waguinho (z -7,3), Pedro Paulo (z -5,6), Veritá 24 a 28/08 | Lote Veritá com viés de casa pró-PL: Jordy 26,2 e Portinho 23,2 (as demais casas dão 10 a 18 e 8 a 16); Crivella 5,6, Waguinho 0,9, Pedro Paulo 5,0. No mesmo lote, GOV-RJ: Douglas Ruas +6,5 e Garotinho -4,2. Na rodada seguinte de cada casa Crivella volta a 16 a 18. | **Artefato candidato (choque comum do lote Veritá)**, já coberto por `h-2026-09-25-05`. O horário eleitoral começa em 28/08 (art. 47 da Lei 9.504), mas o campo (24 a 28/08) é anterior a quase toda a exposição: não explica. | `inflexoes.json` (lote), `hipoteses.json` (h-05). |
| 29/08 | SEN-MA · Hilton Gonçalo (z +6,5, IPSensus) | Idem 25/08. | Idem 25/08: **não pesquisado na imprensa**. | W4. |
| 30/08 | PRES · Cury (z +19,2, AtlasIntel e Nexus/BTG) | Atlas 25 a 30/08 7,8; Nexus 28 a 30/08 11,6; depois RTBD 10,9, Futura 10,9, Quaest 12,2, Datafolha 8,6, PoderData 10,8, Veritá 12,6. Quem paga: Flávio (Nexus 36,6 para 32,6; RTBD 31,5; Atlas 33,8, contra 37 a 40 antes), Zema (Atlas z -4,6) e Marçal (Atlas z -3,8); Lula cai menos (Nexus 43,0 para 38,9; Quaest 45,1 estável). Renan Santos, que dividiu o palco, NÃO sobe (Nexus 3,2; Futura 3,1; Quaest 3,7; Atlas 7,6 e RTBD 6,5 são as exceções). | **Evento candidato (schema)**: debate da Band 23/08 mais amplificação (registrada). Candidato secundário: **pesquisa-bomba** (publicação de Atlas e Nexus com Cury em 8 a 11 puxando as seguintes por adesão); as datas de divulgação não estão no dado (não confirmado). | W1, `polls.json`, `inflexoes.json`. |
| 31/08 | PRES · Cury (z +8,0, RTBD) · SEN-PB · Dr. Marcelo Queiroga (z -3,5, TDL) | PB: duas camadas de casas: Polêmica/Seta 19,0 (09/08) e RTBD 17,4 (22/08) contra Quaest 9,4 (24/08), TDL 7,4 (31/08), Anova 7,3 (05/09) e Data Ranking 8,3 (07/09). A TDL só repete a Quaest da semana anterior. | PRES: idem 30/08. PB: **não pesquisado**; a assinatura é de casa, mas quatro casas baixas em sequência também são compatíveis com queda real: só imprensa da PB decide. | Só dado local. |

Marcos de calendário que atravessam todas as corridas do período (não são eventos no sentido do registro, mas são covariáveis a declarar): 15/08 prazo de registro (a lista de candidatos congela: é por isso que a composição das pesquisas muda entre julho e agosto em RJ, MA e MS); 16/08 início da propaganda; 28/08 início do rádio e TV. Fonte: Lei 9.504/1997, não reconferida nesta sessão.

---

## (3) Bloco JSON dos eventos

### 3a. Array P1 no schema exato (passa em `src/eleicoes_eventos.py`: tipos e escopos válidos, alvo com sq da lista, sem `pre_especificado`)

```json
[
  {
    "id": "debate-band-2026-08-23",
    "data": "2026-08-23",
    "registrado_em": "2026-09-25",
    "tipo": "debate",
    "alvo": [280002551547, 280002540694],
    "direcao_esperada": "+",
    "escopo": "nacional",
    "fonte": {
      "url": "https://pt.wikipedia.org/wiki/Elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2026",
      "veiculo": "Wikipédia PT, tabela de debates (organização Band, TV Cultura, Estadão, TV Gazeta e Jovem Pan; mediação Adriana Araújo e Eduardo Oinegue); CartaCapital e o vídeo da Band no YouTube só vistos no resultado de busca, não abertos",
      "acesso": "2026-09-25"
    },
    "notas": "EXPLORATÓRIO (registrado em 25/09 para fato de 23/08). Participantes: Renan Santos e Augusto Cury; ausentes: Lula, Flávio Bolsonaro, Romeu Zema e Ronaldo Caiado; Samara não convidada (W1). A hipótese h-2026-09-25-10 do projeto, citando o Correio Braziliense de 23/09, diz que Caiado compareceu: divergência NÃO resolvida, conferir na fonte primária (Band). Mecanismo: exposição nacional sem os líderes no palco prevê '+' para os dois presentes. A direção para Cury foi escrita depois de ver o movimento (o dossiê o traz); a direção para Renan Santos foi escrita ANTES de eu computar a série dele e NÃO se confirma (Renan fica em 3 a 4 na maioria das casas; Atlas 7,6 e RTBD 6,5 são exceções), o que enfraquece 'exposição no debate' como causa suficiente e é consistente com a amplificação específica de Cury já registrada em cury-viral-2026-08-26 (não duplicada aqui). Implicação cruzada: quem paga é Flávio (3 a 5 pontos normalizados), Zema e Marçal, não Lula. Magnitude: o filtro subestima por construção; confie na data."
  },
  {
    "id": "pesquisa-bomba-cury-2026-08-30",
    "data": "2026-08-30",
    "registrado_em": "2026-09-25",
    "tipo": "pesquisa_bomba",
    "alvo": [280002551547],
    "direcao_esperada": "+",
    "escopo": "nacional",
    "fonte": {
      "url": "https://pt.wikipedia.org/wiki/Pesquisas_de_opini%C3%A3o_para_a_elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2026",
      "veiculo": "Wikipédia PT, página de pesquisas, via data/live/polls.json do projeto (ingest de 25/09); AtlasIntel 25 a 30/08 (n=5014, Cury 7,8 bruto) e Nexus/BTG 28 a 30/08 (n=2005, Cury 11,0 bruto); datas de divulgação não constam no dado",
      "acesso": "2026-09-25"
    },
    "notas": "EXPLORATÓRIO e SECUNDÁRIO. Candidato fraco, registrado porque é a única classe do schema que descreve o mecanismo de adesão (bandwagon): a publicação das primeiras pesquisas com Cury em 8 a 11 puxaria as seguintes. Teste: pesquisas com campo iniciado DEPOIS da divulgação (Quaest 30/08 a 01/09 12,2; Datafolha 01 a 02/09 8,6; PoderData 30/08 a 02/09 10,8; Veritá 01 a 04/09 12,6) contra as fielded antes ou durante (Atlas 7,8; Nexus 11,6; RTBD 27 a 31/08 10,9; Futura 27/08 a 01/09 10,9). No dado atual não há degrau claro entre os dois grupos: implicação não sustentada até aqui. Datas de divulgação 'não confirmadas'. Direção escrita depois de ver o movimento."
  },
  {
    "id": "debate-globo-2026-10-01",
    "data": "2026-10-01",
    "registrado_em": "2026-09-25",
    "tipo": "debate",
    "alvo": [280002551547, 280002551932],
    "direcao_esperada": "-",
    "escopo": "nacional",
    "fonte": {
      "url": "https://pt.wikipedia.org/wiki/Elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2026",
      "veiculo": "Wikipédia PT, tabela de debates (Globo, mediação César Tralli); agenda também citada no dossiê P1 como 'único restante do 1º turno, segundo a imprensa' e em h-2026-09-25-10 (Correio Braziliense, 23/09)",
      "acesso": "2026-09-25"
    },
    "notas": "PRÉ-ESPECIFICADO (registrado antes do fato). Condição escrita antes: se Lula e Flávio Bolsonaro estiverem no palco, os pequenos presentes (Cury, Caiado) perdem exposição relativa e a direção esperada é '-' para ambos, alinhada a h-2026-09-25-10; se um dos dois líderes faltar, a classe do evento passa a ser a da Band de 23/08 e a direção esperada vira '+' para os presentes, com o teste de replicação: Caiado, que faltou à Band, deveria subir desta vez. A página lista Lula, Caiado e Cury como convidados e Flávio e Zema como 'não convidados' (extração automática, parece inconsistente com o critério usual da Globo): NÃO confirmado; se Flávio não estiver, aplicar a segunda condição. Para Caiado a base é pequena (3,5) e a previsão é fraca. Janela de teste: destaques datados em 02 e 03/10 e o share publicado em 04/10."
  }
]
```

### 3b. Fora de P1 (setembro), no schema, para o dossiê P2 se ainda não estiver registrado

```json
[
  {
    "id": "marcal-registro-cassado-2026-09-11",
    "data": "2026-09-11",
    "registrado_em": "2026-09-25",
    "tipo": "decisao_judicial",
    "alvo": [280002553884],
    "direcao_esperada": "-",
    "escopo": "nacional",
    "fonte": {
      "url": "https://pt.wikipedia.org/wiki/Elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2026",
      "veiculo": "Wikipédia PT, cronologia (registro de Pablo Marçal cassado por decisão unânime; Leonardo Avalanche confirmado pelo PRTB); acórdão do TSE não aberto",
      "acesso": "2026-09-25"
    },
    "notas": "EXPLORATÓRIO. Fora do período P1; entra aqui só porque apareceu na mesma fonte e cabe no schema. Mecanismo: candidato cassado sai das pesquisas ou vira 'outros'; direção '-' para Marçal é trivial; a implicação testável é para onde vai o 0,4 a 3 dele (previsão pelo mecanismo: Flávio e Cury, não Lula). Decisão de tribunal, não da Wikipédia: conferir o acórdão."
  }
]
```

Também na mesma fonte (W3), sem sq disponível nesta sessão para preencher `alvo`: 11/09, "Anthony Garotinho (Republicanos) tem sua candidatura indeferida pelo TRE-RJ" (GOV-RJ, tipo decisao_judicial, direção '-' para Garotinho; previsão pelo mecanismo: o voto dele vai para Douglas Ruas (PL), não para Paes). Registrar no P2 com o sq de Garotinho.

### 3c. FORA do schema: classe "candidatura" (o validador recusa; não passar ao `eventos.json` sem decisão)

O `_tipos` do registro não tem a classe que domina agosto: entrada, saída, substituição, confirmação e indeferimento de candidatos. Proposta: adicionar `"candidatura"` a `_tipos`, com a mesma exigência de direção pré-escrita. Enquanto não houver decisão, os quatro eventos abaixo ficam aqui, no mesmo formato, para o parent decidir.

```json
[
  {
    "id": "canella-desiste-senado-rj-2026-08-03",
    "data": "2026-08-03",
    "registrado_em": "2026-09-25",
    "tipo": "candidatura",
    "alvo": [190002550182, 190002550184],
    "direcao_esperada": "?",
    "escopo": "UF",
    "fonte": {
      "url": "https://www.poder360.com.br/poder-eleicoes-2026/pl-tera-chapa-puro-sangue-para-o-senado-no-rj/",
      "veiculo": "Poder360, 04/08/2026 20h37 (Canella, ex-prefeito de Belford Roxo e favorito da coligação, recua para a Alerj após operação policial e detenção por porte ilegal de arma); data de 03/08 pela linha de anotação da Wikipédia PT (W3)",
      "acesso": "2026-09-25"
    },
    "notas": "EXPLORATÓRIO. Canella (UNIÃO) não tem sq na lista (não registrou), por isso não pode ser alvo; os alvos são quem recebe o efeito. Duas forças opostas sobre Waguinho: '+' porque Canella sucedeu Waguinho na prefeitura de Belford Roxo em 2024 e o eleitorado da Baixada fica livre (conhecimento anterior ao corte, não reconferido), e '-' porque a saída de Canella é o que viabiliza a chapa pura do PL (evento seguinte). Direção '?' declarada por isso. Data da operação policial: não consta."
  },
  {
    "id": "jordy-confirmado-pl-senado-rj-2026-08-04",
    "data": "2026-08-04",
    "registrado_em": "2026-09-25",
    "tipo": "candidatura",
    "alvo": [190002550184, 190002550182, 190002535142],
    "direcao_esperada": "-",
    "escopo": "UF",
    "fonte": {
      "url": "https://www.poder360.com.br/poder-eleicoes-2026/pl-tera-chapa-puro-sangue-para-o-senado-no-rj/",
      "veiculo": "Poder360, 04/08/2026 20h37 ('PL terá chapa puro-sangue para o Senado no RJ': Jordy e Portinho; decisão chancelada após a federação União Brasil-PP declarar neutralidade no Estado); linha de anotação da Wikipédia PT em 04/08 (W3)",
      "acesso": "2026-09-25"
    },
    "notas": "EXPLORATÓRIO. Direção '-' vale para Crivella e Waguinho (Republicanos, mesma faixa bolsonarista fora do PL); para Portinho (PL) a direção pelo mecanismo é '?' (pode perder para o colega de chapa ou ganhar com a consolidação): registrado com '-' no campo único e a ressalva aqui. Escrevi o mecanismo ao ver a mudança de composição (Jordy ausente em julho, presente na Datafolha de 18 a 21/08) e só depois computei as séries dentro de cada casa; o resultado está na seção 4. Parte do z de 21/08 é casa (Datafolha e Quaest baixas para Crivella), e o de 28/08 é o lote Veritá: o evento explica a queda de nível de julho para agosto, não os dois picos de z."
  },
  {
    "id": "convencao-avante-cury-2026-08-03",
    "data": "2026-08-03",
    "registrado_em": "2026-09-25",
    "tipo": "candidatura",
    "alvo": [280002551547],
    "direcao_esperada": "+",
    "escopo": "nacional",
    "fonte": {
      "url": "https://pt.wikipedia.org/wiki/Elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2026",
      "veiculo": "Wikipédia PT, cronologia (03/08 Avante oficializa Cury, vice Júlio Delgado; 05/08 Agir apoia)",
      "acesso": "2026-09-25"
    },
    "notas": "EXPLORATÓRIO. Registrado como controle negativo: a direção '+' (visibilidade da convenção) NÃO se confirma. Cury fica em 1,1 a 3,3 normalizado de 03 a 25/08 (PoderData 3,3; Quaest 2,4; Nexus 1,1; Datafolha 2,2; Veritá 2,3; Indexa 0,0; Gerp 1,1). Serve para dizer que a convenção sozinha não moveu nada e que o salto começa depois de 23/08."
  }
]
```

(O quarto marco, o prazo de registro de 15/08 com a propaganda de 16/08 e o rádio e TV de 28/08, é calendário e vale para todos os alvos; não recebe JSON.)

---

## (4) Cada evento: mecanismo, implicações cruzadas, replicação para a frente, fonte

### E1 · debate-band-2026-08-23 (schema, exploratório)

1. **Mecanismo.** [fato] Em 23/08 a Band, com TV Cultura, Estadão, TV Gazeta e Jovem Pan, realizou o primeiro debate presidencial do 1º turno; participaram Renan Santos e Augusto Cury; Lula, Flávio Bolsonaro, Zema e Caiado não foram (W1; a presença de Caiado é contestada por h-10 e não foi resolvida). [inferência] Sem os líderes, os dois presentes recebem exposição nacional que não teriam, e o eleitor anti-Lula que não gosta de Flávio ganha uma alternativa visível. [hipótese] O ganho de exposição só vira intenção de voto quando é amplificado depois (o crescimento de seguidores e de buscas que a W1 descreve, e a suspeita de amplificação não orgânica), o que explicaria por que Cury sobe e Renan não.
2. **Implicações cruzadas, conferíveis no dado do site.** Explica: PRES · Cury em 26/08 (PoderData), 27/08 (Vox), 30/08 (Atlas e Nexus, z +19,2), 31/08 (RTBD), e o nível de 8 a 12 em todas as casas de 30/08 a 04/09. Prevê e o dado confirma: quem paga é a faixa anti-Lula, Flávio (Nexus 36,6 para 32,6; RTBD 31,5; Atlas 33,8 contra 37 a 40 antes), Zema (Atlas 30/08 z -4,6, corroborado por Gerp, Indexa, PoderData e Veritá) e Marçal (Atlas z -3,8); Lula cai pouco (Nexus 43,0 para 38,9; Quaest 45,1 e Futura 42,4 estáveis). Prevê e o dado NÃO confirma: Renan Santos, presente no palco, deveria subir e não sobe (Nexus 3,2; Futura 3,1; Quaest 3,7; Datafolha 3,2; só Atlas 7,6 e RTBD 6,5 destoam; nenhum destaque positivo dele no detector no período). Também não explica o z -3,5 de Cury em 23/08 pela Indexa/Broadcast (0,0 no bruto), que é casa. Quem mais deveria ter se movido e não se moveu: Caiado (se esteve no palco, como diz h-10, deveria subir; fica em 3,3 a 6,3, sem destaque), o que favorece a versão da W1 (Caiado ausente) ou a hipótese de que o debate sozinho não move.
3. **Replicação para a frente.** Próxima ocorrência da classe: debate da Globo em 01/10 (E3, pré-especificado): com Lula e Flávio no palco, '-' para Cury e Caiado; sem um dos dois líderes, '+' para os presentes, e o teste limpo é Caiado, que faltou à Band. O debate CNN/SBT de 14/09 foi cancelado (W1), por isso não há ocorrência intermediária. Pesquisas de referência para julgar: destaques datados em 02 e 03/10 e o share publicado em 04/10.
4. **Fonte.** W1, https://pt.wikipedia.org/wiki/Elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2026, acesso 2026-09-25. CartaCapital (opinião) e YouTube (Band) só no resultado de busca: título e URL na seção 1, conteúdo não confirmado.

### E2 · pesquisa-bomba-cury-2026-08-30 (schema, exploratório, secundário)

1. **Mecanismo.** [fato] As primeiras pesquisas com Cury em 8 a 11 foram AtlasIntel (campo 25 a 30/08, 7,8) e Nexus/BTG (28 a 30/08, 11,0), seguidas por RTBD, Futura, Quaest, Datafolha, PoderData e Veritá em 8,6 a 12,6 (polls.json). [hipótese] A publicação de um número inédito para um candidato de 2 muda a percepção de viabilidade e puxa as pesquisas seguintes (adesão). [inferência] Se isso vale, as pesquisas com campo iniciado depois da divulgação deveriam dar mais que as fielded antes ou durante.
2. **Implicações cruzadas.** Explica, em tese, a persistência de 30/08 a 04/09. Não explica o início (PoderData 23 a 26/08 e o próprio campo da Atlas, anteriores a qualquer divulgação). O teste está desenhado nas notas do JSON e, no dado atual, não mostra degrau: Quaest 12,2 e Veritá 12,6 depois, Nexus 11,6 e Futura 10,9 antes ou durante. Datas de divulgação não constam no dado: não confirmado.
3. **Replicação para a frente.** A próxima AtlasIntel com campo entre 26/09 e 03/10, já coberta por h-2026-09-25-04 (direção '-' para os pequenos no detector); e as últimas Datafolha e Quaest antes de 04/10 (datas não confirmadas), com a mesma pergunta: as pesquisas fielded depois delas repetem o número?
4. **Fonte.** Página de pesquisas presidenciais da Wikipédia PT via polls.json (URL no JSON), acesso do ingest 2026-09-25; não aberta por mim nesta sessão.

### E3 · debate-globo-2026-10-01 (schema, PRÉ-ESPECIFICADO)

1. **Mecanismo.** [fato] A Globo marcou debate para 01/10, mediação de César Tralli (W1); o dossiê e h-10 o tratam como o único restante do 1º turno. [inferência] Com os dois líderes no palco, a cobertura se concentra neles e os pequenos perdem exposição relativa; sem um deles, repete-se a assimetria da Band. [hipótese] Cury, que já devolve o pico de agosto (h-01), não tem segundo salto; Caiado, se a Band lhe foi negada, tem o teste mais limpo da classe.
2. **Implicações cruzadas (a conferir depois de 01/10).** Se '-' para Cury e Caiado se confirmar com Lula e Flávio presentes, o padrão da classe é "debate só move pequeno quando líder falta". Se Cury subir mesmo com os líderes, a causa de agosto não foi o debate, e sim a amplificação, e o registro deve ser relido. Quem não deveria se mover: Renan Santos (não convidado, segundo a página).
3. **Replicação.** É a própria replicação da classe de E1. Depois dela, só o 2º turno (25/10), fora do escopo.
4. **Fonte.** W1, acesso 2026-09-25. A lista de convidados na página é extração automática e parece inconsistente (Flávio como "não convidado"): não confirmado; conferir na Globo.

### C1 · canella-desiste-senado-rj-2026-08-03 (fora do schema, exploratório)

1. **Mecanismo.** [fato] Canella (UNIÃO), ex-prefeito de Belford Roxo e "então favorito da coligação", desistiu do Senado para disputar a Alerj depois de operação policial e detenção por porte ilegal de arma (W2; data da operação não consta; anotação de 03/08 em W3). [fato, conhecimento anterior ao corte, não reconferido] Canella sucedeu Waguinho na prefeitura de Belford Roxo em 2024, no mesmo grupo político. [inferência] O voto da Baixada que ia para Canella fica livre, e o destino natural é Waguinho; ao mesmo tempo, a saída de Canella é o que abre a chapa pura do PL (C2), que tira de Waguinho. Direção '?' por isso.
2. **Implicações cruzadas.** Nas pesquisas de julho, Canella tinha 14,2 (Paraná) e 9,4 (Prefab) no bruto; se o voto dele fosse para Waguinho, Waguinho subiria de julho para agosto; ele CAI em todas as casas (Quaest 10,8 para 5,1; Prefab 14,0 para 9,3; RTBD 12,7 para 10,3; Paraná parado). Ou seja: o efeito C2 domina, ou o voto de Canella não era transferível. Canella não tem sq: o site não mede a saída dele.
3. **Replicação.** Próxima saída de candidato com base regional até 04/10: nenhuma marcada; a classe reaparece se o TRE ou o TSE indeferir alguém (ver Garotinho, 11/09, GOV-RJ, em 3b).
4. **Fonte.** W2 (Poder360, 04/08/2026, acesso 2026-09-25) e W3 (Wikipédia PT, acesso 2026-09-25).

### C2 · jordy-confirmado-pl-senado-rj-2026-08-04 (fora do schema, exploratório)

1. **Mecanismo.** [fato] Em 04/08 o PL confirmou Carlos Jordy ao Senado, formando chapa pura com Carlos Portinho, depois de a federação União Brasil-PP declarar neutralidade no Estado e inviabilizar chapa mista (W2, W3). [fato] Jordy aparece pela primeira vez na Datafolha de 18 a 21/08; em julho as pesquisas traziam Canella e Mauro Campos (NOVO) e não Jordy (polls.json). [inferência] Dois candidatos do PL captam o voto bolsonarista que, sem eles, ia para Crivella e Waguinho (Republicanos); a direção prevista é '-' para os dois e '?' para Portinho.
2. **Implicações cruzadas (computadas depois de escrever o mecanismo).** Explica: SEN-RJ 21/08 (Crivella z -5,0, Waguinho z -3,6, Datafolha) como queda de NÍVEL de julho para agosto, dentro de casa: Quaest Crivella 24,3 para 15,4 e Waguinho 10,8 para 5,1; RTBD 26,8 para 17,9 e 12,7 para 10,3; Paraná 24,1 para 19,7; Prefab Waguinho 14,0 para 9,3. Jordy entra com 10,3 a 17,9 e o detector o marca positivo em 24/08 (Quaest z +3,0). Prevê e confirma: Portinho não cai (Quaest 10,8 para 12,8; Paraná 8,7 para 10,0; Prefab 5,8 para 7,7; RTBD é exceção, 19,7 para 11,5, mas mudou de 5 para 8 candidatos). Prevê e confirma em parte: a esquerda não deveria se mover; Benedita fica parada em Paraná (28,2 para 27,8) e Prefab (30,9 para 30,8), mas cai na Quaest (32,4 para 25,6), e Monica Benicio sobe na Quaest (10,8 para 12,8): a normalização espalha mecanicamente a entrada de um candidato por todos, então a prova forte é a assimetria (Crivella e Waguinho perdem mais que Benedita e Portinho), não o sinal isolado. NÃO explica: os picos de z de 21/08 (Datafolha é casa baixa para Crivella: 11,3 nas duas rodadas) e de 28/08 (lote Veritá, h-05); e Pedro Paulo (PSD) em 24/08 (Quaest 7,7), que o mecanismo não prevê e que as outras casas não veem.
3. **Replicação para a frente.** Não há nova entrada de candidato possível até 04/10 (lista congelada em 15/08); a classe reaparece só por indeferimento ou substituição. No RJ, o indeferimento de Garotinho pelo TRE (11/09, GOV-RJ) é a ocorrência da classe no P2, com direção pré-escrita aqui: voto de Garotinho vai para Douglas Ruas (PL), '+' para Ruas, '0' para Paes. Também vale como replicação a hipótese h-2026-09-25-09 (Jordy à frente de Portinho na 2ª vaga), que é o mesmo mecanismo visto de dentro do PL.
4. **Fonte.** W2, https://www.poder360.com.br/poder-eleicoes-2026/pl-tera-chapa-puro-sangue-para-o-senado-no-rj/, publicado 04/08/2026 20h37, acesso 2026-09-25; W3, acesso 2026-09-25. Revista Fórum e Congresso em Foco só no resultado de busca.

### C3 · convencao-avante-cury-2026-08-03 (fora do schema, controle negativo)

1. **Mecanismo.** [fato] Convenção do Avante oficializou Cury em 03/08, com Júlio Delgado de vice; o Agir aderiu em 05/08 (W1). [hipótese] Convenção dá visibilidade e deveria render '+'.
2. **Implicações cruzadas.** Não se confirma: Cury fica em 0,0 a 3,3 normalizado de 03 a 25/08 em oito casas. Serve para datar o início do movimento depois de 23/08 e para descartar a convenção como causa.
3. **Replicação.** Nenhuma (convenções acabaram em 05/08).
4. **Fonte.** W1, acesso 2026-09-25; Wikipédia EN "Augusto Cury" só no resultado de busca.

---

## (5) O que não dá para afirmar

1. **Causa.** Nenhum dos eventos acima causou movimento algum, até prova do estudo de evento (M3) com janela placebo. Todos os eventos passados nascem exploratórios pela regra do projeto. Nos exploratórios, a direção do alvo principal foi escrita depois de ver o movimento (o dossiê o traz); só as direções dos outros candidatos (Renan, Caiado, Zema, Marçal, Flávio, Lula; Portinho, Benedita, Monica) foram escritas antes de computar as séries, e são elas que valem alguma coisa. E3 é o único pré-especificado.
2. **Presença de Caiado na Band.** W1 (acesso hoje) diz ausente; h-2026-09-25-10, citando o Correio Braziliense de 23/09, diz presente. Não resolvido; muda a leitura de E1 (Caiado não subiu: se estava lá, é mais uma implicação falha da "exposição").
3. **Convidados da Globo.** A extração de W1 lista Flávio e Zema como "não convidados". Parece inconsistente com o critério usual da emissora. Não confirmado. E3 carrega a condição.
4. **Percentuais lidos da Wikipédia por extração automática.** Divergem do polls.json em SEN-RJ (Datafolha 18 a 21/08: 9/12/12 para Pedro Paulo, Jordy e Portinho na leitura, 6/8/8 no repo; Prefab 20 a 23/08 com números repetidos da rodada de setembro) e em SEN-MS (coluna de 20,2 atribuída a Nelsinho Trad). Não usei esses números; usei o polls.json. A linha Ranking Brasil 23 a 27/08 (Soraya 32,2) pede conferência humana na fonte primária: pode ser transcrição trocada na Wikipédia ou número da própria casa.
5. **"Véritas" e "Veritá" no MA.** Casas distintas na página; sem alias no repo. Se forem a mesma, as inflexões de 10 e 11/08 mudam de artefato para reversão real dentro de casa, sem evento encontrado.
6. **Lacunas por orçamento (não pesquisado, e não "não existe"):** imprensa e TSE para Hilton Gonçalo (MA, 19 a 29/08: salto dentro da IPSensus com mudança de formato da mesma casa; conferir contratante no registro TSE), Merísio (SC, 23/08 a 09/09), Soraya (MS, 21 a 27/08), Queiroga (PB, 22 a 31/08), Bueno (GO), Araceli (PA), Coronel (BA). Agência Lupa e Aos Fatos não foram consultadas para nenhuma data; a coluna "peca_desinformacao" do período fica vazia por falta de busca, não por ausência de fato. Recomendo uma sessão de discovery só para MA, SC e MS, nesta ordem.
7. **Artefato de ingestão no DF.** Confirmado no dado local (aliases contaminados nas pesquisas IGAPE e Paraná de 17 a 19/07; 3 de 6 sq casados; Celina em 66 a 71 normalizado; inovações negativas em 01, 15 e 18/08). Registrado como tarefa separada (`task_410cc639`), sem tocar no repositório. O mesmo padrão aparece em GOV-BA, GOV-MA, GOV-MT, GOV-PI, SEN-MG, SEN-RJ (março e abril), SEN-RN, SEN-RO e SEN-RR; as inflexões dessas corridas nas datas vizinhas às pesquisas contaminadas merecem a mesma suspeita.
8. **Schema.** A classe "candidatura" (entrada, saída, confirmação, substituição, indeferimento) não existe em `_tipos`, e é a que domina agosto (RJ, MA, MS, DF, presidencial). Sem ela, o registro fica cego para o tipo de evento mais frequente do mês do registro. Os quatro itens de 3c dependem dessa decisão.
9. **Horário eleitoral (28/08).** Marco de calendário, não evento; não explica nenhuma inflexão do período porque os campos que disparam em 28 a 31/08 são anteriores ou simultâneos à primeira exposição. Vale como covariável a partir de setembro.
10. **Magnitude.** Todos os Δ do detector são subestimados por construção (passeio em logit calibrado a 50%); usei a data e o sinal, e as séries normalizadas para o tamanho.
