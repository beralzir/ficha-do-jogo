#!/usr/bin/env python3
"""
Harness multi-modelo · Eleições 2026 (etapa B5): congela o forecast de cada
modelo registrado em data/eleicoes/model_configs.json.

Freeze = data/eleicoes/models/freeze-<as_of>-<modelo>.json com shares e
P(eleito) compactos por corrida. Congelar é barato e é o ativo de pesquisa
que permite medição retroativa honesta (aprendizado da Copa, retrospectiva §5.8).
Idempotente: freeze existente do mesmo (as_of, modelo) não é regravado
(rode após o ingest do dia; determinístico dado o polls.json).

FAIL-CLOSED para modelo sintético (18/09/2026). Modelo que declara
POLL_SOURCE sintetico ou ambos só congela se EXISTIR pesquisa sintética no
polls.json. Sem isso, o motor cai no prior de "corrida sem pesquisa" e produz
um freeze que não mede nada, mas que o `eleicoes_compare.py` conta como se
medisse: o leaderboard da página Modelos publicaria histórico de acerto de um
competidor que nunca rodou.

Não é hipótese. O `ingest_polls.py` reescreve o polls.json inteiro a cada
rodada e não preserva a linha sintética (ela nasce no `synths_para_polls.py`),
então o synth some no primeiro ciclo do cron. Medido: `synths_solo` ia de 1
freeze e 54 comparações para 2 e 108, ganhando um freeze falso por DIA.

É a mesma regra do motor, que recusa pesquisa sem a flag `sintetico` em vez de
assumir que é real: na dúvida, o sistema para e declara, não preenche sozinho.
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
    n_sinteticas = sum(1 for p in polls_doc.get("polls", []) if p.get("sintetico"))
    os.makedirs(OUTDIR, exist_ok=True)
    made = skipped = sem_lastro = 0
    for mid in sorted(cfg["models"]):
        params = dict(em.DEFAULTS)
        params.update(cfg["models"][mid].get("params", {}))
        # fail-closed: sintético sem lastro não congela (ver docstring)
        if params.get("POLL_SOURCE", "real") in ("sintetico", "ambos") and not n_sinteticas:
            sem_lastro += 1
            print(f"  PULADO {mid}: declara POLL_SOURCE={params['POLL_SOURCE']!r} e não há "
                  f"pesquisa sintética no polls.json. Freeze de prior vazio viraria "
                  f"histórico de acerto falso no leaderboard.")
            continue
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
    resumo = f"OK: {made} freeze(s) novos, {skipped} já existiam."
    if sem_lastro:
        resumo += (f" {sem_lastro} modelo(s) sintético(s) PULADOS por falta de lastro "
                   f"(rode src/synths_para_polls.py quando o campo existir).")
    print(resumo)


if __name__ == "__main__":
    main()
