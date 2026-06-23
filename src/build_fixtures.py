#!/usr/bin/env python3
"""
Build data/fixtures.json — calendário do torneio.

- Os 72 confrontos de grupo são DERIVADOS de worldcup2026_structure.json (GROUPS) — autoritativos.
- As datas/horários vêm do calendário oficial (ESPN, coletado 2026-06-08), anexados a cada confronto
  por par de times (cross-validação: cada grupo precisa ter exatamente seus 6 confrontos round-robin).
- Kickoffs ancorados em ET; BRT (America/Sao_Paulo, UTC-3) = ET (EDT, UTC-4) + 1h.
- Os 31+ slots de mata-mata vêm de structure.json (baseados em slot: 1A, 2B, 3rd, W74...).
- Só grava fixtures.json se TODAS as validações passarem (72 jogos, 48 times com 3 jogos, 0 erros).
"""
import json, os, itertools
from datetime import datetime, timedelta
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "data")
S = json.load(open(f"{BASE}/worldcup2026_structure.json"))
GROUPS = S["groups"]

# Nomes ESPN -> canônico do projeto
NORM = {"Türkiye": "Turkey", "Curaçao": "Curacao"}
def norm(n): return NORM.get(n.strip(), n.strip())

# Calendário oficial dos grupos (ESPN, coletado 2026-06-08):
# match | data | kickoff ET | grupo | time1 | time2 | cidade
SCHED = """
1 | 2026-06-11 | 3:00 PM | A | Mexico | South Africa | Mexico City
2 | 2026-06-11 | 10:00 PM | A | South Korea | Czechia | Zapopan
3 | 2026-06-12 | 3:00 PM | B | Canada | Bosnia and Herzegovina | Toronto
4 | 2026-06-12 | 9:00 PM | D | United States | Paraguay | Inglewood
5 | 2026-06-13 | 3:00 PM | B | Qatar | Switzerland | Santa Clara
6 | 2026-06-13 | 6:00 PM | C | Brazil | Morocco | East Rutherford
7 | 2026-06-13 | 9:00 PM | C | Haiti | Scotland | Foxborough
8 | 2026-06-14 | 12:00 AM | D | Australia | Türkiye | Vancouver
9 | 2026-06-14 | 1:00 PM | E | Germany | Curaçao | Houston
10 | 2026-06-14 | 4:00 PM | F | Netherlands | Japan | Arlington
11 | 2026-06-14 | 7:00 PM | E | Ivory Coast | Ecuador | Philadelphia
12 | 2026-06-14 | 10:00 PM | F | Sweden | Tunisia | Guadalupe
13 | 2026-06-15 | 1:00 PM | H | Spain | Cape Verde | Atlanta
14 | 2026-06-15 | 6:00 PM | G | Belgium | Egypt | Seattle
15 | 2026-06-15 | 6:00 PM | H | Saudi Arabia | Uruguay | Miami Gardens
16 | 2026-06-16 | 12:00 AM | G | Iran | New Zealand | Inglewood
17 | 2026-06-16 | 3:00 PM | I | France | Senegal | East Rutherford
18 | 2026-06-16 | 6:00 PM | I | Iraq | Norway | Foxborough
19 | 2026-06-16 | 9:00 PM | J | Argentina | Algeria | Kansas City
20 | 2026-06-17 | 12:00 AM | J | Austria | Jordan | Santa Clara
21 | 2026-06-17 | 1:00 PM | K | Portugal | DR Congo | Houston
22 | 2026-06-17 | 4:00 PM | L | England | Croatia | Arlington
23 | 2026-06-17 | 7:00 PM | L | Ghana | Panama | Toronto
24 | 2026-06-17 | 10:00 PM | K | Uzbekistan | Colombia | Mexico City
25 | 2026-06-18 | 12:00 PM | A | Czechia | South Africa | Atlanta
26 | 2026-06-18 | 3:00 PM | B | Switzerland | Bosnia and Herzegovina | Inglewood
27 | 2026-06-18 | 6:00 PM | B | Canada | Qatar | Vancouver
28 | 2026-06-18 | 11:00 PM | A | Mexico | South Korea | Zapopan
29 | 2026-06-19 | 3:00 PM | D | United States | Australia | Seattle
30 | 2026-06-19 | 6:00 PM | C | Scotland | Morocco | Foxborough
31 | 2026-06-19 | 9:00 PM | C | Brazil | Haiti | Philadelphia
32 | 2026-06-20 | 12:00 AM | D | Türkiye | Paraguay | Santa Clara
33 | 2026-06-20 | 1:00 PM | F | Netherlands | Sweden | Houston
34 | 2026-06-20 | 4:00 PM | E | Germany | Ivory Coast | Toronto
35 | 2026-06-20 | 8:00 PM | E | Ecuador | Curaçao | Kansas City
36 | 2026-06-21 | 12:00 AM | F | Tunisia | Japan | Guadalupe
37 | 2026-06-21 | 12:00 PM | H | Spain | Saudi Arabia | Atlanta
38 | 2026-06-21 | 3:00 PM | G | Belgium | Iran | Inglewood
39 | 2026-06-21 | 6:00 PM | H | Uruguay | Cape Verde | Miami Gardens
40 | 2026-06-21 | 9:00 PM | G | New Zealand | Egypt | Vancouver
41 | 2026-06-22 | 1:00 PM | J | Argentina | Austria | Arlington
42 | 2026-06-22 | 5:00 PM | I | France | Iraq | Philadelphia
43 | 2026-06-22 | 8:00 PM | I | Norway | Senegal | East Rutherford
44 | 2026-06-22 | 11:00 PM | J | Jordan | Algeria | Santa Clara
45 | 2026-06-23 | 1:00 PM | K | Portugal | Uzbekistan | Houston
46 | 2026-06-23 | 4:00 PM | L | England | Ghana | Foxborough
47 | 2026-06-23 | 7:00 PM | L | Panama | Croatia | Toronto
48 | 2026-06-23 | 10:00 PM | K | Colombia | DR Congo | Zapopan
49 | 2026-06-24 | 3:00 PM | B | Switzerland | Canada | Vancouver
50 | 2026-06-24 | 3:00 PM | B | Bosnia and Herzegovina | Qatar | Seattle
51 | 2026-06-24 | 6:00 PM | C | Scotland | Brazil | Miami Gardens
52 | 2026-06-24 | 6:00 PM | C | Morocco | Haiti | Atlanta
53 | 2026-06-24 | 9:00 PM | A | Czechia | Mexico | Mexico City
54 | 2026-06-24 | 9:00 PM | A | South Africa | South Korea | Guadalupe
55 | 2026-06-25 | 4:00 PM | E | Ecuador | Germany | East Rutherford
56 | 2026-06-25 | 4:00 PM | E | Curaçao | Ivory Coast | Philadelphia
57 | 2026-06-25 | 7:00 PM | F | Japan | Sweden | Arlington
58 | 2026-06-25 | 7:00 PM | F | Tunisia | Netherlands | Kansas City
59 | 2026-06-25 | 10:00 PM | D | Türkiye | United States | Inglewood
60 | 2026-06-25 | 10:00 PM | D | Paraguay | Australia | Santa Clara
61 | 2026-06-26 | 3:00 PM | I | Norway | France | Foxborough
62 | 2026-06-26 | 3:00 PM | I | Senegal | Iraq | Toronto
63 | 2026-06-26 | 8:00 PM | H | Cape Verde | Saudi Arabia | Houston
64 | 2026-06-26 | 8:00 PM | H | Uruguay | Spain | Zapopan
65 | 2026-06-26 | 11:00 PM | G | Egypt | Iran | Seattle
66 | 2026-06-26 | 11:00 PM | G | New Zealand | Belgium | Vancouver
67 | 2026-06-27 | 5:00 PM | L | Panama | England | East Rutherford
68 | 2026-06-27 | 5:00 PM | L | Croatia | Ghana | Philadelphia
69 | 2026-06-27 | 7:30 PM | K | Colombia | Portugal | Miami Gardens
70 | 2026-06-27 | 7:30 PM | K | DR Congo | Uzbekistan | Atlanta
71 | 2026-06-27 | 10:00 PM | J | Algeria | Austria | Kansas City
72 | 2026-06-27 | 10:00 PM | J | Jordan | Argentina | Arlington
"""

def parse_et(date, t):
    return datetime.strptime(f"{date} {t}", "%Y-%m-%d %I:%M %p")

rows = []
for line in SCHED.strip().splitlines():
    p = [x.strip() for x in line.split("|")]
    rows.append((int(p[0]), p[1], p[2], p[3], norm(p[4]), norm(p[5]), p[6]))

# confrontos autoritativos a partir de GROUPS
want = {g: {frozenset(c) for c in itertools.combinations(ts, 2)} for g, ts in GROUPS.items()}
seen = {g: set() for g in GROUPS}
errors, fixtures = [], []

for mno, date, et, grp, t1, t2, city in rows:
    if grp not in GROUPS:
        errors.append(f"m{mno}: grupo {grp} inexistente"); continue
    for t in (t1, t2):
        if t not in GROUPS[grp]:
            errors.append(f"m{mno}: '{t}' não pertence ao grupo {grp}")
    pair = frozenset((t1, t2))
    if pair not in want[grp]:
        errors.append(f"m{mno}: {t1}/{t2} não é confronto válido do grupo {grp}")
    elif pair in seen[grp]:
        errors.append(f"m{mno}: {t1}/{t2} duplicado")
    else:
        seen[grp].add(pair)
    brt = parse_et(date, et) + timedelta(hours=1)
    fixtures.append({"match": mno, "stage": "group", "group": grp,
                     "home": t1, "away": t2, "city": city, "date": date,
                     "kickoff_et": parse_et(date, et).strftime("%Y-%m-%dT%H:%M"),
                     "kickoff_brt": brt.strftime("%Y-%m-%dT%H:%M")})

for g in GROUPS:
    for pair in (want[g] - seen[g]):
        errors.append(f"grupo {g}: confronto {sorted(pair)} ausente no calendário")

# slots de mata-mata (baseados em slot, sem times até os grupos fecharem)
ko = []
for r in S["r32"]:
    ko.append({"match": r["match"], "stage": "R32", "home": r["home"], "away": r["away"],
               "third_from": r.get("third_from")})
for rd, key in (("R16", "r16"), ("QF", "qf"), ("SF", "sf")):
    for r in S[key]:
        ko.append({"match": r["match"], "stage": rd, "home": r["home"], "away": r["away"]})
fr = S["final"]; ko.append({"match": fr["match"], "stage": "Final", "home": fr["home"], "away": fr["away"]})
tp = S.get("third_place_game")
if tp:
    ko.append({"match": tp["match"], "stage": "3rd", "home": tp["home"], "away": tp["away"]})

out = {"tz": "America/Sao_Paulo",
       "provenance": "datas dos grupos: ESPN 2026 FIFA WC, coletado 2026-06-08; "
                     "confrontos derivados de structure.json GROUPS; BRT = ET + 1h",
       "group": sorted(fixtures, key=lambda x: x["match"]),
       "knockout": sorted(ko, key=lambda x: x["match"])}

# ---- validação ----
per_team = Counter()
for f in fixtures:
    per_team[f["home"]] += 1; per_team[f["away"]] += 1
bad = {t: c for t, c in per_team.items() if c != 3}
print("=== VALIDAÇÃO fixtures ===")
print("jogos de grupo:", len(fixtures), "(esperado 72)")
print("slots de mata-mata:", len(ko))
print("times distintos com jogo:", len(per_team), "(esperado 48)")
print("times com != 3 jogos:", bad or "nenhum")
print("janela de datas:", min(f["date"] for f in fixtures), "->", max(f["date"] for f in fixtures))
print("erros:", errors or "NENHUM")

ok = (not errors and len(fixtures) == 72 and not bad and len(per_team) == 48)
if ok:
    json.dump(out, open(f"{BASE}/fixtures.json", "w"), ensure_ascii=False, indent=1)
    print("\n✓ data/fixtures.json gravado.")
else:
    print("\n✗ NÃO gravei fixtures.json — corrigir os erros acima primeiro.")
