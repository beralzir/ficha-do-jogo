#!/usr/bin/env python3
"""Testes do competidor v2_estado (M1, Fase D).

Regra da casa: gate só vale com ERRO PLANTADO. O erro plantado aqui é o BUG que
o pacote de modelagem trazia, e que a verificação de 21/09 pegou antes do commit:

    as_of = max(p["campo_fim"] for p in polls if p["campo_fim"]
                and not p.get("sintetico"))

O filtro `not sintetico` estava CRAVADO em vez de derivar das pesquisas que
aquele modelo enxerga. É a mesma classe que o C3 corrigiu no motor oficial em
31/08, quando o oficial não lia dado sintético mas herdava o as_of dele: o gate
não pegou, o diff byte a byte pegou. Vazamento de metadado é vazamento igual.

O caso 3 planta uma pesquisa sintética DEPOIS da última real e exige que o
modelo `real` a ignore; o caso 4 exige o contrário do modelo `sintetico`. A
expressão antiga é executada lado a lado e tem de ERRAR, senão o teste não
estaria provando nada.

Usa rede? Não.

Uso:  python3 src/test_v2_estado.py
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eleicoes_model as em        # noqa: E402
import eleicoes_model_v2 as v2     # noqa: E402

ROOT = os.path.join(HERE, "..")
FALHAS = []


def check(nome, cond, detalhe=""):
    print(f"  {'ok  ' if cond else 'FALHA'} {nome}" + (f"  ({detalhe})" if detalhe else ""))
    if not cond:
        FALHAS.append(nome)


def as_of_bug_antigo(polls_doc):
    """A expressão do pacote, ANTES da correção. Existe só para o teste provar
    que ela erra: teste de regressão sem o bug ao lado não prova regressão."""
    return max(p["campo_fim"] for p in polls_doc["polls"]
               if p["campo_fim"] and not p.get("sintetico"))


def planta_synth_futura(polls_doc, data):
    """Copia o doc e planta uma pesquisa SINTÉTICA depois de toda pesquisa real."""
    doc = copy.deepcopy(polls_doc)
    modelo = next(p for p in doc["polls"] if p.get("sintetico"))
    nova = copy.deepcopy(modelo)
    nova["id"] = "PLANTADA-teste-as-of"
    nova["campo_ini"] = nova["campo_fim"] = nova["divulgacao"] = data
    doc["polls"].append(nova)
    return doc


def main():
    structure = em.load(em.STRUCT)
    polls_doc = em.load(em.POLLS)
    real_max = max(p["campo_fim"] for p in polls_doc["polls"]
                   if p["campo_fim"] and not p.get("sintetico"))
    print(f"base real: {len(polls_doc['polls'])} pesquisas · última real {real_max}\n")

    # 1. zero-dep: o competidor não pode arrastar dependência nova
    print("1. zero-dep e disciplina de import")
    fonte = open(os.path.join(HERE, "eleicoes_model_v2.py"), encoding="utf-8").read()
    proibidos = ("numpy", "scipy", "numpyro", "jax", "pandas", "requests", "urllib")
    achados = [m for m in proibidos if f"import {m}" in fonte]
    check("nenhuma dependência externa", not achados, f"achados: {achados}")
    check("sem rede", "http" not in fonte.replace("https://pt.wikipedia", ""),
          "nenhuma URL no fonte")
    check("POLL_SOURCE nasce 'real'", em.DEFAULTS["POLL_SOURCE"] == "real")

    # 2. invariantes, no NSIMS de produção
    print("\n2. invariantes das 55 corridas")
    out = v2.simulate_v2(structure, polls_doc, v2.params_v2(), verbose=False)
    bad = em.check_invariants(out)
    check("invariantes do oficial valem para o v2", not bad, f"{len(bad)} violação(ões)")
    somas_ok = True
    for key, r in sorted(out["races"].items()):
        s = sum(c["share"] for c in r["candidates"])
        if abs(s - 1.0) > 0.005:
            somas_ok = False
            print(f"      {key}: Σshare={s:.4f}")
    check("Σshare = 1 em toda corrida", somas_ok)

    # 3. ERRO PLANTADO: synth DEPOIS da última real, modelo 'real' tem de ignorar
    print("\n3. erro plantado: pesquisa sintética posterior a toda pesquisa real")
    futura = "2026-09-25"
    doc_p = planta_synth_futura(polls_doc, futura)
    params_real = v2.params_v2({"NSIMS": 200, "POLL_SOURCE": "real"})
    out_real = v2.simulate_v2(structure, doc_p, params_real, verbose=False)
    check("v2 'real' NÃO herda o as_of da sintética", out_real["meta"]["as_of"] == real_max,
          f"as_of={out_real['meta']['as_of']}, esperado {real_max}")
    check("v2 'real' declara poll_source=real", out_real["meta"]["poll_source"] == "real")
    check("v2 'real' declara usa_sintetico=False", out_real["meta"]["usa_sintetico"] is False)
    # a expressão antiga acerta NESTA direção: por isso o caso 4 existe
    check("(controle) a expressão antiga também acerta aqui",
          as_of_bug_antigo(doc_p) == real_max, "o bug não aparece nesta direção")

    # 4. ERRO PLANTADO na direção em que o bug APARECE
    print("\n4. erro plantado: o modelo sintético tem de ver a data DELE")
    params_synth = v2.params_v2({"NSIMS": 200, "POLL_SOURCE": "sintetico"})
    out_synth = v2.simulate_v2(structure, doc_p, params_synth, verbose=False)
    check("v2 'sintetico' usa o as_of da sintética", out_synth["meta"]["as_of"] == futura,
          f"as_of={out_synth['meta']['as_of']}, esperado {futura}")
    check("v2 'sintetico' declara usa_sintetico=True",
          out_synth["meta"]["usa_sintetico"] is True)
    antigo = as_of_bug_antigo(doc_p)
    check("o BUG do pacote ERRA aqui (prova que o teste morde)", antigo != futura,
          f"expressão antiga daria {antigo}, o certo é {futura}")

    # 5. determinismo
    print("\n5. determinismo")
    p_det = v2.params_v2({"NSIMS": 500})
    a = json.dumps(v2.simulate_v2(structure, polls_doc, p_det, verbose=False), sort_keys=True)
    b = json.dumps(v2.simulate_v2(structure, polls_doc, p_det, verbose=False), sort_keys=True)
    check("duas execuções byte-idênticas", a == b, f"{len(a)} bytes")

    # 6. o competidor tem de ser DIFERENTE do oficial, senão não mede nada
    print("\n6. o competidor é estruturalmente diferente")
    of = em.simulate(structure, polls_doc, dict(em.DEFAULTS), verbose=False)
    a_p = {c["sq"]: c["share"] for c in of["races"]["PRES"]["candidates"]}
    b_p = {c["sq"]: c["share"] for c in out["races"]["PRES"]["candidates"]}
    dif = max(abs(a_p[sq] - b_p[sq]) for sq in a_p) * 100
    check("share da presidencial difere do oficial", dif > 0.5, f"máx {dif:.2f}pp")
    trocas = 0
    for k in sorted(of["races"]):
        x = max(of["races"][k]["candidates"], key=lambda c: c["eleito"], default=None)
        y = max(out["races"][k]["candidates"], key=lambda c: c["eleito"], default=None)
        if x and y and x["sq"] != y["sq"]:
            trocas += 1
    check("há corrida em que os dois discordam do favorito", trocas > 0,
          f"{trocas}/55 corridas")

    # 7. o registro tem de bater com o código
    print("\n7. registro x código")
    cfg = json.load(open(os.path.join(ROOT, "data", "eleicoes", "model_configs.json"),
                         encoding="utf-8"))
    ent = cfg["models"].get(v2.MODEL_ID)
    check("v2_estado está no model_configs.json", ent is not None)
    if ent:
        check("declara engine próprio", ent.get("engine") == v2.MODEL_ID)
        check("NÃO é o modelo oficial do site", cfg["official"] != v2.MODEL_ID)
        check("não se declara sintético", not ent.get("sintetico"))
        faltando = [k for k in sorted(v2.DEFAULTS_V2) if k not in ent.get("params", {})]
        check("todo hiperparâmetro viaja no freeze", not faltando, f"faltando: {faltando}")
        import eleicoes_run_models as run
        check("o despacho resolve o engine", run.motor(ent.get("engine")) is v2.simulate_v2)

    print()
    if FALHAS:
        print(f"REPROVADO: {len(FALHAS)} falha(s): {', '.join(FALHAS)}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: competidor v2_estado validado · {dif:.2f}pp de diferença no share da "
          f"presidencial, {trocas}/55 corridas discordam do favorito.")


if __name__ == "__main__":
    main()
