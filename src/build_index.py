#!/usr/bin/env python3
"""Landing/index de bera.ia.br/ficha-do-jogo/ -> dist/index.html (front door das 4 páginas).
Sistema 2.5 (theme.py, dark+light via prefers-color-scheme), zero-dep, zero-JS, mobile-first."""
import os, sys, shutil, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme, shell
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); DIST = os.path.join(ROOT, "dist")

# data do forecast derivada do dado (não hardcoded) — acompanha o cron de atualização
_MO = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
try:
    _gen = json.load(open(os.path.join(ROOT, "data", "wc2026_results.json")))["meta"]["generated"]
    _y, _m, _d = _gen.split("-"); GENDATE = f"{int(_d):02d}/{_MO[int(_m) - 1]}/{_y}"
except Exception:
    GENDATE = ""

CARDS = [
    ("Dashboard", "dashboard", "Probabilidade por seleção, fase e jogo — 48 seleções, 50k simulações.", "📊"),
    ("Resultados", "resultados", "Tabelas por grupo e a chave do mata-mata, conforme os jogos acontecem.", "🏆"),
    ("Placares", "placares", "Placar previsto de 4 modelos por jogo + previsto × real dos já disputados.", "⚽"),
    ("Modelos", "modelos", "Laboratório: qual modelagem acerta mais, pra quê e por quê — leaderboard e odds por modelo.", "🧪"),
]
cards = "".join(f'<a class=card href="./{href}"><div class=ci aria-hidden="true">{ic}</div>'
                f'<div class=ct><b>{t}</b><span>{d}</span></div></a>' for t, href, d, ic in CARDS)

HTML = f"""<!DOCTYPE html><html lang=pt-BR><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>Ficha do Jogo · Copa do Mundo 2026</title>
{shell.HEAD}{shell.meta("Ficha do Jogo · Copa do Mundo 2026", "Modelo probabilístico da Copa do Mundo 2026 — probabilidades por seleção, fase e jogo, placares previstos e comparação de modelos.", "")}
<style>
{theme.PALETTE}
{shell.CSS}
*{{box-sizing:border-box}}body{{margin:0;--maxw:900px;background:var(--bg);color:var(--ink);font-family:-apple-system,system-ui,"Segoe UI",Roboto,sans-serif;line-height:1.4}}
.wrap{{max-width:900px;margin:0 auto;padding:20px 16px 48px}}
.hero{{margin:16px 0 20px}}
.cardgrid{{display:grid;grid-template-columns:1fr;gap:10px}}
@media(min-width:680px){{.cardgrid{{grid-template-columns:1fr 1fr}}}}
h1{{font-size:26px;font-weight:800;letter-spacing:-.02em;margin:0}}
.sub{{color:var(--mut);font-size:14px;margin:4px 0 22px}}
.card{{display:flex;gap:14px;align-items:center;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px;margin:0;text-decoration:none;color:inherit}}
.card:hover{{border-color:var(--ac)}}
.ci{{font-size:26px;flex:none;width:44px;height:44px;display:flex;align-items:center;justify-content:center;background:var(--box);border-radius:11px}}
.ct b{{display:block;font-size:16px;font-weight:800;color:var(--ac)}}
.ct span{{display:block;font-size:12.5px;color:var(--mut);margin-top:2px}}
.foot{{color:var(--mut);font-size:11px;margin-top:24px;border-top:1px solid var(--line);padding-top:12px}}
</style></head><body data-page="index">{shell.topbar("", tabs=False)}
<main class=wrap id=main tabindex=-1>
<div class=hero><h1>Copa do Mundo 2026</h1>
<div class=sub>Modelo probabilístico · 48 seleções, 50k simulações</div></div>
<div class=cardgrid>{cards}</div>
<footer class=foot>Site estático · estimativas, não garantias{f' · forecast {GENDATE}' if GENDATE else ''} · {shell.CREDIT}</footer>
</main>{shell.JS}</body></html>"""

open(f"{DIST}/index.html", "w").write(HTML)
open(f"{DIST}/favicon.svg", "w").write(shell.FAVICON_SVG)  # ícone do site (a marca) — referenciado por todas as páginas
# ícone do atalho de tela (iOS/Chrome usam apple-touch-icon PNG) — gerado do logo, em assets/ (commitado)
_ati = os.path.join(ROOT, "assets", "apple-touch-icon.png")
if os.path.exists(_ati): shutil.copy(_ati, f"{DIST}/apple-touch-icon.png")
# capa OG (preview social 1200x630, gerada da marca) — referenciada por shell.meta()
_og = os.path.join(ROOT, "assets", "og-cover.png")
if os.path.exists(_og): shutil.copy(_og, f"{DIST}/og-cover.png")
# redirect da página Comparativo (removida; unificada em Placares/Resultados/Modelos) — zero-dep, sem GTM
_REDIR = ('<!DOCTYPE html><html lang=pt-BR><head><meta charset=utf-8>'
          '<meta http-equiv=refresh content="0; url=./placares">'
          '<link rel=canonical href="./placares"><title>Movido · Ficha do Jogo</title></head>'
          '<body>Esta página foi unificada — veja <a href="./placares">Placares</a>, '
          '<a href="./resultados">Resultados</a> e <a href="./modelos">Modelos</a>.</body></html>')
open(f"{DIST}/copa2026_comparativo.html", "w").write(_REDIR)
# 404 da marca (servida pelo worker.js em qualquer rota inexistente)
_404 = f"""<!DOCTYPE html><html lang=pt-BR><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>Página não encontrada · Ficha do Jogo</title>
{shell.HEAD}<style>{theme.PALETTE}{shell.CSS}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,system-ui,"Segoe UI",Roboto,sans-serif;line-height:1.5}}
.e404{{max-width:560px;margin:0 auto;padding:72px 20px;text-align:center}}
.e404 h1{{font-size:60px;margin:0;color:var(--ac);letter-spacing:-.02em}}
.e404 p{{color:var(--mut);font-size:15px;margin:8px 0 0}}
.e404 .b{{display:inline-block;margin-top:20px;padding:10px 18px;border:1px solid var(--ac);border-radius:10px;color:var(--ac);text-decoration:none;font-weight:700}}
.e404 .b:hover{{background:var(--acsoft)}}
</style></head>
<body data-page="index">{shell.topbar("", tabs=False)}
<main class=e404 id=main tabindex=-1><h1>404</h1><p>Essa página não existe ou foi movida.</p><a class=b href="./">← Voltar ao início</a></main>{shell.JS}</body></html>"""
open(f"{DIST}/404.html", "w").write(_404)
print("index:", len(HTML), "chars | cards:", len(CARDS), "| http:", HTML.count("http://") + HTML.count("https://"),
      "| favicon.svg + apple-touch-icon:", os.path.exists(f"{DIST}/apple-touch-icon.png"))
