#!/usr/bin/env python3
"""
Competidor `v2_estado` · Eleições 2026 (M1 da Fase D): filtro de Kalman de nível
local com efeitos fixos por instituto.

Só stdlib, determinístico, sem rede, como o resto do repo.

POR QUE ESTE MODELO
-------------------
O agregador oficial (`eleicoes_model.py`) estima o nível MÉDIO das últimas ~3
semanas (média ponderada por recência). Este estima o nível DE HOJE e a
velocidade com que ele se move, separando três fontes de variação que a média
ponderada mistura:

    pesquisa = nível latente + viés do instituto + erro amostral + ruído extra

O leaderboard de 21/09 (19 freezes, 824 comparações) mostra as cinco variantes do
oficial dentro de 0,3 milésimo de MAE: mexer em meia-vida, piso e house effect
não discrimina. Um competidor estruturalmente diferente é a única forma de o
harness medir alguma coisa. É por isso que este arquivo troca A AGREGAÇÃO e nada
mais: o Monte Carlo, o 2º turno, a regra do Senado, a correlação nacional e os
invariantes continuam sendo os do oficial, por injeção (`em.simulate(...,
aggregator=...)`). Duplicá-los faria o competidor divergir por motivo errado, e o
leaderboard mediria a duplicação em vez da modelagem.

MÉTODO
------
Estado escalar por candidato, em logit do share:

    nível:      mu_t = mu_{t-1} + w_t,      w_t ~ N(0, q)     (passeio aleatório)
    observação: y_it = mu_t + d_j(i) + v_it, v_it ~ N(0, r_it)

  - y_it  = logit do share do candidato na pesquisa i, com a normalização do
            oficial (`em.poll_shares`: share entre os casados, invariante à base
            do Senado). Reaproveitada de propósito, para não haver duas
            definições de share no repo.
  - d_j   = viés do instituto j, soma zero, por iteração de ponto fixo: roda o
            filtro, mede o resíduo médio de cada instituto, encolhe para zero em
            proporção ao n dele, repete.
  - r_it  = 1/(n_ef · p(1-p)) + S_EXTRA²  (delta method na binomial + ruído não
            amostral). n_ef = amostra / DEFF.
  - q     = SIGMA_RW², variância diária do passeio.

AUSÊNCIA != ZERO (diferença declarada em relação ao oficial). O oficial trata
candidato que não aparece numa pesquisa como 0,0% naquela pesquisa. Aqui a
ausência é DADO FALTANTE: a linha não entra no filtro. Em logit não há
alternativa honesta (logit(0) não existe), e para um modelo de estado é a
semântica certa: candidato que entrou na disputa em agosto não tem nível zero em
janeiro, tem nível desconhecido. Candidato ausente de TODAS as pesquisas da
corrida sai com share 0,0, igual ao oficial.

ZERO PUBLICADO É CENSURA, NÃO MEDIÇÃO. Instituto que publica 0% para um candidato
está dizendo "abaixo do arredondamento", não "o nível é zero". Medido no nosso
dado: 15,4% das observações da presidencial são exatamente 0,0%. Tratá-las pelo
clamp numérico de 1e-4 punha cada uma em -9,21 em logit, a 4,62 de distância de
1%, e o filtro lia isso como movimento violento. Efeito visível: o detector do M2
acusava z de 10 a 18 em candidatos de ~0% cujo nível mal se movia (0,01 p.p.).
O tratamento correto é o PONTO MÉDIO DO INTERVALO DE CENSURA: com percentual
publicado em inteiro, 0% significa [0 ; 0,5%), cujo meio é 0,25%. PCT_FLOOR sai
daí, não de ajuste: é a precisão declarada da fonte.

CALIBRAÇÃO DOS HIPERPARÂMETROS
------------------------------
Os defaults vêm de `pesquisa/calibrar.py` (numpyro/NUTS), rodado FORA do repo em
21/09/2026 sobre o polls.json com campo até 20/09 (133 pesquisas de 2º turno, 19
institutos). O ambiente bayesiano NÃO entra aqui: quebra o zero-dep e não é
preciso, porque a versão stdlib reproduz a bayesiana com 0,16 p.p. de erro médio
na série e correlação 0,997 nos vieses de casa.

Recalibrar 1x/MÊS e CONGELAR o valor entre calibrações. Reestimar a cada rodada
faria o competidor virar um modelo diferente todo dia, e o walk-forward pararia
de medir a mesma coisa. Os valores usados viajam no campo `params` do freeze,
que é o que torna a medição auditável depois.

ERRO_ELEICAO NÃO É MAIS CHUTE (M4, 21/09/2026). Era 2,5 p.p. sem procedência;
`src/ingest_historico.py` estimou 2,55 p.p. das quatro rodadas presidenciais
brasileiras de 2018 e 2022, com 65 pesquisas na última semana antes da urna. O
chute estava quase certo, e agora tem origem auditável.

Uso:
    python3 src/eleicoes_model_v2.py            # roda e imprime a presidencial
    python3 src/eleicoes_model_v2.py --freeze   # grava o freeze no schema do harness
    python3 src/eleicoes_model_v2.py --full     # roda as 55 corridas e checa invariantes
"""
import datetime as dt
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)

import eleicoes_model as em  # noqa: E402

MODEL_ID = "v2_estado"

DEFAULTS_V2 = dict(
    SIGMA_RW=0.0131,     # desvio diário do passeio, em logit (estimado)
    S_EXTRA=0.0197,      # ruído não amostral por pesquisa, em logit (estimado)
    DEFF=1.6,            # efeito de desenho: n_efetivo = amostra / DEFF (estimado)
    TAU_HOUSE=0.0697,    # escala do encolhimento do viés de casa, em logit (estimado)
    N_ITER_HOUSE=5,
    # ESTIMADO pelo M4 em 2018 e 2022 (src/ingest_historico.py), não mais chutado:
    # desvio do erro do agregado no 1º turno, 4 rodadas, 65 pesquisas da última
    # semana antes da urna. Ver data/eleicoes/calibracao_erro.json.
    ERRO_ELEICAO=0.0255,
    # Piso numérico do desvio, NÃO o FLOORPP=3,0 do oficial. Um piso de 3pp
    # dominaria a incerteza do filtro na presidencial e o competidor voltaria a
    # ser o oficial com outro nome, que é justamente o que o leaderboard já
    # mostrou não discriminar. 0,5pp existe só para o Monte Carlo não degenerar.
    FLOORPP_V2=0.5,
    # M2, detector de salto por resíduo padronizado. 3 sigma é o que os
    # agregadores clássicos usam. NÃO baixar: se der falso positivo em corrida
    # pequena, o remédio é exigir corroboração por dois institutos (campo
    # `corroborado` do inflexoes.json), não afrouxar o limiar.
    Z_SALTO=3.0,
    JANELA_SALTO=3,      # dias à frente para medir a variação de NÍVEL
    # Ponto médio do intervalo de censura de um 0% publicado em inteiro:
    # [0 ; 0,5%) tem meio em 0,25%. Ver docstring do módulo. NÃO é ajuste fino.
    PCT_FLOOR=0.0025,
    # M5, prior de reputação por instituto. NASCE DESLIGADO de propósito: o
    # `v2_estado` já tem freeze congelado, e ligar o prior nele faria o
    # competidor virar outro modelo no meio da medição, que é exatamente o que
    # a regra de recalibração acima proíbe. Quem liga é o competidor NOVO
    # `v2_prior` no model_configs.json, e aí o leaderboard mede se o M5 ajuda
    # em vez de a gente supor que ajuda.
    PRIOR_INST=0,
)

# cache do prior do M5: lido uma vez por processo. None = ainda não tentou.
_PRIOR_CACHE = None


def prior_institutos():
    """{instituto: {bloco: viés em logit}} do M5, ou {} se o arquivo não existe.

    Falha ABERTA de propósito, ao contrário dos gates: prior ausente significa
    encolher para zero, que é o comportamento de sempre. Um competidor não pode
    derrubar o pipeline por causa de um arquivo de diagnóstico que só ele lê.
    """
    global _PRIOR_CACHE
    if _PRIOR_CACHE is None:
        caminho = os.path.join(ROOT, "data", "eleicoes", "prior_institutos.json")
        try:
            with open(caminho, encoding="utf-8") as f:
                doc = json.load(f)
            _PRIOR_CACHE = {i: v["prior_logit"]
                            for i, v in sorted(doc.get("prior", {}).items())}
        except (OSError, ValueError, KeyError):
            _PRIOR_CACHE = {}
    return _PRIOR_CACHE


def _p(params, nome):
    return params.get(nome, DEFAULTS_V2[nome])


def logit(p):
    p = min(max(p, 1e-4), 1 - 1e-4)
    return math.log(p / (1 - p))


def expit(x):
    return 1.0 / (1.0 + math.exp(-x))


# ---------------------------------------------------------------------------
# Filtro de Kalman escalar + suavizador RTS
# ---------------------------------------------------------------------------

def kalman_smooth(obs_por_dia, n_dias, q, mu0, p0):
    """obs_por_dia: {t: [(y, r, tag), ...]}. Devolve (mu[t], var[t], residuos).

    Filtro para frente, suavizador RTS para trás. Múltiplas observações no mesmo
    dia entram em sequência (equivalente a uma atualização conjunta). O resíduo
    devolvido é a inovação PADRONIZADA, (y - previsão)/sqrt(S), com o `tag` da
    observação junto: é o insumo do detector de salto do M2, e sem o tag não dá
    para exigir corroboração por DOIS institutos diferentes, que é o remédio que
    o plano manda usar no lugar de baixar o limiar.
    """
    mu_f = [0.0] * n_dias
    p_f = [0.0] * n_dias
    mu_p = [0.0] * n_dias
    p_p = [0.0] * n_dias
    resid = []

    m, v = mu0, p0
    for t in range(n_dias):
        if t > 0:
            v = v + q                     # predição (matriz de transição = 1)
        mu_p[t], p_p[t] = m, v
        for (y, r, tag) in obs_por_dia.get(t, []):
            s = v + r                     # variância da inovação
            resid.append((t, (y - m) / math.sqrt(s), tag))
            k = v / s                     # ganho de Kalman
            m = m + k * (y - m)
            v = (1 - k) * v
        mu_f[t], p_f[t] = m, v

    mu_s = list(mu_f)
    p_s = list(p_f)
    for t in range(n_dias - 2, -1, -1):
        if p_p[t + 1] <= 0:
            continue
        c = p_f[t] / p_p[t + 1]
        mu_s[t] = mu_f[t] + c * (mu_s[t + 1] - mu_p[t + 1])
        p_s[t] = p_f[t] + c * c * (p_s[t + 1] - p_p[t + 1])
    return mu_s, p_s, resid


def estimar_house(linhas, n_dias, params, prior=None):
    """Ponto fixo: filtra, mede o resíduo médio por instituto, encolhe, repete.

    `linhas`: [(t, instituto, y, r), ...] já em logit. Devolve {instituto: viés},
    com média ponderada zero (identificação: sem isso o nível e os vieses não são
    separáveis, só a soma deles é).

    `prior` (M5): {instituto: viés histórico em logit} JÁ NO BLOCO deste
    candidato. É o ALVO do encolhimento. Sem ele (o default), o alvo é zero e
    instituto com poucas pesquisas perde o viés inteiro, que é o comportamento
    de antes do M5. Instituto ausente do prior recebe 0,0, então ligar o prior
    não mexe em quem não tem histórico.
    """
    prior = prior or {}
    house = {}
    q = _p(params, "SIGMA_RW") ** 2
    tau2 = _p(params, "TAU_HOUSE") ** 2
    # precomputado fora do laço: dentro, isto era O(n²) por candidato por corrida
    cont, r_soma = {}, {}
    for (_t, inst, _y, r) in linhas:
        cont[inst] = cont.get(inst, 0) + 1
        r_soma[inst] = r_soma.get(inst, 0.0) + r
    n_total = sum(cont.values())

    for _ in range(int(_p(params, "N_ITER_HOUSE"))):
        obs = {}
        for (t, inst, y, r) in linhas:
            obs.setdefault(t, []).append((y - house.get(inst, 0.0), r, inst))
        mu, _, _ = kalman_smooth(obs, n_dias, q, mu0=0.0, p0=1.0)
        soma = {}
        for (t, inst, y, _r) in linhas:
            soma[inst] = soma.get(inst, 0.0) + (y - mu[t])
        novo = {}
        for inst in sorted(soma):                     # sorted: determinismo
            n = cont[inst]
            media = soma[inst] / n
            # encolhimento de James-Stein: instituto com poucas pesquisas vai para
            # zero. É o que impede um instituto de 1 pesquisa de ganhar um viés de
            # 3 p.p. só por ter saído num dia atípico.
            r_med = r_soma[inst] / n
            peso = tau2 / (tau2 + r_med / n)
            # M5: o que sobra do encolhimento vai para o viés HISTÓRICO do
            # instituto, não para zero. Com prior={} isto é idêntico à linha
            # anterior (peso*media + (1-peso)*0), e é assim que o v2_estado
            # continua reproduzindo os freezes dele.
            novo[inst] = peso * media + (1.0 - peso) * prior.get(inst, 0.0)
        media_geral = sum(novo[i] * cont[i] for i in sorted(novo)) / n_total
        house = {i: novo[i] - media_geral for i in sorted(novo)}
    return house


# ---------------------------------------------------------------------------
# Agregador: MESMA assinatura e MESMO contrato de retorno de em.aggregate_race
# ---------------------------------------------------------------------------

def _prior(sqs):
    k = len(sqs) or 1
    return {"mode": "prior", "mu": {sq: 1.0 / k for sq in sqs},
            "sd": {sq: 0.30 for sq in sqs}, "undecided": 0.5,
            "n_polls": 0, "freshest": None, "institutes": 0}


def aggregate_race_v2(race_key, race, plist, as_of, params):
    """Nível latente de hoje por Kalman, no contrato de `em.aggregate_race`.

    Devolve as mesmas chaves (mode, mu, sd, undecided, n_polls, freshest,
    institutes) porque quem consome é o `em.simulate()` sem saber quem produziu.
    Guarda o diagnóstico do M2 em `_saltos` e `_serie` (prefixo `_`: o simulate
    ignora, o `inflexoes.py` lê).
    """
    cands = [c for c in race["candidates"] if c["concorrendo"]]
    sqs = [c["sq"] for c in cands]
    if not plist or not sqs:
        return _prior(sqs)

    datas = sorted({p["campo_fim"] for p in plist if p["campo_fim"]})
    if not datas:
        return _prior(sqs)
    t0 = dt.date.fromisoformat(datas[0])
    n_dias = (as_of - t0).days + 1
    if n_dias < 1:
        return _prior(sqs)

    dias_eleicao = max((em.T1 - as_of).days, 0)
    extra_rw = _p(params, "SIGMA_RW") * math.sqrt(dias_eleicao)
    erro_el = _p(params, "ERRO_ELEICAO")
    piso = _p(params, "FLOORPP_V2") / 100.0

    # M5: bloco por candidato, mesma regra do simulate() oficial. O prior de
    # reputação é DIRECIONAL (o instituto puxa para um lado do espectro), então
    # ele só faz sentido lido no bloco do candidato cuja série está sendo
    # filtrada. O viés ESCALAR do histórico é zero por construção, porque os
    # shares são normalizados a 100 dos dois lados; é o direcional que informa.
    usa_prior = int(_p(params, "PRIOR_INST")) == 1
    pri = prior_institutos() if usa_prior else {}
    bloco_sq = {c["sq"]: em.BLOCO.get(c["partido"], "centro") for c in cands}

    mu, sd, saltos, serie = {}, {}, {}, {}
    for sq in sqs:
        linhas = []
        for p in plist:
            if not p["campo_fim"]:
                continue
            sh = em.poll_shares(p)
            if sq not in sh:            # AUSÊNCIA != ZERO: ver docstring do módulo
                continue
            n_ef = (p["amostra"] or 800) / _p(params, "DEFF")
            # zero publicado = censura: ponto médio do intervalo, não o clamp
            share = max(sh[sq], _p(params, "PCT_FLOOR"))
            r = 1.0 / max(n_ef * share * (1 - share), 1e-6) + _p(params, "S_EXTRA") ** 2
            t = (dt.date.fromisoformat(p["campo_fim"]) - t0).days
            if 0 <= t < n_dias:
                linhas.append((t, p["instituto"], logit(share), r))
        if not linhas:
            mu[sq], sd[sq] = 0.0, piso
            continue
        b = bloco_sq.get(sq, "centro")
        prior_b = {i: v[b] for i, v in sorted(pri.items()) if b in v} if pri else {}
        house = estimar_house(linhas, n_dias, params, prior_b)
        obs = {}
        for (t, inst, y, r) in linhas:
            obs.setdefault(t, []).append((y - house.get(inst, 0.0), r, inst))
        m, v, resid = kalman_smooth(obs, n_dias, _p(params, "SIGMA_RW") ** 2, 0.0, 1.0)
        nivel = expit(m[-1])
        # delta method para voltar de logit a share: d expit/d eta = p(1-p).
        # O passeio que falta até a eleição e o erro sistemático entram aqui,
        # porque o simulate() sorteia em share e não em logit.
        sd_logit = math.sqrt(max(v[-1], 0.0) + extra_rw ** 2)
        sd_share = nivel * (1.0 - nivel) * sd_logit
        mu[sq] = nivel
        sd[sq] = max(math.sqrt(sd_share ** 2 + erro_el ** 2), piso)
        nivel_dia = [expit(x) for x in m]
        saltos[sq] = []
        for (t, z, inst) in resid:
            if abs(z) <= _p(params, "Z_SALTO"):
                continue
            # DUAS escalas diferentes, nomeadas de propósito. O plano avisa que
            # confundi-las é fácil e que a segunda costuma ser o dobro da
            # primeira: `delta_dia_pp` é o quanto o NÍVEL saltou naquele dia, e
            # `delta_janela_pp` é a variação de nível na janela seguinte.
            d_dia = (nivel_dia[t] - nivel_dia[t - 1]) * 100 if t >= 1 else 0.0
            j = min(t + int(_p(params, "JANELA_SALTO")), n_dias - 1)
            base = max(t - 1, 0)
            d_jan = (nivel_dia[j] - nivel_dia[base]) * 100
            saltos[sq].append({
                "data": (t0 + dt.timedelta(days=t)).isoformat(),
                "z": round(z, 2),
                "instituto": inst,
                "delta_dia_pp": round(d_dia, 2),
                "delta_janela_pp": round(d_jan, 2),
            })
        serie[sq] = [round(x, 4) for x in nivel_dia]

    tot = sum(mu.values())
    if tot <= 1e-9:      # pesquisas só casaram com quem saiu da disputa
        return _prior(sqs)
    for sq in mu:
        mu[sq] /= tot

    insts = sorted({p["instituto"] for p in plist})
    freshest = max(p["campo_fim"] for p in plist if p["campo_fim"])
    und = []
    for p in plist:
        indef = p.get("indefinidos_pct") or {}
        und.append(min(((indef.get("indecisos") or 0.0) +
                        (indef.get("outros") or 0.0)) / 100.0, 0.6))
    idade = (as_of - dt.date.fromisoformat(freshest)).days
    return {"mode": "polls" if idade <= params.get("STALE_D", 120) else "prior_velho",
            "mu": mu, "sd": sd,
            "undecided": (sum(und) / len(und)) if und else 0.0,
            "n_polls": len(plist), "freshest": freshest, "institutes": len(insts),
            "_saltos": saltos, "_serie": serie, "_t0": datas[0]}


def simulate_v2(structure, polls_doc, params, verbose=True):
    """O simulate oficial com o agregador trocado. Nada mais muda."""
    return em.simulate(structure, polls_doc, params, verbose=verbose,
                       aggregator=aggregate_race_v2)


def params_v2(extra=None):
    """DEFAULTS do oficial + DEFAULTS_V2 + overrides. Uma só montagem."""
    params = dict(em.DEFAULTS)
    params.update(DEFAULTS_V2)
    params.update(extra or {})
    return params


def main():
    argv = sys.argv[1:]
    params = params_v2()
    structure = em.load(em.STRUCT)
    polls_doc = em.load(em.POLLS)

    if "--freeze" in argv:
        # Delegado ao harness de propósito: o schema do freeze, a checagem de
        # invariantes e o fail-closed de POLL_SOURCE sintético moram lá. Um
        # segundo escritor de freeze seria um segundo lugar para esquecer o
        # fail-closed, que é a classe de bug que o C3 corrigiu em 31/08.
        import eleicoes_run_models as run
        feito = run.freeze_um(MODEL_ID, structure, polls_doc,
                              {k: params[k] for k in sorted(DEFAULTS_V2)},
                              simulate_fn=simulate_v2)
        print("freeze gravado." if feito else "freeze já existia (idempotente).")
        return

    out = simulate_v2(structure, polls_doc, params, verbose=True)
    bad = em.check_invariants(out)
    print(f"invariantes: {'VERDES' if not bad else bad[:3]}")
    if "--full" in argv:
        if bad:
            sys.exit(1)
        return

    pres = out["races"]["PRES"]
    print(f"\nPRES · as_of {out['meta']['as_of']} · {pres['n_polls']} pesquisas · "
          f"{pres['institutes']} institutos · qualidade {pres['data_quality']}")
    for c in pres["candidates"][:6]:
        print(f"  {c['urna']:24s} share {c['share']:.4f}  sd {c['sd']:.4f}  "
              f"1ºT {c.get('t1_win', 0):.3f}  eleito {c['eleito']:.4f}")


if __name__ == "__main__":
    main()
