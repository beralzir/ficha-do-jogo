#!/usr/bin/env python3
"""Página "Modelos" (Laboratório de modelos) -> dist/copa2026_modelos.html
Mostra, estático-primeiro e zero-dep, o leaderboard de CALIBRAÇÃO dos modelos do harness
(data/model_scores.json), uma narrativa de atribuição auto-gerada dos números, e as odds de
título por modelo (data/models/*.json) com SELO de conditioning (pré-torneio vs ao-vivo).

Honestidade em destaque: caixa de RESSALVAS (n pequeno = ruído; mercado já tem Opta; só grupos).
NÃO entra no white-label (expõe método/Opta de propósito — é a página de metodologia).
"""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme, shell, flags
from pt import PT

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "data"); DIST = os.path.join(ROOT, "dist")
scores = json.load(open(f"{BASE}/model_scores.json"))
CARDS = scores["models"]

# modelos curados p/ as tabelas de odds de título (largura mobile). DUAS tabelas separadas por
# conditioning — comparáveis só DENTRO de cada uma (mesma informação). Só os que têm forecast.
PRE_COLS = [c for c in ("baseline", "market_only", "w_mkt85") if c in CARDS]
LIVE_COLS = [c for c in ("dynamic_k20", "dynamic_k40") if c in CARDS]

def nm(t): return PT.get(t, ["", t])[1]
def fl(t): return PT.get(t, ["", t])[0]
def pct1(p):
    if p > 0.995: return ">99%"
    if 0 < p < 0.005: return "<1%"
    return f"{p*100:.1f}%"

def _forecast(mid):
    p = f"{BASE}/models/{mid}.json"
    return json.load(open(p)) if os.path.exists(p) else None

TYPE_PT = {None: "estático", "dynamic": "aprende (Elo)", "poisson_form": "forma de gols"}

# ── Leaderboard (ranqueado por Brier; menor = melhor) ─────────────────────────
order = sorted(CARDS, key=lambda m: (CARDS[m]["brier"] is None, CARDS[m]["brier"] or 9))
best = order[0]
rows = []
for i, mid in enumerate(order):
    c = CARDS[mid]
    vm = c.get("value_vs_market")
    vmcls = "pos" if (vm is not None and vm > 0) else ("neg" if (vm is not None and vm < 0) else "")
    vms = "—" if vm is None else f"{vm:+.4f}"
    lt = c.get("learning")
    typ = TYPE_PT.get(lt, "estático") + ('<sup class=dag>†</sup>' if lt else '')
    crown = "👑 " if mid == best else ""
    rows.append(
        f'<tr class="{ "win" if mid==best else "" }">'
        f'<td class=rk>{i+1}</td>'
        f'<td class=ml>{crown}{c["label"]}<span class=mid>{mid}</span></td>'
        f'<td class=ty>{typ}</td>'
        f'<td class=num><b>{c["brier"]:.4f}</b></td>'
        f'<td class=num>{c["logloss"]:.4f}</td>'
        f'<td class="num {vmcls}">{vms}</td>'
        f'<td class=num>{c["seguro_pts"]}</td>'
        f'<td class=num>{c["ousado_pts"]}</td>'
        f'<td class=num>{c["exact_ev"]}/{c["n_matches"]}</td></tr>')
LEAD = ('<table class=lb><thead><tr>'
        '<th>#</th><th>modelo</th><th>tipo</th><th>Brier</th><th>log-loss</th>'
        '<th>vs&nbsp;merc.</th><th>Seg.</th><th>Ous.</th><th>exato</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
        '<div class=kb>Brier/log-loss do 1X2 nos jogos de grupo — <b>menor = melhor calibrado</b>. '
        'vs&nbsp;merc. = Brier(modelo) − Brier(market_only); <span class=neg>negativo</span> = melhor que o consenso de odds. '
        'Seg./Ous. = pontos dacopa (placar Seguro/Ousado). exato = cravadas de placar. '
        '<b>†</b> modelos que aprendem: a diferença vs baseline está <b>dentro do ruído</b> (n pequeno) — ainda não dá pra dizer que aprender ajuda.</div>')

# ── Narrativa de atribuição (auto-gerada dos números) ─────────────────────────
def narrative():
    bc = CARDS[best]; base = CARDS.get("baseline"); mkt = CARDS.get("market_only"); mods = CARDS.get("models_only")
    s = [f'Melhor calibração até agora: <b>{bc["label"]}</b> (Brier {bc["brier"]:.4f}).']
    if mkt and base and mkt["brier"] < base["brier"]:
        extra = f' — e carregar nos modelos/qualitativo piora (só-modelos {mods["brier"]:.4f})' if mods else ""
        s.append(f'Dar <b>mais peso ao mercado</b> calibra melhor: o consenso de odds ({mkt["brier"]:.4f}) supera o ensemble 45/35/20 ({base["brier"]:.4f}){extra}.')
    dyn = {m: c for m, c in CARDS.items() if c.get("learning") == "dynamic" and c["brier"] is not None}
    if dyn and base:
        bm = min(dyn, key=lambda m: dyn[m]["brier"]); d = base["brier"] - dyn[bm]["brier"]
        if d > 0:
            s.append(f'<b>Aprender com os jogos</b> ({CARDS[bm]["label"]}) melhora o Brier em {d:.4f} sobre o baseline — mas isso está <b>dentro do ruído</b> (erro-padrão ~0,008 em {base["n_matches"]} jogos), então ainda <b>não</b> dá pra dizer que aprender funciona; precisa de mais jogos.')
        else:
            s.append('<b>Aprender com os jogos</b> ainda não superou o baseline nesta amostra (diferença dentro do ruído).')
    return "".join(f"<li>{x}</li>" for x in s)

# ── Odds de título por modelo — DUAS tabelas (comparáveis só dentro de cada conditioning) ─────
def _champ_table(cols, top):
    fcs = {m: _forecast(m) for m in cols}
    fcs = {m: v for m, v in fcs.items() if v}
    if not fcs:
        return ""
    heads = "".join(f'<th>{CARDS[m]["label"].split("(")[0].strip()[:16]}</th>' for m in fcs)
    trows = []
    for t in top:
        cells = "".join(f'<td class=num>{pct1(fcs[m]["teams"][t]["champion"])}</td>' for m in fcs)
        trows.append(f'<tr><td class=tm>{fl(t)} {nm(t)}</td>{cells}</tr>')
    return (f'<table class=ch><thead><tr><th>seleção</th>{heads}</tr></thead>'
            f'<tbody>{"".join(trows)}</tbody></table>')

ref = _forecast("baseline") or (_forecast(PRE_COLS[0]) if PRE_COLS else None)
if ref:
    top = sorted(ref["teams"], key=lambda t: ref["teams"][t]["champion"], reverse=True)[:8]
    preT = _champ_table(PRE_COLS, top)
    liveT = _champ_table(LIVE_COLS, top)
    CHAMP = (f'<div class=subsec>Pré-torneio · mesma informação (compare o efeito dos <b>pesos</b>)</div>{preT}'
             f'<div class=subsec>Ao vivo · força aprendida + condicionada aos jogos (reage à Copa)</div>{liveT}'
             '<div class=kb>Cada tabela usa <b>uma</b> informação — compare colunas <b>dentro</b> dela. '
             'Entre as duas, veja o <b>efeito de reagir à Copa</b>: ex., a Espanha cai do pré-torneio pro ao&nbsp;vivo '
             '(rendeu abaixo do esperado nos grupos). <b>Não</b> compare uma coluna pré-torneio com uma ao&nbsp;vivo diretamente.</div>')
else:
    CHAMP = '<div class=empty>Forecasts ainda não gerados (rode run_models.py).</div>'

CAVE = "".join(f"<li>{c}</li>" for c in scores.get("caveats", []))
asof = scores.get("as_of", "")
n = scores.get("n_matches", 0)

METODO = shell.accordion("Como ler / metodologia", (
    '<p>Cada <b>modelo</b> é uma combinação de pesos (mercado × modelos Opta/Elo × qualitativo) e, '
    'opcionalmente, um mecanismo que <b>aprende com os jogos</b>:</p>'
    '<dl>'
    '<dt>estático</dt><dd>força congelada no pré-torneio (9/jun). O 1X2 de cada jogo não muda durante a Copa.</dd>'
    '<dt>aprende (Elo)</dt><dd>a força do time sobe/desce a cada resultado (estilo Elo, zero-soma, ajuste por saldo). '
    'A previsão de cada jogo usa só a força da <b>véspera</b> (walk-forward, sem look-ahead).</dd>'
    '<dt>forma de gols</dt><dd>multiplicadores de ataque/defesa por seleção, atualizados dos gols. Entra só na calibração (sem forecast de título).</dd>'
    '</dl>'
    '<p><b>Brier / log-loss</b>: medem se as probabilidades batem com a realidade (menor = melhor). '
    'Calculados no 1X2 (vitória/empate/derrota) dos jogos de grupo já disputados.</p>'
    '<p>O leaderboard é <b>preliminar</b>: com poucos jogos, as diferenças pequenas são ruído. '
    'A medição de fase/título só fecha ao fim da Copa.</p>'), hint="abrir")

OUT = os.environ.get("OUT_FILE") or f"{DIST}/copa2026_modelos.html"
HTML = f"""<!DOCTYPE html><html lang=pt-BR><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>Modelos · Ficha do Jogo</title>
{shell.HEAD}
<style>
{theme.PALETTE}
{shell.CSS}
*{{box-sizing:border-box}}body{{margin:0;--maxw:920px;background:var(--bg);color:var(--ink);font-family:-apple-system,system-ui,"Segoe UI",Roboto,sans-serif;line-height:1.4;font-size:14px}}
.wrap{{max-width:920px;margin:0 auto;padding:14px}}
h1{{font-size:22px;font-weight:800;letter-spacing:-.02em;margin:0}}
.sub{{font-size:12px;color:var(--mut);margin:3px 0 14px}}
.sec{{font-size:11px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--ac);margin:22px 0 8px}}
.callout{{background:var(--acsoft);border:1px solid var(--ac);border-radius:11px;padding:12px 14px;margin:10px 0}}
.callout .ct{{font-size:11px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--ac);margin-bottom:6px}}
.callout ul,.story ul{{margin:0;padding-left:18px}}.callout li{{font-size:12px;color:var(--mut);margin:4px 0;line-height:1.5}}
.story{{background:var(--card);border-radius:11px;padding:6px 14px;margin:6px 0}}.story li{{font-size:13.5px;color:var(--ink);margin:8px 0;line-height:1.55}}.story b{{color:var(--ink)}}
.tw{{overflow-x:auto;-webkit-overflow-scrolling:touch}}
table{{border-collapse:collapse;width:100%;font-size:12.5px}}
.lb th,.ch th{{text-align:right;font-size:10px;text-transform:uppercase;letter-spacing:.05em;color:var(--mut);font-weight:800;padding:7px 7px;border-bottom:1px solid var(--line);white-space:nowrap}}
.lb th:nth-child(2),.ch th:first-child{{text-align:left}}
.lb td,.ch td{{padding:8px 7px;border-bottom:1px solid var(--line)}}
.num{{text-align:right;font-variant-numeric:tabular-nums}}
.lb .rk{{color:var(--mut);width:18px}}
.ml{{font-weight:700;color:var(--ink)}}.ml .mid{{display:block;font-weight:500;font-size:10.5px;color:var(--mut);font-variant-numeric:tabular-nums}}
.ty{{color:var(--mut);font-size:11.5px;white-space:nowrap}}
.lb tr.win td{{background:var(--acsoft)}}.lb tr.win .num b{{color:var(--ac)}}
.neg{{color:var(--win)}}.pos{{color:var(--mut)}}
.tm{{font-weight:600;white-space:nowrap}}
.subsec{{font-size:12px;font-weight:700;color:var(--ink);margin:14px 0 6px}}
.dag{{color:var(--ac);font-weight:800}}
.kb{{font-size:11px;color:var(--mut);margin-top:8px;line-height:1.5}}.kb b{{color:var(--ink)}}.kb .neg{{color:var(--win)}}
.empty{{color:var(--mut);font-size:13px;padding:12px;background:var(--card);border-radius:10px}}
.gl dt{{color:var(--ink);font-weight:700;margin-top:8px}}.gl dd{{margin:2px 0 0;color:var(--mut)}}
.foot{{color:var(--mut);font-size:11px;margin-top:20px;border-top:1px solid var(--line);padding-top:10px}}
</style></head><body data-page="modelos">{shell.topbar("mod")}{flags.SPRITE}
<div class=wrap>
<div class=hero><h1>Modelos</h1><div class=sub>Laboratório — qual modelagem acerta mais, pra quê e por quê · {n} jogos · {asof}</div></div>

<div class=callout><div class=ct>Leitura honesta (preliminar)</div><ul>{CAVE}</ul></div>

<div class=sec>O que os dados dizem</div>
<div class=story><ul>{narrative()}</ul></div>

<div class=sec>Leaderboard · calibração (menor Brier = melhor)</div>
<div class=tw>{LEAD}</div>

<div class=sec>Odds de título por modelo</div>
<div class=tw>{CHAMP}</div>

{METODO}

<div class=foot>Comparação de modelagens do mesmo motor (Monte Carlo, 50k). Estimativas, não garantias · ranking preliminar (só grupos). · {shell.CREDIT}</div>
</div>{shell.JS}</body></html>"""

os.makedirs(DIST, exist_ok=True)
open(OUT, "w").write(HTML)
print("modelos:", len(HTML), "chars | modelos:", len(CARDS), "| champ cols:", len(PRE_COLS) + len(LIVE_COLS),
      "| <script>:", HTML.count("<script"), "| http:", HTML.count("http://") + HTML.count("https://"),
      "| OUT:", os.path.basename(OUT))
