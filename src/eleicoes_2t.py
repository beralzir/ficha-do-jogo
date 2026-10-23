#!/usr/bin/env python3
"""
Linha do tempo do 2º turno presidencial: nível diário do par + eventos com hora.

A página presidencial, no modo apuração, mostrava só o 1º turno. Este script mede
o que aconteceu DEPOIS dele: a média diária das pesquisas do par finalista, os dias
em que o nível mudou e, para cada notícia registrada no `eventos.json`, a comparação
antes × depois pareada por instituto.

GRANULARIDADE (decisão do Bera, 23/10/2026): notícia por HORA, efeito por DIA.
Pesquisa tem campo de 2 a 5 dias e saem 2 ou 3 por dia; a menor resolução honesta
do efeito é o dia do fim do campo. A hora do evento serve para uma coisa só, decidir
se uma pesquisa foi a campo DEPOIS do fato (campo_ini posterior ao dia do evento).

MÉTODO, em três peças simples e declaradas no JSON:
1. Share bidirecional: s = A / (A + B), indecisos fora. Pesquisas com 20% de
   indecisos e com 0% ficam na mesma escala.
2. Efeito de casa: desvio médio do instituto contra o nível (sem correção) do dia
   da pesquisa, encolhido por n/(n+K). Instituto com 1 pesquisa quase não é corrigido.
3. Nível diário: média com kernel triangular (meia-largura BW dias) das shares
   corrigidas, peso pela amostra com teto (uma amostra de 15 mil não vale 7 de 2 mil).
   Banda = ±1,96 erro-padrão da média ponderada.

INFLEXÃO (candidata): para cada dia d, compara as pesquisas corrigidas com fim de
campo em [d-J, d) e em [d, d+J). Marca quando |z| >= Z_MIN, as duas janelas têm
MIN_N pesquisas de 2+ institutos e o sinal se repete em 2+ institutos que
aparecem dos dois lados (a mesma corroboração do M2: movimento real aparece em mais
de um instituto). Dias vizinhos marcados viram um só (o de maior |z|).

EVENTO: "antes" = última pesquisa de cada instituto com fim de campo até a véspera
do evento (até 7 dias); "depois" = primeira do mesmo instituto com campo iniciado
DEPOIS do dia do evento. Pareado por instituto, então o efeito de casa se cancela.
Todo evento registrado depois do fato é EXPLORATÓRIO (regra do eleicoes_eventos.py)
e eventos próximos se sobrepõem: o delta não é efeito causal de um evento só.

MODELO (23/10/2026): a chance de vitória do modelo PRINCIPAL do site, dia a dia.
O site não publicou esses números de 05 a 21/10 (o cron estava parado), então a
série é RECONSTRUÍDA: em cada dia d, `eleicoes_model.runoff_prob_from_polls` (a
mesma função que o motor usa no modo apuração) com as pesquisas de 2º turno do par
com fim de campo até d, os parâmetros da última rodada (meta.params do results) e
as_of = d. O motor sorteia em cima dessa probabilidade, então o último ponto bate
com o número do topo da página a menos do ruído do Monte Carlo.

HISTÓRICO PUBLICADO (23/10/2026): antes do 1º turno o site publicou P(eleito) da
presidencial quase todo dia; o git guarda cada versão do results.json. `--congelar`
lê esse histórico (última versão de cada as_of até a véspera do 1º turno) e grava
`historico_pres.json`, versionado, com o commit de cada ponto. O pipeline só LÊ o
arquivo: o 1º turno acabou e esse histórico não muda mais.

Uso:  python3 src/eleicoes_2t.py
      python3 src/eleicoes_2t.py --congelar   # uma vez: congela o histórico publicado
"""
import datetime as dt
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)

POLLS = os.path.join(ROOT, "data", "live", "polls.json")
RESULTS = os.path.join(ROOT, "data", "eleicoes2026_results.json")
EVENTOS = os.path.join(ROOT, "data", "eleicoes", "eventos.json")
OUT = os.path.join(ROOT, "data", "eleicoes", "segundo_turno.json")
HIST = os.path.join(ROOT, "data", "eleicoes", "historico_pres.json")

T1 = dt.date(2026, 10, 4)
T2 = dt.date(2026, 10, 25)
BW = 4          # meia-largura do kernel do nível, em dias
K = 2.0         # encolhimento do efeito de casa
N_CAP = 3000    # teto da amostra no peso
J = 4           # janela de cada lado na inflexão, em dias
Z_MIN = 2.0
MIN_N = 3
ANTES_MAX = 7   # quantos dias para trás o "antes" de um evento pode buscar
DEPOIS_MAX = 7  # e para a frente o "depois"

# Mesmo instituto com a ordem do contratante trocada na Wikipédia.
ALIAS_INST = {"Nexus/BTG": "BTG/Nexus"}


def d(s):
    return dt.date.fromisoformat(s)


def inst_de(p):
    i = p["instituto"].strip()
    return ALIAS_INST.get(i, i)


def pesquisas_do_par(polls, par, desde=T1):
    """Pesquisas de 2º turno do par com campo terminado depois do 1º turno."""
    a, b = par
    out = []
    for p in polls:
        if p.get("race") != "PRES" or not p.get("campo_fim"):
            continue
        num = {n["sq"]: n["pct"] for n in p["numeros"] if n.get("sq") is not None}
        if sorted(num) != sorted(par) or d(p["campo_fim"]) <= desde:
            continue
        va, vb = num[a], num[b]
        if va is None or vb is None or va + vb <= 0:
            continue
        ind = (p.get("indefinidos_pct") or {}).get("indecisos")
        out.append({"id": p["id"], "inst": inst_de(p),
                    "ini": p["campo_ini"] or p["campo_fim"], "fim": p["campo_fim"],
                    "n": p.get("amostra"), "mg": p.get("margem_pp"),
                    "a": va, "b": vb, "ind": ind,
                    "s": va / (va + vb)})
    # duplicata da mesma pesquisa (mesmo instituto e mesmo campo) conta uma vez
    vistos, uniq = set(), []
    for r in sorted(out, key=lambda r: (r["fim"], r["inst"], r["ini"], r["id"])):
        k = (r["inst"], r["ini"], r["fim"])
        if k in vistos:
            continue
        vistos.add(k)
        uniq.append(r)
    return uniq


def peso(r):
    return math.sqrt(min(r["n"] or 1000, N_CAP))


def efeitos_de_casa(rows, ini, fim):
    """Desvio do instituto contra o NÍVEL DO DIA da pesquisa, encolhido.

    Contra a média do período, um instituto que só foi a campo no começo herdaria
    a tendência como viés de casa. Por isso o nível sem correção é medido primeiro
    e o desvio é tomado dia a dia.
    """
    for r in rows:
        r["s_adj"] = r["s"]
    nivel = {x["data"]: x["s"] for x in nivel_diario(rows, ini, fim)}
    por = {}
    for r in rows:
        por.setdefault(r["inst"], []).append(r["s"] - nivel[r["fim"]])
    return {i: (sum(v) / len(v)) * len(v) / (len(v) + K) for i, v in sorted(por.items())}


def nivel_diario(rows, ini, fim):
    serie = []
    dia = ini
    while dia <= fim:
        ws, xs = [], []
        for r in rows:
            k = 1 - abs((d(r["fim"]) - dia).days) / (BW + 1)
            if k > 0:
                ws.append(k * peso(r))
                xs.append(r["s_adj"])
        if ws:
            W = sum(ws)
            m = sum(w * x for w, x in zip(ws, xs)) / W
            # erro-padrão da média ponderada (n efetivo de Kish)
            var = sum(w * (x - m) ** 2 for w, x in zip(ws, xs)) / W
            n_eff = W * W / sum(w * w for w in ws)
            se = math.sqrt(max(var, 0.005 ** 2) / max(n_eff, 1))
            serie.append({"data": dia.isoformat(), "s": round(m, 4),
                          "lo": round(m - 1.96 * se, 4), "hi": round(m + 1.96 * se, 4),
                          "n_pesq": len(ws)})
        dia += dt.timedelta(days=1)
    return serie


def _media(xs):
    return sum(xs) / len(xs)


def inflexoes(rows, ini, fim):
    cand = []
    dia = ini + dt.timedelta(days=J)
    while dia <= fim:
        antes = [r for r in rows if 0 < (dia - d(r["fim"])).days <= J]
        depois = [r for r in rows if 0 <= (d(r["fim"]) - dia).days < J]
        ok_n = (len(antes) >= MIN_N and len(depois) >= MIN_N
                and len({r["inst"] for r in antes}) >= 2 and len({r["inst"] for r in depois}) >= 2)
        if ok_n:
            ma, md = _media([r["s_adj"] for r in antes]), _media([r["s_adj"] for r in depois])
            va = sum((r["s_adj"] - ma) ** 2 for r in antes) / (len(antes) - 1)
            vd = sum((r["s_adj"] - md) ** 2 for r in depois) / (len(depois) - 1)
            se = math.sqrt(max(va, 1e-5) / len(antes) + max(vd, 1e-5) / len(depois))
            z = (md - ma) / se
            # corroboração: institutos dos dois lados, sinal da diferença
            comuns = sorted({r["inst"] for r in antes} & {r["inst"] for r in depois})
            sinais = []
            for i in comuns:
                a_ = _media([r["s"] for r in antes if r["inst"] == i])
                d_ = _media([r["s"] for r in depois if r["inst"] == i])
                sinais.append((i, d_ - a_))
            mesmo = [i for i, x in sinais if x * (md - ma) > 0]
            if abs(z) >= Z_MIN:
                cand.append({"data": dia.isoformat(), "delta_pp": round(100 * (md - ma), 2),
                             "z": round(z, 2), "n_antes": len(antes), "n_depois": len(depois),
                             "institutos_mesmo_sinal": mesmo,
                             "institutos_comparaveis": [i for i, _ in sinais],
                             "corroborado": len(mesmo) >= 2})
        dia += dt.timedelta(days=1)
    # vizinhos viram um só: o de maior |z| em cada sequência de dias consecutivos
    picos, grupo = [], []
    for c in cand:
        if grupo and (d(c["data"]) - d(grupo[-1]["data"])).days > 1:
            picos.append(max(grupo, key=lambda x: abs(x["z"])))
            grupo = []
        grupo.append(c)
    if grupo:
        picos.append(max(grupo, key=lambda x: abs(x["z"])))
    return picos


def antes_depois(rows, data_ev):
    """Pareado por instituto. Devolve None sem nenhum par."""
    de = d(data_ev)
    pares = []
    for i in sorted({r["inst"] for r in rows}):
        mine = [r for r in rows if r["inst"] == i]
        antes = [r for r in mine if 0 < (de - d(r["fim"])).days <= ANTES_MAX]
        depois = [r for r in mine if d(r["ini"]) > de and (d(r["ini"]) - de).days <= DEPOIS_MAX]
        if antes and depois:
            a_ = max(antes, key=lambda r: r["fim"])
            d_ = min(depois, key=lambda r: r["ini"])
            pares.append({"inst": i, "antes": a_["fim"], "depois": d_["fim"],
                          "delta_pp": round(100 * (d_["s"] - a_["s"]), 2)})
    if not pares:
        return None
    m = _media([p["delta_pp"] for p in pares])
    return {"n_institutos": len(pares), "delta_medio_pp": round(m, 2),
            "mesmo_sinal": sum(1 for p in pares if p["delta_pp"] * m > 0), "pares": pares}


def serie_modelo(polls, par, params, ini, fim):
    """P(vitória) de cada finalista no modelo principal, reconstruída por dia."""
    import eleicoes_model as em
    # mesmo filtro do simulate(): cenário segundo_turno da corrida; o par é
    # conferido dentro de runoff_prob_from_polls
    p2t = [p for p in polls if p["cenario"] == "segundo_turno" and p["race"] == "PRES"]
    a = min(par)
    out, dia = [], ini
    while dia <= fim:
        vis = [p for p in p2t if p["campo_fim"] and d(p["campo_fim"]) <= dia]
        pr = em.runoff_prob_from_polls(vis, tuple(sorted(par)), dia, params, detalhe=True)
        if pr[0] is not None:
            prob_a, margem, sigma = pr
            do_par = [p for p in vis if sorted(n["sq"] for n in p["numeros"]
                                               if n["sq"] is not None) == sorted(par)]
            out.append({"data": dia.isoformat(), "n_pesq": len(do_par),
                        "n_pesq_pos_1t": sum(1 for p in do_par if d(p["campo_fim"]) > T1),
                        "p": {str(sq): round(prob_a if sq == a else 1 - prob_a, 4) for sq in par},
                        "margem": round(margem, 4), "sigma": round(sigma, 4)})
        dia += dt.timedelta(days=1)
    return out


def congela_historico(par):
    """P(eleito) PUBLICADA da presidencial, uma por as_of, lida do git."""
    import subprocess
    rel = "data/eleicoes2026_results.json"
    hs = subprocess.run(["git", "log", "--format=%H", "--", rel], cwd=ROOT,
                        capture_output=True, text=True, check=True).stdout.split()
    por_dia = {}
    for h in hs:   # do mais novo para o mais antigo: a 1ª vista de cada as_of é a última publicada
        doc = json.loads(subprocess.run(["git", "show", f"{h}:{rel}"], cwd=ROOT,
                                        capture_output=True, text=True, check=True).stdout)
        as_of = doc["meta"]["as_of"]
        if d(as_of) >= T1 or as_of in por_dia:
            continue
        cs = {c["sq"]: c for c in doc["races"]["PRES"]["candidates"]}
        if not all(sq in cs for sq in par):
            continue
        por_dia[as_of] = {"data": as_of, "commit": h[:12],
                          "p": {str(sq): round(cs[sq]["eleito"], 4) for sq in par}}
    serie = [por_dia[k] for k in sorted(por_dia)]
    with open(HIST, "w", encoding="utf-8") as f:
        json.dump({"_doc": ("P(eleito presidente) PUBLICADA pelo site antes do 1º turno: última "
                            "versão do results.json de cada as_of no git (commit em cada ponto). "
                            "Congelado por `eleicoes_2t.py --congelar` em 23/10/2026; não regenerar."),
                   "par": par, "serie": serie}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"historico_pres.json · {len(serie)} dias publicados ({serie[0]['data']} a {serie[-1]['data']})")


def eventos_2t(doc, par):
    out = []
    for e in doc.get("eventos", []):
        if d(e["data"]) <= T1 or not set(e["alvo"]) & set(par):
            continue
        out.append(e)
    return sorted(out, key=lambda e: (e["data"], e.get("hora") or "99:99", e["id"]))


def main():
    res = json.load(open(RESULTS, encoding="utf-8"))
    ap = res["races"]["PRES"].get("apuracao_1t")
    if not ap or ap.get("status") != "segundo_turno":
        print("sem 2º turno presidencial apurado; segundo_turno.json NÃO gerado")
        return 0
    cands = {c["sq"]: c for c in res["races"]["PRES"]["candidates"]}
    # ordem de exibição: 1º colocado do 1º turno primeiro
    par = sorted(ap["finalistas"], key=lambda sq: -ap["votos_validos"][str(sq)])
    polls = json.load(open(POLLS, encoding="utf-8"))["polls"]
    rows = pesquisas_do_par(polls, par)
    if len(rows) < 2:
        print(f"só {len(rows)} pesquisa(s) do par; segundo_turno.json NÃO gerado")
        return 0
    ini = d(min(r["fim"] for r in rows))
    fim = d(max(r["fim"] for r in rows))
    casa = efeitos_de_casa(rows, ini, fim)
    for r in rows:
        r["s_adj"] = r["s"] - casa[r["inst"]]
    serie = nivel_diario(rows, ini, fim)
    picos = inflexoes(rows, ini, fim)

    if "--congelar" in sys.argv:
        congela_historico(par)
    params = res["meta"]["params"]
    modelo = serie_modelo(polls, par, params, T1 + dt.timedelta(days=1), fim)

    doc = json.load(open(EVENTOS, encoding="utf-8"))
    evs = []
    for e in eventos_2t(doc, par):
        # o delta é sempre na share do 1º do par; a página traduz para o alvo
        ad = antes_depois(rows, e["data"])
        evs.append({"id": e["id"], "data": e["data"], "hora": e.get("hora"),
                    "hora_tipo": e.get("hora_tipo"), "tipo": e["tipo"],
                    "titulo": e.get("titulo") or e["id"], "resumo": e.get("resumo", ""),
                    "alvo": e["alvo"], "direcao_esperada": e["direcao_esperada"],
                    "importancia": e.get("importancia", 1),
                    "pre_especificado": e["registrado_em"] <= e["data"],
                    # None = o registro não diz (eventos anteriores ao campo)
                    "direcao_cega": e.get("direcao_cega"),
                    "fonte": e["fonte"], "antes_depois": ad})

    out = {
        "schema_version": 1,
        "_doc": ("Linha do tempo do 2º turno presidencial (src/eleicoes_2t.py). "
                 "s = share bidirecional do 1º sq do par, A/(A+B), indecisos fora. "
                 "Nível diário com kernel triangular e efeito de casa encolhido. "
                 "Inflexão = candidata, |z|>=Z_MIN entre janelas de J dias; "
                 "'corroborado' exige o mesmo sinal em 2+ institutos. "
                 "Evento: antes × depois pareado por instituto, exploratório se "
                 "registrado depois do fato, e não separa eventos próximos."),
        "params": {"BW": BW, "K": K, "N_CAP": N_CAP, "J": J, "Z_MIN": Z_MIN,
                   "MIN_N": MIN_N, "ANTES_MAX": ANTES_MAX, "DEPOIS_MAX": DEPOIS_MAX},
        "par": par,
        "nomes": {str(sq): cands[sq].get("urna") or cands[sq].get("nome") for sq in par},
        "primeiro_turno": {str(sq): ap["votos_validos"][str(sq)] for sq in par},
        "efeito_casa_pp": {i: round(100 * v, 2) for i, v in casa.items()},
        "pesquisas": [{k: r[k] for k in ("id", "inst", "ini", "fim", "n", "mg", "a", "b", "ind")}
                      | {"s": round(r["s"], 4), "s_adj": round(r["s_adj"], 4)} for r in rows],
        "serie": serie,
        "modelo": {"_doc": ("RECONSTRUÍDA: P(vitória) do modelo principal (runoff_prob_from_polls) "
                            "em cada dia com as pesquisas de 2º turno do par com fim de campo até o "
                            "dia. O site não publicou esses valores de 05 a 21/10."),
                   "eleito_site": {str(sq): cands[sq]["eleito"] for sq in par},
                   "serie": modelo,
                   "publicado_1t": (json.load(open(HIST, encoding="utf-8"))["serie"]
                                    if os.path.exists(HIST) else [])},
        "inflexoes": picos,
        "eventos": evs,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"segundo_turno.json · {len(rows)} pesquisas do par · {len(serie)} dias · "
          f"{len(picos)} inflexão(ões) candidata(s) · {len(evs)} evento(s)")
    for p in picos:
        print(f"  {p['data']}  {p['delta_pp']:+.2f}pp  z={p['z']:+.2f}  "
              f"{'corroborada' if p['corroborado'] else 'não corroborada'} "
              f"({', '.join(p['institutos_mesmo_sinal']) or '-'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
