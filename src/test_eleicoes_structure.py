#!/usr/bin/env python3
"""
Validador OFFLINE de data/eleicoes2026_structure.json (gate da etapa B3).
Sem rede, sem dependências. Uso: python3 test_eleicoes_structure.py

Checa: contagem de corridas (1+27+27) e de candidatos (14/201/318 na captura
de 25/09; eram 13/198/318 na de 29/08), unicidade global de SQ, regras por
cargo (seats/two_round), mínimo de 2 concorrendo por corrida, duplicatas de
número de urna (mesma pessoa = WARN, pessoas diferentes = FAIL), determinismo
do builder (2 runs idênticos) e a exceção sub judice (EXCECOES_SUB_JUDICE do
builder): cada entrada tem de estar aplicada e declarada no meta.notes, vira WARN
visível a cada rodada, e o builder tem de PARAR se a situação da API mudar ou se
o sq sumir da captura (dois erros plantados, rodados no build() de produção).
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
STRUCT = os.path.join(HERE, "..", "data", "eleicoes2026_structure.json")
RAW = os.path.join(HERE, "..", "data", "live", "candidatos_raw.json")
sys.path.insert(0, HERE)
import build_eleicoes_structure as bes  # noqa: E402

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

    # 5b. exceção sub judice: aplicada, declarada e fail-closed
    notas = d["meta"].get("notes", [])
    for sq, exc in sorted(bes.EXCECOES_SUB_JUDICE.items()):
        c = next((c for c in races.get(exc["corrida"], {}).get("candidates", []) if c["sq"] == sq), None)
        if c is None:
            fails.append(f"exceção sub judice: sq {sq} fora de {exc['corrida']}")
            continue
        check(c["situacao"] == exc["situacao_api"] and c["concorrendo"] is True,
              f"exceção sub judice não aplicada: sq {sq} ({c['situacao']!r}, concorrendo={c['concorrendo']})")
        check(any(str(sq) in n and exc["registrada_em"] in n for n in notas),
              f"exceção sub judice sem declaração no meta.notes: sq {sq}")
        warns.append(f"exceção sub judice ativa: sq {sq} ({exc['urna']}, {exc['corrida']}) desde "
                     f"{exc['registrada_em']}; reavalie no complementar do TSE a cada recaptura")
    with open(RAW, encoding="utf-8") as f:
        raw = json.load(f)
    for sq, exc in sorted(bes.EXCECOES_SUB_JUDICE.items()):
        # erro plantado 1: a situação da API muda (ex.: Cancelado) e a exceção seguiria valendo
        plantado = json.loads(json.dumps(raw))
        for r in plantado["pres_gov"] + plantado["senado"]:
            for row in r["c"]:
                if row[0] == sq:
                    row[5] = "Cancelado"
        try:
            bes.build(plantado)
            fails.append(f"erro plantado: situação mudou para 'Cancelado' e o builder NÃO parou (sq {sq})")
        except bes.ExcecaoVencida:
            pass
        # erro plantado 2: o sq some da captura e a exceção ficaria órfã
        plantado = json.loads(json.dumps(raw))
        for r in plantado["pres_gov"] + plantado["senado"]:
            r["c"] = [row for row in r["c"] if row[0] != sq]
        try:
            bes.build(plantado)
            fails.append(f"erro plantado: sq {sq} sumiu da captura e o builder NÃO parou")
        except bes.ExcecaoVencida:
            pass

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
