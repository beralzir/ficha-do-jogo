#!/usr/bin/env python3
"""Build the single-file dashboard — STATIC-FIRST. v2: + jogos de grupo (1X2/xG/placar),
mata-mata provável (matchups das 50k sims), calculadora de confronto, gols esperados."""
import json
import os, sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE=os.path.join(ROOT,"data")
DIST=os.path.join(ROOT,"dist")
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import snapshot as _snapshot
import awards as _awards
import shell
import flags
res=json.load(open(f"{BASE}/wc2026_results.json"))
doss=json.load(open(f"{BASE}/wc2026_dossiers.json"))
S=json.load(open(f"{BASE}/worldcup2026_structure.json"))
teams=res["teams"]; meta=res["meta"]
HA=meta["HA"]; GOAL_DIV=meta["GOAL_DIV"]; MUG=meta["MU"]
HOSTS={"United States","Mexico","Canada"}

PT={
"Spain":["\U0001F1EA\U0001F1F8","Espanha"],"France":["\U0001F1EB\U0001F1F7","França"],
"Argentina":["\U0001F1E6\U0001F1F7","Argentina"],"England":["\U0001F3F4\U000E0067\U000E0062\U000E0065\U000E006E\U000E0067\U000E007F","Inglaterra"],
"Portugal":["\U0001F1F5\U0001F1F9","Portugal"],"Brazil":["\U0001F1E7\U0001F1F7","Brasil"],
"Germany":["\U0001F1E9\U0001F1EA","Alemanha"],"Netherlands":["\U0001F1F3\U0001F1F1","Holanda"],
"Belgium":["\U0001F1E7\U0001F1EA","Bélgica"],"Norway":["\U0001F1F3\U0001F1F4","Noruega"],
"Colombia":["\U0001F1E8\U0001F1F4","Colômbia"],"Japan":["\U0001F1EF\U0001F1F5","Japão"],
"Morocco":["\U0001F1F2\U0001F1E6","Marrocos"],"United States":["\U0001F1FA\U0001F1F8","Estados Unidos"],
"Uruguay":["\U0001F1FA\U0001F1FE","Uruguai"],"Mexico":["\U0001F1F2\U0001F1FD","México"],
"Switzerland":["\U0001F1E8\U0001F1ED","Suíça"],"Croatia":["\U0001F1ED\U0001F1F7","Croácia"],
"Turkey":["\U0001F1F9\U0001F1F7","Turquia"],"Ecuador":["\U0001F1EA\U0001F1E8","Equador"],
"Senegal":["\U0001F1F8\U0001F1F3","Senegal"],"Sweden":["\U0001F1F8\U0001F1EA","Suécia"],
"Austria":["\U0001F1E6\U0001F1F9","Áustria"],"Canada":["\U0001F1E8\U0001F1E6","Canadá"],
"Paraguay":["\U0001F1F5\U0001F1FE","Paraguai"],"Ivory Coast":["\U0001F1E8\U0001F1EE","Costa do Marfim"],
"Egypt":["\U0001F1EA\U0001F1EC","Egito"],"Algeria":["\U0001F1E9\U0001F1FF","Argélia"],
"Scotland":["\U0001F3F4\U000E0067\U000E0062\U000E0073\U000E0063\U000E0074\U000E007F","Escócia"],"Czechia":["\U0001F1E8\U0001F1FF","Chéquia"],
"Bosnia and Herzegovina":["\U0001F1E7\U0001F1E6","Bósnia"],"Ghana":["\U0001F1EC\U0001F1ED","Gana"],
"South Korea":["\U0001F1F0\U0001F1F7","Coreia do Sul"],"Iran":["\U0001F1EE\U0001F1F7","Irã"],
"Tunisia":["\U0001F1F9\U0001F1F3","Tunísia"],"Australia":["\U0001F1E6\U0001F1FA","Austrália"],
"DR Congo":["\U0001F1E8\U0001F1E9","RD Congo"],"Cape Verde":["\U0001F1E8\U0001F1FB","Cabo Verde"],
"Iraq":["\U0001F1EE\U0001F1F6","Iraque"],"Jordan":["\U0001F1EF\U0001F1F4","Jordânia"],
"New Zealand":["\U0001F1F3\U0001F1FF","Nova Zelândia"],"Panama":["\U0001F1F5\U0001F1E6","Panamá"],
"Qatar":["\U0001F1F6\U0001F1E6","Catar"],"Saudi Arabia":["\U0001F1F8\U0001F1E6","Arábia Saudita"],
"South Africa":["\U0001F1FF\U0001F1E6","África do Sul"],"Uzbekistan":["\U0001F1FA\U0001F1FF","Uzbequistão"],
"Curacao":["\U0001F1E8\U0001F1FC","Curaçao"],"Haiti":["\U0001F1ED\U0001F1F9","Haiti"],
}
for _t in PT:  # bandeira emoji -> SVG inline (flags.py); Windows não tem fonte de bandeira de país
    PT[_t][0]=flags.ref(_t)
def _wl(s):  # white-label: esconde nome de método citado em texto curado (dossiês)
    return s.replace("Elo alto","rating alto").replace("Elo/inexperiência","rating/inexperiência").replace("Elo","rating") if isinstance(s,str) else s
DATA={}
for t,x in teams.items():
    d={k:_wl(v) for k,v in doss.get(t,{}).items()}
    DATA[t]={"pt":PT[t][1],"flag":PT[t][0],"group":x["group"],
        "gw":x["group_win"],"adv":x["advance"],"r16":x["r16"],"qf":x["qf"],
        "sf":x["sf"],"fin":x["final"],"ch":x["champion"],
        "mkt":x["mkt"],"opta":x["opta"],"cons":x["consensus"],
        "R":x["R_cal"],"host":(t in HOSTS),
        "gf":x["g_for"],"ga":x["g_ag"],"mp":x["mp"],
        "tier":d.get("tier",""),"coach":d.get("coach",""),"stars":d.get("stars",""),
        "inj":d.get("inj",""),"form":d.get("form",""),"hist":d.get("hist",""),
        "edge":d.get("edge",""),"risk":d.get("risk",""),"read":d.get("read","")}

# motor analítico de partida + helpers (pcb/fx) migraram p/ predcards.py (dedup Fase 3 → página Resultados).
# O dashboard mantém só a calculadora (que reimplementa o motor em JS).
_MO=["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]
def _ptdate(iso):  # "2026-06-10" -> "10/jun/2026"
    y,mo,d=iso.split("-"); return f"{int(d):02d}/{_MO[int(mo)-1]}/{y}"

# jogos de grupo (72) e mata-mata provável migraram p/ predcards.group_grid / predcards.ko_blocks
# (página Resultados, dedup Fase 3). O dashboard foca em probabilidades + calculadora + metodologia.

# ---------- pre-rendered bits from v1 ----------
TIERCLS={"Favorito ao título":"t0","Candidato real":"t1","Azarão":"t2","Aposta externa":"t3","Completando o chaveamento":"t4"}
KENT=[(.93,"Quase certo","#16a34a"),(.75,"Muito provável","#22c55e"),(.55,"Provável","#84cc16"),
      (.45,"Chances iguais","#eab308"),(.25,"Pouco provável","#f97316"),(.07,"Improvável","#ef4444"),(0,"Remoto","#991b1b")]
def kent(p):
    for k in KENT:
        if p>=k[0]: return k
    return KENT[-1]
def pc(p): return f"{p*100:.0f}%" if p>=0.10 else (f"{p*100:.1f}%" if p>=0.01 else f"{p*100:.2f}%")
def heat(p):
    a=0.10+0.82*(p**0.5)
    # AA: célula de prob alta = verde-menta + tinta escura (--heat-ink); faint = verde padrão + texto (--tx).
    if a>=0.52:
        return f"background:rgba(110,231,160,{a:.3f});color:var(--heat-ink)"
    return f"background:rgba(34,197,94,{a:.3f})"
STAGES=[("gw","Vencer grupo"),("adv","Avançar (32)"),("r16","Oitavas"),("qf","Quartas"),("sf","Semifinal"),("fin","Final"),("ch","Título")]
byCh=sorted(DATA,key=lambda n:DATA[n]["ch"],reverse=True)
def clk(n):  # atributos p/ tornar o elemento clicável -> dossiê (acessível por teclado), igual às outras páginas
    nm=n.replace("\\","").replace("'","\\'")
    return ('''onclick="openDrawer('%s')" tabindex="0" role="button" '''
            '''onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();openDrawer('%s')}"'''%(nm,nm))
rows=[]
for n in byCh:
    d=DATA[n]
    cells="".join(f'<span class="mc" style="{heat(d[k])}">{pc(d[k])}</span>' for k,_ in STAGES)
    rows.append(f'<div class="mrow" {clk(n)}>'
        f'<div class="mtop"><span class="flag">{d["flag"]}</span><span class="mname">{d["pt"]}</span>'
        f'<span class="grp">{d["group"]}</span><span class="tier {TIERCLS.get(d["tier"],"t4")}">{d["tier"]}</span>'
        f'<span class="mch">{pc(d["ch"])}</span></div><div class="mcells">{cells}</div></div>')
ROWS="".join(rows)
# KPIs em destaque: os 3 maiores favoritos + Brasil mesmo fora do top 3 (tarefa 2); cards clicáveis → dossiê (tarefa 1).
_kpi=byCh[:3]+["Brazil"] if "Brazil" not in byCh[:3] else byCh[:4]
KPIS="".join(f'<div class="kpi" {clk(n)}><div class="n">{DATA[n]["flag"]} {DATA[n]["pt"]}</div>'
    f'<div class="v">{pc(DATA[n]["ch"])}</div>'
    f'<div class="d">{kent(DATA[n]["ch"])[1]} · título</div></div>' for n in _kpi)
KENTROWS="".join(f'<tr><td style="font-weight:700"><span class="kentsw" style="background:{KENT[i][2]}" aria-hidden="true"></span>{lab}</td><td class="kb">{rng}</td></tr>'
    for i,(rng,lab) in enumerate([("≥ 93%","Quase certo"),("75–93%","Muito provável"),("55–75%","Provável"),
    ("45–55%","Chances iguais"),("25–45%","Pouco provável"),("7–25%","Improvável"),("< 7%","Remoto")]))
top=byCh[:16]; mx=max(max(DATA[n]["ch"],DATA[n]["mkt"],DATA[n]["opta"]) for n in top)
def bar(v,color):
    w=max(0.8,v/mx*100)
    return f'<div class="cb"><i style="width:{w:.1f}%;background:{color}"></i><b>{pc(v)}</b></div>'
CHART="".join(f'<div class="crow" {clk(n)}><div class="cn">{DATA[n]["flag"]} {DATA[n]["pt"]}</div>'
    f'<div class="cbars">{bar(DATA[n]["ch"],"#22c55e")}{bar(DATA[n]["mkt"],"#38bdf8")}{bar(DATA[n]["opta"],"#a78bfa")}</div></div>' for n in top)
# ---------- "o que mudou" vs snapshot anterior (condicional: some sem histórico) ----------
MUDOU=""; MUDOUNAV=""
_prev=_snapshot.find_previous(meta["generated"])
if _prev:
    _pt=_prev["teams"]
    _dch=sorted(((teams[t]["champion"]-_pt[t]["champion"],t) for t in sorted(teams) if t in _pt),reverse=True)
    _up=[(d,t) for d,t in _dch if d>=0.005][:4]
    _dn=[(d,t) for d,t in reversed(_dch) if d<=-0.005][:4]
    _dadv=sorted(((teams[t]["advance"]-_pt[t]["advance"],t) for t in sorted(teams) if t in _pt),key=lambda x:(abs(x[0]),x[1]),reverse=True)
    _adv=[(d,t) for d,t in _dadv if abs(d)>=0.02][:3]
    def _mvrow(d,t):
        col="#22c55e" if d>0 else "#ef4444"; arr="▲" if d>0 else "▼"
        return (f'<div class="mvrow" {clk(t)}><span class="flag">{DATA[t]["flag"]}</span>'
                f'<span class="mvname">{DATA[t]["pt"]}</span>'
                f'<span class="mvvals">{pc(_pt[t]["champion"])} → {pc(teams[t]["champion"])}</span>'
                f'<span class="mvd" style="color:{col}">{arr} {abs(d)*100:.1f}pp</span></div>')
    _rows="".join(_mvrow(d,t) for d,t in _up)+"".join(_mvrow(d,t) for d,t in _dn)
    if not _rows:
        _rows='<div class="kb" style="padding:4px 0">Sem movimento relevante (≥0,5pp) na probabilidade de título entre os dois forecasts.</div>'
    _advtx=""
    if _adv:
        _advtx='<div class="mvsec">Avançar de grupo: '+" · ".join(
            f'{DATA[t]["flag"]} {DATA[t]["pt"]} {"+" if d>0 else "−"}{abs(d)*100:.0f}pp' for d,t in _adv)+'</div>'
    MUDOU=(f'<h2 id="mudou">O que mudou — vs forecast de {_ptdate(_prev["meta"]["generated"])}</h2>'
           f'<div class="card" style="padding:10px 14px"><div class="mvlist">{_rows}</div>{_advtx}'
           f'<div class="kb" style="margin-top:8px">Probabilidade de título, antes → agora; variação em pontos percentuais (pp) entre os dois forecasts.</div></div>')
    MUDOUNAV='<a href="#mudou">O que mudou</a>'

# ---------- prêmios individuais (Chuteira/Luva de Ouro — favoritos do mercado) ----------
PREMIOS=""; PREMIOSNAV=""
_awd=_awards.load(teams48=set(DATA))
if _awd:
    def _awcard(title,emoji,rows,topn):
        mx=rows[0]["p"]; lines=[]
        for r in rows[:topn]:
            w=max(2.0,r["p"]/mx*100)
            lines.append(
                f'<div class="awrow"><span class="flag">{DATA[r["team"]]["flag"]}</span>'
                f'<span class="awn"><b>{r["player"]}</b> <span class="kb">{DATA[r["team"]]["pt"]}</span></span>'
                f'<span class="awb"><i style="width:{w:.1f}%"></i></span>'
                f'<span class="awp">{pc(r["p"])}</span></div>')
        resto=sum(r["p"] for r in rows[topn:])
        if resto>0:
            lines.append(f'<div class="kb" style="margin-top:6px">outros listados pelas odds: {pc(resto)}</div>')
        return f'<div class="card gmcard"><div class="gmh"><span aria-hidden="true">{emoji}</span> {title}</div>{"".join(lines)}</div>'
    PREMIOS=('<h2 id="premios">Prêmios individuais — favoritos pelas odds</h2>'
             '<div class="kb" style="margin-bottom:8px">Artilheiro (Chuteira de Ouro) e melhor goleiro (Luva de Ouro): '
             'probabilidade implícita das odds com a margem removida, normalizada entre os candidatos listados '
             '(coleta 9/jun). O motor é nível-seleção — estes números vêm das odds, não da simulação.</div>'
             '<div class="gmgrid">'
             +_awcard("Chuteira de Ouro · artilheiro","👟",_awd["golden_boot"],10)
             +_awcard("Luva de Ouro · goleiro","🧤",_awd["golden_glove"],8)
             +'</div>')
    PREMIOSNAV='<a href="#premios">Prêmios</a>'

GOPTS="".join(f'<option value="{g}">Grupo {g}</option>' for g in sorted({d["group"] for d in DATA.values()}))
TOPTS="".join(f'<option value="{t}">{t}</option>' for t in TIERCLS)
CALCOPTS="".join(f'<option value="{n}">{DATA[n]["pt"]}</option>' for n in sorted(DATA,key=lambda x:DATA[x]["pt"]))

HTML=r"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ficha do Jogo — Copa do Mundo 2026 · probabilidades por fase e por jogo</title>
__SHELLHEAD__
<style>
__PALETTE__
*{box-sizing:border-box}body{margin:0;--maxw:1280px;background:var(--bg);color:var(--tx);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;font-size:14px;line-height:1.45}
a{color:var(--ac);text-decoration:none}.wrap{max-width:1280px;margin:0 auto;padding:20px}
h1{font-size:23px;margin:0 0 2px}h2{font-size:17px;margin:26px 0 10px;border-left:3px solid var(--ac);padding-left:9px}
h3.koh{font-size:14px;color:var(--mut);margin:18px 0 8px;text-transform:uppercase;letter-spacing:.5px}
.sub{color:var(--mut);font-size:13px;margin-bottom:14px}
/* nav/pílulas antigos removidos — shell.py (topbar/abas/âncoras/selos) cuida da navegação */
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:14px 0}
.kpi{background:linear-gradient(160deg,var(--kpia),var(--kpib));border:1px solid var(--line);border-radius:12px;padding:12px 14px}
.kpi .n{font-size:13px;color:var(--mut)}.kpi .v{font-size:24px;font-weight:700;margin-top:2px}
.kpi .d{font-size:12px;margin-top:2px;color:var(--mut)}
/* destaques clicáveis -> dossiê (tarefa 1: igualar o Dashboard às outras páginas) */
.kpi,.crow,.mvrow{cursor:pointer}
.kpi:hover{border-color:var(--ac)}
.crow:hover .cn,.mvrow:hover .mvname{color:var(--ac)}
.kpi:focus-visible,.crow:focus-visible,.mvrow:focus-visible,.mrow:focus-visible{outline:2px solid var(--ac);outline-offset:2px}
.controls{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:10px 0}
input,select{background:var(--card);border:1px solid var(--line);color:var(--tx);border-radius:8px;padding:7px 10px;font-size:13px}
input{min-width:210px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:6px}
.calc-hero{border-color:var(--ac);box-shadow:inset 0 0 0 1px var(--acsoft);padding:16px}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
th,td{padding:7px 8px;text-align:center;white-space:nowrap}
th{position:sticky;top:0;background:var(--box);color:var(--mut);font-weight:600;font-size:11.5px;text-transform:uppercase;letter-spacing:.3px;cursor:pointer;user-select:none;border-bottom:1px solid var(--line)}
th.l,td.l{text-align:left}th:hover{color:var(--tx)}
tbody tr{border-bottom:1px solid var(--rowline);cursor:pointer}tbody tr:hover{background:var(--rowhov)}
td.team{font-weight:600}.flag{margin-right:7px}
.grp{display:inline-block;width:20px;height:20px;line-height:20px;text-align:center;border-radius:6px;background:var(--chipbg);color:var(--chiptx);font-size:11px;font-weight:700}
.tier{font-size:10.5px;padding:2px 7px;border-radius:6px;font-weight:600}
__TIERS__
.cell{border-radius:6px;font-weight:600;font-size:12.5px}
.mhead{display:grid;grid-template-columns:repeat(7,1fr);gap:3px;padding:0 10px;font-size:9.5px;color:var(--mut);text-transform:uppercase;letter-spacing:.03em;text-align:center;margin-bottom:4px}
.mlist{background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden}
.mrow{padding:9px 10px;border-bottom:1px solid var(--rowline);cursor:pointer}.mrow:last-child{border-bottom:0}.mrow:hover{background:var(--rowhov)}
.mtop{display:flex;align-items:center;gap:7px;margin-bottom:6px}.mname{font-weight:700;flex:1}
.mch{font-weight:800;font-variant-numeric:tabular-nums;color:var(--ac);font-size:15px}
.mcells{display:grid;grid-template-columns:repeat(7,1fr);gap:3px}
.mc{border-radius:5px;font-size:11px;font-weight:600;text-align:center;padding:4px 0;font-variant-numeric:tabular-nums;color:var(--tx)}
.crow{display:flex;align-items:center;gap:10px;margin:7px 0}
.cn{width:185px;text-align:right;font-size:13px;font-weight:600;flex:none}
.cbars{flex:1;display:flex;flex-direction:column;gap:2px}
.cb{display:flex;align-items:center;gap:7px;height:13px}
.cb i{display:block;height:9px;border-radius:3px}.cb b{font-size:10.5px;color:var(--mut);font-weight:600}
.legend{display:flex;gap:14px;margin:4px 0 10px;font-size:12px;color:var(--mut)}
.legend i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:5px;vertical-align:-1px}
.mvrow{display:flex;align-items:center;gap:8px;padding:6px 2px;border-bottom:1px solid var(--rowline);font-size:13px}
.mvlist .mvrow:last-child{border-bottom:0}
.mvname{flex:1;font-weight:600}
.mvvals{color:var(--mut);font-variant-numeric:tabular-nums;font-size:12.5px}
.mvd{font-weight:700;font-variant-numeric:tabular-nums;min-width:62px;text-align:right;font-size:12.5px}
.mvsec{font-size:11.5px;color:var(--mut);margin-top:6px;border-top:1px solid var(--rowline);padding-top:8px}
.awrow{display:flex;align-items:center;gap:7px;padding:5px 0;border-bottom:1px solid var(--rowline);font-size:12.5px}
.awrow:last-of-type{border-bottom:0}
.awn{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.awb{width:86px;height:7px;background:var(--box);border-radius:4px;overflow:hidden;flex:none}
.awb i{display:block;height:100%;background:#22c55e}
.awp{width:44px;text-align:right;font-variant-numeric:tabular-nums;font-weight:700;font-size:12px}
details.secfold{background:none;border:0;border-radius:0;padding:0;margin:10px 0}
details.secfold>summary{cursor:pointer;list-style:none;font-size:13px;font-weight:700;color:var(--ac);padding:10px 2px;border-top:1px solid var(--line);text-transform:uppercase;letter-spacing:.04em}
details.secfold>summary::-webkit-details-marker{display:none}
details.secfold>summary::before{content:"▸ "}
details.secfold[open]>summary::before{content:"▾ "}
.gmgrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.gmcard{padding:10px 12px}.gmh{font-weight:700;font-size:13px;color:var(--ac);margin:2px 0 8px}
.gmrow{padding:8px 0;border-bottom:1px solid var(--rowline)}
.gmrow:last-child{border-bottom:0}
.gmt{font-size:13px;line-height:1.3}.gmt b{font-weight:700}.gmx{color:var(--mut);margin:0 4px}
.wdl{display:flex;height:9px;border-radius:4px;overflow:hidden;background:var(--box);margin-top:6px}
.wdl i{display:block;height:100%}
.gmn{font-size:10.5px;color:var(--mut);margin-top:5px}
.kogrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.kocell{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 12px}
.kolab{font-size:12px;font-weight:700;color:var(--ac);margin-bottom:6px}
.korow{padding:5px 0;border-bottom:1px solid var(--rowline)}.korow:last-of-type{border-bottom:0}
.kop{font-size:13px}.adv{color:var(--gd,#22c55e);font-weight:700;font-size:12.5px}
.kon{font-size:10.5px;color:var(--mut);margin-top:1px}
.drawer{position:fixed;top:0;right:0;height:100%;width:430px;max-width:94vw;background:var(--card2);border-left:1px solid var(--line);box-shadow:-20px 0 50px var(--dshadow);transform:translateX(102%);transition:transform .25s ease;overflow-y:auto;z-index:50}
.drawer.open{transform:none}.dh{padding:16px 18px;border-bottom:1px solid var(--line);position:sticky;top:0;background:var(--card2)}
.dh .x{float:right;cursor:pointer;color:var(--mut);font-size:22px;line-height:1;background:none;border:0;padding:0;font-family:inherit}
.dh .x:hover{color:var(--tx)}
.db{padding:16px 18px}
.cmp{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:10px 0 4px}
.cmp div{background:var(--box);border:1px solid var(--line);border-radius:9px;padding:8px;text-align:center}
.cmp .v{font-size:18px;font-weight:700}.cmp .n{font-size:11px;color:var(--mut)}
.stage{display:flex;align-items:center;gap:9px;margin:6px 0}
.stage .lab{width:96px;font-size:12px;color:var(--mut);text-align:right}
.stage .pb{flex:1;height:18px;background:var(--box);border-radius:6px;overflow:hidden;border:1px solid var(--line)}
.stage .pb i{display:block;height:100%}
.stage .pv{width:118px;font-size:12px}.kb{font-size:10.5px;color:var(--mut)}
.fld{margin:9px 0}.fld .k{font-size:11px;color:var(--ac);text-transform:uppercase;letter-spacing:.4px;font-weight:700}
.fld .v{font-size:13px;margin-top:1px}
.note{background:var(--box);border:1px solid var(--line);border-radius:10px;padding:11px 13px;color:var(--notetx);font-size:13px}
/* disclosure: agora tudo é .acc (shell.py) ou .secfold */
.kent td{border-bottom:1px solid var(--kentline);text-align:left;padding:5px 8px}
.kentsw{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:8px;vertical-align:-1px}
.foot{color:var(--mut);font-size:12px;margin-top:24px;border-top:1px solid var(--line);padding-top:12px}
.recipe{display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin:12px 0 6px}
.rcol{display:flex;flex-direction:column;gap:5px}
.rchip{display:flex;justify-content:space-between;gap:14px;background:var(--box);border:1px solid var(--line);border-radius:8px;padding:6px 11px;min-width:148px;font-size:12.5px}
.rchip b{font-variant-numeric:tabular-nums;color:var(--tx)}
.rarr{color:var(--ac);font-weight:700;font-size:20px}
.rout{font-size:12.5px;line-height:1.55;color:var(--mut)}.rout .ro1{color:var(--tx);font-weight:700}
@media(max-width:900px){.gmgrid,.kogrid{grid-template-columns:minmax(0,1fr)}}
@media(max-width:760px){.kpis{grid-template-columns:repeat(2,1fr)}.hidecol{display:none}.cn{width:120px}}
@media(max-width:560px){.drawer{width:100vw;max-width:100vw;border-left:0}.db{padding:14px}.cmp{gap:6px}.cmp div{padding:8px 4px}.stage .lab{width:80px}.stage .pv{width:118px}.stage .pv .kb{display:block;margin-top:1px}}
@media(pointer:coarse){.controls input,.controls select{min-height:40px}}
__SHELLCSS__</style></head><body data-page="dashboard">__TOPBAR__
<main class="wrap" id="main" tabindex="-1">
<div class="hero"><h1>Copa do Mundo 2026</h1>
<div class="sub">48 seleções · __N__ simulações da chave real (EUA·México·Canadá) · gerado em __GENDATE__</div></div>
<div class="anchors" style="margin:16px 0 0"><span class="lbl">Nesta página</span>__MUDOUNAV____PREMIOSNAV__<a href="#calc">Calculadora</a><a href="#matriz">Matriz</a><a href="#meta">Metodologia</a></div>
<div class="kpis">__KPIS__</div>

<h2>Probabilidade de título — top 16</h2>
<div class="card" style="padding:14px">
<div class="legend"><span><i style="background:#22c55e"></i>Modelo proprietário</span><span><i style="background:#38bdf8"></i>Odds</span><span><i style="background:#a78bfa"></i>Opta</span></div>
__CHART__
</div>
__MUDOU__
__PREMIOS__
<h2 id="calc" data-scene="calculadora">Calculadora de confronto</h2>
<div class="kb" style="margin-bottom:8px">Monte qualquer jogo possível — V/E/D, gols esperados e os placares mais prováveis, do mesmo motor da simulação.</div>
<div class="card calc-hero">
<div class="controls">
<select id="ca" aria-label="Primeira seleção do confronto">__CALCOPTS__</select>
<span style="color:var(--mut)" aria-hidden="true">×</span>
<select id="cb" aria-label="Segunda seleção do confronto">__CALCOPTS__</select>
<select id="cm" aria-label="Tipo de jogo"><option value="g">Fase de grupos (90')</option><option value="k">Mata-mata (com prorrogação e pênaltis)</option></select>
</div>
<div id="cout" class="note" aria-live="polite">Ative o JavaScript para usar a calculadora.</div>
</div>

<h2 id="matriz" data-scene="matriz">Matriz completa — 48 seleções × fase</h2>
<div class="controls">
<input id="q" placeholder="Buscar seleção..." aria-label="Buscar seleção na matriz">
<select id="fg" aria-label="Filtrar por grupo"><option value="">Todos os grupos</option>__GOPTS__</select>
<select id="ft" aria-label="Filtrar por tier"><option value="">Todos os tiers</option>__TOPTS__</select>
<select id="sortk" aria-label="Ordenar a matriz"><option value="ch">Ordenar: Título</option><option value="fin">Final</option><option value="sf">Semi</option><option value="qf">Quartas</option><option value="r16">Oitavas</option><option value="adv">Avançar</option><option value="gw">Vencer grupo</option><option value="pt">Nome</option><option value="group">Grupo</option></select>
</div>
<div class="kb" style="margin-bottom:6px">Toque numa seleção para o dossiê · cor = probabilidade da fase (o número é mostrado em toda célula)</div>
<div id="mstatus" class="sr-only" role="status" aria-live="polite"></div>
<div class="mhead" aria-hidden="true"><span>Gr</span><span>Av</span><span>Oi</span><span>Qu</span><span>Se</span><span>Fi</span><span>Tí</span></div>
<div id="mlist" class="mlist">__ROWS__</div>

<div class="note" style="margin:18px 0"><span aria-hidden="true">⚽</span> Os <b>jogos da fase de grupos</b> (com placar previsto) e os <b>confrontos prováveis do mata-mata</b> agora ficam na <a href="./resultados">página Resultados</a>, ao lado das tabelas e da chave reais.</div>

<h2 id="meta" data-scene="metodologia">Leitura, metodologia e limites</h2>
<details class="acc" open><summary><span class="adot"></span><span class="attl">Achado central: a assimetria da chave</span><span class="achev">▸</span></summary><div class="abd">
<div style="margin-top:8px" class="note">
Se vencerem seus grupos, <b>Brasil, Argentina, Portugal e Inglaterra caem todos na metade de baixo</b> do chaveamento — só um deles chega à final. <b>Espanha e França dividem a metade de cima</b> e tendem a se cruzar já na semifinal. Por isso o modelo, ao simular a chave real, reduz o título dos quatro de baixo em relação às odds isoladas e mantém Espanha/França altas. As divergências modelo×odds são, em boa parte, <b>efeito de sorteio</b> — e indicam onde pode haver valor.
</div></div></details>
<details class="acc"><summary><span class="adot"></span><span class="attl">Pipeline e pesos — modelo proprietário</span><span class="ahint">abrir</span><span class="achev">▸</span></summary><div class="abd">
<div class="recipe">
<div class="rcol">
<div class="rchip"><span>Odds</span><b>45%</b></div>
<div class="rchip"><span>Opta</span><b>35%</b></div>
<div class="rchip"><span>Qualitativo</span><b>20%</b></div>
</div>
<div class="rarr">→</div>
<div class="rout"><div class="ro1">rating de força por seleção <span class="kb">(modelo proprietário)</span></div>
<div>↓ 50.000 simulações da chave oficial</div>
<div>↓ probabilidade por fase e título</div></div>
</div>
<div style="margin-top:8px">Cada seleção recebe um <b>rating de força</b> numa escala de pontos, combinando: força implícita das <b>odds</b> (probabilidades de título com a margem da casa removida) a 45%; <b>Opta</b> (supercomputador) a 35%; e um <b>ajuste qualitativo limitado</b> (±~22 pontos) a 20%, vindo da síntese de jornalismo confiável (lesões, forma, técnico, momento). Sobre esses ratings, um modelo de partida de <b>Poisson</b> (gols a partir da diferença de rating, com vantagem de mando para os anfitriões) alimenta a simulação da <b>chave oficial</b> 50 mil vezes — grupos com critérios de desempate, regra dos 8 melhores terceiros (conjuntos do Anexo C da FIFA) e mata-mata com prorrogação/pênaltis. As probabilidades por fase são <b>saída</b> da simulação, então são coerentes entre si. Os jogos de grupo e a calculadora usam o <b>mesmo motor</b> em forma analítica (matriz de Poisson), e os confrontos prováveis do mata-mata vêm da frequência observada nas simulações.</div></div></details>
<details class="acc"><summary><span class="adot"></span><span class="attl">Escala probabilística (probabilidade estimativa)</span><span class="ahint">abrir</span><span class="achev">▸</span></summary><div class="abd">
<table class="kent" style="margin-top:8px;width:100%"><caption class="sr-only">Escala de probabilidade estimativa: rótulo e faixa percentual</caption><tbody>__KENTROWS__</tbody></table>
<div class="kb" style="margin-top:6px">Vocabulário de probabilidade estimativa usado como camada de comunicação/calibração sobre os números — não é fonte de dado.</div></div></details>
<details class="acc"><summary><span class="adot"></span><span class="attl">Limites honestos</span><span class="ahint">abrir</span><span class="achev">▸</span></summary><div class="abd">
<div style="margin-top:8px" class="note">As odds de aposta são o melhor preditor único e já incorporam lesão, forma e dinheiro esperto; nenhum método "ganha do mercado" de forma confiável num mata-mata único. Odds e Opta não são independentes (o Opta usa odds como insumo). O modelo de gols é Poisson independente — bom para 1X2 e xG, mas subestima levemente placares correlacionados (ex.: 1-1) por não modelar dependência entre ataques. O ajuste qualitativo é limitado para não sobreajustar narrativa. Números mudam com convocações/lesões até a estreia (11/jun).</div></div></details>
<details class="acc"><summary><span class="adot"></span><span class="attl">Fontes</span><span class="ahint">abrir</span><span class="achev">▸</span></summary><div class="abd">
<div style="margin-top:8px" class="kb">Estrutura/chave: FIFA, Wikipédia (sorteio e fase final). Odds de título: consenso de FanDuel, DraftKings, bet365, Pinnacle, Unibet e Betfred (via SI, ESPN, CBS e comparadores UK). Modelo de referência: Opta/The Analyst (supercomputador). Prêmios individuais: DraftKings/FanDuel (artilheiro) e bet365 (luvas). Noticiário/qualitativo: ESPN, BBC, The Athletic, The Guardian, Sky Sports, Al Jazeera, L'Équipe, Marca, ge/Globo, perfis oficiais FIFA (dossiês por seleção: curadoria de 1–3/jun). Coletado 9/jun/2026.</div></div></details>

<footer class="foot">Modelo preditivo proprietário · __N__ simulações · gols~Poisson · Probabilidades são estimativas, não garantias. · __CREDIT__</footer>
</main>

<div class="drawer" id="drawer" role="dialog" aria-modal="true" aria-label="Dossiê da seleção" tabindex="-1"><div class="dh"><button type="button" class="x" onclick="closeDrawer()" aria-label="Fechar">×</button>
<div id="dtitle" style="font-size:20px;font-weight:700"></div><div id="dsub" class="kb" style="margin-top:3px"></div></div>
<div class="db" id="dbody"></div></div>

<script>
const DATA=__DATA__;
const H2H=__H2H__;
const STAGES=[["gw","Vencer grupo"],["adv","Avançar (32)"],["r16","Oitavas"],["qf","Quartas"],["sf","Semifinal"],["fin","Final"],["ch","Título"]];
const KENT=[[.93,"Quase certo","#16a34a"],[.75,"Muito provável","#22c55e"],[.55,"Provável","#84cc16"],[.45,"Chances iguais","#eab308"],[.25,"Pouco provável","#f97316"],[.07,"Improvável","#ef4444"],[0,"Remoto","#991b1b"]];
function kent(p){for(const k of KENT){if(p>=k[0])return k}return KENT[KENT.length-1]}
function heat(p){const a=0.10+0.82*Math.sqrt(p);return a>=0.52?"background:rgba(110,231,160,"+a.toFixed(3)+");color:var(--heat-ink)":"background:rgba(34,197,94,"+a.toFixed(3)+")"}
function pc(p){return(p*100).toFixed(p>=0.10?0:p>=0.01?1:2)+'%'}
const TIERCLS={"Favorito ao título":"t0","Candidato real":"t1","Azarão":"t2","Aposta externa":"t3","Completando o chaveamento":"t4"};
const names=Object.keys(DATA);
let sortK="ch",sortDir=-1;
function render(){
  const q=document.getElementById('q').value.toLowerCase(),fg=document.getElementById('fg').value,ft=document.getElementById('ft').value;
  let rows=names.filter(n=>(DATA[n].pt.toLowerCase().includes(q)||n.toLowerCase().includes(q))&&(!fg||DATA[n].group===fg)&&(!ft||DATA[n].tier===ft));
  rows.sort((a,b)=>{let x=DATA[a][sortK],y=DATA[b][sortK];if(typeof x==='string')return sortDir*x.localeCompare(y);return sortDir*(x-y)});
  document.getElementById('mlist').innerHTML=rows.map(n=>{const d=DATA[n];
    const cells=STAGES.map(s=>'<span class="mc" style="'+heat(d[s[0]])+'">'+pc(d[s[0]])+'</span>').join('');
    const e=n.replace(/'/g,"\\'");
    return '<div class="mrow" onclick="openDrawer(\''+e+'\')" tabindex="0" role="button" onkeydown="if(event.key===\'Enter\'||event.key===\' \'){event.preventDefault();openDrawer(\''+e+'\')}"><div class="mtop"><span class="flag">'+d.flag+'</span><span class="mname">'+d.pt+'</span><span class="grp">'+d.group+'</span><span class="tier '+(TIERCLS[d.tier]||'t4')+'">'+d.tier+'</span><span class="mch">'+pc(d.ch)+'</span></div><div class="mcells">'+cells+'</div></div>'}).join('');
  var _ms=document.getElementById('mstatus');if(_ms)_ms.textContent=rows.length+' seleções na matriz';
}
document.getElementById('sortk').onchange=e=>{sortK=e.target.value;sortDir=(sortK==='pt'||sortK==='group')?1:-1;render()};
['q','fg','ft'].forEach(id=>document.getElementById(id).oninput=render);
function openDrawer(n){const d=DATA[n];
  document.getElementById('dtitle').innerHTML=d.flag+' '+d.pt;
  const val=d.ch-d.cons, vtx=Math.abs(val)<0.005?'alinhado ao consenso odds+Opta':(val>0?'modelo ACIMA do consenso (+'+(val*100).toFixed(1)+'pp)':'modelo ABAIXO do consenso ('+(val*100).toFixed(1)+'pp)');
  document.getElementById('dsub').innerHTML='Grupo '+d.group+' · <span class="tier '+(TIERCLS[d.tier]||'t4')+'">'+d.tier+'</span> · rating '+d.rk;
  let h='<div class="cmp"><div><div class="v">'+pc(d.ch)+'</div><div class="n">Proprietário</div></div><div><div class="v">'+pc(d.mkt)+'</div><div class="n">Odds</div></div><div><div class="v">'+pc(d.opta)+'</div><div class="n">Opta</div></div></div>'
    +'<div class="kb" style="margin:2px 0 8px">'+vtx+'</div>'
    +'<div class="note" style="margin-bottom:10px">Torneio (valores esperados): <b>'+d.gf.toFixed(1)+'</b> gols marcados · <b>'+d.ga.toFixed(1)+'</b> sofridos · <b>'+d.mp.toFixed(1)+'</b> jogos</div>'
    +'<div class="fld"><div class="k">Caminho por fase (escala probabilística)</div></div>';
  STAGES.forEach(s=>{const p=d[s[0]],k=kent(p);
    h+='<div class="stage"><div class="lab">'+s[1]+'</div><div class="pb"><i style="width:'+Math.max(2,p*100)+'%;background:'+k[2]+'"></i></div><div class="pv"><b>'+pc(p)+'</b> <span class="kb">'+k[1]+'</span></div></div>'});
  const F=[["Técnico",d.coach],["Craques",d.stars],["Lesões / disponibilidade",d.inj],["Forma",d.form],["Histórico",d.hist],["Maior trunfo",d.edge],["Maior risco",d.risk]];
  h+='<div style="margin-top:12px"></div>';
  F.forEach(f=>{if(f[1])h+='<div class="fld"><div class="k">'+f[0]+'</div><div class="v">'+f[1]+'</div></div>'});
  if(d.read)h+='<div class="note" style="margin-top:10px">'+d.read+'</div>';
  document.getElementById('dbody').innerHTML=h;
  document.getElementById('drawer').classList.add('open');
  if(window.fdjDrawerOpen)fdjDrawerOpen(document.getElementById('drawer'));
}
function closeDrawer(){document.getElementById('drawer').classList.remove('open');if(window.fdjDrawerClose)fdjDrawerClose()}
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeDrawer()});

// ---- calculadora: consulta a tabela pré-computada H2H (xG + classificação) e monta
//      V/E/D e placares com pois()/wdl() genéricos sobre os xG servidos. O motor de rating
//      (parâmetros + rating cru) fica no build, fora do cliente. ----
function pois(l,k){return Math.exp(-l)*Math.pow(l,k)/[1,1,2,6,24,120,720,5040,40320,362880,3628800][k]}
function wdl(x,y,N){let W=0,D=0,L=0,sc=[];
  for(let i=0;i<N;i++)for(let j=0;j<N;j++){const p=pois(x,i)*pois(y,j);sc.push([p,i,j]);
    if(i>j)W+=p;else if(i===j)D+=p;else L+=p}
  sc.sort((u,v)=>v[0]-u[0]);return{W,D,L,sc}}
function calcRender(){
  const a=document.getElementById('ca').value,b=document.getElementById('cb').value,ko=document.getElementById('cm').value==='k';
  const o=document.getElementById('cout');
  if(a===b){o.innerHTML='Escolha duas seleções diferentes.';return}
  const da=DATA[a],db=DATA[b];
  const sw=a>b,lo=sw?b:a,hi=sw?a:b,e=H2H[lo+'|'+hi];
  const la=sw?e[1]:e[0],lb=sw?e[0]:e[1],m=wdl(la,lb,11);
  const r={la,lb,W:m.W,D:m.D,L:m.L,top:m.sc.slice(0,5)};
  if(ko){r.advA=sw?e[3]:e[2];r.advB=1-r.advA}
  let h='<div style="font-size:15px;margin-bottom:6px">'+da.flag+' <b>'+da.pt+'</b> × <b>'+db.pt+'</b> '+db.flag+(da.host||db.host?' <span class="kb">(vantagem de mando aplicada ao anfitrião)</span>':'')+'</div>';
  h+='<div class="wdl" style="height:12px;max-width:520px"><i style="width:'+(r.W*100)+'%;background:#22c55e"></i><i style="width:'+(r.D*100)+'%;background:#64748b"></i><i style="width:'+(r.L*100)+'%;background:#ef4444"></i></div>';
  h+='<div style="margin:6px 0">90 minutos: <b>'+da.pt+' '+pc(r.W)+'</b> · empate '+pc(r.D)+' · <b>'+db.pt+' '+pc(r.L)+'</b></div>';
  h+='<div>Gols esperados (xG): <b>'+r.la.toFixed(2)+'</b> × <b>'+r.lb.toFixed(2)+'</b></div>';
  if(ko)h+='<div style="margin-top:4px">Classificação (prorrogação+pênaltis): <b style="color:#22c55e">'+da.pt+' '+pc(r.advA)+'</b> × <b>'+pc(r.advB)+' '+db.pt+'</b></div>';
  h+='<div style="margin-top:6px" class="kb">Placares mais prováveis (90\'): '+r.top.map(s=>s[1]+'-'+s[2]+' ('+(s[0]*100).toFixed(1)+'%)').join(' · ')+'</div>';
  o.innerHTML=h;
}
['ca','cb','cm'].forEach(id=>document.getElementById(id).oninput=calcRender);
document.getElementById('ca').value='Brazil';document.getElementById('cb').value='Morocco';calcRender();
</script>__SHELLJS__</body></html>"""

# ---- calculadora: tabela de confrontos PRÉ-COMPUTADA (o motor sai do cliente) ----
# O motor de partida (rating→λ via HA/GOAL_DIV/MU + rating cru R) roda AQUI, no build.
# O cliente recebe só, por par, os xG e a prob. de classificação no mata-mata — que são
# SAÍDA/produto (já exibidos), nunca os parâmetros nem o rating cru. pois()/wdl() (Poisson
# genérico, já descrito na metodologia) seguem no cliente só p/ montar V/E/D e placares a
# partir dos xG servidos. O confronto é simétrico (calcPair(b,a)=espelho de calcPair(a,b)),
# então guardamos só pares não-ordenados (a<b) e o lookup espelha quando necessário.
import math as _math
_FACT=[1,1,2,6,24,120,720,5040,40320,362880,3628800]
def _pois(l,k): return _math.exp(-l)*l**k/_FACT[k]
def _wdl(x,y,N):
    W=D=L=0.0
    for i in range(N):
        pi=_pois(x,i)
        for j in range(N):
            p=pi*_pois(y,j)
            if i>j: W+=p
            elif i==j: D+=p
            else: L+=p
    return W,D,L
def _h2h(a,b):  # la(a), lb(b), P(a classifica), P(b classifica) — espelha o antigo calcPair JS
    da,db=DATA[a],DATA[b]
    d=(da["R"]+(HA if da["host"] else 0))-(db["R"]+(HA if db["host"] else 0))
    sup=d/GOAL_DIV
    la=max(0.15,MUG/2+sup/2); lb=max(0.15,MUG/2-sup/2)
    mW,mD,mL=_wdl(la,lb,11)
    eW,eD,eL=_wdl(la*0.34,lb*0.34,8)
    pensA=min(0.8,max(0.2,0.5+(da["R"]-db["R"])/4000))
    pensB=min(0.8,max(0.2,0.5+(db["R"]-da["R"])/4000))
    advA=mW+mD*(eW+eD*pensA)   # P(a avança) — orientação (a,b), exatamente como o OLD calcPair(a,b)
    advB=mL+mD*(eL+eD*pensB)   # P(b avança) — orientação (b,a), espelhando OLD calcPair(b,a)
    # NB: advA+advB != 1 sob a matriz TRUNCADA (N=11/8); por isso guardamos os DOIS sentidos
    # em vez de derivar advB=1-advA (isso introduziria ~1e-4 de erro vs o motor antigo).
    return la,lb,advA,advB
_cnames=sorted(DATA)
H2H={}
for _i in range(len(_cnames)):
    for _j in range(_i+1,len(_cnames)):
        _a,_b=_cnames[_i],_cnames[_j]
        _la,_lb,_advA,_advB=_h2h(_a,_b)
        # SEM arredondar: json.dumps preserva o double exato → JS reparseia idêntico →
        # toFixed/pc batem byte-a-byte com o motor antigo. Arredondar cruzaria bordas de
        # toFixed (ex.: 1.0650000000000004→"1.07" vira 1.065→"1.06").
        H2H[_a+"|"+_b]=[_la,_lb,_advA,_advB]
# DATA servido: SEM o rating cru (R_cal float) — o motor não vai mais ao cliente, e o dossiê
# só precisa do rating ARREDONDADO (rk). mkt/opta/cons reduzidos à precisão que a view mostra.
DATA_JS={}
for _n,_d in DATA.items():
    _o={k:v for k,v in _d.items() if k!="R"}
    _o["rk"]=round(_d["R"])
    for _k in ("mkt","opta","cons"): _o[_k]=round(_d[_k],4)
    DATA_JS[_n]=_o

HTML=(HTML.replace("__DATA__",json.dumps(DATA_JS,ensure_ascii=False))
          .replace("__H2H__",json.dumps(H2H,ensure_ascii=False))
          .replace("__ROWS__",ROWS).replace("__KPIS__",KPIS).replace("__CHART__",CHART)
          .replace("__KENTROWS__",KENTROWS).replace("__GOPTS__",GOPTS).replace("__TOPTS__",TOPTS)
          .replace("__CALCOPTS__",CALCOPTS)
          .replace("__MUDOU__",MUDOU).replace("__MUDOUNAV__",MUDOUNAV)
          .replace("__PREMIOS__",PREMIOS).replace("__PREMIOSNAV__",PREMIOSNAV)
          .replace("__GENDATE__",_ptdate(meta["generated"]))
          .replace("__N__",f"{meta['N']:,}".replace(",","."))
          .replace("__SHELLHEAD__",shell.HEAD+shell.meta("Dashboard — Ficha do Jogo · Copa 2026","Probabilidades da Copa do Mundo 2026 por seleção, fase e jogo — 48 seleções, 50 mil simulações, calculadora de confronto e dossiês por seleção.","dashboard")).replace("__SHELLCSS__",shell.CSS)
          .replace("__TOPBAR__",shell.topbar("dash")+flags.SPRITE).replace("__SHELLJS__",shell.JS).replace("__CREDIT__",shell.CREDIT))

# Tokens do dashboard (mesmos valores do sistema theme.py, com o conjunto ampliado que o dashboard usa).
# Dark = morno + accent gold; Light = cream + accent verde. Cores de DADO (heatmap/V-E-D/Kent/chart) seguem inline.
DARK_BODY=("--bg:#0f1b13;--card:#18271d;--card2:#132015;--line:#25382b;--tx:#f1ece0;--mut:#9fae9d;"
           "--ac:#f3b03c;--box:#0a140d;--rowline:#17251b;--rowhov:#1d2e22;--chipbg:#243a2c;--chiptx:#cfe2cf;"
           "--notetx:#e6efe2;--kentline:#1d2e22;--kpia:#1a2a1e;--kpib:#132015;--pillbg:#132015;--dshadow:rgba(0,0,0,.55);--gd:#22c55e;"
           "--ink:#f1ece0;--acsoft:rgba(243,176,60,.13);--logo-frame:#f3b03c;--logo-bar:#22c55e;--heat-ink:#07120b")
LIGHT_BODY=("--bg:#f5f2e6;--card:#fffef9;--card2:#fffef9;--line:#e3ddc8;--tx:#23271b;--mut:#6f7259;"
            "--ac:#1a7a43;--box:#ece6d6;--rowline:#ece7d4;--rowhov:#f0ece0;--chipbg:#e7e0cd;--chiptx:#4a4327;"
            "--notetx:#3a4030;--kentline:#e3ddc8;--kpia:#f3efe2;--kpib:#fffef9;--pillbg:#f0ece0;--dshadow:rgba(40,30,15,.18);--gd:#15803d;"
            "--ink:#23271b;--acsoft:rgba(26,122,67,.12);--logo-frame:#bd8b1f;--logo-bar:#16924a;--heat-ink:#102013")
# tiers num ramo QUENTE (ordinal: favorito gold → completando cinza-quente), sem azul/teal frio.
TIERS_DARK=".t0{background:#6b3a14;color:#fac98a}.t1{background:#574311;color:#e8c47a}.t2{background:#3f3c18;color:#cfc985}.t3{background:#3a342a;color:#c8bda6}.t4{background:#2c2720;color:#a89c8a}"
TIERS_LIGHT=".t0{background:#fbe6c6;color:#8a4a12}.t1{background:#f4e3bd;color:#7a5810}.t2{background:#ebe9c4;color:#5d5c1c}.t3{background:#ece6da;color:#5c5446}.t4{background:#f1ece2;color:#6e6557}"
# dashboard.html = dark padrão FIXO + claro só via toggle [data-theme] (não segue o SO). artifact.html = light forçado.
def _scope(css, pfx):  # escopa as regras de tier (.t0..t4) sob um seletor (p/ overrides do toggle)
    for k in ("t0", "t1", "t2", "t3", "t4"): css = css.replace("." + k + "{", pfx + " ." + k + "{")
    return css
ADAPT_PAL=(":root{color-scheme:dark;"+DARK_BODY+"}:root[data-theme=light]{color-scheme:light;"+LIGHT_BODY+"}")
ADAPT_TIERS=(TIERS_DARK+_scope(TIERS_LIGHT,":root[data-theme=light]"))
dark=HTML.replace("__PALETTE__",ADAPT_PAL).replace("__TIERS__",ADAPT_TIERS)
light=HTML.replace("__PALETTE__",":root{color-scheme:light;"+LIGHT_BODY+"}").replace("__TIERS__",TIERS_LIGHT)
light=light.replace(shell.GTM_HEAD,"").replace(shell.GTM_NOSCRIPT,"")  # artifact (light) sai SEM GTM — Opção B
open(f"{DIST}/copa2026_dashboard.html","w").write(dark)
open(f"{DIST}/copa2026_artifact.html","w").write(light)
print("dashboard(adapt):",len(dark),"| artifact(light):",len(light),
      "| prefers:",dark.count("prefers-color-scheme"),"| cdn:",dark.count("cdnjs")+dark.count("<script src"))
