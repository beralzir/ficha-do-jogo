#!/usr/bin/env python3
"""Converte a saída do survey sintético do vox numa pesquisa do polls.json (C3).

O vox produz respostas por persona; o harness consome pesquisa. Este arquivo é a
ponte, e é o ÚNICO lugar do repo autorizado a escrever `sintetico: true`.

## Regras que este arquivo faz valer

1. **Rotulagem estrutural.** Toda pesquisa que sai daqui tem `sintetico: true` e
   `fonte.tipo` do provedor. Não é convenção de quem escreve: é o que o motor lê
   para decidir se o modelo oficial pode enxergar a linha (`POLL_SOURCE`).
2. **Ponderação por universo.** As personas são alocadas IGUALMENTE entre os 5
   grupos (30 cada, mais precisão nos grupos pequenos), então a agregação PRECISA
   ponderar pelo universo de cada grupo. Sem isso, Bolsonaristas (20,2M) pesariam
   o mesmo que Independentes (44,5M).
3. **Instabilidade viaja junto.** Cada persona responde 2 vezes; quem muda de voto
   entra em `flags` e no campo `instaveis_pct`. Um synth instável que acerta na
   média é sorte, e o número precisa estar visível para dizer isso.
4. **Sem amostra inventada.** `amostra` fica **null**. Uma pesquisa sintética não
   tem margem de erro amostral, e preencher esse campo daria a ela peso de
   pesquisa real no agregador (o peso usa sqrt(amostra)). Com null, o motor usa o
   default de 800, que é deliberadamente modesto.

## Uso

  # a partir da saída real do vox (quando o campo rodar)
  python3 src/synths_para_polls.py --respostas <arquivo.json> --data 2026-08-31

  # MOCK, para provar o encanamento ponta a ponta sem campo
  python3 src/synths_para_polls.py --mock --data 2026-08-31

O mock é marcado com `mock: true` e `instituto: "vox (MOCK)"`, para que ninguém o
confunda com resultado de campo. `--mock` recusa sobrescrever pesquisa não-mock.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
POLLS = os.path.join(ROOT, "data", "live", "polls.json")
STRUCT = os.path.join(ROOT, "data", "eleicoes2026_structure.json")
PUBLICOS = os.path.join(ROOT, "data", "publicos", "audiencias.json")

PROVEDOR = {"vox": "vox", "synth_almap": "synth_almap"}


def carrega(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def universos():
    return {p["slug"]: p["universo"] for p in carrega(PUBLICOS)["publicos"]}


def agrega(por_grupo, pesos):
    """{grupo: {sq: n_votos}} + {grupo: universo} -> {sq: share ponderado}."""
    total_peso = sum(pesos[g] for g in por_grupo if pesos.get(g))
    acc = {}
    for g, votos in sorted(por_grupo.items()):
        n = sum(votos.values())
        if not n or not pesos.get(g):
            continue
        w = pesos[g] / total_peso
        for sq, v in votos.items():
            acc[sq] = acc.get(sq, 0.0) + w * (v / n)
    return acc


def mock_por_grupo(structure):
    """Votos plausíveis por grupo, para provar o encanamento SEM campo.

    Os números vêm de um mapeamento grosseiro grupo->candidato, declarado aqui e
    em lugar nenhum mais. Não representam nada: existem para o pipeline ter uma
    linha sintética com a forma certa e o gate poder ser testado.
    """
    cands = {c["urna"]: c["sq"] for c in structure["races"]["PRES"]["candidates"]
             if c["concorrendo"]}
    def sq(nome):
        for k, v in cands.items():
            if nome.upper() in k.upper():
                return v
        raise KeyError(nome)
    L, F, C, M, Z = (sq("LULA"), sq("FLAVIO BOLSONARO"), sq("CAIADO"),
                     sq("MARÇAL"), sq("ZEMA"))
    return {
        "lulistas":                 {L: 27, F: 1, C: 1, M: 0, Z: 1},
        "esquerda-nao-lulista":     {L: 19, F: 2, C: 4, M: 1, Z: 4},
        "independentes":            {L: 9, F: 8, C: 5, M: 4, Z: 4},
        "direita-nao-bolsonarista": {L: 2, F: 11, C: 8, M: 3, Z: 6},
        "bolsonaristas":            {L: 0, F: 26, C: 2, M: 2, Z: 0},
    }


def monta(shares, data, provedor, mock, instaveis_pct, n_personas):
    urna = {}
    for c in carrega(STRUCT)["races"]["PRES"]["candidates"]:
        urna[c["sq"]] = c["urna"]
    numeros = [{"sq": sq, "alias": urna.get(sq, str(sq)), "pct": round(100 * v, 1)}
               for sq, v in sorted(shares.items(), key=lambda kv: -kv[1]) if v > 0]
    flags = ["sintetico", f"personas_{n_personas}"]
    if mock:
        flags.append("MOCK_sem_campo")
    if instaveis_pct is not None:
        flags.append(f"instaveis_{instaveis_pct:.0f}pct")
    return {
        "id": f"{provedor}-BR-{data}-presidente{'-mock' if mock else ''}",
        "race": "PRES",
        "instituto": f"{provedor} (MOCK)" if mock else provedor,
        "contratante": "Ficha do Jogo (pesquisa própria, sintética)",
        "tse_protocolo": None,
        "campo_ini": data, "campo_fim": data, "divulgacao": data,
        # amostra NULL de propósito: sintético não tem erro amostral, e preencher
        # daria peso de pesquisa real no agregador (o peso usa sqrt(amostra)).
        "amostra": None, "margem_pp": None,
        "metodo": "survey sintético por personas com quotas (vox)",
        "cenario": "estimulada", "par_segundo_turno": None,
        "base": "normalizada_100",
        "numeros": numeros,
        "indefinidos_pct": None,
        "fonte": {"tipo": PROVEDOR.get(provedor, provedor), "url": None,
                  "revid": None, "acesso": data},
        "flags": flags,
        "sintetico": True,          # <- o campo que o motor lê. Estrutural.
        "mock": bool(mock),
        "instaveis_pct": instaveis_pct,
        "corroborada": False,       # sintético nunca é corroborado por outra fonte
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--respostas", help="JSON de respostas do vox")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--data", required=True)
    ap.add_argument("--provedor", default="vox", choices=sorted(PROVEDOR))
    a = ap.parse_args()
    if not a.mock and not a.respostas:
        sys.exit("ERRO: use --respostas <arquivo> ou --mock.")

    structure = carrega(STRUCT)
    if a.mock:
        por_grupo, instaveis, n = mock_por_grupo(structure), None, 150
    else:
        d = carrega(a.respostas)
        por_grupo = {g: {int(k): v for k, v in votos.items()}
                     for g, votos in d["votos_por_grupo"].items()}
        instaveis, n = d.get("instaveis_pct"), d.get("n_personas", 0)

    nova = monta(agrega(por_grupo, universos()), a.data, a.provedor, a.mock, instaveis, n)

    doc = carrega(POLLS)
    if doc.get("schema_version", 1) < 2:
        sys.exit("ERRO: polls.json ainda no schema v1. Rode src/ingest_polls.py antes.")
    antigas = [p for p in doc["polls"] if p["id"] == nova["id"]]
    if antigas and not antigas[0].get("mock") and a.mock:
        sys.exit("ERRO: existe pesquisa NÃO-mock com este id. Mock não sobrescreve campo real.")
    doc["polls"] = [p for p in doc["polls"] if p["id"] != nova["id"]] + [nova]
    doc["polls"].sort(key=lambda p: (p["race"], p["campo_fim"] or "", p["instituto"], p["id"]))
    with open(POLLS, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")

    n_sint = sum(1 for p in doc["polls"] if p.get("sintetico"))
    print(f"OK -> {nova['id']}")
    resumo = "  ".join(f"{x['alias']}={x['pct']}" for x in nova["numeros"][:5])
    print(f"  {resumo}")
    print(f"  polls.json: {len(doc['polls'])} pesquisas, {n_sint} sintética(s)")


if __name__ == "__main__":
    main()
