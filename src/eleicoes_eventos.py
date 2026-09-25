#!/usr/bin/env python3
"""
Registro de eventos da campanha: validador e lista de trabalho (M3 da Fase D).

O `eventos.json` é CURADO À MÃO, como o dossiê da Copa. Este script não escreve
eventos: valida os que existem e imprime o que falta curar. Gerar evento
automaticamente seria fabricar a variável independente do próprio estudo.

O QUE ELE PROTEGE. Com ~50 eventos num ano e um detector que acha alguns saltos,
sempre haverá "um evento perto" de qualquer salto. O que separa análise de
racionalização é a `direcao_esperada` ter sido escrita ANTES de olhar o efeito.
Por isso `pre_especificado` é DERIVADO aqui, como (registrado_em <= data), e não
existe no arquivo: campo declarável seria preenchido com boa-fé retroativa, que é
o viés que o método existe para evitar. A regra é conservadora, evento registrado
no dia seguinte já conta como exploratório.

LISTA DE TRABALHO (--worklist). Imprime as datas em que o M2 viu movimento
corroborado e que ainda não têm evento no raio da janela. É insumo de CURADORIA,
não de análise, e tudo que entrar por ali nasce exploratório por construção: a
data veio do detector, então a direção nunca foi cega. Está separado no relatório
justamente para que essa origem não se perca.

Uso:
    python3 src/eleicoes_eventos.py              # valida e resume
    python3 src/eleicoes_eventos.py --worklist   # datas que pedem curadoria
"""
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)

EVENTOS = os.path.join(ROOT, "data", "eleicoes", "eventos.json")
INFLEX = os.path.join(ROOT, "data", "eleicoes", "inflexoes.json")
STRUCT = os.path.join(ROOT, "data", "eleicoes2026_structure.json")

# "candidatura" (entrada, saída, confirmação e substituição de candidato) entrou em
# 25/09/2026 por decisão do Bera: é a classe que domina agosto, mês do registro,
# e o validador a recusava. Indeferimento e cassação seguem em decisao_judicial.
TIPOS = ("debate", "decisao_judicial", "denuncia", "peca_desinformacao",
         "economico", "pesquisa_bomba", "candidatura")
DIRECOES = ("+", "-", "?")
ESCOPOS = ("nacional", "UF")
RAIO_D = 7   # proximidade evento/inflexão, em dias, na lista de trabalho


def pre_especificado(ev):
    """DERIVADO, nunca lido do arquivo. Ver docstring."""
    return ev["registrado_em"] <= ev["data"]


def valida(doc, sqs_validos):
    """Devolve lista de problemas. Vazia = registro íntegro."""
    ruim = []
    vistos = set()
    for i, ev in enumerate(doc.get("eventos", [])):
        w = f"evento[{i}] {ev.get('id', '(sem id)')!r}"
        for campo in ("id", "data", "registrado_em", "tipo", "alvo",
                      "direcao_esperada", "escopo", "fonte"):
            if campo not in ev:
                ruim.append(f"{w}: falta o campo obrigatório {campo!r}")
        if "id" in ev:
            if ev["id"] in vistos:
                ruim.append(f"{w}: id repetido")
            vistos.add(ev["id"])
        for campo in ("data", "registrado_em"):
            if campo in ev:
                try:
                    dt.date.fromisoformat(ev[campo])
                except (ValueError, TypeError):
                    ruim.append(f"{w}: {campo}={ev.get(campo)!r} não é data ISO")
        if ev.get("tipo") not in TIPOS:
            ruim.append(f"{w}: tipo {ev.get('tipo')!r} fora de {TIPOS}")
        if ev.get("direcao_esperada") not in DIRECOES:
            ruim.append(f"{w}: direcao_esperada {ev.get('direcao_esperada')!r} "
                        f"fora de {DIRECOES}")
        if ev.get("escopo") not in ESCOPOS:
            ruim.append(f"{w}: escopo {ev.get('escopo')!r} fora de {ESCOPOS}")
        alvo = ev.get("alvo")
        if not isinstance(alvo, list) or not alvo:
            ruim.append(f"{w}: alvo tem de ser lista não vazia de sq")
        else:
            for sq in alvo:
                if sq not in sqs_validos:
                    ruim.append(f"{w}: sq {sq} não existe na structure")
        f = ev.get("fonte") or {}
        for campo in ("url", "veiculo", "acesso"):
            if not f.get(campo):
                ruim.append(f"{w}: fonte.{campo} vazio. Evento sem procedência não "
                            f"entra: é a diferença entre registro e lembrança.")
        # o campo proibido: pré-especificação é derivada, não declarada
        if "pre_especificado" in ev:
            ruim.append(f"{w}: o campo 'pre_especificado' NÃO pode estar no arquivo. "
                        f"Ele é derivado de (registrado_em <= data). Declará-lo seria "
                        f"exatamente o viés que o M3 existe para evitar.")
    return ruim


def worklist():
    """Datas com movimento corroborado e sem evento por perto."""
    if not os.path.exists(INFLEX):
        return []
    infl = json.load(open(INFLEX, encoding="utf-8"))
    doc = json.load(open(EVENTOS, encoding="utf-8"))
    datas_ev = [dt.date.fromisoformat(e["data"]) for e in doc["eventos"]]
    falta = {}
    for r in infl["inflexoes"]:
        if not (r["corroborado"] and r["relevante"]):
            continue
        d = dt.date.fromisoformat(r["data"])
        if any(abs((d - x).days) <= RAIO_D for x in datas_ev):
            continue
        k = (r["data"], r["corrida"])
        cur = falta.get(k)
        if cur is None or abs(r["delta_janela_pp"]) > abs(cur["delta_janela_pp"]):
            falta[k] = r
    return sorted(falta.values(), key=lambda r: -abs(r["delta_janela_pp"]))


def main():
    structure = json.load(open(STRUCT, encoding="utf-8"))
    sqs = {c["sq"] for r in structure["races"].values() for c in r["candidates"]}
    doc = json.load(open(EVENTOS, encoding="utf-8"))
    ruim = valida(doc, sqs)
    if ruim:
        print(f"REGISTRO DE EVENTOS REPROVADO: {len(ruim)} problema(s)", file=sys.stderr)
        for p in ruim:
            print(f"  {p}", file=sys.stderr)
        sys.exit(1)

    evs = doc["eventos"]
    pre = [e for e in evs if pre_especificado(e)]
    exp = [e for e in evs if not pre_especificado(e)]
    print(f"registro íntegro · {len(evs)} evento(s): {len(pre)} PRÉ-ESPECIFICADO(S), "
          f"{len(exp)} exploratório(s)")
    for e in sorted(evs, key=lambda e: e["data"]):
        marca = "pré-esp." if pre_especificado(e) else "EXPLOR. "
        print(f"  {e['data']}  {marca}  {e['tipo']:18s} {e['direcao_esperada']}  {e['id']}")
    if not pre:
        print("\nNENHUM evento pré-especificado ainda. Só evento com direção escrita "
              "ANTES do fato sustenta afirmação de efeito no estudo do M3; o que há "
              "hoje serve para exercitar o método, não para concluir nada.")

    if "--worklist" in sys.argv:
        w = worklist()
        print(f"\nLISTA DE TRABALHO: {len(w)} data(s) com movimento corroborado e sem "
              f"evento no raio de {RAIO_D} dias.")
        print("Tudo que entrar por aqui nasce EXPLORATÓRIO: a data veio do detector, "
              "então a direção nunca foi cega. Curar assim mesmo é legítimo e útil; "
              "chamar de confirmação, não.")
        print(f"\n{'data':10s} {'corrida':9s} {'candidato':24s} {'nível':>7s}  institutos")
        for r in w[:20]:
            print(f"{r['data']:10s} {r['corrida']:9s} {r['urna'][:24]:24s} "
                  f"{r['delta_janela_pp']:+7.2f}  {','.join(r['institutos'][:2])}")


if __name__ == "__main__":
    main()
