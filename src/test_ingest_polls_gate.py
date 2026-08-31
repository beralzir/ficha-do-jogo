#!/usr/bin/env python3
"""Testes OFFLINE do gate de plausibilidade do ingest de pesquisas (C0-c).

Nasceu do plano de risco (docs/plano-risco-eleicoes.md): até 31/08/2026 a
Wikipédia entrava sem NENHUMA validação num pipeline que publica sozinho, e uma
linha forjada valia 67,9% do agregado em GOV-RR/SEN-RR.

Regra da casa (aprendizado do gate_citacao do vox, que nasceu com bug de
pareamento e 41 falsos positivos): gate só vale depois de provado com ERRO
PLANTADO. Os casos 2 a 5 plantam adulteração de propósito e exigem que o gate
pegue; o caso 1 exige que ele NÃO reprove o dado real em massa.

Uso:  python3 src/test_ingest_polls_gate.py        (não usa rede)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ingest_polls as ip  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
POLLS = os.path.join(ROOT, "data", "live", "polls.json")

FALHAS = []


def check(nome, cond, detalhe=""):
    print(f"  {'ok  ' if cond else 'FALHA'} {nome}" + (f"  ({detalhe})" if detalhe else ""))
    if not cond:
        FALHAS.append(nome)


def forjar(base, race, pct_alvo, manter_lista=True, **over):
    """Clona uma pesquisa real e adultera o líder, como faria quem edita a wiki.

    Usa os SQ REAIS da pesquisa modelo de propósito: o parser só casa candidato
    que existe no structure, então uma forjadura com SQ inventado nem chegaria
    aqui. Testar com SQ falso mediria um cenário que não acontece.

    manter_lista=True (padrão) mantém a MESMA lista de candidatos da tabela e só
    mexe nos números: é o que faz quem edita uma wikitable e quer que a linha
    continue parecendo as vizinhas. manter_lista=False encolhe para 2 nomes, o
    caso que o gate reconhecidamente não bloqueia (ver caso 7).
    """
    p = json.loads(json.dumps(base))
    p["id"] = "FORJADA-" + race
    p["race"] = race
    reais = sorted([n for n in base["numeros"] if n.get("sq")], key=lambda n: -n["pct"])
    if not manter_lista:
        reais = reais[:2]
    resto = max(0.0, 100.0 - pct_alvo)
    p["numeros"] = [dict(reais[0], pct=pct_alvo)]
    outros = reais[1:]
    for n in outros:                       # divide o resto entre os demais
        p["numeros"].append(dict(n, pct=round(resto / len(outros), 1)))
    p.update(over)
    return p


def main():
    polls = json.load(open(POLLS, encoding="utf-8"))["polls"]
    ids = {p["id"] for p in polls}
    print(f"base real: {len(polls)} pesquisas\n")

    # 1. O gate NÃO pode reprovar o dado real em massa. Rodando com prev_ids
    #    vazio, TODA pesquisa é tratada como nova: é o pior caso possível.
    print("1. dado real não é reprovado em massa (pior caso: tudo é novo)")
    rep = {}
    aceitas, quar = ip.plausibility_gate(json.loads(json.dumps(polls)), set(), rep)
    taxa = 100.0 * len(quar) / max(len(polls), 1)
    check("taxa de quarentena do dado real <= 2%", taxa <= 2.0, f"{taxa:.2f}% ({len(quar)})")
    check("nenhuma pesquisa some sem ir para a quarentena",
          len(aceitas) + len(quar) == len(polls), f"{len(aceitas)}+{len(quar)}={len(polls)}")

    # 2. Pesquisas já publicadas não são reescritas retroativamente.
    print("\n2. histórico já publicado não é reescrito")
    rep2 = {}
    aceitas2, quar2 = ip.plausibility_gate(json.loads(json.dumps(polls)), ids, rep2)
    check("com todas conhecidas, quarentena é vazia", not quar2, f"{len(quar2)}")
    check("todas as pesquisas seguem aceitas", len(aceitas2) == len(polls))

    # 3. ERRO PLANTADO: desvio grosseiro numa corrida COM consenso (presidencial).
    print("\n3. erro plantado: desvio grosseiro onde há consenso")
    pres = [p for p in polls if p["race"] == "PRES" and p["cenario"] == "estimulada"
            and p["campo_fim"]]
    pres.sort(key=lambda p: p["campo_fim"])
    modelo = pres[-1]
    plantada = forjar(modelo, "PRES", 95.0)
    rep3 = {}
    _, quar3 = ip.plausibility_gate(json.loads(json.dumps(polls)) + [plantada], ids, rep3)
    pegou = any(q["id"] == "FORJADA-PRES" for q in quar3)
    check("gate PEGA a pesquisa forjada", pegou,
          quar3[0]["motivos"][0][:60] if quar3 else "não pegou")
    check("gate não arrasta ninguém junto", len(quar3) == 1, f"{len(quar3)} em quarentena")

    # 3b. LIMITE CONHECIDO E DECLARADO: forjadura que encolhe a lista para 2 nomes
    #     não é bloqueada (com 2 candidatos em comum a re-normalização é ruidosa
    #     demais: falso positivo pularia de 2,3% para 8,7% no dado real). Ela sai
    #     marcada corroborada=False, e o teste TRAVA esse comportamento para que
    #     ninguém o mude sem perceber.
    print("\n3b. limite declarado: forjadura com lista encolhida")
    curta = forjar(modelo, "PRES", 95.0, manter_lista=False)
    curta["id"] = "FORJADA-CURTA"
    rep3b = {}
    ac3b, quar3b = ip.plausibility_gate(json.loads(json.dumps(polls)) + [curta], ids, rep3b)
    achou = [p for p in ac3b if p["id"] == "FORJADA-CURTA"]
    check("não bloqueia (limite conhecido)", not any(q["id"] == "FORJADA-CURTA" for q in quar3b))
    check("mas sai marcada corroborada=False",
          bool(achou) and achou[0].get("corroborada") is False)

    # 4. ERRO PLANTADO: sanidade absoluta (roda mesmo sem consenso).
    print("\n4. erro plantado: sanidade absoluta")
    casos = [
        ("pct fora de [0,100]", forjar(modelo, "PRES", 180.0)),
        ("amostra implausível", forjar(modelo, "PRES", 40.0, amostra=99000000)),
        ("soma acima do teto da base",
         dict(json.loads(json.dumps(modelo)), id="FORJADA-SOMA", base="normalizada_100",
              numeros=[{"sq": 1, "alias": "A", "pct": 99.0},
                       {"sq": 2, "alias": "B", "pct": 99.0}])),
    ]
    for nome, p in casos:
        v = ip.sanity_violations(p)
        check(f"sanidade pega: {nome}", bool(v), v[0][:58] if v else "passou batido")

    # 5. Corrida SEM base comparável não é bloqueada, mas viaja marcada.
    print("\n5. corrida sem base: não bloqueia, declara")
    rr = [p for p in polls if p["race"] == "GOV-RR"]
    nova_rr = forjar(rr[-1] if rr else modelo, "GOV-RR", 70.0)
    nova_rr["amostra"] = 800
    rep5 = {}
    ac5, quar5 = ip.plausibility_gate(json.loads(json.dumps(polls)) + [nova_rr], ids, rep5)
    entrou = [p for p in ac5 if p["id"] == "FORJADA-GOV-RR"]
    check("entra (não some do site)", bool(entrou) and not quar5)
    check("marcada corroborada=False", bool(entrou) and entrou[0].get("corroborada") is False)

    # 6. Determinismo: mesma entrada, mesma saída.
    print("\n6. determinismo")
    a = ip.plausibility_gate(json.loads(json.dumps(polls)), set(), {})[0]
    b = ip.plausibility_gate(json.loads(json.dumps(polls)), set(), {})[0]
    check("duas execuções são idênticas",
          [p["id"] for p in a] == [p["id"] for p in b])

    print()
    if FALHAS:
        print(f"REPROVADO: {len(FALHAS)} falha(s): {', '.join(FALHAS)}")
        sys.exit(1)
    print(f"OK: gate de plausibilidade validado (limiar {ip.GATE_DEV_PP:.0f}pp, "
          f"jaccard {ip.GATE_JACCARD}, base mín. {ip.GATE_MIN_BASE}).")


if __name__ == "__main__":
    main()
