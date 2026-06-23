#!/usr/bin/env python3
"""
Resolvedor da chave real a partir do estado (Frente 2).

Dado os 72 resultados de grupo (e os de mata-mata já ocorridos), descobre QUAIS times jogam
cada jogo de KO (73..104) e até onde cada seleção chegou. Usado por:
  - bolão: recomendar placar de KO (precisa dos times reais do confronto)
  - comparativo: rastrear fases R16→título (previsto vs real)

`assign_thirds` é cópia fiel de `wc2026_model.assign_thirds` (Anexo C; estrutura fixa da FIFA 2026 —
manter em sincronia manualmente). Desempate de grupo: pts, saldo, gols-pró, nome (determinístico) —
aproxima, NÃO replica, o desempate canônico exato da FIFA (mesma ressalva do HANDOFF §6).
"""

ORDER = ["group", "R32", "R16", "QF", "SF", "Final", "Champion"]


def _allowed_thirds(structure):
    allowed = {r["match"]: set(r["third_from"]) for r in structure["r32"] if "third_from" in r}
    return allowed, structure["third_slot_match_order"]


def assign_thirds(qual_groups, allowed, third_slots):
    """Anexo C: casa cada slot '3rd' a um grupo permitido (pareamento por caminho aumentante)."""
    matchR = {}
    def aug(m, seen):
        for g in sorted(allowed[m]):              # sorted -> determinístico
            if g in qual_groups and g not in seen:
                seen.add(g)
                if g not in matchR or aug(matchR[g], seen):
                    matchR[g] = m; return True
        return False
    for m in third_slots:
        aug(m, set())
    return {m: g for g, m in matchR.items()}      # match -> group


def all_group_teams(fixtures):
    teams = set()
    for f in fixtures["group"]:
        teams.update([f["home"], f["away"]])
    return teams


def group_table(state, fixtures):
    """(table {grupo:[times ordenados]}, pts, gd, gf) dos 72 grupos. None se incompletos."""
    res = (state.get("results", {}) or {}).get("group", []) or []
    if len(res) < 72:
        return None
    gmap = {f["match"]: f for f in fixtures["group"]}
    groups = {}
    for f in fixtures["group"]:
        groups.setdefault(f["group"], set()).update([f["home"], f["away"]])
    pts = {t: 0 for g in groups for t in groups[g]}; gd = dict(pts); gf = dict(pts)
    for r in res:
        fx = gmap[r["match"]]; a, b = fx["home"], fx["away"]; ga, gb = r["hg"], r["ag"]
        gf[a] += ga; gf[b] += gb; gd[a] += ga - gb; gd[b] += gb - ga
        if ga > gb: pts[a] += 3
        elif gb > ga: pts[b] += 3
        else: pts[a] += 1; pts[b] += 1
    key = lambda t: (pts[t], gd[t], gf[t], t)     # nome como desempate final (determinístico, total)
    table = {g: sorted(ts, key=key, reverse=True) for g, ts in groups.items()}
    return table, pts, gd, gf


def resolve_bracket(state, fixtures, structure):
    """
    {matchups: {match#:(home,away) p/ KO já determinável}, reached: {team: fase mais distante},
     qual_groups: [grupos cujo 3º avançou]}  — None se os 72 grupos não estão completos.
    """
    gt = group_table(state, fixtures)
    if gt is None:
        return None
    table, pts, gd, gf = gt
    winner = {g: table[g][0] for g in table}
    runner = {g: table[g][1] for g in table}
    third = {g: table[g][2] for g in table}
    tkey = lambda g: (pts[third[g]], gd[third[g]], gf[third[g]], third[g])
    qual_groups = set(sorted(table.keys(), key=tkey, reverse=True)[:8])
    allowed, third_slots = _allowed_thirds(structure)
    third_assign = assign_thirds(qual_groups, allowed, third_slots)   # match -> group

    def slot(s, mno):
        if s == "3rd":
            return third[third_assign[mno]]
        return winner[s[1]] if s[0] == "1" else runner[s[1]]

    matchups = {}
    for r in structure["r32"]:
        matchups[r["match"]] = (slot(r["home"], r["match"]), slot(r["away"], r["match"]))

    ko_res = {x["match"]: x for x in (state.get("results", {}) or {}).get("knockout", []) or []}
    mw = {}                                        # match -> time vencedor (real)
    rounds = [("R32", structure["r32"]), ("R16", structure["r16"]),
              ("QF", structure["qf"]), ("SF", structure["sf"]), ("Final", [structure["final"]])]
    stage_by_match = {}
    for rd, ms in rounds:
        for r in ms:
            stage_by_match[r["match"]] = rd
    # progride: vencedor real de cada jogo preenche o próximo
    for r in structure["r32"]:
        if r["match"] in ko_res:
            mw[r["match"]] = ko_res[r["match"]]["winner"]
    for rd, ms in (("R16", structure["r16"]), ("QF", structure["qf"]),
                   ("SF", structure["sf"]), ("Final", [structure["final"]])):
        for r in ms:
            hm, am = int(r["home"][1:]), int(r["away"][1:])
            if hm in mw and am in mw:
                matchups[r["match"]] = (mw[hm], mw[am])
                if r["match"] in ko_res:
                    mw[r["match"]] = ko_res[r["match"]]["winner"]

    nxt = {"R32": "R16", "R16": "QF", "QF": "SF", "SF": "Final", "Final": "Champion"}
    reached = {t: "group" for t in all_group_teams(fixtures)}
    def mark(team, stage):
        if ORDER.index(stage) > ORDER.index(reached.get(team, "group")):
            reached[team] = stage
    for g in qual_groups:                          # 8 melhores 3ºs entram no R32
        mark(third[g], "R32")
    for g in table:                                # top-2 entram no R32
        mark(winner[g], "R32"); mark(runner[g], "R32")
    for m, (a, b) in matchups.items():             # participantes alcançam a fase do jogo
        mark(a, stage_by_match[m]); mark(b, stage_by_match[m])
    for m, w in mw.items():                         # vencedor real alcança a próxima
        mark(w, nxt[stage_by_match[m]])
    return {"matchups": matchups, "reached": reached, "qual_groups": sorted(qual_groups)}
