#!/usr/bin/env python3
"""Fecha a medição do harness ao FIM da Copa (roda uma vez): grupos + mata-mata + fase/título.

Produz data/model_scores.json (schema retrocompatível + campos novos):
  - Por modelo: brier/logloss/n_matches passam a cobrir TODOS os jogos medidos (72 grupos +
    31 KO); *_group e *_ko separados; pontos dacopa/exatos incluem KO (multiplicador 2x da regra).
  - Fase/título (só modelos com forecast): Brier dos marcadores r16/qf/sf/final/champion e
    log-loss do título usando o CONGELAMENTO DA VÉSPERA DO MATA-MATA (commit e5d934f,
    as_of 2026-06-28: 72 jogos de grupo, 0 KO, chave já corrigida) vs a realidade; e a
    trajetória p(campeã real) por congelamento diário (histórico git de data/models/).
  - measurement_complete: true · ranking: "final" · caveats reescritos.

Decisões de medição (declaradas nos caveats e na retrospectiva):
  * Walk-forward também no KO: modelos 'learning' seguem aprendendo com os jogos de KO
    anteriores (ordem = match id; as rodadas do KO são sequenciais no calendário).
  * Elo/forma no KO usam o placar do fim da prorrogação (pênaltis = empate p/ o rating).
  * 1X2 do KO no espaço {H, D=pênaltis, A} dos 120 min, via bolao.score_dist_ko.
  * Jogo 103 (3º lugar) não entrou na ingestão -> medição sobre 31/32 jogos de KO.
  * Fase: estáticos = leitura PRÉ-TORNEIO congelada; dinâmicos = leitura pós-grupos
    (aprendida + condicionada). A comparação mede "reagir à Copa ajudou a ler o mata-mata?".

Determinístico; usa `git show` p/ ler os freezes históricos (repo = fonte da verdade).
Depois de rodar, compare.py se recusa a sobrescrever (guarda measurement_complete).
"""
import json
import math
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bolao
import compare
import learn
import models as CFG
import state as ST
import wc2026_model as M

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "model_scores.json")

# Véspera do mata-mata: grupos completos, 0 jogos de KO, chave dos 32-avos já corrigida (PR #4).
MILESTONE_SHA = "e5d934f"
MARKERS = ("r16", "qf", "sf", "final", "champion")

CAVEATS_FINAL = [
    "Medição FINAL da edição: 1X2 de 103 dos 104 jogos (o 3º lugar, jogo 103, não foi capturado pela ingestão) + fase/título pela véspera do mata-mata (as_of 2026-06-28).",
    "Uma Copa ainda é UMA amostra: diferenças pequenas de Brier seguem dentro do ruído (erro-padrão ~0,006 em n=103). Ranking final DESTA edição, não lei geral.",
    "market_only = consenso de odds, que já incorpora o Opta (odds coletadas depois do Opta, corr ~0,98) — não é 'mercado puro sem modelos'. 'market_only vence' = 'o consenso calibra melhor que diluí-lo no blend', e NÃO refuta Opta/Elo isoladamente.",
    "Pesos pré-especificados antes do torneio: nenhum parâmetro foi ajustado a estes jogos (sem p-hacking); baseline = fórmula 45/35/20.",
    "Mata-mata medido no espaço dos 120 min: 'empate' = decisão nos pênaltis (4 jogos). Para o rating dos modelos que aprendem, pênaltis contam como empate.",
    "Fase/título: modelos estáticos são julgados pela leitura PRÉ-TORNEIO congelada; dinâmicos pela leitura pós-grupos (aprendida e condicionada — reagir é a proposta deles). A comparação responde se reagir à Copa ajudou a ler o mata-mata.",
]


def _git_json(sha, relpath):
    r = subprocess.run(["git", "show", f"{sha}:{relpath}"],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def freeze_history():
    """[(data, sha)] — último commit de cada dia que tocou data/models (mais antigo -> recente)."""
    r = subprocess.run(["git", "log", "--format=%h %ad", "--date=short", "--", "data/models"],
                       cwd=ROOT, capture_output=True, text=True, check=True)
    seen, out = set(), []
    for line in r.stdout.splitlines():  # log vem do mais recente p/ o mais antigo
        sha, date = line.split()
        if date not in seen:
            seen.add(date)
            out.append((date, sha))
    return list(reversed(out))


def played_ko(state):
    return sorted(state["results"]["knockout"], key=lambda r: r["match"])


def ko_lams(cfg, fx, state):
    """{match: (la, lb)} p/ jogos de KO, walk-forward (λ da véspera, sem look-ahead)."""
    ko = played_ko(state)
    typ = (cfg.get("learning") or {}).get("type")
    lam = {}
    if not typ:
        R = M.build_strengths(cfg)
        for r in ko:
            lam[r["match"]] = learn._lams_from_R(R, r["home"], r["away"], cfg)
        return lam
    if typ == "dynamic":
        _, R = learn.dynamic_R_timeline(cfg, fx, state)  # força pós-grupos
        K = float(cfg["learning"].get("K", 20.0))
        for r in ko:
            a, b = r["home"], r["away"]
            lam[r["match"]] = learn._lams_from_R(R, a, b, cfg)
            dr = (R[a] + (cfg["HA"] if a in M.HOSTS else 0)) - (R[b] + (cfg["HA"] if b in M.HOSTS else 0))
            exp_a = 1.0 / (1.0 + 10 ** (-dr / 400.0))
            ga, gb = r["hg"], r["ag"]
            res_a = 1.0 if ga > gb else (0.5 if ga == gb else 0.0)  # pênaltis = empate p/ rating
            delta = K * learn._margin_mult(abs(ga - gb)) * (res_a - exp_a)
            R[a] += delta
            R[b] -= delta
        return lam
    if typ == "poisson_form":
        _, (att, dfn) = learn.poisson_form_timeline(cfg, fx, state)  # multiplicadores pós-grupos
        R0 = M.build_strengths(cfg)
        eta = float(cfg["learning"].get("eta", 0.2))
        for r in ko:
            a, b = r["home"], r["away"]
            la0, lb0 = learn._lams_from_R(R0, a, b, cfg)
            la = max(0.15, la0 * att[a] * dfn[b])
            lb = max(0.15, lb0 * att[b] * dfn[a])
            lam[r["match"]] = (la, lb)
            ga, gb = r["hg"], r["ag"]
            ext = 1.34 if (ga == gb or (r.get("decided_by") or "reg") != "reg") else 1.0
            ea, eb = la * ext, lb * ext  # jogo com prorrogação: esperado em 120min
            ra_ = (ga + 0.5) / (ea + 0.5)
            rb_ = (gb + 0.5) / (eb + 0.5)
            att[a] *= (1 - eta) + eta * ra_
            dfn[b] *= (1 - eta) + eta * ra_
            att[b] *= (1 - eta) + eta * rb_
            dfn[a] *= (1 - eta) + eta * rb_
        return lam
    raise ValueError(f"learning.type desconhecido: {typ!r}")


def score_ko(cfg, fx, state):
    """Scorecard 1X2/pontos dos jogos de KO (espaço 120min: D = pênaltis)."""
    lam = ko_lams(cfg, fx, state)
    brier = ll = 0.0
    n = seguro = ousado = exact_ev = exact_bold = 0
    for r in played_ko(state):
        la, lb = lam[r["match"]]
        dist = bolao.score_dist_ko(la, lb)
        ph = sum(p for (i, j), p in dist.items() if i > j)
        pd = sum(p for (i, j), p in dist.items() if i == j)
        pa = max(0.0, 1 - ph - pd)
        p = {"H": ph, "D": pd, "A": pa}
        ga, gb = r["hg"], r["ag"]
        o = "H" if ga > gb else ("A" if ga < gb else "D")
        brier += sum((p[k] - (1.0 if k == o else 0.0)) ** 2 for k in ("H", "D", "A"))
        ll += -math.log(max(p[o], 1e-12))
        n += 1
        ev_pick = bolao.best_pick(dist, True)[0]
        ml_pick = max(dist.items(), key=lambda z: z[1])[0]
        seguro += bolao.dacopa_points(ev_pick, (ga, gb), True)
        ousado += bolao.dacopa_points(ml_pick, (ga, gb), True)
        exact_ev += 1 if tuple(ev_pick) == (ga, gb) else 0
        exact_bold += 1 if tuple(ml_pick) == (ga, gb) else 0
    return {"n": n, "brier": brier / n, "logloss": ll / n, "seguro": seguro,
            "ousado": ousado, "exact_ev": exact_ev, "exact_bold": exact_bold}


def realized_phase_sets(state):
    """Conjuntos realizados por marcador a partir dos vencedores do KO."""
    win = {r["match"]: r["winner"] for r in played_ko(state)}
    sets = {
        "r16": {win[m] for m in range(73, 89) if m in win},
        "qf": {win[m] for m in range(89, 97) if m in win},
        "sf": {win[m] for m in range(97, 101) if m in win},
        "final": {win[m] for m in range(101, 103) if m in win},
        "champion": {win[104]} if 104 in win else set(),
    }
    return sets, (win.get(104))


def score_phase(mid, sets):
    """Brier de fase + log-loss de título do freeze da véspera do mata-mata (None se sem forecast)."""
    frozen = _git_json(MILESTONE_SHA, f"data/models/{mid}.json")
    if not frozen:
        return None
    teams = frozen["teams"]
    champ = next(iter(sets["champion"])) if sets["champion"] else None
    markers = {}
    for mk in MARKERS:
        s = 0.0
        for t, d in teams.items():
            y = 1.0 if t in sets[mk] else 0.0
            s += (float(d[mk]) - y) ** 2
        markers[mk] = round(s / len(teams), 4)
    p_champ = float(teams[champ]["champion"]) if champ and champ in teams else None
    return {
        "milestone_as_of": frozen.get("meta", {}).get("generated"),
        "conditioning": frozen.get("meta", {}).get("conditioning", "live"),
        "markers": markers,
        "brier_phase": round(sum(markers.values()) / len(markers), 4),
        "champion_p": round(p_champ, 5) if p_champ is not None else None,
        "champion_ll": round(-math.log(max(p_champ, 1e-12)), 4) if p_champ is not None else None,
    }


def trajectory(mids, champ):
    """{mid: [{date, p}]} — p(campeã real) a cada congelamento diário do histórico."""
    out = {m: [] for m in mids}
    for date, sha in freeze_history():
        for m in mids:
            j = _git_json(sha, f"data/models/{m}.json")
            if not j or champ not in j.get("teams", {}):
                continue
            out[m].append({"date": date, "p": round(float(j["teams"][champ]["champion"]), 5)})
    return {m: pts for m, pts in out.items() if pts}


def main():
    fx = ST.load_fixtures()
    state = ST.ManualFileSource().load()
    errs = ST.validate_state(state, fx)
    if errs:
        sys.exit("ESTADO INVÁLIDO: " + "; ".join(errs))

    prev = json.load(open(OUT)) if os.path.exists(OUT) else {}
    prev_models = prev.get("models", {})

    sets, champ = realized_phase_sets(state)
    if not champ:
        sys.exit("Sem campeão no estado (jogo 104) — a Copa não terminou; nada a fechar.")

    cards = {}
    for cfg in CFG.load_configs():
        g = compare.score_config(cfg, fx, state)  # bloco de GRUPOS — idêntico ao preliminar
        k = score_ko(cfg, fx, state)
        # continuidade: o Brier de grupos tem de reproduzir o número publicado no preliminar
        pg = prev_models.get(cfg["id"], {})
        if pg.get("brier") is not None and not prev.get("measurement_complete"):
            if abs(pg["brier"] - g["brier"]) > 1e-9:
                sys.exit(f"REGRESSÃO: brier de grupos de {cfg['id']} mudou "
                         f"({pg['brier']} -> {g['brier']}). Abortando sem escrever.")
        n_all = g["n_matches"] + k["n"]
        cards[cfg["id"]] = {
            "label": g["label"], "learning": g["learning"],
            "n_matches": n_all, "n_group": g["n_matches"], "n_ko": k["n"],
            "brier": round((g["brier"] * g["n_matches"] + k["brier"] * k["n"]) / n_all, 4),
            "logloss": round((g["logloss"] * g["n_matches"] + k["logloss"] * k["n"]) / n_all, 4),
            "brier_group": g["brier"], "logloss_group": g["logloss"],
            "brier_ko": round(k["brier"], 4), "logloss_ko": round(k["logloss"], 4),
            "calib_n": n_all,
            "seguro_pts": g["seguro_pts"] + k["seguro"], "ousado_pts": g["ousado_pts"] + k["ousado"],
            "seguro_pts_group": g["seguro_pts"], "ousado_pts_group": g["ousado_pts"],
            "exact_ev": g["exact_ev"] + k["exact_ev"], "exact_bold": g["exact_bold"] + k["exact_bold"],
            "exact_ev_rate": round((g["exact_ev"] + k["exact_ev"]) / n_all, 4),
            "has_forecast": g["has_forecast"],
            "phase": score_phase(cfg["id"], sets) if g["has_forecast"] else None,
        }

    mkt = cards.get("market_only", {}).get("brier")
    for c in cards.values():
        c["value_vs_market"] = (round(c["brier"] - mkt, 4) if mkt is not None else None)

    traj = trajectory([m for m, c in cards.items() if c["has_forecast"]], champ)

    out = {
        "as_of": state.get("as_of"), "champion": champ,
        "n_matches": next(iter(cards.values()))["n_matches"],
        "n_group": next(iter(cards.values()))["n_group"],
        "n_ko": next(iter(cards.values()))["n_ko"],
        "missing_matches": [103],
        "measurement_complete": True, "ranking": "final",
        "milestone": {"sha": MILESTONE_SHA, "as_of": "2026-06-28",
                      "note": "véspera do mata-mata: 72 jogos de grupo fechados, 0 KO, chave corrigida"},
        "caveats": CAVEATS_FINAL,
        "models": cards,
        "trajectory": traj,
    }
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)

    order = sorted(cards, key=lambda m: cards[m]["brier"])
    print(f"=== LEADERBOARD FINAL — {out['n_matches']} jogos (72 grupos + {out['n_ko']} KO) · campeã: {champ} ===")
    print(f"{'modelo':16s}{'Brier':>8}{'grupos':>8}{'KO':>8}{'vs_mkt':>8}{'fase':>7}{'p(tít.)':>9}{'Seg':>6}{'Ous':>6}")
    for m in order:
        c = cards[m]
        ph = c["phase"] or {}
        fase = f"{ph['brier_phase']:.4f}" if ph else "—"
        ptit = f"{ph['champion_p']:.3f}" if ph.get("champion_p") is not None else "—"
        print(f"{m:16s}{c['brier']:>8.4f}{c['brier_group']:>8.4f}{c['brier_ko']:>8.4f}"
              f"{c['value_vs_market']:>+8.4f}{fase:>7}{ptit:>9}{c['seguro_pts']:>6}{c['ousado_pts']:>6}")
    print("\nCaveats finais:")
    for cv in CAVEATS_FINAL:
        print(f"  • {cv}")
    print(f"\nescrito: {os.path.relpath(OUT, ROOT)} (measurement_complete=True)")


if __name__ == "__main__":
    main()
