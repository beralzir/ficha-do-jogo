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


class SemLastro(Exception):
    """Modelo sintético sem pesquisa sintética no polls.json (fail-closed)."""


def motor(engine):
    """Resolve o nome do motor no config para a função de simulação.

    MOTOR != VARIANTE. As cinco variantes do oficial são o mesmo motor com
    parâmetros diferentes, e o leaderboard mostrou que não discriminam (0,3
    milésimo de MAE entre elas). Um `engine` novo é um modelo ESTRUTURALMENTE
    diferente, que é a única coisa que o walk-forward consegue medir.
    Import adiado: o v2 importa este módulo de volta para o --freeze.
    """
    if engine in (None, "oficial"):
        return em.simulate
    if engine == "v2_estado":
        import eleicoes_model_v2 as v2
        return v2.simulate_v2
    raise ValueError(f"engine desconhecido no model_configs.json: {engine!r}")


def freeze_um(mid, structure, polls_doc, params_cfg, simulate_fn=None):
    """Grava o freeze de UM modelo. True = gravou, False = já existia.

    Escritor ÚNICO de freeze, de propósito. O fail-closed de POLL_SOURCE e a
    checagem de invariantes moram aqui; um segundo escritor seria um segundo
    lugar para esquecê-los, e esquecer o fail-closed é a classe de bug que o C3
    corrigiu no motor oficial em 31/08.
    """
    params = dict(em.DEFAULTS)
    params.update(params_cfg or {})
    n_sinteticas = sum(1 for p in polls_doc.get("polls", []) if p.get("sintetico"))
    if params.get("POLL_SOURCE", "real") in ("sintetico", "ambos") and not n_sinteticas:
        raise SemLastro(params["POLL_SOURCE"])
    out = (simulate_fn or em.simulate)(structure, polls_doc, params, verbose=False)
    bad = em.check_invariants(out)
    if bad:
        print(f"{mid}: INVARIANTE VIOLADA, freeze abortado: {bad[:2]}")
        sys.exit(1)
    as_of = out["meta"]["as_of"]
    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, f"freeze-{as_of}-{mid}.json")
    if os.path.exists(path):
        return False
    compact = {"model": mid, "as_of": as_of, "params": params_cfg or {}, "races": {}}
    for key, r in sorted(out["races"].items()):
        compact["races"][key] = {
            "quality": r["data_quality"],
            "c": {str(c["sq"]): [c["share"], c["eleito"]] for c in r["candidates"]},
        }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(compact, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    print(f"  freeze {as_of} {mid}")
    return True


def main():
    with open(CONFIGS, encoding="utf-8") as f:
        cfg = json.load(f)
    structure = em.load(em.STRUCT)
    polls_doc = em.load(em.POLLS)
    os.makedirs(OUTDIR, exist_ok=True)
    made = skipped = sem_lastro = 0
    for mid in sorted(cfg["models"]):
        conf = cfg["models"][mid]
        try:
            feito = freeze_um(mid, structure, polls_doc, conf.get("params", {}),
                              simulate_fn=motor(conf.get("engine")))
        except SemLastro as e:
            sem_lastro += 1
            print(f"  PULADO {mid}: declara POLL_SOURCE={str(e)!r} e não há "
                  f"pesquisa sintética no polls.json. Freeze de prior vazio viraria "
                  f"histórico de acerto falso no leaderboard.")
            continue
        made += int(feito)
        skipped += int(not feito)
    resumo = f"OK: {made} freeze(s) novos, {skipped} já existiam."
    if sem_lastro:
        resumo += (f" {sem_lastro} modelo(s) sintético(s) PULADOS por falta de lastro "
                   f"(rode src/synths_para_polls.py quando o campo existir).")
    print(resumo)


if __name__ == "__main__":
    main()
