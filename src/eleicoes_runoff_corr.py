#!/usr/bin/env python3
"""
M8 · Correlação 1º turno -> par de 2º turno (Fase D, Janela 2).

Fecha uma limitação DECLARADA desde a B4, e que está escrita no caveat do
`eleicoes2026_results.json`: "Prob. de 2º turno por par não correlaciona com a
força sorteada no 1º (v1)". Hoje `runoff_prob_from_polls` pré-computa a
probabilidade do par das pesquisas de 2º turno e essa probabilidade é CONSTANTE
entre simulações. Candidato que sorteia um 1º turno forte entra no 2º turno
exatamente igual a quando sorteia um 1º turno fraco, o que é falso.

Este módulo estima o coeficiente que liga as duas margens e escreve
`data/eleicoes/runoff_corr.json`. Quem o aplica é o `simulate()`.

MEDIÇÃO DENTRO DO PAR, e é isto que muda o número
-------------------------------------------------
O plano manda "regredir a margem de 2T na margem de 1T nas pesquisas que têm os
dois cenários no mesmo campo". Feito assim, cru, dá beta 0,12 na presidencial.
Esse número está ERRADO para o uso que o modelo faz dele, e o motivo é o
estimador, não o dado: há só 6 pares distintos de 2º turno na presidencial, e
153 campos no maior deles. Uma regressão simples mistura a variação ENTRE pares
(que é identidade de candidato, não resposta a nada) com a variação DENTRO do
par (que é a pergunta). A simulação sempre mantém o par FIXO e move a margem de
1º turno, ou seja, é uma pergunta dentro do par.

Com efeito fixo por (corrida, par), a inclinação da presidencial vai de 0,12
para 0,33, quase 3x. No governo vai de 0,71 para 0,66, quase nada: lá há 45
pares com 2 campos ou mais, então a regressão crua já estava quase identificada.

POR QUE PRES E GOV NÃO COMPARTILHAM COEFICIENTE
------------------------------------------------
0,33 contra 0,66, com erro-padrão de 0,035 e 0,026. São regimes diferentes, e
faz sentido: na presidencial o 2º turno é outra disputa, com transferência de
voto e polarização que comprimem a margem; nas estaduais a margem de 2º turno
acompanha muito mais de perto a de 1º. Agrupar os dois daria 0,58 e estaria
errado nos dois lados.

REGRA PRÉ-ESPECIFICADA de uso (escrita antes de olhar se o beta "ajuda"):
o coeficiente só é usado se n_obs >= 100 E |beta| > 2 * erro-padrão. Quem não
passa sai com `usar: false` e o modelo cai no comportamento de hoje.

O QUE ESTE COEFICIENTE NÃO É
-----------------------------
Ele é a associação medida ENTRE AS DUAS MARGENS NAS PESQUISAS, e é aplicado à
variação SIMULADA do 1º turno, que tem outra origem (o sorteio do Monte Carlo).
Isso é uma suposição, não um fato medido, e está nas ressalvas do JSON. O que se
ganha é deixar de afirmar correlação ZERO, que é a única coisa que se sabia
falsa.

Usa rede? Não.

Uso:
    python3 src/eleicoes_runoff_corr.py           # escreve o JSON
    python3 src/eleicoes_runoff_corr.py --check   # só imprime
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)

import eleicoes_model as em  # noqa: E402

POLLS = os.path.join(ROOT, "data", "live", "polls.json")
OUT = os.path.join(ROOT, "data", "eleicoes", "runoff_corr.json")

N_MIN = 100          # pré-especificado
T_MIN = 2.0          # pré-especificado: |beta| > 2 erros-padrão


def coleta(polls, params):
    """[(grupo, (corrida,par), m1, m2)] para todo par com 1T e 2T no MESMO campo.

    "Mesmo campo" = (corrida, instituto, campo_fim), que é a mesma chave com que
    o `usable_polls` colapsa cenário duplicado. Usa o 1º turno JÁ FILTRADO pelo
    MATCH_MIN do motor: pesquisa que o modelo não usaria não deve calibrar o
    modelo.
    """
    usable = em.usable_polls(polls, params)
    idx1 = {}
    for corrida, lst in sorted(usable.items()):
        for p in lst:
            idx1[(corrida, p["instituto"], p["campo_fim"])] = p

    linhas = []
    for p in polls:
        if p.get("sintetico") or p["cenario"] != "segundo_turno" or not p["campo_fim"]:
            continue
        q = idx1.get((p["race"], p["instituto"], p["campo_fim"]))
        if q is None:
            continue
        sqs = sorted(n["sq"] for n in p["numeros"] if n["sq"] is not None)
        if len(sqs) != 2:
            continue
        sh2, sh1 = em.poll_shares(p), em.poll_shares(q)
        a, b = sqs
        if a not in sh1 or b not in sh1:
            continue
        d1, d2 = sh1[a] + sh1[b], sh2[a] + sh2[b]
        if d1 <= 0 or d2 <= 0:
            continue
        grupo = "PRES" if p["race"] == "PRES" else "GOV"
        linhas.append((grupo, (p["race"], (a, b)),
                       (sh1[a] - sh1[b]) / d1, (sh2[a] - sh2[b]) / d2))
    return linhas


def regride_dentro(linhas):
    """OLS com efeito fixo por par: cada par entra centrado na própria média.

    Sem intercepto, porque a centragem já o absorve. Devolve None se não houver
    par com 2 campos ou mais, que é o caso em que a pergunta "dentro do par" não
    tem resposta.
    """
    por_par = {}
    for (_g, par, m1, m2) in linhas:
        por_par.setdefault(par, []).append((m1, m2))
    xs, ys, n_pares = [], [], 0
    for par in sorted(por_par):
        v = por_par[par]
        if len(v) < 2:
            continue
        n_pares += 1
        mx = sum(x for x, _ in v) / len(v)
        my = sum(y for _, y in v) / len(v)
        for (x, y) in v:
            xs.append(x - mx)
            ys.append(y - my)
    n = len(xs)
    if n < 3 or n_pares == 0:
        return None
    sxx = sum(x * x for x in xs)
    if sxx <= 0:
        return None
    beta = sum(x * y for x, y in zip(xs, ys)) / sxx
    ss = sum((y - beta * x) ** 2 for x, y in zip(xs, ys))
    st = sum(y * y for y in ys)
    gl = max(n - n_pares - 1, 1)
    s2 = ss / gl
    return {
        "beta": round(beta, 4),
        "ep": round(math.sqrt(s2 / sxx), 4),
        "n_obs": n,
        "n_pares": n_pares,
        "r2_dentro": round(1 - ss / st, 3) if st > 0 else None,
        "sd_residuo": round(math.sqrt(s2), 4),
    }


def regride_entre(linhas):
    """OLS cru, SEM efeito fixo. Existe para o JSON registrar o contraste que
    motivou a escolha do estimador, e para o gate poder exigir que os dois
    números continuem diferentes na presidencial."""
    n = len(linhas)
    if n < 3:
        return None
    mx = sum(r[2] for r in linhas) / n
    my = sum(r[3] for r in linhas) / n
    sxx = sum((r[2] - mx) ** 2 for r in linhas)
    if sxx <= 0:
        return None
    beta = sum((r[2] - mx) * (r[3] - my) for r in linhas) / sxx
    return {"beta": round(beta, 4), "n_obs": n}


def main():
    polls = json.load(open(POLLS, encoding="utf-8"))["polls"]
    params = dict(em.DEFAULTS)
    linhas = coleta(polls, params)

    grupos = {}
    for g in ("PRES", "GOV"):
        sub = [r for r in linhas if r[0] == g]
        dentro = regride_dentro(sub)
        entre = regride_entre(sub)
        if dentro is None:
            grupos[g] = {"usar": False, "motivo": "sem par com 2+ campos"}
            continue
        t = abs(dentro["beta"]) / max(dentro["ep"], 1e-9)
        usar = dentro["n_obs"] >= N_MIN and t > T_MIN
        grupos[g] = {
            "usar": usar,
            "motivo": ("passa a regra pré-especificada" if usar else
                       f"n={dentro['n_obs']} (min {N_MIN}) ou t={t:.1f} (min {T_MIN})"),
            "t": round(t, 1),
            "dentro_do_par": dentro,
            "entre_pares_cru": entre,
        }

    doc = {
        "schema_version": 1,
        "gerado_por": "src/eleicoes_runoff_corr.py",
        "consumidor": "src/eleicoes_model.py :: simulate (param RUNOFF_CORR)",
        "as_of": max((p["campo_fim"] for p in polls
                      if p["campo_fim"] and not p.get("sintetico")), default=None),
        "estimador": (
            "OLS com efeito fixo por (corrida, par): cada par entra centrado na própria "
            "média, sem intercepto. A simulação mantém o par FIXO e move a margem de 1º "
            "turno, então a pergunta é DENTRO do par. A regressão crua mistura isso com a "
            "variação entre pares, que é identidade de candidato e não resposta a nada."),
        "regra_pre_especificada": (
            f"usa o coeficiente só se n_obs >= {N_MIN} E |beta| > {T_MIN} erros-padrão. "
            "Escrita antes de olhar se o beta 'ajuda'."),
        "pres_e_gov_separados": (
            "Não compartilham coeficiente porque não são o mesmo regime: na presidencial o "
            "2º turno é outra disputa (transferência de voto e polarização comprimem a "
            "margem) e nas estaduais a margem de 2º acompanha de perto a de 1º."),
        "ressalvas": [
            "O coeficiente é a associação entre as duas margens NAS PESQUISAS, e é aplicado "
            "à variação SIMULADA do 1º turno, que tem outra origem (o sorteio do Monte "
            "Carlo). Isso é SUPOSIÇÃO, não medição. O que se ganha é deixar de afirmar "
            "correlação ZERO, que é a única coisa que se sabia falsa.",
            "A presidencial tem só 6 pares distintos: o efeito fixo identifica o beta, mas "
            "o universo de pares é pequeno e o beta pode mudar quando o campo mudar.",
            "Pares de 2º turno sob 'Hipóteses com Lula' saem com par=None no ingest (dívida "
            "pré-existente declarada em 18/09), então não entram aqui.",
            "Só entra pesquisa de 1º turno que o motor USARIA (passa o MATCH_MIN de 0,90): "
            "pesquisa que o modelo descarta não deve calibrar o modelo.",
        ],
        "grupos": grupos,
    }
    if "--check" not in sys.argv:
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
            f.write("\n")

    print(f"correlação 1T->2T · {len(linhas)} pares casados no mesmo campo")
    for g in ("PRES", "GOV"):
        d = grupos[g]
        if not d.get("dentro_do_par"):
            print(f"  {g:5s} {d['motivo']}")
            continue
        dd, de = d["dentro_do_par"], d["entre_pares_cru"]
        print(f"  {g:5s} beta_dentro={dd['beta']:+.4f} (ep {dd['ep']:.4f}, t={d['t']}) "
              f"n={dd['n_obs']} pares={dd['n_pares']} R2={dd['r2_dentro']} "
              f"| cru={de['beta']:+.4f} | usar={d['usar']}")
    if "--check" not in sys.argv:
        print(f"\nOK: {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
