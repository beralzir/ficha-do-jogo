#!/usr/bin/env python3
"""Congela a previsão de cada modelo do registro (data/model_configs.json) em data/models/<id>.json
— para a UI da Fase D (odds de título por modelo) e a pontuação de FASE ao fim da Copa.
Determinístico (run_model re-semeia seed 42). NÃO mexe em data/wc2026_results.json (baseline publicado).

Condicionamento por tipo de modelo:
  - estático (learning=null): forecast PRÉ-TORNEIO (estado ao vivo zerado) — previsão a ser julgada.
  - learning 'dynamic': forecast AO VIVO REAGIDO — força aprendida com todos os jogos até hoje
    (learn.final_strength) + Monte Carlo CONDICIONADO ao estado real. É a previsão que reage à Copa.
  - learning 'poisson_form': PULADO (calibração-only; ajusta λ por jogo, não vira forecast de fase).

O leaderboard de calibração é separado (src/compare.py, lê os configs direto — não precisa destes JSON).

  python3 src/run_models.py            # n = NFINAL (50k)
  NFINAL=4000 python3 src/run_models.py  # mais rápido p/ teste
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wc2026_model as M
import models as CFG
import learn
import state as ST

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "data", "models")

SUMK = ("champion", "final", "sf", "qf", "r16", "advance", "group_win")
SUMEXP = (1, 2, 4, 8, 16, 32, 12)
MONO = [("advance", "r16"), ("r16", "qf"), ("qf", "sf"), ("sf", "final"), ("final", "champion")]


def _top(res):
    return max(res, key=lambda t: res[t]["champion"])


def _invariants_ok(res):
    sums = {k: round(sum(res[t][k] for t in res), 2) for k in SUMK}
    bad = [k for k, exp in zip(SUMK, SUMEXP) if abs(sums[k] - exp) > 0.02]
    viol = sum(1 for t in res if any(res[t][a] + 1e-9 < res[t][b] for a, b in MONO))
    return (not bad and viol == 0), bad, viol


def main():
    n = int(os.environ.get("NFINAL", M.NFINAL))
    generated = os.environ.get("GENERATED") or time.strftime("%Y-%m-%d")
    os.makedirs(OUTDIR, exist_ok=True)
    fx = ST.load_fixtures()
    live = ST.ManualFileSource().load()
    # estado ao vivo carregado no import do motor — guarda p/ alternar por modelo
    LIVE_FG, LIVE_FK = dict(M.FIXED_GROUP), dict(M.FIXED_KO)
    configs = CFG.load_configs()
    print(f"Congelando forecasts de {len(configs)} modelos (n={n}) -> {os.path.relpath(OUTDIR, ROOT)}/")
    ok_all = True
    for cfg in configs:
        learning = cfg.get("learning")
        typ = (learning or {}).get("type")
        if typ == "poisson_form":
            print(f"  {cfg['id']:16s} (calibração-only — sem forecast de fase)")
            continue
        t0 = time.time()
        if typ == "dynamic":
            M.FIXED_GROUP, M.FIXED_KO = LIVE_FG, LIVE_FK         # condicionado ao estado real
            R = learn.final_strength(cfg, fx, live)               # força aprendida c/ todos os jogos
            out = M.run_model(cfg, n, generated, with_state=True, R=R)
            cond = "ao-vivo reagido"
        else:
            M.FIXED_GROUP, M.FIXED_KO = {}, {}                    # pré-torneio
            out = M.run_model(cfg, n, generated, with_state=False)
            cond = "pré-torneio"
        out["meta"]["model_id"] = cfg["id"]
        out["meta"]["label"] = cfg["label"]
        out["meta"]["conditioning"] = "live-reacted" if typ == "dynamic" else "pre-tournament"
        if learning:
            out["meta"]["learning"] = learning
        with open(os.path.join(OUTDIR, cfg["id"] + ".json"), "w") as f:
            json.dump(out, f, indent=1)
        ok, bad, viol = _invariants_ok(out["teams"])
        ok_all = ok_all and ok
        tag = "OK" if ok else f"FALHA bad={bad} viol={viol}"
        top = _top(out["teams"])
        print(f"  {cfg['id']:16s} {time.time()-t0:4.0f}s  {cond:16s} favorito {top} {out['teams'][top]['champion']*100:4.1f}%  {tag}")
    if not ok_all:
        sys.exit("VERIFICAÇÃO FALHOU — invariante quebrada em algum modelo.")
    print("Todos os forecasts passam somas/monotonicidade.")


if __name__ == "__main__":
    main()
