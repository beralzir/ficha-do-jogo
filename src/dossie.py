#!/usr/bin/env python3
"""Dossiê da seleção (painel/drawer) COMPARTILHADO — clica num time (bandeira+nome) em qualquer página
e abre o painel: proprietário/odds/opta, gols esperados, caminho por fase (escala probabilística),
técnico, craques, lesões, forma, histórico, trunfo, risco, leitura.

Saiu do dashboard (ajuste #4) pra ficar disponível em TODAS as páginas. Expõe:
- build_data(res, doss, HOSTS) -> dict DATA (com white-label _wl aplicado aos dossiês)
- tlink(name_en, inner, cls="") -> envolve bandeira+nome num gatilho clicável
- DRAWER (html do painel + scrim) · CSS · js(DATA) (<script> com DATA + open/closeDrawer)
Tokens usados (todos existem em theme.py e no dashboard): --card2 --line --box --ink --mut --ac --notetx --dshadow.
NÃO incluir js(DATA) no dashboard (ele já tem o seu próprio DATA/openDrawer — evita redeclaração)."""
import json
from pt import PT


def _wl(s):  # white-label: esconde "Elo" no texto curado dos dossiês
    return s.replace("Elo alto", "rating alto").replace("Elo/inexperiência", "rating/inexperiência").replace("Elo", "rating") if isinstance(s, str) else s


def build_data(res, doss, HOSTS):
    teams = res["teams"]; DATA = {}
    for t, x in teams.items():
        d = {k: _wl(v) for k, v in doss.get(t, {}).items()}
        DATA[t] = {"pt": PT[t][1], "flag": PT[t][0], "group": x["group"],
                   "gw": x["group_win"], "adv": x["advance"], "r16": x["r16"], "qf": x["qf"],
                   "sf": x["sf"], "fin": x["final"], "ch": x["champion"],
                   "mkt": x["mkt"], "opta": x["opta"], "cons": x["consensus"],
                   "R": x["R_cal"], "host": (t in HOSTS),
                   "gf": x["g_for"], "ga": x["g_ag"], "mp": x["mp"],
                   "tier": d.get("tier", ""), "coach": d.get("coach", ""), "stars": d.get("stars", ""),
                   "inj": d.get("inj", ""), "form": d.get("form", ""), "hist": d.get("hist", ""),
                   "edge": d.get("edge", ""), "risk": d.get("risk", ""), "read": d.get("read", "")}
    return DATA


def tlink(name_en, inner, cls=""):
    """Envolve uma exibição de time (bandeira+nome) num gatilho clicável pro dossiê (acessível por teclado)."""
    n = name_en.replace("\\", "").replace("'", "\\'")
    c = ("tlink " + cls).strip()
    return (f'<span class="{c}" tabindex="0" role="button" onclick="openDrawer(\'{n}\')" '
            f'onkeydown="if(event.key===\'Enter\'||event.key===\' \'){{event.preventDefault();openDrawer(\'{n}\')}}">{inner}</span>')


DRAWER = ('<div class="dscrim" id="dscrim" onclick="closeDrawer()"></div>'
          '<div class="drawer" id="drawer" role="dialog" aria-label="Dossiê da seleção">'
          '<div class="dh"><span class="x" onclick="closeDrawer()" role="button" aria-label="Fechar">×</span>'
          '<div id="dtitle" style="font-size:20px;font-weight:700"></div>'
          '<div id="dsub" class="kb" style="margin-top:3px"></div></div>'
          '<div class="db" id="dbody"></div></div>')


def js(DATA):
    # DATA servido SEM o rating cru (R_cal float): o dossiê só precisa do rating ARREDONDADO
    # (rk); mkt/opta/cons reduzidos à precisão exibida (defesa contra raspagem/eng. reversa
    # dos pesos). Mesma blindagem do build_dashboard.py. Não afeta o uso Python do DATA.
    DJS = {n: {**{k: v for k, v in d.items() if k != "R"}, "rk": round(d["R"]),
               "mkt": round(d["mkt"], 4), "opta": round(d["opta"], 4), "cons": round(d["cons"], 4)}
           for n, d in DATA.items()}
    return ('<script>\n'
            'const DATA=' + json.dumps(DJS, ensure_ascii=False) + ';\n'
            'const STAGES=[["gw","Vencer grupo"],["adv","Avançar (32)"],["r16","Oitavas"],["qf","Quartas"],["sf","Semifinal"],["fin","Final"],["ch","Título"]];\n'
            'const KENT=[[.93,"Quase certo","#16a34a"],[.75,"Muito provável","#22c55e"],[.55,"Provável","#84cc16"],[.45,"Chances iguais","#eab308"],[.25,"Pouco provável","#f97316"],[.07,"Improvável","#ef4444"],[0,"Remoto","#991b1b"]];\n'
            'function kent(p){for(const k of KENT){if(p>=k[0])return k}return KENT[KENT.length-1]}\n'
            'function pc(p){return(p*100).toFixed(p>=0.10?0:p>=0.01?1:2)+"%"}\n'
            'function openDrawer(n){const d=DATA[n];if(!d)return;\n'
            '  document.getElementById("dtitle").innerHTML=d.flag+" "+d.pt;\n'
            '  const val=d.ch-d.cons, vtx=Math.abs(val)<0.005?"alinhado ao consenso odds+Opta":(val>0?"modelo ACIMA do consenso (+"+(val*100).toFixed(1)+"pp)":"modelo ABAIXO do consenso ("+(val*100).toFixed(1)+"pp)");\n'
            '  document.getElementById("dsub").innerHTML="Grupo "+d.group+" · <b style=\\"color:var(--ac)\\">"+d.tier+"</b> · rating "+d.rk;\n'
            '  let h=\'<div class="cmp"><div><div class="v">\'+pc(d.ch)+\'</div><div class="n">Proprietário</div></div><div><div class="v">\'+pc(d.mkt)+\'</div><div class="n">Odds</div></div><div><div class="v">\'+pc(d.opta)+\'</div><div class="n">Opta</div></div></div>\'\n'
            '    +\'<div class="kb" style="margin:2px 0 8px">\'+vtx+\'</div>\'\n'
            '    +\'<div class="note" style="margin-bottom:10px">Torneio (valores esperados): <b>\'+d.gf.toFixed(1)+\'</b> gols marcados · <b>\'+d.ga.toFixed(1)+\'</b> sofridos · <b>\'+d.mp.toFixed(1)+\'</b> jogos</div>\'\n'
            '    +\'<div class="fld"><div class="k">Caminho por fase (escala probabilística)</div></div>\';\n'
            '  STAGES.forEach(s=>{const p=d[s[0]],k=kent(p);h+=\'<div class="stage"><div class="lab">\'+s[1]+\'</div><div class="pb"><i style="width:\'+Math.max(2,p*100)+\'%;background:\'+k[2]+\'"></i></div><div class="pv"><b>\'+pc(p)+\'</b> <span class="kb">\'+k[1]+\'</span></div></div>\'});\n'
            '  const F=[["Técnico",d.coach],["Craques",d.stars],["Lesões / disponibilidade",d.inj],["Forma",d.form],["Histórico",d.hist],["Maior trunfo",d.edge],["Maior risco",d.risk]];\n'
            '  h+=\'<div style="margin-top:12px"></div>\';\n'
            '  F.forEach(f=>{if(f[1])h+=\'<div class="fld"><div class="k">\'+f[0]+\'</div><div class="v">\'+f[1]+\'</div></div>\'});\n'
            '  if(d.read)h+=\'<div class="note" style="margin-top:10px">\'+d.read+\'</div>\';\n'
            '  document.getElementById("dbody").innerHTML=h;\n'
            '  document.getElementById("drawer").classList.add("open");document.getElementById("dscrim").classList.add("open");\n'
            '}\n'
            'function closeDrawer(){document.getElementById("drawer").classList.remove("open");document.getElementById("dscrim").classList.remove("open")}\n'
            'document.addEventListener("keydown",e=>{if(e.key==="Escape")closeDrawer()});\n'
            '</script>')


CSS = r"""
/* dossiê (drawer) compartilhado + gatilho .tlink */
.tlink{cursor:pointer;border-radius:4px;transition:color .12s}
.tlink:hover,.tlink:focus-visible{color:var(--ac);outline:none;text-decoration:underline;text-decoration-color:var(--ac);text-underline-offset:2px}
.dscrim{position:fixed;inset:0;background:rgba(0,0,0,.45);opacity:0;pointer-events:none;transition:opacity .25s;z-index:49}
.dscrim.open{opacity:1;pointer-events:auto}
.drawer{position:fixed;top:0;right:0;height:100%;width:430px;max-width:94vw;background:var(--card2);border-left:1px solid var(--line);box-shadow:-20px 0 50px var(--dshadow);transform:translateX(102%);transition:transform .25s ease;overflow-y:auto;z-index:50}
.drawer.open{transform:none}
.dh{padding:16px 18px;border-bottom:1px solid var(--line);position:sticky;top:0;background:var(--card2)}
.dh .x{float:right;cursor:pointer;color:var(--mut);font-size:22px;line-height:1}
.db{padding:16px 18px}
.cmp{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:10px 0 4px}
.cmp div{background:var(--box);border:1px solid var(--line);border-radius:9px;padding:8px;text-align:center}
.cmp .v{font-size:18px;font-weight:700}.cmp .n{font-size:11px;color:var(--mut)}
.stage{display:flex;align-items:center;gap:9px;margin:6px 0}
.stage .lab{width:96px;font-size:12px;color:var(--mut);text-align:right}
.stage .pb{flex:1;height:18px;background:var(--box);border-radius:6px;overflow:hidden;border:1px solid var(--line)}
.stage .pb i{display:block;height:100%}
.stage .pv{width:118px;font-size:12px}
.fld{margin:9px 0}.fld .k{font-size:11px;color:var(--ac);text-transform:uppercase;letter-spacing:.4px;font-weight:700}
.fld .v{font-size:13px;margin-top:1px}
.note{background:var(--box);border:1px solid var(--line);border-radius:10px;padding:11px 13px;color:var(--notetx);font-size:13px}
.db .kb{font-size:10.5px;color:var(--mut)}
@media(max-width:560px){.drawer{width:100vw;max-width:100vw;border-left:0}.db{padding:14px}}
"""
