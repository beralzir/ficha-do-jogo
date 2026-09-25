#!/usr/bin/env python3
"""Testes do validador de hipóteses pré-especificadas.

O arquivo real tem de passar; e cinco erros plantados têm de ser RECUSADOS, cada
um o vazamento que o M3 existe para evitar:
  1. hipótese RETROATIVA (janela começa antes do registro);
  2. sq que não existe no structure;
  3. id repetido;
  4. alvo de outra corrida;
  5. status fechado ('confirmada') sem julgado_em/evidencia.
Mais: linguagem de causa e Kent fora da faixa.

Usa rede? Não.

Uso:  python3 src/test_hipoteses.py
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eleicoes_hipoteses as eh   # noqa: E402

FALHAS = []


def check(nome, cond, detalhe=""):
    print(f"  {'ok  ' if cond else 'FALHA'} {nome}" + (f"  ({detalhe})" if detalhe else ""))
    if not cond:
        FALHAS.append(nome)


def main():
    doc = json.load(open(eh.ARQ, encoding="utf-8"))
    st = json.load(open(eh.STRUCT, encoding="utf-8"))
    print("1. o arquivo real")
    prob = eh.validar(doc, st)
    check("valida sem problema", not prob, f"{prob[:3]}")
    check("tem hipóteses", len(doc["hipoteses"]) >= 6, f"{len(doc['hipoteses'])}")
    check("todas abertas ao nascer", all(h["status"] == "aberta" for h in doc["hipoteses"]))
    check("todas registradas antes da janela",
          all(h["janela"]["inicio"] >= h["registrado_em"] for h in doc["hipoteses"]))
    check("a doutrina está no arquivo", "racionalização" in doc["_doc"] and "julgado_em" in doc["_como_julgar"])

    def recusa(nome, muta):
        d = copy.deepcopy(doc)
        muta(d)
        p = eh.validar(d, st)
        check(f"RECUSA: {nome}", bool(p), f"{p[:1]}" if p else "aceitou")

    print("\n2. erros plantados")
    recusa("hipótese retroativa", lambda d: d["hipoteses"][0]["janela"].update(inicio="2026-09-01"))
    recusa("sq inexistente", lambda d: d["hipoteses"][0].update(alvo=[123]))
    recusa("id repetido", lambda d: d["hipoteses"].append(copy.deepcopy(d["hipoteses"][0])))

    def outra_corrida(d):
        h = next(x for x in d["hipoteses"] if x["corrida"] != "MULTI")
        h["corrida"] = "GOV-SP" if h["corrida"] != "GOV-SP" else "GOV-RJ"
    recusa("alvo de outra corrida", outra_corrida)
    recusa("fechada sem evidência", lambda d: d["hipoteses"][0].update(status="confirmada"))
    recusa("linguagem de causa", lambda d: d["hipoteses"][0].update(mecanismo="o debate causou a queda"))
    recusa("Kent fora da faixa", lambda d: d["hipoteses"][0]["probabilidade"].update(kent="provável", aprox=0.95))
    recusa("campo fora do esquema", lambda d: d["hipoteses"][0].update(resultado="deu certo"))
    recusa("travessão espaçado", lambda d: d["hipoteses"][0].update(titulo="isto — aquilo"))
    recusa("MULTI com uma corrida só", lambda d: d["hipoteses"][0].update(corrida="MULTI", origem={"tipo": "destaque", "datas": [], "corridas": ["PRES"]}))

    print("\n3. fechar uma hipótese do jeito certo é ACEITO")
    d = copy.deepcopy(doc)
    d["hipoteses"][0].update(status="falsa", julgado_em="2026-10-05",
                             evidencia={"arquivo": "data/eleicoes2026_results.json", "as_of": "2026-10-03", "valor": 6.4})
    check("status fechado com julgado_em e evidencia passa", not eh.validar(d, st))

    print()
    if FALHAS:
        print(f"REPROVADO: {len(FALHAS)} falha(s): {', '.join(FALHAS)}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: validador de hipóteses · {len(doc['hipoteses'])} reais válidas, 10 erros plantados recusados.")


if __name__ == "__main__":
    main()
