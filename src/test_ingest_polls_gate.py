#!/usr/bin/env python3
"""Testes OFFLINE do gate de plausibilidade do ingest de pesquisas (C0-c).

Nasceu do plano de risco (docs/plano-risco-eleicoes.md): até 31/08/2026 a
Wikipédia entrava sem NENHUMA validação num pipeline que publica sozinho, e uma
linha forjada valia 67,9% do agregado em GOV-RR/SEN-RR.

Regra da casa (aprendizado do gate_citacao do vox, que nasceu com bug de
pareamento e 41 falsos positivos): gate só vale depois de provado com ERRO
PLANTADO. Os casos 2 a 5 plantam adulteração de propósito e exigem que o gate
pegue; o caso 1 exige que ele NÃO reprove o dado real em massa.

Uso:  python3 src/test_ingest_polls_gate.py        (não usa rede)
"""
import collections
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ingest_polls as ip  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
POLLS = os.path.join(ROOT, "data", "live", "polls.json")

FALHAS = []


def check(nome, cond, detalhe=""):
    print(f"  {'ok  ' if cond else 'FALHA'} {nome}" + (f"  ({detalhe})" if detalhe else ""))
    if not cond:
        FALHAS.append(nome)


def diff_em_tmp(prev_polls, aceitas, quarentena):
    """Roda o write_diff de produção sem tocar o data/eleicoes/ingest_diff.txt,
    que é versionado: aponta DIFFOUT para um arquivo temporário e devolve o texto."""
    orig = ip.DIFFOUT
    with tempfile.TemporaryDirectory() as d:
        ip.DIFFOUT = os.path.join(d, "ingest_diff.txt")
        try:
            return ip.write_diff(prev_polls, aceitas, quarentena)
        finally:
            ip.DIFFOUT = orig


def cabecalho(txt):
    """{'antes': n, 'depois': n, ...} da linha de contagens do diff."""
    return {k: int(v) for k, v in (c.split(": ") for c in txt.split("\n")[1].split(" | "))}


def forjar(base, race, pct_alvo, manter_lista=True, **over):
    """Clona uma pesquisa real e adultera o líder, como faria quem edita a wiki.

    Usa os SQ REAIS da pesquisa modelo de propósito: o parser só casa candidato
    que existe no structure, então uma forjadura com SQ inventado nem chegaria
    aqui. Testar com SQ falso mediria um cenário que não acontece.

    manter_lista=True (padrão) mantém a MESMA lista de candidatos da tabela e só
    mexe nos números: é o que faz quem edita uma wikitable e quer que a linha
    continue parecendo as vizinhas. manter_lista=False encolhe para 2 nomes, o
    caso que o gate reconhecidamente não bloqueia (ver caso 7).
    """
    p = json.loads(json.dumps(base))
    p["id"] = "FORJADA-" + race
    p["race"] = race
    reais = sorted([n for n in base["numeros"] if n.get("sq")], key=lambda n: -n["pct"])
    if not manter_lista:
        reais = reais[:2]
    resto = max(0.0, 100.0 - pct_alvo)
    p["numeros"] = [dict(reais[0], pct=pct_alvo)]
    outros = reais[1:]
    for n in outros:                       # divide o resto entre os demais
        p["numeros"].append(dict(n, pct=round(resto / len(outros), 1)))
    p.update(over)
    return p


def main():
    polls = json.load(open(POLLS, encoding="utf-8"))["polls"]
    ids = {p["id"] for p in polls}
    print(f"base real: {len(polls)} pesquisas\n")

    # 1. O gate NÃO pode reprovar o dado real em massa. Rodando com prev_ids
    #    vazio, TODA pesquisa é tratada como nova: é o pior caso possível.
    print("1. dado real não é reprovado em massa (pior caso: tudo é novo)")
    rep = {}
    aceitas, quar = ip.plausibility_gate(json.loads(json.dumps(polls)), set(), rep)
    taxa = 100.0 * len(quar) / max(len(polls), 1)
    check("taxa de quarentena do dado real <= 2%", taxa <= 2.0, f"{taxa:.2f}% ({len(quar)})")
    check("nenhuma pesquisa some sem ir para a quarentena",
          len(aceitas) + len(quar) == len(polls), f"{len(aceitas)}+{len(quar)}={len(polls)}")

    # 2. Pesquisas já publicadas não são reescritas retroativamente.
    print("\n2. histórico já publicado não é reescrito")
    rep2 = {}
    aceitas2, quar2 = ip.plausibility_gate(json.loads(json.dumps(polls)), ids, rep2)
    check("com todas conhecidas, quarentena é vazia", not quar2, f"{len(quar2)}")
    check("todas as pesquisas seguem aceitas", len(aceitas2) == len(polls))

    # 2b. O diff de auditoria não acusa sintética como sumida da fonte.
    #     main() reanexa as sintéticas do arquivo anterior DEPOIS do write_diff,
    #     então elas nunca chegam em `aceitas`. Até 25/09/2026 o diff as contava só
    #     no "antes" e toda rodada gravava "- sumiu da fonte" em falso para o mock
    #     da vox. Cenário construído (uma sintética clonada), como no caso 5: não
    #     depende de haver sintética no polls.json do mês. A fonte é a lista real
    #     inalterada, que o gate aceita inteira quando tudo é conhecido (caso 2).
    print("\n2b. diff de auditoria: sintética preservada não some da fonte")
    reais = [p for p in polls if not p.get("sintetico")]
    sint = dict(json.loads(json.dumps(reais[0])), id="SINTETICA-TESTE", sintetico=True)
    prev2b = polls + [sint]
    n_sint = sum(1 for p in prev2b if p.get("sintetico"))
    txt2b = diff_em_tmp(prev2b, reais, [])
    cab2b = cabecalho(txt2b)
    check("fonte inalterada: sumidas 0 e nenhuma linha 'sumiu da fonte'",
          cab2b["sumidas"] == 0 and "sumiu da fonte" not in txt2b, f"sumidas: {cab2b['sumidas']}")
    check("'antes' e 'depois' contam a mesma coisa (só reais)",
          cab2b["antes"] == cab2b["depois"] == len(reais),
          f"antes {cab2b['antes']}, depois {cab2b['depois']}, reais {len(reais)}")
    check("o cabeçalho declara as sintéticas fora da conta",
          cab2b.get("sintéticas fora da conta") == n_sint,
          f"{cab2b.get('sintéticas fora da conta')} de {n_sint}")
    # O outro lado, também plantado: a correção não pode cegar o diff. Uma
    # pesquisa REAL que some da fonte segue acusada, e só ela.
    vezes = collections.Counter(p["id"] for p in reais)
    alvo = min(i for i, c in vezes.items() if c == 1)      # id de uma linha só
    txt2c = diff_em_tmp(prev2b, [p for p in reais if p["id"] != alvo], [])
    check("pesquisa real que some segue acusada, e só ela",
          f"- sumiu da fonte: {alvo}\n" in txt2c and cabecalho(txt2c)["sumidas"] == 1,
          f"{alvo}; sumidas: {cabecalho(txt2c)['sumidas']}")

    # 3. ERRO PLANTADO: desvio grosseiro numa corrida COM consenso (presidencial).
    print("\n3. erro plantado: desvio grosseiro onde há consenso")
    pres = [p for p in polls if p["race"] == "PRES" and p["cenario"] == "estimulada"
            and p["campo_fim"]]
    pres.sort(key=lambda p: p["campo_fim"])
    modelo = pres[-1]
    plantada = forjar(modelo, "PRES", 95.0)
    rep3 = {}
    _, quar3 = ip.plausibility_gate(json.loads(json.dumps(polls)) + [plantada], ids, rep3)
    pegou = any(q["id"] == "FORJADA-PRES" for q in quar3)
    check("gate PEGA a pesquisa forjada", pegou,
          quar3[0]["motivos"][0][:60] if quar3 else "não pegou")
    check("gate não arrasta ninguém junto", len(quar3) == 1, f"{len(quar3)} em quarentena")

    # 3b. LIMITE CONHECIDO E DECLARADO: forjadura que encolhe a lista para 2 nomes
    #     não é bloqueada (com 2 candidatos em comum a re-normalização é ruidosa
    #     demais: falso positivo pularia de 2,3% para 8,7% no dado real). Ela sai
    #     marcada corroborada=False, e o teste TRAVA esse comportamento para que
    #     ninguém o mude sem perceber.
    print("\n3b. limite declarado: forjadura com lista encolhida")
    curta = forjar(modelo, "PRES", 95.0, manter_lista=False)
    curta["id"] = "FORJADA-CURTA"
    rep3b = {}
    ac3b, quar3b = ip.plausibility_gate(json.loads(json.dumps(polls)) + [curta], ids, rep3b)
    achou = [p for p in ac3b if p["id"] == "FORJADA-CURTA"]
    check("não bloqueia (limite conhecido)", not any(q["id"] == "FORJADA-CURTA" for q in quar3b))
    check("mas sai marcada corroborada=False",
          bool(achou) and achou[0].get("corroborada") is False)

    # 4. ERRO PLANTADO: sanidade absoluta (roda mesmo sem consenso).
    print("\n4. erro plantado: sanidade absoluta")
    casos = [
        ("pct fora de [0,100]", forjar(modelo, "PRES", 180.0)),
        ("amostra implausível", forjar(modelo, "PRES", 40.0, amostra=99000000)),
        ("soma acima do teto da base",
         dict(json.loads(json.dumps(modelo)), id="FORJADA-SOMA", base="normalizada_100",
              numeros=[{"sq": 1, "alias": "A", "pct": 99.0},
                       {"sq": 2, "alias": "B", "pct": 99.0}])),
    ]
    for nome, p in casos:
        v = ip.sanity_violations(p)
        check(f"sanidade pega: {nome}", bool(v), v[0][:58] if v else "passou batido")

    # 5. Corrida SEM base comparável não é bloqueada, mas viaja marcada.
    #     O cenário é CONSTRUÍDO, não caçado no dado real. Até 18/09/2026 este caso
    #     usava GOV-RR como exemplo de "corrida pouco pesquisada"; GOV-RR cresceu
    #     para 14 pesquisas e o teste passou a reprovar por premissa vencida, não
    #     por bug. Pior: hoje NENHUMA corrida real tem menos que GATE_MIN_BASE (o
    #     mínimo observado é 10), então o cenário simplesmente não existe mais no
    #     dado. Teste de comportamento do gate não pode depender de qual corrida
    #     está magra neste mês, senão ele envelhece sozinho de novo.
    print("\n5. corrida sem base: não bloqueia, declara")
    RACE5 = "GOV-XX-TESTE"          # corrida inexistente: base garantidamente vazia
    irmas = []
    for k in range(ip.GATE_MIN_BASE - 1):   # menos que o mínimo = base fraca
        irma = forjar(modelo, RACE5, 40.0)
        irma["id"] = f"IRMA-{RACE5}-{k}"
        irma["campo_fim"] = "2026-01-0%d" % (k + 1)
        irma["amostra"] = 800
        irmas.append(irma)
    nova5 = forjar(modelo, RACE5, 70.0)
    nova5["amostra"] = 800
    ids5 = ids | {x["id"] for x in irmas}     # as irmãs são "já publicadas"
    rep5 = {}
    ac5, quar5 = ip.plausibility_gate(
        json.loads(json.dumps(polls)) + irmas + [nova5], ids5, rep5)
    entrou = [q for q in ac5 if q["id"] == "FORJADA-" + RACE5]
    check(f"entra (não some do site) [base de {len(irmas)}, mínimo {ip.GATE_MIN_BASE}]",
          bool(entrou) and not quar5, f"{len(quar5)} em quarentena")
    check("marcada corroborada=False",
          bool(entrou) and entrou[0].get("corroborada") is False,
          f"corroborada={entrou[0].get('corroborada') if entrou else 'ausente'}")

    # 5b. TOLERÂNCIA DECLARADA do modo interseção, travada por teste.
    #     Em corrida COM base mas cenário divergente, o gate compara sobre a
    #     interseção re-normalizada com limiar de 40pp (calibrado no C0-c: p99 = 42pp
    #     nesse modo). Consequência medida em 18/09: uma forjadura que dá 70% ao
    #     líder do GOV-RR desvia 27,7pp e PASSA, marcada corroborada=True. Não é
    #     regressão, é o preço da calibragem, e fica escrito aqui para que baixar o
    #     limiar seja uma decisão consciente e não um efeito colateral.
    print("\n5b. tolerância declarada do modo interseção")
    rr = [p for p in polls if p["race"] == "GOV-RR"]
    if rr:
        f_rr = forjar(rr[-1], "GOV-RR", 70.0)
        f_rr["amostra"] = 800
        ac5b, quar5b = ip.plausibility_gate(json.loads(json.dumps(polls)) + [f_rr], ids, {})
        e5b = [p for p in ac5b if p["id"] == "FORJADA-GOV-RR"]
        s_ = ip._shares(f_rr)
        base_rr = [p for p in polls if p["race"] == "GOV-RR"
                   and (p["campo_fim"] or "") <= (f_rr["campo_fim"] or "")]
        _, largo = ip._consenso(f_rr, base_rr, s_)
        pior = ip._pior_desvio(s_, largo[0], intersecao=True)[0] if largo else None
        check("desvio medido fica abaixo do limiar de interseção",
              pior is not None and pior < ip.GATE_DEV_INTER_PP,
              f"{pior:.1f}pp vs limiar {ip.GATE_DEV_INTER_PP:.0f}pp; "
              f"entrou corroborada={e5b[0].get('corroborada') if e5b else None}")

    # 6. Determinismo: mesma entrada, mesma saída.
    print("\n6. determinismo")
    a = ip.plausibility_gate(json.loads(json.dumps(polls)), set(), {})[0]
    b = ip.plausibility_gate(json.loads(json.dumps(polls)), set(), {})[0]
    check("duas execuções são idênticas",
          [p["id"] for p in a] == [p["id"] for p in b])

    # 7. ERRO PLANTADO: subpágina FORJADA não pode virar fonte (risco R1).
    #     Cenário do atacante, passo a passo: ele cria um artigo novo cujo título
    #     é subpágina do artigo vigiado (a Wikipédia permite, e o artigo novo
    #     nasce sem observadores), e faz UMA edição de uma linha no artigo
    #     vigiado apontando um hatnote para lá. Sem a allowlist, o ingest segue
    #     e trata as wikitables dele como pesquisa da corrida.
    print("\n7. erro plantado: subpágina forjada apontada por hatnote")

    class _W:                      # walker mínimo: o gate só lê .hatnotes
        def __init__(self, hatnotes):
            self.hatnotes = hatnotes

    mae = ip.PRES_TITLE
    forjada = mae + "/Pesquisas recentes"          # nome plausível, criado hoje
    legitima = (mae + "/Primeiro Turno/2023-2025")  # está na allowlist
    alheio = "Pesquisas de opinião para a eleição presidencial no Brasil em 2022"
    w = _W([(["Primeiro turno", "2026", None], [legitima, forjada, alheio])])

    permitidas = ip.subpaginas_permitidas()
    check("a allowlist versionada tem conteúdo", bool(permitidas),
          f"{len(permitidas)} autorizada(s)")

    rep7 = {}
    seguidas = [t for t, _ in ip.subpaginas(w, mae, permitidas, rep7)]
    desconhecidas = rep7.get("subpaginas_desconhecidas") or []
    check("gate NÃO segue a subpágina forjada", forjada not in seguidas,
          "seguiu" if forjada in seguidas else "recusou")
    check("e a REPORTA, para derrubar o run em vez de silenciar",
          any(forjada in d for d in desconhecidas), f"{len(desconhecidas)} reportada(s)")
    check("segue a subpágina legítima (senão a trava mataria a correção)",
          legitima in seguidas)
    check("prefixo ainda barra artigo alheio, sem nem reportar como subpágina",
          alheio not in seguidas and not any(alheio in d for d in desconhecidas))

    # 7b. Allowlist vazia ou ausente é FAIL-CLOSED: nada autorizado, não tudo.
    print("\n7b. allowlist vazia não pode virar 'libera tudo'")
    rep7b = {}
    seguidas_vazio = [t for t, _ in ip.subpaginas(w, mae, set(), rep7b)]
    check("com lista vazia, nenhuma subpágina é seguida", not seguidas_vazio,
          f"{len(seguidas_vazio)} seguida(s)")
    check("e as duas subpáginas viram desconhecidas",
          len(rep7b.get("subpaginas_desconhecidas") or []) == 2)

    print()
    if FALHAS:
        print(f"REPROVADO: {len(FALHAS)} falha(s): {', '.join(FALHAS)}")
        sys.exit(1)
    print(f"OK: gate de plausibilidade validado (limiar {ip.GATE_DEV_PP:.0f}pp, "
          f"jaccard {ip.GATE_JACCARD}, base mín. {ip.GATE_MIN_BASE}).")


if __name__ == "__main__":
    main()
