#!/usr/bin/env python3
"""Landing/index de bera.ia.br/ficha-do-jogo/ -> dist/index.html (front door das 4 páginas).
Sistema 2.5 (theme.py, dark+light via prefers-color-scheme), zero-dep, zero-JS, mobile-first."""
import os, sys, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme, shell
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); DIST = os.path.join(ROOT, "dist")

CARDS = [
    ("Dashboard", "copa2026_dashboard.html", "Probabilidade por seleção, fase e jogo — 48 seleções, 50k simulações.", "📊"),
    ("Resultados", "copa2026_resultados.html", "Tabelas por grupo e a chave do mata-mata, conforme os jogos acontecem.", "🏆"),
    ("Placares", "copa2026_bolao.html", "Placar previsto de 4 modelos por jogo + previsto × real dos já disputados.", "⚽"),
    ("Modelos", "copa2026_modelos.html", "Laboratório: qual modelagem acerta mais, pra quê e por quê — leaderboard e odds por modelo.", "🧪"),
]
cards = "".join(f'<a class=card href="./{href}"><div class=ci>{ic}</div>'
                f'<div class=ct><b>{t}</b><span>{d}</span></div></a>' for t, href, d, ic in CARDS)

HTML = f"""<!DOCTYPE html><html lang=pt-BR><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>Ficha do Jogo · Copa do Mundo 2026</title>
{shell.HEAD}
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
<div class=wrap>
<div class=hero><h1>Copa do Mundo 2026</h1>
<div class=sub>Modelo probabilístico · 48 seleções, 50k simulações</div></div>
<div class=cardgrid>{cards}</div>
<div class=foot>Site estático · estimativas, não garantias · forecast 9/jun/2026 · {shell.CREDIT}</div>
</div>{shell.JS}</body></html>"""

open(f"{DIST}/index.html", "w").write(HTML)
open(f"{DIST}/favicon.svg", "w").write(shell.FAVICON_SVG)  # ícone do site (a marca) — referenciado por todas as páginas
# ícone do atalho de tela (iOS/Chrome usam apple-touch-icon PNG) — gerado do logo, em assets/ (commitado)
_ati = os.path.join(ROOT, "assets", "apple-touch-icon.png")
if os.path.exists(_ati): shutil.copy(_ati, f"{DIST}/apple-touch-icon.png")
# redirect da página Comparativo (removida; unificada em Placares/Resultados/Modelos) — zero-dep, sem GTM
_REDIR = ('<!DOCTYPE html><html lang=pt-BR><head><meta charset=utf-8>'
          '<meta http-equiv=refresh content="0; url=./copa2026_bolao.html">'
          '<link rel=canonical href="./copa2026_bolao.html"><title>Movido · Ficha do Jogo</title></head>'
          '<body>Esta página foi unificada — veja <a href="./copa2026_bolao.html">Placares</a>, '
          '<a href="./copa2026_resultados.html">Resultados</a> e <a href="./copa2026_modelos.html">Modelos</a>.</body></html>')
open(f"{DIST}/copa2026_comparativo.html", "w").write(_REDIR)
print("index:", len(HTML), "chars | cards:", len(CARDS), "| http:", HTML.count("http://") + HTML.count("https://"),
      "| favicon.svg + apple-touch-icon:", os.path.exists(f"{DIST}/apple-touch-icon.png"))
