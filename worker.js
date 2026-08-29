// Infra de rota (Cloudflare Worker): serve bera.ia.br/ficha-do-jogo/* a partir dos
// assets estáticos em ./dist. Responsabilidades:
//  1) tira o prefixo /ficha-do-jogo do caminho;
//  2) URLs LIMPAS: /dashboard -> copa2026_dashboard.html, /placares -> copa2026_bolao.html, etc.;
//  3) 301 dos .html legados (e do antigo /comparativo) -> slug limpo (canônico, sem conteúdo duplicado);
//  4) security headers + CSP (libera GTM/GA4; mantém inline — invariante zero-dep/estático-primeiro);
//  5) Cache-Control por tipo (HTML revalida; ícones/og em cache).
// As páginas seguem 100% estáticas/zero-dep; este Worker é só o roteador + cabeçalhos da subpasta.

const BASE = "/ficha-do-jogo";

// slug limpo -> arquivo real em ./dist. EDIÇÃO ATUAL NA RAIZ = Eleições 2026 (virada da B7);
// a Copa vive congelada em /copa2026/* e os slugs antigos da raiz dão 301 pro arquivo.
const SLUG = {
  "presidencial": "eleicoes_dashboard.html",
  "modelos": "eleicoes_modelos.html",
  "uf-ac": "eleicoes_uf_ac.html", "uf-al": "eleicoes_uf_al.html", "uf-am": "eleicoes_uf_am.html",
  "uf-ap": "eleicoes_uf_ap.html", "uf-ba": "eleicoes_uf_ba.html", "uf-ce": "eleicoes_uf_ce.html",
  "uf-df": "eleicoes_uf_df.html", "uf-es": "eleicoes_uf_es.html", "uf-go": "eleicoes_uf_go.html",
  "uf-ma": "eleicoes_uf_ma.html", "uf-mg": "eleicoes_uf_mg.html", "uf-ms": "eleicoes_uf_ms.html",
  "uf-mt": "eleicoes_uf_mt.html", "uf-pa": "eleicoes_uf_pa.html", "uf-pb": "eleicoes_uf_pb.html",
  "uf-pe": "eleicoes_uf_pe.html", "uf-pi": "eleicoes_uf_pi.html", "uf-pr": "eleicoes_uf_pr.html",
  "uf-rj": "eleicoes_uf_rj.html", "uf-rn": "eleicoes_uf_rn.html", "uf-ro": "eleicoes_uf_ro.html",
  "uf-rr": "eleicoes_uf_rr.html", "uf-rs": "eleicoes_uf_rs.html", "uf-sc": "eleicoes_uf_sc.html",
  "uf-se": "eleicoes_uf_se.html", "uf-sp": "eleicoes_uf_sp.html", "uf-to": "eleicoes_uf_to.html",
};
// slugs da Copa que moravam na raiz: 301 direto para o arquivo congelado.
// (/modelos NÃO redireciona: a seção Modelos agora é da edição Eleições; a da Copa
//  segue em /copa2026/modelos.)
const COPA_301 = {
  "dashboard": "dashboard",
  "resultados": "resultados",
  "placares": "placares",
  "bolao": "placares",
  "comparativo": "placares",
};
// slugs do arquivo /copa2026: os mesmos da edição + a retrospectiva (só existe no arquivo).
const ARQ_SLUG = {
  "dashboard": "copa2026_dashboard.html",
  "resultados": "copa2026_resultados.html",
  "placares": "copa2026_bolao.html",
  "modelos": "copa2026_modelos.html",
  "retrospectiva": "retrospectiva.html",
};
// arquivo .html antigo (ou stub comparativo) -> slug limpo, para 301.
// Após a virada, os .html da Copa na raiz apontam pro ARQUIVO; os da edição
// Eleições apontam pro slug limpo da raiz.
const LEGACY = {
  "copa2026_dashboard.html": "copa2026/dashboard",
  "copa2026_resultados.html": "copa2026/resultados",
  "copa2026_bolao.html": "copa2026/placares",
  "copa2026_modelos.html": "copa2026/modelos",
  "copa2026_comparativo.html": "copa2026/placares",
  "eleicoes_index.html": "",
  "eleicoes_dashboard.html": "presidencial",
  "eleicoes_modelos.html": "modelos",
  "index.html": "",
};
// eleicoes_uf_xx.html -> uf-xx (gerado, mesmo padrão)
for (const s of Object.keys(SLUG)) {
  if (s.startsWith("uf-")) LEGACY[SLUG[s]] = s;
}

// CSP: 'self' + GTM/GA4 + inline (theme pre-paint, GTM bootstrap, track.js inline, onclick=).
const CSP = [
  "default-src 'self'",
  "base-uri 'self'",
  "object-src 'none'",
  "form-action 'self'",
  "frame-ancestors 'self'",
  "script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com",
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data: https://www.googletagmanager.com https://www.google-analytics.com https://*.google-analytics.com",
  "font-src 'self'",
  "connect-src 'self' https://www.google-analytics.com https://*.google-analytics.com https://*.analytics.google.com https://www.googletagmanager.com",
  "frame-src https://www.googletagmanager.com",
].join("; ");

function redirect(to, status) {
  return new Response(null, { status: status || 301, headers: { Location: to } });
}

function withHeaders(resp, file) {
  const h = new Headers(resp.headers);
  const frozen = file.startsWith("copa2026/"); // arquivo histórico: conteúdo congelado
  h.set("X-Content-Type-Options", "nosniff");
  h.set("Referrer-Policy", "strict-origin-when-cross-origin");
  h.set("Permissions-Policy", "geolocation=(), microphone=(), camera=(), browsing-topics=()");
  h.set("Strict-Transport-Security", "max-age=31536000"); // sem preload/includeSubDomains (seguro/reversível)
  if (file.endsWith(".html") && frozen) {
    // Edição arquivada não muda: pode cachear (1h dá folga p/ correção rara no snapshot).
    h.set("Content-Security-Policy", CSP);
    h.set("Cache-Control", "public, max-age=3600");
    return new Response(resp.body, { status: resp.status, statusText: resp.statusText, headers: h });
  }
  if (file.endsWith(".html")) {
    h.set("Content-Security-Policy", CSP);
    // HTML muda a cada update do cron. 'no-store' impede o navegador de GUARDAR/reusar o
    // documento; 'no-cache' (antigo) só exigia revalidação e o browser ainda reusava a cópia
    // ao navegar dentro do site (exigia shift-reload p/ ver a versão nova). Remover ETag/
    // Last-Modified evita um 304 condicional contra a cópia velha. Assets seguem cacheáveis.
    h.set("Cache-Control", "no-store");
    h.delete("ETag");
    h.delete("Last-Modified");
  } else {
    h.set("Cache-Control", "public, max-age=86400"); // ícones / og-cover
  }
  return new Response(resp.body, { status: resp.status, statusText: resp.statusText, headers: h });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const rel = url.pathname.startsWith(BASE) ? url.pathname.slice(BASE.length) : url.pathname;

    // /ficha-do-jogo (sem barra) -> /ficha-do-jogo/
    if (rel === "") return redirect(url.origin + BASE + "/", 301);
    // /copa2026 (sem barra) -> /copa2026/ (páginas do arquivo usam links relativos)
    if (rel === "/copa2026") return redirect(url.origin + BASE + "/copa2026/", 301);

    const seg = rel.replace(/^\/+/, "").replace(/\/+$/, ""); // sem barras nas pontas

    // ── Arquivo congelado da edição Copa 2026 (dist/copa2026/), mesmos slugs limpos ──
    if (seg === "copa2026" || seg.startsWith("copa2026/")) {
      const sub = seg === "copa2026" ? "" : seg.slice("copa2026/".length);
      if (Object.prototype.hasOwnProperty.call(LEGACY, sub)) {
        return redirect(url.origin + BASE + "/copa2026/" + LEGACY[sub], 301);
      }
      let afile;
      if (sub === "") afile = "copa2026/index.html";
      else if (ARQ_SLUG[sub]) afile = "copa2026/" + ARQ_SLUG[sub];
      else afile = "copa2026/" + sub;             // asset local do arquivo (favicon, og-cover…)
      url.pathname = "/" + afile;
      let aresp = await env.ASSETS.fetch(new Request(url, request));
      if (aresp.status === 404 && afile !== "404.html") {
        const u404 = new URL(url); u404.pathname = "/404.html";
        const r404 = await env.ASSETS.fetch(new Request(u404, request));
        if (r404.status === 200) {
          return withHeaders(new Response(r404.body, { status: 404, headers: r404.headers }), "404.html");
        }
      }
      return withHeaders(aresp, afile);
    }

    // slugs da Copa que moravam na raiz -> 301 pro arquivo congelado
    if (Object.prototype.hasOwnProperty.call(COPA_301, seg)) {
      return redirect(url.origin + BASE + "/copa2026/" + COPA_301[seg], 301);
    }

    // 301 dos .html legados -> destino canônico
    if (Object.prototype.hasOwnProperty.call(LEGACY, seg)) {
      return redirect(url.origin + BASE + "/" + LEGACY[seg], 301);
    }

    // resolve o arquivo a servir
    let file;
    if (seg === "") file = "eleicoes_index.html"; // raiz = edição atual (Eleições 2026)
    else if (SLUG[seg]) file = SLUG[seg];          // slug limpo -> arquivo
    else file = seg;                               // asset (favicon.svg, apple-touch-icon.png, og-cover.png)

    url.pathname = "/" + file;
    let resp = await env.ASSETS.fetch(new Request(url, request));

    // 404 amigável (se existir um 404.html servido pelos assets)
    if (resp.status === 404 && file !== "404.html") {
      const u404 = new URL(url); u404.pathname = "/404.html";
      const r404 = await env.ASSETS.fetch(new Request(u404, request));
      if (r404.status === 200) {
        return withHeaders(new Response(r404.body, { status: 404, headers: r404.headers }), "404.html");
      }
    }
    return withHeaders(resp, file);
  },
};
