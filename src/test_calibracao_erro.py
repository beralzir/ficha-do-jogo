#!/usr/bin/env python3
"""Testes da calibração do erro sistemático (M4, Fase D).

Regra da casa: gate só vale com ERRO PLANTADO. Aqui há três provas.

EXTERNA: o resultado apurado de 2018 e 2022 é fato público e verificável fora
deste repositório. O caso 2 exige os quatro números exatos. Parser que se quebrar
numa reedição da página muda esses números e o gate reprova, em vez de recalibrar
o site em silêncio em cima de lixo.

PLANTADA: as duas armadilhas que de fato morderam no desenvolvimento, e que são
sutis porque produzem número plausível em vez de erro:
  - a linha "Eleitores aptos a votar" (100%) lida como candidato, que destruiu a
    normalização na primeira execução e deu erro de 45pp;
  - a linha "Eleições de 2014" (n = 115 milhões) no fim das tabelas de 2018, que
    cai dentro da janela da última semana porque a data é reescrita com o ano da
    seção.

DE COERÊNCIA: o número que o modelo usa tem de ser o número que a calibração
produziu. Calibração que existe no disco e não chega ao modelo é teatro.

Usa rede? Não. Lê o extrato congelado em historico_2018_2022.json.

Uso:  python3 src/test_calibracao_erro.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ingest_historico as ih  # noqa: E402

ROOT = os.path.join(HERE, "..")
FALHAS = []

# Resultado oficial, em % dos votos válidos. Fato público, verificável fora daqui.
OFICIAL = {
    "2018-1T": {"bolsonaro": 46.03, "haddad": 29.28, "gomes": 12.47, "alckmin": 4.76},
    "2018-2T": {"bolsonaro": 55.13, "haddad": 44.87},
    "2022-1T": {"lula": 48.43, "bolsonaro": 43.20, "tebet": 4.16, "gomes": 3.04},
    "2022-2T": {"lula": 50.90, "bolsonaro": 49.10},
}


def check(nome, cond, detalhe=""):
    print(f"  {'ok  ' if cond else 'FALHA'} {nome}" + (f"  ({detalhe})" if detalhe else ""))
    if not cond:
        FALHAS.append(nome)


def main():
    if not os.path.exists(ih.BRUTO):
        print(f"REPROVADO: {os.path.relpath(ih.BRUTO, ROOT)} não existe. O extrato "
              f"congelado é o que torna a calibração auditável.", file=sys.stderr)
        sys.exit(1)
    bruto = json.load(open(ih.BRUTO, encoding="utf-8"))
    cal = json.load(open(ih.OUT, encoding="utf-8"))
    print(f"extrato de {bruto['acesso']} · {len(bruto['rodadas'])} rodadas · "
          f"{sum(r['n'] for r in bruto['rodadas'])} pesquisas na janela\n")

    # 1. proveniência
    print("1. proveniência")
    check("revid gravado para cada fonte",
          all("revid" in v and v["revid"] for v in bruto["fontes"].values()),
          f"{len(bruto['fontes'])} páginas")
    check("as 4 rodadas estão presentes",
          sorted(r["rodada"] for r in bruto["rodadas"]) == sorted(OFICIAL))
    check("a métrica pré-especificada viaja no arquivo",
          "pré-especificada" in cal.get("metrica_pre_especificada", "") or
          len(cal.get("metrica_pre_especificada", "")) > 100)
    check("as ressalvas viajam junto", len(cal.get("ressalvas", [])) >= 5,
          f"{len(cal.get('ressalvas', []))}")
    # insensível a caixa de propósito: a asserção já falhou duas vezes por
    # 'CONSTRUÇÃO' contra 'construção', que é ruído e não defeito.
    check("declara que a média é zero POR CONSTRUÇÃO",
          "constru" in cal["erro_sistematico"]
          .get("media_e_zero_por_construcao", "").lower())

    # 2. ÂNCORA EXTERNA: o apurado é fato público
    print("\n2. âncora externa: o resultado apurado de 2018 e 2022")
    for rid, esperado in OFICIAL.items():
        got = bruto["resultado_oficial"][rid]
        for cand, pct in esperado.items():
            check(f"{rid} {cand} = {pct}%", abs(got.get(cand, -1) - pct) < 0.005,
                  f"lido {got.get(cand)}")

    # 3. ERRO PLANTADO: as linhas de contabilidade não podem virar candidato
    print("\n3. erro plantado: contabilidade lida como candidato")
    contabeis = ["Total de votos válidos", "Votos em branco", "Votos nulos",
                 "Votos pendentes", "Total", "Abstenções", "Não apurado",
                 "Eleitores aptos a votar"]
    for nome in contabeis:
        check(f"{nome!r} NÃO é candidato", not ih.RE_CAND.search(nome))
    for nome in ["Jair Bolsonaro (PSL)", "Lula (PT)", "Simone Tebet (MDB)"]:
        check(f"{nome!r} É candidato", bool(ih.RE_CAND.search(nome)))
    for rid, got in bruto["resultado_oficial"].items():
        check(f"{rid} sem candidato de 100% (a armadilha do eleitorado)",
              not any(v >= 99.9 for v in got.values()),
              f"máx {max(got.values()):.2f}%")

    # 4. ERRO PLANTADO: a linha "Eleições de 2014" das tabelas de 2018
    print("\n4. erro plantado: a linha de resultado apurado dentro da tabela")
    for txt in ["Eleições de 2014", "Eleições de 2018", "Resultado apurado"]:
        check(f"{txt!r} é descartado", bool(ih.RE_NAO_PESQUISA.search(txt)))
    check("'Globo e Folha/Datafolha' NÃO é descartado",
          not ih.RE_NAO_PESQUISA.search("Globo e Folha/Datafolha"))
    r18 = next(r for r in bruto["rodadas"] if r["rodada"] == "2018-1T")
    check("o descarte dessa armadilha aconteceu de verdade em 2018-1T",
          any("armadilha" in k for k in r18["descartes"]), f"{r18['descartes']}")
    for r in bruto["rodadas"]:
        gordas = [p for p in r["pesquisas"] if (p["amostra"] or 0) > ih.AMOSTRA_MAX]
        check(f"{r['rodada']} sem amostra absurda", not gordas,
              f"máx {max((p['amostra'] or 0) for p in r['pesquisas']):,}")

    # 5. a janela é a pré-especificada, e não inclui o dia da urna
    print("\n5. a janela")
    for r in bruto["rodadas"]:
        ini, fim = r["janela"]
        dentro = all(ini <= p["campo_fim"] <= fim for p in r["pesquisas"])
        check(f"{r['rodada']}: toda pesquisa dentro de {ini}..{fim}", dentro)
        check(f"{r['rodada']}: janela termina antes da urna ({r['eleicao']})",
              fim < r["eleicao"])
    check("janela é de 7 dias", bruto["janela_dias"] == 7)

    # 6. COERÊNCIA: o que a calibração produziu é o que o modelo usa
    print("\n6. o modelo usa o número da calibração")
    rec = cal["erro_sistematico"]["recomendacao_ERRO_ELEICAO"]
    cfg = json.load(open(os.path.join(ROOT, "data", "eleicoes", "model_configs.json"),
                         encoding="utf-8"))
    usado = cfg["models"]["v2_estado"]["params"]["ERRO_ELEICAO"]
    check("ERRO_ELEICAO do model_configs = recomendação da calibração",
          abs(usado - rec) < 1e-9, f"config {usado} vs calibração {rec}")
    import eleicoes_model_v2 as v2
    check("o default do módulo também acompanha",
          abs(v2.DEFAULTS_V2["ERRO_ELEICAO"] - rec) < 1e-9,
          f"módulo {v2.DEFAULTS_V2['ERRO_ELEICAO']}")
    check("a recomendação é plausível (0,5pp a 6pp)", 0.005 <= rec <= 0.06,
          f"{rec*100:.2f}pp")

    # 7. o padrão conhecido: a direita subestimada em 2018 e 2022
    print("\n7. sanidade: reproduz o padrão conhecido do período")
    erros = {r["rodada"]: r["erro_do_agregado_pp"] for r in cal["rodadas"]}
    check("Bolsonaro subestimado no 1º turno de 2018", erros["2018-1T"]["bolsonaro"] < 0,
          f"{erros['2018-1T']['bolsonaro']:+.2f}pp")
    check("Bolsonaro subestimado no 1º turno de 2022", erros["2022-1T"]["bolsonaro"] < 0,
          f"{erros['2022-1T']['bolsonaro']:+.2f}pp")
    check("o bloco 'dir' sai subestimado no agregado",
          cal["vies_por_bloco_pp"]["dir"]["medio_pp"] < 0,
          f"{cal['vies_por_bloco_pp']['dir']['medio_pp']:+.2f}pp")
    check("o 2º turno é mais previsível que o 1º",
          cal["erro_sistematico"]["sd_por_turno_pp"]["2T"] <
          cal["erro_sistematico"]["sd_por_turno_pp"]["1T"],
          f"{cal['erro_sistematico']['sd_por_turno_pp']}")

    # 8. determinismo do recálculo offline
    print("\n8. determinismo")
    antes = open(ih.OUT, encoding="utf-8").read()
    _stdout, sys.stdout = sys.stdout, open(os.devnull, "w")   # o recálculo imprime
    try:
        ih.calibrar(bruto)
    finally:
        sys.stdout.close()
        sys.stdout = _stdout
    check("recalcular offline dá arquivo byte-idêntico",
          antes == open(ih.OUT, encoding="utf-8").read())

    print()
    if FALHAS:
        print(f"REPROVADO: {len(FALHAS)} falha(s): {', '.join(FALHAS)}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: calibração validada · ERRO_ELEICAO = {rec:.4f} ({rec*100:.2f}pp), "
          f"com origem em {sum(r['n'] for r in bruto['rodadas'])} pesquisas de 2018 e 2022.")


if __name__ == "__main__":
    main()
