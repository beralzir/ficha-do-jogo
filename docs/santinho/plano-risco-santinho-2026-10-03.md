# Meu Santinho: plano de risco e segurança

**Projeto:** ficha-do-jogo, página pessoal e não listada "Meu Santinho"
(`bera.ia.br/ficha-do-jogo/santinho`), colinha de voto do 1º turno com dados abertos do TSE.
**Tier:** T1 (solo, pipeline autônomo)
**Data:** 03/10/2026, véspera do 1º turno
**Escopo:** a publicação desta etapa (branch `santinho-v2`, 2 commits sobre `origin/main`).

---

## 1. O sistema avaliado

Não há LLM em produção. O sistema autônomo é o **workflow `atualizar-eleicoes`** (GitHub
Actions, cron 1×/dia às 07:37 BRT). Sem humano no meio, ele:

1. ingere pesquisas;
2. roda o modelo;
3. gera as páginas;
4. a partir desta etapa, **baixa 28 zips de fotos de `cdn.tse.jus.br`** (com `actions/cache` de
   reserva) e os empacota em `dist/santinho/fotos`;
5. passa nos gates;
6. publica via `cloudflare/wrangler-action@v3` (wrangler 4.99.0, token em GitHub Secrets);
7. faz commit de volta em `data/` e `dist/`.

**O que vai ao ar no santinho:**
- 19.095 candidaturas com identidade oficial do TSE, sem CPF, título ou e-mail. Há teste que
  confere contra os 20.875 CPFs do CSV.
- Fotos oficiais do TSE.
- "Detalhes públicos" de 36 candidaturas (resumo, espectro e posição em 15 pautas), compilados
  por IA na versão 1 **sem fonte item a item**.
- A chance de eleição do modelo do site.
- Um destaque verde e vermelho pessoal, sem rótulo.

**Superfície:** página estática servida pelo Worker, com CSP `default-src 'self'`. Sem GTM e com
`noindex` (verificado no HTML gerado). Nenhuma página do site linka para ela.

## 2. Checklist NIST CSF

| Categoria | Pergunta | Resposta | Observação (fato do projeto) |
|---|---|---|---|
| **Identificar** | Sabemos o que o sistema acessa? | Sim | Wikipédia (pesquisas), `cdn.tse.jus.br` (fotos), GitHub (push) e Cloudflare (deploy). Tudo declarado em `.github/workflows/atualizar-eleicoes.yml`. |
| | Encaixe no ambiente? | Sim | Mesmo Worker e mesmo pipeline do site. O santinho entra como mais uma página e não cria serviço novo. |
| | Risco de tarefa confidencial? | Não tenho certeza | O CSV do TSE com CPF e título fica só em `.cache/tse` (gitignored) na máquina local. O CI não baixa o CSV. Falta prazo para apagar o cache local. |
| **Proteger** | Controle do que ele pode fazer? | Não tenho certeza | `permissions: contents: write`; o token da Cloudflare fica restrito a dois passos. As actions estão fixadas por **tag** (`@v4`, `@v3`), não por SHA. |
| | Pessoas sabem o que ele faz? | Sim | Projeto solo, documentado em `CLAUDE.md`, `docs/` e na memória do projeto. |
| | Dado sensível protegido? | Sim | Saída sem CPF, título, e-mail ou nascimento (`src/test_santinho_pagina.py`). Escolhas do usuário ficam só no `localStorage`. |
| **Detectar** | Percebe algo errado? | Não tenho certeza | Gates do `atualizar_eleicoes.sh` (zero-dep, estrutura, volume). **O teste do santinho não roda no CI**: um número de urna errado só seria pego localmente. |
| | Monitoramento regular? | Sim | `health.yml` verifica o site no ar. Falha de workflow gera e-mail do GitHub. |
| **Responder** | Conserto rápido? | Sim | Revert de commit e `gh workflow run ... -f force_deploy=true` (cerca de 4 min). |
| | Quem notificar? | Sim | O próprio Bera (e-mail do GitHub). |
| **Recuperar** | Recupera o serviço? | Sim | Git é a trilha completa (`data/` e `dist/` versionados). As fotos se regeneram dos zips em cache. |
| | Melhora após incidente? | Sim | Lições registradas na memória do projeto (ex.: cron parado 26/09 a 02/10). |

## 3. Ameaças aplicáveis

| Ameaça | Por que se aplica aqui | Mitigação |
|---|---|---|
| **LLM09 · Desinformação** | Os 36 "detalhes públicos" foram gerados por IA, sem fonte, e aparecem atribuídos a candidatos reais. Há item duvidoso conhecido: Flávio Bolsonaro marcado "contra Nossa Senhora Aparecida". | Publicar só o que tem fonte, ou ocultar pautas e resumos até haver fonte (ver P0). |
| **Integridade da colinha** | Número errado leva o voto para outra pessoa. A v1 tinha 19 de 23 deputados assim. | A v2 usa só dado do TSE, com teste de número único por cargo e UF, dígitos por cargo, cruzamento com a base do modelo e selo de voto anulado. **Falta:** o teste não roda no CI (P2). |
| **LLM03/ASI04 · Supply chain** | Download diário de 28 zips de governo; actions por tag; ImageMagick processando JPEG externo no runner que tem `contents: write`. | HTTPS e `unzip -t`. A foto vira `data:image/jpeg;base64` com prefixo fixo (não executa script). Pin por SHA e restrição de formato no `mogrify` (P3). |
| **ASI02/ASI03 · Privilégio do deploy** | O pipeline publica sem humano e tem token de deploy. | Token só nos passos de deploy; rodada só publica com gates verdes. |
| **ASI10 · Sistema descontrolado** | Cron publica sozinho, inclusive no **dia da eleição** (04/10, 07:37 BRT). | Pausar a publicação automática no dia 04/10 (P1). |

## 4. Transparência e legal

- **Rotulagem de IA (Res. TSE 23.732/2024, art. 9-B):** vale para conteúdo **multimídia** sintético
  em propaganda eleitoral. Texto compilado por IA numa página pessoal não se encaixa. Mesmo assim, o
  disclaimer já diz que os detalhes não foram verificados item a item.
- **Crime de divulgação de fato inverídico (Código Eleitoral, art. 323):** exige que quem divulga
  **saiba** que o fato é falso e que ele possa influenciar o eleitor. Depois de alertado sobre um
  item duvidoso, publicá-lo sem checar enfraquece a defesa de boa-fé. O disclaimer ajuda, mas não
  afasta o risco. *(Isto não é parecer jurídico.)*
- **Dia da eleição (Lei 9.504/1997, art. 39, §5º, IV):** é crime a **publicação de novos conteúdos**
  na internet no dia da eleição. O que já estava no ar pode continuar. Publicar hoje (03/10) é o
  caminho. A rodada automática de amanhã cedo republicaria o site inteiro.
- **EU AI Act:** não se aplica (sem operação na UE).

## 5. Recomendações priorizadas

**Decisões do Bera (03/10/2026):** P0 publicar os detalhes públicos **como estão**, com o risco
do art. 323 assumido por ele, depois do alerta; P1 **aplicado**: o workflow não publica em
04/10 nem em 25/10 (trava no passo "Preflight", com a data de Brasília).

**P0, antes do push (decisão do Bera):**
- Decidir o que fazer com os 36 "detalhes públicos": (a) ocultar pautas e resumos até haver fonte,
  (b) manter só os resumos biográficos (fatos de cargo, menor risco) e ocultar as pautas, ou
  (c) publicar como está, assumindo o risco do art. 323.

**P1, hoje:**
- Pausar a publicação automática em 04/10. Por exemplo, uma trava de data no passo "Preflight" do
  workflow (`if today == 2026-10-04: run=0`), retomando em 05/10. Afeta o site inteiro.

**P2, depois da eleição:**
- Pôr `src/test_santinho_pagina.py` nos gates do CI, com o cruzamento com a base do modelo
  rebaixado a aviso (lição de 26/09: teste que depende do dado do dia trava o cron).
- Apagar `.cache/tse/*.csv` (CPF e título de 20 mil candidaturas) quando a eleição acabar.

**P3, estrutural:**
- Fixar `actions/*` e `cloudflare/wrangler-action` por SHA.
- Restringir o `mogrify` a JPEG (`jpeg:` explícito e `policy.xml`).

## Fontes

- [TRE-SP: crimes eleitorais mais comuns na campanha e no dia da eleição](https://www.tre-sp.jus.br/comunicacao/arquivos/crimes-eleitorais-delitos-mais-comuns-durante-a-campanha-e-no-dia-da-eleicao)
- [TSE Temas Selecionados: divulgação de fato inverídico (CE art. 323)](https://temasselecionados.tse.jus.br/temas-selecionados/propaganda-eleitoral/crimes-na-propaganda-eleitoral/fato-inveridico-2013-divulgacao)
- [TSE: Resolução 23.714/2022 (substituiu o art. 9-A da Res. 23.610)](https://www.tse.jus.br/legislacao/compilada/res/2022/resolucao-no-23-714-de-20-de-outubro-de-2022)
- [ConJur: propaganda eleitoral e IA na Res. 23.732/2024](https://www.conjur.com.br/2024-mar-21/propaganda-eleitoral-o-que-pode-e-o-que-nao-pode-a-partir-da-nova-resolucao-do-tse//?print=1)
