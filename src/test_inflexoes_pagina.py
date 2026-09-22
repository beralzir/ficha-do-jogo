#!/usr/bin/env python3
"""Testes da página Inflexões (Fase D, Janela 2).

Esta página é a mais fácil do site de tornar desonesta sem ninguém perceber. Ela
põe, no mesmo eixo, um movimento detectado e um evento da campanha, e o leitor
liga os dois sozinho. As três ressalvas que impedem isso são texto, e texto some
em refactor sem quebrar nada. Este gate existe para que sumir quebre.

ERRO PLANTADO (rodado no HTML de produção, não só aqui):
  1. Apagar a ressalva de MAGNITUDE. Sem ela a página vende +1,87 p.p. como se
     fosse medida confiável, quando a magnitude é subestimada por construção.
  2. Apagar o aviso de que coincidir não é causar.
  3. Datar, no gráfico de um candidato, um evento que NÃO mira ele. Com um único
     evento no registro isso fazia o episódio do Cury aparecer datado embaixo da
     série do Flávio Bolsonaro, sugerindo relevância inexistente.
  4. Declarar `pre_especificado` em vez de derivar de (registrado_em <= data).

Usa rede? Não.

Uso:  python3 src/test_inflexoes_pagina.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
PAG = os.path.join(ROOT, "dist", "eleicoes_inflexoes.html")
FALHAS = []


def check(nome, cond, detalhe=""):
    print(f"  {'ok  ' if cond else 'FALHA'} {nome}" + (f"  ({detalhe})" if detalhe else ""))
    if not cond:
        FALHAS.append(nome)


def main():
    print("1. a página existe e é estático-primeiro")
    check("dist/eleicoes_inflexoes.html existe", os.path.exists(PAG))
    if not os.path.exists(PAG):
        print("REPROVADO", file=sys.stderr)
        sys.exit(1)
    h = open(PAG, encoding="utf-8").read()
    # INVARIANTE 3 da casa: renderiza com JavaScript desativado.
    sem_js = re.sub(r"<script.*?</script>", "", h, flags=re.S)
    check("o conteúdo sobrevive sem JavaScript", len(sem_js) > 40000,
          f"{len(sem_js)} bytes sem <script>")
    check("o gráfico é gerado em Python, não por JS",
          sem_js.count("<polyline") >= 4 and sem_js.count("<polygon") >= 4,
          f"{sem_js.count('<polyline')} linhas, {sem_js.count('<polygon')} bandas")
    check("as tabelas estão no HTML", sem_js.count("<table") >= 2)
    # Regra certa: todo <svg> ou é conteúdo (role=img + aria-label) ou é
    # decorativo (aria-hidden). A 1ª versão exigia role=img de TODOS e reprovava
    # o logo da marca, que é decorativo e está certo com aria-hidden: o gate
    # acusava a página por um acerto dela.
    tags = re.findall(r"<svg[^>]*>", sem_js)
    ruins = [t[:70] for t in tags
             if not (('role="img"' in t and "aria-label=" in t)
                     or 'aria-hidden="true"' in t)]
    check("todo SVG é conteúdo rotulado ou decorativo declarado",
          not ruins, f"{len(tags)} svg, {len(ruins)} sem tratamento: {ruins[:2]}")
    graficos = [t for t in tags if 'role="img"' in t]
    check("todo gráfico tem aria-label descritivo",
          all("aria-label=" in t and len(t) > 80 for t in graficos),
          f"{len(graficos)} gráficos rotulados")

    # INVARIANTE 4: zero-dep, só GTM e o link CC.
    ext = sorted(set(re.findall(r"https?://([a-z0-9.-]+)", h)))
    permitidas = {"bera.ia.br", "www.googletagmanager.com", "creativecommons.org"}
    check("zero dependência externa além do GTM e do link CC",
          not (set(ext) - permitidas), f"origens: {ext}")

    print("\n2. ERRO PLANTADO 1 e 2: as ressalvas que seguram a página")
    # Os NÚMEROS, não só as palavras: uma reescrita que perca a medição perde o
    # argumento, e o gate tem de reprovar isso também.
    check("declara 'confie na DATA, desconfie da MAGNITUDE'",
          "desconfie da" in h and "MAGNITUDE" in h.upper())
    for n in ("0,33", "0,06", "48"):
        check(f"traz o número medido {n}", n in h)
    check("explica a causa (p·(1−p) / logit)",
          ("logit" in h and ("p·(1−p)" in h or "p(1-p)" in h)))
    check("diz que coincidir NÃO é causar",
          re.search(r"[Cc]oincidir não é causar", h) is not None)
    check("declara que atribuir efeito exige placebo",
          "placebo" in h)
    check("a banda é declarada como do FILTRO, não do forecast",
          "não a banda do" in h and "forecast" in h)

    print("\n3. ERRO PLANTADO 4: pré-especificação é DERIVADA")
    evp = os.path.join(ROOT, "data", "eleicoes", "eventos.json")
    ev = json.load(open(evp, encoding="utf-8"))
    eventos = ev.get("eventos", [])
    check("o arquivo de eventos NÃO declara pre_especificado",
          not any("pre_especificado" in e for e in eventos))
    n_pre = sum(1 for e in eventos if e["registrado_em"] <= e["data"])
    check("a página publica a contagem DERIVADA",
          f"({n_pre} de {len(eventos)})" in h,
          f"esperado '({n_pre} de {len(eventos)})'")
    # cada evento tem de aparecer na tabela com o selo que a derivação manda
    n_expl = sum(1 for e in eventos if e["registrado_em"] > e["data"])
    check("cada evento exploratório sai rotulado EXPLORATÓRIO",
          h.count("EXPLORATÓRIO") == n_expl, f"{h.count('EXPLORATÓRIO')} de {n_expl}")
    check("nenhum evento sai como PRÉ-ESPECIFICADO sem a derivação permitir",
          h.count("PRÉ-ESPECIFICADO") == n_pre,
          f"{h.count('PRÉ-ESPECIFICADO')} de {n_pre}")

    print("\n4. ERRO PLANTADO 3: evento só é datado em quem ele mira")
    infl = json.load(open(os.path.join(ROOT, "data", "eleicoes", "inflexoes.json"),
                          encoding="utf-8"))
    dest = [r for r in infl["inflexoes"] if r["corroborado"] and r["relevante"]]
    cards = re.findall(r"<article class=infc>(.*?)</article>", h, re.S)
    check("há cartas de candidato", len(cards) >= 4, f"{len(cards)} cartas")
    por_nome = {}
    for c in cards:
        m = re.search(r"<h3 class=sech3>(.*?)\s*<span", c)
        datados = re.findall(r"text-anchor=middle>(\d\d/[a-z]{3})</text>", c)
        por_nome[m.group(1)] = (c, datados)
    erros = []
    for nome, (c, datados) in sorted(por_nome.items()):
        # de quem é esta carta
        sq = next((r["sq"] for r in dest
                   if r["urna"].lower().replace(" ", "") == nome.lower().replace(" ", "")), None)
        mirados = {e["data"] for e in eventos if sq in (e.get("alvo") or [])}
        # toda data desenhada tem de ser de um evento que mira este candidato
        for d in datados:
            if not any(d == f"{int(x[8:10]):02d}/{['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'][int(x[5:7])-1]}"
                       for x in mirados):
                erros.append((nome, d))
    check("nenhuma carta data um evento que não mira aquele candidato",
          not erros, f"vazamentos: {erros[:3]}")
    sem_alvo = [n for n, (c, d) in sorted(por_nome.items()) if not d]
    check("quem não é alvo declara isso em texto",
          all("nenhum evento registrado MIRA" in por_nome[n][0] for n in sem_alvo),
          f"{len(sem_alvo)} carta(s) sem evento próprio")
    # e o evento conhecido TEM de estar datado em quem ele mira
    alvo_sqs = {sq for e in eventos for sq in (e.get("alvo") or [])}
    com_alvo = [n for n, (c, d) in sorted(por_nome.items()) if d]
    check("o evento do registro aparece datado em quem ele mira",
          bool(com_alvo) if alvo_sqs else True,
          f"cartas com evento datado: {com_alvo}")

    print("\n5. a página não afirma mais do que o funil entrega")
    check("declara o funil (bruto -> destaques)",
          str(len(infl["inflexoes"])) in h and str(len(dest)) in h,
          f"{len(infl['inflexoes'])} brutos, {len(dest)} destaques")
    check("as ressalvas do JSON viajam para a página",
          all(c[:40] in h for c in infl.get("ressalvas", [])[:3]))
    proibidas = ["causou", "provocou", "por causa do evento", "efeito do evento"]
    achadas = [p for p in proibidas if p in h.lower()]
    check("a página não usa linguagem de causa", not achadas, f"{achadas}")

    print("\n6. rota e navegação")
    w = open(os.path.join(ROOT, "worker.js"), encoding="utf-8").read()
    check("worker.js roteia /inflexoes", '"inflexoes": "eleicoes_inflexoes.html"' in w)
    check("worker.js dá 301 do .html para o slug",
          '"eleicoes_inflexoes.html": "inflexoes"' in w)
    check("a aba aparece na navegação de TODA página da edição",
          all('href="./inflexoes"' in open(os.path.join(ROOT, "dist", f), encoding="utf-8").read()
              or f == "eleicoes_inflexoes.html"
              for f in os.listdir(os.path.join(ROOT, "dist"))
              if f.startswith("eleicoes_") and f.endswith(".html")))

    print()
    if FALHAS:
        print(f"REPROVADO: {len(FALHAS)} falha(s): {', '.join(FALHAS)}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: página Inflexões validada · {len(cards)} cartas, {len(dest)} destaques, "
          f"{n_pre} de {len(eventos)} eventos pré-especificados.")


if __name__ == "__main__":
    main()
