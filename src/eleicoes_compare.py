#!/usr/bin/env python3
"""
Leaderboard walk-forward · Eleições 2026 (etapa B5).

MÉTRICA PRÉ-ESPECIFICADA (ver data/eleicoes/model_configs.json; definida
ANTES de qualquer medição): para cada freeze F (as_of=D, modelo M) e cada
corrida, a "próxima pesquisa" é a primeira com campo_fim em (D, D+14].
Erro da corrida = MAE entre share previsto e share normalizado da pesquisa,
sobre candidatos com share >= 2% na pesquisa. Score do modelo = média dos
erros das (freeze, corrida) cobertas. Brier vs resultado oficial só no fim
(placeholder até a apuração).

RESSALVAS (viajam no JSON): share de pesquisa != voto; wiki tem latência
1-3 dias; n de comparações pequeno no começo; freezes do mesmo dia veem as
mesmas pesquisas (o walk-forward só discrimina quando o tempo passa).
"""
import datetime as dt
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import eleicoes_model as em  # noqa: E402

OUTDIR = os.path.join(ROOT, "data", "eleicoes", "models")
SCORES = os.path.join(ROOT, "data", "eleicoes", "model_scores.json")
HORIZON_D = 14
MIN_SHARE = 0.02


def next_polls_by_race(polls_doc, after, params):
    by_race = em.usable_polls(polls_doc["polls"], params)
    out = {}
    for race, plist in by_race.items():
        nxt = [p for p in plist if p["campo_fim"] > after]
        if not nxt:
            continue
        first_date = min(p["campo_fim"] for p in nxt)
        lim = (dt.date.fromisoformat(after) + dt.timedelta(days=HORIZON_D)).isoformat()
        if first_date > lim:
            continue
        same_day = [p for p in nxt if p["campo_fim"] == first_date]
        out[race] = same_day
    return out


def score_freeze(freeze, polls_doc, params):
    """Devolve (erro_médio, n_corridas) do freeze contra as próximas pesquisas."""
    nxt = next_polls_by_race(polls_doc, freeze["as_of"], params)
    errs = []
    for race, plist in sorted(nxt.items()):
        pred = freeze["races"].get(race)
        if not pred:
            continue
        # share normalizado médio das pesquisas do dia-alvo
        obs = {}
        for p in plist:
            for sq, sh in em.poll_shares(p).items():
                obs.setdefault(sq, []).append(sh)
        obs = {sq: sum(v) / len(v) for sq, v in obs.items()}
        pairs = [(pred["c"][str(sq)][0], sh) for sq, sh in sorted(obs.items())
                 if sh >= MIN_SHARE and str(sq) in pred["c"]]
        if len(pairs) < 2:
            continue
        errs.append(sum(abs(a - b) for a, b in pairs) / len(pairs))
    return (sum(errs) / len(errs), len(errs)) if errs else (None, 0)


def main():
    if os.path.exists(SCORES):
        with open(SCORES, encoding="utf-8") as f:
            if json.load(f).get("measurement_complete"):
                print("model_scores.json marcado como measurement_complete; não sobrescrevo.")
                sys.exit(0)
    polls_doc = em.load(em.POLLS)
    params = dict(em.DEFAULTS)
    rows = {}
    for path in sorted(glob.glob(os.path.join(OUTDIR, "freeze-*.json"))):
        with open(path, encoding="utf-8") as f:
            fr = json.load(f)
        err, n = score_freeze(fr, polls_doc, params)
        r = rows.setdefault(fr["model"], {"freezes": 0, "comparacoes": 0, "soma_erro": 0.0})
        r["freezes"] += 1
        if err is not None:
            r["comparacoes"] += n
            r["soma_erro"] += err * n
    board = []
    for mid, r in sorted(rows.items()):
        mae = (r["soma_erro"] / r["comparacoes"]) if r["comparacoes"] else None
        board.append({"model": mid, "freezes": r["freezes"], "comparacoes": r["comparacoes"],
                      "mae_share": round(mae, 4) if mae is not None else None})
    board.sort(key=lambda b: (b["mae_share"] is None, b["mae_share"] or 0, b["model"]))
    out = {
        "edition": "eleicoes2026",
        "measurement_complete": False,
        "metric": "MAE de share vs próxima pesquisa (<=14d), candidatos >=2%; Brier vs resultado no fim",
        "caveats": [
            "Share de pesquisa não é voto; mede acompanhamento, não a urna.",
            "Freezes do mesmo dia veem as mesmas pesquisas: o walk-forward só discrimina com o tempo.",
            "n pequeno no início da série; diferenças pequenas são ruído.",
            "Fonte das pesquisas: Wikipédia (latência 1-3 dias; ver docs/fontes-eleicoes.md).",
        ],
        "leaderboard": board,
        "brier_final": None,
    }
    with open(SCORES, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    for b in board:
        mae = f"{b['mae_share']:.4f}" if b["mae_share"] is not None else "  s/dado"
        print(f"  {b['model']:16s} freezes={b['freezes']:3d} comps={b['comparacoes']:4d} mae={mae}")
    print(f"OK -> data/eleicoes/model_scores.json")


if __name__ == "__main__":
    main()
