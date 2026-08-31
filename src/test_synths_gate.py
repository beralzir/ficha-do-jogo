#!/usr/bin/env python3
"""GATE anti-vazamento do sintético (etapa C3d).

A decisão do Bera (29/08, reafirmada em 31/08) é dura: **pesquisa sintética nunca
entra no forecast oficial do site**. Ela compete no leaderboard e só.

"Nunca" precisa de prova mecânica, não de disciplina. Uma linha sintética que
vazasse para o oficial publicaria número inventado como se fosse agregação de
pesquisa de instituto, num site de forecast eleitoral em plena campanha. É o pior
incidente que este projeto consegue produzir.

Este gate prova três coisas e, como todo gate da casa, é validado com ERRO
PLANTADO antes de servir para alguma coisa:

1. O modelo OFICIAL não vê pesquisa sintética, mesmo com sintética no polls.json.
2. Um modelo declarado sintético produz forecast DIFERENTE do oficial (se fosse
   igual, o filtro não estaria fazendo nada e o teste 1 passaria por acidente).
3. A flag é FAIL-CLOSED: pesquisa sem `sintetico` derruba o motor, em vez de ser
   tratada como real por omissão.

Uso:  python3 src/test_synths_gate.py       (não usa rede)
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eleicoes_model as em  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CONFIGS = os.path.join(ROOT, "data", "eleicoes", "model_configs.json")

FALHAS = []


def check(nome, cond, detalhe=""):
    print(f"  {'ok  ' if cond else 'FALHA'} {nome}" + (f"  ({detalhe})" if detalhe else ""))
    if not cond:
        FALHAS.append(nome)


def shares_pres(out):
    return {c["sq"]: c["share"] for c in out["races"]["PRES"]["candidates"]}


def main():
    cfg = json.load(open(CONFIGS, encoding="utf-8"))
    structure = em.load(em.STRUCT)
    polls_doc = em.load(em.POLLS)
    sint = [p for p in polls_doc["polls"] if p.get("sintetico")]
    print(f"base: {len(polls_doc['polls'])} pesquisas, {len(sint)} sintética(s), "
          f"schema v{polls_doc.get('schema_version')}\n")

    # 0. Pré-condição: sem sintética no arquivo, o gate não prova nada.
    print("0. pré-condição")
    check("existe ao menos 1 pesquisa sintética para testar", bool(sint),
          "sem isso o gate passaria vazio")
    if not sint:
        print("\nGATE INCONCLUSIVO: gere a sintética antes (src/synths_para_polls.py).")
        sys.exit(1)

    # 1. O registro de modelos respeita a regra dura.
    print("\n1. registro de modelos")
    oficial = cfg["official"]
    check("o modelo oficial NÃO é sintético",
          not cfg["models"][oficial].get("sintetico"), f"official={oficial}")
    for mid, m in sorted(cfg["models"].items()):
        fonte = m.get("params", {}).get("POLL_SOURCE", "real")
        if m.get("sintetico"):
            check(f"{mid} declarado sintético lê fonte sintética",
                  fonte in ("sintetico", "ambos"), f"POLL_SOURCE={fonte}")
        else:
            check(f"{mid} não-sintético lê só pesquisa real",
                  fonte == "real", f"POLL_SOURCE={fonte}")

    # 2. ERRO PLANTADO: o oficial roda com sintética no arquivo e não pode enxergá-la.
    print("\n2. erro plantado: sintética presente, oficial cego")
    params = dict(em.DEFAULTS)
    params.update(cfg["models"][oficial].get("params", {}))
    usaveis = em.usable_polls(polls_doc["polls"], params)
    ids = {p["id"] for lst in usaveis.values() for p in lst}
    vazou = [p["id"] for p in sint if p["id"] in ids]
    check("nenhuma sintética entrou nas pesquisas usáveis do oficial",
          not vazou, f"vazaram: {vazou[:3]}" if vazou else f"{len(ids)} pesquisas reais")

    # 3. O filtro faz diferença de verdade (se não fizesse, o teste 2 seria vácuo).
    print("\n3. o filtro muda o resultado (senão o teste 2 passa por acidente)")
    p_sint = dict(em.DEFAULTS)
    p_sint.update({"POLL_SOURCE": "sintetico", "NSIMS": 2000})
    p_real = dict(params)
    p_real["NSIMS"] = 2000
    out_real = em.simulate(structure, polls_doc, p_real, verbose=False)
    out_sint = em.simulate(structure, polls_doc, p_sint, verbose=False)
    a, b = shares_pres(out_real), shares_pres(out_sint)
    dif = max(abs(a.get(k, 0) - b.get(k, 0)) for k in set(a) | set(b)) * 100
    check("oficial e synths_solo divergem na presidencial", dif > 1.0, f"{dif:.1f}pp")
    check("meta do oficial declara poll_source=real",
          out_real["meta"].get("poll_source") == "real")
    check("meta do sintético declara usa_sintetico=true",
          out_sint["meta"].get("usa_sintetico") is True)

    # 4. ERRO PLANTADO: pesquisa sem a flag tem de DERRUBAR, não virar real.
    print("\n4. erro plantado: pesquisa sem a flag obrigatória")
    sem_flag = copy.deepcopy(polls_doc)
    for p in sem_flag["polls"]:
        p.pop("sintetico", None)
    try:
        em.usable_polls(sem_flag["polls"], params)
        check("motor recusa pesquisa sem flag", False, "ACEITOU, fail-open")
    except ValueError as e:
        check("motor recusa pesquisa sem flag", True, str(e)[:52])

    # 5. ERRO PLANTADO: POLL_SOURCE inválido não pode virar "real" em silêncio.
    print("\n5. erro plantado: POLL_SOURCE inválido")
    ruim = dict(params)
    ruim["POLL_SOURCE"] = "tudo"
    try:
        em.usable_polls(polls_doc["polls"], ruim)
        check("motor recusa POLL_SOURCE inválido", False, "ACEITOU")
    except ValueError:
        check("motor recusa POLL_SOURCE inválido", True)

    print()
    if FALHAS:
        print(f"GATE REPROVADO: {len(FALHAS)} falha(s): {', '.join(FALHAS[:4])}")
        sys.exit(1)
    print("OK: sintético isolado do oficial, com erro plantado em 3 frentes.")


if __name__ == "__main__":
    main()
