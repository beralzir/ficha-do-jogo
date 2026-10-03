#!/usr/bin/env python3
"""
Gera data/eleicoes2026_structure.json a partir de data/live/candidatos_raw.json.

O raw é o dump verificado (SHA-256 na sessão de captura) da API pública do
DivulgaCandContas (eleição 20322002026, cargos 1/3/5). O CDN/API do TSE devolve
403 Akamai fora de navegador real, então a captura é feita via navegador e
committada; este builder é OFFLINE e determinístico (ordenações explícitas).

Refresh: recapturar o raw (mesma sessão de navegador do wrangler dev ou CI, se
passar), rodar este script, conferir o diff. Ver docs/handoff-eleicoes.md.

Regra `concorrendo` (desde 03/10/2026 manda o DESTINO DO VOTO do TSE, lido de
data/eleicoes/destino_votos.json, gerado por build_destino_votos.py):
  - "Nulo técnico" ou "#NULO": NÃO concorre. O nome pode estar na urna, mas o
    voto nele é nulo e sai do denominador dos válidos.
  - "Anulado sub judice": concorre (o voto vale se o registro for deferido, Lei
    9.504/1997, art. 16-A), mesmo com a API mostrando "Indeferido".
  - "Válido": regra da API, totalizacao == "Concorrendo" E situacao fora de
    NAO_CONCORRE.
  Sq da captura sem destino, ou destino fora dos quatro valores: o builder PARA
  (fail-closed) e um humano baixa o complementar novo.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "live", "candidatos_raw.json")
OUT = os.path.join(HERE, "..", "data", "eleicoes2026_structure.json")
DESTINO = os.path.join(HERE, "..", "data", "eleicoes", "destino_votos.json")

UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS",
       "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC",
       "SE", "SP", "TO"]

NAO_CONCORRE = {"Renúncia", "Cancelado", "Indeferido", "Pedido não conhecido",
                "Não conhecimento do pedido", "Falecido"}

# Destino do voto (NM_TIPO_DESTINACAO_VOTOS, verbatim do TSE). Substituiu, em
# 03/10/2026, a exceção manual EXCECOES_SUB_JUDICE (Arruda, GOV-DF, 25/09): a
# premissa dela ("Anulado sub judice") venceu quando o TSE passou o destino para
# "Nulo técnico", e o builder não percebeu porque só lia a situação da API.
DESTINOS = {"Válido", "Anulado sub judice", "Nulo técnico", "#NULO"}


class DestinoVencido(Exception):
    """Captura e destino_votos.json não batem: baixar o complementar novo."""


def _cand(row, destino):
    sq, urna, nome, numero, partido, situacao, totalizacao = row
    dest = destino.get(str(sq))
    if dest is None:
        raise DestinoVencido(
            f"sq {sq} ({urna}) sem destino do voto em destino_votos.json: baixe o "
            f"complementar novo do TSE e rode build_destino_votos.py.")
    if dest not in DESTINOS:
        raise DestinoVencido(f"sq {sq} ({urna}): destino do voto desconhecido {dest!r}.")
    if dest == "Anulado sub judice":
        concorrendo = totalizacao == "Concorrendo"
    elif dest == "Válido":
        concorrendo = (totalizacao == "Concorrendo") and (situacao not in NAO_CONCORRE)
    else:
        concorrendo = False
    return {
        "sq": sq,
        "urna": urna,
        "nome": nome,
        "numero": numero,
        "partido": partido,
        "situacao": situacao,
        "concorrendo": concorrendo,
        "destino_voto": dest,
    }


def build(raw, destino_doc):
    destino = destino_doc["destino"]
    races = {}
    for r in raw["pres_gov"] + raw["senado"]:
        ue, cargo = r["ue"], r["cargo"]
        if cargo == 1:
            key, nome_cargo, seats, two_round = "PRES", "presidente", 1, True
        elif cargo == 3:
            key, nome_cargo, seats, two_round = f"GOV-{ue}", "governador", 1, True
        elif cargo == 5:
            key, nome_cargo, seats, two_round = f"SEN-{ue}", "senador", 2, False
        else:
            raise ValueError(f"cargo inesperado: {cargo}")
        cands = sorted((_cand(c, destino) for c in r["c"]),
                       key=lambda c: (c["numero"], c["sq"]))
        races[key] = {
            "cargo": nome_cargo,
            "uf": "BR" if ue == "BR" else ue,
            "seats": seats,
            "two_round": two_round,
            "candidates": cands,
        }
    return {
        "meta": {
            "edition": "eleicoes2026",
            "election_id": 20322002026,
            "source": raw["source"],
            "source_fetched_at": raw["fetched_at"],
            "dates": {"turno1": "2026-10-04", "turno2": "2026-10-25"},
            "notes": [
                "Chave canônica de candidato: sq (SQ_CANDIDATO do TSE).",
                "Senado 2026: 2 vagas por UF, sem 2º turno (eleitor vota em 2 nomes).",
                "concorrendo é flag derivada do destino do voto (ver build_eleicoes_structure.py): "
                "'Nulo técnico' não concorre, 'Anulado sub judice' concorre.",
                f"Destino do voto: {destino_doc['meta']['fonte']}, geração "
                f"{destino_doc['meta']['geracao']}.",
            ],
        },
        "races": {k: races[k] for k in sorted(races)},
    }


def main():
    with open(RAW, encoding="utf-8") as f:
        raw = json.load(f)
    with open(DESTINO, encoding="utf-8") as f:
        destino_doc = json.load(f)
    try:
        out = build(raw, destino_doc)
    except DestinoVencido as e:
        print(f"PARADO: {e}", file=sys.stderr)
        return 1
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write("\n")
    n = sum(len(r["candidates"]) for r in out["races"].values())
    print(f"OK: {len(out['races'])} corridas, {n} candidatos -> {os.path.relpath(OUT, os.path.join(HERE, '..'))}")


if __name__ == "__main__":
    sys.exit(main())
