#!/usr/bin/env python3
"""Cartões de PREVISÃO por jogo — motor analítico (Poisson, espelha o simulador) + HTML dos jogos de
grupo (V/E/D, xG, placar provável) e dos confrontos prováveis do mata-mata.

Saiu do dashboard na DEDUP (Fase 3 do redesign): o dashboard foca em probabilidades + calculadora;
a página Resultados reúne tabela/chave REAIS + estas PREVISÕES em acordeão (.acc). Importado por
build_resultados.py. Usa tokens do tema (theme.py) no CSS. Determinístico (só lê o results.json)."""
import math
from pt import PT


def _nm(t): return PT.get(t, ["", t])[1]
def _fl(t): return PT.get(t, ["", t])[0]
def _pcb(p): return f"{p*100:.0f}%"
def _fx(v): return f"{v:.1f}"


# ---- motor de partida (idêntico ao simulador: gols ~ Poisson independentes) ----
def _lams(Ra, hosta, Rb, hostb, HA, GD, MU):
    d = (Ra + (HA if hosta else 0)) - (Rb + (HA if hostb else 0)); sup = d / GD
    return max(0.15, MU / 2 + sup / 2), max(0.15, MU / 2 - sup / 2)


def _pmf(l, k): return math.exp(-l) * l ** k / math.factorial(k)


def _grid(la, lb, N=11):
    pa = [_pmf(la, k) for k in range(N)]; pb = [_pmf(lb, k) for k in range(N)]
    W = D = L = 0.0; sc = []
    for i in range(N):
        for j in range(N):
            p = pa[i] * pb[j]; sc.append((p, i, j))
            if i > j: W += p
            elif i == j: D += p
            else: L += p
    sc.sort(reverse=True); return W, D, L, sc


def match_calc(Ra, hosta, Rb, hostb, HA, GD, MU, ko=False):
    la, lb = _lams(Ra, hosta, Rb, hostb, HA, GD, MU); W, D, L, sc = _grid(la, lb)
    out = {"la": la, "lb": lb, "W": W, "D": D, "L": L, "top": sc[:5]}
    if ko:
        eW, eD, eL, _ = _grid(la * 0.34, lb * 0.34, 8)
        pens = min(0.80, max(0.20, 0.5 + (Ra - Rb) / 4000))
        out["advA"] = W + D * (eW + eD * pens); out["advB"] = 1 - out["advA"]
    return out


# ---- HTML: 72 jogos de grupo (resultado/gols previstos) ----
def group_grid(model, S, HOSTS):
    teams = model["teams"]; m = model["meta"]; HA, GD, MU = m["HA"], m["GOAL_DIV"], m["MU"]
    cards = []
    for g, ts in sorted(S["groups"].items()):
        rows = []
        for i in range(4):
            for j in range(i + 1, 4):
                a, b = ts[i], ts[j]
                r = match_calc(teams[a]["R_cal"], a in HOSTS, teams[b]["R_cal"], b in HOSTS, HA, GD, MU)
                si, sj = r["top"][0][1], r["top"][0][2]
                bar = (f'<div class="wdl"><i style="width:{r["W"]*100:.1f}%;background:#22c55e"></i>'
                       f'<i style="width:{r["D"]*100:.1f}%;background:#64748b"></i>'
                       f'<i style="width:{r["L"]*100:.1f}%;background:#ef4444"></i></div>')
                rows.append(f'<div class="gmrow"><div class="gmt">{_fl(a)} <b>{_nm(a)}</b> '
                            f'<span class="gmx">×</span> <b>{_nm(b)}</b> {_fl(b)}</div>{bar}'
                            f'<div class="gmn">V {_pcb(r["W"])} · E {_pcb(r["D"])} · D {_pcb(r["L"])} · '
                            f'xG {_fx(r["la"])}–{_fx(r["lb"])} · placar+ {si}-{sj} ({r["top"][0][0]*100:.0f}%)</div></div>')
        cards.append(f'<div class="gmcard"><div class="gmh">Grupo {g}</div>{"".join(rows)}</div>')
    return f'<div class="gmgrid">{"".join(cards)}</div>'


# ---- HTML: confrontos mais prováveis do mata-mata (frequência das simulações) ----
def ko_blocks(model, S, HOSTS):
    teams = model["teams"]; m = model["meta"]; HA, GD, MU = m["HA"], m["GOAL_DIV"], m["MU"]; MUS = model["matchups"]

    def slotlab(s, r):
        if s == "3rd": return "3º (" + "/".join(r["third_from"]) + ")"
        if s.startswith("W"): return "Venc. J" + s[1:]
        return ("1º " if s[0] == "1" else "2º ") + s[1]

    ROUNDS = [("32-avos de final", S["r32"]), ("Oitavas de final", S["r16"]),
              ("Quartas de final", S["qf"]), ("Semifinais", S["sf"]), ("FINAL", [S["final"]])]
    out = []
    for rname, matches in ROUNDS:
        cells = []
        for r in sorted(matches, key=lambda x: x["match"]):
            mno = str(r["match"]); mu = MUS.get(mno, [])[:4]; shown = sum(f for _, _, f in mu)
            prs = []
            for a, b, f in mu:
                k = match_calc(teams[a]["R_cal"], a in HOSTS, teams[b]["R_cal"], b in HOSTS, HA, GD, MU, ko=True)
                prs.append(f'<div class="korow"><div class="kop">{_fl(a)} <b>{_nm(a)}</b> '
                           f'<span class="adv">{_pcb(k["advA"])}</span> × <span class="adv">{_pcb(k["advB"])}</span> '
                           f'<b>{_nm(b)}</b> {_fl(b)}</div>'
                           f'<div class="kon">prob. do confronto {f*100:.1f}% · xG {_fx(k["la"])}–{_fx(k["lb"])}</div></div>')
            prs.append(f'<div class="kon" style="margin-top:4px">outros confrontos possíveis: {max(0,(1-shown))*100:.0f}%</div>')
            cells.append(f'<div class="kocell"><div class="kolab">Jogo {mno} — {slotlab(r["home"], r)} × {slotlab(r["away"], r)}</div>{"".join(prs)}</div>')
        out.append(f'<h3 class="koh">{rname}</h3><div class="kogrid">{"".join(cells)}</div>')
    return "".join(out)


# ---- CSS dos cartões (usa tokens do theme.py; cores de DADO inline = verde) ----
CSS = r"""
.gmgrid,.kogrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px}
.gmcard,.kocell{background:var(--card);border:1px solid var(--line);border-radius:11px;padding:10px 12px}
.gmh{font-weight:800;font-size:12px;color:var(--ac);margin:2px 0 8px}
.gmrow{padding:8px 0;border-bottom:1px solid var(--line2)}.gmrow:last-child{border-bottom:0}
.gmt{font-size:13px;line-height:1.3}.gmt b{font-weight:700}.gmx{color:var(--mut);margin:0 4px}
.wdl{display:flex;height:9px;border-radius:4px;overflow:hidden;background:var(--box);margin-top:6px}.wdl i{display:block;height:100%}
.gmn{font-size:10.5px;color:var(--mut);margin-top:5px}
.koh{font-size:12px;color:var(--mut);margin:14px 0 6px;text-transform:uppercase;letter-spacing:.5px}
.kolab{font-size:12px;font-weight:700;color:var(--ac);margin-bottom:6px}
.korow{padding:5px 0;border-bottom:1px solid var(--line2)}.korow:last-of-type{border-bottom:0}
.kop{font-size:13px}.adv{color:var(--win);font-weight:700;font-size:12.5px}
.kon{font-size:10.5px;color:var(--mut);margin-top:1px}
"""
