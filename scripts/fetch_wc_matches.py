#!/usr/bin/env python3
"""Busca TODOS os jogos da Copa em football-data.org (/v4/competitions/WC/matches) usando
FOOTBALL_DATA_TOKEN e imprime, no stdout, um JSON enxuto por jogo (stage · utcDate · status ·
times · sede). Feito para rodar numa GitHub Action: o token vem do secret e NUNCA sai do runner;
a saída vira um artefato + é ecoada no log (dados de jogo não são segredo, só o token é mascarado).
SÓ LEITURA da API — não escreve nada no repositório. Uso local: FOOTBALL_DATA_TOKEN=... python3 este.py
"""
import json, os, sys, urllib.request, urllib.error

TOKEN = os.environ.get("FOOTBALL_DATA_TOKEN")
if not TOKEN:
    sys.exit("FOOTBALL_DATA_TOKEN ausente (defina como env/secret).")

URL = "https://api.football-data.org/v4/competitions/WC/matches"
req = urllib.request.Request(URL, headers={"X-Auth-Token": TOKEN})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
except urllib.error.HTTPError as e:
    sys.exit(f"HTTP {e.code} ao buscar {URL}: {e.read()[:300]!r}")

out = []
for m in data.get("matches", []):
    ht = m.get("homeTeam") or {}
    at = m.get("awayTeam") or {}
    ven = m.get("venue")
    out.append({
        "id": m.get("id"),
        "stage": m.get("stage"),
        "group": m.get("group"),
        "matchday": m.get("matchday"),
        "utcDate": m.get("utcDate"),
        "status": m.get("status"),
        "home": ht.get("name"),
        "away": at.get("name"),
        "venue": ven,
    })
print(json.dumps({"competition": "WC", "count": len(out), "matches": out},
                 ensure_ascii=False, indent=1))
