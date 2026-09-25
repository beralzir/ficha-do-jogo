#!/usr/bin/env python3
"""
Validador OFFLINE de data/eleicoes2026_structure.json (gate da etapa B3).
Sem rede, sem dependências. Uso: python3 test_eleicoes_structure.py

Checa: contagem de corridas (1+27+27) e de candidatos (14/201/318 na captura
de 25/09; eram 13/198/318 na de 29/08), unicidade global de SQ, regras por
cargo (seats/two_round), mínimo de 2 concorrendo por corrida, duplicatas de
número de urna (mesma pessoa = WARN, pessoas diferentes = FAIL) e determinismo
do builder (2 runs idênticos).
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
STRUCT = os.path.join(HERE, "..", "data", "eleicoes2026_structure.json")

UFS = {"AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS",
       "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC",
       "SE", "SP", "TO"}

fails, warns = [], []


def check(cond, msg):
    if not cond:
        fails.append(msg)


def main():
    with open(STRUCT, encoding="utf-8") as f:
        d = json.load(f)
    races = d["races"]

    # 1. universo de corridas
    check(len(races) == 55, f"esperava 55 corridas, achei {len(races)}")
    check("PRES" in races, "corrida PRES ausente")
    for pref, cargo, seats, two_round in (("GOV", "governador", 1, True),
                                          ("SEN", "senador", 2, False)):
        got = {k.split("-", 1)[1] for k in races if k.startswith(pref + "-")}
        check(got == UFS, f"{pref}: UFs faltando {sorted(UFS - got)} / sobrando {sorted(got - UFS)}")
        for uf in sorted(got & UFS):
            r = races[f"{pref}-{uf}"]
            check(r["cargo"] == cargo and r["seats"] == seats and r["two_round"] == two_round,
                  f"{pref}-{uf}: regra de cargo errada ({r['cargo']}/{r['seats']}/{r['two_round']})")
    p = races.get("PRES", {})
    check(p.get("seats") == 1 and p.get("two_round") is True and p.get("uf") == "BR",
          "PRES: regra errada")

    # 2. contagens da captura de 2026-09-25 (mudou o raw? atualize aqui junto).
    # Conferidas sq a sq contra o consulta_cand_2026.zip oficial (geração
    # 25/09/2026 12:31:26): o zip traz 14/201/319; a única diferença é Gustavo
    # Galassi (SEN-MG, 130002553354, RENÚNCIA, substituído por Aécio Neves), que
    # a API de listagem deixou de mostrar. Número, cargo e UE batem em todos os
    # outros 533. Na captura de 29/08 eram 13/198/318, iguais ao zip de 27/08.
    by_cargo = {}
    for r in races.values():
        by_cargo[r["cargo"]] = by_cargo.get(r["cargo"], 0) + len(r["candidates"])
    check(by_cargo.get("presidente") == 14, f"presidente: {by_cargo.get('presidente')} != 14")
    check(by_cargo.get("governador") == 201, f"governador: {by_cargo.get('governador')} != 201")
    check(by_cargo.get("senador") == 318, f"senador: {by_cargo.get('senador')} != 318")

    # 3. SQ único global + campos obrigatórios
    seen = {}
    for key, r in races.items():
        for c in r["candidates"]:
            for field in ("sq", "urna", "nome", "numero", "partido", "situacao", "concorrendo"):
                check(c.get(field) is not None, f"{key}: candidato sem campo {field}: {c.get('sq')}")
            if c["sq"] in seen:
                fails.append(f"SQ duplicado entre corridas: {c['sq']} em {seen[c['sq']]} e {key}")
            seen[c["sq"]] = key

    # 4. mínimo de disputa real por corrida
    for key, r in races.items():
        n = sum(1 for c in r["candidates"] if c["concorrendo"])
        check(n >= 2, f"{key}: só {n} candidato(s) concorrendo")

    # 5. número de urna repetido na mesma corrida
    for key, r in races.items():
        by_num = {}
        for c in r["candidates"]:
            by_num.setdefault(c["numero"], []).append(c)
        for num, cs in sorted(by_num.items()):
            if len(cs) < 2:
                continue
            ativos = [c for c in cs if c["concorrendo"]]
            if len(ativos) < 2:
                continue  # substituição (renúncia + substituto) é normal
            nomes = {c["nome"] for c in ativos}
            if len(nomes) == 1:
                warns.append(f"{key}: registro duplicado da mesma pessoa no nº {num} ({ativos[0]['nome']})")
            elif all(c["situacao"] == "Deferido" for c in ativos):
                # duas pessoas DIFERENTES, ambas deferidas em definitivo, mesmo nº: inconsistência real
                fails.append(f"{key}: nº {num} com {len(ativos)} pessoas DIFERENTES deferidas: {sorted(nomes)}")
            else:
                # disputa de registro em andamento (sub judice); o TSE resolve antes da urna
                warns.append(f"{key}: nº {num} disputado sub judice por {sorted(nomes)}")

    # 6. determinismo do builder (2 runs, bytes idênticos)
    builder = os.path.join(HERE, "build_eleicoes_structure.py")
    outs = []
    for _ in range(2):
        with tempfile.TemporaryDirectory() as td:
            env = dict(os.environ)
            r = subprocess.run([sys.executable, builder], capture_output=True, text=True, env=env)
            check(r.returncode == 0, f"builder falhou: {r.stderr.strip()[:200]}")
            with open(STRUCT, "rb") as f:
                outs.append(f.read())
    check(outs[0] == outs[1], "builder não é determinístico (2 runs diferem)")

    for w in warns:
        print(f"WARN: {w}")
    if fails:
        for m in fails:
            print(f"FAIL: {m}")
        print(f"\n{len(fails)} falha(s).")
        return 1
    print(f"OK: 55 corridas, {sum(by_cargo.values())} candidatos, SQ único, "
          f"regras por cargo, determinismo. {len(warns)} warn(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
