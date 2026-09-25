#!/usr/bin/env python3
"""Testes do link da proposta de governo (TSE) nas linhas de candidato.

Regra: TODO candidato a cargo executivo (presidente, governador) que vira linha
na página (share >= 0,5% ou P(eleito) >= 0,5%) leva exatamente um link para a sua página oficial no DivulgaCandContas,
com a UE certa ("BR" para presidente, a UF para governador). Senador NÃO leva
(não registra proposta de governo). O link é hiperlink, não dependência
(invariante 4), e a origem tem de estar liberada no gate `_ext`.

ERRO PLANTADO (rodado na produção): montar o link do governador com UE "BR". A
URL continua válida em forma e a página abre no TSE, mas num candidato que NÃO é
aquele. O bloco 3 confere cada UE contra a corrida do sq.

Usa rede? Não.

Uso:  python3 src/test_propostas_link.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
FALHAS = []
RX = re.compile(r'href="https://divulgacandcontas\.tse\.jus\.br/divulga/#/candidato/2026/(\d+)/([A-Z]{2})/(\d+)"')


def check(nome, cond, detalhe=""):
    print(f"  {'ok  ' if cond else 'FALHA'} {nome}" + (f"  ({detalhe})" if detalhe else ""))
    if not cond:
        FALHAS.append(nome)


def links(html):
    return [(m.group(1), m.group(2), int(m.group(3))) for m in RX.finditer(html)]


def esperados(race):
    """Quem vira LINHA na página: a mesma regra do build (share >= 0,5% OU
    P(eleito) >= 0,5%). O gate também confere contra as linhas renderizadas,
    para não confiar só na cópia da regra."""
    return {c["sq"] for c in race["candidates"]
            if not (c["share"] < 0.005 and c.get("eleito", 0) < 0.005)}


def linhas_tabela0(html):
    t = re.search(r"<table class=extb>(.*?)</table>", html, re.S)
    return len(re.findall(r"<tr><th scope=row>", t.group(1))) if t else 0


def main():
    res = json.load(open(os.path.join(ROOT, "data", "eleicoes2026_results.json"), encoding="utf-8"))
    races = res["races"]
    dist = os.path.join(ROOT, "dist")

    print("1. presidencial")
    h = open(os.path.join(dist, "eleicoes_dashboard.html"), encoding="utf-8").read()
    L = links(h)
    sqs = esperados(races["PRES"])
    check("um link por candidato que vira linha (share>=0,5% ou P(eleito)>=0,5%)",
          len(L) == len(sqs), f"{len(L)} links, {len(sqs)} esperados de {len(races['PRES']['candidates'])}")
    check("links == linhas renderizadas na tabela de candidatos",
          len(L) == linhas_tabela0(h), f"{len(L)} vs {linhas_tabela0(h)}")
    check("todos com UE = BR", all(ue == "BR" for _, ue, _ in L))
    check("todos os sq são da presidencial", {sq for _, _, sq in L} == sqs)
    check("id da eleição único", {e for e, _, _ in L} == {"20322002026"})
    check("link acessível: aria-label com o nome", h.count("aria-label=\"Proposta de governo e registro de") == len(L))

    print("\n2. governadores e senadores, nas 27 UFs")
    ufs = sorted(k[4:] for k in races if k.startswith("GOV-"))
    ruins = []
    for uf in ufs:
        h = open(os.path.join(dist, f"eleicoes_uf_{uf.lower()}.html"), encoding="utf-8").read()
        L = links(h)
        gov = esperados(races[f"GOV-{uf}"])
        if len(L) != linhas_tabela0(h):
            ruins.append((uf, "links != linhas", len(L), linhas_tabela0(h)))
        sen = {c["sq"] for c in races.get(f"SEN-{uf}", {"candidates": []})["candidates"]}
        if {sq for _, _, sq in L} != gov:
            ruins.append((uf, "gov", len(L), len(gov)))
        if any(sq in sen for _, _, sq in L):
            ruins.append((uf, "senado com link"))
        if any(ue != uf for _, ue, _ in L):
            ruins.append((uf, "UE errada", sorted({ue for _, ue, _ in L})))
    check("todo governador listado tem link, nenhum senador tem", not ruins, f"{ruins[:4]}")
    check("27 UFs conferidas", len(ufs) == 27)

    print("\n3. ERRO PLANTADO: a UE de cada link tem de ser a da corrida do sq")
    corrida_de = {}
    for k, r in races.items():
        for c in r["candidates"]:
            corrida_de[c["sq"]] = k
    errados = []
    for f in sorted(os.listdir(dist)):
        if not (f.startswith("eleicoes_uf_") or f == "eleicoes_dashboard.html"):
            continue
        for _, ue, sq in links(open(os.path.join(dist, f), encoding="utf-8").read()):
            k = corrida_de.get(sq)
            esperada = "BR" if k == "PRES" else (k[4:] if k else None)
            if esperada != ue:
                errados.append((f, ue, sq, k))
    check("nenhum link aponta para a UE errada", not errados, f"{errados[:3]}")

    print("\n4. zero-dep continua valendo")
    sh = open(os.path.join(ROOT, "atualizar_eleicoes.sh"), encoding="utf-8").read()
    check("o gate _ext libera a origem do TSE", "divulgacandcontas\\.tse\\.jus\\.br" in sh)
    h = open(os.path.join(dist, "eleicoes_dashboard.html"), encoding="utf-8").read()
    check("nada é CARREGADO do TSE (só <a href>)",
          not re.search(r'<(script|link|img|iframe)[^>]+divulgacandcontas', h))
    inf = open(os.path.join(dist, "eleicoes_inflexoes.html"), encoding="utf-8").read()
    check("a página de inflexões não ganhou link (não tem linha de candidato)", "divulgacandcontas" not in inf)

    print()
    if FALHAS:
        print(f"REPROVADO: {len(FALHAS)} falha(s): {', '.join(FALHAS)}", file=sys.stderr)
        sys.exit(1)
    print("OK: link da proposta validado · presidencial e 27 governadores com UE certa, senado sem link.")


if __name__ == "__main__":
    main()
