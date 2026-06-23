// Infra de rota (Cloudflare Worker): serve bera.ia.br/ficha-do-jogo/* a partir dos
// assets estáticos em ./dist, removendo o prefixo /ficha-do-jogo do caminho.
// As páginas continuam 100% estáticas/zero-dep; este Worker é só o roteador da subpasta.
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    let p = url.pathname.replace(/^\/ficha-do-jogo/, "");
    if (p === "" || p.endsWith("/")) p += "index.html"; // raiz/diretório -> index
    url.pathname = p;
    return env.ASSETS.fetch(new Request(url, request));
  },
};
