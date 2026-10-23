#!/usr/bin/env python3
"""Testes da linha do tempo do 2º turno (src/eleicoes_2t.py + seção da presidencial).

Regra da casa: gate só vale com ERRO PLANTADO. Os casos sintéticos medem o CÓDIGO
e não dependem do dado do dia (lição de 03/10/2026); os casos do dado real só
conferem coerência interna do JSON gerado e da página.

Os três erros que importam:
1. Contar como "depois" uma pesquisa que começou NO DIA do evento. O campo estava
   parcialmente antes do fato, e o antes × depois mediria o nada.
2. Antes × depois sem parear por instituto: o efeito de casa vira "efeito".
3. Chamar de corroborada uma inflexão vista por um instituto só.

Usa rede? Não.

Uso:  python3 src/test_2t_linha_do_tempo.py
"""
import copy
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eleicoes_2t as t2      # noqa: E402
import eleicoes_eventos as ev  # noqa: E402

ROOT = os.path.join(HERE, "..")
FALHAS = []


def check(nome, cond, detalhe=""):
    print(f"  {'ok  ' if cond else 'FALHA'} {nome}" + (f"  ({detalhe})" if detalhe else ""))
    if not cond:
        FALHAS.append(nome)


def row(inst, ini, fim, s, n=2000):
    return {"id": f"{inst}-{fim}", "inst": inst, "ini": ini, "fim": fim, "n": n,
            "mg": 2.0, "a": 100 * s, "b": 100 * (1 - s), "ind": None, "s": s, "s_adj": s}


def main():
    # 1. antes × depois: campo iniciado no dia do evento NÃO é "depois"
    print("1. antes × depois respeita o início do campo")
    rows = [row("A", "2026-10-08", "2026-10-09", 0.52),
            row("A", "2026-10-10", "2026-10-12", 0.40),   # começou NO dia do evento
            row("A", "2026-10-11", "2026-10-13", 0.50)]
    ad = t2.antes_depois(rows, "2026-10-10")
    check("o 'depois' é a 1ª pesquisa com campo iniciado DEPOIS do dia do evento",
          ad and ad["pares"][0]["depois"] == "2026-10-13", str(ad))
    check("delta = 0,50 - 0,52 = -2 p.p. (e não -12 com a pesquisa contaminada)",
          ad and abs(ad["delta_medio_pp"] + 2.0) < 1e-9, str(ad and ad["delta_medio_pp"]))
    check("sem pesquisa depois, não inventa par",
          t2.antes_depois(rows[:1], "2026-10-10") is None)

    # 2. pareado por instituto: viés de casa se cancela
    print("\n2. antes × depois pareado por instituto")
    rows = [row("A", "2026-10-07", "2026-10-08", 0.50), row("A", "2026-10-11", "2026-10-12", 0.51),
            row("B", "2026-10-07", "2026-10-08", 0.55), row("B", "2026-10-11", "2026-10-12", 0.56)]
    # sem parear, "B só antes, A só depois" daria um salto de -4 p.p. que não existe
    ad = t2.antes_depois(rows, "2026-10-10")
    check("dois institutos, +1 p.p. cada, média +1", ad and ad["n_institutos"] == 2
          and abs(ad["delta_medio_pp"] - 1.0) < 1e-9 and ad["mesmo_sinal"] == 2, str(ad))
    so_a_depois = [rows[1], rows[2]]
    check("instituto que só aparece de um lado não forma par (viés de casa não vira efeito)",
          t2.antes_depois(so_a_depois, "2026-10-10") is None)

    # 3. inflexão: corroboração exige 2 institutos no mesmo sentido
    print("\n3. inflexão corroborada só com 2+ institutos")
    base = []
    for i, dd in enumerate(range(1, 9)):
        dia = f"2026-10-{dd:02d}"
        for inst, s in (("A", 0.52), ("B", 0.521), ("C", 0.519)):
            base.append(row(inst, dia, dia, s + (0.001 if i % 2 else -0.001)))
    salto_dois = copy.deepcopy(base)
    for r in salto_dois:
        if r["fim"] >= "2026-10-05" and r["inst"] in ("A", "B"):
            r["s"] = r["s_adj"] = r["s"] - 0.02
    salto_um = copy.deepcopy(base)
    for r in salto_um:
        if r["fim"] >= "2026-10-05" and r["inst"] == "A":
            r["s"] = r["s_adj"] = r["s"] - 0.06
    d0, d1 = t2.d("2026-10-01"), t2.d("2026-10-08")
    p2 = [p for p in t2.inflexoes(salto_dois, d0, d1) if p["data"] == "2026-10-05"]
    p1 = [p for p in t2.inflexoes(salto_um, d0, d1) if p["data"] == "2026-10-05"]
    check("queda em 2 institutos: inflexão em 05/10 corroborada", p2 and p2[0]["corroborado"], str(p2))
    check("queda num instituto só: se detectada, NÃO é corroborada",
          not p1 or not p1[0]["corroborado"], str(p1))
    check("sem salto, nenhuma inflexão", not t2.inflexoes(base, d0, d1))

    # 4. validador: hora
    print("\n4. registro de eventos: hora")
    structure = json.load(open(ev.STRUCT, encoding="utf-8"))
    sqs = {c["sq"] for r in structure["races"].values() for c in r["candidates"]}
    doc = json.load(open(ev.EVENTOS, encoding="utf-8"))
    check("registro versionado válido", not ev.valida(doc, sqs), str(ev.valida(doc, sqs)[:3]))
    e0 = copy.deepcopy(doc["eventos"][0])
    for h, ht, nome in (("25:00", "fato", "hora 25:00"), ("21h20", "fato", "hora sem dois-pontos"),
                        ("21:20", None, "hora sem hora_tipo")):
        e = dict(e0, hora=h, id="plantado")
        if ht:
            e["hora_tipo"] = ht
        check(f"recusa {nome}", ev.valida({"eventos": [e]}, sqs))
    check("aceita 21:20 do fato", not ev.valida({"eventos": [dict(e0, hora="21:20", hora_tipo="fato")]}, sqs))

    # 5. dado real: JSON coerente e página estática
    print("\n5. segundo_turno.json e a página")
    if not os.path.exists(t2.OUT):
        check("segundo_turno.json existe (rode src/eleicoes_2t.py)", False)
    else:
        seg = json.load(open(t2.OUT, encoding="utf-8"))
        ser = seg["serie"]
        check("série diária contínua", all((t2.d(b["data"]) - t2.d(a["data"])).days == 1
                                           for a, b in zip(ser, ser[1:])))
        check("lo <= s <= hi em todo dia", all(x["lo"] <= x["s"] <= x["hi"] for x in ser))
        check("pesquisas só depois do 1º turno",
              all(t2.d(p["fim"]) > t2.T1 for p in seg["pesquisas"]))
        chave = [(e["data"], e["hora"] or "99:99") for e in seg["eventos"]]
        check("eventos em ordem de data e hora", chave == sorted(chave))
        h = open(os.path.join(ROOT, "dist", "eleicoes_dashboard.html"), encoding="utf-8").read()
        sem_js = re.sub(r"<script.*?</script>", "", h, flags=re.S)
        check("seção pré-renderizada (funciona sem JS)",
              "data-scene=segundo_turno_tempo" in sem_js and "<svg" in sem_js)
        n_tl = len(re.findall(r'<li class="tli', sem_js))
        check("linha do tempo da página tem todos os eventos do JSON",
              n_tl == len(seg["eventos"]), f"{n_tl} vs {len(seg['eventos'])}")
        sec = sem_js.split("data-scene=segundo_turno_tempo", 1)[-1].split("data-scene=evolucao", 1)[0]
        check("nenhum link externo na seção (fonte vai por nome; o gate _ext não lista veículos)",
              "http" not in sec)
        # 23/10 (2): com 3 linhas fixas de números o nº 9, o fato da semana, sumia do gráfico
        nums = {int(x) for x in re.findall(r'class="ct cen(?: cef)?" text-anchor=middle>(\d+)</text>', sec)}
        check("todo evento tem número no gráfico",
              nums == set(range(1, len(seg["eventos"]) + 1)),
              f"faltam {sorted(set(range(1, len(seg['eventos']) + 1)) - nums)[:8]}")
        check("cada número e cada inflexão do gráfico tem balão (data-tip)",
              len(re.findall(r'<g class=tip [^>]*data-tip="\d+ ·', sec)) == len(seg["eventos"])
              and len(re.findall(r'data-tip="Inflexão', sec)) >= len(seg["inflexoes"]))
        check("linha do tempo fechada num acordeão",
              re.search(r'<details class="acc"><summary>.{0,200}Linha do tempo', sec, re.S) is not None)
        import build_eleicoes as be
        check("o balão não mede nada (regra LGPD: nenhum texto de notícia no dataLayer)",
              "dataLayer" not in be.TIP_JS and "track(" not in be.TIP_JS)

    # 6. modelo principal reconstruído
    print("\n6. chance de vitória do modelo principal, reconstruída por dia")
    if os.path.exists(t2.OUT):
        mod = seg["modelo"]
        ms = mod["serie"]
        par = [str(sq) for sq in seg["par"]]
        check("série do modelo diária e contínua desde 05/10",
              ms and ms[0]["data"] == "2026-10-05"
              and all((t2.d(b["data"]) - t2.d(a["data"])).days == 1 for a, b in zip(ms, ms[1:])))
        check("as duas chances somam 100% em todo dia",
              all(abs(x["p"][par[0]] + x["p"][par[1]] - 1) < 1e-3 for x in ms))
        dif = max(abs(ms[-1]["p"][sq] - mod["eleito_site"][sq]) for sq in par)
        check("último ponto bate com o número do topo da página (ruído do Monte Carlo)",
              dif < 0.015, f"diferença {dif * 100:.2f} p.p.")
        check("só pesquisas até o dia: em 05/10 nenhuma pesquisa pós-1º turno",
              ms[0]["n_pesq_pos_1t"] == 0 and ms[-1]["n_pesq_pos_1t"] == len(seg["pesquisas"]),
              f'{ms[0]["n_pesq_pos_1t"]} e {ms[-1]["n_pesq_pos_1t"]}')
        # ERRO PLANTADO: reconstrução que enxerga o futuro dá o mesmo valor todo dia
        import eleicoes_model as em
        res = json.load(open(t2.RESULTS, encoding="utf-8"))
        polls = json.load(open(t2.POLLS, encoding="utf-8"))["polls"]
        par_i = [int(sq) for sq in par]
        orig = em.runoff_prob_from_polls
        try:
            em.runoff_prob_from_polls = lambda ps, pair, as_of, params, detalhe=False: orig(
                [p for p in polls if p["cenario"] == "segundo_turno" and p["race"] == "PRES"],
                pair, as_of, params, detalhe)
            vaz = t2.serie_modelo(polls, par_i, res["meta"]["params"], t2.d(ms[0]["data"]), t2.d(ms[-1]["data"]))
        finally:
            em.runoff_prob_from_polls = orig
        check("erro plantado (olhar o futuro) muda a série: o teste pega vazamento",
              abs(vaz[0]["p"][par[0]] - ms[0]["p"][par[0]]) > 0.02,
              f'{vaz[0]["p"][par[0]]:.3f} vs {ms[0]["p"][par[0]]:.3f}')

    print()
    if FALHAS:
        print(f"REPROVADO: {len(FALHAS)} falha(s)", file=sys.stderr)
        sys.exit(1)
    print("OK: linha do tempo do 2º turno validada")


if __name__ == "__main__":
    main()
