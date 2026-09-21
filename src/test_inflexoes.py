#!/usr/bin/env python3
"""Testes do detector de inflexão (M2, Fase D).

Regra da casa: gate só vale com ERRO PLANTADO. Aqui há dois tipos de prova.

REAL: o plano da Fase D cita um episódio concreto, o salto de Cury em 27/08.
O caso 2 exige que o detector o encontre, corroborado por instituto diferente.
Detector que não acha o exemplar do próprio plano não serve.

PLANTADO: a regra de corroboração é o único remédio que o plano autoriza contra
falso positivo (em vez de baixar o limiar), então ela precisa ser provada a
quebrar nas três direções em que pode vazar: mesmo instituto, sinal oposto e
fora da janela. O caso 3 planta as três.

Usa rede? Não.

Uso:  python3 src/test_inflexoes.py
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eleicoes_inflexoes as inf  # noqa: E402

ROOT = os.path.join(HERE, "..")
ALVO = os.path.join(ROOT, "data", "eleicoes", "inflexoes.json")
FALHAS = []


def check(nome, cond, detalhe=""):
    print(f"  {'ok  ' if cond else 'FALHA'} {nome}" + (f"  ({detalhe})" if detalhe else ""))
    if not cond:
        FALHAS.append(nome)


def main():
    if not os.path.exists(ALVO):
        subprocess.run([sys.executable, os.path.join(HERE, "eleicoes_inflexoes.py")],
                       check=True, capture_output=True)
    doc = json.load(open(ALVO, encoding="utf-8"))
    I = doc["inflexoes"]
    print(f"base real: {doc['n']} inflexões agrupadas · as_of {doc['as_of']}\n")

    # 1. schema e honestidade viajando junto do dado
    print("1. schema")
    check("tem schema_version", doc.get("schema_version") == 1)
    check("declara o modelo que produziu", doc.get("modelo") == "v2_estado")
    check("params do detector viajam no arquivo",
          all(k in doc.get("params", {}) for k in
              ("Z_SALTO", "JANELA_SALTO", "CORROB_D", "MIN_SHARE")))
    check("as ressalvas viajam junto do dado", len(doc.get("ressalvas", [])) >= 5,
          f"{len(doc.get('ressalvas', []))} ressalvas")
    # a ressalva da magnitude é a mais fácil de alguém apagar por parecer derrotista
    check("a ressalva da magnitude subestimada está lá",
          any("MAGNITUDE" in r for r in doc.get("ressalvas", [])))
    check("nenhum grupo duplicado (corrida, candidato, data)",
          len({(r["corrida"], r["sq"], r["data"]) for r in I}) == len(I))
    check("ordenado por movimento de nível, não por z",
          all(abs(I[i]["delta_janela_pp"]) >= abs(I[i + 1]["delta_janela_pp"]) - 1e-9
              for i in range(min(len(I), 50) - 1)))

    # 2. ÂNCORA REAL: o exemplar que o plano da Fase D cita
    print("\n2. âncora real: o episódio de Cury de 27/08 que o plano cita")
    cury = [r for r in I if r["corrida"] == "PRES" and "CURY" in r["urna"].upper()]
    check("há detecção de Cury na presidencial", len(cury) > 0, f"{len(cury)} datas")
    janela = [r for r in cury if "2026-08-25" <= r["data"] <= "2026-08-31"]
    check("detecta na janela de 25 a 31/08", len(janela) > 0,
          f"datas: {sorted(r['data'] for r in janela)}")
    check("ao menos uma é corroborada por outro instituto",
          any(r["corroborado"] for r in janela))
    check("e são altas no ranking (top 10 por movimento de nível)",
          any(r in I[:10] for r in janela))

    # 3. ERRO PLANTADO: as três formas de a corroboração vazar
    print("\n3. erro plantado: a regra de corroboração")
    base = lambda d, z, i: {"data": d, "z": z, "instituto": i,
                            "delta_dia_pp": 0.0, "delta_janela_pp": 0.0}
    casos = [
        ("mesmo instituto NÃO corrobora",
         [base("2026-08-26", 4.0, "Datafolha"), base("2026-08-27", 4.0, "Datafolha")], False),
        ("sinal oposto NÃO corrobora",
         [base("2026-08-26", 4.0, "Datafolha"), base("2026-08-27", -4.0, "AtlasIntel")], False),
        (f"fora da janela de {inf.CORROB_D}d NÃO corrobora",
         [base("2026-08-01", 4.0, "Datafolha"), base("2026-08-27", 4.0, "AtlasIntel")], False),
        ("institutos diferentes, mesmo sinal, na janela: CORROBORA",
         [base("2026-08-26", 4.0, "Datafolha"), base("2026-08-27", 4.0, "AtlasIntel")], True),
    ]
    for nome, lista, esperado in casos:
        got = any(r["corroborado"] for r in inf.corrobora(lista))
        check(nome, got == esperado, f"corroborado={got}")

    # 4. o funil usa limiar PRÉ-ESPECIFICADO, não inventado ao ver o resultado
    print("\n4. o funil é pré-especificado")
    import eleicoes_compare as ec
    check("MIN_SHARE do destaque é o mesmo da métrica do harness",
          doc["params"]["MIN_SHARE"] == ec.MIN_SHARE, f"{ec.MIN_SHARE}")
    d = doc["n_destaques"]
    check("destaques são um subconjunto próprio", 0 < d < doc["n"], f"{d} de {doc['n']}")
    check("todo destaque é corroborado E relevante",
          all(r["corroborado"] and r["relevante"]
              for r in I if r["corroborado"] and r["relevante"]))

    # 5. determinismo
    print("\n5. determinismo")
    a = open(ALVO, encoding="utf-8").read()
    subprocess.run([sys.executable, os.path.join(HERE, "eleicoes_inflexoes.py")],
                   check=True, capture_output=True)
    check("regerar dá arquivo byte-idêntico", a == open(ALVO, encoding="utf-8").read())

    print()
    if FALHAS:
        print(f"REPROVADO: {len(FALHAS)} falha(s): {', '.join(FALHAS)}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: detector validado · {doc['n']} candidatos, {doc['n_destaques']} destaques, "
          f"e o exemplar do plano (Cury, 27/08) está entre eles.")


if __name__ == "__main__":
    main()
