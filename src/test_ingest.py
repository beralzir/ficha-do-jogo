#!/usr/bin/env python3
"""Testa o adaptador de ingestão (ingest.py). Roda: python3 src/test_ingest.py

Duas partes:
  A) MATA-MATA (self-contained, roda SEMPRE): reconstrói as fontes a partir do state.json + dados
     inline; cobre pênaltis (placar = fim da prorrogação, sem pênaltis), quórum de vencedor,
     cascata (R32 -> R16 no mesmo run) e append-only.
  B) GRUPO (offline, precisa de .api_cache/ gravado): teste de ouro, quórum, fail-closed,
     plausibilidade, temporal, contrato DataSource. Em CI a validação ao vivo fica na Fase 3.
Não toca a rede nem grava state.json."""
import json, os, glob, sys, datetime as dt, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ingest, bracket
_state = ingest._state

ROOT = ingest.ROOT
CACHE = os.path.join(ROOT, ".api_cache")
fix = ingest.load_fixtures()
S = json.load(open(os.path.join(ingest.BASE, "worldcup2026_structure.json")))
P = F = 0


def ok(cond, msg):
    global P, F
    if cond:
        P += 1; print("  ✓", msg)
    else:
        F += 1; print("  ✗ FALHOU:", msg)


# ══════════════════════════════ A) MATA-MATA (self-contained) ══════════════════════════════
def _group_srcs():
    """fd/espn de GRUPO reconstruídos do state.json (formato dos fetchers) + a lista de resultados."""
    st = json.load(open(ingest.STATE_PATH))
    gmap = {f["match"]: f for f in fix["group"]}
    fd_g, espn_g = {}, {}
    for r in st["results"].get("group", []) or []:
        fx = gmap[r["match"]]; h, a = fx["home"], fx["away"]
        fd_g[frozenset((h, a))] = {"goals": {h: r["hg"], a: r["ag"]}, "final": True}
        espn_g[frozenset((h, a))] = {"goals": {h: r["hg"], a: r["ag"]}, "final": True}
    return fd_g, espn_g, st["results"].get("group", []) or []


NOW_KO = dt.datetime(2026, 7, 6, 12, 0)
fd_g, espn_g, gres = _group_srcs()
rb0 = bracket.resolve_bracket({"results": {"group": gres, "knockout": []}}, fix, S)

if rb0 is None:
    print("A) MATA-MATA: SKIP (state.json não tem os 72 grupos — chave não resolve).")
else:
    def _pair(mno):
        return rb0["matchups"][mno]

    mA, mB = S["r32"][0]["match"], S["r32"][1]["match"]
    HA, AA = _pair(mA); HB, AB = _pair(mB)

    print("A1) PÊNALTIS gravam o placar do FIM DA PRORROGAÇÃO (não incluem os pênaltis) + vencedor")
    fd_ko = {frozenset((HA, AA)): {"goals": {HA: 2, AA: 0}, "winner": HA, "decided_by": "reg", "final": True},
             frozenset((HB, AB)): {"goals": {HB: 1, AB: 1}, "winner": AB, "decided_by": "pens", "final": True}}
    espn_ko = {frozenset((HA, AA)): {"goals": {HA: 2, AA: 0}, "winner": HA, "final": True},
               frozenset((HB, AB)): {"goals": {HB: 1, AB: 1}, "winner": AB, "final": True}}
    cand, rep = ingest.build(fix, fd_g, espn_g, fd_ko, espn_ko, NOW_KO, S)
    kd = {r["match"]: r for r in cand["results"]["knockout"]}
    ok(kd.get(mB, {}).get("hg") == 1 and kd.get(mB, {}).get("ag") == 1, "jogo de pênaltis gravado 1-1 (fim da prorrogação)")
    ok(kd.get(mB, {}).get("winner") == AB and kd.get(mB, {}).get("decided_by") == "pens",
       "vencedor de pênaltis vem do winner da fonte; decided_by=pens")
    ok(kd.get(mA, {}).get("decided_by") == "reg" and kd.get(mA, {}).get("winner") == HA,
       "jogo normal: winner pelo placar, decided_by=reg")
    ok(not _state.validate_state(cand, fix), "candidato com KO passa no validate_state")

    print("A2) QUÓRUM — divergência de vencedor entre fontes REJEITA (bloqueia auto-promote), sem duplicar")
    bad = {frozenset((HA, AA)): {"goals": {HA: 2, AA: 0}, "winner": AA, "final": True},   # ESPN diverge
           frozenset((HB, AB)): dict(espn_ko[frozenset((HB, AB))])}
    cand2, rep2 = ingest.build(fix, fd_g, espn_g, fd_ko, bad, NOW_KO, S)
    ok(any(r[0] == mA for r in rep2["ko_rejects"]), f"m{mA} (vencedor divergente) listado em ko_rejects")
    ok(mA not in {r["match"] for r in cand2["results"]["knockout"]}, f"m{mA} divergente NÃO entra no candidato")
    ok(len([r for r in rep2["ko_rejects"] if r[0] == mA]) == 1, "rejeição logada 1x (dedup na cascata)")

    print("A3) CASCATA — vencedores do R32 revelam o R16 no MESMO run")
    allk_fd, allk_espn, win = {}, {}, {}
    for rd in S["r32"]:
        H, A = _pair(rd["match"])
        allk_fd[frozenset((H, A))] = {"goals": {H: 1, A: 0}, "winner": H, "decided_by": "reg", "final": True}
        allk_espn[frozenset((H, A))] = {"goals": {H: 1, A: 0}, "winner": H, "final": True}
        win[rd["match"]] = H
    tmp = [{"match": m, "home": _pair(m)[0], "away": _pair(m)[1], "hg": 1, "ag": 0, "winner": w, "decided_by": "reg"}
           for m, w in win.items()]
    r16m = S["r16"][0]["match"]
    H16, A16 = bracket.resolve_bracket({"results": {"group": gres, "knockout": tmp}}, fix, S)["matchups"][r16m]
    allk_fd[frozenset((H16, A16))] = {"goals": {H16: 2, A16: 1}, "winner": H16, "decided_by": "et", "final": True}
    allk_espn[frozenset((H16, A16))] = {"goals": {H16: 2, A16: 1}, "winner": H16, "final": True}
    cand3, rep3 = ingest.build(fix, fd_g, espn_g, allk_fd, allk_espn, NOW_KO, S)
    ok(len(rep3["ko_added"]) == 17, f"16 R32 + 1 R16 = 17 gravados (veio {len(rep3['ko_added'])})")
    ok(r16m in {r["match"] for r in cand3["results"]["knockout"]}, f"R16 m{r16m} ingerido via cascata")

    print("A4) APPEND-ONLY — jogo de KO já no state NÃO é reingerido (append-only)")
    prev = {"results": {"group": gres, "knockout":
            [{"match": mA, "home": HA, "away": AA, "hg": 2, "ag": 0, "winner": HA, "decided_by": "reg"}]}}
    tmpf = os.path.join(ROOT, ".test_state_ko.json")
    json.dump(prev, open(tmpf, "w"))
    _orig = ingest.STATE_PATH
    try:
        ingest.STATE_PATH = tmpf
        cand4, rep4 = ingest.build(fix, fd_g, espn_g, fd_ko, espn_ko, NOW_KO, S)
    finally:
        ingest.STATE_PATH = _orig
        os.remove(tmpf)
    ok(not any(r["match"] == mA for r in rep4["ko_added"]), f"m{mA} já gravado NÃO reaparece em ko_added")
    ok(mA in {r["match"] for r in cand4["results"]["knockout"]}, f"m{mA} preservado no state (não some)")


# ══════════════════════════════ B) GRUPO (offline, precisa de .api_cache) ═══════════════════
if not glob.glob(os.path.join(CACHE, "espn_*.json")):
    print("\nB) GRUPO: SKIP (sem .api_cache/ gravado). Em CI a validação ao vivo fica na Fase 3.")
    print(f"\n=== {P} passaram · {F} falharam ===")
    raise SystemExit(1 if F else 0)

NOW = dt.datetime(2026, 6, 23, 23, 0)
dates = sorted({f["date"].replace("-", "") for f in fix["group"]})
fd = ingest.fetch_fd_group(CACHE)
espn = ingest.fetch_espn_group(dates, CACHE)

print("\nB1) TESTE DE OURO — adaptador reproduz o state.json manual (jogos de grupo)")
cand, rep = ingest.build(fix, fd, espn, {}, {}, NOW, S)
manual = json.load(open(ingest.STATE_PATH))
man = {r["match"]: (r["hg"], r["ag"]) for r in manual["results"]["group"]}
got = {r["match"]: (r["hg"], r["ag"]) for r in cand["results"]["group"]}
mism = [m for m in man if m not in got or got[m] != man[m]]
ok(not mism, f"todos os {len(man)} jogos manuais reproduzidos byte-a-byte (mismatch={mism})")
ok(set(got) >= set(man), "adaptador cobre >= os jogos manuais")
ok(rep["accepted"] >= len(man), f"aceitou {rep['accepted']} (>= {len(man)} manuais; pegou novos)")

print("B2) QUORUM — divergência entre fontes é REJEITADA (não escrita)")
espn2 = copy.deepcopy(espn)
m1 = fix["group"][0]; pair = frozenset((m1["home"], m1["away"]))
g = espn2[pair]["goals"]; some = list(g); g[some[0]] = g[some[0]] + 5
cand2, rep2 = ingest.build(fix, fd, espn2, {}, {}, NOW, S)
got2 = {r["match"] for r in cand2["results"]["group"]}
ok(m1["match"] not in got2, f"m{m1['match']} divergente NÃO entrou no candidato")
ok(any(r[0] == m1["match"] for r in rep2["rejects"]), f"m{m1['match']} listado em rejects (divergência)")

print("B3) FAIL-CLOSED — nome de seleção desconhecido ABORTA")
try:
    ingest.canon("Republica de Narnia", "fd"); ok(False, "deveria ter abortado")
except ingest.IngestAbort:
    ok(True, "nome desconhecido lança IngestAbort (fail-closed)")
ok(ingest.canon("Bosnia-Herzegovina", "fd") == "Bosnia and Herzegovina", "mapa FD resolve Bosnia")
ok(ingest.canon("Türkiye", "espn") == "Turkey", "mapa ESPN resolve Türkiye")

print("B4) PLAUSIBILIDADE — placar atípico ENTRA mas é sinalizado")
fd3, espn3 = copy.deepcopy(fd), copy.deepcopy(espn)
for src in (fd3, espn3):
    gg = src[pair]["goals"]; k = list(gg); gg[k[0]], gg[k[1]] = 9, 0
cand3, rep3 = ingest.build(fix, fd3, espn3, {}, {}, NOW, S)
ok(any(r[0] == m1["match"] for r in rep3["warns"]), f"m{m1['match']} 9-0 sinalizado em warns")
ok(m1["match"] in {r["match"] for r in cand3["results"]["group"]}, "placar atípico ENTRA (não bloqueia futebol real)")

print("B5) TEMPORAL — antes do kickoff, nada é aceito")
cand4, rep4 = ingest.build(fix, fd, espn, {}, {}, dt.datetime(2026, 6, 11, 12, 0), S)
ok(rep4["accepted"] == 0, f"now=11/jun 12:00 -> 0 aceitos (1o kickoff 15:00), veio {rep4['accepted']}")

print("B6) CONTRATO DataSource — o motor consome o candidato sem saber que veio de API")
src = ingest.ApiQuorumSource(cache=CACHE, now=NOW)
st = src.load()
ok(isinstance(st, dict) and "results" in st, "ApiQuorumSource.load() devolve state dict")
ok(not _state.validate_state(st, fix), "validate_state(candidato) sem erros")

print("B7) APPEND-ONLY — diff detecta sobrescrita de jogo já gravado")
old = {"results": {"group": [{"match": 1, "hg": 9, "ag": 9}]}}
added, changed, removed = ingest.diff(old, cand)
ok(any(c[0] == 1 for c in changed), "m1 com placar diferente aparece em 'changed' (trava o auto-promote)")

print(f"\n=== {P} passaram · {F} falharam ===")
raise SystemExit(1 if F else 0)
