#!/usr/bin/env python3
"""Validador de `data/eleicoes/hipoteses.json` (hipóteses pré-especificadas).

Regras, todas verificáveis sem rede:
  - esquema exato por item (15 campos), id único no padrão h-AAAA-MM-DD-NN, e
    `registrado_em` igual à data do id;
  - PRÉ-ESPECIFICAÇÃO: a janela começa em ou depois de `registrado_em`. Hipótese
    cuja janela começa antes do registro é retroativa e o arquivo é RECUSADO;
  - alvo: todo sq existe no structure.json e pertence à corrida (ou, em 'MULTI',
    a uma das corridas de origem.corridas);
  - domínio: direção em {+,-}, métrica em {share, eleito, inflexao}, status nos
    válidos, palavra de Kent na escala e número dentro da faixa dela;
  - status != 'aberta' exige `julgado_em` e `evidencia`: ninguém fecha hipótese
    sem dizer com que dado;
  - sem linguagem de causa sobre o passado ("causou", "provocou", "por causa").

Uso:  python3 src/eleicoes_hipoteses.py --check
"""
import datetime as dt
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
ARQ = os.path.join(ROOT, "data", "eleicoes", "hipoteses.json")
STRUCT = os.path.join(ROOT, "data", "eleicoes2026_structure.json")

CAMPOS = {"id", "registrado_em", "titulo", "hipotese", "mecanismo", "origem", "corrida", "alvo",
          "direcao_esperada", "metrica", "janela", "limiar_pp", "falsificacao", "probabilidade",
          "status"}
STATUS = {"aberta", "confirmada", "falsa", "nao_testavel"}
METRICAS = {"share", "eleito", "inflexao"}
RX_ID = re.compile(r"^h-(\d{4}-\d{2}-\d{2})-\d{2}$")
RX_CAUSA = re.compile(r"\b(causou|provocou|por causa d[oa]|efeito d[oa] evento)\b", re.I)


def _data(s):
    try:
        return dt.date.fromisoformat(s)
    except (TypeError, ValueError):
        return None


def validar(doc, structure):
    """Lista de problemas; vazia = válido."""
    prob = []
    races = structure["races"]
    sq_corrida = {c["sq"]: k for k, r in races.items() for c in r["candidates"]}
    escala = doc.get("escala_kent") or {}
    for k in ("_doc", "_como_julgar", "hipoteses"):
        if k not in doc:
            prob.append(f"arquivo sem `{k}`")
    ids = set()
    for i, h in enumerate(doc.get("hipoteses", [])):
        tag = h.get("id", f"#{i}")
        faltam = CAMPOS - set(h)
        sobram = set(h) - CAMPOS - {"julgado_em", "evidencia"}
        if faltam:
            prob.append(f"{tag}: faltam campos {sorted(faltam)}")
        if sobram:
            prob.append(f"{tag}: campos fora do esquema {sorted(sobram)}")
        m = RX_ID.match(str(h.get("id", "")))
        if not m:
            prob.append(f"{tag}: id fora do padrão h-AAAA-MM-DD-NN")
        elif h.get("registrado_em") != m.group(1):
            prob.append(f"{tag}: registrado_em ({h.get('registrado_em')}) difere da data do id")
        if h.get("id") in ids:
            prob.append(f"{tag}: id repetido")
        ids.add(h.get("id"))
        reg = _data(h.get("registrado_em"))
        jan = h.get("janela") or {}
        ini, fim = _data(jan.get("inicio")), _data(jan.get("fim"))
        if not (reg and ini and fim):
            prob.append(f"{tag}: datas inválidas (registrado_em/janela)")
        else:
            if ini < reg:
                prob.append(f"{tag}: RETROATIVA, a janela ({ini}) começa antes do registro ({reg})")
            if fim < ini:
                prob.append(f"{tag}: janela termina antes de começar")
        if h.get("direcao_esperada") not in ("+", "-"):
            prob.append(f"{tag}: direcao_esperada fora de {{+,-}}")
        if h.get("metrica") not in METRICAS:
            prob.append(f"{tag}: metrica fora de {sorted(METRICAS)}")
        if h.get("status") not in STATUS:
            prob.append(f"{tag}: status fora de {sorted(STATUS)}")
        elif h.get("status") != "aberta" and not (h.get("julgado_em") and h.get("evidencia")):
            prob.append(f"{tag}: status '{h.get('status')}' sem julgado_em/evidencia")
        corrida = h.get("corrida")
        origem = h.get("origem") or {}
        permitidas = set(origem.get("corridas") or []) if corrida == "MULTI" else {corrida}
        if corrida != "MULTI" and corrida not in races:
            prob.append(f"{tag}: corrida {corrida!r} não existe")
        if corrida == "MULTI" and len(permitidas) < 2:
            prob.append(f"{tag}: 'MULTI' exige 2+ corridas em origem.corridas")
        alvo = h.get("alvo") or []
        if not alvo:
            prob.append(f"{tag}: alvo vazio")
        for sq in alvo:
            if sq not in sq_corrida:
                prob.append(f"{tag}: sq {sq} não existe no structure")
            elif sq_corrida[sq] not in permitidas:
                prob.append(f"{tag}: sq {sq} é de {sq_corrida[sq]}, não de {sorted(permitidas)}")
        pr = h.get("probabilidade") or {}
        kent, aprox = pr.get("kent"), pr.get("aprox")
        if kent not in escala:
            prob.append(f"{tag}: palavra de Kent {kent!r} fora da escala")
        elif not (isinstance(aprox, (int, float)) and escala[kent][0] <= aprox <= escala[kent][1]):
            prob.append(f"{tag}: aprox {aprox} fora da faixa de {kent!r} {escala[kent]}")
        if not isinstance(h.get("limiar_pp"), (int, float)) or h.get("limiar_pp") < 0:
            prob.append(f"{tag}: limiar_pp inválido")
        for campo in ("hipotese", "mecanismo"):
            if RX_CAUSA.search(h.get(campo, "")):
                prob.append(f"{tag}: linguagem de causa em `{campo}`")
        if " — " in json.dumps(h, ensure_ascii=False):
            prob.append(f"{tag}: travessão espaçado")
    return prob


def main():
    doc = json.load(open(ARQ, encoding="utf-8"))
    st = json.load(open(STRUCT, encoding="utf-8"))
    prob = validar(doc, st)
    n = len(doc.get("hipoteses", []))
    if prob:
        print(f"REPROVADO: {len(prob)} problema(s) em {n} hipótese(s):", file=sys.stderr)
        for p in prob:
            print("  -", p, file=sys.stderr)
        sys.exit(1)
    abertas = sum(1 for h in doc["hipoteses"] if h["status"] == "aberta")
    print(f"OK: {n} hipótese(s) válida(s), {abertas} aberta(s), todas pré-especificadas.")


if __name__ == "__main__":
    main()
