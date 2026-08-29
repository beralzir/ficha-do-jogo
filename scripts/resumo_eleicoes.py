#!/usr/bin/env python3
"""Resumo do run do atualizar-eleicoes (vai pro GITHUB_STEP_SUMMARY).
Inclui o ALARME DE COMPLETUDE: corridas sem dado fresco listadas em todo run
(aprendizado do jogo 103 da Copa: buraco de cobertura nunca fica silencioso)."""
import json

polls = json.load(open("data/live/polls.json", encoding="utf-8"))
res = json.load(open("data/eleicoes2026_results.json", encoding="utf-8"))
ok = sum(1 for r in res["races"].values() if r["data_quality"] == "ok")
print(f"- Pesquisas na base: **{len(polls['polls'])}** (as_of {res['meta']['as_of']})")
print(f"- Corridas com dado fresco: **{ok}/55**")
ruins = sorted(k for k, r in res["races"].items() if r["data_quality"] != "ok")
if ruins:
    print(f"- ⚠️ Corridas sem dado fresco: {', '.join(ruins)}")
pend = json.load(open("data/eleicoes/aliases_pendentes.json", encoding="utf-8"))
print(f"- Nomes sem match aguardando alias: {len(pend.get('candidatos_sem_match', {}))}")
