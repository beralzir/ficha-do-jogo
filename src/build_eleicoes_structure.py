#!/usr/bin/env python3
"""
Gera data/eleicoes2026_structure.json a partir de data/live/candidatos_raw.json.

O raw é o dump verificado (SHA-256 na sessão de captura) da API pública do
DivulgaCandContas (eleição 20322002026, cargos 1/3/5). O CDN/API do TSE devolve
403 Akamai fora de navegador real, então a captura é feita via navegador e
committada; este builder é OFFLINE e determinístico (ordenações explícitas).

Refresh: recapturar o raw (mesma sessão de navegador do wrangler dev ou CI, se
passar), rodar este script, conferir o diff. Ver docs/handoff-eleicoes.md.

Regra `concorrendo` (soft flag; a lista oficial na urna é do TSE):
  totalizacao == "Concorrendo" E situacao fora de {Renúncia, Cancelado,
  Indeferido "seco", Pedido não conhecido}. "Indeferido em prazo recursal ou
  com recurso" e "Aguardando julgamento" CONTAM como concorrendo (sub judice).
  Exceção explícita: EXCECOES_SUB_JUDICE (abaixo), com fonte e data por entrada.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "live", "candidatos_raw.json")
OUT = os.path.join(HERE, "..", "data", "eleicoes2026_structure.json")

UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS",
       "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC",
       "SE", "SP", "TO"]

NAO_CONCORRE = {"Renúncia", "Cancelado", "Indeferido", "Pedido não conhecido",
                "Não conhecimento do pedido", "Falecido"}

# EXCEÇÃO SUB JUDICE (decisão do Bera, 25/09/2026). A regra acima lê a situação
# da API de listagem, que passa a mostrar "Indeferido" assim que o TSE confirma o
# indeferimento. A urna pode ficar para trás: o arquivo oficial complementar ainda
# traz o candidato INSERIDO na urna, com situação de urna "INDEFERIDO EM PRAZO
# RECURSAL OU COM RECURSO" e votos "Anulado sub judice". Enquanto for assim, ele
# conta como concorrendo, igual a qualquer sub judice.
# Não é regra geral: cada entrada tem fonte e data, e só vale para a situação da
# API registrada nela. Se a situação mudar, ou se o sq sumir da captura, o builder
# PARA (fail-closed) e um humano reavalia com o complementar novo. A cada
# recaptura, confira no complementar se a situação de urna ainda é a da fonte.
EXCECOES_SUB_JUDICE = {
    70002552586: {
        "urna": "ARRUDA",
        "corrida": "GOV-DF",
        "situacao_api": "Indeferido",
        "registrada_em": "2026-09-25",
        "fonte": ("consulta_cand_complementar_2026.zip (cdn.tse.jus.br), geração "
                  "25/09/2026 12:31:26: DS_SITUACAO_JULGAMENTO_URNA e "
                  "DS_SITUACAO_CANDIDATO_TOT 'INDEFERIDO EM PRAZO RECURSAL OU COM "
                  "RECURSO', ST_CANDIDATO_INSERIDO_URNA 'SIM', "
                  "NM_TIPO_DESTINACAO_VOTOS 'Anulado sub judice'"),
    },
}


class ExcecaoVencida(Exception):
    """Exceção sub judice que não bate mais com a captura: reavaliar à mão."""


def _cand(row):
    sq, urna, nome, numero, partido, situacao, totalizacao = row
    concorrendo = (totalizacao == "Concorrendo") and (situacao not in NAO_CONCORRE)
    exc = EXCECOES_SUB_JUDICE.get(sq)
    if exc is not None:
        if situacao != exc["situacao_api"]:
            raise ExcecaoVencida(
                f"sq {sq} ({urna}): a exceção sub judice foi registrada para a situação "
                f"{exc['situacao_api']!r} e a captura traz {situacao!r}. Reavalie no "
                f"complementar do TSE e atualize ou remova EXCECOES_SUB_JUDICE.")
        concorrendo = totalizacao == "Concorrendo"
    return {
        "sq": sq,
        "urna": urna,
        "nome": nome,
        "numero": numero,
        "partido": partido,
        "situacao": situacao,
        "concorrendo": concorrendo,
    }


def build(raw):
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
        cands = sorted((_cand(c) for c in r["c"]),
                       key=lambda c: (c["numero"], c["sq"]))
        races[key] = {
            "cargo": nome_cargo,
            "uf": "BR" if ue == "BR" else ue,
            "seats": seats,
            "two_round": two_round,
            "candidates": cands,
        }
    for sq, exc in sorted(EXCECOES_SUB_JUDICE.items()):
        corrida = races.get(exc["corrida"], {"candidates": []})
        if not any(c["sq"] == sq for c in corrida["candidates"]):
            raise ExcecaoVencida(
                f"sq {sq} ({exc['urna']}) não está em {exc['corrida']} na captura: "
                f"reavalie e remova a entrada de EXCECOES_SUB_JUDICE.")
    notas_exc = [
        f"Exceção sub judice: sq {sq} ({exc['urna']}, {exc['corrida']}) conta como "
        f"concorrendo com situação da API {exc['situacao_api']!r}, registrada em "
        f"{exc['registrada_em']}. Fonte: {exc['fonte']}."
        for sq, exc in sorted(EXCECOES_SUB_JUDICE.items())]
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
                "concorrendo é flag derivada (ver build_eleicoes_structure.py); sub judice conta como concorrendo.",
            ] + notas_exc,
        },
        "races": {k: races[k] for k in sorted(races)},
    }


def main():
    with open(RAW, encoding="utf-8") as f:
        raw = json.load(f)
    try:
        out = build(raw)
    except ExcecaoVencida as e:
        print(f"PARADO: {e}", file=sys.stderr)
        return 1
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write("\n")
    n = sum(len(r["candidates"]) for r in out["races"].values())
    print(f"OK: {len(out['races'])} corridas, {n} candidatos -> {os.path.relpath(OUT, os.path.join(HERE, '..'))}")


if __name__ == "__main__":
    sys.exit(main())
