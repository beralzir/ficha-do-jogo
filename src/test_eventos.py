#!/usr/bin/env python3
"""Testes do registro de eventos (M3, Fase D).

Regra da casa: gate só vale com ERRO PLANTADO. O erro plantado aqui é o viés que
o M3 inteiro existe para evitar: declarar que a direção foi pré-especificada
depois de já ter visto o efeito.

Por isso o caso 2 planta um `pre_especificado: true` num evento retroativo e exige
que o validador RECUSE o arquivo. Não basta o campo ser ignorado: se ele puder
estar ali, alguém vai acreditar nele algum dia.

Usa rede? Não.

Uso:  python3 src/test_eventos.py
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eleicoes_eventos as ev  # noqa: E402

ROOT = os.path.join(HERE, "..")
FALHAS = []


def check(nome, cond, detalhe=""):
    print(f"  {'ok  ' if cond else 'FALHA'} {nome}" + (f"  ({detalhe})" if detalhe else ""))
    if not cond:
        FALHAS.append(nome)


def main():
    structure = json.load(open(ev.STRUCT, encoding="utf-8"))
    sqs = {c["sq"] for r in structure["races"].values() for c in r["candidates"]}
    doc = json.load(open(ev.EVENTOS, encoding="utf-8"))
    print(f"registro real: {len(doc['eventos'])} evento(s)\n")

    # 1. o arquivo que está no repo é válido
    print("1. o registro versionado")
    check("valida sem problema", not ev.valida(doc, sqs),
          f"{len(ev.valida(doc, sqs))} problema(s)")
    check("a doutrina da pré-especificação derivada está no arquivo",
          "_pre_especificado_e_derivado" in doc)
    check("declara que é curado à mão", "à mão" in doc.get("_doc", "").lower() or
          "curado" in doc.get("_doc", "").lower())
    check("lista as fontes de curadoria", len(doc.get("_fontes_de_curadoria", [])) >= 3)

    # 2. ERRO PLANTADO: declarar pré-especificação
    print("\n2. erro plantado: declarar que a direção foi pré-especificada")
    d = copy.deepcopy(doc)
    d["eventos"][0]["pre_especificado"] = True
    probs = ev.valida(d, sqs)
    check("o arquivo é RECUSADO se trouxer o campo", bool(probs),
          f"{len(probs)} problema(s)")
    check("e a mensagem explica por quê",
          any("derivado" in p for p in probs))

    # 3. a derivação, nas duas direções
    print("\n3. a derivação de pre_especificado")
    casos = [
        ({"data": "2026-09-28", "registrado_em": "2026-09-25"}, True,
         "debate futuro, direção escrita antes: PRÉ-ESPECIFICADO"),
        ({"data": "2026-09-28", "registrado_em": "2026-09-28"}, True,
         "registrado no próprio dia do fato: ainda conta"),
        ({"data": "2026-08-26", "registrado_em": "2026-09-21"}, False,
         "fato de agosto registrado em setembro: exploratório"),
        ({"data": "2026-09-20", "registrado_em": "2026-09-21"}, False,
         "registrado no dia seguinte: exploratório (regra conservadora)"),
    ]
    for campos, esperado, desc in casos:
        check(desc, ev.pre_especificado(campos) == esperado)
    check("o evento real do Cury sai como exploratório",
          not ev.pre_especificado(doc["eventos"][0]))

    # 4. ERRO PLANTADO: as outras formas de o registro apodrecer
    print("\n4. erro plantado: campos inválidos")
    plantios = [
        ("tipo inventado", lambda e: e.update(tipo="fofoca")),
        ("direção fora do domínio", lambda e: e.update(direcao_esperada="talvez")),
        ("escopo inválido", lambda e: e.update(escopo="galaxia")),
        ("sq que não existe na structure", lambda e: e.update(alvo=[999999999999])),
        ("alvo vazio", lambda e: e.update(alvo=[])),
        ("data que não é ISO", lambda e: e.update(data="26 de agosto")),
        ("fonte sem url", lambda e: e["fonte"].update(url="")),
        ("fonte sem veículo", lambda e: e["fonte"].update(veiculo="")),
        ("fonte sem data de acesso", lambda e: e["fonte"].update(acesso="")),
        ("sem campo obrigatório", lambda e: e.pop("direcao_esperada")),
    ]
    for nome, estraga in plantios:
        d = copy.deepcopy(doc)
        estraga(d["eventos"][0])
        check(f"{nome}: RECUSADO", bool(ev.valida(d, sqs)))

    print("\n5. erro plantado: id repetido")
    d = copy.deepcopy(doc)
    d["eventos"].append(copy.deepcopy(d["eventos"][0]))
    probs = ev.valida(d, sqs)
    check("dois eventos com o mesmo id: RECUSADO",
          any("repetido" in p for p in probs))

    # 6. a lista de trabalho não pode virar registro
    print("\n6. a lista de trabalho é insumo, não registro")
    w = ev.worklist()
    check("a lista de trabalho roda", isinstance(w, list), f"{len(w)} data(s)")
    ids = {e["id"] for e in doc["eventos"]}
    check("nada da lista entrou no registro sozinho", len(ids) == len(doc["eventos"]))
    check("o registro tem no máximo os eventos curados à mão",
          len(doc["eventos"]) < 50,
          f"{len(doc['eventos'])} eventos; curadoria é humana, não geração")

    print()
    if FALHAS:
        print(f"REPROVADO: {len(FALHAS)} falha(s): {', '.join(FALHAS)}", file=sys.stderr)
        sys.exit(1)
    pre = sum(1 for e in doc["eventos"] if ev.pre_especificado(e))
    print(f"OK: registro validado · {len(doc['eventos'])} evento(s), {pre} "
          f"pré-especificado(s) · o campo declarável é recusado.")


if __name__ == "__main__":
    main()
