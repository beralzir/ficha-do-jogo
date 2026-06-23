#!/usr/bin/env python3
"""
Camada de estado ao vivo + fonte de dados (Frente 2).

- ManualFileSource: lê resultados+palpites de um JSON editado à mão (data/live/state.json).
  É a implementação concreta de DataSource; um adaptador de API futuro implementa a mesma
  interface (.load()) sem o motor saber a diferença.
- validate_state: checa o estado contra fixtures.json (não lança; devolve lista de erros).
- build_fixed: traduz o estado em (FIXED_GROUP, FIXED_KO) consumidos pelo motor condicional.

Schema (ver HANDOFF §5):
  results.group:    [ {match, hg, ag} ]                                   # gols de home/away conforme fixtures
  results.knockout: [ {match, home, away, hg, ag, winner, decided_by} ]   # times reais; hg/ag=fim da prorrogação (pênaltis não contam); winner fixa a chave
  results.awards:   { golden_boot?: {player, team}, golden_glove?: {player, team} }  # prêmio CONHECIDO (fim do torneio)
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "data")


def load_fixtures(path=None):
    with open(path or f"{BASE}/fixtures.json") as f:
        return json.load(f)


class DataSource:
    """Interface mínima. .load() devolve o dict de estado (schema state.json)."""
    def load(self) -> dict:
        raise NotImplementedError


class ManualFileSource(DataSource):
    """Resultados+palpites de um arquivo JSON editado à mão."""
    def __init__(self, path=None):
        self.path = path or f"{BASE}/live/state.json"

    def load(self) -> dict:
        if not os.path.exists(self.path):
            return {"as_of": None, "results": {"group": [], "knockout": []}}
        with open(self.path) as f:
            return json.load(f)


def _nat(x):
    return isinstance(x, int) and x >= 0


def is_empty(state):
    r = state.get("results", {}) or {}
    return not r.get("group") and not r.get("knockout")


def validate_state(state, fixtures):
    """Lista de erros (vazia = ok). Não lança."""
    errs = []
    gmap = {f["match"]: f for f in fixtures["group"]}
    komap = {f["match"]: f for f in fixtures["knockout"]}
    res = state.get("results", {}) or {}

    seen_g = set()
    for r in res.get("group", []) or []:
        m = r.get("match")
        if m not in gmap:
            errs.append(f"group result m{m} não existe em fixtures"); continue
        if m in seen_g:
            errs.append(f"group result m{m} duplicado")
        seen_g.add(m)
        if not (_nat(r.get("hg")) and _nat(r.get("ag"))):
            errs.append(f"m{m}: gols inválidos (use inteiros >= 0)")

    ko = res.get("knockout", []) or []
    if ko and len(res.get("group", []) or []) < 72:
        errs.append("resultados de mata-mata exigem os 72 jogos de grupo preenchidos (a chave depende deles)")
    for r in ko:
        m = r.get("match")
        if m not in komap:
            errs.append(f"KO result m{m} não existe em fixtures"); continue
        for k in ("home", "away", "winner"):
            if not str(r.get(k, "")).strip():
                errs.append(f"m{m}: campo '{k}' vazio")
        if r.get("winner") not in (r.get("home"), r.get("away")):
            errs.append(f"m{m}: winner não é nem home nem away")
        if r.get("decided_by") not in ("reg", "et", "pens"):
            errs.append(f"m{m}: decided_by inválido (reg|et|pens)")
        if not (_nat(r.get("hg")) and _nat(r.get("ag"))):
            errs.append(f"m{m}: gols (90min) inválidos")

    # prêmio individual conhecido (golden_boot/golden_glove) — resultado real, fim do torneio
    teams48 = {f["home"] for f in fixtures["group"]} | {f["away"] for f in fixtures["group"]}
    _check_awards(res.get("awards"), "results.awards", teams48, errs)
    return errs


AWARD_KEYS = ("golden_boot", "golden_glove")


def _check_awards(block, label, teams48, errs):
    """Valida {golden_boot?: {player, team}, golden_glove?: {player, team}}.
    Jogador é texto livre (palpite não pontua); team tem que ser uma das 48 (chave EN canônica)."""
    if block is None:
        return
    if not isinstance(block, dict):
        errs.append(f"{label}: deve ser objeto {{golden_boot/golden_glove}}"); return
    for k in sorted(block):
        if k not in AWARD_KEYS:
            errs.append(f"{label}.{k}: categoria desconhecida (use golden_boot|golden_glove)"); continue
        v = block[k] or {}
        if not isinstance(v, dict):
            errs.append(f"{label}.{k}: deve ser objeto {{player, team}}"); continue
        if not str(v.get("player", "")).strip():
            errs.append(f"{label}.{k}: campo 'player' vazio")
        if v.get("team") not in teams48:
            errs.append(f"{label}.{k}: team '{v.get('team')}' não é uma das 48 (chave EN canônica)")


def build_fixed(state, fixtures):
    """
    FIXED_GROUP: frozenset({home,away}) -> {team: goals}   (par único por grupo)
    FIXED_KO:    match -> {home, away, hg, ag, winner, decided_by}
    Pressupõe estado já validado.
    """
    gmap = {f["match"]: f for f in fixtures["group"]}
    res = state.get("results", {}) or {}
    FIXED_GROUP = {}
    for r in res.get("group", []) or []:
        fx = gmap[r["match"]]
        FIXED_GROUP[frozenset((fx["home"], fx["away"]))] = {fx["home"]: r["hg"], fx["away"]: r["ag"]}
    FIXED_KO = {}
    for r in res.get("knockout", []) or []:
        FIXED_KO[r["match"]] = {"home": r["home"], "away": r["away"], "hg": r["hg"],
                                "ag": r["ag"], "winner": r["winner"],
                                "decided_by": r.get("decided_by", "reg")}
    return FIXED_GROUP, FIXED_KO
