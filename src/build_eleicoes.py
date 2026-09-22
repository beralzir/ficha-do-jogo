#!/usr/bin/env python3
"""
Páginas da edição Eleições 2026 (etapa B6) -> dist/eleicoes_*.html

Gera, estático-primeiro e zero-dep, reusando shell.py/theme.py (mesmo design
da Copa; schema da marca em ~/Workspaces/design-schemas/ficha-do-jogo.md):
  - eleicoes_index.html      hub: ficha presidencial + 27 cards de UF
  - eleicoes_dashboard.html  presidencial (matriz, gráfico SVG, pares de 2ºT)
  - eleicoes_uf_<uf>.html    27 páginas: governador + senado (2 vagas)
  - eleicoes_modelos.html    harness: leaderboard walk-forward + método

Assinaturas visuais da edição (dentro do sistema): banda de incerteza
LISTRADA na ponta da barra (±1 desvio) e chip de qualidade do dado por
corrida. Barras de dado usam semânticas (--win/--draw); cromo nunca em dado.

Links internos com SLUGS LIMPOS da raiz (/presidencial, /uf-xx, /modelos),
mapeados pelo worker.js desde a virada (B7). Os .html diretos dão 301 pro slug.
"""
import datetime as dt
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shell
import theme

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "data")
DIST = os.path.join(ROOT, "dist")

R = json.load(open(f"{BASE}/eleicoes2026_results.json", encoding="utf-8"))
POLLS = json.load(open(f"{BASE}/live/polls.json", encoding="utf-8"))
STRUCT = json.load(open(f"{BASE}/eleicoes2026_structure.json", encoding="utf-8"))
SCORES_P = f"{BASE}/eleicoes/model_scores.json"
SCORES = json.load(open(SCORES_P, encoding="utf-8")) if os.path.exists(SCORES_P) else None
CFG = json.load(open(f"{BASE}/eleicoes/model_configs.json", encoding="utf-8"))


def _opt(caminho):
    """Lê um JSON opcional. Falha ABERTA: a página de Inflexões é diagnóstico, e
    um arquivo ausente não pode derrubar o build das 30 páginas que publicam."""
    return (json.load(open(caminho, encoding="utf-8"))
            if os.path.exists(caminho) else None)


INFL = _opt(f"{BASE}/eleicoes/inflexoes.json")
INFL_SER = _opt(f"{BASE}/eleicoes/inflexoes_series.json")
EVENTOS = _opt(f"{BASE}/eleicoes/eventos.json")

AS_OF = R["meta"]["as_of"]
T1 = dt.date(2026, 10, 4)
DIAS_T1 = max((T1 - dt.date.fromisoformat(AS_OF)).days, 0)

UF_NOME = {
    "AC": "Acre", "AL": "Alagoas", "AM": "Amazonas", "AP": "Amapá", "BA": "Bahia",
    "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás",
    "MA": "Maranhão", "MG": "Minas Gerais", "MS": "Mato Grosso do Sul",
    "MT": "Mato Grosso", "PA": "Pará", "PB": "Paraíba", "PE": "Pernambuco",
    "PI": "Piauí", "PR": "Paraná", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RO": "Rondônia", "RR": "Roraima", "RS": "Rio Grande do Sul", "SC": "Santa Catarina",
    "SE": "Sergipe", "SP": "São Paulo", "TO": "Tocantins",
}
UFS = sorted(UF_NOME)

QUAL = {  # rótulo + classe do chip de qualidade do dado
    "ok": ("dado fresco", "q-ok"),
    "defasada": ("dado defasado", "q-mid"),
    "pesquisa_velha": ("pesquisa velha", "q-old"),
    "sem_pesquisa": ("sem pesquisa: prior declarado", "q-old"),
}


def pct(p, dec=0):
    if p > 0.995:
        return "&gt;99%"
    if 0 < p < 0.005:
        return "&lt;1%"
    return f"{p * 100:.{dec}f}%"


def title_case(u):
    """Nome de urna vem TODO MAIÚSCULO do TSE; exibe em Title Case, preservando
    siglas-nome curtas (JHC, ACM, ZÉ) que o capitalize() estragaria."""
    out = []
    for w in u.split():
        lw = w.lower()
        if lw in ("de", "do", "da", "dos", "das", "e"):
            out.append(lw)
        elif len(w) <= 3:
            out.append(w.upper())
        else:
            out.append(lw.capitalize())
    return " ".join(out)


def nome(c):
    return title_case(c["urna"])


def qual_chip(q):
    lbl, cls = QUAL[q]
    return f'<span class="qch {cls}">{lbl}</span>'


def bar(share, sd, cls="b-win"):
    """Barra de share com banda listrada de ±1 desvio na ponta (assinatura da edição)."""
    w = max(min(share * 100, 100), 0)
    band = max(min(sd * 100 * 2, 100 - max(w - sd * 100, 0)), 0)
    left = max(w - sd * 100, 0)
    return (f'<div class="exbar" role="img" aria-label="{share*100:.0f}% com incerteza de '
            f'mais ou menos {sd*100:.0f} pontos"><i class="{cls}" style="width:{w:.1f}%"></i>'
            f'<i class="exband" style="left:{left:.1f}%;width:{band:.1f}%"></i></div>')


def minibar(share, cls="b-win"):
    w = max(min(share * 100, 100), 0)
    return f'<div class="exmini"><i class="{cls}" style="width:{w:.1f}%"></i></div>'


def page(fname, title, desc, slug, body, data_page, active=None):
    html = f"""<!DOCTYPE html><html lang=pt-BR><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>{title}</title>
{shell.HEAD}{shell.meta(title, desc, slug)}
<style>{theme.PALETTE}{shell.CSS}{CSS}</style>
</head><body data-page="{data_page}">{topbar(active)}
<main id=main class=wrap>
{body}
<footer class=foot>Agregador de pesquisas registradas + Monte Carlo (20 mil cenários). Estimativas com incerteza, não garantias · edição Eleições 2026 · {shell.CREDIT}</footer>
</main>{shell.JS}</body></html>"""
    with open(os.path.join(DIST, fname), "w", encoding="utf-8") as f:
        f.write(html)


NAV = [("Corridas", "", "idx"),
       ("Presidencial", "presidencial", "pres"),
       ("Inflexões", "inflexoes", "inf"),
       ("Públicos", "publicos", "pub"),
       ("Modelos", "modelos", "mod")]


def topbar(active):
    links = "".join((f'<a class="on" aria-current="page">{l}</a>' if k == active
                     else f'<a href="./{h}">{l}</a>') for l, h, k in NAV)
    nav = f'<nav class="tabs" aria-label="Navegação entre páginas">{links}</nav>'
    return (shell.GTM_NOSCRIPT + '<a class="skip" href="#main">Pular para o conteúdo</a>'
            '<header class="topbar"><div class="bar">'
            '<a class="brand" href="./" aria-label="Ficha do Jogo, Eleições 2026, início">'
            + shell.LOGO + '<span class="nm">Ficha <span>do Jogo</span></span></a>'
            '<span class="ed">Eleições 2026</span><span class="sp"></span>'
            '<button class="tg" id="tg" type="button" onclick="cycleTheme()" title="Tema escuro · clique para alternar" aria-label="Alternar tema">☾</button>'
            '</div>' + nav + '</header>')


def upd():
    n_polls = sum(1 for p in POLLS["polls"] if p["campo_fim"])
    return (f'<p class=upd>forecast com pesquisas até {shell._d_br(AS_OF, True)} · '
            f'{DIAS_T1} dias para o 1º turno (04/out) · {n_polls} pesquisas na base</p>')


# ---------------------------------------------------------------- index

def card_pres():
    r = R["races"]["PRES"]
    rows = ""
    for c in r["candidates"][:4]:
        rows += (f'<div class=exrow><span class=exnm>{nome(c)} <b class=pty>{c["partido"]}</b></span>'
                 + bar(c["share"], c["sd"]) +
                 f'<span class=exval>{pct(c["eleito"])}</span></div>')
    return (f'<a class="fichon" href="./presidencial">'
            f'<div class=fh><h2>Presidência da República</h2>{qual_chip(r["data_quality"])}</div>'
            f'<p class=fsub>share agregado (barra, com banda de incerteza) e probabilidade de ELEIÇÃO (número)</p>'
            f'{rows}<span class=fmore>abrir a ficha presidencial ▸</span></a>')


def card_uf(uf):
    g = R["races"][f"GOV-{uf}"]
    s = R["races"][f"SEN-{uf}"]
    gtop = g["candidates"][:2]
    stop = s["candidates"][:2]
    grows = "".join(
        f'<div class=exrow-s><span class=exnm-s>{nome(c)}</span>{minibar(c["share"])}'
        f'<span class=exval-s>{pct(c["eleito"])}</span></div>' for c in gtop)
    snames = " · ".join(f'{nome(c)} <span class=exval-s>{pct(c["eleito"])}</span>' for c in stop)
    worst = g["data_quality"] if QUALRANK[g["data_quality"]] >= QUALRANK[s["data_quality"]] else s["data_quality"]
    return (f'<a class="ficha" href="./uf-{uf.lower()}">'
            f'<div class=fh><h3>{UF_NOME[uf]} <b class=pty>{uf}</b></h3>{qual_chip(worst)}</div>'
            f'<p class=flbl>governador</p>{grows}'
            f'<p class=flbl>senado (2 vagas)</p><p class=fsen>{snames}</p></a>')


QUALRANK = {"ok": 0, "defasada": 1, "pesquisa_velha": 2, "sem_pesquisa": 3}


def build_index():
    cards = "".join(card_uf(uf) for uf in UFS)
    body = f"""<section class=hero>
<h1>Ficha do Jogo <span class=hx>· Eleições 2026</span></h1>
<p class=lead>Modelo probabilístico aberto das 55 corridas majoritárias do país: presidência,
27 governos e 54 vagas do Senado (2 por UF, sem 2º turno). Agregamos pesquisas registradas,
simulamos 20 mil cenários e mostramos a incerteza em vez de escondê-la.</p>
{upd()}
</section>
{card_pres()}
<h2 class=sech id=estados>As 27 unidades da federação</h2>
<p class=fsub>cada ficha traz os 2 primeiros de governador e do Senado; clique para a corrida completa</p>
<div class=fgrid>{cards}</div>
{shell.accordion("Como ler estas fichas / método", METODO_TXT)}
"""
    page("eleicoes_index.html", "Ficha do Jogo · Eleições 2026",
         "Probabilidades das eleições 2026: presidência, 27 governos e Senado, com agregador de pesquisas e Monte Carlo. Incerteza declarada, corrida a corrida.",
         "", body, "eleicoes_index", "idx")


METODO_TXT = (
    "<p><b>Share agregado</b>: média ponderada das pesquisas registradas (recência com meia-vida de "
    "21 dias, tamanho de amostra, correção básica de viés de instituto), com indecisos realocados "
    "proporcionalmente. <b>A banda listrada</b> na ponta de cada barra é ±1 desvio: onde ela é larga, "
    "a corrida está aberta de verdade.</p>"
    "<p><b>P(eleito)</b> vem de 20 mil simulações Monte Carlo por corrida: incerteza entre institutos, "
    "indecisos, deriva até a eleição e um choque nacional simples por bloco partidário. Presidência e "
    "governos têm 2º turno condicional (pesquisas de pares quando existem); o Senado elege os 2 mais "
    "votados em turno único, com o eleitor votando em 2 nomes.</p>"
    "<p><b>Chips de qualidade</b>: corrida com pesquisa velha ou sem pesquisa carrega um prior declarado "
    "de alta incerteza, nunca um 50/50 silencioso. Candidatos e situação de registro vêm do TSE "
    "(chave estável por candidato); pesquisas, das tabelas públicas da Wikipédia, validadas por "
    "amostragem contra as fichas com nº de registro TSE. Método completo na página "
    '<a href="./modelos">Modelos</a>.</p>')


# ---------------------------------------------------------------- presidencial

def chart_pres():
    """SVG estático: share mensal ponderado dos 4 líderes ao longo de 2026."""
    r = R["races"]["PRES"]
    tops = [c["sq"] for c in r["candidates"][:4]]
    names = {c["sq"]: nome(c) for c in r["candidates"]}
    pts = {sq: {} for sq in tops}
    for p in POLLS["polls"]:
        if p["race"] != "PRES" or p["cenario"] != "estimulada" or not p["campo_fim"]:
            continue
        if not p["campo_fim"].startswith("2026"):
            continue
        tot = sum(n["pct"] for n in p["numeros"] if n["sq"] is not None)
        got = sum(n["pct"] for n in p["numeros"] if n["sq"] in tops)
        if tot <= 0 or got / max(sum(n["pct"] for n in p["numeros"]), 1e-9) < 0.5:
            continue
        mo = int(p["campo_fim"][5:7])
        for n in p["numeros"]:
            if n["sq"] in tops:
                pts[n["sq"]].setdefault(mo, []).append(n["pct"] / tot)
    months = sorted({m for d in pts.values() for m in d})
    if len(months) < 2:
        return ""
    W, H, PADL, PADB, PADT = 720, 240, 34, 26, 10
    x0, x1 = months[0], months[-1]

    def X(m):
        return PADL + (m - x0) / max(x1 - x0, 1) * (W - PADL - 12)

    def Y(v):
        return PADT + (1 - v / 0.6) * (H - PADT - PADB)
    cores = ["var(--win)", "var(--loss)", "var(--draw)", "var(--mut)"]
    grid = "".join(f'<line x1="{PADL}" y1="{Y(v):.0f}" x2="{W-8}" y2="{Y(v):.0f}" class=cg />'
                   f'<text x="4" y="{Y(v)+4:.0f}" class=ct>{int(v*100)}%</text>'
                   for v in (0.0, 0.2, 0.4, 0.6))
    meses_lbl = "".join(f'<text x="{X(m):.0f}" y="{H-6}" class=ct text-anchor=middle>{shell._MO_BR[m-1]}</text>'
                        for m in months)
    lines = legend = ""
    for i, sq in enumerate(tops):
        mm = sorted(pts[sq])
        if len(mm) < 2:
            continue
        d = " ".join(f"{X(m):.0f},{Y(sum(pts[sq][m])/len(pts[sq][m])):.0f}" for m in mm)
        lines += f'<polyline points="{d}" fill="none" stroke="{cores[i]}" stroke-width="2.2" />'
        last = mm[-1]
        lines += "".join(f'<circle cx="{X(m):.0f}" cy="{Y(sum(pts[sq][m])/len(pts[sq][m])):.0f}" r="3" fill="{cores[i]}"/>' for m in mm)
        legend += (f'<span class=lg><i style="background:{cores[i]}"></i>{names[sq]} '
                   f'{sum(pts[sq][last])/len(pts[sq][last])*100:.0f}%</span>')
    return (f'<div class=chwrap><svg viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Evolução mensal do share agregado dos quatro líderes em 2026">{grid}{meses_lbl}{lines}</svg>'
            f'<div class=lgs>{legend}</div></div>')


def build_pres():
    r = R["races"]["PRES"]
    lider = r["candidates"][0]
    p_t1 = sum(c.get("t1_win", 0) for c in r["candidates"])
    par_top = max((r["pares_2t"] or {}).items(), key=lambda kv: kv[1], default=(None, 0))
    par_lbl = "–"
    if par_top[0]:
        a, b = par_top[0].split("x")
        nm_ = {str(c["sq"]): nome(c) for c in r["candidates"]}
        par_lbl = f"{nm_.get(a, a)} × {nm_.get(b, b)}"
    kpis = (
        f'<div class=kpi><b>{pct(lider["eleito"])}</b><span>{nome(lider)} eleito</span></div>'
        f'<div class=kpi><b>{pct(p_t1)}</b><span>decisão já no 1º turno</span></div>'
        f'<div class=kpi><b>{pct(par_top[1])}</b><span>2º turno {par_lbl}</span></div>'
        f'<div class=kpi><b>{r["n_polls"]}</b><span>pesquisas de {r["institutes"]} institutos</span></div>')
    rows = ""
    for c in r["candidates"]:
        if c["share"] < 0.005 and c["eleito"] < 0.005:
            continue
        rows += (f'<tr><th scope=row>{nome(c)} <b class=pty>{c["partido"]}</b></th>'
                 f'<td class=cbar>{bar(c["share"], c["sd"])}<span class=shl>{pct(c["share"])} ±{c["sd"]*100:.0f}</span></td>'
                 f'<td>{pct(c["t2"])}</td><td>{pct(c["t1_win"])}</td><td class=big>{pct(c["eleito"])}</td></tr>')
    pares = ""
    if r["pares_2t"]:
        nm_ = {str(c["sq"]): nome(c) for c in r["candidates"]}
        for k, v in r["pares_2t"].items():
            a, b = k.split("x")
            pares += f'<tr><th scope=row>{nm_.get(a, a)} × {nm_.get(b, b)}</th><td>{pct(v)}</td></tr>'
        pares = (f'<h2 class=sech>Pares possíveis de 2º turno</h2>'
                 f'<table class=extb><thead><tr><th scope=col>par</th>'
                 f'<th scope=col>chance de ser ESTE o par</th></tr></thead><tbody>{pares}</tbody></table>')
    body = f"""<h1>Presidência da República {qual_chip(r["data_quality"])}</h1>
{upd()}
<div class=kpis>{kpis}</div>
<h2 class=sech>A corrida, candidato a candidato</h2>
<table class=extb>
<thead><tr><th scope=col>candidato</th><th scope=col>share agregado (±1 desvio)</th>
<th scope=col>vai ao 2º turno</th><th scope=col>vence no 1º</th><th scope=col>ELEITO</th></tr></thead>
<tbody>{rows}</tbody></table>
<h2 class=sech>Evolução em 2026</h2>
{chart_pres()}
{pares}
{shell.accordion("Como ler / limitações declaradas", METODO_TXT + CAVEATS_TXT)}
"""
    page("eleicoes_dashboard.html", "Presidencial — Ficha do Jogo · Eleições 2026",
         "Probabilidades da eleição presidencial 2026: share agregado das pesquisas, chance de 2º turno e de eleição por candidato, com incerteza declarada.",
         "presidencial", body, "eleicoes_dashboard", "pres")


CAVEATS_TXT = ("<p><b>Limitações desta versão</b>: indecisos são realocados proporcionalmente; a "
               "probabilidade do 2º turno por par não se correlaciona com a força sorteada no 1º; "
               "pesquisa mede intenção declarada, não voto. Os números são estimativas com ruído, "
               "e diferenças pequenas entre candidatos são empate técnico na prática.</p>")


# ---------------------------------------------------------------- UF

def build_uf(uf):
    g = R["races"][f"GOV-{uf}"]
    s = R["races"][f"SEN-{uf}"]
    grows = ""
    for c in g["candidates"]:
        if c["share"] < 0.005 and c["eleito"] < 0.005:
            continue
        grows += (f'<tr><th scope=row>{nome(c)} <b class=pty>{c["partido"]}</b></th>'
                  f'<td class=cbar>{bar(c["share"], c["sd"])}<span class=shl>{pct(c["share"])} ±{c["sd"]*100:.0f}</span></td>'
                  f'<td>{pct(c["t2"])}</td><td class=big>{pct(c["eleito"])}</td></tr>')
    pares = ""
    if g["pares_2t"]:
        nm_ = {str(c["sq"]): nome(c) for c in g["candidates"]}
        linhas = "".join(f'<tr><th scope=row>{nm_.get(k.split("x")[0], "?")} × {nm_.get(k.split("x")[1], "?")}</th>'
                         f'<td>{pct(v)}</td></tr>' for k, v in g["pares_2t"].items())
        pares = (f'<h3 class=sech3>Pares possíveis de 2º turno</h3><table class=extb>'
                 f'<thead><tr><th scope=col>par</th><th scope=col>chance</th></tr></thead>'
                 f'<tbody>{linhas}</tbody></table>')
    srows = ""
    for c in s["candidates"]:
        if c["eleito"] < 0.005 and c["share"] < 0.01:
            continue
        srows += (f'<tr><th scope=row>{nome(c)} <b class=pty>{c["partido"]}</b></th>'
                  f'<td>{pct(c["share"])}</td>'
                  f'<td class=cbar>{minibar(c["eleito"])}<span class=shl>{pct(c["eleito"])}</span></td></tr>')
    body = f"""<p class=bcr><a href="./">◂ todas as corridas</a></p>
<h1>{UF_NOME[uf]} <b class=pty>{uf}</b></h1>
{upd()}
<h2 class=sech>Governador {qual_chip(g["data_quality"])}</h2>
<p class=fsub>{g["n_polls"]} pesquisas de {g["institutes"]} institutos · última em {shell._d_br(g["freshest"] or "", True) or "–"}</p>
<table class=extb>
<thead><tr><th scope=col>candidato</th><th scope=col>share agregado (±1 desvio)</th>
<th scope=col>vai ao 2º turno</th><th scope=col>ELEITO</th></tr></thead><tbody>{grows}</tbody></table>
{pares}
<h2 class=sech>Senado · 2 vagas {qual_chip(s["data_quality"])}</h2>
<p class=fsub>o eleitor vota em DOIS nomes; elegem-se os 2 mais votados, sem 2º turno ·
{s["n_polls"]} pesquisas · consolidado re-normalizado (institutos divulgam bases diferentes)</p>
<table class=extb>
<thead><tr><th scope=col>candidato</th><th scope=col>share</th><th scope=col>P(uma das 2 vagas)</th></tr></thead>
<tbody>{srows}</tbody></table>
{shell.accordion("Como ler / método", METODO_TXT + CAVEATS_TXT)}
"""
    page(f"eleicoes_uf_{uf.lower()}.html", f"{UF_NOME[uf]} — Ficha do Jogo · Eleições 2026",
         f"Probabilidades 2026 em {UF_NOME[uf]}: governador e as 2 vagas do Senado, com agregador de pesquisas e incerteza declarada.",
         f"uf-{uf.lower()}", body, "eleicoes_uf")


# ---------------------------------------------------------------- modelos

def build_modelos():
    # Um competidor sintético alimentado por MOCK não pode aparecer como se
    # tivesse rodado campo. A página lê a própria pesquisa e declara.
    mocks = [p for p in POLLS["polls"] if p.get("sintetico") and p.get("mock")]
    board = ""
    if SCORES:
        for b in SCORES["leaderboard"]:
            mae = f"{b['mae_share']*100:.1f} pp" if b["mae_share"] is not None else "sem dado ainda"
            m = CFG["models"].get(b["model"], {})
            # Rotulagem SINTÉTICO é PERMANENTE e sai do registro de modelos, não
            # de uma lista de nomes aqui: modelo sintético novo nasce rotulado.
            if m.get("sintetico"):
                rot_ = "SINTÉTICO (MOCK)" if mocks else "SINTÉTICO"
                tit = ("Pesquisa sintética por personas. Não é evidência de comportamento real."
                       if not mocks else
                       "Ainda sem campo: o número por trás é um mock de teste do encanamento.")
                selo = f'<span class="qch q-syn" title="{tit}">{rot_}</span> '
            else:
                selo = ""
            board += (f'<tr><th scope=row>{selo}{b["model"]}</th><td>{m.get("desc", "")}</td>'
                      f'<td>{b["freezes"]}</td><td>{b["comparacoes"]}</td><td class=big>{mae}</td></tr>')
    MOCKAVISO = ("" if not mocks else
                 '<p class=lead style="border:1px dashed var(--ac);border-radius:8px;'
                 'padding:11px 14px"><b>Aviso: o campo sintético ainda não rodou.</b> '
                 'Os competidores marcados SINTÉTICO (MOCK) estão alimentados por um '
                 'número de teste, colocado para provar que o encanamento funciona de '
                 'ponta a ponta. Eles não medem nada até o painel de personas ir a campo, '
                 'e é por isso que aparecem sem comparações.</p>')
    n_freezes = len(glob.glob(f"{BASE}/eleicoes/models/freeze-*.json"))
    cav = "".join(f"<li>{c}</li>" for c in (SCORES or {}).get("caveats", []))
    body = f"""<h1>Laboratório de modelos</h1>
{upd()}
<p class=lead>Variantes do agregador congelam um forecast por dia desde o primeiro dia da
edição. A métrica foi definida ANTES de medir: erro médio de share contra a PRÓXIMA pesquisa de
cada corrida (até 14 dias), e Brier contra o resultado oficial quando a urna abrir. Quem calibra
melhor, vence.</p>
<p class=lead><b>Os competidores marcados SINTÉTICO não leem pesquisa de instituto</b>: o voto
deles vem de um painel de personas geradas por IA. Estão aqui para responder uma pergunta de
pesquisa, se um painel sintético consegue acompanhar pesquisa de campo, e a resposta pode muito
bem ser que não. <b>Nada do que eles produzem entra no forecast do site</b>, e isso não depende
de disciplina: o motor recusa ler pesquisa sintética no modelo oficial, e um teste
(<code>src/test_synths_gate.py</code>) reprova se alguém quebrar essa separação.</p>
{MOCKAVISO}
<h2 class=sech>Leaderboard walk-forward</h2>
<table class=extb><thead><tr><th scope=col>modelo</th><th scope=col>o que muda</th>
<th scope=col>freezes</th><th scope=col>comparações</th><th scope=col>erro médio</th></tr></thead>
<tbody>{board}</tbody></table>
<p class=fsub>{n_freezes} freezes gravados · comparações acumulam conforme novas pesquisas chegam:
no começo da série o quadro é vazio MESMO, e está certo assim.</p>
<h2 class=sech>Ressalvas (viajam com os dados)</h2>
<ul class=cavs>{cav}</ul>
{shell.accordion("Método em uma tela", METODO_TXT + CAVEATS_TXT, is_open=True)}
"""
    page("eleicoes_modelos.html", "Modelos — Ficha do Jogo · Eleições 2026",
         "Harness multi-modelo das eleições 2026: variantes do agregador, freezes diários e leaderboard walk-forward com métrica pré-especificada.",
         "modelos", body, "eleicoes_modelos", "mod")



# ---------------------------------------------------------------- Inflexões

def _dia(t0, i):
    return (dt.date.fromisoformat(t0) + dt.timedelta(days=i)).isoformat()


def chart_inflexao(ser, saltos, eventos, titulo, sq_alvo=None):
    """SVG estático do nível latente com banda, faixas nos saltos e eventos.

    Estático-primeiro (invariante 3): o traçado inteiro é calculado em Python e
    sai no HTML. Sem JavaScript a página mostra exatamente o mesmo gráfico.

    A BANDA é de 1 desvio do FILTRO: a incerteza sobre onde o nível estava
    naquele dia. NÃO é a banda do forecast, que inclui o passeio que falta até a
    urna e o ERRO_ELEICAO e vive no `sd` do results.json. Misturar as duas faria
    a página parecer mais confiante sobre o passado do que o modelo é sobre o
    futuro, que é o contrário da verdade.
    """
    nivel, banda, t0 = ser["nivel"], ser["banda"], ser["t0"]
    # RECORTE no ano da campanha. Algumas séries começam em jan/2025 (a
    # presidencial tem 614 dias), e desenhar 20 meses para mostrar um movimento
    # de três semanas deixa o gráfico quase todo reta. Medido antes de cortar:
    # ZERO dos 119 dias em destaque cai em 2025, o mais antigo é 11/01/2026,
    # então o recorte não esconde nenhum movimento que a página mostra. O eixo
    # diz onde começa, e o corte é o mesmo para todos os candidatos.
    corte = (dt.date(2026, 1, 1) - dt.date.fromisoformat(t0)).days
    if corte > 0:
        nivel, banda = nivel[corte:], banda[corte:]
        t0 = "2026-01-01"
    n = len(nivel)
    if n < 8:
        return ""
    W, H, HT = 720, 196, 34
    PADL, PADR, PADT, PADB = 38, 10, 12, 20
    topo = max(max(v + b for v, b in zip(nivel, banda)) * 1.12, 0.03)

    def X(i):
        return PADL + i / max(n - 1, 1) * (W - PADL - PADR)

    def Y(v):
        return PADT + (1 - min(v / topo, 1.0)) * (H - PADT - PADB)

    # Escala pequena precisa de passo pequeno: com topo de 8% e passo de 5pp o
    # gráfico saía com DUAS linhas de grade, que é grade nenhuma.
    passo = (0.02 if topo <= 0.12 else
             0.05 if topo <= 0.25 else
             0.1 if topo <= 0.55 else 0.2)
    linhas_y, v = "", 0.0
    while v <= topo + 1e-9:
        linhas_y += ('<line x1="%d" y1="%.0f" x2="%d" y2="%.0f" class=cg />'
                     '<text x="4" y="%.0f" class=ct>%.0f%%</text>'
                     % (PADL, Y(v), W - PADR, Y(v), Y(v) + 4, v * 100))
        v += passo

    marcas, visto = "", set()
    for i in range(n):
        d = _dia(t0, i)
        if d[:7] in visto:
            continue
        visto.add(d[:7])
        if n < 120 or len(visto) % 2 == 0:
            marcas += ('<text x="%.0f" y="%d" class=ct text-anchor=middle>%s</text>'
                       % (X(i), H - 5, shell._MO_BR[int(d[5:7]) - 1]))

    # FAIXA no salto, não linha: a datação tem LARGURA (a janela que o detector
    # mediu). Desenhar um traço de um dia venderia precisão que o método não tem.
    jw = int((INFL or {}).get("params", {}).get("JANELA_SALTO", 3))
    faixas = ""
    for sl in saltos:
        i = (dt.date.fromisoformat(sl["data"]) - dt.date.fromisoformat(t0)).days
        if not (0 <= i < n):
            continue
        x0, x1 = X(max(i - 1, 0)), X(min(i + jw, n - 1))
        cor = "var(--win)" if sl["delta_janela_pp"] >= 0 else "var(--loss)"
        faixas += ('<rect x="%.0f" y="%d" width="%.0f" height="%.0f" fill="%s" opacity=".13" />'
                   '<line x1="%.0f" y1="%d" x2="%.0f" y2="%.0f" stroke="%s" '
                   'stroke-width="1.4" opacity=".75" />'
                   % (x0, PADT, max(x1 - x0, 2), H - PADT - PADB, cor,
                      X(i), PADT, X(i), H - PADB, cor))

    cima = " ".join("%.1f,%.1f" % (X(i), Y(nivel[i] + banda[i])) for i in range(n))
    baixo = " ".join("%.1f,%.1f" % (X(i), Y(max(nivel[i] - banda[i], 0)))
                     for i in range(n - 1, -1, -1))
    linha = " ".join("%.1f,%.1f" % (X(i), Y(nivel[i])) for i in range(n))

    # LINHA DO TEMPO. Evento que MIRA este candidato sai cheio e datado; os
    # outros saem como tique fraco, sem rótulo. A 1ª versão desenhava todo
    # evento igual em todo gráfico, e com um único evento no registro isso fazia
    # o episódio do Cury aparecer marcado e datado embaixo da série do Flávio
    # Bolsonaro e da Maria do Carmo, sugerindo uma relevância que não existe.
    tl = '<line x1="%d" y1="%d" x2="%d" y2="%d" class=cg />' % (PADL, H + 14, W - PADR, H + 14)
    meus = outros = 0
    for e in eventos:
        i = (dt.date.fromisoformat(e["data"]) - dt.date.fromisoformat(t0)).days
        if not (0 <= i < n):
            continue
        if sq_alvo is not None and sq_alvo in (e.get("alvo") or []):
            meus += 1
            tl += ('<line x1="%.0f" y1="%d" x2="%.0f" y2="%d" stroke="var(--ac)" '
                   'stroke-width="2" /><text x="%.0f" y="%d" class=ct text-anchor=middle>'
                   '%s</text>'
                   % (X(i), H + 7, X(i), H + 21, X(i), H + 31, shell._d_br(e["data"])))
        else:
            outros += 1
            tl += ('<line x1="%.0f" y1="%d" x2="%.0f" y2="%d" stroke="var(--mut)" '
                   'stroke-width="1" opacity=".5" />' % (X(i), H + 11, X(i), H + 17))
    if not meus:
        tl += ('<text x="%d" y="%d" class=ct>nenhum evento registrado MIRA este '
               'candidato nesta janela%s</text>'
               % (PADL, H + 30, (" (%d outro(s) marcado(s) fraco)" % outros) if outros else ""))

    return ('<div class=chwrap><svg viewBox="0 0 %d %d" role="img" aria-label="%s">'
            '%s%s<polygon points="%s %s" fill="var(--ac)" opacity=".16" />'
            '<polyline points="%s" fill="none" stroke="var(--ac)" stroke-width="1.9" />'
            '%s%s</svg></div>'
            % (W, H + HT, titulo, linhas_y, faixas, cima, baixo, linha, marcas, tl))


def build_inflexoes():
    """Página Inflexões. Falha ABERTA: sem o JSON de diagnóstico ela não sai, e
    as 30 páginas que publicam seguem normalmente."""
    if not INFL or not INFL_SER:
        print("AVISO: sem inflexoes.json/inflexoes_series.json; página NÃO gerada")
        return False
    infl = INFL["inflexoes"]
    dest = [r for r in infl if r["corroborado"] and r["relevante"]]
    evs = [dict(e) for e in (EVENTOS or {}).get("eventos", [])]
    # pre_especificado é DERIVADO, nunca declarado (M3). A página recalcula em
    # vez de ler um campo: se lesse, haveria duas verdades possíveis no repo.
    for e in evs:
        e["_pre"] = e["registrado_em"] <= e["data"]
    n_pre = sum(1 for e in evs if e["_pre"])
    jw = int(INFL.get("params", {}).get("JANELA_SALTO", 3))

    cartas, vistos = "", []
    for r in dest:
        ch = (r["corrida"], r["sq"])
        if ch in vistos or len(vistos) >= 8:
            continue
        ser = INFL_SER["series"].get("%s|%s" % (r["corrida"], r["sq"]))
        if not ser:
            continue
        meus = [x for x in dest if x["corrida"] == r["corrida"] and x["sq"] == r["sq"]]
        alvo = ('Nível estimado de %s em %s ao longo da campanha, com banda de incerteza '
                'e faixas nos dias de movimento detectado'
                % (title_case(r["urna"]), r["corrida"]))
        svg = chart_inflexao(ser, meus, evs, alvo, sq_alvo=r["sq"])
        if not svg:
            continue
        vistos.append(ch)
        datas = ", ".join(shell._d_br(x["data"], True) for x in meus[:4])
        inst = sorted(set(sum([x["institutos"] + x["corroborado_por"] for x in meus], [])))
        maior = max(meus, key=lambda x: abs(x["delta_janela_pp"]))
        cartas += (
            '<article class=infc><h3 class=sech3>%s <span class=pty>%s</span></h3>'
            '<p class=fsub>%d movimento(s) detectado(s): %s · corroborado por %d instituto(s)</p>'
            '%s'
            '<p class=fsub>Maior movimento de nível na janela: <b>%+.2f p.p.</b> em %d dias. '
            'A faixa colorida marca a janela medida, não um instante.</p></article>'
            % (title_case(r["urna"]), r["corrida"], len(meus), datas, len(inst), svg,
               maior["delta_janela_pp"], jw))

    linhas = ""
    for r in dest[:60]:
        linhas += ('<tr><th scope=row>%s</th><td>%s</td><td>%s</td><td>%+.1f</td>'
                   '<td class=big>%+.2f pp</td><td>%d</td></tr>'
                   % (title_case(r["urna"]), r["corrida"], shell._d_br(r["data"], True),
                      r["z"], r["delta_janela_pp"],
                      len(set(r["institutos"] + r["corroborado_por"]))))

    ev_linhas = ""
    for e in sorted(evs, key=lambda x: x["data"]):
        selo = ('<span class="qch q-ok">PRÉ-ESPECIFICADO</span>' if e["_pre"]
                else '<span class="qch q-mid">EXPLORATÓRIO</span>')
        ev_linhas += ('<tr><th scope=row>%s</th><td>%s</td><td>%s</td><td>%s</td></tr>'
                      % (shell._d_br(e["data"], True), e["tipo"].replace("_", " "),
                         e.get("direcao_esperada", "?"), selo))
    if not ev_linhas:
        ev_linhas = "<tr><td colspan=4>Nenhum evento no registro ainda.</td></tr>"

    cav = "".join("<li>%s</li>" % c for c in INFL.get("ressalvas", []))
    body = """<h1>Inflexões</h1>
%s
<p class=lead>O resto do site mostra <b>onde</b> cada corrida está. Esta página tenta responder
<b>quando mudou</b>. Um filtro de estado estima o nível de cada candidato dia a dia; quando uma
pesquisa chega muito longe do que o filtro esperava, aquele dia vira candidato a ponto de
inflexão. Embaixo de cada gráfico fica a linha do tempo dos eventos registrados, no mesmo eixo,
para você ver com os próprios olhos se as duas coisas coincidem.</p>

<p class=lead style="border:1px dashed var(--ac);border-radius:8px;padding:11px 14px">
<b>Confie na DATA, desconfie da MAGNITUDE.</b> O tamanho do salto aqui é subestimado por
construção, e isso foi medido, não suposto. O modelo faz o nível passear em escala logit com um
desvio diário constante, calibrado num segundo turno em que os dois candidatos estavam perto de
50%%. Como a conversão de logit para share vale p·(1−p), o mesmo passeio vale <b>0,33 p.p./dia</b>
para quem está em 50%% e <b>0,06 p.p./dia</b> para quem está em 5%%. Um movimento de +3,0 p.p. num
dia, num candidato com 5%%, exigiria um desvio <b>48 vezes</b> maior que o calibrado para este
filtro aceitá-lo. A data em que o movimento aparece, essa, é confiável: o episódio conhecido de
27 de agosto aparece aqui em 26 e 27 de agosto, corroborado por instituto diferente.</p>

<h2 class=sech>Como ler esta página</h2>
<ol class=lead>
<li><b>Candidato a inflexão não é inflexão confirmada.</b> O método não separa um salto real do
nível de uma pesquisa fora da curva. Por isso só entram aqui os dias corroborados por pelo menos
dois institutos, em candidato com 2%% ou mais. Os dois cortes foram fixados antes de olhar o
resultado.</li>
<li><b>Coincidir não é causar.</b> A linha do tempo e as faixas dividem o mesmo eixo para você
comparar, e só isso. Atribuir efeito a um evento exige direção escrita antes do fato e janela
placebo, que é trabalho ainda não feito.</li>
<li><b>Nenhum evento do registro foi pré-especificado até agora</b> (%d de %d). Um evento só conta
como pré-especificado se a direção esperada foi escrita <i>antes</i> de ele acontecer, e isso é
derivado da data de registro, não declarado à mão. Enquanto esse número for zero, nada nesta
página sustenta afirmação de efeito.</li>
</ol>

<h2 class=sech>Movimentos detectados</h2>
<p class=fsub>Os %d candidatos com maior movimento de nível, entre os %d dias em destaque. A área
sombreada é a incerteza do filtro sobre onde o nível estava naquele dia, e não a banda do
forecast.</p>
%s

<h2 class=sech>Registro de eventos</h2>
<p class=fsub>Curado à mão. O selo é DERIVADO de (data de registro ≤ data do fato): o arquivo não
aceita um campo declarando pré-especificação, justamente porque ele seria preenchido de boa-fé
depois de o efeito já ser conhecido.</p>
<table class=extb><thead><tr><th scope=col>data</th><th scope=col>tipo</th>
<th scope=col>direção esperada</th><th scope=col>status</th></tr></thead>
<tbody>%s</tbody></table>

<h2 class=sech>Todos os dias em destaque</h2>
<p class=fsub>%d dias, de %d candidatos brutos. Ordenados por movimento de nível, não por z: z
grande com nível parado é pesquisa fora da curva, que é o que o método não sabe separar.</p>
<table class=extb><thead><tr><th scope=col>candidato</th><th scope=col>corrida</th>
<th scope=col>dia</th><th scope=col>z</th><th scope=col>movimento na janela</th>
<th scope=col>institutos</th></tr></thead>
<tbody>%s</tbody></table>
%s

<h2 class=sech>Ressalvas (viajam com os dados)</h2>
<ul class=cavs>%s</ul>
""" % (upd(), n_pre, len(evs), len(vistos), len(dest),
       cartas or "<p class=lead>Nenhum movimento passou no funil nesta rodada.</p>",
       ev_linhas, len(dest), len(infl), linhas,
       "<p class=fsub>Mostrando os 60 primeiros.</p>" if len(dest) > 60 else "", cav)

    page("eleicoes_inflexoes.html", "Inflexões — Ficha do Jogo · Eleições 2026",
         "Quando cada corrida das eleições 2026 se mexeu: nível latente com banda, dias de "
         "movimento detectado e a linha do tempo dos eventos registrados.",
         "inflexoes", body, "eleicoes_inflexoes", "inf")
    return True


# ---------------------------------------------------------------- CSS da edição

CSS = r"""
/* Inflexões: card por candidato. Sem cor de cromo no dado, como no resto da
   edição; a faixa do salto usa --win/--loss porque ali a cor SIGNIFICA direção
   do movimento, e o texto ao lado repete o sinal para quem não vê a cor. */
.infc{border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:14px 0}
.infc .sech3{margin:0 0 2px}
.infc .chwrap{margin:6px 0 2px}
body{margin:0;--maxw:1100px;background:var(--bg);color:var(--ink);font-family:-apple-system,system-ui,"Segoe UI",Roboto,sans-serif;line-height:1.4}
.wrap{max-width:var(--maxw,1100px);margin:0 auto;padding:18px 16px 40px}
.ed{font-size:11px;font-weight:800;letter-spacing:.09em;text-transform:uppercase;color:var(--ac);border:1px solid var(--line);border-radius:20px;padding:3px 10px;white-space:nowrap}
.hero h1{font-size:clamp(24px,4.4vw,34px);letter-spacing:-.02em;margin:14px 0 8px}
.hero .hx{color:var(--ac)}
.lead{color:var(--notetx);max-width:70ch;line-height:1.55;margin:0 0 6px}
.upd{color:var(--mut);font-size:12.5px;margin:4px 0 14px}
.sech{font-size:17px;margin:26px 0 4px;letter-spacing:-.01em}
.sech3{font-size:14px;margin:18px 0 4px}
.fsub{color:var(--mut);font-size:12.5px;margin:2px 0 10px}
.bcr{margin:8px 0 0;font-size:13px}
.pty{color:var(--mut);font-weight:700;font-size:.78em;vertical-align:1px}
.qch{font-size:10px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;border-radius:20px;padding:2px 8px;white-space:nowrap;flex:none}
.q-ok{background:rgba(34,197,94,.14);color:var(--win)}
.q-mid{background:rgba(234,179,8,.15);color:var(--draw)}
.q-old{background:rgba(239,68,68,.14);color:var(--loss)}
/* SINTÉTICO: chip próprio, não reaproveita o de "dado velho". Não é dado ruim,
   é dado de OUTRA natureza, e a distinção tem de ser visível. Borda tracejada
   como marca permanente de que aquilo não veio de campo. */
/* SINTÉTICO: selo de NATUREZA, não chip de qualidade, por isso não reaproveita
   q-ok/q-mid/q-old. Texto em --ink e borda em --ac de propósito: --ac sobre o
   card no tema claro chega a 3.9:1, abaixo do 4.5:1 que texto pequeno exige.
   Separar leitura (texto) de identidade (borda) resolve sem perder a marca. */
.q-syn{background:none;color:var(--ink);border:1px dashed var(--ac)}
.fichon{display:block;border:1px solid var(--ac);border-radius:12px;background:var(--card);padding:16px 18px;margin:16px 0 4px;text-decoration:none;color:var(--ink)}
.fichon:hover{background:var(--rowhov)}
.fichon h2{margin:0;font-size:19px}
.fmore{display:inline-block;margin-top:10px;color:var(--ac);font-size:12.5px;font-weight:700}
.fh{display:flex;align-items:center;gap:10px;justify-content:space-between}
.fgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px;margin:12px 0 22px}
.ficha{display:block;border:1px solid var(--line);border-radius:12px;background:var(--card);padding:13px 14px;text-decoration:none;color:var(--ink)}
.ficha:hover{border-color:var(--ac);background:var(--rowhov)}
.ficha h3{margin:0;font-size:15px}
.flbl{margin:9px 0 3px;font-size:10px;text-transform:uppercase;letter-spacing:.11em;font-weight:800;color:var(--mut)}
.fsen{margin:0;font-size:12.5px;line-height:1.5}
.exrow{display:grid;grid-template-columns:minmax(150px,1fr) 2fr 52px;gap:10px;align-items:center;margin:7px 0}
.exrow-s{display:grid;grid-template-columns:minmax(90px,1fr) 1fr 40px;gap:8px;align-items:center;margin:4px 0}
.exnm{font-weight:700;font-size:14px}
.exnm-s{font-weight:600;font-size:12.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.exval{font-weight:800;font-variant-numeric:tabular-nums;text-align:right}
.exval-s{font-weight:700;font-size:12px;color:var(--mut);font-variant-numeric:tabular-nums;text-align:right}
.exbar,.exmini{position:relative;height:14px;background:var(--box);border-radius:5px;overflow:hidden}
.exmini{height:9px}
.exbar i,.exmini i{position:absolute;left:0;top:0;bottom:0;border-radius:5px}
.b-win{background:var(--win)}
.exband{background:repeating-linear-gradient(-55deg,transparent 0 3px,var(--draw) 3px 5px);opacity:.75;border-radius:0!important}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:14px 0 8px}
.kpi{border:1px solid var(--line);border-radius:12px;background:var(--card);padding:12px 14px}
.kpi b{display:block;font-size:24px;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.kpi span{color:var(--mut);font-size:11.5px}
.extb{width:100%;border-collapse:collapse;margin:8px 0 6px;font-size:13.5px}
.extb th,.extb td{padding:8px 10px;text-align:left;border-bottom:1px solid var(--line2);vertical-align:middle}
.extb thead th{font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:var(--mut)}
.extb tbody th{font-weight:700}
.extb td.big{font-weight:800;font-variant-numeric:tabular-nums}
.cbar{min-width:180px}
.cbar .exbar,.cbar .exmini{margin-bottom:3px}
.shl{font-size:11px;color:var(--mut);font-variant-numeric:tabular-nums}
.chwrap{border:1px solid var(--line);border-radius:12px;background:var(--card);padding:12px;overflow-x:auto}
.chwrap svg{width:100%;height:auto;min-width:520px}
.cg{stroke:var(--line2)}
.ct{fill:var(--mut);font-size:10px}
.lgs{display:flex;gap:14px;flex-wrap:wrap;margin-top:8px;font-size:12px}
.lg{display:inline-flex;align-items:center;gap:6px;font-weight:600}
.lg i{width:10px;height:10px;border-radius:3px;display:inline-block}
.cavs{color:var(--notetx);font-size:13px;line-height:1.6}
.foot{color:var(--mut);font-size:11.5px;margin-top:34px;border-top:1px solid var(--line);padding-top:12px}
@media (max-width:560px){.exrow{grid-template-columns:1fr 1.4fr 46px}.cbar{min-width:120px}}
"""

# accordion body precisa do CSS do shell (.acc etc.), já incluído via shell.CSS


def main():
    os.makedirs(DIST, exist_ok=True)
    build_index()
    build_pres()
    for uf in UFS:
        build_uf(uf)
    build_modelos()
    n = 30 + (1 if build_inflexoes() else 0)
    print(f"OK: {n} páginas (index, presidencial, 27 UFs, modelos"
          f"{', inflexões' if n > 30 else ''}) em dist/eleicoes_*.html · as_of {AS_OF}")


if __name__ == "__main__":
    main()
