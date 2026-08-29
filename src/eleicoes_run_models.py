#!/usr/bin/env python3
"""
Harness multi-modelo · Eleições 2026 (etapa B5): congela o forecast de cada
modelo registrado em data/eleicoes/model_configs.json.

Freeze = data/eleicoes/models/freeze-<as_of>-<modelo>.json com shares e
P(eleito) compactos por corrida. Congelar é barato e é o ativo de pesquisa
que permite medição retroativa honesta (aprendizado da Copa, retrospectiva §5.8).
Idempotente: freeze existente do mesmo (as_of, modelo) não é regravado
(rode após o ingest do dia; determinístico dado o polls.json).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import eleicoes_model as em  # noqa: E402

CONFIGS = os.path.join(ROOT, "data", "eleicoes", "model_configs.json")
OUTDIR = os.path.join(ROOT, "data", "eleicoes", "models")


def main():
    with open(CONFIGS, encoding="utf-8") as f:
        cfg = json.load(f)
    structure = em.load(em.STRUCT)
    polls_doc = em.load(em.POLLS)
    os.makedirs(OUTDIR, exist_ok=True)
    made = skipped = 0
    for mid in sorted(cfg["models"]):
        params = dict(em.DEFAULTS)
        params.update(cfg["models"][mid].get("params", {}))
        out = em.simulate(structure, polls_doc, params, verbose=False)
        bad = em.check_invariants(out)
        if bad:
            print(f"{mid}: INVARIANTE VIOLADA, freeze abortado: {bad[:2]}")
            sys.exit(1)
        as_of = out["meta"]["as_of"]
        path = os.path.join(OUTDIR, f"freeze-{as_of}-{mid}.json")
        if os.path.exists(path):
            skipped += 1
            continue
        compact = {"model": mid, "as_of": as_of, "params": cfg["models"][mid].get("params", {}),
                   "races": {}}
        for key, r in sorted(out["races"].items()):
            compact["races"][key] = {
                "quality": r["data_quality"],
                "c": {str(c["sq"]): [c["share"], c["eleito"]] for c in r["candidates"]},
            }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(compact, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")
        made += 1
        print(f"  freeze {as_of} {mid}")
    print(f"OK: {made} freeze(s) novos, {skipped} já existiam.")


if __name__ == "__main__":
    main()
