# GA4 + GTM — Setup do tagueamento · Ficha do Jogo (Copa 2026)

> Runbook de SAÍDA da skill **tags-bera**, derivado de `site.config.json` via `scripts/derive.mjs`. Painel GA4 em **PT-BR (2026)**. Modo: **runbook manual** (zero credencial). Stack: Cloudflare Workers (estático) + GTM + GA4, **sem gtag.js**.

- **Site:** https://bera.ia.br/ficha-do-jogo/ · 5 páginas live geradas por Python.
- **GA4 Measurement ID:** `G-X6GGP30QVK` (vai nas tags do GTM, **não** na página)
- **GTM Container ID:** `GTM-K524DJN7` (injetado no `<head>` das 5 páginas live)
- **page_section:** `ficha_do_jogo` · **page_name:** `index | dashboard | resultados | bolao | comparativo`
- **Escopo (Opção B):** GTM só nas **5 páginas live**. `copa2026_artifact.html` (light) e `copa2026_dashboard_generico.html` (white-label) saem **SEM GTM** (removido na build dessas variantes).
- **Quando executar:** dims/métricas **ANTES** do deploy (definições só capturam a partir da criação — gotcha #4).

---

## 0 · Estado / pré-condições

- **Property + container DEDICADOS de bera.ia.br** (IDs reais acima). Confirme no painel se a property é **nova/dedicada** (não compartilhada) — se for dedicada, "em uso" no pre-flight de cota = 0.
- **Injeção no site = só `src/shell.py`** (constantes `HEAD`/`JS`/`topbar`). `dist/` é gerado — não editar à mão.
- **Gate zero-dep liberado p/ GTM:** `atualizar.sh` (passo 3/4) reprova URL externa em `dist/*.html`. O `_ext` foi ajustado p/ permitir `googletagmanager.com` (única dep externa, só nas live). artifact/generico saem limpos e passam sem depender disso.
- **Execução por API:** indisponível (a conta bloqueia credencial de escrita). Ficamos no manual.
- **CSP (`worker.js`) libera `https://www.google.com` no `connect-src`** (25/09/2026). É a rota de reserva do gtag: se o `fetch` do hit para `www.google-analytics.com` é rejeitado (bloqueio de rede/DNS, rede instável), ele reenvia o MESMO hit para `www.google.com/g/collect` com `gaf=1` e sem cookies. Sem a liberação, a CSP barrava a reserva e o hit se perdia inteiro (page_view e `fdj_*`); o sintoma era o erro "Connecting to 'https://www.google.com/g/collect…' violates … connect-src" no console. **Não é Google Signals:** a propriedade entrega `allow_google_signals=false` e todo hit sai com `ngs=1`. A CSP oficial do Google para GA4 sem anúncios (atualizada em 18/09/2026) pede `https://*.google.com`; liberamos só o host que o código usa.

## Pré-flight de cota (~2 min)

Administrador → Configurações da propriedade → **Exibição de dados** → **Definições personalizadas** → **Informações de cota** (canto sup. dir.).

| Categoria (escopo Evento) | Em uso | Cap | A adicionar | OK se |
|---|---|---|---|---|
| Dimensões personalizadas | `{ver}` | 50 (360: 125) | **7** | total < 41 |
| Métricas personalizadas | `{ver}` | 50 (360: 125) | **4** | total < 41 |

> Property dedicada → "em uso" = 0, folga total.

---

## 1 · Dimensões personalizadas (7)

Administrador → … → Definições personalizadas → **Dimensões personalizadas** → **Criar**. Escopo = **Evento**. **Parâmetro do evento** = EXATO do dataLayer (case-sensitive — **erro #1**).

| Nome da dimensão | Escopo | Parâmetro do evento | Descrição |
|---|---|---|---|
| `page_section` | Evento | `page_section` | Discriminador do site na property (sempre `ficha_do_jogo`) |
| `page_name` | Evento | `page_name` | Qual das 5 páginas (index/dashboard/resultados/bolao/comparativo) |
| `section_id` | Evento | `section_id` | Seção no `fdj_section_view` (calculadora, matriz, metodologia, classificacao, chave) |
| `interaction_type` | Evento | `interaction_type` | Tipo de interação (calc_select, matrix_filter, matrix_sort, accordion_open, dossie_open, anchor_jump) |
| `target` | Evento | `target` | Alvo da ação (id do controle, seleção do dossiê, título do acordeão, página de destino) |
| `scene` | Evento | `scene` | Contexto de onde a interação partiu (calculadora, matriz, ou page_name) |
| `context` | Evento | `context` | Contexto de nav/outbound (index_card, topbar_tab, footer_license) |

---

## 2 · Métricas personalizadas (4)

aba **Métricas personalizadas** → **Criar**. Escopo = **Evento**. Unidade: **Segundos** p/ duração, **Padrão** p/ o resto.

| Nome da métrica | Escopo | Parâmetro do evento | Unidade | Descrição |
|---|---|---|---|---|
| `engaged_seconds` | Evento | `engaged_seconds` | Padrão | Segundos ativos quando a sessão vira "engajada" (≥10s) — no `fdj_page_engaged` |
| `depth_percent` | Evento | `depth_percent` | Padrão | Marco de rolagem (25/50/75/100) — no `fdj_scroll_depth` |
| `dwell_time_seconds` | Evento | `dwell_time_seconds` | **Segundos** | Tempo na seção (saída do IntersectionObserver) — no `fdj_section_view` |
| `interaction_value` | Evento | `interaction_value` | Padrão | Valor numérico opcional (ex.: has_query=1 na busca) — no `fdj_interaction` |

> ⚠️ Nada de param `value` (reservado ecommerce — gotcha #3); usamos `interaction_value`. `page_version` é **sent-only** (vai no push, sem dimensão).

---

## 3 · Eventos principais (3) — APÓS publish do GTM + tráfego real

Administrador → … → **Eventos** → marcar ⭐. Só aparecem **depois** de dispararem em produção (etapa final).

| Evento | Por que é principal |
|---|---|
| `fdj_page_engaged` | **Engajamento real** — métrica-norte do dashboard ("leu de verdade", não bounce) |
| `fdj_interaction` | **Uso ativo** — calculadora, filtros, dossiês, acordeões. Proxy de "quem USA o bolão e o dashboard" (segmente por `page_name`/`interaction_type`) |
| `fdj_nav_select` | **Chegada/escolha de página** — quem sai da home pro bolão/dashboard (segmente por `target`/`context`) |

---

## 4 · Wiring no SITE (já aplicado em `src/shell.py` + builders)

Tudo injetado no **ponto único `src/shell.py`** + data-attributes nos builders. Referência do que entrou:

1. **Snippet GTM** — `GTM_HEAD` prefixado em `shell.HEAD` (`<script>` no topo do `<head>`); `GTM_NOSCRIPT` no início de `shell.topbar()` (`<noscript>` logo após `<body>`). Como as 5 páginas concatenam `shell.HEAD`+`shell.topbar()`, cobre todas de uma vez.
2. **`track.js` INLINE** em `shell.TRACK` (anexado a `shell.JS`, fim do `<body>`). **Não** é arquivo separado de propósito: o gate `_ext` reprova `<script src=…>` (mesmo same-origin) — inline passa e mantém o "tudo inline" (invariante #4) para tudo exceto o GTM.
3. **`page_name`** via `<body data-page="…">` nos 5 builders (index/dashboard/resultados/bolao/comparativo). O `track.js` cai em `index` se faltar.
4. **`data-scene`** nas seções (habilita `fdj_section_view`):
   - **dashboard:** `calculadora` (h2#calc), `matriz` (h2#matriz), `metodologia` (h2#meta).
   - **resultados:** `classificacao` (div.sec "Classificação por grupo"), `chave` (div.sec "Mata-mata · chave").
   - bolão/comparativo são curtos — `page_engaged` + `scroll_depth` cobrem (sem seção).
   - ⚠️ São headings/labels planos (sem wrapper) — `dwell_time_seconds` é proxy aproximado da visibilidade do heading; `section_id` registra com confiança QUAIS seções foram alcançadas.
5. **artifact (light) + generico:** GTM removido na build dessas variantes (`build_dashboard.py` na variante light, `make_generic.py` no generico). Continuam zero-dep.

> Demais hooks do `track.js` já casam com o DOM atual (calc `#ca/#cb/#cm`, matriz `#q/#fg/#ft/#sortk`, dossiês `onclick=openDrawer` via `dossie.tlink`, acordeões `details.acc/.more/.gl`, abas `.tabs a`, cards `a.card`, licença CC) — sem mudança extra de HTML.

---

## 5 · Wiring no GTM (forwarding) — 6 eventos = 6 pares trigger+tag

Um `dataLayer.push` **não** vira dado no GA4 sozinho. Para **cada** evento: DLVs dos params + 1 **Custom Event trigger** + 1 **tag GA4 Event** (params → `{{dlv - <param>}}`). Workspace **novo** (`ficha-do-jogo-v1.0`), 1 **folder** "Ficha do Jogo".

| Evento (dataLayer) | Trigger (Custom Event) | Tag (GA4 Event) |
|---|---|---|
| `fdj_page_engaged` | `CE - fdj_page_engaged` | `GA4 - fdj_page_engaged` |
| `fdj_scroll_depth` | `CE - fdj_scroll_depth` | `GA4 - fdj_scroll_depth` |
| `fdj_section_view` | `CE - fdj_section_view` | `GA4 - fdj_section_view` |
| `fdj_interaction` | `CE - fdj_interaction` | `GA4 - fdj_interaction` |
| `fdj_outbound` | `CE - fdj_outbound` | `GA4 - fdj_outbound` |
| `fdj_nav_select` | `CE - fdj_nav_select` | `GA4 - fdj_nav_select` |

**DLVs (11)** — *Data Layer Variable Name* = nome EXATO do param (nomear `dlv - <param>`): `page_section`, `page_name`, `section_id`, `interaction_type`, `target`, `scene`, `context`, `engaged_seconds`, `depth_percent`, `dwell_time_seconds`, `interaction_value`.

Em cada **tag GA4 Event**: *Measurement ID* = `G-X6GGP30QVK` (ou uma Config tag), *Event Name* = o nome do evento (case-sensitive, igual ao push), **Event Parameters** = os params daquele evento → DLVs, *Triggering* = o `CE - <evento>`. (Ver `references/gtm-wiring.md` da skill p/ o passo-a-passo e a opção **Importar via JSON**.)

> **Sem evento compartilhado** com outro site do Bera hoje → **nenhuma Exception** (gotcha #2 não se aplica). `page_section='ficha_do_jogo'` já isola.

---

## 6 · Schema-validation — prove a cobertura ANTES de subir

Cada (evento × param) com o caminho origem → DLV → trigger → tag → GA4 def. Origem = `shell.TRACK` (track.js inline).

| Event | Param | Tipo | Origem | DLV | Trigger | Tag | GA4 def |
|---|---|---|---|---|---|---|---|
| `fdj_page_engaged` | `engaged_seconds` | number | track §1 | `dlv - engaged_seconds` | `CE - fdj_page_engaged` | `GA4 - fdj_page_engaged` | **métrica** (Padrão) |
| `fdj_scroll_depth` | `depth_percent` | number | track §2 | `dlv - depth_percent` | `CE - fdj_scroll_depth` | `GA4 - fdj_scroll_depth` | **métrica** (Padrão) |
| `fdj_section_view` | `section_id` | string | track §3 | `dlv - section_id` | `CE - fdj_section_view` | `GA4 - fdj_section_view` | **dimensão** |
| `fdj_section_view` | `dwell_time_seconds` | number | track §3 | `dlv - dwell_time_seconds` | `CE - fdj_section_view` | `GA4 - fdj_section_view` | **métrica** (Segundos) |
| `fdj_interaction` | `interaction_type` | string | track §4 | `dlv - interaction_type` | `CE - fdj_interaction` | `GA4 - fdj_interaction` | **dimensão** |
| `fdj_interaction` | `target` | string | track §4 | `dlv - target` | `CE - fdj_interaction` | `GA4 - fdj_interaction` | **dimensão** |
| `fdj_interaction` | `interaction_value` | number | track §4b | `dlv - interaction_value` | `CE - fdj_interaction` | `GA4 - fdj_interaction` | **métrica** (Padrão) |
| `fdj_interaction` | `scene` | string | track §4 | `dlv - scene` | `CE - fdj_interaction` | `GA4 - fdj_interaction` | **dimensão** |
| `fdj_outbound` | `target` | string | track §6 | `dlv - target` | `CE - fdj_outbound` | `GA4 - fdj_outbound` | **dimensão** (reusa) |
| `fdj_outbound` | `context` | string | track §6 | `dlv - context` | `CE - fdj_outbound` | `GA4 - fdj_outbound` | **dimensão** |
| `fdj_nav_select` | `target` | string | track §5 | `dlv - target` | `CE - fdj_nav_select` | `GA4 - fdj_nav_select` | **dimensão** (reusa) |
| `fdj_nav_select` | `context` | string | track §5 | `dlv - context` | `CE - fdj_nav_select` | `GA4 - fdj_nav_select` | **dimensão** (reusa) |
| *(defaults)* | `page_section` | string | track DEFAULTS | `dlv - page_section` | (todos) | (todas) | **dimensão** |
| *(defaults)* | `page_name` | string | track DEFAULTS | `dlv - page_name` | (todos) | (todas) | **dimensão** |
| *(defaults)* | `page_version` | string | track DEFAULTS | — | — | — | **sent-only** |

Inventário esperado: **11 DLVs · 6 triggers · 6 tags · 1 folder** · 7 dims + 4 métricas no GA4. Qualquer ❌ = gap antes de importar/publicar.

---

## 7 · Validação (24–48h)

- [ ] **Tempo real → Eventos** (navegando em prod): `fdj_*` aparecem. `fdj_scroll_depth`/`fdj_section_view` dependem de scroll/IntersectionObserver — **não auto-disparam em headless**; teste em browser real com Tag Assistant.
- [ ] **DebugView** (Tag Assistant): params com **valores**, não `(not set)`. Conferir que `page_name` muda entre as 5 páginas e que a busca da matriz manda `interaction_value=1` **sem** o termo.
- [ ] **Explorar → Formato livre** (24–48h): `fdj_interaction` × `interaction_type`; `fdj_page_engaged` × `page_name` (dashboard vs resto); `fdj_nav_select` × `target` (quem vai pro bolão). `(not set)` em tudo → Parâmetro do evento errado (§1, erro #1).

---

## Checklist final

- [ ] §0: property GA4 + container GTM dedicados confirmados; IDs reais (`G-X6GGP30QVK` / `GTM-K524DJN7`)
- [ ] Pré-flight < 41 dims e < 41 métricas
- [ ] **7** dimensões + **4** métricas criadas (escopo Evento, parâmetro exato; `dwell_time_seconds` = Segundos)
- [ ] Código aplicado em `shell.py` + builders + companions (gate, build_dashboard light, make_generic) — build Python regerado
- [ ] GTM: 11 DLVs + 6 triggers + 6 tags + 1 folder em workspace novo; QA em Preview (Fired + params com valor)
- [ ] Schema-validation (tabela §6) sem ❌
- [ ] **[NO deploy]** `./atualizar.sh` passa (gate verde) → subir → Preview do GTM apontado p/ prod (armado, draft)
- [ ] **[PÓS-deploy]** publish do GTM (versão nomeada) → disparar ≥1 de cada evento em prod → marcar **3** eventos principais ⭐
- [ ] (24–48h) dimensões populando, sem `(not set)`
- [ ] Conferir: `copa2026_artifact.html` e `…_generico.html` saíram **sem** `googletagmanager` (grep limpo)
