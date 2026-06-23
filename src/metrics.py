#!/usr/bin/env python3
"""
Métricas previsto × realizado (Frente 2) — a partir do forecast (results.json), da baseline
pré-torneio e do estado ao vivo (jogos ocorridos).

Dimensões:
  A) Placar: por jogo concluído, as leituras Seguro (EV-pick) e Ousado (modal) do modelo
     vs placar real + pontos dacopa de cada uma. Seguro e Ousado saem da MESMA distribuição de
     placar — mudam só a estratégia (maior EV × placar mais provável), não o modelo.
  C) Calibração: Brier + log-loss do 1X2 do modelo nos jogos de grupo concluídos (comum às duas vias).
  B) Fase (nível avanço): P(advance) da baseline vs quem REALMENTE avançou (top2 + 8 melhores 3ºs),
     quando os 72 jogos de grupo estiverem completos.

Nota: 'actual_advancers' usa desempate pts/saldo/gols-pró + alfabético (determinístico) — aproxima,
não replica, o desempate canônico exato da FIFA (mesma ressalva do HANDOFF §6 p/ terceiros).
λ vêm de R_cal (estáticos), então a recomendação/1X2 de um jogo não dependem do condicionamento.
"""
import math, os
import bolao

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _outcome(hg, ag):
    return "H" if hg > ag else ("A" if hg < ag else "D")


def match_reports(model, fixtures, state):
    """Por jogo concluído: placar real, leituras Seguro (EV) e Ousado (modal) + pontos de cada,
    1X2 (grupo)."""
    gmap = {f["match"]: f for f in fixtures["group"]}
    komap = {f["match"]: f for f in fixtures["knockout"]}
    out = []
    res = state.get("results", {}) or {}

    for r in res.get("group", []) or []:
        fx = gmap[r["match"]]; a, b = fx["home"], fx["away"]
        actual = (r["hg"], r["ag"])
        rec = bolao.recommend(model, a, b, ko=False)
        la, lb = bolao.lams_for(model, a, b); d = bolao.score_dist_group(la, lb)
        ph = sum(p for (i, j), p in d.items() if i > j)
        pd = sum(p for (i, j), p in d.items() if i == j)
        pa = max(0.0, 1 - ph - pd)
        mp = bolao.dacopa_points(tuple(rec["ev_pick"]), actual, ko=False)
        bp = bolao.dacopa_points(tuple(rec["bold_pick"]), actual, ko=False)
        out.append({"match": r["match"], "stage": "group", "a": a, "b": b, "actual": list(actual),
                    "outcome": _outcome(*actual),
                    "model_pick": rec["ev_pick"], "model_pts": mp,
                    "bold_pick": rec["bold_pick"], "bold_pts": bp,
                    "p1x2": {"H": round(ph, 4), "D": round(pd, 4), "A": round(pa, 4)}})

    for r in res.get("knockout", []) or []:
        fx = komap.get(r["match"], {}); a, b = r["home"], r["away"]
        actual = (r["hg"], r["ag"])
        rec = bolao.recommend(model, a, b, ko=True)
        mp = bolao.dacopa_points(tuple(rec["ev_pick"]), actual, ko=True)
        bp = bolao.dacopa_points(tuple(rec["bold_pick"]), actual, ko=True)
        out.append({"match": r["match"], "stage": fx.get("stage", "KO"), "a": a, "b": b,
                    "actual": list(actual), "outcome": _outcome(*actual),
                    "model_pick": rec["ev_pick"], "model_pts": mp,
                    "bold_pick": rec["bold_pick"], "bold_pts": bp})
    return out


def summarize(reports):
    """Totais de pontos (Seguro · Ousado) + calibração 1X2 (Brier/log-loss) sobre jogos de grupo."""
    model_pts = sum(r["model_pts"] for r in reports)
    bold_pts = sum(r["bold_pts"] for r in reports)
    brier, ll, n = 0.0, 0.0, 0
    for r in reports:
        if r["stage"] != "group":
            continue
        p = r["p1x2"]; o = r["outcome"]; n += 1
        brier += sum((p[k] - (1.0 if k == o else 0.0)) ** 2 for k in ("H", "D", "A"))
        ll += -math.log(max(p[o], 1e-12))
    return {"n_matches": len(reports), "model_pts": model_pts, "bold_pts": bold_pts,
            "brier": round(brier / n, 4) if n else None,
            "logloss": round(ll / n, 4) if n else None, "calib_n": n}


def actual_advancers(state, fixtures):
    """Quem avançou de fato (top2 de cada grupo + 8 melhores 3ºs). None se os 72 grupos não estão completos."""
    gmap = {f["match"]: f for f in fixtures["group"]}
    res = (state.get("results", {}) or {}).get("group", []) or []
    if len(res) < 72:
        return None
    groups = {}
    for f in fixtures["group"]:
        groups.setdefault(f["group"], set()).update([f["home"], f["away"]])
    pts = {t: 0 for g in groups for t in groups[g]}
    gd = dict(pts); gf = dict(pts)
    for r in res:
        fx = gmap[r["match"]]; a, b = fx["home"], fx["away"]; ga, gb = r["hg"], r["ag"]
        gf[a] += ga; gf[b] += gb; gd[a] += ga - gb; gd[b] += gb - ga
        if ga > gb: pts[a] += 3
        elif gb > ga: pts[b] += 3
        else: pts[a] += 1; pts[b] += 1
    key = lambda t: (pts[t], gd[t], gf[t], -ord(t[0]))  # alfabético inverso como desempate determinístico
    advanced, thirds = set(), []
    for g, ts in groups.items():
        order = sorted(ts, key=key, reverse=True)
        advanced.update(order[:2]); thirds.append(order[2])
    thirds.sort(key=key, reverse=True)
    advanced.update(thirds[:8])
    return advanced


def phase_advance_report(baseline, state, fixtures):
    """Por seleção: P(advance) da baseline vs avanço real (0/1), quando os grupos fecharem."""
    adv = actual_advancers(state, fixtures)
    if adv is None:
        return {"ready": False, "rows": []}
    tb = baseline["teams"]
    rows = [{"team": t, "forecast_advance": round(tb[t]["advance"], 4),
             "actual_advanced": 1 if t in adv else 0} for t in tb]
    rows.sort(key=lambda r: -r["forecast_advance"])
    return {"ready": True, "rows": rows}
