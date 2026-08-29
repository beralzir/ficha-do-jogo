#!/usr/bin/env python3
"""Página "Modelos" (Laboratório de modelos) -> dist/copa2026_modelos.html
Mostra, estático-primeiro e zero-dep, o leaderboard de CALIBRAÇÃO dos modelos do harness
(data/model_scores.json), uma narrativa de atribuição auto-gerada dos números, e as odds de
título por modelo (data/models/*.json) com SELO de conditioning (pré-torneio vs ao-vivo).

Dois modos, decididos pelos DADOS (scores["measurement_complete"]):
  - preliminar (durante a Copa): só calibração de grupos, rótulos "preliminar".
  - FINAL (após finalize_scores.py): 1X2 de grupos+mata-mata, seção "Fase e título",
    narrativa de fechamento. É o modo do arquivo /copa2026.

Honestidade em destaque: caixa de RESSALVAS vinda dos dados (caveats).
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
FINAL = bool(scores.get("measurement_complete"))

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
    split = (f'<td class=num>{c["brier_group"]:.4f}</td><td class=num>{c["brier_ko"]:.4f}</td>'
             if FINAL else '')
    rows.append(
        f'<tr class="{ "win" if mid==best else "" }">'
        f'<td class=rk>{i+1}</td>'
        f'<td class=ml>{crown}{c["label"]}</td>'  # id interno (mid) NÃO exibido: vaza K/QUALK (dynamic_k40, qual_heavy…)
        f'<td class=ty>{typ}</td>'
        f'<td class=num><b>{c["brier"]:.4f}</b></td>'
        f'{split}'
        f'<td class=num>{c["logloss"]:.4f}</td>'
        f'<td class="num {vmcls}">{vms}</td>'
        f'<td class=num>{c["seguro_pts"]}</td>'
        f'<td class=num>{c["ousado_pts"]}</td>'
        f'<td class=num>{c["exact_ev"]}/{c["n_matches"]}</td></tr>')
split_h = '<th scope="col">grupos</th><th scope="col">KO</th>' if FINAL else ''
kb_lead = (
    ('Brier/log-loss do 1X2 nos <b>103 jogos medidos</b> (72 grupos + 31 mata-mata no espaço dos 120&nbsp;min) — <b>menor = melhor calibrado</b>. '
     'vs&nbsp;merc. = Brier(modelo) − Brier(market_only); <span class=neg>negativo</span> = melhor que o consenso de odds. '
     'Seg./Ous. = pontos dacopa (KO vale 2x). exato = cravadas de placar. '
     '<b>†</b> modelos que aprendem: no 1X2 a diferença segue dentro do ruído; na leitura de <b>fase</b> eles venceram (seção abaixo).')
    if FINAL else
    ('Brier/log-loss do 1X2 nos jogos de grupo — <b>menor = melhor calibrado</b>. '
     'vs&nbsp;merc. = Brier(modelo) − Brier(market_only); <span class=neg>negativo</span> = melhor que o consenso de odds. '
     'Seg./Ous. = pontos dacopa (placar Seguro/Ousado). exato = cravadas de placar. '
     '<b>†</b> modelos que aprendem: a diferença vs baseline está <b>dentro do ruído</b> (n pequeno) — ainda não dá pra dizer que aprender ajuda.'))
LEAD = ('<table class=lb><caption class="sr-only">Leaderboard de calibração dos modelos (menor Brier = melhor)</caption><thead><tr>'
        '<th scope="col">#</th><th scope="col">modelo</th><th scope="col">tipo</th><th scope="col">Brier</th>'
        f'{split_h}<th scope="col">log-loss</th>'
        '<th scope="col">vs&nbsp;merc.</th><th scope="col">Seg.</th><th scope="col">Ous.</th><th scope="col">exato</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
        f'<div class=kb>{kb_lead}</div>')

# ── Narrativa de atribuição (auto-gerada dos números) ─────────────────────────
def narrative():
    bc = CARDS[best]; base = CARDS.get("baseline"); mkt = CARDS.get("market_only"); mods = CARDS.get("models_only")
    if FINAL:
        s = [f'Medição <b>fechada</b> ({scores.get("n_matches")} jogos + fase/título): melhor calibração 1X2 da Copa inteira: <b>{bc["label"]}</b> (Brier {bc["brier"]:.4f}).']
        if mkt and base and mkt["brier"] <= base["brier"]:
            s.append(f'O aprendizado central se confirmou de ponta a ponta: <b>o consenso de odds venceu o 1X2</b> ({mkt["brier"]:.4f} vs {base["brier"]:.4f} do ensemble 45/35/20) — diluir o mercado no blend não pagou.')
        if mkt and mods and mods.get("brier_ko") is not None and mods["brier_ko"] < mkt["brier_ko"]:
            s.append(f'No <b>mata-mata isolado</b> o quadro inverte: só-modelos calibrou melhor ({mods["brier_ko"]:.4f}) que o consenso ({mkt["brier_ko"]:.4f}). Com 31 jogos, é indício, não veredito.')
        dyn = {m: c for m, c in CARDS.items() if c.get("learning") == "dynamic" and (c.get("phase") or {}).get("brier_phase") is not None}
        stat_ph = [c["phase"]["brier_phase"] for c in CARDS.values() if c.get("phase") and c.get("learning") is None]
        if dyn and stat_ph:
            bd = min(dyn.values(), key=lambda c: c["phase"]["brier_phase"])
            s.append(f'Na <b>leitura de fase</b> (véspera do mata-mata), os modelos que aprendem venceram: Brier {bd["phase"]["brier_phase"]:.4f} vs {min(stat_ph):.4f} do melhor estático — <b>reagir à Copa ajudou a ler o mata-mata</b>, mesmo com o 1X2 no ruído.')
        champ = scores.get("champion")
        if (champ and base and mkt and (base.get("phase") or {}).get("champion_p") is not None
                and (mkt.get("phase") or {}).get("champion_p") is not None):
            s.append(f'A campeã ({fl(champ)} {nm(champ)}) estava mais cotada nos modelos que no mercado na véspera do mata-mata: {base["phase"]["champion_p"]*100:.0f}% no ensemble vs {mkt["phase"]["champion_p"]*100:.0f}% no consenso. Um caso não é evidência, mas é o tipo de discordância que o harness existe pra medir.')
        return "".join(f"<li>{x}</li>" for x in s)
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

# ── Fase e título (só no modo FINAL) ──────────────────────────────────────────
def _phase_section():
    mods = [(m, c) for m, c in CARDS.items() if c.get("phase")]
    if not mods:
        return ""
    mods.sort(key=lambda z: z[1]["phase"]["brier_phase"])
    best_ph = mods[0][0]
    trs = []
    for m, c in mods:
        ph = c["phase"]
        cond = "pré-torneio" if ph.get("conditioning") == "pre-tournament" else "pós-grupos (ao vivo)"
        crown = "👑 " if m == best_ph else ""
        ptit = pct1(ph["champion_p"]) if ph.get("champion_p") is not None else "—"
        pll = f'{ph["champion_ll"]:.2f}' if ph.get("champion_ll") is not None else "—"
        trs.append(f'<tr class="{ "win" if m==best_ph else "" }"><td class=ml>{crown}{c["label"]}</td><td class=ty>{cond}</td>'
                   f'<td class=num><b>{ph["brier_phase"]:.4f}</b></td>'
                   f'<td class=num>{ptit}</td><td class=num>{pll}</td></tr>')
    ms = scores.get("milestone", {})
    champ = scores.get("champion", "")
    tbl = ('<table class=lb><caption class="sr-only">Leitura de fase e título por modelo (menor Brier de fase = melhor)</caption><thead><tr>'
           '<th scope="col">modelo</th><th scope="col">leitura</th><th scope="col">Brier fase</th>'
           f'<th scope="col">p({nm(champ)} 🏆)</th><th scope="col">log-loss título</th></tr></thead>'
           f'<tbody>{"".join(trs)}</tbody></table>'
           f'<div class=kb>Congelamento da <b>véspera do mata-mata</b> ({ms.get("as_of","")}: 72 jogos de grupo fechados, 0 KO) julgado contra a realidade: '
           'Brier dos marcadores oitavas/quartas/semi/final/título nas 48 seleções (menor = melhor) e a probabilidade dada à campeã real. '
           '<b>Leituras diferentes por desenho</b>: estáticos respondem "quem chutou melhor antes do torneio"; os que aprendem respondem "reagir à Copa ajuda?". A resposta desta edição: ajudou.</div>')
    return f'<h2 class=sec>Fase e título · fechado ao fim da Copa</h2><div class=tw>{tbl}</div>'

PHASE_HTML = _phase_section() if FINAL else ""

# ── Odds de título por modelo — DUAS tabelas (comparáveis só dentro de cada conditioning) ─────
def _champ_table(cols, top):
    fcs = {m: _forecast(m) for m in cols}
    fcs = {m: v for m, v in fcs.items() if v}
    if not fcs:
        return ""
    heads = "".join(f'<th scope="col">{CARDS[m]["label"].split("(")[0].strip()[:16]}</th>' for m in fcs)
    trows = []
    for t in top:
        cells = "".join(f'<td class=num>{pct1(fcs[m]["teams"][t]["champion"])}</td>' for m in fcs)
        trows.append(f'<tr><td class=tm>{fl(t)} {nm(t)}</td>{cells}</tr>')
    return (f'<table class=ch><caption class="sr-only">Probabilidade de título por modelo</caption><thead><tr><th scope="col">seleção</th>{heads}</tr></thead>'
            f'<tbody>{"".join(trows)}</tbody></table>')

ref = _forecast("baseline") or (_forecast(PRE_COLS[0]) if PRE_COLS else None)
if ref:
    top = sorted(ref["teams"], key=lambda t: ref["teams"][t]["champion"], reverse=True)[:8]
    preT = _champ_table(PRE_COLS, top)
    liveT = _champ_table(LIVE_COLS, top)
    live_lbl = ('Ao vivo · congelamento final de 20/07 (pós-final: colapsa na realidade)'
                if FINAL else 'Ao vivo · força aprendida + condicionada aos jogos (reage à Copa)')
    CHAMP = (f'<div class=subsec>Pré-torneio · mesma informação (compare o efeito dos <b>pesos</b>)</div>{preT}'
             f'<div class=subsec>{live_lbl}</div>{liveT}'
             '<div class=kb>Cada tabela usa <b>uma</b> informação — compare colunas <b>dentro</b> dela. '
             'Entre as duas, veja o <b>efeito de reagir à Copa</b>: ex., a Espanha cai do pré-torneio pro ao&nbsp;vivo '
             '(rendeu abaixo do esperado nos grupos). <b>Não</b> compare uma coluna pré-torneio com uma ao&nbsp;vivo diretamente.</div>')
else:
    CHAMP = '<div class=empty>Forecasts ainda não gerados (rode run_models.py).</div>'

CAVE = "".join(f"<li>{c}</li>" for c in scores.get("caveats", []))
asof = scores.get("as_of", "")
n = scores.get("n_matches", 0)

metodo_fim = (
    '<p>Medição <b>fechada</b> ao fim da Copa: 1X2 dos 103 jogos capturados (mata-mata no espaço '
    'dos 120&nbsp;min: "empate" = decisão nos pênaltis) e leitura de fase/título pela véspera do '
    'mata-mata. Ressalvas na caixa do topo.</p>'
    if FINAL else
    '<p>O leaderboard é <b>preliminar</b>: com poucos jogos, as diferenças pequenas são ruído. '
    'A medição de fase/título só fecha ao fim da Copa.</p>')
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
    'Calculados no 1X2 (vitória/empate/derrota) dos jogos já disputados.</p>'
    f'{metodo_fim}'), hint="abrir")

modo = "medição fechada" if FINAL else "qual modelagem acerta mais, pra quê e por quê"
foot_modo = "ranking FINAL (103 jogos + fase/título)." if FINAL else "ranking preliminar (só grupos)."
callout_t = "Leitura honesta (final)" if FINAL else "Leitura honesta (preliminar)"

OUT = os.environ.get("OUT_FILE") or f"{DIST}/copa2026_modelos.html"
HTML = f"""<!DOCTYPE html><html lang=pt-BR><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>Modelos · Ficha do Jogo</title>
{shell.HEAD}{shell.meta("Modelos — Ficha do Jogo · Copa 2026", "Laboratório de modelos da Copa 2026: qual modelagem calibra melhor (Brier/log-loss) e as odds de título por modelo.", "modelos")}
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
<main class=wrap id=main tabindex=-1>
<div class=hero><h1>Modelos</h1><div class=sub>Laboratório — {modo} · {n} jogos · {asof}</div></div>

<div class=callout><div class=ct>{callout_t}</div><ul>{CAVE}</ul></div>

<h2 class=sec>O que os dados dizem</h2>
<div class=story><ul>{narrative()}</ul></div>

<h2 class=sec>Leaderboard · calibração (menor Brier = melhor)</h2>
<div class=tw>{LEAD}</div>

{PHASE_HTML}

<h2 class=sec>Odds de título por modelo</h2>
<div class=tw>{CHAMP}</div>

{METODO}

<footer class=foot>Comparação de modelagens do mesmo motor (Monte Carlo, 50k). Estimativas, não garantias · {foot_modo} · {shell.CREDIT}</footer>
</main>{shell.JS}</body></html>"""

os.makedirs(DIST, exist_ok=True)
open(OUT, "w").write(HTML)
print("modelos:", len(HTML), "chars | modelos:", len(CARDS), "| modo:", "FINAL" if FINAL else "preliminar",
      "| champ cols:", len(PRE_COLS) + len(LIVE_COLS),
      "| <script>:", HTML.count("<script"), "| http:", HTML.count("http://") + HTML.count("https://"),
      "| OUT:", os.path.basename(OUT))
