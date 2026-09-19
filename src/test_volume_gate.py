#!/usr/bin/env python3
"""Testes do alarme de volume por corrida (D2).

Regra da casa: gate só vale depois de provado com ERRO PLANTADO. Aqui o erro
plantado mais forte não precisou ser inventado: o INCIDENTE REAL está no histórico
do git. O caso 2 reproduz a rodada de 04/09/2026, em que a presidencial perdeu 558
pesquisas estimuladas de uma vez, e exige que o alarme a reprove. Um alarme que não
pega o incidente que o motivou não serve.

Usa rede? Não. Usa `git show` para ler commits que já estão no repositório.

Uso:  python3 src/test_volume_gate.py
"""
import collections
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_volume as cv  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# Commits que cercam o incidente, na main. Se a main for reescrita e estes sumirem,
# o teste FALHA em vez de passar de mentira: silenciar a prova é pior que não tê-la.
ANTES_DO_INCIDENTE = "e061871"   # 2026-09-03
DEPOIS_DO_INCIDENTE = "4f84e57"  # 2026-09-04

FALHAS = []


def check(nome, cond, detalhe=""):
    print(f"  {'ok  ' if cond else 'FALHA'} {nome}" + (f"  ({detalhe})" if detalhe else ""))
    if not cond:
        FALHAS.append(nome)


def do_commit(sha):
    out = subprocess.run(["git", "show", f"{sha}:data/live/polls.json"],
                         cwd=ROOT, capture_output=True)
    if out.returncode != 0:
        return None
    return json.loads(out.stdout)


def migra(doc):
    """polls.json antigo é schema v1, sem a flag `sintetico`. O alarme só conta
    pesquisa real, então a flag precisa existir para o teste medir o que mede."""
    for p in doc.get("polls", []):
        p["sintetico"] = bool(p.get("sintetico", False))
    return doc


def main():
    atual = migra(json.load(open(cv.POLLS, encoding="utf-8")))
    print(f"base real: {len(atual['polls'])} pesquisas\n")

    # 1. O dado real de hoje, comparado consigo mesmo, não pode disparar.
    print("1. dado real não dispara o alarme")
    v = cv.volumes(atual)
    check("nenhuma queda contra si mesmo", not cv.quedas(v, v))
    check("conta por (corrida, cenário), não por corrida", len(v) > 55,
          f"{len(v)} pares para 55 corridas")

    # 2. ERRO PLANTADO PELA REALIDADE: a rodada em que o incidente aconteceu.
    print("\n2. erro plantado real: a rodada de 04/09/2026")
    a_doc, b_doc = do_commit(ANTES_DO_INCIDENTE), do_commit(DEPOIS_DO_INCIDENTE)
    if a_doc is None or b_doc is None:
        check(f"commits do incidente existem ({ANTES_DO_INCIDENTE}, "
              f"{DEPOIS_DO_INCIDENTE})", False, "git show falhou")
    else:
        qs = cv.quedas(cv.volumes(migra(a_doc)), cv.volumes(migra(b_doc)))
        pres = [q for q in qs if q[2] == "PRES" and q[3] == "estimulada"]
        check("alarme PEGA a perda da presidencial", bool(pres),
              f"{pres[0][1]} pesquisas, {pres[0][0]:.1f}%" if pres else "passou batido")
        check("alarme não arrasta corrida saudável junto", len(qs) == 1,
              f"{len(qs)} corrida(s) acusada(s)")

        # É AQUI que o alarme por corrida se paga. No MESMO limiar, o total não
        # denuncia: 3.523 -> 3.008 é queda de 14,6%, abaixo dos 20%, porque a
        # perda de uma corrida se dilui em 55. A presidencial, sozinha, cai 99,1%.
        ta = sum(cv.volumes(a_doc).values())
        tb = sum(cv.volumes(b_doc).values())
        queda_total = (ta - tb) / ta * 100
        check("o TOTAL, no mesmo limiar, não teria denunciado",
              queda_total <= cv.LIM_PCT,
              f"total caiu {queda_total:.1f}%, limiar {cv.LIM_PCT:.0f}%")

    # 2b. E 14 dias depois o total já tinha se recuperado, enquanto a presidencial
    #     seguia com 11% do dado. Qualquer vigilância sobre o total teria ficado
    #     muda; a vigilância por corrida continua acusando.
    print("\n2b. 14 dias depois: o total se recupera, a corrida não")
    hoje_doc = do_commit("origin/main")
    if a_doc is None or hoje_doc is None:
        check("commit de origin/main legível", False)
    else:
        va, vh = cv.volumes(migra(a_doc)), cv.volumes(migra(hoje_doc))
        ta, th = sum(va.values()), sum(vh.values())
        check("total praticamente igual ao de antes do incidente",
              abs(th - ta) / ta * 100 < 2.0, f"{ta} -> {th}")
        qs2 = cv.quedas(va, vh)
        pres2 = [q for q in qs2 if q[2] == "PRES" and q[3] == "estimulada"]
        check("mas o alarme por corrida continua acusando a presidencial",
              bool(pres2),
              f"{pres2[0][4]} -> {pres2[0][5]} ({pres2[0][0]:.1f}%)" if pres2 else "mudo")

    # 3. ERRO PLANTADO sintético: some com 88% de uma corrida qualquer.
    print("\n3. erro plantado: 88% de uma corrida somem")
    alvo = max(((n, k) for k, n in v.items()), key=lambda x: x[0])[1]
    resto = [p for p in atual["polls"]
             if not (p["race"] == alvo[0] and p["cenario"] == alvo[1])]
    mantidas = [p for p in atual["polls"]
                if p["race"] == alvo[0] and p["cenario"] == alvo[1]][: max(1, v[alvo] // 8)]
    qs3 = cv.quedas(v, cv.volumes({"polls": resto + mantidas}))
    check(f"alarme pega a perda em {alvo[0]}/{alvo[1]}",
          any(q[2] == alvo[0] and q[3] == alvo[1] for q in qs3),
          f"{qs3[0][1]} pesquisas, {qs3[0][0]:.1f}%" if qs3 else "passou batido")

    # 4. RUÍDO REAL não pode disparar. Nas 20 rodadas do robô as únicas quedas
    #    legítimas foram de UMA pesquisa (GOV-PE, 05/09). Se o alarme reprovar
    #    isso, vira carimbo ignorado em duas semanas.
    print("\n4. ruído real não dispara")
    for perder, rotulo in ((1, "1 pesquisa a menos (caso real GOV-PE)"),
                           (cv.LIM_ABS - 1, f"{cv.LIM_ABS - 1} a menos (abaixo do piso absoluto)")):
        falsos = []
        for k, n in v.items():
            if n <= perder:
                continue
            b = dict(v); b[k] = n - perder
            falsos += [q for q in cv.quedas(v, b)]
        check(rotulo, not falsos,
              f"{len(falsos)} falso(s) positivo(s)" if falsos else "")
    # e uma queda grande em corrida pequena também não, por causa do piso absoluto
    pequena = min(v.items(), key=lambda x: x[1])
    b = dict(v); b[pequena[0]] = pequena[1] - (cv.LIM_ABS - 1)
    check(f"queda de {cv.LIM_ABS - 1} na menor corrida ({pequena[0][0]}, {pequena[1]}) "
          f"não dispara", not cv.quedas(v, b))

    # 5. Pesquisa sintética não entra na conta: ela é nosso experimento, e contá-la
    #    deixaria o alarme de perda de dado refém do C3.
    print("\n5. sintética fica fora da conta")
    com_synth = {"polls": atual["polls"] + [dict(atual["polls"][0], id="SYNTH-X",
                                                 sintetico=True)]}
    check("adicionar sintética não muda o volume medido",
          cv.volumes(com_synth) == v)

    # 6. Determinismo.
    print("\n6. determinismo")
    check("duas execuções são idênticas", cv.quedas(v, v) == cv.quedas(v, v))

    print()
    if FALHAS:
        print(f"REPROVADO: {len(FALHAS)} falha(s): {', '.join(FALHAS)}")
        sys.exit(1)
    print(f"OK: alarme de volume validado (queda > {cv.LIM_PCT:.0f}% E "
          f">= {cv.LIM_ABS} pesquisas), incluindo replay do incidente de 04/09.")


if __name__ == "__main__":
    main()
