#!/usr/bin/env python3
"""Registro de modelos do harness multi-modelo (Fase B).

Lê data/model_configs.json (editável à mão) e entrega configs ao motor
(wc2026_model.run_model), ao runner (run_models.py) e ao scorer (compare.py).

Cada config usa pesos MECÂNICOS na escala de força (Elo):
  w_market + w_models  -> convexos (somam ~1)
  opta_in_models       -> fração de Opta dentro de 'models' (resto = Elo)
  QUALK                -> bump aditivo (Elo por unidade do sinal qualitativo)
  SLOPE/HA/GOAL_DIV/MU -> hiperparâmetros do motor
Para o nominal X/Y/Z: w_market = X/(X+Y), w_models = Y/(X+Y) (Z entra via QUALK).
'weights_display' é só rótulo (meta/UI). 'learning' fica null na Fase B.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "data", "model_configs.json")


def load_configs(path=None):
    """Lista de configs (na ordem do arquivo)."""
    with open(path or PATH) as f:
        return json.load(f)["models"]


def get(model_id, path=None):
    for c in load_configs(path):
        if c["id"] == model_id:
            return c
    raise KeyError(f"config de modelo '{model_id}' não existe em {path or PATH}")


def with_env(cfg):
    """Overrides de env (HA/SLOPE/QUALK/GOAL_DIV/MU) sobre uma CÓPIA do config — preserva o
    contrato 'sobrescrevível por env var' do run default do motor. Sem env => config intacto
    (garante o baseline byte-idêntico)."""
    c = dict(cfg)
    for k in ("HA", "SLOPE", "QUALK", "GOAL_DIV", "MU"):
        if k in os.environ:
            c[k] = float(os.environ[k])
    return c


if __name__ == "__main__":
    cs = load_configs()
    print(f"{len(cs)} modelos em {os.path.relpath(PATH, ROOT)}:")
    for c in cs:
        print(f"  {c['id']:14s} w_market={c['w_market']} w_models={c['w_models']} "
              f"opta_in={c['opta_in_models']} QUALK={c['QUALK']} SLOPE={c['SLOPE']} — {c['label']}")
