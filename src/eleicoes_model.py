#!/usr/bin/env python3
"""
Motor probabilístico · Ficha do Jogo · Eleições 2026 (etapa B4).

Agregador de pesquisas + Monte Carlo por corrida. Só stdlib, determinístico
(seed 42, iterações ordenadas). Lê data/eleicoes2026_structure.json e
data/live/polls.json; escreve data/eleicoes2026_results.json.

Método (v1, honesto e declarado):
- Pesquisa "realizada" = estimulada com >=90% do share casado em SQ; cenários
  duplicados do mesmo (instituto, campo_fim) colapsam no mais completo.
- Share por candidato = pct / Σpct dos casados (indecisos realocados
  proporcionalmente: LIMITAÇÃO declarada; Senado fica invariante à base).
- Peso = recência (meia-vida HALFLIFE dias) × sqrt(amostra).
- House effect básico: desvio médio do instituto vs consenso da corrida,
  encolhido pela metade, subtraído quando o instituto tem >=2 pesquisas e a
  corrida >=3 institutos.
- Incerteza por candidato: dispersão entre pesquisas + termo temporal
  (TIMEPP·sqrt(dias/35)) + termo de indecisos; piso FLOORPP.
- Correlação nacional↔UF simples: choque comum por bloco partidário
  (esq/centro/dir) com sd SIGMA_NAT, compartilhado entre corridas no mesmo sim.
- 2º turno: pares com pesquisa de 2T usam prob agregada delas (Φ da margem);
  par sem pesquisa cai no repasse s1/(s1+s2) com ruído RUNOFF_PP. LIMITAÇÃO:
  prob de 2T por par é constante entre sims (não correlaciona com a força
  sorteada no 1T).
- Corrida sem pesquisa fresca: prior DECLARADO (uniforme entre concorrendo,
  incerteza alta) + data_quality na saída; nunca 50/50 silencioso.

Hiperparâmetros por env: NSIMS HALFLIFE TIMEPP FLOORPP SIGMA_NAT RUNOFF_PP.
"""
import datetime as dt
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
STRUCT = os.path.join(ROOT, "data", "eleicoes2026_structure.json")
POLLS = os.path.join(ROOT, "data", "live", "polls.json")
OUT = os.path.join(ROOT, "data", "eleicoes2026_results.json")

T1 = dt.date(2026, 10, 4)
SQRT2 = math.sqrt(2.0)

DEFAULTS = dict(
    NSIMS=20000,      # sims por rodada (todas as corridas juntas por sim)
    HALFLIFE=21.0,    # meia-vida da recência, em dias
    TIMEPP=2.0,       # incerteza temporal: TIMEPP*sqrt(dias_para_eleicao/35) em pp
    FLOORPP=3.0,      # piso do desvio por candidato, em pp
    SIGMA_NAT=0.02,   # sd do choque nacional por bloco (fração do share)
    RUNOFF_PP=8.0,    # sd do repasse em 2º turno SEM pesquisa de par, em pp
    # M8: 1 liga a correlação entre a margem SORTEADA no 1º turno e a margem de
    # 2º turno do par (coeficiente em data/eleicoes/runoff_corr.json). NASCE
    # DESLIGADO: ligar muda o número PUBLICADO, e a regra da casa é que nada da
    # edição Eleições muda no ar sem validação local. Enquanto for 0, o caveat
    # "prob de 2º turno não correlaciona com a força sorteada no 1º" continua
    # verdadeiro e continua impresso na saída.
    RUNOFF_CORR=0,
    MATCH_MIN=0.90,   # share casado mínimo p/ pesquisa "realizada"
    # Mínimo de candidatos CASADOS COM NÚMERO para a pesquisa contar. Achado de
    # 24/09/2026: uma linha da CTAS (SEN-SE, 03/09) trazia UM único número
    # (14,2%) e travessão nas outras colunas. Passava no MATCH_MIN com
    # 14,2/14,2 = 1,0, e como o share é normalizado entre os casados, aquele
    # candidato recebia 100% naquela pesquisa, com 6 a 8% do peso da corrida.
    # Foi a origem do sd de 19,6pp que ficou NO AR de 14 a 24/09, e do alarme
    # que segurou o cron por 3 dias quando um editor moveu o número de coluna.
    # Uma pesquisa de corrida compara candidatos; com um só, a normalização é
    # tautologia. 2 é o mínimo que ainda compara alguma coisa, e é o que
    # menos mexe: só 1 das 1.454 pesquisas usáveis tinha 1 casado.
    MIN_CASADOS=2,
    FRESH_D=35, STALE_D=120,
    HOUSE=1,          # 1 = aplica house effect básico; 0 = desliga (variante do harness)
    # C3: de qual FONTE este modelo pode ler pesquisa.
    #   "real"      = só pesquisa de instituto (é o do modelo OFICIAL do site)
    #   "sintetico" = só pesquisa sintética (competidor synths_solo)
    #   "ambos"     = real + sintética juntas (competidor synths_mix)
    # O default é "real" de propósito: um modelo novo que esqueça de declarar a
    # fonte nasce limpo, nunca contaminado.
    POLL_SOURCE="real",
)
FONTES_VALIDAS = ("real", "sintetico", "ambos")

# bloco partidário (crude, declarado; só alimenta a correlação nacional)
BLOCO = {
    "PT": "esq", "PSOL": "esq", "PSB": "esq", "PDT": "esq", "PCdoB": "esq",
    "REDE": "esq", "PV": "esq", "UP": "esq", "PCB": "esq", "PSTU": "esq",
    "PCO": "esq",
    "PL": "dir", "NOVO": "dir", "PP": "dir", "REPUBLICANOS": "dir",
    "UNIÃO": "dir", "PRTB": "dir", "DC": "dir", "DEMOCRATA": "dir",
    "MISSÃO": "dir", "AGIR": "dir",
    # resto (PSD, MDB, PSDB, PODE, CIDADANIA, SOLIDARIEDADE, AVANTE, PRD,
    # MOBILIZA, …) = centro
}


def param(name, cast=float):
    v = os.environ.get(name)
    return cast(v) if v is not None else DEFAULTS[name]


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def usable_polls(polls, params):
    """Filtra estimuladas realizadas e colapsa cenários duplicados.

    Aqui mora a separação real/sintético (C3). É FAIL-CLOSED: pesquisa sem a flag
    `sintetico` levanta erro em vez de ser tratada como real. Assumir seria
    exatamente a porta pela qual um synth entraria no forecast oficial num
    refactor futuro, e a decisão do Bera (29/08) é que isso nunca aconteça.
    """
    fonte = params.get("POLL_SOURCE", "real")
    if fonte not in FONTES_VALIDAS:
        raise ValueError(f"POLL_SOURCE inválido: {fonte!r} (use {FONTES_VALIDAS})")
    by_race = {}
    for p in polls:
        if "sintetico" not in p:
            raise ValueError(
                f"pesquisa {p.get('id')!r} sem a flag obrigatória 'sintetico'. "
                f"polls.json precisa estar no schema v2; rode src/ingest_polls.py.")
        if fonte == "real" and p["sintetico"]:
            continue
        if fonte == "sintetico" and not p["sintetico"]:
            continue
        if p["cenario"] != "estimulada" or not p["campo_fim"]:
            continue
        tot = sum(n["pct"] for n in p["numeros"])
        got = sum(n["pct"] for n in p["numeros"] if n["sq"] is not None)
        if tot <= 0 or got / tot < params["MATCH_MIN"]:
            continue
        # Casado COM número: um candidato casado em 0% não compara nada, e
        # "A=14,2 / B=0" normalizado dá A=100% do mesmo jeito. Esta é a ÚNICA
        # camada que julga isso (decisão de 25/09): um guarda igual no ingest
        # quarentenava cenário "candidato × Outros", legítimo, e derrubou o
        # cron. O ingest preserva o registro; o corte é aqui.
        casados = sum(1 for n in p["numeros"] if n["sq"] is not None and n["pct"] > 0)
        if casados < int(params.get("MIN_CASADOS", DEFAULTS["MIN_CASADOS"])):
            continue
        key = (p["race"], p["instituto"], p["campo_fim"])
        cur = by_race.setdefault(p["race"], {})
        prev = cur.get(key)
        score = (sum(1 for n in p["numeros"] if n["sq"]), got)
        if prev is None or score > prev[0]:
            cur[key] = (score, p)
    return {race: sorted((v[1] for v in d.values()),
                         key=lambda p: (p["campo_fim"], p["instituto"], p["id"]))
            for race, d in sorted(by_race.items())}


def poll_shares(p):
    """{sq: share} normalizado entre os casados (invariante à base do Senado)."""
    tot = sum(n["pct"] for n in p["numeros"] if n["sq"] is not None)
    if tot <= 0:
        return {}
    out = {}
    for n in p["numeros"]:
        if n["sq"] is not None:
            out[n["sq"]] = out.get(n["sq"], 0.0) + n["pct"] / tot
    return out


def weight(p, as_of, params):
    age = (as_of - dt.date.fromisoformat(p["campo_fim"])).days
    w_rec = 0.5 ** (max(age, 0) / params["HALFLIFE"])
    n = p["amostra"] or 800
    return w_rec * math.sqrt(min(n, 3000) / 1000.0)


def aggregate_race(race_key, race, plist, as_of, params):
    """Média ponderada + house effect básico + dispersão por candidato."""
    cands = [c for c in race["candidates"] if c["concorrendo"]]
    sqs = [c["sq"] for c in cands]
    if not plist:
        k = len(sqs)
        return {"mode": "prior", "mu": {sq: 1.0 / k for sq in sqs}, "sd": {sq: 0.30 for sq in sqs},
                "undecided": 0.5, "n_polls": 0, "freshest": None, "institutes": 0}
    rows = []
    for p in plist:
        sh = poll_shares(p)
        w = weight(p, as_of, params)
        indef = p.get("indefinidos_pct") or {}
        und = ((indef.get("indecisos") or 0.0) + (indef.get("outros") or 0.0)) / 100.0
        rows.append({"inst": p["instituto"], "w": w, "sh": sh, "und": min(und, 0.6),
                     "fim": p["campo_fim"]})
    # consenso preliminar
    mu0 = {}
    wtot = sum(r["w"] for r in rows) or 1.0
    for sq in sqs:
        mu0[sq] = sum(r["w"] * r["sh"].get(sq, 0.0) for r in rows) / wtot
    # house effect básico (shrink 0.5)
    insts = sorted({r["inst"] for r in rows})
    he = {}
    if len(insts) >= 3 and params.get("HOUSE", 1):
        for inst in insts:
            mine = [r for r in rows if r["inst"] == inst]
            if len(mine) >= 2:
                he[inst] = {sq: 0.5 * (sum(r["sh"].get(sq, 0.0) for r in mine) / len(mine) - mu0[sq])
                            for sq in sqs}
    mu = {}
    for sq in sqs:
        num = sum(r["w"] * (r["sh"].get(sq, 0.0) - he.get(r["inst"], {}).get(sq, 0.0)) for r in rows)
        mu[sq] = max(num / wtot, 0.0)
    tot = sum(mu.values())
    if tot <= 1e-9:  # pesquisas só casaram com quem saiu da disputa: prior declarado
        k = len(sqs)
        return {"mode": "prior", "mu": {sq: 1.0 / k for sq in sqs}, "sd": {sq: 0.30 for sq in sqs},
                "undecided": 0.5, "n_polls": 0, "freshest": None, "institutes": 0}
    mu = {sq: v / tot for sq, v in mu.items()}
    # dispersão ponderada entre pesquisas (em share)
    sd = {}
    days = max((T1 - as_of).days, 0)
    t_pp = params["TIMEPP"] * math.sqrt(days / 35.0)
    und_mean = sum(r["w"] * r["und"] for r in rows) / wtot
    for sq in sqs:
        var = sum(r["w"] * (r["sh"].get(sq, 0.0) - mu[sq]) ** 2 for r in rows) / wtot
        disp_pp = 100.0 * math.sqrt(var)
        extra_pp = und_mean * 100.0 * 0.25 * mu[sq]  # indecisos: incerteza proporcional
        total_pp = math.sqrt(disp_pp ** 2 + t_pp ** 2 + extra_pp ** 2)
        sd[sq] = max(total_pp, params["FLOORPP"]) / 100.0
    freshest = max(r["fim"] for r in rows)
    age = (as_of - dt.date.fromisoformat(freshest)).days
    mode = "polls" if age <= params["STALE_D"] else "prior_velho"
    return {"mode": mode, "mu": mu, "sd": sd, "undecided": und_mean,
            "n_polls": len(rows), "freshest": freshest, "institutes": len(insts)}


def runoff_prob_from_polls(polls2t, pair, as_of, params, detalhe=False):
    """P(vitória do menor SQ do par) agregando pesquisas de 2º turno do par.

    `detalhe=True` devolve (prob, margem, sigma) em vez de só a prob. O M8 precisa
    dos COMPONENTES, não do resultado: para correlacionar com o 1º turno sorteado
    ele desloca a MARGEM dentro de cada simulação e refaz o Φ. Recomputar a prob
    a partir da prob seria impossível sem inverter o Φ, e inverter só para
    reaplicar é mais caro e menos claro do que devolver o que já foi calculado.
    """
    rows = []
    for p in polls2t:
        sqs = sorted(n["sq"] for n in p["numeros"] if n["sq"] is not None)
        if sqs != sorted(pair) or not p["campo_fim"]:
            continue
        sh = poll_shares(p)
        if not sh:
            continue
        rows.append((weight(p, as_of, params), sh))
    if not rows:
        return (None, None, None) if detalhe else None
    a, b = sorted(pair)
    wtot = sum(w for w, _ in rows)
    ma = sum(w * sh.get(a, 0.0) for w, sh in rows) / wtot
    mb = sum(w * sh.get(b, 0.0) for w, sh in rows) / wtot
    margin = (ma - mb) / max(ma + mb, 1e-9)
    days = max((T1 - as_of).days, 0)
    sigma = max(0.05, 0.03 * math.sqrt(days / 35.0) + 0.03)
    prob = 0.5 * (1.0 + math.erf(margin / (sigma * math.sqrt(2))))
    return (prob, margin, sigma) if detalhe else prob


def runoff_prob_corrigida(margem, sigma, m1_ref, beta, m1):
    """P(vitória do menor SQ do par) deslocada pela margem de 1º turno SORTEADA.

    É o M8 inteiro em uma linha. Vive FORA do laço de propósito, ainda que custe
    uma chamada por simulação: escrita inline, a fórmula ficava fora do alcance
    do gate, e um sinal trocado aqui passaria despercebido. Rodei exatamente esse
    erro plantado (`margem - beta*(...)`) no código de produção e o gate deixou
    passar, porque ele só conseguia testar uma cópia da fórmula escrita no
    próprio teste. Mesmo furo que o M5 tinha.

    `m1` e `m1_ref` são margens do par no 1º turno, em (share_a - share_b) sobre
    a soma dos dois: `m1` é a SORTEADA naquela simulação e `m1_ref` a implícita
    no agregado. A diferença entre elas é o quanto aquele cenário foi melhor ou
    pior que o esperado para o candidato de menor SQ.
    """
    return 0.5 * (1.0 + math.erf((margem + beta * (m1 - m1_ref)) / (sigma * SQRT2)))


def carrega_runoff_corr():
    """{grupo: beta} do M8, ou {} se o arquivo não existe ou a regra reprovou.

    Falha ABERTA: sem o arquivo, beta some e o 2º turno volta a ser o de hoje
    (probabilidade constante entre simulações). Um arquivo de calibração
    ausente não pode derrubar o motor que publica.
    """
    caminho = os.path.join(ROOT, "data", "eleicoes", "runoff_corr.json")
    try:
        with open(caminho, encoding="utf-8") as f:
            doc = json.load(f)
    except (OSError, ValueError):
        return {}
    out = {}
    for g, d in sorted(doc.get("grupos", {}).items()):
        if d.get("usar") and d.get("dentro_do_par"):
            out[g] = float(d["dentro_do_par"]["beta"])
    return out


def simulate(structure, polls_doc, params, verbose=True, aggregator=None):
    """`aggregator`: função com a assinatura de `aggregate_race`. None = a oficial.

    A costura existe para o harness poder medir um motor ESTRUTURALMENTE
    diferente (M1, `eleicoes_model_v2.py`: nível latente por Kalman no lugar da
    média ponderada por recência) sem duplicar o Monte Carlo, o 2º turno, a regra
    do Senado, a correlação nacional nem os invariantes. Duplicar isso faria o
    competidor divergir do oficial por motivo errado, e o leaderboard mediria a
    duplicação em vez da modelagem.
    """
    polls = polls_doc["polls"]
    races = structure["races"]
    # as_of vem SÓ das pesquisas que este modelo pode ler. Calcular sobre todas
    # faria o modelo OFICIAL herdar a data de uma pesquisa sintética que ele nem
    # enxerga: o site diria "pesquisas até 31/08" com a última real em 29/08.
    # Vazamento de metadado é vazamento igual (achado ao rodar o C3).
    _fonte = params.get("POLL_SOURCE", "real")
    _visiveis = [p for p in polls
                 if not (_fonte == "real" and p.get("sintetico"))
                 and not (_fonte == "sintetico" and not p.get("sintetico"))]
    as_of_str = max((p["campo_fim"] for p in _visiveis if p["campo_fim"]),
                    default="2026-08-29")
    as_of = dt.date.fromisoformat(as_of_str)
    by_race = usable_polls(polls, params)
    polls2t = [p for p in polls if p["cenario"] == "segundo_turno"]

    agg_fn = aggregator or aggregate_race
    aggs = {}
    for key in sorted(races):
        aggs[key] = agg_fn(key, races[key], by_race.get(key, []), as_of, params)

    # pares plausíveis de 2º turno com prob pré-computada de pesquisas de par
    # M8: `pair_ctx` guarda os COMPONENTES (margem de 2T, sigma, margem de 1T
    # implícita no agregado). Com RUNOFF_CORR=1 a margem de 2T é deslocada, em
    # cada simulação, pelo quanto a margem de 1T SORTEADA se afastou da margem
    # de 1T do agregado. Com RUNOFF_CORR=0 nada disso é lido e o comportamento
    # é o de sempre.
    usa_corr = int(params.get("RUNOFF_CORR", 0)) == 1
    betas = carrega_runoff_corr() if usa_corr else {}
    pair_prob, pair_ctx = {}, {}
    for key in sorted(races):
        if not races[key]["two_round"]:
            continue
        mu = aggs[key]["mu"]
        top = sorted(mu, key=lambda sq: -mu[sq])[:4]
        p2t = [p for p in polls2t if p["race"] == key]
        for i in range(len(top)):
            for j in range(i + 1, len(top)):
                pair = (min(top[i], top[j]), max(top[i], top[j]))
                pr, margem, sigma = runoff_prob_from_polls(
                    p2t, pair, as_of, params, detalhe=True)
                if pr is None:
                    continue
                pair_prob[(key, pair)] = pr
                if usa_corr:
                    beta = betas.get("PRES" if key == "PRES" else "GOV", 0.0)
                    den = mu.get(pair[0], 0.0) + mu.get(pair[1], 0.0)
                    m1_ref = ((mu.get(pair[0], 0.0) - mu.get(pair[1], 0.0)) / den
                              if den > 0 else 0.0)
                    pair_ctx[(key, pair)] = (margem, sigma, m1_ref, beta)

    nsims = int(params["NSIMS"])
    rng = random.Random(42)
    bloco_de = {}
    for key in sorted(races):
        for c in races[key]["candidates"]:
            bloco_de[c["sq"]] = BLOCO.get(c["partido"], "centro")

    stats = {key: {"eleito": {}, "t2": {}, "t1_win": {}, "pares": {}} for key in races}
    for _ in range(nsims):
        z = {b: rng.gauss(0.0, params["SIGMA_NAT"]) for b in ("esq", "centro", "dir")}
        for key in sorted(races):
            race = races[key]
            agg = aggs[key]
            mu, sd = agg["mu"], agg["sd"]
            draw = {}
            for sq in mu:
                base = mu[sq]
                eps = rng.gauss(0.0, sd[sq]) + z[bloco_de[sq]] * base
                draw[sq] = max(base + eps, 0.0)
            tot = sum(draw.values()) or 1.0
            for sq in draw:
                draw[sq] /= tot
            order = sorted(draw, key=lambda s: (-draw[s], s))
            st = stats[key]
            if race["seats"] == 2:  # Senado: top-2, sem 2º turno
                for sq in order[:2]:
                    st["eleito"][sq] = st["eleito"].get(sq, 0) + 1
                continue
            if not race["two_round"]:
                st["eleito"][order[0]] = st["eleito"].get(order[0], 0) + 1
                continue
            if draw[order[0]] > 0.5 or len(order) < 2:
                st["eleito"][order[0]] = st["eleito"].get(order[0], 0) + 1
                st["t1_win"][order[0]] = st["t1_win"].get(order[0], 0) + 1
                st["t2"][order[0]] = st["t2"].get(order[0], 0) + 1
                continue
            a, b = order[0], order[1]
            for sq in (a, b):
                st["t2"][sq] = st["t2"].get(sq, 0) + 1
            pair = (min(a, b), max(a, b))
            st["pares"][pair] = st["pares"].get(pair, 0) + 1
            pr = pair_prob.get((key, pair))  # P(vitória do menor SQ do par)
            if pr is None:  # repasse simples com ruído
                sa = draw[a] / max(draw[a] + draw[b], 1e-9)
                sa += rng.gauss(0.0, params["RUNOFF_PP"] / 100.0)
                winner = a if sa >= 0.5 else b
            else:
                ctx = pair_ctx.get((key, pair))
                if ctx is not None:
                    # M8: quem sorteia um 1º turno mais forte entra no 2º mais
                    # forte, na proporção medida em pesquisa que traz os DOIS
                    # cenários no mesmo campo. `beta` é por regime (PRES ou GOV)
                    # porque 0,33 e 0,66 não são o mesmo número.
                    margem, sigma, m1_ref, beta = ctx
                    den = draw[pair[0]] + draw[pair[1]]
                    m1 = (draw[pair[0]] - draw[pair[1]]) / den if den > 1e-9 else 0.0
                    pr = runoff_prob_corrigida(margem, sigma, m1_ref, beta, m1)
                winner = pair[0] if rng.random() < pr else pair[1]
            st["eleito"][winner] = st["eleito"].get(winner, 0) + 1

    # monta saída
    out = {"meta": {
        "edition": "eleicoes2026", "as_of": as_of_str, "nsims": nsims,
        "params": {k: params[k] for k in sorted(DEFAULTS)},
        "dates": structure["meta"]["dates"],
        "generated_by": "src/eleicoes_model.py" if aggregator is None else
                        f"src/eleicoes_model.py + agregador {getattr(aggregator, '__module__', '?')}",
        "poll_source": params.get("POLL_SOURCE", "real"),
        "usa_sintetico": params.get("POLL_SOURCE", "real") in ("sintetico", "ambos"),
        "caveats": [
            "Agregador de pesquisas públicas; indecisos realocados proporcionalmente.",
            ("Prob. de 2º turno por par correlaciona com a força sorteada no 1º "
             "(M8: beta medido dentro do par, PRES e GOV separados)."
             if int(params.get("RUNOFF_CORR", 0)) == 1 else
             "Prob. de 2º turno por par não correlaciona com a força sorteada no 1º (v1)."),
            "Corrida com data_quality != 'ok' carrega prior declarado, leia a banda.",
            "Pesquisa sintética NUNCA entra aqui; competidores só no leaderboard (B5).",
        ],
    }, "races": {}}
    for key in sorted(races):
        race, agg, st = races[key], aggs[key], stats[key]
        days_fresh = None
        if agg["freshest"]:
            days_fresh = (as_of - dt.date.fromisoformat(agg["freshest"])).days
        if agg["n_polls"] == 0:
            quality = "sem_pesquisa"
        elif days_fresh > params["STALE_D"]:
            quality = "pesquisa_velha"
        elif days_fresh > params["FRESH_D"]:
            quality = "defasada"
        else:
            quality = "ok"
        cands = []
        for c in sorted(race["candidates"], key=lambda c: (-agg["mu"].get(c["sq"], 0.0), c["sq"])):
            sq = c["sq"]
            if sq not in agg["mu"]:
                continue
            item = {
                "sq": sq, "urna": c["urna"], "partido": c["partido"],
                "share": round(agg["mu"][sq], 4),
                "sd": round(agg["sd"][sq], 4),
                "eleito": round(st["eleito"].get(sq, 0) / nsims, 4),
            }
            if race["two_round"]:
                item["t2"] = round(st["t2"].get(sq, 0) / nsims, 4)
                item["t1_win"] = round(st["t1_win"].get(sq, 0) / nsims, 4)
            cands.append(item)
        pares = {f"{a}x{b}": round(n / nsims, 4)
                 for (a, b), n in sorted(st["pares"].items(), key=lambda kv: -kv[1])[:6]}
        out["races"][key] = {
            "cargo": race["cargo"], "uf": race["uf"], "seats": race["seats"],
            "two_round": race["two_round"], "data_quality": quality,
            "n_polls": agg["n_polls"], "institutes": agg["institutes"],
            "freshest": agg["freshest"], "undecided": round(agg["undecided"], 3),
            "candidates": cands, "pares_2t": pares or None,
        }
    if verbose:
        n_ok = sum(1 for r in out["races"].values() if r["data_quality"] == "ok")
        print(f"as_of={as_of_str} sims={nsims} corridas ok={n_ok}/55")
    return out


def check_invariants(out):
    """Gate: somas e monotonicidade. Devolve lista de violações."""
    bad = []
    for key, r in sorted(out["races"].items()):
        tot = sum(c["eleito"] for c in r["candidates"])
        want = r["seats"] * 1.0
        if abs(tot - want) > 0.02:
            bad.append(f"{key}: Σeleito={tot:.3f} != {want}")
        if r["two_round"]:
            # com vitória no 1º turno o "par" colapsa no vencedor: Σt2 esperado = 2 - Σt1_win
            t2tot = sum(c["t2"] for c in r["candidates"])
            t1tot = sum(c["t1_win"] for c in r["candidates"])
            if abs(t2tot - (2.0 - t1tot)) > 0.03:
                bad.append(f"{key}: Σt2={t2tot:.3f} != 2 - Σt1_win={2 - t1tot:.3f}")
            for c in r["candidates"]:
                if c["eleito"] > c["t2"] + 1e-9:
                    bad.append(f"{key}: {c['urna']}: eleito {c['eleito']} > t2 {c['t2']}")
    return bad


def main():
    params = {k: param(k, float if not isinstance(DEFAULTS[k], int) else int)
              for k in DEFAULTS}
    structure = load(STRUCT)
    polls_doc = load(POLLS)
    out = simulate(structure, polls_doc, params)
    bad = check_invariants(out)
    if bad:
        for b in bad:
            print("INVARIANTE VIOLADA:", b)
        sys.exit(1)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"OK -> {os.path.relpath(OUT, ROOT)} (invariantes verdes)")


if __name__ == "__main__":
    main()
