# Ficha do Jogo · Eleições 2026, plano de risco e segurança de IA

**Projeto:** Ficha do Jogo, modelo probabilístico e dashboard da eleição brasileira de 2026,
publicado em https://bera.ia.br/ficha-do-jogo (Cloudflare Worker + HTML estático).
**Tier:** T1 (solo/pequeno), com as extensões agênticas aplicadas, porque o sistema age
sozinho sobre produção.
**Data:** 31 de agosto de 2026 · **Revisão 2:** 21 de setembro de 2026 (§0) ·
**Método:** NIST CSF + OWASP Top 10 (LLM 2025 / Agentic 2026) + SAIF, via skill `para-raios`.

> Todas as afirmações abaixo foram verificadas por leitura do código e por medição no dado
> real desta data. Onde não deu para confirmar, está escrito "Não tenho certeza" e o que
> falta checar.

---

## 0. Revisão 2 · 21 de setembro de 2026

> A tabela da §2 e as ameaças da §3 ficam como **registro do que era verdade em 31/08**.
> Esta seção traz o que mudou, o placar novo e os riscos que não existiam antes.
> **Contexto:** faltam 13 dias para o 1º turno e a edição está no ar.

### 0.1. O que a realidade ensinou entre as duas revisões

O plano de 31/08 respondeu **Não** para "temos como identificar se o agente está fazendo
algo incomum?" e recomendou um alarme de movimento. O alarme foi construído (C0-c) e,
mesmo assim, **em 04/09 o sistema perdeu 89% das pesquisas da presidencial e publicou
forecast sobre 11% do dado por 14 dias, com o pipeline verde todo dia.**

A lição não é que o alarme falhou; é que a categoria estava certa e o **controle cobria
metade dela**. Os dois alarmes existentes olhavam o **valor** do dado (entrada implausível,
saída que se move demais). Nenhum olhava o dado que **simplesmente some**. Pior: o alarme de
completude do B8 media FRESCOR, e a corrida seguia recebendo pesquisa nova, então continuava
marcada "ok". E o total da base até **subiu** no período, porque as outras 54 corridas
cresceram mais do que a presidencial perdeu.

Correção: `src/check_volume.py`, por **(corrida, cenário)**, com limiar calibrado em 20
rodadas reais e validado reproduzindo o incidente a partir do histórico do git.

### 0.2. Placar revisado

| Categoria | Pergunta | 31/08 | 21/09 | O que mudou |
|---|---|---|---|---|
| Proteger | Controlamos o que o agente pode ver e fazer? | **Não** | **Parcial** | Ganhou gate de plausibilidade calibrado com erro plantado (C0-c). Mas a **superfície de entrada aumentou** em 21/09: ver R1 |
| Proteger | As pessoas foram treinadas? (documentação) | **Não** | **Sim** | O runbook descrevia gates da edição Copa que não existiam aqui. Corrigido, e ganhou a seção do incidente de 04/09 com o mecanismo escrito |
| Proteger | Saída validada antes de virar HTML? | **Não** | **Sim** | Escaping por padrão no `build_publicos.py` (quick win #4 desta mesma skill, aplicado no C1c) |
| Detectar | Identificamos comportamento incomum? | **Não** | **Parcial** | Três camadas agora: valor na entrada (gate), valor na saída (`check_movimento`), **volume por corrida** (`check_volume`). Cego para **adição** em massa: ver R2 |
| Responder | Kill switch documentado? | **Não** | **Sim** | `docs/runbook-incidente.md`, 4 níveis |
| Recuperar | Conseguimos recuperar? | **Sim** | **Parcial** | Ver R5: o caminho de emergência do runbook esteve **indisponível por 8 dias sem ninguém saber** |
| Identificar | Escopo do `CLOUDFLARE_API_TOKEN`? | **Incerteza** | **Incerteza** | Não verificado. Segue como a pendência mais antiga em aberto |
| Proteger | Dependências fixadas? | **Não** | **Não** | `actions/checkout@v4`, `setup-python@v5`, `wrangler-action@v3` seguem por tag móvel |

**Placar 21/09:** 7 Sim · 1 Não · 1 incerteza · 4 parciais. Melhorou, e as parciais são
honestas, não meias-vitórias.

### 0.3. Riscos NOVOS

#### R1 · ALTO · O ingest passou a seguir link lido do conteúdo da fonte

**Introduzido em 21/09/2026, por mim, para corrigir o incidente.** Quando a Wikipédia
quebrou a presidencial em subpáginas, o ingest passou a seguir hatnotes (`Ver artigo
principal`) cujo alvo é subpágina da própria página (`src/ingest_polls.py::subpaginas`).

| | Antes de 21/09 | Depois |
|---|---|---|
| Fontes que o robô lê | **28 títulos fixos, no código** | 28 fixos **+ qualquer subpágina deles que um hatnote apontar** |
| Para injetar, o atacante precisa | editar um dos 28 artigos, todos vigiados | **criar um artigo novo**, sem vigilância nem histórico, e fazer **uma edição de uma linha** no artigo vigiado |

**OWASP:** LLM04 (Data Poisoning) agravado, ASI02 (Tool Misuse: a "ferramenta" de busca
passa a aceitar destino vindo do dado), ASI01 (comportamento dirigido por input).

**O que NÃO muda:** a autorização. Nos dois mundos, quem injeta é "qualquer editor da
Wikipédia". **O que muda é a detectabilidade**, e é isso que importa: uma tabela de pesquisa
forjada dentro de um artigo vigiado tende a ser revertida por editores; um artigo novo com
zero observadores, não. O elo visível vira uma edição de uma linha.

**Por que os controles atuais não fecham:** o gate de plausibilidade só **quarentena** o que
desvia mais de 25pp do consenso (40pp no modo interseção). Entrada forjada que fique
**dentro** do limiar não é quarentenada, logo não conta para o teto de 3 que derruba o run.
O alarme de volume só olha queda (R2). Sobra o alarme de movimento (10pp share), que um viés
pequeno e consistente não atinge. O plano de 31/08 já tinha medido que **5 entradas valiam
18,8pp na presidencial**.

**Mitigação proposta (quick win Q1):** allowlist versionada de subpáginas conhecidas. Ao
encontrar subpágina fora da lista, o ingest **não a ingere e falha**, transformando "fonte
nova apareceu" em evento revisável. É a mesma forma dos outros gates da casa: declarar em vez
de assumir. O ingest já registra `subpaginas_seguidas` no relatório, então o dado para montar
a lista existe.

#### R2 · MÉDIO · O alarme de volume é unidirecional, por desenho

`check_volume.py` reprova **queda** e ignora **crescimento** (`if antes <= 0 or depois >=
antes: continue`). Foi a escolha certa para o incidente que o motivou, mas deixa a injeção em
massa por adição sem nenhum detector dedicado. **Mitigação:** estender para ganho atípico,
com limiar próprio e mais frouxo (pesquisa nova em lote é legítima perto da eleição), ou ao
menos reportar ganho acima de N no summary do run.

#### R3 · MÉDIO (legal, não técnico) · Dado licenciado no histórico do git

Desde 21/09 os 5 `audiencia-*.json`, o `audiencias-eleitorais.json` e o PPTX do painel
sindicalizado vivem em `data/publicos/fonte/`. Decisão consciente do Bera, coerente com a de
31/08 (bruto no repo privado, só derivado publicado), e verificado antes de commitar: repo
**PRIVATE**, worker serve só `dist/`, e `dist/` não tem nenhuma ocorrência de TGI, Ibope,
Kantar, Almap ou "Target Group". **O risco residual é de irreversibilidade:** tornar o repo
público um dia exigiria reescrever histórico, não bastaria apagar os arquivos.

#### R4 · ALTO para a validade do experimento · Reversão do D6

Em 21/09 o Bera decidiu voltar a usar `claude -p` como canal do campo sintético. A sonda de
19/08 reprovava esse canal porque **toda invocação expõe o e-mail do dono ao processo**, e a
sonda rodou **já com as flags mais duras** (`--setting-sources ''`, `--strict-mcp-config`, de
diretório temporário fora de repo). Não é configuração, é identidade de conta.

**Consequência, e ela é de honestidade, não de segurança do site:** a persona pode inferir
onde está rodando, o que contamina justamente o que o survey quer medir. O resultado é
publicado como competidor no leaderboard da página Modelos, com selo SINTÉTICO.
**Mitigação mínima, se o canal for mesmo o CLI:** rodar a sonda de novo **antes do campo** e,
se ela reprovar, registrar o vazamento como **condição experimental declarada** no
`estudo.md` e na página Modelos, em vez de publicar como se o canal fosse limpo. Hoje isso
está bloqueado: a sessão OAuth do CLI `claude` também expirou.

#### R5 · MÉDIO (disponibilidade) · Credencial de emergência expira em silêncio

O runbook manda `wrangler rollback` como caminho de recuperação rápida. Em 21/09 descobrimos
que o token OAuth do wrangler **expirou em 13/09** e o refresh também morreu: por **8 dias**
o caminho de emergência documentado esteve indisponível, e ninguém saberia até precisar dele.
O mesmo vale para o CLI `claude`. O deploy automático não foi afetado, porque o CI usa o
`CLOUDFLARE_API_TOKEN` dos Secrets, que segue válido (o deploy de 21/09 passou).
**Mitigação:** o `health.yml` (já roda a cada 30 min) passar a checar também a validade do
caminho de recuperação, ou uma checagem semanal que falhe alto quando a credencial local
morrer. Controle de RECUPERAR que só se testa na hora do incidente não é controle.

#### R6 · Carry-over que mudou de status · a Fase C foi ao ar com o item legal em aberto

A §4 deste plano classificou a norma do TSE sobre IA em 2026 como `[a verificar]` e como
**"o único item legal que pode bloquear a Fase C"**. A Fase C **foi publicada em 21/09**, e
o item segue sem verificação.

Atenuantes reais, não desculpas: o que está no ar é a linha de competidor marcada
**SINTÉTICO (MOCK)**, com aviso de que o campo não rodou e de que nada do que ela produz
entra no forecast oficial; o motor é fail-closed contra pesquisa sintética; e desde 21/09 o
harness nem congela modelo sintético sem lastro. Ou seja, **não há número sintético sendo
apresentado como pesquisa**.

Ainda assim, o plano dizia "verificar antes de ir ao ar" e foi ao ar. Registrar isso é o
ponto: a decisão de publicar foi consciente quanto ao QA, e não quanto a este item.
**Encaminhamento:** ler a resolução vigente antes de o campo REAL rodar, que é exatamente
quando a linha deixa de ser mock e passa a exibir número de origem sintética. Faltam 13 dias
para o 1º turno, então isso deixou de ser pendência de planejamento e virou pendência datada.

#### R7 · MÉDIO · A credencial local de deploy é muito mais ampla que a tarefa

Observado em 21/09, quando o Bera refez o `wrangler login` e a URL de OAuth expôs os escopos
pedidos. Não é escolha dele: é o conjunto **padrão** do wrangler. Entre eles, além do
esperado `workers:write` e `pages:write`:

`secrets_store:write` · `connectivity:admin` · `email_routing:write` · `email_sending:write` ·
`ssl_certs:write` · `d1:write` · `queues:write` · `containers:write` · `cloudchamber:write` ·
`ai:write` · `browser:write` · `zone:read` · `offline_access`

Para publicar HTML estático, o necessário é `workers:write` e pouco mais. O token que vive no
laptop pode **mandar e-mail pelo domínio**, **mexer em certificado TLS**, **escrever no cofre
de segredos** e administrar conectividade da conta. Máquina comprometida não perde só o site.

**Distinção que importa, e ela ainda deixa E1 em aberto:** isto é o token OAuth **local**, do
`wrangler login`. O `CLOUDFLARE_API_TOKEN` usado pelo CI é **outra credencial**, criada no
painel, e o escopo dela segue não verificado desde 31/08. Ou seja, R7 não responde E1, mostra
que a pergunta vale para os dois caminhos.

**Mitigação:** usar, no uso rotineiro local, um API token de escopo mínimo ("Edit Cloudflare
Workers") exportado como `CLOUDFLARE_API_TOKEN`, em vez da sessão OAuth ampla; deixar o OAuth
para o que de fato precisa de administração. Efeito colateral bom: o mesmo token serviria para
o `wrangler deploy` das sessões, que hoje depende de um OAuth que expira em silêncio (R5).

#### R6 · ENCERRADO por decisão do Bera (21/09), com a exposição de hoje medida

O Bera decidiu que a resolução do TSE sobre IA **não é impeditivo do projeto**, e que o item
só volta se aparecer novidade.

Registro do que isso custa HOJE, para a decisão ser julgável depois: **nada**. O que está no
ar é a linha de competidor marcada SINTÉTICO (MOCK), com aviso de que o campo não rodou;
nenhum número de origem sintética é publicado. O primeiro campo real rodou em 21/09 e **não
foi publicado**, por decisão do mesmo dia, devido ao defeito de denominador do `agrega()`.
Ou seja, não existe saída sintética exposta ao público que a norma pudesse alcançar.

O item volta a valer no dia em que um resultado sintético for efetivamente publicado como
número. Até lá, encerrado.

### 0.4. Recomendações priorizadas, revisão 2

| # | Ação | Esforço | Por quê agora |
|---|---|---|---|
| **Q1** | Allowlist de subpáginas no ingest, fail-closed em fonte nova | baixo | Fecha R1, que é uma porta que eu abri em 21/09, a 13 dias da eleição |
| **Q2** | Sonda de isolamento antes de qualquer campo sintético; se reprovar, declarar na página | baixo | Fecha R4 sem discutir a decisão do Bera: mede e declara |
| **Q3** | Checagem periódica da credencial de recuperação | baixo | Fecha R5. Um comando no `health.yml` |
| **Q4** | Reportar ganho atípico de volume no summary (sem reprovar) | baixo | Reduz R2 sem risco de falso positivo perto da eleição |
| ~~**E1a**~~ | ~~Escopo do `CLOUDFLARE_API_TOKEN` do CI~~ · **FECHADO em 21/09** | | Bera criou token pelo template "Edit Cloudflare Workers", restrito à conta e à zona `bera.ia.br`, e substituiu o segredo. Verificado ponta a ponta: deploy passou (run 35658811809, passo "Publicar (Cloudflare)" verde) e as 4 rotas respondem 200. Pendência mais antiga do plano, aberta desde 31/08 |
| **E1b** | Exportar o mesmo token como `CLOUDFLARE_API_TOKEN` no perfil local | baixo, é do Bera | Fecha R7 (a sessão OAuth do wrangler pede `secrets_store:write`, `connectivity:admin` e `email_sending:write` para publicar HTML) e R5 de carona (token não expira em silêncio como o OAuth de 4h, que deixou o rollback do runbook morto por 8 dias) |
| **E2** | Pinar as GitHub Actions por SHA | médio | ASI04. Segue aberto desde 31/08 |
| **E3** | Escrever o procedimento de comunicação externa de número errado | médio | Em contexto eleitoral, rollback silencioso não resolve print que já circulou |
| ~~**E4**~~ | ~~Ler a resolução do TSE sobre IA~~ · **ENCERRADO em 21/09** | | Decisão do Bera: não é impeditivo. Exposição hoje é zero (nada sintético publicado como número). Reabrir só se um campo real for ao ar |

---

## 1. Mapa: o que é "o agente"

**Não há LLM em runtime.** O agente avaliado é o **pipeline autônomo `atualizar-eleicoes`**
(GitHub Actions, cron diário às 10:37 UTC, com janela que autoencerra em 01/11/2026).

| Dimensão | O que é, de fato |
|---|---|
| **Acessa** | `pt.wikipedia.org` (leitura, via `src/ingest_polls.py`) · `cdn.tse.jus.br` (sonda em observação, 403 esperado) · o próprio repositório (`permissions: contents: write`) · a conta Cloudflare (`CLOUDFLARE_API_TOKEN`) |
| **Decide sozinho** | se houve pesquisa nova (`git diff --quiet data/live/polls.json`); se sim, re-simula 20 mil Monte Carlo por corrida, congela 5 modelos, reconstrói 30 páginas, roda os gates e **publica em produção** |
| **Age sozinho** | `wrangler deploy` (via `cloudflare/wrangler-action@v3`, wrangler fixado em 4.99.0), depois `git add data dist` + `git commit` + `git push` na `main` |
| **Secrets** | `CLOUDFLARE_API_TOKEN` em GitHub Secrets, rotacionado em 31/08/2026. `.gitignore` cobre `.dev.vars`, `*.token`, `*.secret`, `.api_cache/`. `FOOTBALL_DATA_TOKEN` foi removido por não ter uso |
| **Superfície pública** | 30+ páginas estáticas servidas pelo `worker.js`, com CSP, `Referrer-Policy`, `Strict-Transport-Security` e `Cache-Control` por tipo |
| **Humano no meio** | **nenhum**, entre a edição de uma tabela na Wikipédia e a publicação no site |

**O que a Fase C acrescenta ao mapa:** conteúdo gerado por LLM (personas sintéticas de
eleitores) entrando no mesmo fluxo de dados, e fichas de públicos políticos publicadas em
site aberto durante a campanha.

---

## 2. Checklist NIST Cybersecurity Framework

| Categoria | Pergunta | Resposta | Observação ancorada em fato |
|---|---|---|---|
| **Identificar** | Sabemos quais sistemas, dados e ferramentas o agente pode acessar? | **Sim** | Inventário pequeno e declarado em `.github/workflows/atualizar-eleicoes.yml` e `docs/automacao-setup.md`. Quatro superfícies, listadas na §1. |
| | Pensamos em como o agente se encaixa no ambiente? | **Sim** | Janela temporal explícita (preflight encerra após 01/11/2026), `concurrency group` impede runs simultâneos, e o cron da Copa se autoencerrou por data (`today > 2026-07-20 → run=0`). |
| | Consideramos os riscos de dar a ele acesso a tarefas confidenciais? | **Não tenho certeza** | O **escopo** do `CLOUDFLARE_API_TOKEN` não foi verificado (não é possível ler permissões do painel daqui). Se for token de conta ampla em vez de escopo mínimo "Edit Workers", o raio de dano de um vazamento passa muito além deste site. **Falta checar:** painel Cloudflare, permissões do token. |
| **Proteger** | Podemos controlar com quem o agente fala e o que ele pode ver ou fazer? | **Não** | O `permissions: contents: write` é escopo limitado, e isso é bom. Mas a **entrada é irrestrita**: `src/ingest_polls.py` não tem uma única validação de conteúdo (busca por quorum/plausibilidade/gate retorna apenas 2 ocorrências, ambas sobre correção de ano em data), e escreve `polls.json` direto, sem etapa de candidato nem diff. |
| | As pessoas foram treinadas sobre o que o agente pode e não pode fazer? | **Não** | Autor único, então "treinamento" vira documentação. E a documentação está **errada**: `docs/runbook-incidente.md` descreve os gates do `src/ingest.py` (quorum de fonte dupla, plausibilidade, diff-before-write) como a proteção vigente. Aqueles gates são da edição Copa. A edição atual não os tem. O operador está treinado no sistema anterior. |
| | Os dados confidenciais estão protegidos contra vazamento? | **Sim** | Secrets fora do repo (GitHub Secrets), `.gitignore` cobrindo os padrões de token, rotação executada em 31/08, credencial sem uso removida. Nenhum secret aparece em `data/` ou `dist/`. |
| **Detectar** | Temos como identificar se o agente está fazendo algo incomum ou errado? | **Não** | Os gates existentes checam **coerência interna**, não plausibilidade: `eleicoes_model.py` valida somas e monotonicidade; `atualizar_eleicoes.sh` valida estrutura, zero-dep e sintaxe do JS. **Nenhum ponto do pipeline compara o forecast de hoje com o de ontem.** Um dado adulterado que seja internamente coerente atravessa a cadeia inteira sem disparar nada. |
| | Há alguém ou algo monitorando o comportamento regularmente? | **Parcialmente** | `health.yml` roda a cada 30 min, porém mede **disponibilidade** (HTTP 200 + presença de conteúdo) em `/` e `/presidencial`. Um site publicando número errado responde 200 e passa no health. |
| **Responder** | Se algo der errado, temos plano para consertar rápido? | **Sim** | `docs/runbook-incidente.md` traz classificação por gravidade, detecção e rollback (`wrangler rollback`, ou `git checkout <commit-bom> -- dist`). Ressalva: precisa da correção apontada acima. |
| | Sabemos quem notificar e como comunicar? | **Não tenho certeza** | O runbook cobre a mecânica técnica. Não há nada sobre **comunicação externa** se um número errado já circulou: em contexto eleitoral, um forecast falso publicado e printado não se resolve com rollback silencioso. |
| **Recuperar** | Poderíamos recuperar dados ou serviços? | **Sim** | Todo estado publicado é versionado: o robô commita `data` e `dist` a cada ciclo, então qualquer versão anterior é recuperável por commit, e o Worker tem rollback próprio. Trilha de auditoria real. |
| | Temos plano para melhorar o agente após um incidente? | **Sim, na prática** | Há precedente documentado: `docs/retrospectiva-copa2026.md` registra o jogo 103 perdido virando alarme de completude na edição seguinte. O ciclo funciona; não está escrito como processo. |

**Placar:** 6 Sim · 3 Não · 2 Não tenho certeza · 1 parcial.

### Extensões agênticas aplicáveis

- **Ações irreversíveis mapeadas?** Sim: `wrangler deploy` e `git push` na `main`. Ambas
  sem aprovação humana, por desenho aprovado.
- **Least-privilege?** Parcial: `contents: write` é mínimo no GitHub; o escopo do token
  Cloudflare é a incerteza da §2.
- **Entrada sanitizada contra poisoning?** **Não.** É o gap central deste plano.
- **Saída validada antes de virar HTML?** **Não**, mas hoje não explorável (ver G3).
- **Kill switch?** Sim, na prática: desabilitar o workflow no GitHub, ou revogar o token.
  Não está documentado como procedimento.

---

## 3. Ameaças aplicáveis

| Ameaça | Por que se aplica aqui | Mitigação |
|---|---|---|
| **LLM04 · Data Poisoning** (≈ dado de entrada não confiável) | A fonte primária é a Wikipédia, editável por qualquer pessoa, e entra sem validação num pipeline que publica sozinho. **Ver §3.1: está medido.** | Gate de plausibilidade no ingest (delta vs consenso da corrida), quorum ou confirmação em segundo ciclo, e diff-before-write como no `ingest.py` da Copa |
| **LLM06 · Excessive Agency** | O agente publica em produção sem humano no meio, todo dia | Manter o deploy automático (é a decisão de produto), porém condicionar a um gate de plausibilidade que force revisão quando o movimento for atípico |
| **LLM09 · Misinformation** | A saída é um forecast eleitoral apresentado como número, em ano de eleição, assinado pelo autor | As páginas já declaram fonte, `as_of` e banda de incerteza. Falta o alarme de movimento atípico |
| **ASI03 · Identity & Privilege Abuse** | O agente tem credencial própria de deploy na conta Cloudflare | Confirmar escopo mínimo do token (pendência da §2); rotação já praticada |
| **ASI04 / LLM03 · Supply chain** | Depende de `actions/checkout@v4`, `actions/setup-python@v5`, `cloudflare/wrangler-action@v3`, todos por tag móvel, não por SHA | Pinar por commit SHA. Wrangler já está pinado em 4.99.0, o que é o bom precedente a estender |
| **ASI10 · Rogue Agent** | Pipeline autônomo em produção com credencial de deploy | Kill switch existe (desabilitar workflow, revogar token) mas não está escrito no runbook |
| **LLM05 · Improper Output Handling** | `src/build_eleicoes.py` **não escapa nada** ao gerar HTML | **Hoje não explorável** (ver G3), mas a Fase C adiciona campos novos. Adotar escaping por padrão antes de qualquer campo de texto livre chegar à página |
| **ASI09 · Human-Agent Trust Exploitation** *(Fase C)* | Personas sintéticas apresentadas em site público podem ser lidas como pesquisa real | Rotulagem SINTÉTICO estrutural (flag obrigatória no schema), não por convenção, mais o gate anti-vazamento já previsto no C3 |

### 3.1. O vetor principal, medido

A cadeia completa, verificada: editar tabela na Wikipédia → `ingest_polls.py` aceita sem
checar → agregador incorpora → invariantes passam (o dado é internamente coerente) → gates
de build passam → `wrangler deploy` → site publica. **Nenhum elo detecta.**

O que **amortece** o ataque, e é um controle real já existente: o peso de cada pesquisa é
`recência × sqrt(min(amostra, 3000)/1000)`. O **teto de 3000 na amostra** impede que uma
entrada forjada ganhe peso desproporcional inflando o N declarado. Isso importa e está bem
feito.

Medindo o impacto residual com o dado real de 29/08:

| Corrida | Peso do agregado | Quanto vale **uma** entrada forjada |
|---|---|---|
| **GOV-RR e SEN-RR** | 0,82 | **67,9%** |
| GOV-RO | 2,38 | 42,1% |
| GOV-SC | 2,57 | 40,3% |
| GOV-PR | 13,28 | 11,5% |
| **PRES** | 37,44 | 4,4% (18,8pp com 5 entradas) |

**Leitura honesta:** na presidencial o amortecedor funciona, uma entrada isolada move ~4pp,
o que já é material mas não inverte a corrida. **Nas corridas estaduais pouco pesquisadas
ele não funciona:** em Roraima, uma única edição na Wikipédia decide dois terços do que o
site publica sobre governo e Senado do estado. Duas das 55 corridas estão nessa situação, e
oito estão acima de 33%.

---

## 4. Transparência e legal

- **Usa IA?** Hoje, não em runtime. **Na Fase C, sim**: as personas sintéticas são geradas
  por LLM e o resultado vai a um site público.
- **Rotular saída de IA (EU AI Act, Art. 50)?** O projeto é brasileiro e hospedado fora da
  UE, então a obrigação direta é discutível. Independente disso, a rotulagem é **exigida
  pelo próprio método** já decidido: o vox obriga o banner "SINTÉTICO: não é evidência de
  comportamento real", e a decisão do Bera de 29/08 põe o synths como competidor, nunca no
  oficial. O plano da Fase C já converte isso em flag obrigatória de schema (C3a) e gate
  anti-vazamento (C3d), que é a forma correta: estrutural, não editorial.
- **Prática proibida (Art. 5)?** Não. Não há manipulação subliminar, scoring social, nem
  inferência sobre indivíduos. As fichas descrevem agregados de painel, não pessoas.
- **Alto risco (Anexo III)?** Não se enquadra. Anexo III não cobre previsão eleitoral
  editorial publicada por um particular.
- **Legislação eleitoral brasileira sobre uso de IA:** `[a verificar]`. O TSE regulou uso de
  IA em propaganda eleitoral no ciclo anterior, e há resolução própria para 2026 que eu
  **não confirmei** e não vou citar de memória. Este site não é propaganda eleitoral (não
  pede voto, não é contratado por candidato), o que provavelmente o coloca fora do escopo,
  mas a publicação de "pesquisa sintética" durante a campanha merece uma leitura da norma
  vigente antes do C2 ir ao ar. **Este é o único item legal que pode bloquear a Fase C.**

---

## 5. Recomendações priorizadas

### Quick wins (baixo esforço, alto retorno)

1. **Gate de plausibilidade no `ingest_polls.py`.** Rejeitar ou quarentenar entrada cujo
   share desvie mais que um limiar do consenso recente da corrida; escrever
   `polls.json.candidate` + diff, como o `ingest.py` da Copa já faz. Ataca diretamente o
   67,9% de Roraima. **Maior retorno por linha de código deste plano.**
2. **Corrigir o `runbook-incidente.md`.** Ele hoje promete proteções que a edição atual não
   tem. Documentação errada é pior que documentação ausente, porque impede a pergunta.
3. **Alarme de movimento atípico no `atualizar_eleicoes.sh`.** Comparar o forecast novo com
   o anterior e falhar o run (que já vira e-mail) quando algum candidato se mover além de um
   limiar. O pipeline já tem o hábito de falhar em gate; falta este.
4. **Escaping por padrão no builder**, antes que a Fase C adicione campos de texto livre.
5. **Documentar o kill switch** no runbook: desabilitar o workflow e revogar o token, com os
   cliques exatos.

### Estruturais (planejar)

6. **Confirmar o escopo do `CLOUDFLARE_API_TOKEN`** e reduzir a "Edit Cloudflare Workers"
   se estiver mais amplo. É a incerteza de maior raio de dano deste plano.
7. **Pinar as GitHub Actions por SHA** em vez de tag móvel.
8. **Nota de correção pública** no runbook: o que fazer se um número errado já circulou.
9. **Ler a norma eleitoral vigente sobre IA** antes de publicar conteúdo sintético (§4).

---

## 6. Memo à liderança

O Ficha do Jogo está hoje mais bem protegido do que a maioria dos projetos pessoais que
publicam sozinhos: os segredos estão fora do repositório e foram rotacionados esta semana,
o site sai com cabeçalhos de segurança e política de conteúdo restritiva, cada publicação
fica versionada e reversível, o robô se desliga sozinho depois da eleição, e existe um
runbook de incidente com rollback testado. A cultura de "gate que falha em vez de publicar"
já está instalada, e ela é a coisa mais difícil de construir.

A exposição está concentrada em um ponto, e ele é estrutural, não acidental: **o sistema
confia integralmente no que lê**. A fonte primária de pesquisas é a Wikipédia, que qualquer
pessoa edita, e não existe nenhuma validação entre o que é lido e o que é publicado. Todos
os controles do projeto são de saída, e verificam se o número é coerente consigo mesmo, não
se ele é plausível. Um dado falso bem formatado atravessa a cadeia inteira e chega ao ar em
poucos minutos, sem que nada dispare.

O tamanho disso foi medido, não estimado. Na corrida presidencial o dano de uma entrada
isolada é de cerca de 4 pontos percentuais, porque o agregado tem volume suficiente para
diluir, e há um teto de amostra bem desenhado que impede um resultado forjado de ganhar peso
artificial. Nas corridas estaduais pouco pesquisadas o quadro é outro: em Roraima, uma única
edição na Wikipédia determina dois terços do que o site publica sobre o governo e o Senado
do estado. Oito das 55 corridas passam de um terço.

Há ainda um risco silencioso que vale mais atenção do que costuma receber: o runbook de
incidente descreve proteções de entrada que existiam na edição anterior do projeto e que a
atual não herdou. O operador acredita estar protegido por gates que não estão mais lá. Numa
emergência, esse tipo de divergência custa os minutos que mais importam.

Nada disso pede reengenharia. As cinco correções de maior retorno são pequenas e cabem na
mesma frente de trabalho já em curso, e a primeira delas, um gate de plausibilidade na
entrada, resolve sozinha a maior parte da exposição. A recomendação é tratá-la como parte da
Fase C, e não como melhoria futura: a eleição é em 34 dias, e o valor de um forecast público
é exatamente a confiança de que o número não foi plantado por um terceiro.

---

## 7. Declaração de uso de IA

- **Ferramenta:** Claude Code (Opus 5, Anthropic) · **Data:** 31/08/2026
- **Como foi usada:** estruturou a análise a partir de fatos verificados diretamente no
  repositório (leitura de `src/ingest_polls.py`, `src/ingest.py`, `src/eleicoes_model.py`,
  `src/build_eleicoes.py`, `worker.js`, `.github/workflows/*.yml`, `docs/runbook-incidente.md`)
  e de medição executada sobre `data/live/polls.json` na data.
- **Verificação:** os números da §3.1 vêm de cálculo sobre o dado real, reproduzível com a
  fórmula de peso do `eleicoes_model.py` (`0.5**(idade/21) * sqrt(min(amostra,3000)/1000)`).
  A ausência de gates foi confirmada por leitura, não por inferência. O item legal da §4 está
  explicitamente marcado como não confirmado.
- **Responsabilidade:** revisão e edição finais são do autor.
