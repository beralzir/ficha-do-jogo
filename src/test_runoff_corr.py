#!/usr/bin/env python3
"""Testes da correlação 1º turno -> 2º turno (M8, Fase D, Janela 2).

Regra da casa: gate só vale com ERRO PLANTADO. São QUATRO aqui, e três deles
foram rodados no código de produção até morderem (o do M5 ensinou que provar o
erro só dentro do teste não basta):

  1. ESTIMADOR CRU, sem efeito fixo por par. É o que o plano sugeria ao pé da
     letra e é errado para este uso: a simulação mantém o par FIXO e move a
     margem de 1º turno, então a pergunta é DENTRO do par. O bloco 2 calcula os
     dois e exige que difiram na presidencial, onde há só 6 pares distintos e a
     regressão crua mede identidade de candidato.

  2. BETA ÚNICO para PRES e GOV. 0,33 contra 0,66 não são o mesmo regime. O
     bloco 3 exige que continuem separados e longe um do outro.

  3. CHAVE QUE NÃO ISOLA. Com RUNOFF_CORR=0 o número PUBLICADO não pode mudar,
     nem que o runoff_corr.json traga um beta absurdo. Este é o que protege a
     regra da casa: nada da edição Eleições muda no ar sem validação local.

  4. CORRELAÇÃO COM SINAL TROCADO. Sorteio de 1º turno mais forte tem de elevar
     a probabilidade de 2º turno daquele candidato, nunca baixar.

Usa rede? Não.

Uso:  python3 src/test_runoff_corr.py
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eleicoes_model as em          # noqa: E402
import eleicoes_runoff_corr as rc    # noqa: E402

ROOT = os.path.join(HERE, "..")
FALHAS = []


def check(nome, cond, detalhe=""):
    print(f"  {'ok  ' if cond else 'FALHA'} {nome}" + (f"  ({detalhe})" if detalhe else ""))
    if not cond:
        FALHAS.append(nome)


def main():
    doc_p = os.path.join(ROOT, "data", "eleicoes", "runoff_corr.json")
    st = json.load(open(os.path.join(ROOT, "data", "eleicoes2026_structure.json"),
                        encoding="utf-8"))
    pd = json.load(open(os.path.join(ROOT, "data", "live", "polls.json"), encoding="utf-8"))

    print("1. o arquivo da correlação")
    check("runoff_corr.json existe", os.path.exists(doc_p))
    doc = json.load(open(doc_p, encoding="utf-8")) if os.path.exists(doc_p) else {}
    check("declara quem consome", "simulate" in doc.get("consumidor", ""))
    check("declara a regra PRÉ-ESPECIFICADA", "pre_especificada" in
          json.dumps(doc, ensure_ascii=False))
    check("traz ressalvas", len(doc.get("ressalvas", [])) >= 3,
          f"{len(doc.get('ressalvas', []))}")
    # a ressalva que não pode sumir: o beta é medido em pesquisa e aplicado ao sorteio
    check("declara que aplicar o beta ao sorteio é SUPOSIÇÃO",
          any("SUPOSIÇÃO" in r for r in doc.get("ressalvas", [])))
    g = doc.get("grupos", {})

    print("\n2. ERRO PLANTADO 1: estimador cru, sem efeito fixo por par")
    polls = pd["polls"]
    linhas = rc.coleta(polls, dict(em.DEFAULTS))
    check("há pares casados de sobra", len(linhas) > 300, f"{len(linhas)} pares")
    for grupo in ("PRES", "GOV"):
        sub = [r for r in linhas if r[0] == grupo]
        dentro = rc.regride_dentro(sub)
        cru = rc.regride_entre(sub)
        check(f"{grupo}: os dois estimadores existem", dentro and cru)
    pres_d = rc.regride_dentro([r for r in linhas if r[0] == "PRES"])
    pres_c = rc.regride_entre([r for r in linhas if r[0] == "PRES"])
    raz = abs(pres_d["beta"]) / max(abs(pres_c["beta"]), 1e-9)
    check("na PRES o cru difere MUITO do dentro-do-par (o erro plantado)",
          raz > 2.0, f"dentro={pres_d['beta']:+.4f} cru={pres_c['beta']:+.4f} ({raz:.1f}x)")
    check("e o motivo está no n de pares", pres_d["n_pares"] <= 8,
          f"só {pres_d['n_pares']} pares distintos na presidencial")

    print("\n3. ERRO PLANTADO 2: beta único para PRES e GOV")
    bp = g.get("PRES", {}).get("dentro_do_par", {}).get("beta")
    bg = g.get("GOV", {}).get("dentro_do_par", {}).get("beta")
    check("os dois betas existem", bp is not None and bg is not None)
    if bp is not None and bg is not None:
        epp = g["PRES"]["dentro_do_par"]["ep"]
        epg = g["GOV"]["dentro_do_par"]["ep"]
        sep = abs(bg - bp) / math.sqrt(epp ** 2 + epg ** 2)
        check("PRES e GOV são regimes DIFERENTES (separados por 3+ erros-padrão)",
              sep > 3.0, f"{bp:+.4f} vs {bg:+.4f}, separação = {sep:.1f} ep")
        check("o motor lê os dois separados, não um só",
              sorted(em.carrega_runoff_corr()) == ["GOV", "PRES"],
              f"{em.carrega_runoff_corr()}")

    print("\n4. regra pré-especificada")
    for grupo in ("PRES", "GOV"):
        d = g.get(grupo, {})
        dd = d.get("dentro_do_par", {})
        t = abs(dd.get("beta", 0)) / max(dd.get("ep", 1e-9), 1e-9)
        coerente = d.get("usar") == (dd.get("n_obs", 0) >= rc.N_MIN and t > rc.T_MIN)
        check(f"{grupo}: o campo 'usar' obedece à regra escrita", coerente,
              f"usar={d.get('usar')} n={dd.get('n_obs')} t={t:.1f}")

    print("\n5. ERRO PLANTADO 3: a chave tem de isolar o NÚMERO PUBLICADO")
    p0 = dict(em.DEFAULTS)
    p0["NSIMS"] = 3000
    p1 = dict(p0)
    p1["RUNOFF_CORR"] = 1
    r0 = em.simulate(st, pd, p0, verbose=False)
    r0b = em.simulate(st, pd, p0, verbose=False)
    r1 = em.simulate(st, pd, p1, verbose=False)
    check("RUNOFF_CORR=0 é determinístico",
          json.dumps(r0, sort_keys=True) == json.dumps(r0b, sort_keys=True))
    check("o DEFAULT do motor é DESLIGADO", em.DEFAULTS["RUNOFF_CORR"] == 0)
    # beta absurdo no cache: com a chave desligada, a saída tem de ser a mesma
    orig = em.carrega_runoff_corr
    try:
        em.carrega_runoff_corr = lambda: {"PRES": 99.0, "GOV": 99.0}
        r0_falso = em.simulate(st, pd, dict(p0), verbose=False)
        check("RUNOFF_CORR=0 ignora até um beta de 99 (a chave isola)",
              json.dumps(r0, sort_keys=True) == json.dumps(r0_falso, sort_keys=True))
        r1_falso = em.simulate(st, pd, dict(p1), verbose=False)
        check("RUNOFF_CORR=1 REAGE ao beta falso (prova que estava lendo)",
              json.dumps(r1, sort_keys=True) != json.dumps(r1_falso, sort_keys=True))
    finally:
        em.carrega_runoff_corr = orig

    print("\n6. o que o M8 pode e o que NÃO pode mexer")
    sa = {(k, c["sq"]): c["share"] for k in sorted(r0["races"])
          for c in r0["races"][k]["candidates"]}
    sb = {(k, c["sq"]): c["share"] for k in sorted(r1["races"])
          for c in r1["races"][k]["candidates"]}
    check("o M8 NÃO toca o share (só o 2º turno, não a agregação)", sa == sb,
          f"{len(sa)} candidatos")
    dif = []
    for k in sorted(r0["races"]):
        x = {c["sq"]: c.get("eleito", 0.0) for c in r0["races"][k]["candidates"]}
        y = {c["sq"]: c.get("eleito", 0.0) for c in r1["races"][k]["candidates"]}
        for sq in sorted(x):
            if sq in y:
                dif.append(abs(x[sq] - y[sq]) * 100)
    check("o M8 MUDA P(eleito) em alguma corrida (senão não faz nada)",
          max(dif) > 1.0, f"máx {max(dif):.2f}pp")
    check("o caveat conta a verdade de cada modo",
          "não correlaciona" in r0["meta"]["caveats"][1]
          and "não correlaciona" not in r1["meta"]["caveats"][1])

    print("\n7. ERRO PLANTADO 4: sinal da correlação")
    # 1º turno mais forte tem de ELEVAR a prob de 2º turno daquele candidato.
    # Chama a função DE PRODUÇÃO, não uma cópia da fórmula escrita aqui. A 1ª
    # versão deste bloco testava a cópia, e por isso um sinal trocado no motor
    # passava batido: rodei o erro plantado e o gate ficou verde.
    f = em.runoff_prob_corrigida
    check("1º turno mais forte => 2º turno mais provável (função de produção)",
          f(0.0, 0.05, 0.0, 0.3318, 0.10) > f(0.0, 0.05, 0.0, 0.3318, -0.10),
          f"m1=+0,10 -> {f(0.0, 0.05, 0.0, 0.3318, 0.10):.3f} · "
          f"m1=-0,10 -> {f(0.0, 0.05, 0.0, 0.3318, -0.10):.3f}")
    check("beta=0 devolve exatamente a prob de hoje (compatível para trás)",
          abs(f(0.03, 0.05, 0.0, 0.0, 0.9) - f(0.03, 0.05, 0.0, 0.0, -0.9)) < 1e-15
          and abs(f(0.03, 0.05, 0.0, 0.0, 0.5)
                  - 0.5 * (1 + math.erf(0.03 / (0.05 * em.SQRT2)))) < 1e-12)
    check("m1 igual à referência não desloca nada",
          abs(f(0.03, 0.05, 0.2, 0.66, 0.2)
              - 0.5 * (1 + math.erf(0.03 / (0.05 * em.SQRT2)))) < 1e-12)
    check("o motor CHAMA a função testada, não uma cópia inline",
          "runoff_prob_corrigida(margem, sigma, m1_ref, beta, m1)" in
          open(os.path.join(HERE, "eleicoes_model.py"), encoding="utf-8").read())
    check("o sinal do beta medido é positivo nos dois regimes",
          (bp or 0) > 0 and (bg or 0) > 0, f"PRES {bp:+.4f}, GOV {bg:+.4f}")

    print("\n8. registro")
    cfg = json.load(open(os.path.join(ROOT, "data", "eleicoes", "model_configs.json"),
                         encoding="utf-8"))
    ent = cfg["models"].get("v3_runoff")
    check("v3_runoff está no model_configs.json", ent is not None)
    if ent:
        check("v3_runoff liga a correlação", ent["params"].get("RUNOFF_CORR") == 1)
        check("v3_runoff NÃO é o oficial", cfg["official"] != "v3_runoff")
        check("v3_runoff usa o motor oficial (sem engine próprio)", "engine" not in ent)
        check("declara a dúvida aberta da dupla contagem",
              "duplica" in json.dumps(ent, ensure_ascii=False).lower()
              or "duvida_aberta" in ent)
    of = cfg["models"].get(cfg["official"], {})
    check("o modelo OFICIAL declara RUNOFF_CORR=0, não herda do default",
          of.get("params", {}).get("RUNOFF_CORR") == 0,
          f"official={cfg['official']}")

    print()
    if FALHAS:
        print(f"REPROVADO: {len(FALHAS)} falha(s): {', '.join(FALHAS)}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: correlação 1T->2T validada · PRES beta={bp:+.4f}, GOV beta={bg:+.4f}, "
          f"efeito máx {max(dif):.2f}pp em P(eleito), oficial DESLIGADO.")


if __name__ == "__main__":
    main()
