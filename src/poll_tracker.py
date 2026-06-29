#!/usr/bin/env python3
"""Poll tracker — gráfico de linhas (estilo pesquisa eleitoral) da evolução das chances de cada
seleção ao longo das atualizações da Copa. Vai na página Resultados (build_resultados.py).

Fonte de dados: data/snapshots/*.json (1 por atualização; já existe). Métrica alternável:
Avançar (advance) · Título (champion) · Oitavas (r16). Eixo X = datas dos snapshots.

CONTRATO DURO (igual ao resto do site):
- SVG inline GERADO EM PYTHON, ZERO dependência (nada de Chart.js/D3/CDN). Bandeiras via <use
  href="#fl-xx"> (fragmento; o SPRITE de flags.py já entra 1x na página). SEM xmlns/xlink/http.
- ESTÁTICO-PRIMEIRO: render_svg() em Python desenha o conjunto default (Brasil + top-5 título) já
  no HTML — funciona com JS off. O JS (js()) re-renderiza ao trocar métrica/seleção (≤6 linhas).
  ⚠️ A matemática de render do JS ESPELHA render_svg(): manter as duas em sincronia.
- Lápide: quando a métrica plotada ZERA tendo sido > LIVE_EPS antes, a linha encerra e planta-se
  uma lápide (bandeira + sigla) no ponto da eliminação. Brasil é sempre fixo (mesmo eliminado).

Determinístico (sem aleatório; iteração ordenada)."""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flags
from pt import PT

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP_DIR = os.environ.get("SNAP_DIR") or os.path.join(ROOT, "data", "snapshots")

# métricas alternáveis: (chave no snapshot, rótulo, teto fixo do eixo Y ou None=adaptativo)
METRICS = [("advance", "Avançar", 100.0), ("champion", "Título", None), ("r16", "Oitavas", 100.0)]
ML_LABEL = {k: lab for k, lab, _ in METRICS}
LIVE_EPS = 0.05          # % mínimo p/ considerar que a seleção "esteve viva" naquela métrica
MO = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

# geometria do viewBox (proporção ~mobile; escala via width:100%, max-width no CSS)
W, H = 360.0, 226.0
ML, MR, MT, MB = 27.0, 54.0, 12.0, 22.0   # margens: Y-labels · chips de ponta · topo · datas
X0, X1, Y0, Y1 = ML, W - MR, MT, H - MB

# paleta de linhas (5 + Brasil); valores reais ficam em CSS por tema. Brasil = âmbar icônico.
LN = ["--ln1", "--ln2", "--ln3", "--ln4", "--ln5"]
BR = "--ln-br"


def nm(t): return PT.get(t, ["", t])[1]


# ─────────────────────────── dados ───────────────────────────
def load_series(snap_dir=None):
    """Lê todos os snapshots ordenados. Retorna (dates, series, last_champ).
    series[team][metric] = [valor% por snapshot]; last_champ[team] = título% no último (p/ ordenar)."""
    snap_dir = snap_dir or SNAP_DIR
    snaps = []
    for p in sorted(glob.glob(os.path.join(snap_dir, "*.json"))):
        try:
            d = json.load(open(p))
            snaps.append((d["meta"]["generated"], d))
        except Exception:
            pass
    snaps.sort(key=lambda x: x[0])
    dates = [g for g, _ in snaps]
    teams = set()
    for _, d in snaps:
        teams |= set(d.get("teams", {}))
    series, last_champ = {}, {}
    for t in sorted(teams):
        series[t] = {}
        for mk, _, _ in METRICS:
            series[t][mk] = [round((d.get("teams", {}).get(t, {}).get(mk) or 0) * 100, 2) for _, d in snaps]
        last_champ[t] = series[t]["champion"][-1] if dates else 0.0
    return dates, series, last_champ


def default_selection(last_champ):
    """Brasil (fixo) + top-5 por título no último snapshot."""
    top = [t for t in sorted(last_champ, key=lambda x: -last_champ[x]) if t != "Brazil"][:5]
    return ["Brazil"] + top


def _nice_max(v):
    """Teto 'redondo' acima de v (p/ a escala adaptativa do Título)."""
    if v <= 5: return 5.0
    for step in (10, 20, 25, 30, 40, 50, 60, 80, 100):
        if v <= step: return float(step)
    return 100.0


def maxy_for(series, metric, sel=None):
    fixed = dict((k, mx) for k, _, mx in METRICS)[metric]
    if fixed: return fixed
    pool = sel or list(series)
    peak = max((max(series[t][metric]) for t in pool if t in series), default=0)
    return _nice_max(peak)


# ─────────────────────────── render (FONTE DA VERDADE; o JS espelha) ───────────────────────────
def _x(i, n): return (X0 + X1) / 2 if n <= 1 else X0 + (X1 - X0) * i / (n - 1)
def _y(v, maxy): return Y1 - (Y1 - Y0) * (max(0.0, min(v, maxy)) / maxy)


def _ticks(maxy):
    step = next(s for s in (1, 2, 5, 10, 20, 25, 50) if maxy / s <= 6)
    t, v = [], 0.0
    while v <= maxy + 1e-9:
        t.append(round(v, 2)); v += step
    return t


def _life(vals):
    """(idx_morte, esteve_vivo): idx do 1º snapshot onde zerou após ter sido > LIVE_EPS; senão None."""
    seen = False
    for i, v in enumerate(vals):
        if v > LIVE_EPS: seen = True
        elif seen and v <= 0.0:
            return i, True
    return None, seen


def _color(team, sel):
    if team == "Brazil": return BR
    others = [t for t in sel if t != "Brazil"]
    return LN[others.index(team) % len(LN)] if team in others else LN[0]


def _tombstone(x, y, iso, sig, color):
    """Lápide SVG (pedra dessaturada + bandeira + sigla) plantada em (x,y) na base."""
    return (f'<g transform="translate({x:.1f} {y:.1f})" class="tomb">'
            f'<path d="M-8,4 L-8,-5 Q-8,-12 0,-12 Q8,-12 8,-5 L8,4 Z" class="ts"/>'
            f'<line x1="-9" y1="4" x2="9" y2="4" class="tg"/>'
            f'<use href="#fl-{iso}" x="-5.5" y="-10.5" width="11" height="8.25" class="tf"/>'
            f'<text x="0" y="2.4" class="tsig" fill="var({color})">{sig}</text></g>')


def render_svg(dates, series, sel, metric):
    n = len(dates)
    maxy = maxy_for(series, metric, sel)
    P = []
    # grid + rótulos Y
    for tv in _ticks(maxy):
        yy = _y(tv, maxy)
        P.append(f'<line x1="{X0}" y1="{yy:.1f}" x2="{X1}" y2="{yy:.1f}" class="grid"/>')
        P.append(f'<text x="{X0-3}" y="{yy+2.5:.1f}" class="ylab">{tv:g}%</text>')
    # rótulos X (datas; rareia se muitos)
    every = max(1, (n + 5) // 6)
    for i, g in enumerate(dates):
        if i % every == 0 or i == n - 1:
            dd = f"{int(g[8:10])}/{MO[int(g[5:7])-1]}" if len(g) == 10 else g
            P.append(f'<text x="{_x(i,n):.1f}" y="{H-8:.1f}" class="xlab">{dd}</text>')
    # linhas (Brasil por último = em cima)
    order = sorted(sel, key=lambda t: t == "Brazil")
    tips = []  # (y, html) p/ dodge dos chips de ponta
    for t in order:
        if t not in series: continue
        vals = series[t][metric]; col = _color(t, sel)
        die, _ = _life(vals)
        end = die if die is not None else n - 1
        pts = " ".join(f"{_x(i,n):.1f},{_y(vals[i],maxy):.1f}" for i in range(end + 1))
        cls = "ln br" if t == "Brazil" else "ln"
        P.append(f'<polyline points="{pts}" class="{cls}" style="stroke:var({col})"/>')
        for i in range(end + 1):
            P.append(f'<circle cx="{_x(i,n):.1f}" cy="{_y(vals[i],maxy):.1f}" r="1.6" class="dot" style="fill:var({col})"/>')
        iso, sig = flags.ISO[t], flags.code3(t)
        if die is not None:
            P.append(_tombstone(_x(die, n), Y1, iso, sig, col))
        else:
            ty = _y(vals[end], maxy)
            tips.append((ty, t, iso, sig, col))
    # chips de ponta com dodge vertical (evita sobreposição)
    tips.sort()
    last = -99
    for ty, t, iso, sig, col in tips:
        cy = max(ty, last + 9)
        last = cy
        xx = X1 + 3
        P.append(f'<g transform="translate({xx:.1f} {cy:.1f})" class="tip">'
                 f'<use href="#fl-{iso}" x="0" y="-4" width="11" height="8.25"/>'
                 f'<text x="13" y="2.4" class="tsig" fill="var({col})">{sig}</text></g>')
    return f'<svg class="ptk-svg" viewBox="0 0 {W:g} {H:g}" role="img" aria-label="Evolução de probabilidades">{"".join(P)}</svg>'


# ─────────────────────────── seletor + alternador ───────────────────────────
def _selector(series, sel, last_champ):
    chips = []
    for t in sorted(series, key=lambda x: (x != "Brazil", -last_champ.get(x, 0), nm(x))):
        on = t in sel
        lock = t == "Brazil"
        cls = "tchip" + (" on" if on else "") + (" lock" if lock else "")
        col = _color(t, sel) if on else "--mut"
        chips.append(f'<button type="button" class="{cls}" data-team="{t}" data-iso="{flags.ISO[t]}" '
                     f'style="--c:var({col})" aria-pressed="{"true" if on else "false"}"'
                     f'{" disabled" if lock else ""}>'
                     f'<svg class="fi" aria-hidden="true"><use href="#fl-{flags.ISO[t]}"/></svg>'
                     f'<span>{nm(t)}</span>{"<i class=lk>fixo</i>" if lock else ""}</button>')
    return (f'<div class="tk-pick"><div class="tk-pick-h"><b>Seleções</b> '
            f'<span class="tk-count"></span> · Brasil é fixo</div>'
            f'<div class="tk-chips">{"".join(chips)}</div></div>')


def _switch(metric):
    btns = "".join(
        f'<button type="button" class="mbtn" data-metric="{k}" '
        f'aria-pressed="{"true" if k==metric else "false"}">{lab}</button>'
        for k, lab, _ in METRICS)
    return f'<div class="tk-switch" role="group" aria-label="Métrica"><span class=mseg>{btns}</span></div>'


# ─────────────────────────── CSS ───────────────────────────
CSS = r"""
/* ===== poll tracker ===== */
:root{--ln-br:#ffd23f;--ln1:#56a8e6;--ln2:#f4978e;--ln3:#c4a3ff;--ln4:#5fd0c5;--ln5:#f5a3c7}
:root[data-theme=light]{--ln-br:#c98a00;--ln1:#1f6fb2;--ln2:#c1452f;--ln3:#6f42c1;--ln4:#0a8a7d;--ln5:#b03a78}
.ptk{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 12px 6px}
.ptk-svg{width:100%;height:auto;max-width:620px;display:block;margin:0 auto;font-family:inherit;overflow:visible}
.ptk-svg .grid{stroke:var(--line);stroke-width:.5}
.ptk-svg .ylab{fill:var(--mut);font-size:9px;text-anchor:end}
.ptk-svg .xlab{fill:var(--mut);font-size:7px;text-anchor:middle}
.ptk-svg .ln{fill:none;stroke-width:1.6;stroke-linejoin:round;stroke-linecap:round}
.ptk-svg .ln.br{stroke-width:2.6;filter:drop-shadow(0 0 1px var(--ln-br))}
.ptk-svg .dot{opacity:.9}
.ptk-svg .tip text,.ptk-svg .tsig{font-size:7px;font-weight:800;dominant-baseline:middle}
.ptk-svg .tomb .ts{fill:var(--mut);opacity:.45}
.ptk-svg .tomb .tg{stroke:var(--mut);opacity:.45;stroke-width:1}
.ptk-svg .tomb .tf{opacity:.85}
.tk-bar{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin:2px 0 8px}
.tk-switch .mseg{display:inline-flex;border:1px solid var(--line);border-radius:8px;overflow:hidden}
.tk-switch .mbtn{appearance:none;border:0;background:var(--card);color:var(--mut);font:inherit;font-size:12px;font-weight:700;padding:5px 12px;cursor:pointer}
.tk-switch .mbtn+.mbtn{border-left:1px solid var(--line)}
.tk-switch .mbtn[aria-pressed=true]{background:var(--acsoft);color:var(--ink);box-shadow:inset 0 -2px 0 var(--ac)}
.tk-pick{margin:10px 0 4px}
.tk-pick-h{font-size:11px;color:var(--mut);margin-bottom:6px}
.tk-pick-h b{color:var(--ink)}
.tk-count{color:var(--ac);font-weight:700}
.tk-chips{display:flex;flex-wrap:wrap;gap:5px}
.tchip{display:inline-flex;align-items:center;gap:5px;border:1px solid var(--line);background:var(--card);
  color:var(--mut);border-radius:20px;padding:3px 10px 3px 7px;font-size:12px;font-weight:600;cursor:pointer}
.tchip .fi{width:1.2em;height:.9em}
.tchip.on{color:var(--ink);border-color:var(--c);box-shadow:inset 0 0 0 1px var(--c)}
.tchip.on .fi{box-shadow:0 0 0 1px var(--c)}
.tchip.lock{cursor:default;opacity:.95}
.tchip .lk{font-style:normal;font-size:9px;color:var(--ac);text-transform:uppercase;letter-spacing:.06em}
.tchip:disabled{opacity:1}
.tk-note{font-size:11px;color:var(--mut);margin-top:8px;line-height:1.5}
"""


# ─────────────────────────── JS (espelha render_svg) ───────────────────────────
def js(dates, series, sel, metric, last_champ):
    payload = {"dates": dates, "series": series, "sel": sel, "metric": metric,
               "iso": {t: flags.ISO[t] for t in series}, "sig": {t: flags.code3(t) for t in series},
               "metrics": [[k, lab, (mx if mx else 0)] for k, lab, mx in METRICS],
               "geom": {"W": W, "H": H, "X0": X0, "X1": X1, "Y0": Y0, "Y1": Y1},
               "ln": LN, "br": BR, "eps": LIVE_EPS}
    return "<script>\n(function(){\nvar PT=" + json.dumps(payload, ensure_ascii=False) + ";\n" + _JS_BODY + "\n})();\n</script>"


_JS_BODY = r"""
var G=PT.geom, MO=["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"];
var sel=PT.sel.slice(), metric=PT.metric;
var FIXED={}; PT.metrics.forEach(function(m){FIXED[m[0]]=m[2];});
function niceMax(v){if(v<=5)return 5;var s=[10,20,25,30,40,50,60,80,100];for(var i=0;i<s.length;i++)if(v<=s[i])return s[i];return 100;}
function maxyFor(m){if(FIXED[m])return FIXED[m];var pk=0;sel.forEach(function(t){var a=PT.series[t]&&PT.series[t][m]||[];a.forEach(function(v){if(v>pk)pk=v;});});return niceMax(pk);}
function xx(i,n){return n<=1?(G.X0+G.X1)/2:G.X0+(G.X1-G.X0)*i/(n-1);}
function yy(v,my){v=Math.max(0,Math.min(v,my));return G.Y1-(G.Y1-G.Y0)*(v/my);}
function life(a){var seen=false;for(var i=0;i<a.length;i++){if(a[i]>PT.eps)seen=true;else if(seen&&a[i]<=0)return i;}return -1;}
function color(t){if(t==="Brazil")return PT.br;var o=sel.filter(function(x){return x!=="Brazil";});var k=o.indexOf(t);return PT.ln[(k<0?0:k)%PT.ln.length];}
function esc(s){return String(s);}
function render(){
 var n=PT.dates.length, my=maxyFor(metric), S=[];
 var step=[1,2,5,10,20,25,50].filter(function(s){return my/s<=6;})[0]||50;
 for(var tv=0;tv<=my+1e-9;tv+=step){var y=yy(tv,my);
   S.push('<line x1="'+G.X0+'" y1="'+y.toFixed(1)+'" x2="'+G.X1+'" y2="'+y.toFixed(1)+'" class="grid"/>');
   S.push('<text x="'+(G.X0-3)+'" y="'+(y+2.5).toFixed(1)+'" class="ylab">'+(+tv.toFixed(2))+'%</text>');}
 var every=Math.max(1,Math.floor((n+5)/6));
 for(var i=0;i<n;i++){if(i%every===0||i===n-1){var g=PT.dates[i];var dd=g.length===10?(parseInt(g.slice(8,10),10)+'/'+MO[parseInt(g.slice(5,7),10)-1]):g;
   S.push('<text x="'+xx(i,n).toFixed(1)+'" y="'+(G.H-8).toFixed(1)+'" class="xlab">'+dd+'</text>');}}
 var order=sel.slice().sort(function(a,b){return (a==="Brazil")-(b==="Brazil");});
 var tips=[];
 order.forEach(function(t){
   var a=PT.series[t]&&PT.series[t][metric]; if(!a)return; var col=color(t), die=life(a), end=die<0?n-1:die, pts=[];
   for(var i=0;i<=end;i++)pts.push(xx(i,n).toFixed(1)+','+yy(a[i],my).toFixed(1));
   S.push('<polyline points="'+pts.join(' ')+'" class="ln'+(t==="Brazil"?' br':'')+'" style="stroke:var('+col+')"/>');
   for(var j=0;j<=end;j++)S.push('<circle cx="'+xx(j,n).toFixed(1)+'" cy="'+yy(a[j],my).toFixed(1)+'" r="1.6" class="dot" style="fill:var('+col+')"/>');
   var iso=PT.iso[t], sig=PT.sig[t];
   if(die>=0){var x=xx(die,n),y=G.Y1;
     S.push('<g transform="translate('+x.toFixed(1)+' '+y.toFixed(1)+')" class="tomb"><path d="M-8,4 L-8,-5 Q-8,-12 0,-12 Q8,-12 8,-5 L8,4 Z" class="ts"/><line x1="-9" y1="4" x2="9" y2="4" class="tg"/><use href="#fl-'+iso+'" x="-5.5" y="-10.5" width="11" height="8.25" class="tf"/><text x="0" y="2.4" class="tsig" fill="var('+col+')">'+sig+'</text></g>');
   } else tips.push([yy(a[end],my),t,iso,sig,col]);
 });
 tips.sort(function(p,q){return p[0]-q[0];}); var last=-99;
 tips.forEach(function(z){var cy=Math.max(z[0],last+9);last=cy;
   S.push('<g transform="translate('+(G.X1+3).toFixed(1)+' '+cy.toFixed(1)+')" class="tip"><use href="#fl-'+z[2]+'" x="0" y="-4" width="11" height="8.25"/><text x="13" y="2.4" class="tsig" fill="var('+z[4]+')">'+z[3]+'</text></g>');});
 var svg=document.querySelector('#ptk .ptk-svg');
 if(svg)svg.innerHTML=S.join('');
 // pinta chips + contador
 document.querySelectorAll('#ptk .tchip').forEach(function(b){var t=b.dataset.team,on=sel.indexOf(t)>=0;
   b.classList.toggle('on',on);b.setAttribute('aria-pressed',on?'true':'false');
   b.style.setProperty('--c', on?'var('+color(t)+')':'var(--mut)');});
 var c=document.querySelector('#ptk .tk-count'); if(c)c.textContent=(sel.length)+'/6';
 document.querySelectorAll('#ptk .mbtn').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.metric===metric?'true':'false');});
 try{localStorage.setItem('fdj-tk-sel',JSON.stringify(sel));localStorage.setItem('fdj-tk-metric',metric);}catch(e){}
}
// restaura preferência salva
try{var ss=JSON.parse(localStorage.getItem('fdj-tk-sel')||'null');if(ss&&ss.length&&ss.indexOf('Brazil')>=0)sel=ss;
var sm=localStorage.getItem('fdj-tk-metric');if(sm&&FIXED.hasOwnProperty(sm))metric=sm;}catch(e){}
document.addEventListener('click',function(e){
 var mb=e.target.closest&&e.target.closest('#ptk .mbtn'); if(mb){metric=mb.dataset.metric;render();return;}
 var ch=e.target.closest&&e.target.closest('#ptk .tchip'); if(ch&&!ch.disabled){var t=ch.dataset.team,k=sel.indexOf(t);
   if(k>=0){if(t!=="Brazil")sel.splice(k,1);} else {if(sel.length>=6){return;} sel.push(t);} render();}
});
render();
"""


def section(model=None, state=None):
    """Bloco HTML completo do tracker (chamado por build_resultados.py): switch + svg + seletor + JS."""
    dates, series, last_champ = load_series()
    if not dates:
        return {"html": '<div class="ptk"><div class=tk-note>Sem histórico de atualizações ainda — '
                'o acompanhamento aparece a partir do 2º forecast.</div></div>', "css": CSS, "js": ""}
    # default = Título: o conjunto default são os favoritos, que "Avançar" deixaria amontoados no
    # topo (~99%); Título os separa (23/13/12/...). O usuário alterna p/ Avançar com 1 clique.
    metric = "champion"
    sel = default_selection(last_champ)
    html = (f'<div class="ptk" id="ptk">'
            f'<div class="tk-bar">{_switch(metric)}'
            f'<span class="tk-count">{len(sel)}/6</span></div>'
            f'{render_svg(dates, series, sel, metric)}'
            f'{_selector(series, sel, last_champ)}'
            f'<div class=tk-note>Cada linha é a probabilidade estimada ao longo das atualizações '
            f'(como uma pesquisa). Escolha até 5 seleções + Brasil (fixo). Quando uma seleção é '
            f'eliminada, a linha vira <b>lápide</b> 🪦. Toque numa seleção para incluir/tirar.</div>'
            f'</div>')
    return {"html": html, "css": CSS, "js": js(dates, series, sel, metric, last_champ)}


if __name__ == "__main__":
    dates, series, last_champ = load_series()
    print(f"snapshots: {len(dates)} {dates}")
    print(f"times: {len(series)} · default sel: {default_selection(last_champ)}")
    for m, lab, _ in METRICS:
        print(f"  maxy[{lab}] = {maxy_for(series, m, default_selection(last_champ))}")
    sec = section()
    # HTML de teste: dark (default) + light, lado a lado, p/ screenshot
    sprite = flags.SPRITE
    shell_tokens = """
:root{--bg:#0f1b13;--card:#18271d;--card2:#1d3024;--line:#25382b;--line2:#1f2e23;--ink:#f1ece0;--mut:#9fae9d;--ac:#f3b03c;--acsoft:#2a3a2c;--box:#13211896}
:root[data-theme=light]{--bg:#f5f2e6;--card:#fffef9;--card2:#fbf8ee;--line:#e3dcc5;--line2:#ece6d3;--ink:#1c2620;--mut:#5f6b5c;--ac:#1a7a43;--acsoft:#e8efe0;--box:#f0ece0}
body{margin:0;font-family:-apple-system,system-ui,sans-serif;background:var(--bg);color:var(--ink)}
.col{padding:16px}.fi{display:inline-block;width:1.34em;height:1em;vertical-align:-.14em;border-radius:2px;overflow:hidden}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:0}
.col.l{background:#f5f2e6}
"""
    html_light = sec["html"].replace('id="ptk"', 'id="ptk2"')   # fora da f-string: backslash em f-string só vale em 3.12+
    out = (f'<!DOCTYPE html><html><head><meta charset=utf-8>'
           f'<meta name=viewport content="width=device-width,initial-scale=1"><style>{shell_tokens}{sec["css"]}</style></head>'
           f'<body>{sprite}<div class=grid2>'
           f'<div class=col><h3 style="font:700 13px sans-serif">DARK</h3>{sec["html"]}</div>'
           f'<div class="col l"><div data-theme=light><h3 style="font:700 13px sans-serif">LIGHT</h3>{html_light}</div></div>'
           f'</div>{sec["js"]}</body></html>')
    test_path = "/tmp/_tracker_test.html"   # /tmp p/ NUNCA poluir dist/ (deploy)
    open(test_path, "w").write(out)
    print(f"teste visual: {test_path} ({len(out)} chars · <script>: {out.count('<script')} · http: {out.count('http://')+out.count('https://')})")
