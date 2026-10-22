#!/usr/bin/env python3
"""
Gate da APURAÇÃO do 1º turno no motor (22/10/2026, plano-segundo-turno.md).

Depois de 04/10 o motor precisa saber o que a urna decidiu: corrida decidida não
é simulada e corrida com 2º turno tem o par FIXO (o da urna). O resultado mora em
data/eleicoes/resultado_1t.json, curado do TSE, e entra pela
`em.anexa_resultado_1t`, nunca pelo `simulate()` direto.

O que este teste prova, com uma apuração CONSTRUÍDA sobre a structure e o
polls.json do dia (independe do arquivo real existir):
  1. sem o arquivo, a structure volta intacta (o motor de antes da apuração);
  2. decidida: eleito = 1 para quem ganhou, 0 para o resto, sem sorteio;
  3. 2º turno: t2 = 1 só para os finalistas, nenhum t1_win, e a prob do par bate
     com `runoff_prob_from_polls` quando há pesquisa do par;
  4. 2º turno sem pesquisa do par: repasse dos votos válidos (o favorito no 1º
     turno é favorito no 2º);
  5. o arquivo de produção tem de cobrir as 55 corridas (parcial reprova);
  6. o gate do arquivo reprova os erros de curadoria plantados.
Erro plantado no motor (rodado à mão em 22/10): ignorar `r1t` no laço reprova 2 a 4.

Usa rede? Não.

Uso:  python3 src/test_segundo_turno.py
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eleicoes_model as em        # noqa: E402

FALHAS = []


def check(nome, cond, detalhe=""):
    print(f"  {'ok  ' if cond else 'FALHA'} {nome}" + (f"  ({detalhe})" if detalhe else ""))
    if not cond:
        FALHAS.append(nome)


def vv_de(shares, top_max):
    """Votos válidos plausíveis a partir do share agregado: o 1º colocado fica em
    `top_max` e o resto se divide na proporção do share."""
    ordem = sorted(shares, key=lambda sq: (-shares[sq], sq))
    resto = sum(shares[sq] for sq in ordem[1:]) or 1.0
    out = {ordem[0]: top_max}
    for sq in ordem[1:]:
        out[sq] = (1.0 - top_max) * shares[sq] / resto
    return ordem, out


def main():
    st = em.load(em.STRUCT)
    pd = em.load(em.POLLS)
    params = dict(em.DEFAULTS)
    params["NSIMS"] = 4000
    base = em.simulate(st, pd, params, verbose=False)

    print("1. sem o arquivo, a structure volta intacta")
    check("anexa_resultado_1t sem arquivo devolve o mesmo objeto",
          em.anexa_resultado_1t(st, path=os.path.join(HERE, "nao-existe.json")) is st)

    # par do 2º turno com e sem pesquisa de par no polls.json do dia
    pares_2t = {}
    for p in pd["polls"]:
        if p["cenario"] == "segundo_turno" and p["campo_fim"]:
            sqs = tuple(sorted(n["sq"] for n in p["numeros"] if n["sq"] is not None))
            if len(sqs) == 2:
                pares_2t.setdefault(p["race"], set()).add(sqs)
    shares = {k: {c["sq"]: c["share"] for c in r["candidates"]} for k, r in base["races"].items()}

    r1t = {}
    ordem, vv = vv_de(shares["PRES"], 0.47)
    par_pres = tuple(sorted(ordem[:2]))
    check("a presidencial do dia tem pesquisa de 2T do par dos 2 primeiros",
          par_pres in pares_2t.get("PRES", set()))
    r1t["PRES"] = {"status": "segundo_turno", "finalistas": list(par_pres), "votos_validos": vv}
    ordem, vv = vv_de(shares["GOV-SP"], 0.56)
    r1t["GOV-SP"] = {"status": "decidida", "eleitos": [ordem[0]], "votos_validos": vv}
    ordem, vv = vv_de(shares["SEN-SP"], 0.30)
    r1t["SEN-SP"] = {"status": "decidida", "eleitos": ordem[:2], "votos_validos": vv}
    # 2T sem pesquisa do par: no dado real todo governo tem pesquisa do par dos 2
    # primeiros, então a urna construída põe o 1º contra o 3º do agregado.
    sem_par = None
    for k in sorted(base["races"]):
        r = base["races"][k]
        if not r["two_round"] or k in r1t or len(r["candidates"]) < 4:
            continue
        o = sorted(shares[k], key=lambda sq: (-shares[k][sq], sq))
        if tuple(sorted((o[0], o[2]))) not in pares_2t.get(k, set()):
            sem_par = k
            break
    check("há governo sem pesquisa de 2T do par 1º x 3º para o caso 4", sem_par is not None, sem_par)
    if sem_par is None:
        sys.exit(1)
    o = sorted(shares[sem_par], key=lambda sq: (-shares[sem_par][sq], sq))
    ordem_sp = [o[0], o[2]] + [sq for sq in o if sq not in (o[0], o[2])]
    resto = sum(shares[sem_par][sq] for sq in ordem_sp[2:]) or 1.0
    vv_sp = {o[0]: 0.44, o[2]: 0.30}
    vv_sp.update({sq: 0.26 * shares[sem_par][sq] / resto for sq in ordem_sp[2:]})
    if max(vv_sp[sq] for sq in ordem_sp[2:]) >= 0.30:
        sys.exit("fixture do caso 4 não fecha: 3º colocado construído passou do 2º")
    r1t[sem_par] = {"status": "segundo_turno", "finalistas": sorted(ordem_sp[:2]),
                    "votos_validos": vv_sp}

    check("a apuração construída passa no gate", em.valida_resultado_1t(r1t, st, completo=False) == [],
          em.valida_resultado_1t(r1t, st, completo=False)[:2])
    st_a = copy.deepcopy(st)
    st_a["resultado_1t"] = r1t
    out = em.simulate(st_a, pd, params, verbose=False)
    out_b = em.simulate(st_a, pd, params, verbose=False)
    check("invariantes verdes com a apuração", em.check_invariants(out) == [],
          em.check_invariants(out)[:2])
    check("determinístico", json.dumps(out, sort_keys=True) == json.dumps(out_b, sort_keys=True))

    print("\n2. decidida: sem sorteio")
    for k in ("GOV-SP", "SEN-SP"):
        el = {c["sq"]: c["eleito"] for c in out["races"][k]["candidates"]}
        quem = set(r1t[k]["eleitos"])
        check(f"{k}: eleito = 1 para {len(quem)} e 0 para o resto",
              all(abs(el[sq] - (1.0 if sq in quem else 0.0)) < 1e-12 for sq in el))
        check(f"{k}: bloco apuracao_1t na saída",
              out["races"][k].get("apuracao_1t", {}).get("eleitos") == sorted(quem))
    t1 = {c["sq"]: c["t1_win"] for c in out["races"]["GOV-SP"]["candidates"]}
    check("GOV-SP: t1_win = 1 para o eleito", t1[r1t["GOV-SP"]["eleitos"][0]] == 1.0)

    print("\n3. 2º turno com pesquisa do par: par fixo e prob do par")
    pr = {c["sq"]: c for c in out["races"]["PRES"]["candidates"]}
    check("PRES: t2 = 1 só para os finalistas",
          all(abs(c["t2"] - (1.0 if sq in par_pres else 0.0)) < 1e-12 for sq, c in pr.items()))
    check("PRES: nenhum t1_win", all(c["t1_win"] == 0 for c in pr.values()))
    p2t = [p for p in pd["polls"] if p["race"] == "PRES" and p["cenario"] == "segundo_turno"]
    as_of = em.dt.date.fromisoformat(out["meta"]["as_of"])
    alvo = em.runoff_prob_from_polls(p2t, par_pres, as_of, params)
    check("PRES: P(menor sq) = prob agregada das pesquisas do par (±2,5pp de MC)",
          abs(pr[par_pres[0]]["eleito"] - alvo) < 0.025,
          f"{pr[par_pres[0]]['eleito']:.3f} vs {alvo:.3f}")
    ap = out["races"]["PRES"]["apuracao_1t"]
    check("PRES: saída declara finalistas e pesquisas do par",
          ap["finalistas"] == list(par_pres) and ap["n_polls_par"] >= 1, ap.get("n_polls_par"))

    print("\n4. 2º turno sem pesquisa do par: repasse dos votos válidos")
    cs = {c["sq"]: c for c in out["races"][sem_par]["candidates"]}
    fav, out2 = ordem_sp[0], ordem_sp[1]
    check(f"{sem_par}: t2 = 1 para os dois finalistas e Σeleito = 1",
          cs[fav]["t2"] == 1.0 and cs[out2]["t2"] == 1.0
          and abs(sum(c["eleito"] for c in cs.values()) - 1.0) < 1e-3)
    check(f"{sem_par}: quem liderou o 1º turno é favorito no 2º",
          cs[fav]["eleito"] > cs[out2]["eleito"],
          f"{cs[fav]['eleito']:.3f} x {cs[out2]['eleito']:.3f}")

    print("\n5. arquivo de produção: as 55 corridas, ou reprova")
    check("apuração parcial reprova no modo de produção",
          any("sem apuração" in b for b in em.valida_resultado_1t(r1t, st)))
    nao = [k for k in sorted(base["races"]) if k not in r1t and base["races"][k]["seats"] == 1]
    check("corrida não apurada continua sorteada (não vira 0/1)",
          all(max(c["eleito"] for c in out["races"][k]["candidates"]) < 1.0 or
              max(c["eleito"] for c in base["races"][k]["candidates"]) == 1.0 for k in nao))

    print("\n6. o gate do arquivo morde (erros de curadoria plantados)")
    plantados = {
        "finalista que não é top-2": ("PRES", lambda r: r.update(
            finalistas=[par_pres[0], ordem_sp[2] if len(ordem_sp) > 2 else 1])),
        "decidida com o 1º abaixo de 50%": ("GOV-SP", lambda r: r.update(
            votos_validos={sq: (0.45 if sq == r["eleitos"][0] else v * 0.55 / 0.44)
                           for sq, v in r["votos_validos"].items()})),
        "eleito que não é o mais votado": ("GOV-SP", lambda r: r.update(
            eleitos=[sorted(r["votos_validos"], key=lambda s: r["votos_validos"][s])[0]])),
        "status inválido": ("GOV-SP", lambda r: r.update(status="eleito")),
        "corrida inexistente": ("GOV-XX", None),
        "2º turno no Senado": ("SEN-SP", lambda r: r.update(
            status="segundo_turno", finalistas=r["eleitos"])),
    }
    for nome, (k, mut) in plantados.items():
        x = copy.deepcopy(r1t)
        if mut is None:
            x[k] = copy.deepcopy(r1t["GOV-SP"])
        else:
            mut(x[k])
        check(f"reprova: {nome}", em.valida_resultado_1t(x, st, completo=False) != [])

    if FALHAS:
        print(f"\nREPROVADO: {len(FALHAS)} falha(s): {FALHAS[0]}", file=sys.stderr)
        sys.exit(1)
    print("\nOK: apuração do 1º turno no motor (decidida sem sorteio, par fixo, gate do arquivo).")


if __name__ == "__main__":
    main()
