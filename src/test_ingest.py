#!/usr/bin/env python3
"""Testa o adaptador de ingestão (ingest.py) OFFLINE contra respostas gravadas em .api_cache/.
Não toca a rede nem state.json. Roda: python3 src/test_ingest.py
Cobre: teste de ouro (reproduz o state manual), quorum, fail-closed, plausibilidade, temporal."""
import json, os, glob, datetime as dt, copy
import ingest

ROOT = ingest.ROOT
CACHE = os.path.join(ROOT, ".api_cache")
if not glob.glob(os.path.join(CACHE, "espn_*.json")):
    print("SKIP: sem .api_cache/ gravado (grave respostas localmente p/ rodar). "
          "Em CI a validação ao vivo fica na Fase 3.")
    raise SystemExit(0)
NOW = dt.datetime(2026, 6, 23, 23, 0)
fix = ingest.load_fixtures()
dates = sorted({f["date"].replace("-", "") for f in fix["group"]})
fd = ingest.fetch_fd_group(CACHE)
espn = ingest.fetch_espn_group(dates, CACHE)
P = F = 0


def ok(cond, msg):
    global P, F
    if cond:
        P += 1; print("  ✓", msg)
    else:
        F += 1; print("  ✗ FALHOU:", msg)


print("1) TESTE DE OURO — adaptador reproduz o state.json manual (jogos 1-40)")
cand, rep = ingest.build(fix, fd, espn, NOW)
manual = json.load(open(ingest.STATE_PATH))
man = {r["match"]: (r["hg"], r["ag"]) for r in manual["results"]["group"]}
got = {r["match"]: (r["hg"], r["ag"]) for r in cand["results"]["group"]}
mism = [m for m in man if m not in got or got[m] != man[m]]
ok(not mism, f"todos os {len(man)} jogos manuais reproduzidos byte-a-byte (mismatch={mism})")
ok(set(got) >= set(man), "adaptador cobre >= os jogos manuais")
ok(rep["accepted"] >= len(man), f"aceitou {rep['accepted']} (>= {len(man)} manuais; pegou novos)")

print("2) QUORUM — divergência entre fontes é REJEITADA (não escrita)")
espn2 = copy.deepcopy(espn)
m1 = fix["group"][0]; pair = frozenset((m1["home"], m1["away"]))
g = espn2[pair]["goals"]; some = list(g); g[some[0]] = g[some[0]] + 5  # adultera ESPN no m1
cand2, rep2 = ingest.build(fix, fd, espn2, NOW)
got2 = {r["match"] for r in cand2["results"]["group"]}
ok(m1["match"] not in got2, f"m{m1['match']} divergente NÃO entrou no candidato")
ok(any(r[0] == m1["match"] for r in rep2["rejects"]), f"m{m1['match']} listado em rejects (divergência)")

print("3) FAIL-CLOSED — nome de seleção desconhecido ABORTA")
try:
    ingest.canon("Republica de Narnia", "fd"); ok(False, "deveria ter abortado")
except ingest.IngestAbort:
    ok(True, "nome desconhecido lança IngestAbort (fail-closed)")
ok(ingest.canon("Bosnia-Herzegovina", "fd") == "Bosnia and Herzegovina", "mapa FD resolve Bosnia")
ok(ingest.canon("Türkiye", "espn") == "Turkey", "mapa ESPN resolve Türkiye")

print("4) PLAUSIBILIDADE — placar atípico ENTRA mas é sinalizado")
fd3, espn3 = copy.deepcopy(fd), copy.deepcopy(espn)
for src in (fd3, espn3):
    gg = src[pair]["goals"]; k = list(gg); gg[k[0]], gg[k[1]] = 9, 0  # 9-0 nos dois (quorum ok)
cand3, rep3 = ingest.build(fix, fd3, espn3, NOW)
ok(any(r[0] == m1["match"] for r in rep3["warns"]), f"m{m1['match']} 9-0 sinalizado em warns")
ok(m1["match"] in {r["match"] for r in cand3["results"]["group"]}, "placar atípico ENTRA (não bloqueia futebol real)")

print("5) TEMPORAL — antes do kickoff, nada é aceito")
cand4, rep4 = ingest.build(fix, fd, espn, dt.datetime(2026, 6, 11, 12, 0))  # antes do 1o jogo (15:00 ET)
ok(rep4["accepted"] == 0, f"now=11/jun 12:00 -> 0 aceitos (1o kickoff 15:00), veio {rep4['accepted']}")

print("6) CONTRATO DataSource — o motor consome o candidato sem saber que veio de API")
src = ingest.ApiQuorumSource(cache=CACHE, now=NOW)
st = src.load()
ok(isinstance(st, dict) and "results" in st, "ApiQuorumSource.load() devolve state dict")
ok(ingest.canon and not ingest._state.validate_state(st, fix), "validate_state(candidato) sem erros")
fg, fk = ingest._state.build_fixed(st, fix)
ok(len(fg) == rep["accepted"], f"build_fixed produz {len(fg)} jogos fixos (== aceitos)")

print("7) APPEND-ONLY — diff detecta sobrescrita de jogo já gravado")
old = {"results": {"group": [{"match": 1, "hg": 9, "ag": 9}]}}   # valor 'antigo' diferente
added, changed, removed = ingest.diff(old, cand)
ok(any(c[0] == 1 for c in changed), "m1 com placar diferente aparece em 'changed' (trava o auto-promote)")

print(f"\n=== {P} passaram · {F} falharam ===")
raise SystemExit(1 if F else 0)
