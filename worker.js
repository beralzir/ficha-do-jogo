// Infra de rota (Cloudflare Worker): serve bera.ia.br/ficha-do-jogo/* a partir dos
// assets estáticos em ./dist. Responsabilidades:
//  1) tira o prefixo /ficha-do-jogo do caminho;
//  2) URLs LIMPAS: /dashboard -> copa2026_dashboard.html, /placares -> copa2026_bolao.html, etc.;
//  3) 301 dos .html legados (e do antigo /comparativo) -> slug limpo (canônico, sem conteúdo duplicado);
//  4) security headers + CSP (libera GTM/GA4; mantém inline — invariante zero-dep/estático-primeiro);
//  5) Cache-Control por tipo (HTML revalida; ícones/og em cache).
// As páginas seguem 100% estáticas/zero-dep; este Worker é só o roteador + cabeçalhos da subpasta.

const BASE = "/ficha-do-jogo";

// slug limpo -> arquivo real em ./dist (placares aponta p/ bolao; page_name do GA4 segue 'bolao').
const SLUG = {
  "dashboard": "copa2026_dashboard.html",
  "resultados": "copa2026_resultados.html",
  "placares": "copa2026_bolao.html",
  "modelos": "copa2026_modelos.html",
};
// arquivo .html antigo (ou stub comparativo) -> slug limpo, para 301.
const LEGACY = {
  "copa2026_dashboard.html": "dashboard",
  "copa2026_resultados.html": "resultados",
  "copa2026_bolao.html": "placares",
  "copa2026_modelos.html": "modelos",
  "copa2026_comparativo.html": "placares",
  "index.html": "",
};

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
  h.set("X-Content-Type-Options", "nosniff");
  h.set("Referrer-Policy", "strict-origin-when-cross-origin");
  h.set("Permissions-Policy", "geolocation=(), microphone=(), camera=(), browsing-topics=()");
  h.set("Strict-Transport-Security", "max-age=31536000"); // sem preload/includeSubDomains (seguro/reversível)
  if (file.endsWith(".html")) {
    h.set("Content-Security-Policy", CSP);
    h.set("Cache-Control", "no-cache"); // HTML muda a cada update do cron — revalida SEMPRE (sem 'public', o edge não serve HTML stale)
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

    const seg = rel.replace(/^\/+/, "").replace(/\/+$/, ""); // sem barras nas pontas

    // 301 dos .html legados -> slug limpo
    if (Object.prototype.hasOwnProperty.call(LEGACY, seg)) {
      return redirect(url.origin + BASE + "/" + LEGACY[seg], 301);
    }

    // resolve o arquivo a servir
    let file;
    if (seg === "") file = "index.html";          // raiz/diretório
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
