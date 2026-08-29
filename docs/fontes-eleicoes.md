# Fontes de dados · Eleições 2026 (decisão da etapa B2)

> **Decisão de 29/08/2026, aprovada pelo Bera** (pergunta clicável na sessão da Fase B):
> percentuais de pesquisas vêm da **Wikipédia PT** (fonte primária); o **registro PesqEle/TSE**
> é a âncora de existência e completude (nenhuma pesquisa entra sem casar com o registro);
> **candidaturas** vêm dos dados abertos do TSE + API DivulgaCandContas. Conferência por
> amostragem nas fichas da Gazeta do Povo. Investigação: 3 subagentes web em 29/08/2026;
> evidências e URLs abaixo.

## O problema

O TSE **não publica percentuais de pesquisa em nenhum dado estruturado** (verificação tripla em
29/08/2026: dataset sem recurso de resultados; aviso do painel da Plural; consulta pública sem
percentuais). O relatório de resultados é PDF por pesquisa cuja publicização a Res. 23.600/2019
art. 2º §7º-B manda ocorrer "depois das eleições". Ou seja: registro é público e estruturado,
resultado é imprensa. Toda fonte de percentuais é, portanto, secundária, e a escolha é sobre qual
secundária é confiável, estruturada e sustentável por ~5 semanas de campanha.

## A decisão

**Fonte primária de percentuais: Wikipédia PT.**
- **27/27 corridas cobertas** (verificado 29/08/2026 via API de busca: 26 páginas "Pesquisas
  eleitorais para a eleição estadual de 2026 em/no {UF}" + "…eleição distrital de 2026 no
  Distrito Federal"), incluindo governador E Senado; presidencial em página própria
  ("Pesquisas de opinião para a eleição presidencial no Brasil em 2026"; atenção: a variante de
  título "brasileira de 2026" dá 404).
- Tabelas wikitext **estáticas** (parse por stdlib, sem headless), acessíveis também pela API
  MediaWiki; licença **CC BY-SA** (uso derivado permitido com atribuição).
- Latência observada: 1 a 3 dias entre campo/divulgação e a tabela (ex.: pesquisa com campo
  25-27/08 já listada em 29/08).
- **Backtest**: páginas equivalentes de 2022 existem (presidencial e estaduais), o que permite
  calibrar o agregador antes do 1º turno.
- Metadados por linha: instituto, contratante (nem sempre), datas de campo, amostra, margem,
  percentuais por candidato, indecisos. **Não traz o nº de registro TSE** (nenhuma fonte pública
  viva traz, exceto DataPolicy, congelado desde 13/08).

**Âncora de existência e completude: PesqEle/TSE (dados abertos).**
- Dataset "Pesquisas Eleitorais - 2026" (dadosabertos.tse.jus.br/dataset/pesquisas-eleitorais-2026),
  fonte Sistema PesqEle, licença **CC-BY**, geração diária (~05:47, D+1 típico).
- CSV principal (zip `pesquisa_eleitoral_2026.zip` no cdn.tse.jus.br): NR_PROTOCOLO_REGISTRO,
  instituto (CNPJ + razão social + fantasia), UF/UE, DS_CARGO, datas de campo, **DT_DIVULGACAO**,
  QT_ENTREVISTADO, estatístico, valor, metodologia. 15.143 linhas na geração de 28/08 (todas as
  eleições, inclui municipais suplementares; filtrar por cargo/eleição).
- Papel no pipeline: (1) **validação anti-instituto-fantasma**: percentual da wiki só entra se
  casar com um registro (instituto+UF+cargo+datas compatíveis); (2) **alarme de completude**
  (aprendizado do jogo 103 da Copa): registro com DT_DIVULGACAO passada e sem resultado ingerido
  em N dias vira aviso para caça manual.

**Candidaturas: dados abertos TSE + API DivulgaCandContas.**
- `consulta_cand_2026.zip` (CC-BY): **SQ_CANDIDATO** (id estável; ex. 260002543589),
  NR_CANDIDATO (nº de urna), NM_URNA_CANDIDATO, partido/federação/coligação. Geração 27/08:
  20.769 candidatos (13 presidente, 198 governador, 318 senador).
- **Pegadinha**: o status real do registro está no arquivo **complementar**
  (DS_SITUACAO_JULGAMENTO: 7.302 deferidos, 13.101 aguardando em 27/08); no principal,
  DS_SITUACAO_CANDIDATURA está 100% "#NE" hoje.
- API REST sem auth (não documentada; schema pode mudar):
  `divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/listar/2026/{UE}/20322002026/{cargo}/candidatos`
  (UE=BR ou sigla da UF; cargo 1=presidente, 3=governador, 5=senador). Serve para atualização de
  status quase em tempo real entre gerações do zip.

**Conferência (quorum humano por amostragem): Gazeta do Povo.**
- Hub `gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/`: matéria por pesquisa com
  ficha técnica **incluindo o nº de registro TSE**, 2-3/dia, cobre gov+Senado por UF. Serve de
  segunda fonte para verificação pontual e para depurar divergências wiki↔TSE.

## Critérios (ROADMAP F2 adaptado) aplicados ao vencedor

| Critério | Wikipédia + âncora TSE |
|---|---|
| Cobertura estadual (o gargalo) | 27/27 corridas confirmadas, gov+Senado |
| Latência | wiki 1-3 dias; TSE D+1 (registro), app mesmo dia |
| Custo | zero (CC BY-SA + CC-BY) |
| Licença/ToS | explícitas e permissivas com atribuição |
| Histórico p/ backtest | páginas 2022 vivas |
| Formato/IDs | tabelas estáveis, sem ID: de-para próprio (abaixo) |
| Âncora de verdade | registro oficial TSE por trás de toda linha |

## Alternativas avaliadas (planos B, em ordem)

1. **Poder360** (drive.poder360.com.br/agregador-de-pesquisas): o mais completo (desde 2000,
   >620 pesquisas em 2026, aberto durante a campanha, citação obrigatória), mas números via
   XHR/JavaScript sem endpoint documentado; robots.txt não bloqueia; risco de fechar pós-eleição.
   Plano B se a wiki degradar.
2. **O POVO** (mais.opovo.com.br/interativos/agregador/): lê o TSE diariamente, whitelist de 9
   institutos (perderia os locais das UFs pequenas), botão de download com formato não
   confirmado, paywall O POVO+ (R$ 1,90 promo / R$ 11,90 mês).
3. **Pipeline TSE-first com extração de matérias**: rastreabilidade máxima (nº TSE), esforço alto
   (parser por matéria); a âncora adotada já captura 80% do valor por fração do custo.
4. Agregadores modelados (PollingData/BBC, Índice CNN, JOTA, UOL, Exame): saída já agregada
   (sinal correlacionado, não pesquisa individual), casca JS e/ou bloqueios; úteis como
   **benchmark de comparação** do nosso agregador, não como fonte.

## De-para de nomes (regras)

- **Chave canônica de candidato: `SQ_CANDIDATO` do TSE.** Display = `NM_URNA_CANDIDATO` +
  sigla do partido (padrão PT-map da Copa: chave estável, tradução na camada de view).
- **Match wiki→TSE por corrida**: normalizar (caixa alta, sem acento, remover "(PARTIDO)")
  e casar contra NM_URNA_CANDIDATO e NM_CANDIDATO dentro de (UF, cargo). Ambiguidade ou
  candidato sem match (ex.: "outros", desistências) vai para `data/eleicoes/aliases.json`,
  tabela curada à mão, e para a fila de revisão; **nunca** descartar linha em silêncio.
- **Match de instituto**: PesqEle traz razão social/fantasia ("QUAEST CONSULTORIA E PESQUISA
  LTDA"), imprensa usa marca ("Quaest"): tabela de aliases de institutos no mesmo arquivo.
- **Match pesquisa↔registro** (a âncora): (instituto normalizado, UF, cargo, datas de campo com
  tolerância ±1 dia). Sem nº TSE na wiki, essa tripla é a chave possível; colisões (mesmo
  instituto, mesma UF, campos sobrepostos) vão à fila de revisão manual.

## Riscos declarados e pegadinhas operacionais

- **403 Akamai do TSE fora de navegador real** (dadosabertos, cdn.tse, www.tse; observado em
  29/08 com WebFetch/curl): **testar do GitHub Actions cedo na B8**; o IP/ambiente do CI pode
  passar; senão, fallback = HTTP Range direto no CDN (aceita), headless, ou espelhos (o painel
  da Plural consome o mesmo dataset). A API DivulgaCandContas respondeu normalmente.
- CSV TSE: latin1 (ISO-8859-1), separador `;`, strings entre aspas (parser ingênuo quebra),
  placeholders `#NULO`/`#NE`/-1/-3; **DF não tem CSV próprio de pesquisas** (só no BRASIL.csv);
  margem de erro sem coluna (texto livre em DS_PLANO_AMOSTRAL).
- Wiki: filtrar a seção "Polling aggregation" (página EN) para não ingerir linha de agregador
  como pesquisa (dupla contagem); distinguir data de campo × divulgação; vandalismo/erro
  comunitário mitigado pela âncora TSE + gate de sanidade (somas, faixas).
- **Senado com 2 votos por eleitor**: institutos divulgam ora soma bruta (>100%, ex. Datafolha
  RJ 116%), ora normalizado para 100% (Quaest, RTBD): detectar a base por pesquisa e
  re-normalizar antes de agregar (regra vai no schema de `polls.json`, etapa B3).
- Cadência desigual por UF (SP/RJ semanal; UFs pequenas ~mensal via Real Time Big Data, Paraná
  Pesquisas, AtlasIntel e locais): banda de incerteza por corrida proporcional à idade e
  escassez de pesquisa (etapa B4), nunca 50/50 silencioso.
- Institutos novos sem histórico (Vox Brasil, Indexa, Gerp, Neokemp…): entram com peso de
  house-effect conservador; a âncora TSE garante que ao menos existem juridicamente.

## Evidências (acessos de 29/08/2026)

- TSE pesquisas: https://dadosabertos.tse.jus.br/dataset/pesquisas-eleitorais-2026 · headers
  lidos direto dos zips no cdn.tse.jus.br (HTTP Range) · consulta pública
  https://pesqele-divulgacao.tse.jus.br/ · Res. 23.600/2019 compilada (art. 2º §7º-A/B/C).
- TSE candidatos: https://dadosabertos.tse.jus.br/dataset/candidatos-2026 · API
  https://divulgacandcontas.tse.jus.br/divulga/rest/v1/eleicao/ordinarias (2026 = 20322002026).
- Wikipédia: 27 páginas confirmadas via API de busca (26 estaduais + DF distrital) + páginas
  presidenciais PT/EN; equivalentes de 2022 vivas.
- Poder360 abre o agregador na campanha:
  https://www.poder360.com.br/poder360/poder360-abre-acesso-ao-agregador-de-pesquisas-mais-completo-da-midia/
- O POVO (metodologia, whitelist, fase 2 gov+sen):
  https://mais.opovo.com.br/interativos/agregador/agregador-pesquisas-2026.php
- Gazeta do Povo hub: https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/
- Volume 2026: 1.135 registros/188 institutos até 29/08 (painel Plural,
  https://www.plural.jor.br/pesquisas-eleitorais-2026/); gov 752 × sen 724 × pres 473 até jul
  (Metrópoles). Senado 2 vagas: 314 candidatos (Senado Notícias, 17/08).
