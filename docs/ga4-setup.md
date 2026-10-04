# GA4 + GTM: setup do tagueamento · Ficha do Jogo (Eleições 2026)

> Runbook de SAÍDA da skill **tags-bera**, derivado de `site.config.json` via `scripts/derive.mjs`.
> Reescrito na auditoria de 04/10/2026 (edição Eleições). A versão da Copa está no git
> (`git show 118c7ec:docs/ga4-setup.md`). Painel GA4 em PT-BR. Stack: Cloudflare Worker (estático)
> + GTM + GA4, sem gtag.js direto.

- **Site:** https://bera.ia.br/ficha-do-jogo/ · edição Eleições 2026 na raiz, Copa 2026 congelada em `/copa2026/`.
- **GTM:** `GTM-K524DJN7` (contêiner do bera.ia.br inteiro, compartilhado com coala, rir, brand guide, ai-clip e home).
- **GA4:** `G-X6GGP30QVK` (propriedade `bera.ia.br`, 541271649). O ID vai só nas tags do GTM, nunca na página.
- **page_section:** `ficha_do_jogo` (empurrado pelo `track()` e também carimbado pelo caminho na Google tag).
- **page_name:** `eleicoes_index` (/), `eleicoes_dashboard` (/presidencial), `eleicoes_inflexoes`, `eleicoes_modelos`,
  `eleicoes_uf` (as 27 /uf-xx, com a UF no `page_location`), `publicos` e `publico-<slug>`, `santinho`,
  `privacidade`, `404`. O arquivo `/copa2026/` segue com os nomes da Copa (`index`, `dashboard`, `resultados`, `bolao`, `modelos`).
- **Páginas com GTM:** as 40 servidas na raiz (32 de Eleições, incluindo `/privacidade`, mais 6 de públicos, santinho e 404).
  `test_tagueamento.py` confere todas a cada rodada do cron.

---

## 0 · Privacidade (regra do Bera, 04/10/2026)

**O site mede só navegação.** Nenhum parâmetro leva candidato (nome, número, `sq`), texto digitado,
valor de filtro, escolha do eleitor ou URL de destino completa. Opinião política é dado pessoal
sensível (LGPD, art. 5º, II, e art. 11), e a combinação "quem consultou qual candidato" permitiria
inferi-la.

| Camada | O que garante | Onde |
|---|---|---|
| `track.js` (`shell.TRACK`) | `fdj_outbound` manda só o host, nenhum hook lê valor de campo, o acordeão manda o título curado | `src/shell.py` |
| Santinho | única ação registrada: troca de aba de cargo (`nav_select`, `context=cargo_tab`) | `src/build_santinho.py` |
| Oposição ("não medir") | com a escolha gravada (`localStorage fdj-nao-medir=1`), o GTM nem carrega e o `track()` não empurra | `shell.GTM_HEAD`, `shell.TRACK`, `/privacidade` |
| Transparência | página `/privacidade` (finalidade, retenção, base legal, como se opor, contato) linkada no rodapé de toda página | `build_eleicoes.build_privacidade()` |
| Guardas | lista fechada de chamadas no santinho (teste 7c) e regras do site, com erros plantados | `src/test_tagueamento.py`, `src/test_santinho_pagina.py` |
| Painel GA4 | sem cliques de saída nem pesquisa no site (mandariam a URL do TSE com o `sq` e texto livre), retenção de 2 meses, Signals desligado | §0.1 |

Base legal: legítimo interesse (LGPD, art. 7º, IX), como admite o
[guia orientativo de cookies da ANPD](https://www.gov.br/anpd/pt-br/documentos-e-publicacoes/guia-orientativo-cookies-e-protecao-de-dados-pessoais.pdf)
(out/2022, p. 25–26) para medição de audiência agregada, sem perfil e com transparência e oposição.
A avaliação está em `docs/privacidade/avaliacao-legitimo-interesse.md`.

### 0.1 · Estado do painel (lido por API em 04/10/2026)

| Item | Estado | Como ficou assim |
|---|---|---|
| Medição otimizada: cliques de saída | **desligado** | API, 04/10/2026, autorizado pelo Bera (estava ligado, com zero eventos `click` em 90 dias: nada vazou) |
| Medição otimizada: pesquisa no site | **desligado** | idem (zero `view_search_results` em 90 dias) |
| Medição otimizada: rolagem, formulário, histórico, vídeo, download | ligados | sem dado pessoal. O histórico pode gerar page_view com `#cargo` no santinho (não é sensível) |
| Retenção de dados de evento e de usuário | **2 meses** | API, 04/10/2026, autorizado (estava em 14 meses) |
| Google Signals | desligado | já estava |
| Redação de e-mail | ligada | já estava |
| Vínculo com Google Ads | nenhum | já estava |
| Compartilhamento de dados da conta (produtos do Google, modelagem e benchmark, suporte, vendas) | **4 ligados** | a API não altera: **passo manual do Bera** (§8) |
| Dados granulares de local e dispositivo | não lido | a API não expõe: **passo manual do Bera** (§8) |

### 0.2 · CSP

O `worker.js` libera GTM e GA4 e, desde 25/09/2026, `https://www.google.com` no `connect-src` (rota de
reserva do gtag, `gaf=1`). Não é Google Signals. Detalhe no histórico deste arquivo.

## Pré-flight de cota

| Categoria (escopo Evento) | Em uso (04/10/2026) | Cap | A adicionar |
|---|---|---|---|
| Dimensões personalizadas | 23 | 50 | **0** |
| Métricas personalizadas | 5 | 50 | **0** |

A propriedade é compartilhada pelos sites do bera.ia.br, e todas as definições abaixo já existem.

---

## 1 · Dimensões personalizadas (7, todas existentes)

Escopo Evento. **Parâmetro do evento** = nome exato do `dataLayer` (gotcha #1).

| Dimensão | Parâmetro | Valores na edição Eleições |
|---|---|---|
| `page_section` | `page_section` | `ficha_do_jogo` |
| `page_name` | `page_name` | ver enum no topo. **Estava `(not set)` em 100% dos eventos até 04/10** (as tags não encaminhavam, ver §5) |
| `section_id` | `section_id` | `estados`, `corrida`, `evolucao`, `segundo_turno`, `governador`, `senado`, `movimentos`, `eventos`, `hipoteses`, `dias`, `leaderboard` |
| `interaction_type` | `interaction_type` | `accordion_open`, `anchor_jump` |
| `target` | `target` | page_name de destino (nav), host (outbound), título do acordeão, id do cargo (santinho) |
| `scene` | `scene` | page_name onde a interação aconteceu |
| `context` | `context` | `topbar_tab`, `brand`, `card`, `inline`, `cargo_tab`, `proposta_tse`, `ficha_tse`, `footer_license` |

## 2 · Métricas personalizadas (4, todas existentes)

| Métrica | Parâmetro | Unidade | Nota |
|---|---|---|---|
| `engaged_seconds` | `engaged_seconds` | Padrão | `fdj_page_engaged` (≥10 s de aba ativa) |
| `depth_percent` | `depth_percent` | Padrão | marcos 25/50/75/100 |
| `dwell_time_seconds` | `dwell_time_seconds` | Segundos | proxy grosso: tempo do título da seção na tela |
| `interaction_value` | `interaction_value` | Padrão | reservada: nenhum hook emite na edição Eleições |

`page_version` (`v2.0`) é sent-only: vai no push, não vira dimensão nem é encaminhado.

## 3 · Eventos principais (3, marcados em 04/10/2026)

| Evento | Por que é principal |
|---|---|
| `fdj_page_engaged` | leitura real ("leu" vs "abriu e saiu") |
| `fdj_interaction` | leitura ativa de conteúdo (acordeões de método e "como ler") |
| `fdj_nav_select` | caminho entre páginas: da home para a presidencial ou as UFs, uso das abas |

Contagem: uma vez por evento.

---

## 4 · Wiring no site

1. **GTM:** `shell.GTM_HEAD` no `<head>` (via `shell.HEAD`) e `shell.GTM_NOSCRIPT` logo depois do `<body>`
   (nos `topbar()` de `build_eleicoes.py`/`build_publicos.py`/`shell.py` e direto no santinho). O bootstrap
   sai antes de tudo se `localStorage fdj-nao-medir=1`.
2. **`track.js` inline** em `shell.TRACK`, no fim do `<body>` (via `shell.JS`). Inline de propósito: o gate `_ext`
   reprova `<script src>`. Expõe `window.fdjTrack` para páginas com JS próprio (hoje só o santinho).
3. **`page_name`** = `<body data-page>`. O mapa slug → page_name do `fdj_nav_select` é `shell.NAV_PAGE`
   (mais `uf-xx` → `eleicoes_uf` e `publico-*` → o próprio slug, no JS). `test_tagueamento.py` confere contra
   o `SLUG` do `worker.js`.
4. **`data-scene`** nos `h2.sech` principais (lista em §1, `section_id`).
5. **`data-context`** nos links do TSE: `proposta_tse` (presidencial e UFs), `ficha_tse` (santinho).
6. **Saíram em 04/10/2026** os hooks da Copa (calculadora, matriz, dossiê, placares), que procuravam elementos
   inexistentes na edição Eleições. O arquivo `/copa2026/` é congelado e mantém o `track.js` da época.

## 5 · Wiring no GTM: 6 pares trigger + tag

| Evento (dataLayer) | Trigger | Tag | Parâmetros encaminhados |
|---|---|---|---|
| `fdj_page_engaged` | `CE - fdj_page_engaged` | `GA4 - fdj_page_engaged` | `engaged_seconds`, `page_name`* |
| `fdj_scroll_depth` | `CE - fdj_scroll_depth` | `GA4 - fdj_scroll_depth` | `depth_percent`, `page_name`* |
| `fdj_section_view` | `CE - fdj_section_view` | `GA4 - fdj_section_view` | `section_id`, `dwell_time_seconds`, `page_name`* |
| `fdj_interaction` | `CE - fdj_interaction` | `GA4 - fdj_interaction` | `interaction_type`, `target`, `interaction_value`, `scene`, `page_name`* |
| `fdj_outbound` | `CE - fdj_outbound` | `GA4 - fdj_outbound` | `target`, `context`, `page_name`* |
| `fdj_nav_select` | `CE - fdj_nav_select` | `GA4 - fdj_nav_select` | `target`, `context`, `page_name`* |

`page_section` sai da Google tag (`GA4 - Config`, tabela por caminho), não das tags de evento.

\* **`page_name` está no workspace `fdj-eleicoes-page_name (2026-10-04)`, ainda NÃO publicado.** A versão no ar
(8, ai-clip) não encaminha `page_name`, por isso a dimensão ficou `(not set)` desde junho. Publicar depois do
deploy validado do site (§8).

Sem evento compartilhado com outro site (`fdj_` é exclusivo): nenhuma Exception (gotcha #2 não se aplica).

## 6 · Schema-validation

| Evento | Param | Tipo | Origem | DLV | Tag | GA4 |
|---|---|---|---|---|---|---|
| `fdj_page_engaged` | `engaged_seconds` | number | track §1 | `dlv - engaged_seconds` | ✅ | métrica |
| `fdj_scroll_depth` | `depth_percent` | number | track §2 | `dlv - depth_percent` | ✅ | métrica |
| `fdj_section_view` | `section_id` | string | track §3 + `data-scene` | `dlv - section_id` | ✅ | dimensão |
| `fdj_section_view` | `dwell_time_seconds` | number | track §3 | `dlv - dwell_time_seconds` | ✅ | métrica (s) |
| `fdj_interaction` | `interaction_type` | string | track §4 | `dlv - interaction_type` | ✅ | dimensão |
| `fdj_interaction` | `target` | string | track §4 | `dlv - target` | ✅ | dimensão |
| `fdj_interaction` | `scene` | string | track §4 | `dlv - scene` | ✅ | dimensão |
| `fdj_interaction` | `interaction_value` | number | sem emissor | `dlv - interaction_value` | ✅ | métrica |
| `fdj_outbound` | `target`, `context` | string | track §5/6 + `data-context` | `dlv - target`, `dlv - context` | ✅ | dimensões |
| `fdj_nav_select` | `target`, `context` | string | track §5/6, santinho | `dlv - target`, `dlv - context` | ✅ | dimensões |
| (defaults) | `page_section` | string | track + Google tag | Google tag | ✅ | dimensão |
| (defaults) | `page_name` | string | `<body data-page>` | `dlv - page_name` | ⏳ workspace não publicado | dimensão |
| (defaults) | `page_version` | string | track | não há | não há | sent-only |

Inventário no GTM: 6 triggers, 6 tags, DLVs existentes. Única pendência: o ⏳ de `page_name`.

## 7 · Validação

**Feita em 04/10/2026 (local, Playwright, todo pedido ao Google bloqueado):**
- `page_name` certo em todas as páginas, nenhum `nav_select` com `target=unknown`, `section_view` disparando,
  `outbound` com `target=divulgacandcontas.tse.jus.br`.
- Santinho: escolha, busca, filtro de espectro e pauta, detalhes e colinha feitos, e 9 valores sensíveis
  procurados no `dataLayer` (sq, número e nome escolhidos, termo, filtros): nenhum.
- "Não medir": nenhum pedido ao Google e zero eventos `fdj_*` nas páginas seguintes, e "voltar a medir" restaura.

**Depois do deploy + publish do GTM (24–48 h):**
- [ ] Tempo real: `fdj_*` chegando, com `page_name` preenchido.
- [ ] DebugView (Tag Assistant): `target` do `fdj_outbound` é só o host, e não há evento `click` automático.
- [ ] Explorar: `fdj_nav_select` × `target`/`context` e `fdj_section_view` × `section_id` × `page_name`.

## 8 · Pendências do Bera

1. **Validar localmente** as mudanças de conteúdo (página `/privacidade`, link no rodapé) antes de qualquer deploy.
   Nada sobe em 04/10 nem em 25/10 (Lei 9.504, art. 39, §5º, IV). O workflow já bloqueia.
2. **Antes do deploy, conferir que o Google já propagou o desligamento dos cliques de saída.** A API confirma
   (04/10, 08h UTC), mas o script público ainda servia o valor antigo. Tem de sair `false`:
   `curl -s "https://www.googletagmanager.com/gtag/js?id=G-X6GGP30QVK" | grep -o '"vtp_enableOutboundClick":[a-z]*'`.
   Com `true`, o GTM no santinho mandaria a URL do TSE com o `sq` no evento automático `click`.
3. **`privacidade@bera.ia.br`** (canal do titular que a página publica, Resolução CD/ANPD nº 2/2022): Email
   Routing do Cloudflare encaminhando para `bera@beralzir.com.br`. O Bera confirmou em 04/10/2026 que o bera.ia.br
   não é usado como domínio de e-mail (o MX `smtp.google.com` que estava lá não atende nada). Feito em 04/10:
   destino `bera@beralzir.com.br` verificado e regra `privacidade@bera.ia.br` → `bera@beralzir.com.br` criada
   (`wrangler email routing rules list bera.ia.br`). **Falta (Bera, painel):** Email Routing → "Fix DNS records"
   (troca o MX do Google pelos `route*.mx.cloudflare.net`) e apagar o TXT `v=spf1 include:_spf.google.com ~all`
   do bera.ia.br. Conferir com `dig +short MX bera.ia.br` e um e-mail de teste.
4. **GA4 → Administrador → Configurações da conta → Compartilhamento de dados:** desligar os 4 itens.
5. **GA4 → Administrador → Coleta de dados → Dados granulares de local e dispositivo:** desligar (recomendado: tira
   cidade e modelo de aparelho, reduz identificabilidade).
6. **Publicar no GTM** o workspace `fdj-eleicoes-page_name (2026-10-04)` (6 mudanças: `page_name` nas tags).
   Funciona com o site atual e com o novo, então pode ir antes do deploy. Em 04/10 a publicação por API foi barrada
   pelo controle de permissões da sessão: fazer pela UI do GTM (Enviar → Publicar) ou liberar a permissão.
7. Opcional: corrigir o `--mut` do tema claro em `src/theme.py` (4,43:1, abaixo de AA) para o site inteiro.
   Hoje só santinho e `/privacidade` têm o ajuste local.
