#!/usr/bin/env python3
"""Shell compartilhado do "Ficha do Jogo" — marca/header, nav em 3 níveis, toggle de tema e
acordeão (disclosure padrão). Fonte única do "cromo" de navegação das 5 páginas (Fase 3 do redesign).

Decisões aplicadas:
- #6 marca: wordmark "Ficha do Jogo" + ícone (radar de atributos, SVG inline theme-adaptável).
- #4 nav em 3 níveis VISUALMENTE distintos: aba sublinhada (muda de página) · âncora com ↓ (mesma
  página) · selo "chato" sem hover (metadado do modelo, NÃO-clicável).
- #3 toggle de tema: micro-JS inline (localStorage, auto/escuro/claro), pré-paint no <head> (sem flash);
  com JS off a página renderiza normal e cai no tema do SO.
- #2 disclosure: acordeão único (.acc) — barra inteira clicável, chevron que gira, dica "abrir".

ZERO dependência externa: logo e favicon são SVG inline; nada de CDN/fonte/lib.
Tokens canônicos (precisam existir nas DUAS paletas — theme.PALETTE e a do dashboard):
  --bg --card --line --ink --mut --ac --box --acsoft --rowhov --logo-frame --logo-bar
Cada página pode definir --maxw (largura do conteúdo) p/ alinhar a barra; default 1100px.
"""
import json

import flags  # set de bandeiras SVG (sprite + CSS .fi); flags.CSS é anexado ao CSS do shell abaixo

# Marca (radar de atributos): moldura = --logo-frame (cromo) · radar de stats = --logo-bar (dado).
LOGO = ('<svg class="bi" viewBox="0 0 32 32" width="27" height="27" aria-hidden="true">'
        '<polygon points="16,3.5 5.18,9.75 5.18,22.25 16,28.5 26.82,22.25 26.82,9.75" fill="none" stroke="var(--logo-frame)" stroke-width="2" stroke-linejoin="round"/>'
        '<polygon points="16,5 10.59,12.88 8.21,20.5 16,23.25 24.88,21.13 22.71,12.13" fill="var(--logo-bar)" fill-opacity=".15" stroke="var(--logo-bar)" stroke-width="1.2" stroke-linejoin="round"/>'
        '<circle cx="16" cy="16" r=".9" fill="var(--logo-frame)"/></svg>')

# Favicon = a marca (radar). CORES FIXAS: var()/@media NÃO renderizam em favicon de aba (ficava em branco).
# Servido como ARQUIVO dist/favicon.svg (mais confiável que data-URI) — escrito por build_index.py.
FAVICON_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
               '<polygon points="16,3 4.65,9.5 4.65,22.5 16,29 27.35,22.5 27.35,9.5" fill="none" stroke="#f3b03c" stroke-width="2.6" stroke-linejoin="round"/>'
               '<polygon points="16,5 10.2,12.9 7.7,20.8 16,23.7 25.4,21.4 23.1,12.1" fill="#22c55e" fill-opacity=".92" stroke="#22c55e" stroke-width="1.4" stroke-linejoin="round"/></svg>')
FAVICON = '<link rel="icon" type="image/svg+xml" href="favicon.svg">'
# Ícone do atalho na tela de início (iOS/Android). Sem ele o iOS desenha a inicial do título.
APPLE_ICON = '<link rel="apple-touch-icon" href="apple-touch-icon.png">'

# Crédito + licença (#1), em todos os footers. O link CC é um <a href> externo (hyperlink) — NÃO é
# dependência carregada (nada de CDN/fonte/lib); é a única ocorrência http(s) esperada nas páginas.
CREDIT = ('© 2026 Renato Beralzir · '
          '<a href="https://creativecommons.org/licenses/by-nc-nd/4.0/" rel="license noopener" target="_blank">CC BY-NC-ND 4.0</a>')

# ── Web analytics (GA4 via GTM) — nas páginas live da edição + santinho; ver docs/ga4-setup.md ──
# GTM carrega googletagmanager.com = a ÚNICA dependência externa do site (o gate zero-dep
# do atualizar_eleicoes.sh libera só esse host). artifact (light) e generico (white-label) da
# Copa saem SEM o snippet, removido na build dessas variantes via shell.GTM_HEAD/GTM_NOSCRIPT.
GTM_ID = "GTM-K524DJN7"
GA4_ID = "G-X6GGP30QVK"  # só referência (ga-disable da página /privacidade): o GA4 mora nas tags do GTM
# LGPD (04/10/2026): "não medir neste navegador", explicado em /privacidade. A escolha fica no
# localStorage; com ela o GTM nem carrega e o track() não empurra nada.
OPTOUT_KEY = "fdj-nao-medir"
PRIVACIDADE = '<a href="./privacidade">Privacidade</a>'  # link de rodapé (todas as páginas da edição)
GTM_HEAD = ('<!-- Google Tag Manager -->'
            "<script>(function(w,d,s,l,i){try{if(w.localStorage.getItem('" + OPTOUT_KEY + "')==='1')return}catch(e){}"
            "w[l]=w[l]||[];w[l].push({'gtm.start':"
            "new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],"
            "j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src="
            "'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);"
            "})(window,document,'script','dataLayer','" + GTM_ID + "');</script>"
            '<!-- End Google Tag Manager -->')
GTM_NOSCRIPT = ('<!-- Google Tag Manager (noscript) -->'
                '<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=' + GTM_ID + '"'
                ' height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>'
                '<!-- End Google Tag Manager (noscript) -->')

# Escudo de saída (LGPD, 04/10/2026). Vai no <head> ANTES do GTM e escuta na fase de captura da janela,
# então roda antes de qualquer ouvinte que o GTM/gtag instale. Clique em link EXTERNO para ali: o nosso
# fdj_outbound registra só o host (window.fdjOut, em TRACK) e mais ninguém vê o clique. Isso inclui o
# "clique de saída" automático da medição otimizada do GA4, que mandaria a URL completa (no link do TSE,
# com o sq do candidato) e que não depende do painel: vale mesmo se a opção for religada. O link abre
# normalmente (o padrão do navegador não é cancelado, só a propagação do evento). auxclick = botão do meio.
OUT_GUARD = ("<script>(function(){function g(e){var t=e.target,a=t&&t.closest?t.closest('a[href]'):null;"
             "if(!a||!/^https?:/i.test(a.getAttribute('href')||'')||a.host===location.host)return;"
             "e.stopImmediatePropagation();"
             "if((e.type==='click'||e.button===1)&&window.fdjOut){try{window.fdjOut(a)}catch(_){}}}"
             "addEventListener('click',g,true);addEventListener('auxclick',g,true)})()</script>")

# Instrumentação (track.js) INLINE — anexada a JS (fim do <body>, depois do GTM). Inline de
# propósito: o gate _ext reprova <script src=…> (mesmo same-origin). Um único track serve todas
# as páginas (cada uma marca seu page_name via <body data-page> e suas seções via data-scene).
# PRIVACIDADE (regra do Bera, 04/10/2026, LGPD): o site mede só NAVEGAÇÃO. Nenhum parâmetro
# carrega candidato (nome, número, sq), texto digitado, valor de filtro, escolha do eleitor ou
# URL de destino completa: só ids curados do próprio site. test_tagueamento.py guarda a regra.
# page_name de destino por slug (fdj_nav_select.target): espelha o SLUG do worker.js e o
# <body data-page> de cada builder (uf-xx -> eleicoes_uf, publico-* -> o próprio slug, no JS).
NAV_PAGE = {"": "eleicoes_index", "presidencial": "eleicoes_dashboard", "inflexoes": "eleicoes_inflexoes",
            "modelos": "eleicoes_modelos", "publicos": "publicos", "santinho": "santinho",
            "privacidade": "privacidade"}
TRACK = r'''<script>
(function () {
  'use strict';
  var DEFAULTS = {
    page_section: 'ficha_do_jogo',
    page_name: (document.body && document.body.dataset.page) || 'index',
    page_version: 'v2.0'
  };
  var PREFIX = 'fdj_';
  window.dataLayer = window.dataLayer || [];
  function track(event, params) {
    try { if (localStorage.getItem('__OPTOUT__') === '1') return; } catch (e) {}  // "nao medir" (/privacidade)
    var p = {}; p.event = PREFIX + event;
    for (var k in DEFAULTS) p[k] = DEFAULTS[k];
    if (params) for (var j in params) p[j] = params[j];
    window.dataLayer.push(p);
  }
  // paginas com JS proprio (santinho) empurram pelo mesmo wrapper (mesmos defaults)
  window.fdjTrack = track;

  // 1) fdj_page_engaged — 1x apos 10s de atencao ATIVA (aba visivel). "Leu" vs "abriu e saiu".
  var ENGAGE_MS = 10000, activeMs = 0, lastTick = Date.now(), engagedFired = false;
  function _accumulate() {
    if (document.visibilityState === 'visible') activeMs += Date.now() - lastTick;
    lastTick = Date.now();
    if (!engagedFired && activeMs >= ENGAGE_MS) {
      engagedFired = true;
      track('page_engaged', { engaged_seconds: Math.round(activeMs / 1000) });
    }
  }
  setInterval(_accumulate, 1000);
  document.addEventListener('visibilitychange', function () { lastTick = Date.now(); });

  // 2) fdj_scroll_depth — marcos 25/50/75/100 (nao auto-dispara em headless).
  var _lastDepth = 0;
  function _onScroll() {
    var h = document.body.scrollHeight - window.innerHeight;
    if (h <= 0) return;
    var pct = Math.round((window.scrollY / h) * 100);
    [25, 50, 75, 100].forEach(function (m) {
      if (pct >= m && _lastDepth < m) { _lastDepth = m; track('scroll_depth', { depth_percent: m }); }
    });
  }
  addEventListener('scroll', function () { requestAnimationFrame(_onScroll); }, { passive: true });

  // 3) fdj_section_view — IntersectionObserver nas secoes [data-scene] (nao auto-dispara em headless).
  if ('IntersectionObserver' in window) {
    var _io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var id = e.target.dataset.scene;
        if (e.isIntersecting) { e.target._enter = Date.now(); }
        else if (e.target._enter) {
          track('section_view', { section_id: id, dwell_time_seconds: Math.round((Date.now() - e.target._enter) / 1000) });
          e.target._enter = 0;
        }
      });
    }, { threshold: 0.5 });
    document.querySelectorAll('[data-scene]').forEach(function (el) { _io.observe(el); });
  }

  // 4) fdj_interaction: so leitura de conteudo da propria pagina, com rotulo curado.
  // Acordeoes: so a ABERTURA. target = titulo curado (.attl, sem a dica "abrir"), truncado a 60.
  document.querySelectorAll('details.acc, details.more, details.gl').forEach(function (d) {
    d.addEventListener('toggle', function () {
      if (!d.open) return;
      var sum = d.querySelector('summary'), t = sum && (sum.querySelector('.attl') || sum);
      var label = t ? (t.textContent || '').trim().slice(0, 60) : 'detalhe';
      track('interaction', { interaction_type: 'accordion_open', target: label, scene: DEFAULTS.page_name });
    });
  });
  // Ancoras "nesta pagina" (.anchors a[href^="#"]).
  document.querySelectorAll('.anchors a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function () {
      track('interaction', { interaction_type: 'anchor_jump', target: a.getAttribute('href').slice(1), scene: DEFAULTS.page_name });
    });
  });

  // 6) fdj_outbound: chamado pelo escudo de saida (shell.OUT_GUARD, no <head>), que segura o clique
  // em link externo antes de qualquer outro ouvinte. So o HOST: a URL do TSE leva o sq do candidato.
  window.fdjOut = function (a) {
    track('outbound', { target: a.hostname, context: a.dataset.context || (/\blicense\b/.test(a.rel) ? 'footer_license' : 'inline') });
  };

  // 5) fdj_nav_select (link interno): listener delegado, que cobre tambem o conteudo montado por JS.
  // target = page_name de destino. Link externo nao chega aqui (o escudo para a propagacao).
  var PAGE_OF = __NAV_PAGE__;
  function _pageOf(href) {
    var seg = (href || '').replace(/[#?].*$/, '').replace(/\/+$/, '').split('/').pop();
    if (seg === '.' || seg === 'index.html') seg = '';
    if (Object.prototype.hasOwnProperty.call(PAGE_OF, seg)) return PAGE_OF[seg];
    if (/^uf-[a-z]{2}$/.test(seg)) return 'eleicoes_uf';
    if (/^publico-[a-z-]+$/.test(seg)) return seg;
    return 'unknown';
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest ? e.target.closest('a[href]') : null;
    if (!a) return;
    var href = a.getAttribute('href');
    if (/^https?:/i.test(href) || href.charAt(0) === '#') return;  // externo (escudo) e ancora/skip-link
    var ctx = a.closest('.tabs') ? 'topbar_tab' : a.classList.contains('brand') ? 'brand'
            : /\b(card|ficha|fichon|carta)\b/.test(a.className) ? 'card' : 'inline';
    track('nav_select', { target: _pageOf(href), context: ctx });
  });
})();
</script>'''.replace("__NAV_PAGE__", json.dumps(NAV_PAGE, sort_keys=True)).replace("__OPTOUT__", OPTOUT_KEY)

# Vai no <head> ANTES do CSS: aplica o tema salvo sem flash (FOUC). PADRÃO = ESCURO (não segue o SO);
# só vira claro se o usuário tiver escolhido. Com JS off, fica no escuro padrão. (GTM async vem antes.)
HEAD = (OUT_GUARD + GTM_HEAD + FAVICON + APPLE_ICON +
        '<script>(function(){try{if(localStorage.getItem("fdj-theme")==="light")'
        'document.documentElement.setAttribute("data-theme","light")}catch(e){}})()</script>')

SITE_URL = "https://bera.ia.br/ficha-do-jogo"

_MO_BR = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def _d_br(iso, year=False):
    """'2026-06-29' -> '29/jun' (year=True -> '29/jun/2026'). '' se inválido."""
    if not iso or len(iso) < 10:
        return ""
    return f"{int(iso[8:10]):02d}/{_MO_BR[int(iso[5:7]) - 1]}" + (f"/{iso[:4]}" if year else "")


def updated_line(generated="", as_of="", year=False):
    """Linha de atualização ÚNICA p/ todas as páginas live — resolve a divergência de datas
    (dashboard/index mostravam só meta.generated; placares/resultados só state.as_of, dando
    29/jun vs 28/jun em páginas diferentes). Mostra as DUAS, rotuladas: 'forecast' = data da
    simulação (meta.generated); 'dados até' = último jogo computado (meta.state.as_of). Colapsa
    numa só quando coincidem. Usar o MESMO texto em dashboard/index/placares/resultados."""
    g = _d_br(generated, year)
    a = _d_br(as_of, year)
    if g and a and generated != as_of:
        return f"forecast {g} · dados até {a}"
    return f"atualizado {g or a}" if (g or a) else ""


def meta(title, desc, slug, og="og-cover.png"):
    """Tags de <head> por página: description + canonical + theme-color + Open Graph + Twitter.
    slug='' = raiz. Inserir logo após o {shell.HEAD} de cada página live. canonical/OG são
    same-origin (bera.ia.br), liberados no gate _ext. Manter desc/title method-neutral (o
    generico roda BANNED sobre o HTML)."""
    canon = SITE_URL + ("/" + slug if slug else "/")
    img = SITE_URL + "/" + og
    return ('<meta name="description" content="' + desc + '">'
            '<link rel="canonical" href="' + canon + '">'
            '<meta name="theme-color" content="#0f1b13">'
            '<meta property="og:type" content="website">'
            '<meta property="og:site_name" content="Ficha do Jogo">'
            '<meta property="og:locale" content="pt_BR">'
            '<meta property="og:title" content="' + title + '">'
            '<meta property="og:description" content="' + desc + '">'
            '<meta property="og:url" content="' + canon + '">'
            '<meta property="og:image" content="' + img + '">'
            '<meta name="twitter:card" content="summary_large_image">'
            '<meta name="twitter:title" content="' + title + '">'
            '<meta name="twitter:description" content="' + desc + '">'
            '<meta name="twitter:image" content="' + img + '">')

# Vai no fim do <body>: alterna ESCURO ↔ CLARO (2 estados; sem "auto") e pinta o botão (☾ escuro / ☀ claro).
JS = ('<script>function curTheme(){return document.documentElement.getAttribute("data-theme")==="light"?"light":"dark"}'
      'function cycleTheme(){var r=document.documentElement;'
      'if(curTheme()==="light"){r.removeAttribute("data-theme");try{localStorage.setItem("fdj-theme","dark")}catch(e){}}'
      'else{r.setAttribute("data-theme","light");try{localStorage.setItem("fdj-theme","light")}catch(e){}}paintTg()}'
      'function paintTg(){var e=document.getElementById("tg");if(!e)return;var l=curTheme()==="light";'
      'e.textContent=l?"☀":"☾";e.title=(l?"Tema claro":"Tema escuro")+" · clique para alternar"}paintTg();'
      # gestão de foco da gaveta (dossiê) — compartilhada por dossie.js e pelo dashboard (modal acessível)
      'var _fdjRet=null,_fdjTrap=null;'
      'function _fdjFoc(c){return [].slice.call(c.querySelectorAll(\'a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])\')).filter(function(el){return el.offsetParent!==null})}'
      'function _fdjOnKey(e){if(e.key!=="Tab"||!_fdjTrap)return;var f=_fdjFoc(_fdjTrap);if(!f.length)return;var a=f[0],b=f[f.length-1];if(e.shiftKey&&document.activeElement===a){e.preventDefault();b.focus()}else if(!e.shiftKey&&document.activeElement===b){e.preventDefault();a.focus()}}'
      'window.fdjDrawerOpen=function(el){if(!el)return;_fdjRet=document.activeElement;_fdjTrap=el;var f=_fdjFoc(el);(f[0]||el).focus();document.addEventListener("keydown",_fdjOnKey,true)};'
      'window.fdjDrawerClose=function(){document.removeEventListener("keydown",_fdjOnKey,true);_fdjTrap=null;if(_fdjRet&&_fdjRet.focus){try{_fdjRet.focus()}catch(e){}}_fdjRet=null};'
      '</script>'
      + TRACK)  # track.js inline (analytics) carrega depois do toggle de tema, no fim do <body>

# href = SLUG limpo (sem .html). O worker.js mapeia o slug -> arquivo e dá 301 nos .html legados.
# 'placares' aponta p/ copa2026_bolao.html; o page_name do GA4 segue 'bolao' (data-page).
PAGES = [("Dashboard", "dashboard", "dash"),
         ("Resultados", "resultados", "res"),
         ("Placares", "placares", "bol"),
         ("Modelos", "modelos", "mod")]


def topbar(active, tabs=True):
    """Barra fixa: marca (link p/ index) + abas de página + toggle. tabs=False na landing."""
    nav = ""
    if tabs:
        links = "".join((f'<a class="on" aria-current="page">{l}</a>' if k == active
                         else f'<a href="./{h}">{l}</a>') for l, h, k in PAGES)
        nav = f'<nav class="tabs" aria-label="Navegação entre páginas">{links}</nav>'
    return (GTM_NOSCRIPT + '<a class="skip" href="#main">Pular para o conteúdo</a>'  # skip-link: 1º foco tabulável
            + '<header class="topbar"><div class="bar">'  # GTM <noscript> logo após <body>
            '<a class="brand" href="./" aria-label="Ficha do Jogo — início">'
            + LOGO + '<span class="nm">Ficha <span>do Jogo</span></span></a>'
            '<span class="sp"></span>'
            '<button class="tg" id="tg" type="button" onclick="cycleTheme()" title="Tema escuro · clique para alternar" aria-label="Alternar tema">☾</button>'
            '</div>' + nav + '</header>')


def accordion(title, body, is_open=False, hint="abrir"):
    """Disclosure padrão (#2): barra inteira clicável, chevron que gira, dica 'abrir'."""
    o = " open" if is_open else ""
    return (f'<details class="acc"{o}><summary><span class="adot"></span>'
            f'<span class="attl">{title}</span><span class="ahint">{hint}</span>'
            f'<span class="achev">▸</span></summary><div class="abd">{body}</div></details>')


# CSS do shell (raw: preserva os escapes \2193 do CSS). Usa só os tokens canônicos.
CSS = r"""
/* ===== shell compartilhado (Ficha do Jogo) ===== */
a{color:var(--ac)}
.topbar{position:sticky;top:0;z-index:40;background:var(--bg);border-bottom:1px solid var(--line)}
.bar{max-width:var(--maxw,1100px);margin:0 auto;padding:10px 16px;display:flex;align-items:center;gap:12px}
.brand{display:flex;align-items:center;gap:9px;text-decoration:none}
.brand .bi{display:block;flex:none}
.brand .nm{font-size:16px;font-weight:800;letter-spacing:-.01em;color:var(--ink)}
.brand .nm span{font-weight:500;color:var(--mut)}
.sp{flex:1}
.tg{width:31px;height:31px;border-radius:50%;border:1px solid var(--line);background:var(--card);color:var(--mut);cursor:pointer;font-size:14px;line-height:1;display:flex;align-items:center;justify-content:center;flex:none;padding:0}
.tg:hover{color:var(--ink);border-color:var(--ac)}
.tabs{max-width:var(--maxw,1100px);margin:0 auto;padding:0 16px;display:flex;gap:2px;overflow-x:auto;scrollbar-width:none}
.tabs::-webkit-scrollbar{display:none}
.tabs a{padding:9px 14px;font-size:13px;font-weight:600;color:var(--mut);border-bottom:2px solid transparent;margin-bottom:-1px;text-decoration:none;white-space:nowrap;cursor:pointer}
.tabs a:hover{color:var(--ink)}
.tabs a.on{color:var(--ink);border-bottom-color:var(--ac);font-weight:700;cursor:default}
/* tira de âncoras (pula na mesma página) — chips com cara de botão/marcador de navegação */
.anchors{display:flex;flex-wrap:wrap;gap:7px;align-items:center}
.anchors .lbl,.tags .lbl{color:var(--mut);font-size:10px;text-transform:uppercase;letter-spacing:.11em;font-weight:800}
.anchors a{display:inline-flex;align-items:center;gap:5px;padding:6px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink);font-size:12.5px;font-weight:600;text-decoration:none;cursor:pointer}
.anchors a::before{content:"\2193";color:var(--ac);font-weight:800;font-size:11px}
.anchors a:hover{border-color:var(--ac);background:var(--rowhov)}
/* selos de metadado do modelo (NÃO-clicáveis) */
.tags{display:flex;flex-wrap:wrap;gap:7px;align-items:center}
.tag{display:inline-flex;gap:6px;align-items:center;background:var(--acsoft);border-radius:5px;padding:3px 9px;font-size:12px;color:var(--mut);cursor:default}
.tag b{color:var(--ink);font-variant-numeric:tabular-nums;font-weight:700}
/* acordeão = disclosure padrão (#2) */
details.acc{background:var(--card);border:1px solid var(--line);border-radius:12px;margin:10px 0;padding:0;overflow:hidden}
details.acc>summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:10px;padding:13px 15px;font-weight:700;font-size:13px;color:var(--ink)}
details.acc>summary::-webkit-details-marker{display:none}
.adot{width:7px;height:7px;border-radius:2px;background:var(--ac);flex:none}
.attl{flex:1}
.ahint{font-size:10px;color:var(--mut);font-weight:600;background:var(--acsoft);padding:2px 8px;border-radius:20px;white-space:nowrap}
.achev{color:var(--ac);transition:transform .2s ease;font-size:11px}
details.acc[open]>summary .achev{transform:rotate(90deg)}
details.acc[open]>summary .ahint{display:none}
details.acc>summary:hover{background:var(--rowhov)}
.abd{padding:2px 15px 15px;font-size:13px;color:var(--mut);line-height:1.55}
"""
CSS += "\n" + flags.CSS  # chip de bandeira (.fi) compartilhado por todas as páginas
CSS += r"""
/* ===== acessibilidade: skip-link · foco visível · movimento reduzido ===== */
.skip{position:absolute;left:8px;top:-48px;z-index:60;background:var(--card);color:var(--ink);border:1px solid var(--ac);border-radius:8px;padding:8px 14px;font-size:13px;font-weight:700;text-decoration:none}
.skip:focus{top:8px}
:focus-visible{outline:2px solid var(--ac);outline-offset:2px}
main:focus{outline:none}
@media (prefers-reduced-motion: reduce){
  *,*::before,*::after{animation-duration:.001ms!important;animation-iteration-count:1!important;transition-duration:.001ms!important;scroll-behavior:auto!important}
}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
@media (pointer:coarse){.tg{width:40px;height:40px}.tabs a{padding-top:12px;padding-bottom:12px}.anchors a{padding-top:9px;padding-bottom:9px}}
"""
