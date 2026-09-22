#!/usr/bin/env python3
"""Testes do prior de reputação por instituto (M5, Fase D, Janela 2).

Regra da casa: gate só vale com ERRO PLANTADO. Aqui são TRÊS erros plantados,
um por decisão de desenho do M5, e cada um é executado lado a lado para provar
que o teste morde:

  1. PRIOR CRU (sem centragem). O viés do M4 é medido contra a URNA; o house
     effect do v2 é medido contra o CONSENSO. Usar o cru injeta o componente
     COMUM a todos os institutos, que não é viés de casa. O bloco 2 constrói o
     prior cru e exige que a média ponderada dele NÃO seja zero, enquanto a do
     prior centrado é zero. Se um dia a centragem sumir, este bloco reprova.

  2. ESCALA EM pp CONVERTIDA NO SHARE DE HOJE. É o defeito que o M2 achou:
     d(share)/d(logit) = p(1-p), então 1/(p(1-p)) explode embaixo e um candidato
     de 2% herdaria um prior medido em candidatos de 30%. O bloco 3 calcula as
     duas escalas e exige que a errada seja ordens de grandeza maior.

  3. PRIOR APLICADO SEM O (1-peso), ou aplicado com PRIOR_INST=0. Quebraria a
     compatibilidade para trás e, com ela, a validade dos freezes já congelados
     do v2_estado. O bloco 4 roda a fórmula errada ao lado e exige que ela erre.

Usa rede? Não.

Uso:  python3 src/test_prior_instituto.py
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eleicoes_model as em            # noqa: E402
import eleicoes_model_v2 as v2         # noqa: E402
import eleicoes_prior_instituto as pri  # noqa: E402

ROOT = os.path.join(HERE, "..")
FALHAS = []


def check(nome, cond, detalhe=""):
    print(f"  {'ok  ' if cond else 'FALHA'} {nome}" + (f"  ({detalhe})" if detalhe else ""))
    if not cond:
        FALHAS.append(nome)


def constroi_cru(cal):
    """ERRO PLANTADO 1: o prior SEM a centragem por bloco."""
    bl = pri.bloco_de(cal)
    bruto, n_inst = {}, {}
    for rodada in cal["rodadas"]:
        for obs in rodada["detalhe"]:
            if obs["instituto"] in pri.NAO_INSTITUTO:
                continue
            b = bl.get(obs["candidato"])
            if b is None:
                continue
            prev, apur = obs["previsto_pp"] / 100.0, obs["apurado_pp"] / 100.0
            if prev <= 0 or apur <= 0:
                continue
            i = pri.canoniza(obs["instituto"])
            bruto.setdefault(i, {}).setdefault(b, []).append(
                pri.logit(prev) - pri.logit(apur))
    out = {}
    for i in sorted(bruto):
        out[i] = {b: sum(v) / len(v) for b, v in sorted(bruto[i].items())}
        n_inst[i] = sum(len(v) for v in bruto[i].values())
    return out, n_inst


def house_referencia(linhas, n_dias, params, prior):
    """Reimplementação INDEPENDENTE do encolhimento com prior.

    Existe porque a 1ª versão deste gate não mordia: ela comparava o house com
    prior contra `house_sem_prior + prior`, que não é a referência de nenhuma das
    duas fórmulas, e por isso passava tanto na certa quanto na errada
    (`peso*media + prior`, sem o `1-peso`). O erro plantado foi rodado no código
    de produção e o gate deixou passar. Com a referência escrita aqui do zero, a
    fórmula de produção tem de bater dígito a dígito, e qualquer mexida nela
    reprova. Reusa `kalman_smooth` de propósito: o que está sob teste é o
    encolhimento, não o filtro.
    """
    q = params["SIGMA_RW"] ** 2
    tau2 = params["TAU_HOUSE"] ** 2
    cont, r_soma = {}, {}
    for (_t, inst, _y, r) in linhas:
        cont[inst] = cont.get(inst, 0) + 1
        r_soma[inst] = r_soma.get(inst, 0.0) + r
    n_total = sum(cont.values())
    house = {}
    for _ in range(int(params["N_ITER_HOUSE"])):
        obs = {}
        for (t, inst, y, r) in linhas:
            obs.setdefault(t, []).append((y - house.get(inst, 0.0), r, inst))
        mu, _, _ = v2.kalman_smooth(obs, n_dias, q, mu0=0.0, p0=1.0)
        soma = {}
        for (t, inst, y, _r) in linhas:
            soma[inst] = soma.get(inst, 0.0) + (y - mu[t])
        novo = {}
        for inst in sorted(soma):
            n = cont[inst]
            media = soma[inst] / n
            peso = tau2 / (tau2 + (r_soma[inst] / n) / n)
            # A fórmula sob teste, escrita aqui de forma independente.
            novo[inst] = peso * media + (1.0 - peso) * prior.get(inst, 0.0)
        mg = sum(novo[i] * cont[i] for i in sorted(novo)) / n_total
        house = {i: novo[i] - mg for i in sorted(novo)}
    return house


def media_ponderada(mapa, n_inst, bloco):
    num = sum(mapa[i][bloco] * n_inst[i] for i in sorted(mapa) if bloco in mapa[i])
    den = sum(n_inst[i] for i in sorted(mapa) if bloco in mapa[i])
    return (num / den) if den else 0.0


def main():
    cal = json.load(open(os.path.join(ROOT, "data", "eleicoes",
                                      "calibracao_erro.json"), encoding="utf-8"))
    doc_path = os.path.join(ROOT, "data", "eleicoes", "prior_institutos.json")

    print("1. o arquivo do prior")
    check("prior_institutos.json existe", os.path.exists(doc_path))
    doc = json.load(open(doc_path, encoding="utf-8")) if os.path.exists(doc_path) else {}
    check("declara origem no M4",
          doc.get("origem", "").endswith("calibracao_erro.json"))
    check("declara quem consome", "v2" in doc.get("consumidor", ""))
    check("traz ressalvas", len(doc.get("ressalvas", [])) >= 5,
          f"{len(doc.get('ressalvas', []))} ressalvas")
    prior = doc.get("prior", {})
    check("tem institutos", len(prior) >= 10, f"{len(prior)}")
    # todo prior_logit tem de ser finito e pequeno: house effect em logit acima
    # de ~1,0 seria maior que a própria diferença entre candidatos.
    extremos = [(i, b, v) for i in sorted(prior)
                for b, v in sorted(prior[i]["prior_logit"].items()) if abs(v) > 1.0]
    check("nenhum prior absurdo (|logit| > 1)", not extremos, f"{extremos[:3]}")

    print("\n2. ERRO PLANTADO 1: prior sem centragem")
    cru, n_inst = constroi_cru(cal)
    centrado = {i: prior[i]["vies_centrado_logit"] for i in sorted(prior)}
    # Tolerância 1e-4 e não 0: o JSON guarda o viés arredondado em 4 casas, e a
    # média ponderada de ~20 institutos arredondados carrega até meia unidade da
    # última casa. Exigir zero exato aqui reprovaria o arredondamento, não o
    # método. O que o gate exige de verdade é a razão entre cru e centrado.
    for b in ("esq", "centro", "dir"):
        m_cru = media_ponderada(cru, n_inst, b)
        m_cen = media_ponderada(centrado, n_inst, b)
        check(f"o prior CRU tem viés comum em '{b}' (o erro plantado)",
              abs(m_cru) > 1e-3, f"média ponderada = {m_cru:+.4f} logit")
        check(f"o prior CENTRADO zera o comum em '{b}'",
              abs(m_cen) < 1e-4, f"média ponderada = {m_cen:+.7f} (piso do arredondamento)")
        check(f"a centragem derruba o comum em '{b}' em 100x ou mais",
              abs(m_cen) * 100 < abs(m_cru), f"{abs(m_cru) / max(abs(m_cen), 1e-12):.0f}x menor")

    print("\n3. ERRO PLANTADO 2: escala em pp convertida no share de hoje")
    # O mesmo viés, nas duas escalas, para um candidato grande e um pequeno.
    vies_pp = 3.11 / 100.0                      # Datafolha na direita, do M4
    for p_hoje, rotulo in ((0.40, "candidato de 40%"), (0.02, "candidato de 2%")):
        errado = vies_pp / (p_hoje * (1 - p_hoje))   # delta method no share de hoje
        if rotulo.endswith("2%"):
            explode = errado
    certo = abs(prior.get("Datafolha", {}).get("prior_logit", {}).get("dir", 0.0))
    check("a conversão ERRADA explode no candidato pequeno (o erro plantado)",
          explode > 1.0, f"{explode:.3f} logit para um candidato de 2%")
    check("o método do M5 não explode", certo < 0.2,
          f"Datafolha/dir = {certo:.4f} logit, medido por observação")
    check("a errada é ordens de grandeza maior", explode > 10 * max(certo, 1e-9),
          f"{explode / max(certo, 1e-9):.0f}x")

    print("\n4. ERRO PLANTADO 3: prior aplicado sem o (1-peso)")
    linhas = [(0, "Datafolha", 0.10, 0.004), (5, "Datafolha", 0.12, 0.004),
              (2, "Zzz Desconhecido", -0.10, 0.004), (7, "Zzz Desconhecido", -0.08, 0.004)]
    params = dict(em.DEFAULTS)
    params.update(v2.DEFAULTS_V2)
    p_dir = {i: v["prior_logit"]["dir"] for i, v in sorted(prior.items())
             if "dir" in v["prior_logit"]}
    h_off = v2.estimar_house(linhas, 10, params)
    h_on = v2.estimar_house(linhas, 10, params, p_dir)
    check("sem prior, o house é o de sempre",
          abs(h_off.get("Datafolha", 0.0) - h_off.get("Zzz Desconhecido", 0.0)) > 0,
          f"gap = {h_off['Datafolha'] - h_off['Zzz Desconhecido']:+.4f}")
    check("com prior, o gap MUDA (o prior de fato morde)",
          abs((h_on["Datafolha"] - h_on["Zzz Desconhecido"])
              - (h_off["Datafolha"] - h_off["Zzz Desconhecido"])) > 1e-4,
          f"gap on = {h_on['Datafolha'] - h_on['Zzz Desconhecido']:+.4f}")
    check("o prior empurra Datafolha na direção do prior dela",
          math.copysign(1, h_on["Datafolha"] - h_off["Datafolha"]) ==
          math.copysign(1, p_dir.get("Datafolha", 0.0)),
          f"prior={p_dir.get('Datafolha', 0.0):+.4f}, "
          f"delta={h_on['Datafolha'] - h_off['Datafolha']:+.4f}")
    check("instituto SEM prior não ganha prior do nada",
          "Zzz Desconhecido" not in p_dir)
    # O DENTE do bloco: a produção tem de bater com a referência independente.
    ref = house_referencia(linhas, 10, params, p_dir)
    pior = max(abs(h_on[i] - ref[i]) for i in sorted(ref))
    check("a produção bate com a referência independente, dígito a dígito",
          pior < 1e-12, f"maior divergência = {pior:.2e}")
    # e a fórmula ERRADA (prior somado inteiro, sem o 1-peso) tem de divergir
    ref_errada = {}
    q = params["SIGMA_RW"] ** 2
    tau2 = params["TAU_HOUSE"] ** 2
    cont = {}
    r_soma = {}
    for (_t, i, _y, r) in linhas:
        cont[i] = cont.get(i, 0) + 1
        r_soma[i] = r_soma.get(i, 0.0) + r
    ntot = sum(cont.values())
    hh = {}
    for _ in range(int(params["N_ITER_HOUSE"])):
        obs = {}
        for (t, i, y, r) in linhas:
            obs.setdefault(t, []).append((y - hh.get(i, 0.0), r, i))
        mu, _, _ = v2.kalman_smooth(obs, 10, q, mu0=0.0, p0=1.0)
        soma = {}
        for (t, i, y, _r) in linhas:
            soma[i] = soma.get(i, 0.0) + (y - mu[t])
        nv = {}
        for i in sorted(soma):
            n = cont[i]
            peso = tau2 / (tau2 + (r_soma[i] / n) / n)
            nv[i] = peso * (soma[i] / n) + p_dir.get(i, 0.0)   # <- SEM o (1-peso)
        mg = sum(nv[i] * cont[i] for i in sorted(nv)) / ntot
        hh = {i: nv[i] - mg for i in sorted(nv)}
    ref_errada = hh
    div = max(abs(ref_errada[i] - ref[i]) for i in sorted(ref))
    check("a fórmula sem (1-peso) DIVERGE da certa (prova que o teste morde)",
          div > 1e-6, f"divergência = {div:.4f} logit")

    print("\n5. compatibilidade para trás (o que protege os freezes do v2_estado)")
    st = json.load(open(os.path.join(ROOT, "data", "eleicoes2026_structure.json"),
                        encoding="utf-8"))
    pd = json.load(open(os.path.join(ROOT, "data", "live", "polls.json"), encoding="utf-8"))
    base = dict(em.DEFAULTS)
    base.update(v2.DEFAULTS_V2)
    # NSIMS baixo de propósito: TUDO que este bloco compara é `share`, que sai do
    # AGREGADOR e não do Monte Carlo (em.simulate lê agg["mu"] direto). Rodar
    # 20 mil cenários seis vezes custaria 40s de pipeline para não mudar nenhum
    # dos números conferidos aqui. Quem mede efeito de MC é o leaderboard.
    base["NSIMS"] = 200
    p0 = dict(base)
    p0["PRIOR_INST"] = 0
    p1 = dict(base)
    p1["PRIOR_INST"] = 1
    r0 = v2.simulate_v2(st, pd, p0, verbose=False)
    r0b = v2.simulate_v2(st, pd, p0, verbose=False)
    r1 = v2.simulate_v2(st, pd, p1, verbose=False)
    check("PRIOR_INST=0 é determinístico",
          json.dumps(r0, sort_keys=True) == json.dumps(r0b, sort_keys=True))
    check("o DEFAULT do módulo é desligado", v2.DEFAULTS_V2["PRIOR_INST"] == 0)
    dif = []
    for k in sorted(r0["races"]):
        a = {c["sq"]: c["share"] for c in r0["races"][k]["candidates"]}
        b = {c["sq"]: c["share"] for c in r1["races"][k]["candidates"]}
        for sq in sorted(a):
            if sq in b:
                dif.append(abs(a[sq] - b[sq]) * 100)
    check("PRIOR_INST=1 MUDA a saída (senão o M5 não faz nada)",
          max(dif) > 0.05, f"máx {max(dif):.2f}pp em {len(dif)} candidatos")

    # A CHAVE tem de isolar de verdade. Este é o erro mais perigoso dos três:
    # se o prior vazar com PRIOR_INST=0, o v2_estado vira outro modelo em
    # silêncio e os freezes já congelados dele passam a medir outra coisa. A
    # primeira versão deste gate não pegava isso (rodei o erro plantado e ele
    # passou), porque nada aqui provava o ISOLAMENTO, só o efeito. Prova agora:
    # com um prior falso e ENORME no cache, PRIOR_INST=0 tem de sair idêntico.
    cache_real = v2._PRIOR_CACHE
    try:
        v2._PRIOR_CACHE = {i: {"esq": 9.0, "centro": 9.0, "dir": -9.0}
                           for i in sorted(prior)}
        r0_falso = v2.simulate_v2(st, pd, dict(p0), verbose=False)
        igual = (json.dumps(r0, sort_keys=True) == json.dumps(r0_falso, sort_keys=True))
        check("PRIOR_INST=0 ignora até um prior absurdo (a chave isola)", igual,
              "saída idêntica com prior falso de ±9 logit no cache")
        r1_falso = v2.simulate_v2(st, pd, dict(p1), verbose=False)
        check("PRIOR_INST=1 REAGE ao prior falso (prova que a chave estava lendo)",
              json.dumps(r1, sort_keys=True) != json.dumps(r1_falso, sort_keys=True))
    finally:
        v2._PRIOR_CACHE = cache_real

    print("\n6. o caminho que publica NÃO foi tocado")
    al = json.load(open(os.path.join(ROOT, "data", "eleicoes", "aliases.json"),
                        encoding="utf-8"))
    # O invariante NÃO é "os dois mapas são disjuntos": `Instituto Veritá` já
    # estava curado no aliases.json antes do M5, e repetir o par lá é correto.
    # O invariante é que o M5 não ESCREVEU no aliases.json, porque quem lê esse
    # arquivo é o ingest_polls.py, ou seja, o caminho que publica: um alias novo
    # mudaria o polls.json na próxima rodada do cron e com ele o número no ar.
    # Por isso a prova é contra o git, não contra o conteúdo.
    import subprocess
    r = subprocess.run(["git", "diff", "--name-only", "HEAD", "--",
                        "data/eleicoes/aliases.json"],
                       cwd=ROOT, capture_output=True, text=True)
    check("o M5 não escreveu no aliases.json do ingest (prova contra o git)",
          r.returncode == 0 and not r.stdout.strip(),
          "intacto" if not r.stdout.strip() else f"MODIFICADO: {r.stdout.strip()}")
    conflitos = [(k, al["institutos"][k], v) for k, v in sorted(pri.MAPA_HISTORICO.items())
                 if k in al.get("institutos", {}) and al["institutos"][k] != v]
    check("onde os dois mapas se encontram, eles concordam", not conflitos,
          f"conflitos: {conflitos}" if conflitos else
          f"{len(set(pri.MAPA_HISTORICO) & set(al.get('institutos', {})))} par(es) em comum")
    check("o maior instituto de 2026 tem prior",
          "Real Time Big Data" in prior,
          "Real Time Big Data, 161 pesquisas usáveis")
    # o oficial não pode ter herdado nada disso
    p_off = dict(em.DEFAULTS)
    p_off["NSIMS"] = 200        # idem: `share` não depende de NSIMS
    off = em.simulate(st, pd, p_off, verbose=False)
    pub = json.load(open(os.path.join(ROOT, "data", "eleicoes2026_results.json"),
                         encoding="utf-8"))
    a = {c["sq"]: c["share"] for c in off["races"]["PRES"]["candidates"]}
    b = {c["sq"]: c["share"] for c in pub["races"]["PRES"]["candidates"]}
    check("o modelo OFICIAL continua idêntico ao publicado", a == b,
          f"{len(a)} candidatos na presidencial")

    print("\n7. registro")
    cfg = json.load(open(os.path.join(ROOT, "data", "eleicoes", "model_configs.json"),
                         encoding="utf-8"))
    ent = cfg["models"].get("v2_prior")
    check("v2_prior está no model_configs.json", ent is not None)
    if ent:
        check("v2_prior liga o prior", ent["params"].get("PRIOR_INST") == 1)
        check("v2_prior NÃO é o oficial", cfg["official"] != "v2_prior")
        check("v2_prior não se declara sintético", not ent.get("sintetico"))
        check("v2_estado declara o prior DESLIGADO",
              cfg["models"]["v2_estado"]["params"].get("PRIOR_INST") == 0)
        so_muda_prior = {k: v for k, v in ent["params"].items()
                         if cfg["models"]["v2_estado"]["params"].get(k) != v}
        check("v2_prior difere do v2_estado SÓ no PRIOR_INST",
              sorted(so_muda_prior) == ["PRIOR_INST"], f"difere em: {sorted(so_muda_prior)}")

    print()
    if FALHAS:
        print(f"REPROVADO: {len(FALHAS)} falha(s): {', '.join(FALHAS)}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: prior de reputação validado · {len(prior)} institutos, "
          f"efeito máximo de {max(dif):.2f}pp, oficial intacto.")


if __name__ == "__main__":
    main()
