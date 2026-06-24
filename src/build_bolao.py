#!/usr/bin/env python3
"""
Página de Placares previstos / comparativo de modelos (Frente 2) -> dist/copa2026_bolao.html
Linguagem visual "B · esportivo condensado". Estático, ZERO dependência, mobile-first, dark+light.

Mostra, por jogo futuro, o PLACAR RECOMENDADO (maior valor esperado) de 4 MODELOS, com um seletor
de modelo em destaque (toggle) + uma linha que compara os 4 lado a lado em cada jogo. Default
(JS off) = baseline. Não há dado pessoal. Reusa bolao (recomendador EV), bracket (chave KO),
state (jogos já ocorridos), pt. Jogos já disputados: previsão trancada do snapshot baseline.
"""
import glob, json, os, sys
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bolao, bracket, theme, shell, dossie, flags, state as ST
from pt import PT

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "data"); DIST = os.path.join(ROOT, "dist")
model = json.load(open(f"{BASE}/wc2026_results.json"))
doss = json.load(open(f"{BASE}/wc2026_dossiers.json"))
fx = json.load(open(f"{BASE}/fixtures.json"))
S = json.load(open(f"{BASE}/worldcup2026_structure.json"))
st = ST.ManualFileSource().load()
errs = ST.validate_state(st, fx)
if errs:
    print("ESTADO INVÁLIDO — abortando:", errs); sys.exit(1)
HOSTS = {"United States", "Mexico", "Canada"}
DATA = dossie.build_data(model, doss, HOSTS)

SNAP_DIR = os.path.join(ROOT, "data", "snapshots")
_snap_cache = {}

def _snap_for(game_date):
    """Snapshot com maior generated <= game_date — forecast antes desse jogo."""
    if game_date in _snap_cache:
        return _snap_cache[game_date]
    best, best_gen = None, None
    for p in sorted(glob.glob(os.path.join(SNAP_DIR, "*.json"))):
        try:
            d = json.load(open(p))
            g = d.get("meta", {}).get("generated", "")
            if g <= game_date and (best_gen is None or g > best_gen):
                best, best_gen = d, g
        except Exception:
            pass
    _snap_cache[game_date] = best
    return best

def nm(t): return PT.get(t, ["", t])[1]
def fl(t): return PT.get(t, ["", t])[0]
WD = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]; MO = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]
def fday(iso): d = datetime.strptime(iso, "%Y-%m-%dT%H:%M"); return f"{WD[d.weekday()]} {d.day:02d}/{MO[d.month-1]}"
def ftime(iso): d = datetime.strptime(iso, "%Y-%m-%dT%H:%M"); return f"{d.hour:02d}:{d.minute:02d}"
def dkey(iso): return iso[:10]

def w_d_l(h, a, ko, m=None):
    m = m or model
    la, lb = bolao.lams_for(m, h, a)
    d = bolao.score_dist_ko(la, lb) if ko else bolao.score_dist_group(la, lb)
    ph = sum(p for (i, j), p in d.items() if i > j); pd = sum(p for (i, j), p in d.items() if i == j)
    return ph, pd, max(0.0, 1 - ph - pd), la, lb

def _load_model(mid):
    p = f"{BASE}/models/{mid}.json"
    return json.load(open(p)) if os.path.exists(p) else None

# 4 modelos comparados por jogo (id, rótulo curto, json). baseline = wc2026_results.json (publicado);
# os outros vêm de data/models/ (gerados por run_models.py). Mantém só os que carregaram.
MODELS = [m for m in (
    ("baseline", "Baseline", model),
    ("dynamic_k40", "Aprende", _load_model("dynamic_k40")),
    ("w_mkt85", "Mais merc.", _load_model("w_mkt85")),
    ("market_only", "Odds", _load_model("market_only")),
) if m[2]]
# código PÚBLICO opaco por modelo (m0,m1…) usado no DOM/CSS/JS — o id interno (mid) NÃO vai
# ao HTML servido (vazaria K/pesos, ex.: dynamic_k40 -> K=40). mid fica só p/ ler data/models/.
PUB = {mid: f"m{i}" for i, (mid, _l, _j) in enumerate(MODELS)}
DEFMODEL = PUB[MODELS[0][0]] if MODELS else "m0"

def card_multi(h, a, ko, kickoff=None, hero=False):
    """Card de jogo futuro: placar recomendado de CADA modelo (o ativo aparece via html[data-model])
    + linha de comparação com os 4 lado a lado. Estático-primeiro; o CSS troca o modelo em foco."""
    when = f'{fday(kickoff)} · {ftime(kickoff)}' if kickoff else ('mata-mata' if ko else '')
    cls = "card hero" if hero else "card"
    th = dossie.tlink(h, f'{fl(h)} {nm(h)}', cls="team")
    ta = dossie.tlink(a, f'{nm(a)} {fl(a)}', cls="team r")
    pvs = barss = mlines = chips = ""
    for mid, lab, mj in MODELS:
        pub = PUB[mid]  # DOM usa o código opaco, nunca o id interno
        rec = bolao.recommend(mj, h, a, ko=ko)
        ph, pd, pa, la, lb = w_d_l(h, a, ko, mj)
        sx, sy = rec["ev_pick"]; bx, by = rec["bold_pick"]
        gole = f' · goleada {rec["goleada"]*100:.0f}%' if rec["goleada"] >= 0.25 else ''
        pvs += (f'<span class=pv data-m="{pub}" data-r=safe>{sx}–{sy}</span>'
                f'<span class=pv data-m="{pub}" data-r=bold>{bx}–{by}</span>')
        barss += (f'<div class=bars data-m="{pub}"><i style="width:{ph*100:.0f}%;background:var(--win)"></i>'
                  f'<i style="width:{pd*100:.0f}%;background:var(--draw)"></i>'
                  f'<i style="width:{pa*100:.0f}%;background:var(--loss)"></i></div>')
        mlines += (f'<div class=mline data-m="{pub}"><span>{when} · xG {la:.1f}–{lb:.1f}{gole}</span>'
                   f'<span class=ms><span data-r=safe><b>{rec["ev"]}</b> pts esp.</span>'
                   f'<span data-r=bold>crava <b>{rec["bold_prob"]*100:.0f}%</b></span></span></div>')
        chips += (f'<span class=ch data-c="{pub}">{lab} '
                  f'<b><span data-r=safe>{sx}–{sy}</span><span data-r=bold>{bx}–{by}</span></b></span>')
    return (f'<div class="{cls}"><div class=row>{th}<span class=px>{pvs}</span>{ta}</div>'
            f'{barss}{mlines}<div class=cmp>{chips}</div></div>')

def card_result(h, a, kickoff, snap, actual):
    """Card de jogo já disputado: placar REAL + a previsão (baseline) anterior ao jogo + acertou/errou,
    nas duas leituras (Seguro/Ousado, alternáveis) — migra o 'previsto × real' do antigo Comparativo.
    Baseline = único com snapshot pré-jogo honesto."""
    rec = bolao.recommend(snap, h, a, ko=False)
    ax, ay = actual
    when = fday(kickoff) if kickoff else ''
    th = dossie.tlink(h, f'{fl(h)} {nm(h)}', cls="team")
    ta = dossie.tlink(a, f'{nm(a)} {fl(a)}', cls="team r")
    def _r(pick, rd):
        sx, sy = pick; pts = bolao.dacopa_points((sx, sy), actual, ko=False)
        ico, cls = ("✓", "ok") if [sx, sy] == [ax, ay] else (("~", "warn") if pts > 0 else ("✗", "no"))
        lbl = "Seguro" if rd == "safe" else "Ousado"
        return (f'<span class=resl data-r={rd}><span>{when} · {lbl} previu <b>{sx}–{sy}</b></span>'
                f'<span class=hit><span class="ico {cls}">{ico}</span> {pts} pts</span></span>')
    return (f'<div class="card locked"><div class=row>{th}<span class=px>{ax}–{ay}</span>{ta}</div>'
            f'{_r(rec["ev_pick"], "safe")}{_r(rec["bold_pick"], "bold")}</div>')

done = {r["match"] for r in st["results"]["group"]} | {r["match"] for r in st["results"]["knockout"]}

# Próximos (herói = o próximo; resto por dia, colapsável)
ups = sorted([f for f in fx["group"] if f["match"] not in done], key=lambda f: f["kickoff_brt"])
HERO = card_multi(ups[0]["home"], ups[0]["away"], False, ups[0]["kickoff_brt"], hero=True) if ups else ""
by_date = {}
for f in ups[1:]:
    by_date.setdefault(dkey(f["kickoff_brt"]), []).append(f)
blocks = []
for idx, dk in enumerate(sorted(by_date)):
    games = by_date[dk]; n = len(games)
    cards = "".join(card_multi(g["home"], g["away"], False, g["kickoff_brt"]) for g in games)
    blocks.append(shell.accordion(f'{fday(games[0]["kickoff_brt"])} · {n} jogo{"s" if n != 1 else ""}',
                                  f'<div class="cardgrid">{cards}</div>', is_open=(idx < 2)))
PROX = (HERO + "".join(blocks)) if ups else '<div class=empty>Sem jogos de grupo futuros.</div>'

# KO (quando a chave resolve)
KOSEC = ""
rb = bracket.resolve_bracket(st, fx, S)
if rb:
    kc = [card_multi(*rb["matchups"][r["match"]], True) for r in (S["r32"]+S["r16"]+S["qf"]+S["sf"]+[S["final"]])
          if r["match"] not in done and r["match"] in rb["matchups"]]
    if kc:
        KOSEC = f'<h2 class=sec>Mata-mata · placar no fim da prorrogação</h2><div class="cardgrid">{"".join(kc)}</div>'

asof = st.get("as_of") or ""
asof_fmt = f"{int(asof[8:10])}/{MO[int(asof[5:7])-1]}" if len(asof) == 10 else asof

# Jogados: placar REAL × previsão (baseline) anterior ao jogo — previsto × real (migrado do Comparativo)
played_fx = sorted([f for f in fx["group"] if f["match"] in done],
                   key=lambda f: f["kickoff_brt"], reverse=True)
actual_by_match = {r["match"]: (r["hg"], r["ag"]) for r in st["results"]["group"]}
JOGSEC = ""
if played_fx:
    pcards = []
    for f in played_fx:
        s = _snap_for(f["date"]); act = actual_by_match.get(f["match"])
        if s and act:
            pcards.append(card_result(f["home"], f["away"], f["kickoff_brt"], s, act))
    if pcards:
        JOGSEC = (f'<h2 class=sec>Já jogados · previsto × real</h2>'
                  f'<div class=tip>Placar real e o que o baseline previu antes do jogo. ✓ cravou · ~ acertou em parte · ✗ zerou.</div>'
                  f'<div class="cardgrid">{"".join(pcards)}</div>')

tip = ('<div class=tip>O placar de <b>4 modelos</b> por jogo, em duas leituras (<b>Seguro</b> = maior valor esperado · '
       '<b>Ousado</b> = mais provável, mostra empates) — troque modelo e leitura acima; a linha de baixo compara os quatro. '
       'Qual modelo <b>acerta</b> mais? veja <a href="./modelos">Modelos</a>. <b>Toque num time para o dossiê.</b></div>')
BODY = f'<h2 class=sec>Próximos · placar previsto por modelo</h2>{tip}{PROX}{KOSEC}{JOGSEC}'

# seletor de modelo (toggle) + seletores CSS gerados a partir de MODELS
mbtns = "".join(
    f'<button type=button class=mbtn data-model="{PUB[mid]}" aria-pressed="{"true" if PUB[mid]==DEFMODEL else "false"}" '
    f'onclick="setModel(\'{PUB[mid]}\')">{lab}</button>' for mid, lab, _ in MODELS)
_hide = ",".join(f'html[data-model="{PUB[mid]}"] [data-m]:not([data-m="{PUB[mid]}"])' for mid, _, _ in MODELS)
_chip = ",".join(f'html[data-model="{PUB[mid]}"] .ch[data-c="{PUB[mid]}"]' for mid, _, _ in MODELS)

HTML = f"""<!DOCTYPE html><html lang=pt-BR data-model="{DEFMODEL}"><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>Placares · Ficha do Jogo</title>
{shell.HEAD}{shell.meta("Placares — Ficha do Jogo · Copa 2026", "Placar previsto de 4 modelos por jogo na Copa 2026, em duas leituras (Seguro/Ousado), com previsto × real dos jogos já disputados.", "placares")}
<script>(function(){{try{{var m=localStorage.getItem("fdj-model");if(m)document.documentElement.setAttribute("data-model",m);if(localStorage.getItem("fdj-bold")==="1")document.documentElement.setAttribute("data-bold","1")}}catch(e){{}}}})()</script>
<style>
{theme.PALETTE}
{shell.CSS}
{dossie.CSS}
*{{box-sizing:border-box}}body{{margin:0;--maxw:820px;background:var(--bg);color:var(--ink);font-family:-apple-system,system-ui,"Segoe UI",Roboto,sans-serif;line-height:1.35;font-size:14px}}
.wrap{{max-width:820px;margin:0 auto;padding:14px}}
h1{{font-size:22px;font-weight:800;letter-spacing:-.02em;margin:0}}
.sub{{font-size:12px;color:var(--mut);margin:3px 0 12px}}
.cardgrid{{display:grid;grid-template-columns:1fr;gap:6px}}
@media(min-width:680px){{.cardgrid{{grid-template-columns:1fr 1fr}}}}
.sec{{font-size:11px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--ac);margin:20px 0 8px}}
.tip{{font-size:12px;color:var(--mut);margin:-2px 0 8px}}
.card{{background:var(--card);border-radius:10px;padding:10px 12px;margin:6px 0}}
.card.hero{{background:var(--card2);border:1px solid var(--ac);box-shadow:inset 0 0 0 1px var(--acsoft)}}
.card.locked{{opacity:.65;border:1px solid var(--line)}}
.row{{display:flex;align-items:center;gap:8px}}
.team{{flex:1;font-weight:700}}.team.r{{text-align:right}}
.px{{font-weight:800;font-variant-numeric:tabular-nums;background:var(--box);border:1px solid var(--ac);color:var(--ac);border-radius:7px;padding:3px 11px;white-space:nowrap}}
.hero .px{{font-size:26px}}.card:not(.hero) .px{{font-size:18px}}
.bars{{display:flex;height:6px;border-radius:3px;overflow:hidden;margin:8px 0 5px;background:var(--box)}}
.bars i{{display:block;height:100%}}
.mline{{font-size:11px;color:var(--mut);display:flex;justify-content:space-between;gap:8px}}
.mline b{{color:var(--ink)}}
/* jogos já disputados: previsto × real (migrado do Comparativo) */
.resl{{font-size:11.5px;color:var(--mut);display:flex;justify-content:space-between;gap:8px;margin-top:7px}}.resl b{{color:var(--ink);font-variant-numeric:tabular-nums}}
.hit{{display:inline-flex;align-items:center;gap:5px;font-variant-numeric:tabular-nums;color:var(--ink);font-weight:700}}
.ico{{width:17px;height:17px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:10px;font-weight:800}}
.ico.ok{{background:rgba(34,197,94,.15);color:var(--win)}}.ico.warn{{background:rgba(234,179,8,.15);color:var(--draw)}}.ico.no{{background:rgba(239,68,68,.15);color:var(--loss)}}
/* comparação dos 4 modelos por jogo (sempre visível); o ativo ganha o anel accent */
.cmp{{display:flex;flex-wrap:wrap;gap:5px;margin-top:8px}}
.ch{{background:var(--box);border:1px solid var(--line);border-radius:6px;padding:2px 8px;font-size:11px;color:var(--mut)}}
.ch b{{color:var(--ink);font-variant-numeric:tabular-nums;font-weight:700}}
{_chip}{{border-color:var(--ac);color:var(--ink);background:var(--acsoft)}}
/* seletor de modelo: mostra só o placar/barras/xG do modelo em foco (data-m); resto escondido */
{_hide}{{display:none}}
/* leitura ativa (Seguro/Ousado): esconde a não-ativa em pv, métrica e chips */
html:not([data-bold]) [data-r=bold],html[data-bold] [data-r=safe]{{display:none}}
.modebar{{display:flex;align-items:center;gap:8px;flex-wrap:wrap;position:sticky;top:var(--tbh,92px);z-index:30;background:var(--bg);margin:0 -14px 12px;padding:8px 14px;border-bottom:1px solid var(--line)}}
.mblbl{{font-size:10px;text-transform:uppercase;letter-spacing:.11em;font-weight:800;color:var(--mut)}}
.mseg{{display:inline-flex;border:1px solid var(--line);border-radius:8px;overflow:hidden;flex-wrap:wrap}}
.mbtn{{appearance:none;border:0;background:var(--card);color:var(--mut);font:inherit;font-size:12.5px;font-weight:700;padding:6px 13px;cursor:pointer}}
.mbtn+.mbtn{{border-left:1px solid var(--line)}}
.mbtn[aria-pressed=true]{{background:var(--acsoft);color:var(--ink);box-shadow:inset 0 -2px 0 var(--ac)}}
.mbhint{{font-size:11px;color:var(--mut)}}
@media(max-width:600px){{.mbhint{{display:none}}}}  /* sticky compacto no mobile — a dica fica no glossário */
.empty{{color:var(--mut);font-size:13px;padding:12px;background:var(--card);border-radius:10px}}
details.gl{{margin-top:18px;font-size:12px;color:var(--mut)}}details.gl summary{{cursor:pointer;color:var(--ac);font-weight:700}}
.gl dl{{margin:8px 0 0}}.gl dt{{color:var(--ink);font-weight:700;margin-top:6px}}.gl a{{color:var(--ac)}}
.foot{{color:var(--mut);font-size:11px;margin-top:18px;border-top:1px solid var(--line);padding-top:10px}}
</style></head><body data-page="bolao">{shell.topbar("bol")}{flags.SPRITE}
<main class=wrap id=main tabindex=-1>
<div class=hero><h1>Placar previsto</h1><div class=sub>placar de 4 modelos por jogo, em 2 leituras (Seguro/Ousado) — comparados em cada jogo · atualizado {asof_fmt}</div></div>
<div class=modebar role=group aria-label="Modelo e leitura"><span class=mblbl>Modelo</span>
<span class=mseg>{mbtns}</span>
<span class=mblbl style="margin-left:8px">Leitura</span>
<span class=mseg><button type=button class=mbtn data-mode=safe aria-pressed=true onclick="setBold(0)">Seguro</button><button type=button class=mbtn data-mode=bold aria-pressed=false onclick="setBold(1)">Ousado</button></span>
<span class=mbhint>Seguro = maior valor esperado · Ousado = placar mais provável (mostra empates)</span></div>
{BODY}

<details class=gl><summary>glossário & método</summary><dl>
<dt>Seguro</dt><dd>placar de <b>maior valor esperado</b> (sob a tabela de pontuação de placar exato) — a leitura que mais soma pontos no longo prazo. <b>Por construção</b>, quase nunca empate ou goleada — por isso o Seguro de todos os modelos fica parecido.</dd>
<dt>Ousado</dt><dd>placar <b>mais provável</b> (modal): crava o exato ou zera. Em jogos equilibrados costuma ser <b>empate</b> — é a leitura que mostra a cara realista de cada modelo.</dd>
<dt>qual modelo é o melhor?</dt><dd>o placar é uma leitura grosseira (o Seguro fica parecido entre modelos). Pra saber qual de fato <b>acerta mais</b>, veja a <b>calibração</b> (Brier/log-loss) em <a href="./modelos">Modelos</a> — a comparação rigorosa.</dd>
<dt>os 4 modelos</dt><dd><b>Baseline</b> = ensemble 45/35/20 (publicado) · <b>Aprende</b> = força que reage aos jogos (Elo dinâmico) · <b>Mais merc.</b> = peso maior no mercado (85/15) · <b>Odds</b> = consenso de odds (já contém Opta). Calibração comparada dos modelos em <a href="./modelos">Modelos</a>.</dd>
<dt>pts esp.</dt><dd>pontos esperados do placar recomendado — valor médio de pontos, ponderando todos os resultados possíveis.</dd>
<dt>goleada</dt><dd>probabilidade de diferença de 3+ gols. Mostrada quando ≥25% (só informativo; goleadas são improváveis demais p/ palpitar).</dd>
<dt>xG</dt><dd>gols esperados de cada lado, segundo o modelo em destaque.</dd>
<dt>barra V/E/D</dt><dd>probabilidade de vitória (verde) / empate (âmbar) / derrota (vermelho).</dd>
<dt>como o placar é estimado</dt><dd>distribuição de gols com correção de <b>Dixon-Coles</b> (1997) e leve sobredispersão na cauda — corrige o viés do Poisson independente, que subestima 0-0/1-1. Parâmetros de literatura, não ajustados aos nossos dados.</dd>
</dl></details>

<footer class=foot>Só leitura — placares previstos por modelo, regerados a cada atualização. Estimativas, não garantias. · {shell.CREDIT}</footer>
</main>{dossie.DRAWER}{dossie.js(DATA)}
<script>
function setModel(id){{document.documentElement.setAttribute("data-model",id);
try{{localStorage.setItem("fdj-model",id)}}catch(e){{}}paintModel()}}
function paintModel(){{var id=document.documentElement.getAttribute("data-model")||"{DEFMODEL}";
document.querySelectorAll(".mbtn[data-model]").forEach(function(x){{x.setAttribute("aria-pressed",x.dataset.model===id?"true":"false")}});}}
function setBold(on){{var r=document.documentElement;if(on)r.setAttribute("data-bold","1");else r.removeAttribute("data-bold");
try{{localStorage.setItem("fdj-bold",on?"1":"0")}}catch(e){{}}paintBold()}}
function paintBold(){{var on=document.documentElement.hasAttribute("data-bold");
document.querySelectorAll(".mbtn[data-mode]").forEach(function(x){{x.setAttribute("aria-pressed",((x.dataset.mode==="bold")===on)?"true":"false")}});}}
paintModel();paintBold();
// barra Modelo/Leitura fixa: alinha o 'top' sticky logo abaixo da topbar (fallback estático no CSS p/ JS off)
(function(){{var tb=document.querySelector(".topbar");function s(){{if(tb)document.documentElement.style.setProperty("--tbh",tb.offsetHeight+"px")}}s();addEventListener("resize",s,{{passive:true}})}})();
</script>{shell.JS}</body></html>"""

os.makedirs(DIST, exist_ok=True)
out = f"{DIST}/copa2026_bolao.html"
open(out, "w").write(HTML)
print("placares:", len(HTML), "chars | próximos:", len(ups), "| modelos:", len(MODELS),
      "| <script>:", HTML.count("<script"), "| http:", HTML.count("http://") + HTML.count("https://"))
