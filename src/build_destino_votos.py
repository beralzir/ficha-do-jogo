#!/usr/bin/env python3
"""
Extrai o DESTINO DO VOTO por candidatura (achado de 03/10/2026) do arquivo
oficial consulta_cand_complementar_2026 do TSE e grava
data/eleicoes/destino_votos.json.

Por que existe: a API de listagem (de onde vem candidatos_raw.json) mostra a
situação do REGISTRO, mas quem decide se o voto conta é o campo
NM_TIPO_DESTINACAO_VOTOS do complementar. Em 03/10, 54 majoritários inseridos
na urna tinham destino "Nulo técnico" ou "Anulado sub judice" e o modelo tratava
todos como voto válido (Arruda no GOV-DF com 21% e 48% de 2º turno, Salles
no SEN-SP com 15,7% depois de renunciar).

O complementar é baixado à mão (cdn.tse.jus.br, odsele/consulta_cand_complementar)
e fica em .cache/tse/ (gitignored). Este script grava SÓ três campos por sq da
captura (destino, inserido na urna, geração): nada de CPF, processo ou protocolo.

Uso: python3 build_destino_votos.py [caminho do CSV]
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
RAW = os.path.join(ROOT, "data", "live", "candidatos_raw.json")
OUT = os.path.join(ROOT, "data", "eleicoes", "destino_votos.json")
CSV_PADRAO = os.path.join(ROOT, ".cache", "tse", "consulta_cand_complementar_2026_BRASIL.csv")
FONTE = ("consulta_cand_complementar_2026.zip (cdn.tse.jus.br/estatistica/sead/odsele/"
         "consulta_cand_complementar/), campo NM_TIPO_DESTINACAO_VOTOS")


def sqs_da_captura():
    with open(RAW, encoding="utf-8") as f:
        raw = json.load(f)
    return {row[0] for r in raw["pres_gov"] + raw["senado"] for row in r["c"]}


def extrai(caminho, sqs):
    destino, geracoes = {}, set()
    with open(caminho, encoding="latin-1", newline="") as f:
        for row in csv.DictReader(f, delimiter=";"):
            sq = int(row["SQ_CANDIDATO"])
            if sq not in sqs:
                continue
            na_urna = row["ST_CANDIDATO_INSERIDO_URNA"] == "SIM"
            dest = row["NM_TIPO_DESTINACAO_VOTOS"]
            if na_urna == (dest == "#NULO"):
                raise ValueError(f"sq {sq}: inserido={row['ST_CANDIDATO_INSERIDO_URNA']!r} "
                                 f"com destino {dest!r}, combinação não prevista")
            destino[str(sq)] = dest
            geracoes.add(f"{row['DT_GERACAO']} {row['HH_GERACAO']}")
    if len(geracoes) != 1:
        raise ValueError(f"arquivo com mais de uma geração: {sorted(geracoes)}")
    return destino, geracoes.pop()


def main():
    caminho = sys.argv[1] if len(sys.argv) > 1 else CSV_PADRAO
    sqs = sqs_da_captura()
    destino, geracao = extrai(caminho, sqs)
    faltam = sorted(sqs - {int(k) for k in destino})
    if faltam:
        print(f"PARADO: {len(faltam)} sq da captura fora do complementar: {faltam[:10]}",
              file=sys.stderr)
        return 1
    out = {"meta": {"fonte": FONTE, "geracao": geracao,
                    "nota": "Valor verbatim do TSE. '#NULO' = não inserido na urna."},
           "destino": {k: destino[k] for k in sorted(destino, key=int)}}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    cont = {}
    for v in destino.values():
        cont[v] = cont.get(v, 0) + 1
    print(f"OK: {len(destino)} sq, geração {geracao}, {dict(sorted(cont.items()))} "
          f"-> {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
