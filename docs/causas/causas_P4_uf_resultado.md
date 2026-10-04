# Cruzamento com notícias · P4 (24/09 a 04/10/2026) · corridas estaduais · resultado

Gerado em 2026-10-04 (dia do 1º turno) a partir do dossiê `causas_P4.md`, do dado local (`data/live/polls.json` com updated_at 2026-10-03 e `data/eleicoes/inflexoes.json` com as_of 2026-10-02) e de buscas web em português. Escopo: GOV-DF, SEN-DF, GOV-RJ, SEN-RJ, SEN-MG, GOV-AM, SEN-RO, SEN-RN, mais o desfecho dos dois debates estaduais pré-especificados (Globo Minas e TV Cabo Branco, 29/09). A presidencial ficou com outro agente e não foi pesquisada. Nada no repositório foi modificado além deste arquivo.

Regra aplicada: só entra no JSON evento cuja matéria foi aberta com sucesso (WebFetch) ou tabela da Wikipédia PT conferida pela revisão. Corte de conhecimento do modelo: junho de 2026. Todo fato datado de setembro e outubro vem das fontes listadas abaixo.

---

## 1. Fontes abertas (todas com acesso em 2026-10-04)

### Fontes locais (só leitura)
- `data/live/polls.json` (updated_at 2026-10-03): séries por casa e cenário, tamanho do lote por (instituto, campo_fim).
- `data/eleicoes/inflexoes.json` (as_of 2026-10-02): destaques depois de 29/09 nas corridas dos debates.
- `data/eleicoes/eventos.json`: schema e eventos já registrados (para não duplicar).

### Wikipédia PT (wikitext baixado pela API, revisão citada)
| # | Página | Revisão (timestamp) | O que rendeu |
|---|---|---|---|
| W1 | [Eleições distritais no Distrito Federal em 2026](https://pt.wikipedia.org/w/index.php?title=Elei%C3%A7%C3%B5es_distritais_no_Distrito_Federal_em_2026&oldid=73116640) | 73116640 (2026-10-03 21:13 UTC) | tabela de debates do governo: Band 09/08, Correio/TV Brasília 01/09, Metrópoles 10/09, TV Globo DF 29/09 (Celina "Ausente", Arruda "Impedido", Caputo, Grass, Belmonte e Cappelli presentes). Não lista debate da Record. |
| W2 | [Eleições estaduais em Minas Gerais em 2026](https://pt.wikipedia.org/w/index.php?title=Elei%C3%A7%C3%B5es_estaduais_em_Minas_Gerais_em_2026&oldid=73120756) | 73120756 (2026-10-04 12:38 UTC) | Globo Minas 29/09, 22h30, mediação Liliana Junger: Kalil, Cleitinho, Roscoe, Gabriel, Simões e Patrus "Presente" |
| W3 | [Eleições estaduais na Paraíba em 2026](https://pt.wikipedia.org/w/index.php?title=Elei%C3%A7%C3%B5es_estaduais_na_Para%C3%ADba_em_2026&oldid=73100406) | 73100406 (2026-10-01 20:41 UTC) | TV Cabo Branco 29/09, mediação Graziela Azevedo: Cícero, Efraim e Lucas "Presente" |
| W4 | [Eleições estaduais no Rio de Janeiro em 2026](https://pt.wikipedia.org/w/index.php?title=Elei%C3%A7%C3%B5es_estaduais_no_Rio_de_Janeiro_em_2026&oldid=73115098) | 73115098 (2026-10-03 17:24 UTC) | Record Rio 21/09 "Cancelado", TV Globo RJ 29/09, mediação Ana Paula Araújo: Garotinho, Ruas, Paes, Siri e Marinho "Presente" (linha sem referência) |
| W5 | [Eleições estaduais no Amazonas em 2026](https://pt.wikipedia.org/w/index.php?title=Elei%C3%A7%C3%B5es_estaduais_no_Amazonas_em_2026&oldid=73114007) | 73114007 | sem seção de debates nem cronologia de setembro |
| W6 | [Eleições estaduais em Rondônia em 2026](https://pt.wikipedia.org/w/index.php?title=Elei%C3%A7%C3%B5es_estaduais_em_Rond%C3%B4nia_em_2026&oldid=73104307) | 73104307 | sem debates nem cronologia |
| W7 | [Eleições estaduais no Rio Grande do Norte em 2026](https://pt.wikipedia.org/w/index.php?title=Elei%C3%A7%C3%B5es_estaduais_no_Rio_Grande_do_Norte_em_2026&oldid=73115714) | 73115714 | debates só de governador, desistências de candidatos a governador em 26/09 (Rodrigo de Bolsonaro, apoio a Álvaro Dias) e 30/09 (Robério Paulino, PSOL, apoio a Cadu Xavier), fora do escopo |

### Matérias abertas (WebFetch com sucesso)
| # | Veículo, data | URL | O que rendeu |
|---|---|---|---|
| F1 | O Hoje, 29/09 | https://ohoje.com/2026/09/29/celina-avalia-participar-de-debate-da-globo-desta-terca-29-e-diz-que-nao-quer-briga-em-campo-aberto/ | Celina "avalia" ir à Globo, chama o debate do Metrópoles de agressão às mulheres, e a nota diz que ela faltou ao debate da Record em setembro alegando funções do cargo (data da Record não dada) |
| F2 | Brasil de Fato, 24/09 17h46 | https://www.brasildefato.com.br/2026/09/24/candidatos-ao-governo-do-df-reagem-a-saida-de-arruda-da-disputa-apos-decisao-do-tse/ | TSE 5 a 2 contra Arruda em 24/09, Belmonte vai "procurar o Arruda" para buscar apoio, Arruda diz que não fará recomendação de voto |
| F3 | Congresso em Foco, 29/09 | https://www.congressoemfoco.com.br/noticia/122700/real-time-celina-leao-tem-47-contra-26-de-leandro-grass-no-df | Real Time Big Data DF (24 a 28/09, DF-04637/2026): Celina 47, Grass 26, Belmonte 10, Cappelli 4 |
| F4 | Jornal de Brasília, 30/09 | https://jornaldebrasilia.com.br/brasilia/sem-celina-ultimo-debate-tem-criticas-ao-governo-e-afagos-a-arruda/ | debate da Globo sem Celina, Caputo e Belmonte criticam a exclusão de Arruda ("tapetão") |
| F5 | NC News, 30/09 | https://ncnews.com.br/?p=54903 | debate TV Globo DF em 29/09, mediação Heraldo Pereira, presentes Caputo, Grass, Belmonte e Cappelli, Celina ausente, BRB como tema central |
| F6 | Jornal de Brasília, 29/09 | https://jornaldebrasilia.com.br/brasilia/celina-tem-39-contra-23-de-grass-na-disputa-pelo-gdf-diz-quaest/ | Quaest DF (25 a 28/09): Celina 39, Grass 23, Belmonte 9, Cappelli 3, Senado: Michelle 26, Leila 20, Kicis 18, Kokay 16, Coelho 1 |
| F7 | Metrópoles (coluna Grande Angular), 22/08 | https://www.metropoles.com/colunas/grande-angular/sebastiao-coelho-se-diz-injusticado-apos-atrito-com-malafaia | contexto: atrito Coelho x Malafaia, Coelho recusou convites de Michelle e Kicis (fora da janela) |
| F8 | Bombeiros DF (blog), 14/09 | https://www.bombeirosdf.com.br/2026/09/disparada-sebastiao-coelho-chega-13-e.html | Real Time Big Data SEN-DF (04 a 08/09): Coelho 10 (fora da janela, contexto de casa) |
| F9 | NC News, 28/09 13h41 | https://ncnews.com.br/?p=54036 | Michelle pede votos para si e para Bia Kicis em 28/09, cita Coelho com respeito mas diz que a chapa dela tem "possibilidade de vencer" |
| F10 | Brasil de Fato, 28/09 17h33 | https://www.brasildefato.com.br/2026/09/28/eleicoes-no-df-arruda-rompe-com-apoio-do-psd-a-celina-leao-e-rejeita-alianca/ | PSD oficializa apoio a Celina em 28/09 (Paulo Octávio), Arruda, em vídeo de 27/09, recusa ("Eles não terão o meu apoio") e ataca o governo e o BRB |
| F11 | SBT News, 18/09 | https://sbtnews.sbt.com.br/noticia/politica/celina-acionara-cvm-contra-lula-por-fala-sobre-crise-do-brb | Lula diz que o governo federal não vai pôr dinheiro no BRB, Celina anuncia representação na CVM |
| F12 | Jornal de Brasília, 17/09 5h43 | https://jornaldebrasilia.com.br/brasilia/leandro-grass-divide-palanque-com-lula-em-ato-de-campanha-em-ceilandia/ | Lula em ato em Ceilândia "ontem" (16/09) pede voto em Grass, Kokay e Leila e cita o caso Master-BRB contra Celina |
| F13 | Brasil de Fato, 25/09 17h03 | https://www.brasildefato.com.br/2026/09/25/debate-ao-senado-no-df-tem-ausencia-de-tres-candidatas-e-defesa-do-fim-da-escala-6x1/ | debate Metrópoles do Senado DF em 24/09: presentes Kokay, Guto Felício, Marley, Ronaldo Fonseca (PSD) e Coelho, ausentes Michelle, Kicis e Leila |
| F14 | Jornal da Paraíba, pré-debate | https://jornaldaparaiba.com.br/_/221231 | debate TVs Cabo Branco e Paraíba, 29/09, 22h15, Graziela Azevedo: Cícero, Efraim, Lucas |
| F15 | Jornal da Paraíba, pós-debate (checagem) | https://jornaldaparaiba.com.br/_/221299 | checagem de falas de Cícero, Efraim e Lucas no debate de 29/09 (prova de que os três foram) |
| F16 | O Tempo, 30/09 | https://www.otempo.com.br/eleicoes/2026/governadores/2026/9/30/cleitinho-sai-da-defensiva-em-debate-da-globo-patrus-se-atrapalha-e-simoes-abandona-zema-na-globo | Globo MG 29/09: seis candidatos, Simões ataca Cleitinho e declara voto em Flávio Bolsonaro, Gabriel ataca Patrus |
| F17 | Por Dentro de Minas, 09/2026 | https://pordentrodeminas.com.br/noticias/eleicoes/2026/09/candidatos-ao-governo-de-minas-trocam-criticas-no-ultimo-debate-antes-do-1o-turno/ | confirma os seis presentes em 29/09 |
| F18 | Bahia Notícias, 30/09 | https://www.bahianoticias.com.br/noticia/321727-candidato-bolsonarista-ultrapassa-ex-prefeita-petista-e-aecio-neves-e-assume-lideranca-para-o-senado-em-minas | Quaest SEN-MG (25 a 28/09, MG-02019/2026): Sávio 14, Marília 13, Aécio 12, Viana 12, Aro 6, Superman 4, manchete de liderança de Sávio |
| F19 | O Fator | https://ofator.com.br/?p=71148 | dobradinha Sávio + Superman anunciada em 12/09 em Januária, articulada por Nikolas (fora do raio) |
| F20 | Diário do Comércio, 23/09 | https://diariodocomercio.com.br/politica/domingos-savio-superman-pedem-desistencia-zema/ | Sávio e Superman pedem que Zema desista e apoie Flávio no 1º turno, o gesto incomodou a direção do Novo |
| F21 | O Fator, 10/08 | https://ofator.com.br/?p=69048 | gravação de Sávio com Flávio para o horário eleitoral em 11/08 (fora da janela) |
| F22 | Tribuna do Sertão, 30/09 | https://www.tribunadosertao.com.br/poder-e-governo/2026/09/30/987842-eduardo-paes-e-douglas-ruas-se-enfrentam-em-debate-da-globo-com-mencoes-a-lula-cabral-castro-e-bacellar | Globo RJ 29/09: Paes, Ruas, Garotinho, Siri e Marinho, Marinho faz "dobradinha" com Ruas em educação |
| F23 | Diário do Rio, 28/09 | https://diariodorio.com/politica/2026/09/28/globo-realiza-debate-para-governador-do-rio-nesta-terca-saiba-quem-participa-e-como-assistir.html | pré-debate lista quatro convidados (Paes, Ruas, Garotinho, Siri), sem Marinho: conflita com F22 e W4 |
| F24 | Tempo Real RJ, 29/09 | https://temporealrj.com/tre-rj-defere-candidatura-waguinho-ao-senado/ | TRE-RJ defere por unanimidade o registro de Waguinho em 29/09, rejeitando as impugnações do MPE (contas de 2021 e 2022 rejeitadas, menção em inquérito da Draco) |
| F25 | Amazônia Sem Fronteira, 30/09 | https://amazoniasemfronteira.com.br/david-almeida-e-contestado-ao-vivo-durante-debate-na-rede-amazonica/ | no debate da Rede Amazônica (29/09) David Almeida acusa empresa ligada a Cidade e é contestado (documentos societários não mostram a família de Cidade), cita também debate da TV A Crítica em 28/09 |
| F26 | Gazeta da Amazônia, 30/09 | https://gazetadaamazonia.com.br/30/09/2026/debate-ao-governo-do-amazonas-2/ | debate Rede Amazônica 29/09, mediação César Menezes, cinco presentes (Aziz, Almeida, Cidade, Maria do Carmo, Isael), acusações a Almeida (R$ 16 milhões para empresas de familiares, viagem ao Caribe, tributos com Manaus) |
| F27 | DGABC, 04/08 | https://www.dgabc.com.br/Noticia/4339208/stf-suspende-condenacao-de-ex-senador-acir-gurgacz-e-libera-candidatura-nas-eleicoes | Nunes Marques suspende em 03/08 a condenação de Acir Gurgacz e libera a candidatura ao Senado RO (fora da janela) |

Abertas sem rendimento útil: Metrópoles/Correio sobre Malafaia x Coelho no blog do Correio (HTTP 404), g1 (bloqueado para o WebFetch, por isso a página de íntegra do debate de MG citada pela Wikipédia não foi aberta, a confirmação veio de F16 e F17).

---

## 2. Tabela data → evento(s) candidato(s) ou "sem evento plausível"

Convenção: lote = corridas que o instituto disparador publicou com o mesmo `campo_fim` (contado em `polls.json`). Raio de busca: 0 a 7 dias antes da data. Eventos novos têm id na seção 3. Datas só presidenciais (25/09) estão fora do escopo.

| Data | Destaques UF do dossiê | Disparador · lote · leitura de casa | Evento(s) candidato(s) no raio | Leitura |
|---|---|---|---|---|
| **24/09** | GOV-DF Grass +1,04 (z +4,4) | Veritá, lote 16 (inclui GOV-DF e SEN-DF). Veritá DF já veio sem Arruda e com 4 nomes: Grass 32,0 contra 17 a 23 nas outras casas | `arruda-tse-confirma-indeferimento-2026-09-24` (já registrado, mesmo dia), `lula-ato-ceilandia-grass-2026-09-16` (dia −8, um dia fora do raio) | Casa (Veritá alta para Grass) mais troca de cenário. Nas casas de referência, no cenário sem Arruda, Grass fica parado (Quaest 23→23, Datafolha 23→22). |
| **24/09** | SEN-RN Rafael Motta Δ +0,03 (z −3,2) | Seta, lote 2 (GOV-RN, SEN-RN), Seta tem Samanda 21 e Zenaide 40,3, fora das demais | **sem evento plausível encontrado**. Procurado: Rafael Motta, Styvenson, Zenaide, Samanda, Senado RN em setembro (só pesquisas Exatus) | Δ de nível nulo: resíduo de casa. |
| **26/09** | GOV-DF Celina +1,91 (z +3,3) | IGAPE, lote 2 (GOV-DF, SEN-DF). IGAPE 26/09 tem dois cenários (com Arruda a 8,3 e sem Arruda) | `arruda-tse-confirma-indeferimento-2026-09-24` (dia −2) | A saída de Arruda redistribui 16 a 20 pontos. Até 24/09 toda casa publicava cenário com Arruda, depois de 24/09 o cenário principal é sem ele. |
| **27/09** | GOV-AM David Almeida −0,41 (z −3,4) | Viva Voz, lote 2 (GOV-AM, SEN-AM), estreia da casa na série (10,6). Em 25/09 a Phoenix tinha dado 27,57 (destaque +4,76, não corroborado) | **sem evento plausível encontrado** no raio 20 a 27/09. Procurado: David Almeida + TRE, denúncia, operação, debate, setembro. Só achado fora do raio: TRE-AM sobre propaganda antecipada (pré-campanha, sem data aberta) e acusações de 09/08 | O destaque negativo é a volta do nível depois do salto da Phoenix: casa. Nas casas de referência ele está estável em 10 a 15 (Quaest 11, PoderData 11, Pontual 14,9→14,5). |
| **28/09** | GOV-DF Celina +1,10, Grass +0,46, Belmonte +0,23 | Correio/Opinião (lote 2), Quaest (lote 10), Real Time (lote 8) | `arruda-tse-confirma-indeferimento-2026-09-24` (dia −4), `psd-apoia-celina-arruda-rejeita-2026-09-28` (mesmo dia, campo já fechado) | Arruda explica a maior parte. Mas há subida também dentro do cenário sem Arruda: Quaest Celina 34→39 e Belmonte 7→9, Datafolha Celina 42→46 (01/10) e Belmonte 7→9. Grass não sobe dentro do cenário. |
| **28/09** | SEN-DF Coelho −0,16 (z −3,9) | Quaest (lote 10) e Real Time (lote 8) | `debate-metropoles-sen-df-2026-09-24` (dia −4, direção '+' para Coelho, contrária), `michelle-pede-voto-kicis-2026-09-28` (mesmo dia) | Quaest 2→1 e Correio 2,1→2,3: dentro do erro. Real Time 11 é casa. |
| **28/09** | GOV-RJ Marinho −0,05 (z −3,5) | Quaest, lote 10: Marinho 0,0 | **sem evento plausível encontrado**. Procurado: André Marinho setembro, debate, Quaest | Δ quase nulo, Quaest 1→0 é arredondamento. Marinho oscila 1 a 4 entre casas. |
| **28/09** | SEN-MG Sávio +0,36, Superman +0,13 | Quaest, lote 10: Sávio 10→14, Superman 1→4 | `savio-superman-pedem-zema-desistir-2026-09-23` (dia −5) | Real Time confirma (16→20 e 4→8 em 02/10), Datafolha 01/10 NÃO (Sávio 9→9, Superman 2→2). |
| **28/09** | SEN-RJ Waguinho −0,11 | Quaest, lote 10: 3→2 | **sem evento plausível com direção '−'**. `tre-rj-defere-waguinho-2026-09-29` é posterior e de direção oposta | Queda pequena e consistente entre casas (Real Time 5→3, Datafolha 3→2, Gerp 2). Lote é a hipótese dominante. |
| **29/09** | GOV-DF Celina +0,59, Grass +0,21, Belmonte +0,11 | IGAPE, lote 2 | os mesmos de 28/09, `michelle-pede-voto-kicis-2026-09-28` não se aplica ao governo | Mesmo mecanismo de 26 e 28/09. O debate da Globo DF é da noite de 29/09, depois do campo. |
| **29/09** | SEN-DF Coelho −0,16 (z −5,8) | IGAPE, lote 2: Coelho 8,6 (26/09) → 2,3 (29/09), enquanto Michelle 40,8→50,2 e Kicis 30,9→36,4 na mesma casa | `michelle-pede-voto-kicis-2026-09-28` (dia −1) | O único movimento grande é dentro da IGAPE e casa com o mecanismo de voto útil. Real Time 28/09 ainda dá 11. |
| **29/09** | SEN-RJ Waguinho −0,06 | Real Time, lote 8: 3 | sem evento com direção '−' (ver 28/09) | Lote. |
| **29/09** | SEN-RO Acir −0,04 (z −3,6) | Real Time, lote 8: Acir 5, Veritá dá 14 a 15 | **sem evento plausível encontrado**. Procurado: Acir Gurgacz + TRE-RO, STF, debate, setembro (só a liminar do STF de 03/08) | Casa (Veritá alta para Acir), Δ quase nulo. |
| **30/09** | GOV-RJ Marinho −0,02, SEN-RJ Waguinho −0,03 | Gerp, lote 4 (GOV-RJ, GOV-SP, SEN-RJ, SEN-SP) | `debate-globo-gov-rj-2026-09-29` (dia −1, direção '+' para Marinho, contrária), `tre-rj-defere-waguinho-2026-09-29` (dia −1, direção '+', contrária) | Os dois eventos do raio apontam na direção oposta ao movimento: não explicam. Lote. |
| **01/10** | GOV-AM David Almeida −0,08 (z −4,0) | Real Time, lote 8: Almeida 9 | `debate-redeamazonica-gov-am-2026-09-29` (dia −2) | Δ pequeno. O campo da Real Time termina 01/10 e pode ter começado antes do debate: exposição parcial. |
| **02/10** | SEN-DF Coelho −0,03 (z −5,5) | Exata GO, lote 1: Coelho 1,7 | `michelle-pede-voto-kicis-2026-09-28` (dia −4) | Nível já baixo em todas as casas, menos Real Time e IGAPE de antes de 29/09. |
| **02/10** | SEN-MG Sávio +0,10, Superman +0,03 | Real Time, lote 1 (só SEN-MG): Sávio 20, Superman 8 | `quaest-savio-lidera-sen-mg-2026-09-30` (dia −2), `savio-superman-pedem-zema-desistir-2026-09-23` (dia −9, fora do raio) | Divulgação da Quaest com Sávio "na liderança" é candidata a efeito de manada. |

### 2b. Desfecho dos debates pré-especificados (sem evento novo, como pede o dossiê)

| Evento já registrado | Convidados | Compareceram | Fonte | Ramo testável |
|---|---|---|---|---|
| `debate-globo-gov-mg-2026-09-29` | Cleitinho, Patrus, Kalil, Simões, Roscoe, Gabriel | **os seis**. Simões e Gabriel foram convidados e foram | W2 (rev 73120756), F16 (O Tempo, 30/09), F17 | O ramo '+' para Simões e Gabriel está testável. Primeiro dado pós-debate: Datafolha 01/10 Simões 5→4 e Gabriel 3→2, nenhum destaque deles em `inflexoes.json` até 02/10. Sinal preliminar contra a direção '+', com uma só pesquisa. |
| `debate-cabobranco-gov-pb-2026-09-29` | Cícero, Efraim, Lucas (Camilo, Pedro Coutinho e Yuri "não convidados" na W3) | **os três**. Cícero foi convidado e foi | W3 (rev 73100406), F14 e F15 (Jornal da Paraíba, pré e pós-debate) | Testável. Primeiro dado pós-debate: Real Time 01/10 Cícero 18 (TDL 27/09: 14, Anova 22/09: 17,4, Quaest 21/09: 15), nenhum destaque de Cícero até 02/10. Inconclusivo. |

Debate presidencial da Globo (01/10): fora do escopo deste agente.

---

## 3. Eventos (JSON)

```json
[
  {"id":"lula-ato-ceilandia-grass-2026-09-16","data":"2026-09-16","registrado_em":"2026-10-04","tipo":"candidatura","alvo":[70002552496,70002552490,70002552492],"direcao_esperada":"+","escopo":"UF","fonte":{"url":"https://jornaldebrasilia.com.br/brasilia/leandro-grass-divide-palanque-com-lula-em-ato-de-campanha-em-ceilandia/","veiculo":"Jornal de Brasília, 17/09/2026 5h43 (ato 'ontem' em Ceilândia, Praça do Trabalhador, Lula pede voto em Grass, Erika Kokay e Leila e cita o caso Master-BRB contra Celina). Reação de Celina (representação na CVM) em SBT News 18/09: https://sbtnews.sbt.com.br/noticia/politica/celina-acionara-cvm-contra-lula-por-fala-sobre-crise-do-brb","acesso":"2026-10-04"},"notas":"EXPLORATÓRIO. Apoio presencial do presidente (tipo candidatura usado para apoio formal, falta classe própria). Dia -8 da inflexão de Grass em 24/09: um dia FORA do raio de 7 dias. Direção '+' é a do mecanismo de transferência e foi escrita depois de ver que Grass subiu em 24/09 e ficou parado nas casas de referência no cenário sem Arruda (Quaest 23->23, Datafolha 23->22). Kokay e Leila não têm destaque no período."},
  {"id":"debate-metropoles-sen-df-2026-09-24","data":"2026-09-24","registrado_em":"2026-10-04","tipo":"debate","alvo":[70002548624,70002552490],"direcao_esperada":"+","escopo":"UF","fonte":{"url":"https://www.brasildefato.com.br/2026/09/25/debate-ao-senado-no-df-tem-ausencia-de-tres-candidatas-e-defesa-do-fim-da-escala-6x1/","veiculo":"Brasil de Fato, 25/09/2026 17h03 (debate do Metrópoles na noite de 24/09: presentes Erika Kokay, Guto Felício, Marley, Ronaldo Fonseca e Sebastião Coelho, ausentes Michelle Bolsonaro, Bia Kicis e Leila)","acesso":"2026-10-04"},"notas":"EXPLORATÓRIO. Regra de exposição: '+' para quem compareceu com as três líderes ausentes. A direção foi escrita depois de ver o movimento, e o movimento de Coelho é o oposto (-0,16 pp em 28 e 29/09): serve como controle negativo. Ronaldo Fonseca (PSD) aparece no debate e no Datafolha de 01/10 (2%) mas não está na lista de candidatos do dossiê, por isso não é alvo."},
  {"id":"psd-apoia-celina-arruda-rejeita-2026-09-28","data":"2026-09-28","registrado_em":"2026-10-04","tipo":"candidatura","alvo":[70002553055],"direcao_esperada":"?","escopo":"UF","fonte":{"url":"https://www.brasildefato.com.br/2026/09/28/eleicoes-no-df-arruda-rompe-com-apoio-do-psd-a-celina-leao-e-rejeita-alianca/","veiculo":"Brasil de Fato, 28/09/2026 17h33 (PSD oficializa apoio à reeleição de Celina em 28/09, anúncio de Paulo Octávio, Arruda, em vídeo de 27/09, recusa: 'Eles não terão o meu apoio', e chama a gestão de 'o pior governo da história de Brasília')","acesso":"2026-10-04"},"notas":"EXPLORATÓRIO. Duas forças opostas no mesmo dia sobre Celina: apoio formal do partido de Arruda ('+') e recusa pública de Arruda com ataque ao governo e ao BRB ('-'), daí '?'. O campo das pesquisas de 28/09 (Quaest 25-28/09, Real Time 24-28/09, Correio 28/09) fecha no mesmo dia ou antes: exposição nula para a inflexão de 28/09 e parcial, no máximo, para a IGAPE de 29/09. Segundo o resumo da matéria, Arruda recomendou voto em Izalci Lucas (PL), que não consta da lista de candidatos a governador ou senador do dossiê (cargo não conferido). Em 24/09 (F2) Arruda tinha dito que não faria recomendação de voto."},
  {"id":"michelle-pede-voto-kicis-2026-09-28","data":"2026-09-28","registrado_em":"2026-10-04","tipo":"candidatura","alvo":[70002548624,70002552934],"direcao_esperada":"-","escopo":"UF","fonte":{"url":"https://ncnews.com.br/?p=54036","veiculo":"NC News, 28/09/2026 13h41 (Michelle Bolsonaro pede votos para si e para Bia Kicis em evento de 28/09, cita Coelho com respeito mas diz que a chapa dela tem 'possibilidade de vencer')","acesso":"2026-10-04"},"notas":"EXPLORATÓRIO. Mecanismo de voto útil na direita: '-' vale para Sebastião Coelho (Novo), que divide o eleitor bolsonarista, para Bia Kicis a direção pelo mecanismo é '+' (registrado com '-' no campo único e a ressalva aqui, como em jordy-confirmado-pl-senado-rj-2026-08-04). Direção escrita depois de ver o movimento. Exposição: nula para 28/09, plausível para IGAPE 29/09 (Coelho 8,6->2,3, Kicis 30,9->36,4, Michelle 40,8->50,2 na mesma casa) e Exata 02/10."},
  {"id":"debate-globo-gov-df-2026-09-29","data":"2026-09-29","registrado_em":"2026-10-04","tipo":"debate","alvo":[70002553055],"direcao_esperada":"-","escopo":"UF","fonte":{"url":"https://ncnews.com.br/?p=54903","veiculo":"NC News, 30/09/2026 (debate TV Globo DF em 29/09, mediação Heraldo Pereira, presentes Kiko Caputo, Leandro Grass, Paula Belmonte e Ricardo Cappelli, Celina Leão ausente, crise do BRB como tema central). Confirmado por Jornal de Brasília 30/09 (https://jornaldebrasilia.com.br/brasilia/sem-celina-ultimo-debate-tem-criticas-ao-governo-e-afagos-a-arruda/) e Wikipédia PT rev 73116640 (Celina 'Ausente', Arruda 'Impedido')","acesso":"2026-10-04"},"notas":"EXPLORATÓRIO. Último debate do 1º turno no DF. Direção '-' para a líder ausente (cadeira vazia, ataques sem resposta sobre o BRB), Grass e Belmonte presentes teriam '+'. SEM INFLEXÃO ASSOCIADA até o as_of de 02/10. A direção foi escrita depois de ver o Datafolha de 01/10, que dá Celina 46 (42 em 24/09 no cenário sem Arruda): o primeiro dado não confirma o '-'."},
  {"id":"savio-superman-pedem-zema-desistir-2026-09-23","data":"2026-09-23","registrado_em":"2026-10-04","tipo":"candidatura","alvo":[130002551786,130002551284],"direcao_esperada":"+","escopo":"UF","fonte":{"url":"https://diariodocomercio.com.br/politica/domingos-savio-superman-pedem-desistencia-zema/","veiculo":"Diário do Comércio, 23/09/2026 (programa Minas Presente: Domingos Sávio e Marco Antônio Superman pedem que Zema desista e apoie Flávio Bolsonaro no 1º turno, a fala de Superman incomodou a direção do Novo)","acesso":"2026-10-04"},"notas":"EXPLORATÓRIO. Alinhamento explícito dos dois com Flávio, consolidando a dobradinha anunciada em 12/09 em Januária (O Fator, https://ofator.com.br/?p=71148). Mecanismo: captura do voto bolsonarista para as duas vagas. Dia -5 da inflexão de 28/09, cujo campo (Quaest 25-28/09) é todo posterior. Direção escrita depois de ver Quaest 10->14 e 1->4. Não explica por que o Datafolha de 01/10 fica parado (9 e 2)."},
  {"id":"quaest-savio-lidera-sen-mg-2026-09-30","data":"2026-09-30","registrado_em":"2026-10-04","tipo":"pesquisa_bomba","alvo":[130002551786],"direcao_esperada":"+","escopo":"UF","fonte":{"url":"https://www.bahianoticias.com.br/noticia/321727-candidato-bolsonarista-ultrapassa-ex-prefeita-petista-e-aecio-neves-e-assume-lideranca-para-o-senado-em-minas","veiculo":"Bahia Notícias, 30/09/2026 (Quaest/Globo 25 a 28/09, MG-02019/2026: Sávio 14, Marília 13, Aécio 12, Viana 12, Aro 6, Superman 4, manchete 'assume liderança')","acesso":"2026-10-04"},"notas":"EXPLORATÓRIO. Data é a da matéria aberta, a Quaest pode ter sido divulgada pela Globo em 29/09 (não conferido). Mecanismo de manada para o novo líder numérico, empatado com três. Candidato a causa da inflexão de 02/10 (Real Time, Sávio 16->20). Direção escrita depois de ver o movimento. Risco de circularidade: a própria Quaest é disparadora da inflexão de 28/09."},
  {"id":"debate-globo-gov-rj-2026-09-29","data":"2026-09-29","registrado_em":"2026-10-04","tipo":"debate","alvo":[190002537524],"direcao_esperada":"+","escopo":"UF","fonte":{"url":"https://www.tribunadosertao.com.br/poder-e-governo/2026/09/30/987842-eduardo-paes-e-douglas-ruas-se-enfrentam-em-debate-da-globo-com-mencoes-a-lula-cabral-castro-e-bacellar","veiculo":"Tribuna do Sertão, 30/09/2026 (debate TV Globo RJ em 29/09: Paes, Ruas, Garotinho, Siri e André Marinho, Marinho faz 'dobradinha' com Ruas em educação). Wikipédia PT rev 73115098 marca os cinco 'Presente' (linha sem referência)","acesso":"2026-10-04"},"notas":"EXPLORATÓRIO. Regra de exposição para o candidato pequeno presente. CONFLITO DE FONTE: Diário do Rio de 28/09 (https://diariodorio.com/politica/2026/09/28/globo-realiza-debate-para-governador-do-rio-nesta-terca-saiba-quem-participa-e-como-assistir.html) lista só quatro convidados, sem Marinho. A presença dele está em duas fontes (uma sem referência) e deve ser reconferida. Direção '+' contrária ao destaque de 30/09 (Gerp, -0,02): não explica. Primeiro e único confronto Paes x Ruas, mas nenhum dos dois tem destaque no período."},
  {"id":"tre-rj-defere-waguinho-2026-09-29","data":"2026-09-29","registrado_em":"2026-10-04","tipo":"decisao_judicial","alvo":[190002550182],"direcao_esperada":"+","escopo":"UF","fonte":{"url":"https://temporealrj.com/tre-rj-defere-candidatura-waguinho-ao-senado/","veiculo":"Tempo Real RJ, 29/09/2026 (TRE-RJ defere por unanimidade o registro de Waguinho ao Senado, relator Paulo Cesar Salomão Filho, rejeitando impugnações do MPE por contas municipais de 2021 e 2022 rejeitadas e menção em inquérito da Draco)","acesso":"2026-10-04"},"notas":"EXPLORATÓRIO. Fim da incerteza de registro: mecanismo '+'. Direção oposta às três inflexões negativas de Waguinho (28, 29 e 30/09), cujo campo é quase todo anterior: não explica nenhuma. Registrado como evento grande da corrida e controle negativo. Data em que as impugnações viraram notícia não foi conferida."},
  {"id":"debate-redeamazonica-gov-am-2026-09-29","data":"2026-09-29","registrado_em":"2026-10-04","tipo":"debate","alvo":[40002536086],"direcao_esperada":"-","escopo":"UF","fonte":{"url":"https://gazetadaamazonia.com.br/30/09/2026/debate-ao-governo-do-amazonas-2/","veiculo":"Gazeta da Amazônia, 30/09/2026 (debate Rede Amazônica em 29/09, mediação César Menezes, presentes Omar Aziz, David Almeida, Roberto Cidade, Maria do Carmo e Isael Munduruku, Cidade acusa Almeida de R$ 16 milhões a empresas ligadas a familiares, Maria do Carmo cobra viagem ao Caribe e tributos com Manaus). Contestação da acusação de Almeida contra Cidade em Amazônia Sem Fronteira 30/09: https://amazoniasemfronteira.com.br/david-almeida-e-contestado-ao-vivo-durante-debate-na-rede-amazonica/","acesso":"2026-10-04"},"notas":"EXPLORATÓRIO. Almeida foi o alvo principal das acusações e fez uma acusação contra Cidade que foi desmentida por documento societário: mecanismo '-'. Direção escrita depois de ver o destaque de 01/10 (Real Time, -0,08). Exposição parcial: o campo da Real Time termina em 01/10, início não conferido. Não explica a inflexão de 27/09, anterior ao debate. Mesma fonte cita debate da TV A Crítica em 28/09 (não aberto)."}
]
```

Contagem por corrida (um evento pode tocar mais de uma): GOV-DF 3 (Lula/Grass, PSD/Arruda, Globo DF), SEN-DF 3 (Metrópoles Senado, Michelle/Kicis, e Lula pelos alvos Kokay e Leila), SEN-MG 2, GOV-RJ 1, SEN-RJ 1, GOV-AM 1, SEN-RO 0, SEN-RN 0. Total de 10 eventos distintos.

---

## 4. Eventos, um a um (mecanismo, implicações cruzadas, fonte)

### lula-ato-ceilandia-grass-2026-09-16
1. Mecanismo. [fato] Em 16/09 Lula pediu voto em Grass, Kokay e Leila em Ceilândia e disse que não faz sentido votar nele e em quem não é aliado. [inferência] Transferência de voto do eleitor lulista que ainda não votava em Grass. [hipótese] O efeito, se houve, entraria no campo da Veritá de 24/09.
2. Implicações cruzadas. Poderia explicar: GOV-DF Grass +1,04 em 24/09 (fora do raio por 1 dia). Não explica: Grass parado nas casas de referência no cenário sem Arruda (Quaest 23→23, Datafolha 23→22), Kokay e Leila sem destaque. Se a transferência fosse real, Kokay deveria subir e não subiu (Quaest 15→16, Datafolha 15→13).
3. Fonte: Jornal de Brasília, 17/09/2026, aberta em 04/10. Reação de Celina em SBT News, 18/09, aberta.

### debate-metropoles-sen-df-2026-09-24
1. Mecanismo. [fato] Debate do Metrópoles do Senado DF com Coelho presente e Michelle, Kicis e Leila ausentes. [inferência] Exposição relativa maior para os presentes. [hipótese] Coelho ganharia com o palco livre da direita.
2. Implicações cruzadas. Não explica nenhuma inflexão: Coelho cai em 28, 29/09 e 02/10. Kokay, presente, não se move. Controle negativo da regra de exposição.
3. Fonte: Brasil de Fato, 25/09/2026, aberta em 04/10.

### psd-apoia-celina-arruda-rejeita-2026-09-28
1. Mecanismo. [fato] PSD oficializa apoio a Celina em 28/09 e Arruda, em vídeo de 27/09, recusa e ataca o governo e o BRB. [inferência] O eleitor de Arruda (16 a 20% até 24/09) recebe sinais opostos. [hipótese] Se o eleitor seguir o partido, Celina sobe. Se seguir Arruda, migra para Belmonte, que buscou o apoio dele (F2) e o defendeu no debate (F4).
2. Implicações cruzadas. Poderia explicar: GOV-DF Celina e Belmonte em 29/09 (IGAPE, exposição parcial). Não explica 26/09 nem 28/09 (campo anterior). Se o ramo "segue Arruda" valesse, Belmonte subiria mais que Celina em pontos: no dado, Quaest sem Arruda dá Celina +5 e Belmonte +2 (22→28/09), o que favorece o ramo "segue o partido" ou simplesmente a saída de Arruda já registrada.
3. Fonte: Brasil de Fato, 28/09/2026, aberta em 04/10.

### michelle-pede-voto-kicis-2026-09-28
1. Mecanismo. [fato] Michelle pede voto para si e para Kicis e diz que a chapa do PL tem possibilidade de vencer. [inferência] Apelo de voto útil que concorre com Coelho pelo mesmo eleitor. [hipótese] O eleitor bolsonarista que dava o 2º voto a Coelho migra para Kicis.
2. Implicações cruzadas. Poderia explicar: SEN-DF Coelho em 29/09 (IGAPE 8,6→2,3, com Kicis 30,9→36,4 na mesma casa) e 02/10 (Exata 1,7). Não explica 28/09 (campo anterior). Kicis deveria ter destaque '+' e não tem até 02/10 (Quaest 15→18, Datafolha 15→18: sobe, mas abaixo do limiar do detector). Hipótese concorrente: dispersão entre casas (Real Time 11 contra 1 a 2 em Quaest, Datafolha e Correio).
3. Fonte: NC News, 28/09/2026, aberta em 04/10.

### debate-globo-gov-df-2026-09-29
1. Mecanismo. [fato] Celina, líder, faltou ao último debate, que girou em torno do BRB. [inferência] Cadeira vazia e ataques sem resposta. [hipótese] Perda pequena para Celina, ganho para Grass e Belmonte.
2. Implicações cruzadas. Sem inflexão associada até 02/10. O Datafolha de 01/10 (campo depois do debate) dá Celina 46, acima dos 42 de 24/09: o primeiro dado vai contra o '-'. Testável na apuração.
3. Fonte: NC News e Jornal de Brasília, 30/09/2026, abertas. Wikipédia rev 73116640.

### savio-superman-pedem-zema-desistir-2026-09-23
1. Mecanismo. [fato] Os dois candidatos pedem publicamente que Zema apoie Flávio já no 1º turno. [inferência] Sinal de alinhamento ao bolsonarismo, que em MG está dividido entre PL, Novo e Republicanos. [hipótese] Captura do 2º voto bolsonarista para a dupla.
2. Implicações cruzadas. Poderia explicar: SEN-MG Sávio e Superman em 28/09 (Quaest) e 02/10 (Real Time). Não explica: Datafolha 01/10 parado para os dois (9 e 2), nem a queda de Aécio só na Real Time de 02/10 (−4,36, não corroborado). Viana (PSD, chapa de Simões) não cai na Quaest (10→12): o ganho não veio dele.
3. Fonte: Diário do Comércio, 23/09/2026, aberta em 04/10.

### quaest-savio-lidera-sen-mg-2026-09-30
1. Mecanismo. [fato] A Quaest de 25 a 28/09 põe Sávio numericamente à frente (14) num empate de quatro. [inferência] A manchete de liderança circula na reta final. [hipótese] Efeito de manada e de voto útil na direita.
2. Implicações cruzadas. Poderia explicar: SEN-MG Sávio +0,10 em 02/10 (Real Time 16→20). Não explica 28/09 (é a própria pesquisa). Superman sobe junto na Real Time (4→8) sem ser citado como líder: o mecanismo de manada não cobre ele, a dobradinha cobre.
3. Fonte: Bahia Notícias, 30/09/2026, aberta em 04/10.

### debate-globo-gov-rj-2026-09-29
1. Mecanismo. [fato] Debate com cinco candidatos, primeiro confronto direto Paes x Ruas. [inferência] Marinho teve papel lateral, de apoio a Ruas. [hipótese] Exposição positiva para o candidato pequeno.
2. Implicações cruzadas. Não explica GOV-RJ Marinho −0,02 em 30/09 (direção oposta). Paes e Ruas não têm destaque no período. Presença de Marinho em conflito entre fontes.
3. Fonte: Tribuna do Sertão, 30/09/2026, aberta. Diário do Rio, 28/09, aberta (conflito). Wikipédia rev 73115098.

### tre-rj-defere-waguinho-2026-09-29
1. Mecanismo. [fato] TRE-RJ deferiu o registro de Waguinho por unanimidade em 29/09. [inferência] Some o risco de voto anulado. [hipótese] Efeito pequeno '+', porque a impugnação teve pouca visibilidade.
2. Implicações cruzadas. Não explica nenhuma das três inflexões negativas de Waguinho (28, 29 e 30/09). Crivella, colega de chapa, também não se move por isso.
3. Fonte: Tempo Real RJ, 29/09/2026, aberta em 04/10.

### debate-redeamazonica-gov-am-2026-09-29
1. Mecanismo. [fato] Almeida foi alvo de três acusações no debate e sua própria acusação contra Cidade foi contestada por documento. [inferência] Saldo de imagem negativo para ele. [hipótese] Perda pequena no fim da campanha.
2. Implicações cruzadas. Poderia explicar: GOV-AM Almeida −0,08 em 01/10 (Real Time, exposição parcial). Não explica 27/09 (anterior). Cidade e Aziz não têm destaque. Hipótese concorrente: casa (Real Time 9 contra Pontual 14,5) e arrasto de Cury (Avante), cuja queda nacional é anterior e cujo candidato Almeida defendia em 01/09 (manchete, não aberta).
3. Fonte: Gazeta da Amazônia e Amazônia Sem Fronteira, 30/09/2026, abertas em 04/10.

---

## 5. Pendentes, só manchete (fora do JSON)

- **Debate da Record no DF em setembro sem Celina.** F1 (aberta) diz que Celina faltou "ao debate promovido pela Record em setembro" por funções do cargo, mas não dá a data, e a tabela da Wikipédia (W1) não tem linha da Record. Falta data e lista de presentes.
- **Debate da TV A Crítica (AM) em 28/09.** Só citado de passagem em F25. Não aberto.
- **"Após confusão, Roberto Cidade pede que apoiadores acompanhem debate da Rede Amazônica de casa"** (Rios de Notícias). Manchete de busca, não aberta.
- **"Sávio ganhou apoio de Flávio Bolsonaro"** (F18 menciona sem data). Não é evento datável com o que foi aberto.
- **TRE-AM e propaganda antecipada de David Almeida** (Revista Cenarium). Manchete, sem data aberta, provavelmente pré-campanha.
- **David Almeida defende Cury como alternativa à polarização (01/09)** (Norte Evidências). Resumo do buscador, não aberto.
- **Arruda e o STF.** Busca apontou "STF retoma julgamento que pode definir candidatura de Arruda" (O Hoje, 11/09) e "Arruda não indica substituto e mantém candidatura sob análise" (Tribuna do Sertão, 15/09). Nenhuma aberta. Nenhuma fonte aberta confirma recurso ao STF depois de 24/09: a condição "sub judice" citada no pedido não foi conferida, e o registro já existente diz que o TSE cessou essa condição.
- **"Lula decide não participar de debate presidencial da Globo nesta quinta"** (O Hoje, 30/09). Manchete de busca, fora do escopo, repassada para o agente da presidencial.

---

## 6. O que não dá para afirmar

1. **Nenhuma causa está confirmada.** Todos os eventos nascem exploratórios e várias direções foram escritas depois de olhar o movimento (dito em cada `notas`).
2. **DF governo: a maior parte das inflexões de 24 a 29/09 é a saída de Arruda, já registrada.** Até 24/09 todas as casas publicavam cenário com Arruda (16 a 21%). Depois, o cenário principal é sem ele. A parte que sobra (Celina +5 e Belmonte +2 na Quaest sem Arruda, Celina +4 no Datafolha sem Arruda) é movimento real, mas não há evento aberto no raio que a explique melhor que a própria redistribuição.
3. **SEN-DF: a queda de Coelho é sobretudo da IGAPE** (8,6→2,3 em três dias). Nas casas de referência ele já estava em 1 a 2 desde 19/09. O voto útil pedido por Michelle em 28/09 casa com o tempo da IGAPE, mas uma casa só não separa evento de troca de questionário.
4. **SEN-MG: Datafolha de 01/10 não confirma a subida de Sávio e Superman** (9 e 2, iguais a 24/09). O sinal vem de Quaest e Real Time.
5. **RJ, RO, RN: Δ de nível de −0,02 a −0,11 pp.** Os eventos encontrados no RJ têm direção oposta ao movimento. RO e RN: sem evento plausível encontrado, e a leitura é casa (Veritá alta para Acir, Seta fora das demais no RN).
6. **AM: o destaque de 27/09 é a volta depois da Phoenix de 25/09** (27,57, contra 10 a 15 nas outras casas). Arrasto de Cury é hipótese sem fonte aberta.
7. **Debates pré-especificados de MG e PB: presença conferida, efeito não.** Só há uma pesquisa pós-debate em cada corrida até 02/10. Primeiro sinal de MG é contrário ao '+' (Simões 5→4, Gabriel 3→2 no Datafolha), o de PB é inconclusivo.
8. **Fora da lista de candidatos:** Ronaldo Fonseca (PSD, Senado DF) aparece em debate e no Datafolha de 01/10 e não está no dossiê. Vale conferir no ingest se é alias pendente.
9. **Fontes primárias não alcançadas:** TSE e TRE-DF por consulta direta (só via imprensa), Lupa e Aos Fatos, g1 (bloqueado para o WebFetch), horário de início dos campos de Real Time e IGAPE (sem isso a exposição a eventos de 28 e 29/09 fica "parcial" e não medida).
