#!/usr/bin/env python3
"""Resumo do run do atualizar-eleicoes (vai pro GITHUB_STEP_SUMMARY).

Dois alarmes, e eles medem coisas DIFERENTES:

- ALARME DE COMPLETUDE (B8): corridas sem dado FRESCO (aprendizado do jogo 103 da
  Copa: buraco de cobertura nunca fica silencioso).
- ALARME DE VOLUME (D2): corridas que PERDERAM pesquisas em relação ao último
  publicado. Existe porque frescor não é volume: em 04/09/2026 a presidencial
  perdeu 558 estimuladas e seguiu marcada "ok" todo dia, porque continuava
  recebendo pesquisa nova. O resumo mostrava "Pesquisas na base: 3.509" e o
  número até subia, já que as outras 54 corridas cobriam a perda.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import check_volume as cv  # noqa: E402

polls = json.load(open("data/live/polls.json", encoding="utf-8"))
res = json.load(open("data/eleicoes2026_results.json", encoding="utf-8"))
ok = sum(1 for r in res["races"].values() if r["data_quality"] == "ok")
print(f"- Pesquisas na base: **{len(polls['polls'])}** (as_of {res['meta']['as_of']})")
print(f"- Corridas com dado fresco: **{ok}/55**")
ruins = sorted(k for k, r in res["races"].items() if r["data_quality"] != "ok")
if ruins:
    print(f"- ⚠️ Corridas sem dado fresco: {', '.join(ruins)}")

# VOLUME por corrida. `HEAD~1` e não `HEAD`: quando este resumo roda, o commit
# automático do run já existe, então HEAD é o dado NOVO e comparar com ele daria
# sempre zero. Fora do CI (sem o commit) o certo é HEAD, e é o que o
# check_volume.py usa por padrão.
ref = os.environ.get("RESUMO_REF", "HEAD~1")
velho = cv.ref_json(ref)
if velho is None:
    print(f"- Volume por corrida: sem referência em `{ref}` (1º run).")
else:
    for p in velho.get("polls", []):        # polls.json antigo é schema v1
        p["sintetico"] = bool(p.get("sintetico", False))
    quedas = cv.quedas(cv.volumes(velho), cv.volumes(polls))
    if quedas:
        print(f"- 🔴 **{len(quedas)} corrida(s) PERDERAM pesquisas** "
              f"(limiar: queda > {cv.LIM_PCT:.0f}% e >= {cv.LIM_ABS} pesquisas):")
        for pct, n, race, cen, antes, depois in quedas[:10]:
            print(f"  - `{race}` / {cen}: {antes} → {depois} "
                  f"(**-{n}**, {pct:.0f}%)")
        print("  - Ver `docs/runbook-incidente.md`, seção "
              "\"A fonte mudou de estrutura e o dado sumiu em silêncio\".")
    else:
        print(f"- Volume por corrida: OK, nenhuma queda acima do limiar (vs `{ref}`).")

pend = json.load(open("data/eleicoes/aliases_pendentes.json", encoding="utf-8"))
print(f"- Nomes sem match aguardando alias: {len(pend.get('candidatos_sem_match', {}))}")
