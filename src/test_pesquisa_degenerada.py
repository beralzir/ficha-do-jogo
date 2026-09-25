#!/usr/bin/env python3
"""Testes da pesquisa degenerada (achado de 24/09/2026, entre as Janelas 2 e 3).

O ERRO PLANTADO AQUI É REAL E ESTÁ NA BASE VERSIONADA: `ctas-sen-se-2026-09-03`
é uma linha da Wikipédia com UM único número (14,2%) e travessão nas outras
colunas. Entrou no polls.json em 14/09 e ficou 10 dias no ar. Passava no
MATCH_MIN com 14,2/14,2 = 1,0 e, como o share é normalizado entre os casados,
aquele candidato recebia 100% naquela pesquisa, com 6 a 8% do peso do SEN-SE.
Foi a origem do sd de 19,6pp publicado para André David, e do alarme de
movimento que segurou o cron por 3 dias quando um editor moveu o 14,2% da
coluna do David para a do Moura: o agregado virou +9,4pp sem nenhuma pesquisa
nova dizer isso (a única nova puxava Moura para BAIXO).

Duas camadas, duas provas:
  MOTOR  `em.usable_polls` com MIN_CASADOS=2 derruba a linha real; com
         MIN_CASADOS=1 (o erro plantado) ela entra e vira 100% de share.
  INGEST NÃO julga estrutura de cenário, e isso é decisão (25/09): um guarda
         de "menos de 2 números" quarentenava linhas "candidato × Outros",
         legítimas, e com GATE_MAX_QUAR=3 derrubou o cron na 1ª reestruturação
         de tabela da Wikipédia (5 linhas). Quarentenada não vira "vista", então
         reprovaria de novo todo dia. O ingest PRESERVA o registro; quem segura
         a linha de um candidato é o motor. Provado com erro plantado nos dois
         sentidos: quarentená-la no ingest reprova, e usá-la no motor reprova.

Usa rede? Não.

Uso:  python3 src/test_pesquisa_degenerada.py
"""
import copy
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eleicoes_model as em     # noqa: E402
import ingest_polls as ip       # noqa: E402

ROOT = os.path.join(HERE, "..")
CTAS = "ctas-sen-se-2026-09-03"
MOURA, DAVID = 260002547290, 260002549130
FALHAS = []


def check(nome, cond, detalhe=""):
    print(f"  {'ok  ' if cond else 'FALHA'} {nome}" + (f"  ({detalhe})" if detalhe else ""))
    if not cond:
        FALHAS.append(nome)


def casados(p):
    return sum(1 for n in p["numeros"] if n.get("sq") and n["pct"] > 0)


def main():
    polls_doc = json.load(open(em.POLLS, encoding="utf-8"))
    polls = polls_doc["polls"]
    st = json.load(open(em.STRUCT, encoding="utf-8"))
    race = st["races"]["SEN-SE"]

    print("1. o erro plantado pela realidade está na base versionada")
    real = [p for p in polls if p.get("id") == CTAS and p["cenario"] == "estimulada"]
    check("a linha ctas-sen-se-2026-09-03 existe no polls.json", len(real) == 1,
          f"{len(real)} ocorrência(s)")
    if not real:
        print("REPROVADO: sem a linha real o teste não prova nada", file=sys.stderr)
        sys.exit(1)
    linha = real[0]
    check("ela tem exatamente UM candidato casado com número", casados(linha) == 1,
          f"casados={casados(linha)}, numeros={[(n['sq'], n['pct']) for n in linha['numeros']]}")
    check("e passa o MATCH_MIN sozinha (é por isso que entrava)",
          sum(n["pct"] for n in linha["numeros"] if n["sq"] is not None)
          / max(sum(n["pct"] for n in linha["numeros"]), 1e-9) >= em.DEFAULTS["MATCH_MIN"])
    check("o share normalizado dela é 100% para um candidato só",
          max(em.poll_shares(linha).values()) == 1.0)

    print("\n2. camada do MOTOR: usable_polls")
    p2 = dict(em.DEFAULTS)
    us = em.usable_polls(polls, p2).get("SEN-SE", [])
    check("com MIN_CASADOS=2 (default) a linha NÃO é usável",
          not any(p.get("id") == CTAS for p in us), f"{len(us)} usáveis em SEN-SE")
    check("o default do motor é 2", em.DEFAULTS["MIN_CASADOS"] == 2)
    p1 = dict(em.DEFAULTS)
    p1["MIN_CASADOS"] = 1
    us1 = em.usable_polls(polls, p1).get("SEN-SE", [])
    check("ERRO PLANTADO: com MIN_CASADOS=1 ela ENTRA (prova que o gate morde)",
          any(p.get("id") == CTAS for p in us1), f"{len(us1)} usáveis")
    # nenhuma pesquisa legítima de 2 casados foi derrubada de carona
    dois = [p for p in em.usable_polls(polls, p1).get("SEN-SE", []) if casados(p) == 2]
    us_ids = {p.get("id") for p in us}
    check("pesquisa de 2 casados continua usável (o gate é cirúrgico)",
          all(p.get("id") in us_ids for p in dois), f"{len(dois)} de 2 casados em SEN-SE")
    # no dado inteiro, o gate derruba EXATAMENTE as usáveis de 1 casado e nada
    # mais. Comparação por CONJUNTO de ids das usáveis, não por contagem bruta:
    # o usable_polls colapsa cenários duplicados por (corrida, instituto, fim), e
    # uma linha de 1 casado que duplique uma pesquisa cheia nunca chega a ser
    # usável. Contar no bruto dava 2 onde o gate derruba 1 (1ª versão, reprovava
    # com o código certo).
    u1 = {p.get("id"): p for v in em.usable_polls(polls, p1).values() for p in v}
    u2 = {p.get("id") for v in em.usable_polls(polls, p2).values() for p in v}
    caiu = set(u1) - u2
    check("no dado inteiro o gate derruba só as usáveis de 1 casado, e todas elas",
          caiu == {i for i, p in u1.items() if casados(p) == 1} and len(caiu) >= 1,
          f"{len(u1)} -> {len(u2)} usáveis, caiu: {sorted(caiu)}")

    print("\n3. o sintoma que estava NO AR some com o gate")
    vis = [p for p in polls if not p.get("sintetico") and p["campo_fim"]]
    as_of = dt.date.fromisoformat(max(p["campo_fim"] for p in vis))
    a2 = em.aggregate_race("SEN-SE", race, us, as_of, p2)
    a1 = em.aggregate_race("SEN-SE", race, us1, as_of, p1)
    dono = next(n["sq"] for n in linha["numeros"] if n.get("sq"))
    check("SEM o gate, o dono do 14,2% carrega um sd absurdo (o sintoma)",
          a1["sd"][dono] * 100 > 15.0, f"sd={a1['sd'][dono]*100:.1f}pp")
    check("COM o gate, o sd dele volta ao normal",
          a2["sd"][dono] * 100 < 8.0, f"sd={a2['sd'][dono]*100:.1f}pp")
    check("e o share dele deixa de ser puxado pelo 100%",
          a1["mu"][dono] > a2["mu"][dono],
          f"{a1['mu'][dono]*100:.1f}% -> {a2['mu'][dono]*100:.1f}%")

    print("\n4. o INGEST preserva a linha de um candidato (não é quarentena)")
    # Decidido em 25/09: um guarda de "menos de 2 números" aqui quarentenava
    # cenários "candidato × Outros", legítimos, e com GATE_MAX_QUAR=3 derrubou o
    # cron na 1ª reestruturação de tabela da Wikipédia. Quem segura é o motor.
    modelo = next(p for p in polls if p["race"] == "SEN-SE" and p["cenario"] == "estimulada"
                  and casados(p) >= 4)
    um = copy.deepcopy(modelo)
    um["id"] = "NOVA-UM-CANDIDATO"
    um["instituto"] = "INSTITUTO-TESTE-UM"      # chave própria: não colide no colapso
    um["numeros"] = [dict(n) for n in modelo["numeros"] if n.get("sq")][:1]
    check("sanidade NÃO acusa linha de um candidato",
          not any("número" in b.lower() or "casado" in b.lower()
                  for b in ip.sanity_violations(um)), f"{ip.sanity_violations(um)}")
    check("o ingest não tem guarda estrutural de números (se voltar, revisar este teste)",
          not hasattr(ip, "GATE_MIN_NUMEROS") and not hasattr(ip, "GATE_MIN_CASADOS"))
    ids = {p["id"] for p in polls}
    ac, quar = ip.plausibility_gate(json.loads(json.dumps(polls)) + [um], ids, {})
    check("pelo gate completo ela ENTRA no registro (erro plantado = quarentená-la)",
          any(p["id"] == "NOVA-UM-CANDIDATO" for p in ac)
          and not any(q["id"] == "NOVA-UM-CANDIDATO" for q in quar))
    check("e entra marcada corroborada=False (base fraca declarada, nunca silenciosa)",
          next((p.get("corroborada") for p in ac if p["id"] == "NOVA-UM-CANDIDATO"), None) is False)
    # as linhas de um número que JÁ estão no registro, tratadas como novas, entram
    um_num = [p for p in polls if p["cenario"] == "estimulada"
              and sum(1 for n in p["numeros"] if n["pct"] > 0) == 1]
    check("há linhas reais de um número no registro (a evidência existe)", len(um_num) >= 1,
          f"{len(um_num)} linha(s)")
    ac2, quar2 = ip.plausibility_gate(json.loads(json.dumps(polls)), set(), {})
    check("com tudo tratado como novo, nenhuma quarentena é por 'número avulso'",
          not any("número avulso" in m or "números com valor" in m or "candidatos casados" in m
                  for q in quar2 for m in q["motivos"]), f"{len(quar2)} quarentena(s) no total")

    print("\n5. uma camada só, e é a do motor")
    check("o motor exclui a linha de um candidato mesmo com o ingest a preservando",
          not any(p.get("id") == "NOVA-UM-CANDIDATO"
                  for v in em.usable_polls(polls + [um], p2).values() for p in v))
    espec = copy.deepcopy(modelo)
    espec["id"] = "NOVA-ESPECULATIVA"
    espec["instituto"] = "INSTITUTO-TESTE-ESPEC"
    nums = [dict(n) for n in modelo["numeros"] if n.get("sq")][:4]
    for n in nums[1:]:
        n["sq"] = None
    espec["numeros"] = nums
    ac3, _ = ip.plausibility_gate(json.loads(json.dumps(polls)) + [espec], ids, {})
    check("pesquisa especulativa (4 números, 1 casado) entra no registro",
          any(p["id"] == "NOVA-ESPECULATIVA" for p in ac3))
    check("e o motor não a usa (MATCH_MIN), sem guarda no ingest",
          not any(p.get("id") == "NOVA-ESPECULATIVA"
                  for v in em.usable_polls(polls + [espec], p2).values() for p in v))
    check("a linha real da CTAS: entra no registro, sai no motor",
          any(p.get("id") == CTAS for p in ac2) and not any(p.get("id") == CTAS for p in us))

    print("\n6. registro e cobertura")
    cfg = json.load(open(os.path.join(ROOT, "data", "eleicoes", "model_configs.json"),
                         encoding="utf-8"))
    check("o modelo OFICIAL declara MIN_CASADOS=2, não herda do default",
          cfg["models"][cfg["official"]]["params"].get("MIN_CASADOS") == 2)
    src = "".join(open(os.path.join(HERE, f), encoding="utf-8").read()
                  for f in ("eleicoes_model.py", "eleicoes_model_v2.py", "eleicoes_inflexoes.py",
                            "eleicoes_runoff_corr.py", "eleicoes_compare.py"))
    check("todo consumidor de pesquisa passa por usable_polls (um só ponto de corte)",
          src.count("usable_polls(") >= 5, f"{src.count('usable_polls(')} chamadas")

    print()
    if FALHAS:
        print(f"REPROVADO: {len(FALHAS)} falha(s): {', '.join(FALHAS)}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: pesquisa degenerada validada · a linha real {CTAS} é derrubada pelo motor "
          f"(sd {a1['sd'][dono]*100:.1f} -> {a2['sd'][dono]*100:.1f}pp) e o ingest "
          f"preserva o registro.")


if __name__ == "__main__":
    main()
