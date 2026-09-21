#!/usr/bin/env python3
"""
Datação de movimento · Eleições 2026 (M2 da Fase D).

O site mostra o NÍVEL. Não responde "quando mudou e quanto", que é a pergunta de
onde sai a página de Inflexões e, depois, o estudo de evento do M3.

MÉTODO: resíduo padronizado da inovação do filtro do `eleicoes_model_v2`,
(y - previsão)/sqrt(S). |z| acima do limiar marca CANDIDATO a ponto de inflexão.
É o que os agregadores clássicos fazem.

O QUE ISTO NÃO FAZ, e está escrito no JSON para viajar junto do dado: o resíduo
padronizado detecta o salto mas NÃO separa "o nível saltou X p.p." de "saiu uma
pesquisa fora da curva". Quem separa é a versão bayesiana com cauda de Student,
em que o salto vira parâmetro com intervalo, e ela não entra no repo (zero-dep).

Por isso o campo `corroborado`: o remédio para falso positivo em corrida pequena
é exigir um SEGUNDO resíduo grande, do MESMO sinal, de instituto DIFERENTE, na
janela. Não é baixar o limiar. Uma pesquisa fora da curva é de um instituto só;
movimento de verdade aparece em mais de um.

DUAS ESCALAS, nomeadas: `delta_dia_pp` é o quanto o nível saltou naquele dia;
`delta_janela_pp` é a variação de nível na janela seguinte. Confundi-las é fácil
e a segunda costuma ser o dobro da primeira.

Não roda Monte Carlo: o salto sai do filtro, não do sorteio.

Uso:  python3 src/eleicoes_inflexoes.py
      TOP=20 python3 src/eleicoes_inflexoes.py   # quantas imprimir
"""
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)

import eleicoes_model as em        # noqa: E402
import eleicoes_model_v2 as v2     # noqa: E402

OUT = os.path.join(ROOT, "data", "eleicoes", "inflexoes.json")
CONFIGS = os.path.join(ROOT, "data", "eleicoes", "model_configs.json")
CORROB_D = int(os.environ.get("CORROB_D", "7"))   # janela da corroboração, em dias
# reaproveitado da métrica pré-especificada do harness, não inventado aqui
MIN_SHARE = __import__("eleicoes_compare").MIN_SHARE


def corrobora(lista):
    """Marca cada salto corroborado por OUTRO instituto, mesmo sinal, na janela.

    `lista`: saltos de UM candidato numa corrida, cada um com data/z/instituto.
    """
    for a in lista:
        da = dt.date.fromisoformat(a["data"])
        conf = []
        for b in lista:
            if b is a or b["instituto"] == a["instituto"]:
                continue
            if (a["z"] > 0) != (b["z"] > 0):          # sinal oposto não corrobora
                continue
            if abs((dt.date.fromisoformat(b["data"]) - da).days) <= CORROB_D:
                conf.append(b["instituto"])
        a["corroborado"] = bool(conf)
        a["corroborado_por"] = sorted(set(conf))
    return lista


def main():
    cfg = json.load(open(CONFIGS, encoding="utf-8"))
    params = v2.params_v2(cfg["models"][v2.MODEL_ID].get("params", {}))
    structure = em.load(em.STRUCT)
    polls_doc = em.load(em.POLLS)

    # as_of das pesquisas VISÍVEIS a este modelo, mesma regra do motor (C3).
    fonte = params.get("POLL_SOURCE", "real")
    visiveis = [p for p in polls_doc["polls"]
                if not (fonte == "real" and p.get("sintetico"))
                and not (fonte == "sintetico" and not p.get("sintetico"))]
    as_of_str = max((p["campo_fim"] for p in visiveis if p["campo_fim"]),
                    default="2026-08-29")
    as_of = dt.date.fromisoformat(as_of_str)
    by_race = em.usable_polls(polls_doc["polls"], params)

    bruto = []
    nivel_hoje = {}
    for key in sorted(structure["races"]):
        race = structure["races"][key]
        plist = by_race.get(key, [])
        if not plist:
            continue
        agg = v2.aggregate_race_v2(key, race, plist, as_of, params)
        saltos = agg.get("_saltos") or {}
        urna = {c["sq"]: c["urna"] for c in race["candidates"]}
        for sq in sorted(saltos):
            nivel_hoje[(key, sq)] = agg["mu"].get(sq, 0.0)
            for s in corrobora(list(saltos[sq])):
                bruto.append({"corrida": key, "sq": sq, "urna": urna.get(sq, "?"), **s})

    # AGRUPA por (corrida, candidato, dia): duas pesquisas do mesmo dia com resíduo
    # grande são UM evento de datação, não dois. Sem isso o artefato conta duas vezes.
    grupos = {}
    for r in bruto:
        k = (r["corrida"], r["sq"], r["data"])
        g = grupos.setdefault(k, {
            "corrida": r["corrida"], "sq": r["sq"], "urna": r["urna"], "data": r["data"],
            "z": 0.0, "n_obs": 0, "institutos": [], "corroborado": False,
            "corroborado_por": [], "delta_dia_pp": r["delta_dia_pp"],
            "delta_janela_pp": r["delta_janela_pp"]})
        if abs(r["z"]) > abs(g["z"]):
            g["z"] = r["z"]
        g["n_obs"] += 1
        g["institutos"].append(r["instituto"])
        g["corroborado"] = g["corroborado"] or r["corroborado"]
        g["corroborado_por"] += r["corroborado_por"]
    infl = []
    for g in grupos.values():
        g["institutos"] = sorted(set(g["institutos"]))
        g["corroborado_por"] = sorted(set(g["corroborado_por"]))
        # RELEVANTE usa o MIN_SHARE de 2% JÁ PRÉ-ESPECIFICADO na métrica do
        # harness (eleicoes_compare.py). Limiar reaproveitado de propósito: um
        # corte novo inventado agora seria escolhido olhando o resultado.
        g["relevante"] = nivel_hoje.get((g["corrida"], g["sq"]), 0.0) >= MIN_SHARE
        infl.append(g)

    # ordena por movimento de NÍVEL, não por z: z grande com nível parado é
    # pesquisa fora da curva, que é o que o método não sabe separar.
    infl.sort(key=lambda r: (-abs(r["delta_janela_pp"]), -abs(r["z"]), r["corrida"]))
    destaques = [r for r in infl if r["corroborado"] and r["relevante"]]

    doc = {
        "schema_version": 1,
        "as_of": as_of_str,
        "gerado_por": "src/eleicoes_inflexoes.py",
        "modelo": v2.MODEL_ID,
        "params": {"Z_SALTO": params["Z_SALTO"], "JANELA_SALTO": params["JANELA_SALTO"],
                   "CORROB_D": CORROB_D, "MIN_SHARE": MIN_SHARE},
        "metodo": ("resíduo padronizado da inovação do filtro de Kalman do "
                   "eleicoes_model_v2; |z| acima de Z_SALTO marca candidato a ponto "
                   "de inflexão; agrupado por (corrida, candidato, dia)"),
        "criterio_destaque": ("corroborado por 2+ institutos E candidato com share >= "
                              "MIN_SHARE. Os dois critérios são PRÉ-ESPECIFICADOS: o "
                              "primeiro é o remédio que o plano da Fase D manda usar "
                              "no lugar de baixar o limiar, e o segundo é o MIN_SHARE "
                              "que a métrica do harness já usava desde a B5."),
        "ressalvas": [
            "CANDIDATO a inflexão, não inflexão confirmada: o resíduo padronizado não "
            "separa salto de nível de pesquisa fora da curva.",
            "MAGNITUDE SUBESTIMADA POR CONSTRUÇÃO, e isto foi medido. O passeio é "
            "gaussiano em LOGIT com SIGMA_RW constante, calibrado num 2º turno em que "
            "os dois candidatos estavam perto de 50%. Como d(share)/d(logit) = p(1-p), "
            "o mesmo passeio vale 0,33 p.p./dia para quem está em 50% e 0,06 p.p./dia "
            "para quem está em 5%. O memo atribui a Cury +3,0 p.p. num dia com share de "
            "~5%: para este filtro aceitar isso, SIGMA_RW teria de ser 48x o calibrado. "
            "Aqueles números vêm do ajuste bayesiano com cauda de Student, em que o "
            "salto é parâmetro próprio, e esse ajuste NÃO entra no repo (zero-dep). "
            "Conclusão prática: confie na DATA, desconfie da magnitude.",
            "A data, essa, confere: o episódio de Cury que o plano cita em 27/08 aparece "
            "aqui em 26/08 e 27/08, corroborado por instituto diferente.",
            "delta_dia_pp e delta_janela_pp são escalas diferentes: salto do nível no dia "
            "contra variação do nível na janela seguinte.",
            "Coincidir com um evento NÃO é causa. A atribuição é o M3, e depende de "
            "direção pré-especificada e de janela placebo.",
            "Corrida com poucas pesquisas produz resíduo instável: olhe corroborado e "
            "institutos antes de acreditar.",
        ],
        "n": len(infl),
        "n_destaques": len(destaques),
        "inflexoes": infl,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")

    top = int(os.environ.get("TOP", "12"))
    print(f"{len(infl)} candidato(s) a inflexão (agrupados) em "
          f"{len(set(r['corrida'] for r in infl))} corrida(s) · as_of {as_of_str}")
    print(f"funil: |z|>{params['Z_SALTO']:.0f} -> {len(infl)} · corroborado -> "
          f"{sum(1 for r in infl if r['corroborado'])} · + share>={MIN_SHARE:.0%} -> "
          f"{len(destaques)} destaques")
    print(f"\n{'corrida':9s} {'candidato':22s} {'data':10s} {'z':>7s} {'dia':>7s} "
          f"{'janela':>7s}  institutos")
    for r in destaques[:top]:
        print(f"{r['corrida']:9s} {r['urna'][:22]:22s} {r['data']:10s} {r['z']:7.2f} "
              f"{r['delta_dia_pp']:+7.2f} {r['delta_janela_pp']:+7.2f}  "
              f"{','.join(r['institutos'][:2])}")
    print(f"\nOK -> data/eleicoes/inflexoes.json")


if __name__ == "__main__":
    main()
