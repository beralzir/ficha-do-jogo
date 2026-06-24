#!/usr/bin/env python3
"""Página RESULTADOS / HUB -> dist/copa2026_resultados.html
REAL é o palco: standings por grupo + bracket/chave. As PREVISÕES do modelo (72 jogos de grupo e
confrontos prováveis do mata-mata) ficam em acordeão (.acc) logo abaixo do real de cada área —
nunca se misturam. DEDUP da Fase 3: estas
previsões saíram do dashboard (via predcards.py). Shell compartilhado (marca/abas/toggle/favicon),
desktop responsivo (#7), zero-dep. Standings = parcial (qualquer nº de jogos). Bracket = real quando
os 72 grupos fecham; antes, esqueleto de slots. Overrides: STATE_FILE · OUT_FILE."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bracket, theme, shell, predcards, dossie, flags, poll_tracker, metrics, state as ST
from pt import PT

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "data"); DIST = os.path.join(ROOT, "dist")
fx = json.load(open(f"{BASE}/fixtures.json"))
S = json.load(open(f"{BASE}/worldcup2026_structure.json"))
model = json.load(open(f"{BASE}/wc2026_results.json"))
doss = json.load(open(f"{BASE}/wc2026_dossiers.json"))
baseline = json.load(open(f"{BASE}/baseline/forecast_pretorneio.json"))
st = ST.ManualFileSource(os.environ.get("STATE_FILE") or None).load()
errs = ST.validate_state(st, fx)
if errs:
    print("ESTADO INVÁLIDO — abortando:", errs); sys.exit(1)
HOSTS = {"United States", "Mexico", "Canada"}
DATA = dossie.build_data(model, doss, HOSTS)
TRACKER = poll_tracker.section()   # poll tracker (evolução das chances pelos snapshots)

def nm(t): return PT.get(t, ["", t])[1]
def fl(t): return PT.get(t, ["", t])[0]
MO = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]

# ---------- standings parcial (qualquer nº de jogos) ----------
def standings():
    res = {r["match"]: r for r in (st.get("results", {}) or {}).get("group", []) or []}
    fxs = sorted(fx["group"], key=lambda x: x["kickoff_brt"])  # ordem cronológica p/ a forma
    groups = {}
    for f in fxs:
        g = f["group"]; groups.setdefault(g, {})
        for t in (f["home"], f["away"]):
            groups[g].setdefault(t, {"p":0,"w":0,"d":0,"l":0,"gf":0,"ga":0,"pts":0,"form":[]})
    for f in fxs:
        if f["match"] not in res: continue
        r = res[f["match"]]; a, b = f["home"], f["away"]; ga, gb = r["hg"], r["ag"]; g = f["group"]
        A, B = groups[g][a], groups[g][b]
        A["p"]+=1; B["p"]+=1; A["gf"]+=ga; A["ga"]+=gb; B["gf"]+=gb; B["ga"]+=ga
        if ga > gb:   A["w"]+=1; B["l"]+=1; A["pts"]+=3; A["form"].append("W"); B["form"].append("L")
        elif gb > ga: B["w"]+=1; A["l"]+=1; B["pts"]+=3; B["form"].append("W"); A["form"].append("L")
        else:         A["d"]+=1; B["d"]+=1; A["pts"]+=1; B["pts"]+=1; A["form"].append("D"); B["form"].append("D")
    gd = lambda s: s["gf"] - s["ga"]
    tbl = {}
    for g, ts in groups.items():
        tbl[g] = sorted(ts.items(), key=lambda kv: (kv[1]["pts"], gd(kv[1]), kv[1]["gf"], kv[0]), reverse=True)
    return tbl, sum(1 for f in fx["group"] if f["match"] in res)

FORMA_PT = {"W": "vitória", "D": "empate", "L": "derrota"}
def fbadges(form):
    # V/E/D dentro do badge = pista não-cromática p/ daltônicos; a cor segue como reforço.
    cm = {"W": ("var(--win)", "V"), "D": ("var(--draw)", "E"), "L": ("var(--loss)", "D")}
    f5 = form[-5:]
    if not f5: return '<span class=fz>—</span>'
    return "".join(f'<i class="fb fb-{s}" aria-hidden="true" style="background:{cm[s][0]}">{cm[s][1]}</i>' for s in f5)

tbl, nplayed = standings()
gcards = []
if nplayed == 0:
    # Pré-torneio: sem jogos, a tabela é só zeros. Mostra a composição compacta.
    for g in sorted(tbl):
        teams = "".join(dossie.tlink(t, f'<span class=flag>{fl(t)}</span>{nm(t)}', cls="gt") for t, _ in tbl[g])
        gcards.append(f'<div class="tbl pre"><div class=gh>Grupo {g}</div><div class=grp>{teams}</div></div>')
else:
    for g in sorted(tbl):
        rows = ""
        for i, (t, s) in enumerate(tbl[g], 1):
            gdv = s["gf"] - s["ga"]; sg = ("+" if gdv > 0 else ("" if gdv < 0 else "±")) + str(gdv)
            zone = " qz" if i <= 2 else ""
            tcell = dossie.tlink(t, f'<span class=flag>{fl(t)}</span>{nm(t)}', cls="tm")
            flab = ("Forma, do mais antigo ao mais recente: " + ", ".join(FORMA_PT[x] for x in s["form"][-5:])) if s["form"] else "Sem jogos ainda"
            rows += (f'<div class="tr{zone}"><span class=pos>{i}</span>'
                     f'{tcell}'
                     f'<span class=num>{s["p"]}</span><span class=num>{sg}</span>'
                     f'<span class=pts>{s["pts"]}</span>'
                     f'<span class="forma" role="img" aria-label="{flab}">{fbadges(s["form"])}</span></div>')
        gcards.append(f'<div class="tbl"><div class=gh>Grupo {g}</div>'
                      f'<div class=th><span>#</span><span class=l>Seleção</span><span>J</span><span>SG</span><span>Pts</span><span class=l>Forma</span></div>'
                      f'{rows}</div>')
STAND = (f'<div class=pregrid>{"".join(gcards)}</div>' if nplayed == 0 else f'<div class=standgrid>{"".join(gcards)}</div>')
STAND_INTRO = ('<div class=tip>O torneio ainda não começou — abaixo, a composição dos 12 grupos. '
               'Tabelas com pontos, saldo e forma aparecem a partir da estreia (11/jun). <b>Toque num time para o dossiê.</b></div>'
               if nplayed == 0 else
               '<div class=tip>Verde = classificado direto (top 2). Os 8 melhores 3º também avançam — definidos no fim dos grupos. <b>Toque num time para o dossiê.</b></div>')

# ---------- Fase: avanço previsto × real (migrado do antigo Comparativo) ----------
def pct1(p):
    if p > 0.995: return ">99%"
    if 0 < p < 0.005: return "<1%"
    return f"{p*100:.0f}%"
phase = metrics.phase_advance_report(baseline, st, fx)
if phase["ready"]:
    CAPF = 16
    def frow(row):
        adv = row["actual_advanced"]; fcp = row["forecast_advance"]
        ico, cls = ("✓", "ok") if adv else ("✗", "no")
        tcell = dossie.tlink(row["team"], f'{fl(row["team"])} {nm(row["team"])}', cls="ft")
        return (f'<div class=fr><span class="ico {cls}">{ico}</span>{tcell}'
                f'<span class=fbar><i style="width:{fcp*100:.0f}%"></i></span>'
                f'<span class=fpct>{pct1(fcp)}</span></div>')
    _fr = [frow(r) for r in phase["rows"]]
    _rest = (f'<details class=more><summary>ver todas as {len(_fr)} seleções</summary>{"".join(_fr[CAPF:])}</details>'
             if len(_fr) > CAPF else "")
    FASE = ('<div class=tip>Probabilidade de avançar (previsão pré-torneio) × avançou de fato (✓/✗). Toque num time para o dossiê.</div>'
            + "".join(_fr[:CAPF]) + _rest)
else:
    FASE = '<div class=empty>Fecha quando os 72 jogos de grupo terminarem (define quem avançou de fato).</div>'

# ---------- bracket: real (72 grupos) ou esqueleto de slots ----------
def slotlab(s, r):
    if s == "3rd": return "3º " + "/".join(r.get("third_from", []))
    if s.startswith("W"): return "Venc. J" + s[1:]
    return ("1º " if s[0] == "1" else "2º ") + s[1]

rb = bracket.resolve_bracket(st, fx, S)
ko_res = {x["match"]: x for x in (st.get("results", {}) or {}).get("knockout", []) or []}
ROUNDS = [("32-avos", S["r32"]), ("Oitavas", S["r16"]), ("Quartas", S["qf"]),
          ("Semifinais", S["sf"]), ("Final", [S["final"]])]
rblocks = []
for idx, (rname, matches) in enumerate(ROUNDS):
    lines = ""
    for r in sorted(matches, key=lambda x: x["match"]):
        mno = r["match"]
        if rb and mno in rb["matchups"]:
            a, b = rb["matchups"][mno]
            wa = ko_res.get(mno, {}).get("winner")
            la = f'<b>{fl(a)} {nm(a)}</b>' if wa == a else f'{fl(a)} {nm(a)}'
            lb = f'<b>{nm(b)} {fl(b)}</b>' if wa == b else f'{nm(b)} {fl(b)}'
            sc = ""
            if mno in ko_res:
                k = ko_res[mno]; tag = {"pens":" (pên)","et":" (pror)"}.get(k.get("decided_by"), "")
                sc = f'<span class=sc>{k["hg"]}–{k["ag"]}{tag}</span>'
            lines += f'<div class=brow><span class=bt>{la}</span>{sc}<span class="bt r">{lb}</span></div>'
        else:
            lines += (f'<div class="brow skel"><span class=bt>{slotlab(r["home"], r)}</span>'
                      f'<span class=bx>×</span><span class="bt r">{slotlab(r["away"], r)}</span></div>')
    rblocks.append(shell.accordion(rname, lines, is_open=(idx == 0 and bool(rb)), hint="ver"))
BRACKET = "".join(rblocks)
bracket_note = ("chave real, conforme os jogos acontecem" if rb else
                "a chave fica definida quando os 72 jogos de grupo terminarem — por ora, os confrontos por vaga")

# ---------- PREVISÕES do modelo (acordeão; real é o palco) ----------
PRED_GROUPS = shell.accordion("Previsões do modelo · 72 jogos de grupo (V/E/D · xG · placar)",
                              predcards.group_grid(model, S, HOSTS), hint="ver previsões")
PRED_KO = shell.accordion("Confrontos mais prováveis do mata-mata (modelo)",
                          predcards.ko_blocks(model, S, HOSTS), hint="ver previsões")

asof = st.get("as_of") or ""
asof_fmt = f"{int(asof[8:10])}/{MO[int(asof[5:7])-1]}" if len(asof) == 10 else asof
status = (f"fase de grupos · {nplayed}/72 jogos" if 0 < nplayed < 72 else
          ("grupos encerrados · mata-mata" if nplayed >= 72 else "antes da estreia (11/jun)"))
OUT = os.environ.get("OUT_FILE") or f"{DIST}/copa2026_resultados.html"

HTML = f"""<!DOCTYPE html><html lang=pt-BR><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>Resultados · Ficha do Jogo</title>
{shell.HEAD}{shell.meta("Resultados — Ficha do Jogo · Copa 2026", "Tabelas por grupo e a chave do mata-mata da Copa 2026, com avanço previsto × real conforme os jogos acontecem.", "resultados")}
<style>
{theme.PALETTE}
{shell.CSS}
{predcards.CSS}
{dossie.CSS}
{TRACKER["css"]}
*{{box-sizing:border-box}}body{{margin:0;--maxw:1000px;background:var(--bg);color:var(--ink);font-family:-apple-system,system-ui,"Segoe UI",Roboto,sans-serif;line-height:1.4;font-size:14px}}
.wrap{{max-width:1000px;margin:0 auto;padding:14px}}
h1{{font-size:22px;font-weight:800;letter-spacing:-.02em;margin:0}}
.sub{{font-size:12px;color:var(--mut);margin:3px 0 12px}}
.sec{{font-size:11px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--ac);margin:24px 0 8px}}
.tip{{font-size:12px;color:var(--mut);margin:-2px 0 10px}}
.standgrid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:10px}}
.pregrid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px}}
.tbl{{background:var(--card);border:1px solid var(--line);border-radius:11px;overflow:hidden}}
.gh{{font-size:12px;font-weight:800;letter-spacing:.06em;color:var(--ac);padding:9px 12px 0}}
.grp{{display:grid;grid-template-columns:1fr;gap:2px;padding:6px 12px 10px}}
.gt{{display:flex;align-items:center;font-size:12.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.th,.tr{{display:grid;grid-template-columns:18px 1fr 22px 34px 28px 64px;gap:7px;align-items:center;padding:7px 12px}}
.th{{font-size:10px;text-transform:uppercase;letter-spacing:.05em;color:var(--mut);font-weight:700;border-bottom:1px solid var(--line)}}
.th span,.tr span{{text-align:center}}.th .l,.tr .tm{{text-align:left}}
.tr{{border-bottom:1px solid var(--line2)}}.tr:last-child{{border-bottom:0}}
.pos{{color:var(--mut);font-variant-numeric:tabular-nums;font-size:12px}}
.tm{{font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}.flag{{margin-right:6px}}
.num{{font-variant-numeric:tabular-nums;font-size:12px;color:var(--mut)}}
.pts{{font-variant-numeric:tabular-nums;font-weight:800;color:var(--ink)}}
.forma{{display:flex;gap:3px;justify-content:flex-start}}.fb{{width:15px;height:15px;border-radius:3px;display:inline-flex;align-items:center;justify-content:center;font-size:10px;font-weight:800;font-style:normal;color:var(--badge-ink)}}.fz{{color:var(--mut)}}
.tr.qz{{box-shadow:inset 3px 0 0 var(--ac);background:var(--acsoft)}}
.zlg{{font-size:11px;color:var(--mut);margin:8px 2px 0;display:flex;align-items:center;gap:6px}}
.zd{{width:10px;height:10px;border-radius:3px;background:var(--ac)}}
.brow{{display:flex;align-items:center;gap:8px;padding:7px 0;border-top:1px solid var(--line2);font-size:13px}}
.bt{{flex:1}}.bt.r{{text-align:right}}.bt b{{font-weight:800}}
.brow.skel{{color:var(--mut)}}.bx{{color:var(--mut)}}
.sc{{font-variant-numeric:tabular-nums;font-weight:700;background:var(--box);border:1px solid var(--line);border-radius:6px;padding:1px 7px;white-space:nowrap}}
.fr{{display:grid;grid-template-columns:24px 1fr 90px 38px;gap:8px;align-items:center;padding:7px 4px;border-bottom:1px solid var(--line2)}}
.ft{{font-weight:600;font-size:13px}}.fbar{{height:7px;background:var(--box);border-radius:4px;overflow:hidden}}.fbar i{{display:block;height:100%;background:var(--win)}}
.fpct{{font-variant-numeric:tabular-nums;font-size:12px;color:var(--mut);text-align:right}}
.ico{{width:18px;height:18px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:11px;font-weight:800}}
.ico.ok{{background:rgba(34,197,94,.15);color:var(--win)}}.ico.no{{background:rgba(239,68,68,.15);color:var(--loss)}}
.empty{{color:var(--mut);font-size:13px;padding:12px;background:var(--card);border-radius:10px}}
details.more{{margin:4px 0 2px}}details.more>summary{{cursor:pointer;color:var(--ac);font-weight:700;font-size:12px;padding:8px 4px;list-style:none}}details.more>summary::-webkit-details-marker{{display:none}}details.more>summary::before{{content:"▸ "}}details.more[open]>summary::before{{content:"▾ "}}
.foot{{color:var(--mut);font-size:11px;margin-top:22px;border-top:1px solid var(--line);padding-top:10px}}
</style></head><body data-page="resultados">{shell.topbar("res")}{flags.SPRITE}
<main class=wrap id=main tabindex=-1>
<div class=hero><h1>Resultados</h1><div class=sub>tabelas e chave · {status}{(' · atualizado '+asof_fmt) if asof_fmt else ''}</div></div>

<h2 class=sec data-scene="classificacao">Classificação por grupo</h2>
{STAND_INTRO}
{STAND}
{'<div class=zlg><i class=zd></i> top 2 do grupo · forma: <i class="fb fb-W" aria-hidden="true" style="background:var(--win)">V</i>vitória <i class="fb fb-D" aria-hidden="true" style="background:var(--draw)">E</i>empate <i class="fb fb-L" aria-hidden="true" style="background:var(--loss)">D</i>derrota</div>' if nplayed else ''}
{PRED_GROUPS}

<h2 class=sec data-scene="fase">Fase · avanço previsto × real</h2>
{FASE}

<h2 class=sec data-scene="tracker">Acompanhamento · evolução das chances</h2>
<div class=tip>Como uma pesquisa: a probabilidade de cada seleção a cada atualização do modelo.</div>
{TRACKER["html"]}

<h2 class=sec data-scene="chave">Mata-mata · chave</h2>
<div class=tip>{bracket_note}.</div>
{BRACKET}
{PRED_KO}

<footer class=foot>Só leitura — resultados vêm de data/live/state.json e o site é regerado. Previsões do modelo proprietário (não garantias). Desempate de grupo: pontos · saldo · gols pró (aproxima o critério FIFA). · {shell.CREDIT}</footer>
</main>{dossie.DRAWER}{dossie.js(DATA)}{TRACKER["js"]}{shell.JS}</body></html>"""

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w").write(HTML)
print("resultados(hub):", len(HTML), "chars | grupos:", len(tbl), "| jogos:", nplayed,
      "| bracket real:", bool(rb), "| .acc:", HTML.count('class="acc"'),
      "| <script>:", HTML.count("<script"), "| http:", HTML.count("http://") + HTML.count("https://"))
