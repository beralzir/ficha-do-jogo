#!/usr/bin/env python3
"""Prêmios individuais (Chuteira de Ouro / Luva de Ouro) — odds de mercado de-vigged.

Fonte única do método de de-vig dos prêmios; consumido por build_dashboard,
build_bolao e build_comparativo. O motor (nível-seleção) NÃO gera dado de jogador —
estas probabilidades vêm 100% do mercado (mesma normalização proporcional do título).
Schema de data/wc2026_awards.json:
  meta: {collected, method, sources, overround}
  golden_boot / golden_glove: [ {player, team(EN canônico), pos, odds, p_raw, p} ]
  p em fração [0,1]; Σp = 1 por mercado; `p` é recomputado das odds no load (pega edição manual).
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "data", "wc2026_awards.json")
MARKETS = ("golden_boot", "golden_glove")


def devig(odds_list):
    """Normalização proporcional: p_i = (1/o_i) / Σ(1/o_j). Mesmo método do título."""
    inv = [1.0 / o for o in odds_list]
    s = sum(inv)
    return [x / s for x in inv]


def validate(data, teams48=None):
    """Lista de erros (vazia = ok). Recomputa o de-vig e confere com o `p` gravado."""
    errs = []
    for mk in MARKETS:
        rows = data.get(mk) or []
        if not rows:
            errs.append(f"{mk}: lista vazia/ausente")
            continue
        bad = False
        for r in rows:
            if not str(r.get("player", "")).strip():
                errs.append(f"{mk}: player vazio"); bad = True
            o = r.get("odds")
            if not (isinstance(o, (int, float)) and o > 1):
                errs.append(f"{mk}/{r.get('player', '?')}: odds inválida ({o!r})"); bad = True
            if teams48 is not None and r.get("team") not in teams48:
                errs.append(f"{mk}/{r.get('player', '?')}: team '{r.get('team')}' não é uma das 48"); bad = True
        if bad:
            continue
        ps = devig([r["odds"] for r in rows])
        for r, p in zip(rows, ps):
            if abs(float(r.get("p", -1)) - p) > 1e-6:
                errs.append(f"{mk}/{r['player']}: p={r.get('p')} difere do de-vig recomputado {p:.6f}")
    return errs


def load(path=None, teams48=None):
    """Lê e valida o awards.json. None se o arquivo não existe (páginas degradam com honestidade)."""
    path = path or PATH
    if not os.path.exists(path):
        return None
    with open(path) as f:
        data = json.load(f)
    errs = validate(data, teams48)
    if errs:
        raise SystemExit("wc2026_awards.json inválido:\n  - " + "\n  - ".join(errs))
    return data


if __name__ == "__main__":
    t48 = None
    fxp = os.path.join(ROOT, "data", "fixtures.json")
    if os.path.exists(fxp):
        with open(fxp) as f:
            fx = json.load(f)
        t48 = {g["home"] for g in fx["group"]} | {g["away"] for g in fx["group"]}
    d = load(teams48=t48)
    if d is None:
        print("data/wc2026_awards.json ainda não existe — nada a validar.")
    else:
        for mk in MARKETS:
            rows = d[mk]
            print(f"{mk}: {len(rows)} candidatos · Σp={sum(r['p'] for r in rows):.6f} · "
                  f"favorito: {rows[0]['player']} ({rows[0]['p'] * 100:.1f}%)")
        print("meta:", d["meta"]["collected"], "· fontes:", ", ".join(d["meta"]["sources"]))
