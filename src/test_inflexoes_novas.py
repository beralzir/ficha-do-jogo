#!/usr/bin/env python3
"""Testes do diff de inflexões por rodada ("Novas nesta rodada").

O detector do M2 já rodava em toda rodada, mas ninguém saberia que apareceu um
movimento novo sem comparar dois JSONs à mão. `eleicoes_inflexoes.novas_vs`
compara os destaques desta rodada com os da rodada anterior (HEAD do git, o
mesmo padrão do check_movimento) e grava `novas_desde_ultima_rodada`, que a
página e o resumo do cron leem.

ERROS PLANTADOS (rodados no código de produção, não só aqui):
  1. Ignorar a rodada anterior: tudo vira "novo" todo dia, e a página passa a
     gritar sempre. O bloco 1 exige zero novas contra si mesma.
  2. Contar candidato a inflexão NÃO corroborado como nova: é o funil do M2
     vazando pela porta dos fundos. O bloco 2 injeta um e exige que não conte.

Usa rede? Não.

Uso:  python3 src/test_inflexoes_novas.py
"""
import copy
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eleicoes_inflexoes as ei   # noqa: E402

ROOT = os.path.join(HERE, "..")
FALHAS = []


def check(nome, cond, detalhe=""):
    print(f"  {'ok  ' if cond else 'FALHA'} {nome}" + (f"  ({detalhe})" if detalhe else ""))
    if not cond:
        FALHAS.append(nome)


def fake(base, corrida, sq, data, **over):
    f = copy.deepcopy(base)
    f.update({"corrida": corrida, "sq": sq, "urna": f"TESTE {sq}", "data": data,
              "corroborado": True, "relevante": True})
    f.update(over)
    return f


def main():
    doc = json.load(open(os.path.join(ROOT, "data", "eleicoes", "inflexoes.json"), encoding="utf-8"))
    dest = [r for r in doc["inflexoes"] if r["corroborado"] and r["relevante"]]
    check("há destaques na base", len(dest) >= 10, f"{len(dest)}")

    print("\n1. ERRO PLANTADO 1: contra si mesma, nada é novo")
    nv = ei.novas_vs(dest, dest, doc, "self")
    check("zero novas", nv["n"] == 0 and nv["itens"] == [], f"n={nv['n']}")
    check("referência declarada", nv["sem_referencia"] is False and nv["as_of_anterior"] == doc["as_of"])

    print("\n2. ERRO PLANTADO 2: destaque injetado aparece; não-destaque, não")
    novo = fake(dest[0], "GOV-ZZ", 999000001, "2026-09-23")
    nv = ei.novas_vs(dest + [novo], dest + [novo], doc, "self")
    check("o destaque injetado é a única nova", nv["n"] == 1 and nv["itens"][0]["sq"] == 999000001)
    nao = fake(dest[0], "GOV-ZZ", 999000002, "2026-09-23", corroborado=False)
    nv = ei.novas_vs(dest + [nao], dest + [nao], doc, "self")
    check("candidato NÃO corroborado não vira nova", nv["n"] == 0, f"n={nv['n']}")
    irr = fake(dest[0], "GOV-ZZ", 999000003, "2026-09-23", relevante=False)
    nv = ei.novas_vs(dest + [irr], dest + [irr], doc, "self")
    check("candidato com share < 2% (irrelevante) não vira nova", nv["n"] == 0)

    print("\n3. remoção não é novidade")
    menos = dest[1:]
    nv = ei.novas_vs(menos, menos, doc, "self")
    check("perder um destaque antigo não gera nova", nv["n"] == 0)

    print("\n4. choque comum em torno das novas")
    d = "2026-09-23"
    tres = [fake(dest[0], "GOV-ZZ", 999000011, d), fake(dest[0], "GOV-YY", 999000012, d),
            fake(dest[0], "SEN-ZZ", 999000013, d)]
    nv = ei.novas_vs(dest + tres, dest + tres, doc, "self")
    ch = [c for c in nv["choques_comuns_com_novas"] if c["data"] == d]
    check("3 candidatos de 2+ corridas no mesmo dia = choque comum",
          ch and ch[0]["n_candidatos"] >= 3 and len(ch[0]["corridas"]) >= 2, f"{ch}")
    dois = [fake(dest[0], "GOV-ZZ", 999000021, "2026-09-27"), fake(dest[0], "GOV-ZZ", 999000022, "2026-09-27")]
    nv = ei.novas_vs(dest + dois, dest + dois, doc, "self")
    check("2 candidatos da MESMA corrida não é choque comum",
          not any(c["data"] == "2026-09-27" for c in nv["choques_comuns_com_novas"]))

    print("\n5. a referência do git")
    prev = ei.anterior("HEAD")
    check("HEAD devolve um inflexoes.json", isinstance(prev, dict) and "inflexoes" in prev)
    check("referência inexistente falha ABERTA (None), não derruba", ei.anterior("ref-que-nao-existe") is None)
    nv = ei.novas_vs(dest, dest, None, "nada")
    check("sem referência: declarado, zero novas", nv["sem_referencia"] is True and nv["n"] == 0)

    print("\n6. o arquivo gerado e a página")
    nvj = doc.get("novas_desde_ultima_rodada") or {}
    check("o JSON carrega novas_desde_ultima_rodada", all(k in nvj for k in ("ref", "n", "itens", "sem_referencia")))
    html = open(os.path.join(ROOT, "dist", "eleicoes_inflexoes.html"), encoding="utf-8").read()
    if nvj.get("sem_referencia"):
        check("página declara a falta de referência", "Primeira rodada com registro" in html)
    elif nvj.get("n", 0) == 0:
        check("página diz que não há movimento novo", "Nenhum movimento novo nesta rodada" in html)
    else:
        check("página mostra o bloco de novas", "Novas nesta rodada" in html)
        check("e lista cada nova", all(x["data"][8:10] in html for x in nvj["itens"][:3]))

    print("\n7. o resumo do cron lista")
    out = subprocess.run([sys.executable, "scripts/resumo_eleicoes.py"], cwd=ROOT,
                         env={**os.environ, "RESUMO_REF": "HEAD"}, capture_output=True, text=True).stdout
    check("o sumário do run tem a linha de inflexões novas", "Inflexões novas" in out or "inflexão(ões) nova(s)" in out,
          out.strip().splitlines()[-1][:80] if out.strip() else "sem saída")

    print()
    if FALHAS:
        print(f"REPROVADO: {len(FALHAS)} falha(s): {', '.join(FALHAS)}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: diff de inflexões por rodada validado · {len(dest)} destaques, "
          f"{nvj.get('n', 0)} nova(s) nesta rodada.")


if __name__ == "__main__":
    main()
