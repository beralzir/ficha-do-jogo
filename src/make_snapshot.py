#!/usr/bin/env python3
"""Congela a edição Copa 2026 em dist/copa2026/ (arquivo histórico: /ficha-do-jogo/copa2026/).

O que faz (determinístico e idempotente; lê de dist/, escreve em dist/copa2026/):
  - copia as 6 páginas + 3 assets;
  - reescreve os URLs absolutos do próprio site (canonical, og:url, og:image) para
    https://bera.ia.br/ficha-do-jogo/copa2026/...;
  - injeta o banner de arquivo logo após <body ...> (inline, zero-dep, cor com fallback);
  - navegação e ícones já funcionam sob /copa2026/ porque os links das páginas são RELATIVOS;
  - verifica zero-dep (mesma regra do gate do atualizar.sh) e a presença do banner.

O snapshot é CONGELADO: não entra no fluxo de build normal. Rode só para (re)gerar o arquivo
da edição (ex.: correção no próprio snapshot). O roteamento fica no worker.js (rotas /copa2026).
"""
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
OUT = os.path.join(DIST, "copa2026")

PAGES = [
    "index.html",
    "copa2026_dashboard.html",
    "copa2026_resultados.html",
    "copa2026_bolao.html",
    "copa2026_modelos.html",
    "copa2026_artifact.html",
    "copa2026_dashboard_generico.html",
]
ASSETS = ["favicon.svg", "apple-touch-icon.png", "og-cover.png"]

SELF = "https://bera.ia.br/ficha-do-jogo/"
SELF_ARQ = "https://bera.ia.br/ficha-do-jogo/copa2026/"

_BANNER_BOX = (
    '<div class="arq-banner" style="background:#0e1626;background:var(--box,#0e1626);'
    'color:#cdd9ea;color:var(--notetx,#cdd9ea);border-bottom:1px solid #1f2a3d;'
    "border-bottom:1px solid var(--line,#1f2a3d);padding:8px 14px;"
    "font:600 12.5px/1.4 -apple-system,system-ui,'Segoe UI',Roboto,sans-serif;text-align:center\">"
)
BANNER = (_BANNER_BOX + '🗄️ Arquivo · edição <b>Copa do Mundo 2026</b>, congelada em 20/07/2026 · '
          '<a href="retrospectiva" style="color:#38bdf8;color:var(--ac,#38bdf8)">retrospectiva</a> · '
          '<a href="../" style="color:#38bdf8;color:var(--ac,#38bdf8)">edição atual da Ficha do Jogo</a></div>')
# white-label não ganha marca nem link de volta: banner neutro.
BANNER_NEUTRO = _BANNER_BOX + '🗄️ Arquivo · edição Copa do Mundo 2026, congelada em 20/07/2026</div>'


def _ext_dep(s):
    """Mesma regra do gate do atualizar.sh: recurso CARREGADO externo = dependência."""
    if re.search(r"cdnjs|<script src|@import|url\(\s*https?:", s):
        return True
    allow = ("creativecommons.org/licenses/", "googletagmanager.com", "bera.ia.br",
             "github.com/beralzir/ficha-do-jogo")  # CC e GitHub são hyperlinks, não recursos carregados
    return any(not any(a in u for a in allow) for u in re.findall(r"https?://\S+", s))


def main():
    os.makedirs(OUT, exist_ok=True)
    problems = []
    for a in ASSETS:
        shutil.copyfile(os.path.join(DIST, a), os.path.join(OUT, a))
    for p in PAGES:
        html = open(os.path.join(DIST, p), encoding="utf-8").read()
        html = html.replace(SELF, SELF_ARQ)
        ban = BANNER_NEUTRO if p.endswith("_generico.html") else BANNER
        html, nsub = re.subn(r"(<body[^>]*>)", lambda m: m.group(1) + ban, html, count=1)
        if nsub != 1:
            problems.append(f"{p}: <body> não encontrado p/ banner")
        if SELF_ARQ not in html:
            problems.append(f"{p}: canonical/og não reescrito")
        if _ext_dep(html):
            problems.append(f"{p}: dependência externa fora da allowlist")
        open(os.path.join(OUT, p), "w", encoding="utf-8").write(html)
        print(f"  copa2026/{p}: {len(html)} chars · banner ok · self-URLs -> /copa2026/")
    if problems:
        sys.exit("SNAPSHOT FALHOU: " + "; ".join(problems))
    print(f"snapshot congelado em {os.path.relpath(OUT, ROOT)}/ ({len(PAGES)} páginas + {len(ASSETS)} assets)")


if __name__ == "__main__":
    main()
