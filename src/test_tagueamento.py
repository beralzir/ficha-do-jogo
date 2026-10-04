#!/usr/bin/env python3
"""Gate do tagueamento GA4/GTM da edição Eleições 2026 (auditoria tags-bera, 04/10/2026).

Regra do Bera (LGPD): o site mede só NAVEGAÇÃO. Nada que identifique pessoa ou revele
opinião: nunca candidato (nome, número, sq), texto digitado, valor de filtro, escolha do
eleitor nem URL de destino completa.

1. Toda página servida na raiz (worker.js SLUG + raiz + 404) tem o GTM no <head>, o
   <noscript> logo depois do <body> e o track.js atual (shell.TRACK), uma vez cada.
2. page_name coerente: o <body data-page> de cada página servida é o que o track.js
   calcula para o slug dela (fdj_nav_select.target). Sem isso o destino vira "unknown".
3. Todo link interno das páginas tem destino conhecido (nenhum nav_select "unknown").
4. 404 com page_name próprio (antes inflava page_name=index).
5. Seções observadas (data-scene) com id curto e único por página.
6. Privacidade do track.js: saída só com o host, nenhum valor de campo lido, nada de
   href completo. ERROS PLANTADOS: mandar a.href no outbound e ler o valor de um campo.
7. Transparência e oposição (guia de cookies da ANPD, 2022): página /privacidade linkada no
   rodapé de toda página servida, com o contato e o botão "não medir"; com a escolha gravada,
   o GTM não carrega e o track() não empurra. ERRO PLANTADO: GTM sem a checagem.
8. Escudo de saída antes do GTM: o clique em link externo é contido na captura da janela, e o
   "clique de saída" automático do GA4 (URL completa, com o sq) nunca vê o evento, mesmo se a opção
   for religada no painel. ERRO PLANTADO: página com o escudo depois do GTM.

Usa rede? Não. Uso:  python3 src/test_tagueamento.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DIST = os.path.join(ROOT, "dist")
sys.path.insert(0, HERE)
import shell  # noqa: E402

FALHAS = []


def check(nome, cond, detalhe=""):
    print(f"  {'ok  ' if cond else 'FALHA'} {nome}" + (f"  ({detalhe})" if detalhe else ""))
    if not cond:
        FALHAS.append(nome)


def page_of(href):
    """Espelho em Python do _pageOf do shell.TRACK."""
    seg = re.sub(r"[#?].*$", "", href or "").rstrip("/").split("/")[-1]
    if seg in (".", "index.html"):
        seg = ""
    if seg in shell.NAV_PAGE:
        return shell.NAV_PAGE[seg]
    if re.fullmatch(r"uf-[a-z]{2}", seg):
        return "eleicoes_uf"
    if re.fullmatch(r"publico-[a-z-]+", seg):
        return seg
    return "unknown"


def privacidade_ok(track):
    return ("target: a.hostname" in track and "a.href" not in track
            and not re.search(r"\.value\b", track) and "location.hash" not in track)


def optout_ok(gtm_head, track):
    k = shell.OPTOUT_KEY
    return (f"if(w.localStorage.getItem('{k}')==='1')return" in gtm_head
            and gtm_head.index(k) < gtm_head.index("gtm.js")
            and f"if (localStorage.getItem('{k}') === '1') return;" in track)


def escudo_ok(h):
    g = shell.OUT_GUARD
    return (h.count(g) == 1 and "<script>" + g[len("<script>"):] in h
            and h.index(g) < h.index(shell.GTM_HEAD) < h.index("</head>")
            and "stopImmediatePropagation" in g and "addEventListener('click',g,true)" in g
            and "window.fdjOut = function (a)" in h)


def main():
    worker = open(os.path.join(ROOT, "worker.js"), encoding="utf-8").read()
    bloco = re.search(r"const SLUG = \{(.*?)\n\};", worker, re.S).group(1)
    slugs = dict(re.findall(r'"([a-z0-9-]+)":\s*"([a-z0-9_]+\.html)"', bloco))
    slugs[""] = "eleicoes_index.html"
    paginas = {s: open(os.path.join(DIST, f), encoding="utf-8").read() for s, f in slugs.items()}
    p404 = open(os.path.join(DIST, "404.html"), encoding="utf-8").read()

    print("1. GTM + track.js atual em toda página servida")
    sem = [s or "/" for s, h in list(paginas.items()) + [("404", p404)]
           if not (h.count(shell.GTM_HEAD) == 1 and h.count(shell.GTM_NOSCRIPT) == 1 and h.count(shell.TRACK) == 1
                   and h.index(shell.GTM_HEAD) < h.index("</head>") < h.index("<body") < h.index(shell.GTM_NOSCRIPT))]
    check(f"{len(paginas) + 1} páginas com GTM {shell.GTM_ID} no head, noscript no body e track.js atual",
          not sem, f"fora: {sem}")

    print("2. page_name = destino calculado pelo track.js")
    erradas = {}
    for s, h in paginas.items():
        dp = re.search(r'<body[^>]*data-page="([^"]+)"', h)
        if not dp or dp.group(1) != page_of("./" + s):
            erradas[s or "/"] = (dp.group(1) if dp else None, page_of("./" + s))
    check("data-page de cada slug do worker bate com o _pageOf", not erradas, str(erradas))

    print("3. links internos sem destino desconhecido")
    desconhecidos = sorted({href for h in paginas.values() for href in re.findall(r'<a [^>]*href="(\./[^"]*)"', h)
                            if page_of(href) == "unknown"})
    check("todo href ./… vira um page_name conhecido", not desconhecidos, str(desconhecidos[:5]))

    print("4. 404")
    check('404 com data-page="404"', '<body data-page="404">' in p404)

    print("5. seções observadas")
    ruins = {}
    for s, h in paginas.items():
        ids = re.findall(r"data-scene=\"?([^\s\">]+)", h)
        if len(ids) != len(set(ids)) or not all(re.fullmatch(r"[a-z_]{3,20}", i) for i in ids):
            ruins[s] = ids
    total = sum(len(re.findall(r"data-scene=", h)) for h in paginas.values())
    check(f"data-scene curtos e únicos por página ({total} no total)", not ruins and total > 0, str(ruins))

    print("6. privacidade do track.js")
    check("outbound manda só o host; nenhum valor de campo, href completo ou hash lido", privacidade_ok(shell.TRACK))
    plantado = shell.TRACK.replace("target: a.hostname", "target: a.href", 1)
    check("erro plantado (URL completa do TSE, com o sq) reprova", plantado != shell.TRACK and not privacidade_ok(plantado))
    plantado = shell.TRACK.replace("var label = t ?", "var q = document.getElementById('busca').value; var label = t ?", 1)
    check("erro plantado (texto digitado na busca) reprova", plantado != shell.TRACK and not privacidade_ok(plantado))

    print("7. transparência e oposição (LGPD)")
    sem_link = [s or "/" for s, h in paginas.items() if s != "privacidade" and shell.PRIVACIDADE not in h]
    check("link Privacidade no rodapé de toda página servida", not sem_link, f"sem link: {sem_link}")
    priv = paginas.get("privacidade", "")
    check("/privacidade com contato, botão 'não medir' e a chave do opt-out",
          "mailto:privacidade@bera.ia.br" in priv and 'id=med-btn' in priv and f'"{shell.OPTOUT_KEY}"' in priv
          and f'ga-disable-{shell.GA4_ID}' in priv)
    check("com a escolha gravada, o GTM não carrega e o track() não empurra", optout_ok(shell.GTM_HEAD, shell.TRACK))
    plantado = shell.GTM_HEAD.replace(f"try{{if(w.localStorage.getItem('{shell.OPTOUT_KEY}')==='1')return}}catch(e){{}}", "", 1)
    check("erro plantado (GTM sem a checagem do opt-out) reprova", plantado != shell.GTM_HEAD and not optout_ok(plantado, shell.TRACK))

    print("8. escudo de saída")
    sem = [s or "/" for s, h in list(paginas.items()) + [("404", p404)] if not escudo_ok(h)]
    check("escudo em toda página servida, antes do GTM, na captura da janela", not sem, f"fora: {sem}")
    h = paginas["presidencial"]
    plantado = h.replace(shell.OUT_GUARD, "", 1).replace(shell.GTM_HEAD, shell.GTM_HEAD + shell.OUT_GUARD, 1)
    check("erro plantado (escudo depois do GTM) reprova", plantado != h and not escudo_ok(plantado))

    if FALHAS:
        print(f"\nTAGUEAMENTO REPROVADO: {len(FALHAS)} falha(s).")
        return 1
    print("\nTAGUEAMENTO VERDE.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
