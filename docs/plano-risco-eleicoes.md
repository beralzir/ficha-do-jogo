# Ficha do Jogo · Eleições 2026, plano de risco e segurança de IA

**Projeto:** Ficha do Jogo, modelo probabilístico e dashboard da eleição brasileira de 2026,
publicado em https://bera.ia.br/ficha-do-jogo (Cloudflare Worker + HTML estático).
**Tier:** T1 (solo/pequeno), com as extensões agênticas aplicadas, porque o sistema age
sozinho sobre produção.
**Data:** 31 de agosto de 2026 · **Método:** NIST CSF + OWASP Top 10 (LLM 2025 / Agentic
2026) + SAIF, via skill `para-raios`.

> Todas as afirmações abaixo foram verificadas por leitura do código e por medição no dado
> real desta data. Onde não deu para confirmar, está escrito "Não tenho certeza" e o que
> falta checar.

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
