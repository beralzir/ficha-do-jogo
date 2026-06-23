#!/usr/bin/env python3
"""Snapshots timestampados do forecast (data/snapshots/<meta.generated>.json).

Histórico de forecasts para análises comparativas (seção "O que mudou" do
dashboard e Fase 4.2 do PLANO_EXECUCAO). A baseline congelada em data/baseline/
é outra linhagem — imutável, nunca tocada por este módulo.
"""
import glob, hashlib, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP_DIR = os.environ.get("SNAP_DIR") or os.path.join(ROOT, "data", "snapshots")


def _md5(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def snapshot_current(results_path=None, snap_dir=None):
    """Copia o results.json atual para snapshots/<meta.generated>.json.

    Dedupe: conteúdo idêntico a um snapshot existente => não grava nada;
    mesmo generated com conteúdo diferente => sufixo -2, -3, ...
    Retorna o caminho gravado, ou None (nada a fazer).
    """
    results_path = results_path or os.path.join(ROOT, "data", "wc2026_results.json")
    snap_dir = snap_dir or SNAP_DIR
    if not os.path.exists(results_path):
        return None
    with open(results_path) as f:
        generated = json.load(f)["meta"]["generated"]
    os.makedirs(snap_dir, exist_ok=True)
    src_md5 = _md5(results_path)
    for p in sorted(glob.glob(os.path.join(snap_dir, "*.json"))):
        if _md5(p) == src_md5:
            return None  # conteúdo já snapshotado
    dest = os.path.join(snap_dir, f"{generated}.json")
    n = 2
    while os.path.exists(dest):
        dest = os.path.join(snap_dir, f"{generated}-{n}.json")
        n += 1
    with open(results_path) as f:
        data = f.read()
    with open(dest, "w") as f:
        f.write(data)
    return dest


def find_previous(generated, snap_dir=None):
    """Snapshot com maior meta.generated estritamente menor que `generated`.

    Lê o meta de dentro de cada arquivo (não confia no nome). Retorna o dict
    do forecast, ou None se não houver anterior.
    """
    snap_dir = snap_dir or SNAP_DIR
    best, best_gen = None, None
    for p in sorted(glob.glob(os.path.join(snap_dir, "*.json"))):
        try:
            with open(p) as f:
                d = json.load(f)
            g = d["meta"]["generated"]
        except (ValueError, KeyError):
            continue
        if g < generated and (best_gen is None or g > best_gen):
            best, best_gen = d, g
    return best


if __name__ == "__main__":
    dest = snapshot_current()
    print("snapshot:", dest or "nada a fazer (conteúdo já snapshotado)")
    with open(os.path.join(ROOT, "data", "wc2026_results.json")) as f:
        cur = json.load(f)["meta"]["generated"]
    prev = find_previous(cur)
    print("anterior a", cur, "->", prev["meta"]["generated"] if prev else None)
