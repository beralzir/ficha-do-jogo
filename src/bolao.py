#!/usr/bin/env python3
"""
Recomendador de placar do bolão (Frente 2) — escolhe o palpite que MAXIMIZA OS PONTOS
ESPERADOS pela tabela do dacopa, que NÃO é necessariamente o placar mais provável.

Tabela dacopa (confirmada 2026-06-08):
  placar exato 25 · vencedor+gols do vencedor 18 · vencedor+saldo 15 ·
  vencedor+gols do perdedor 12 · só o vencedor 10 · nada 0.   Mata-mata = x2.
  Empate real: SÓ o placar exato pontua (as faixas de 'vencedor' exigem um vencedor) -> 0 nos demais.
  Mata-mata: vale o placar ao fim da prorrogação (90+30); pênaltis NÃO contam.

λ (gols esperados) vêm das forças R_cal do modelo (results.json) + vantagem de anfitrião,
pela mesma fórmula do motor (_lams). R_cal é arredondado a 1 casa -> λ ~1e-3 de imprecisão,
irrelevante para placares inteiros.
"""
import json, math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "data")
HOSTS = {"United States", "Mexico", "Canada"}

# ── Camada de risco (só o bolão; o motor Monte Carlo NÃO usa nada disto) ──────────────
# Dixon-Coles (1997): corrige a subestimação de empates de baixa pontuação (0-0, 1-1) do
#   Poisson independente, via fator τ nas 4 células baixas. ρ típico da literatura ≈ -0.13
#   (NÃO ajustado aos nossos dados — suposição documentada; ver notas de honestidade do plano).
# Sobredispersão (Binomial Negativa; Karlis-Ntzoufras 2003): gols de futebol têm variância
#   um pouco > média -> engorda a cauda (goleadas tipo 4-1). NB_SIZE = parâmetro 'size' r;
#   r grande -> quase-Poisson. var = μ + μ²/r. Default modesto.
# Dois palpites por jogo: SEGURO = maior pontos esperados (melhor no longo prazo) · OUSADO =
#   placar MAIS PROVÁVEL (modal): você crava o exato (25/50) ou zera. Naturalmente devolve
#   empates em jogos equilibrados. (Mean-variance foi descartado: o pick de maior EV também é
#   o de maior DP, então não separava nada — medido em 2026-06-13.)
# Overrideáveis por env var (mesma convenção de MU/GOAL_DIV/HA do motor).
RHO = float(os.environ.get("DC_RHO", -0.13))
NB_SIZE = float(os.environ.get("NB_SIZE", 8.0))


def dacopa_points(guess, actual, ko=False):
    """Pontos dacopa de um palpite contra o resultado real."""
    gx, gy = guess; ax, ay = actual
    m = 2 if ko else 1
    if (gx, gy) == (ax, ay):
        return 25 * m                       # placar exato
    if ax == ay:
        return 0                            # jogo real empatado: só o exato pontua
    if gx == gy:
        return 0                            # palpitou empate num jogo decidido
    if (gx > gy) != (ax > ay):
        return 0                            # vencedor errado
    home = ax > ay
    wg_g, lg_g = (gx, gy) if home else (gy, gx)
    wg_a, lg_a = (ax, ay) if home else (ay, ax)
    if wg_g == wg_a:
        return 18 * m                       # vencedor + gols do vencedor
    if abs(gx - gy) == abs(ax - ay):
        return 15 * m                       # vencedor + saldo
    if lg_g == lg_a:
        return 12 * m                       # vencedor + gols do perdedor
    return 10 * m                           # só o vencedor


def _pois(lam, k):
    return math.exp(-lam) * lam ** k / math.factorial(k)


def _nb(mu, k, size):
    """PMF da Binomial Negativa de média `mu` e parâmetro `size` r (var = mu + mu²/r).
    r grande -> Poisson. mu>0 garantido (λ tem piso 0.15 em lams_for)."""
    r = size
    return math.exp(math.lgamma(k + r) - math.lgamma(r) - math.lgamma(k + 1)
                    + r * (math.log(r) - math.log(r + mu))
                    + k * (math.log(mu) - math.log(r + mu)))


def _marg(mu, maxg, size):
    """Marginal de gols [P(0..maxg)]: NB se size finito/positivo, senão Poisson."""
    if size is None or size <= 0 or size == float("inf"):
        return [_pois(mu, k) for k in range(maxg + 1)]
    return [_nb(mu, k, size) for k in range(maxg + 1)]


def _clamp_rho(la, lb, rho):
    """Mantém ρ na região que garante τ ≥ 0 (senão a dist teria célula negativa)."""
    lo = max(-1.0 / la, -1.0 / lb)
    hi = min(1.0 / (la * lb), 1.0)
    return max(lo, min(hi, rho))


def _tau(x, y, la, lb, rho):
    """Fator de dependência de Dixon-Coles (1997) nas 4 células de baixa pontuação."""
    if x == 0 and y == 0: return 1.0 - la * lb * rho
    if x == 0 and y == 1: return 1.0 + la * rho
    if x == 1 and y == 0: return 1.0 + lb * rho
    if x == 1 and y == 1: return 1.0 - rho
    return 1.0


def score_dist_group(la, lb, maxg=10, rho=None, size=None):
    """Distribuição de placar de 90 min, normalizada. Marginais NB (sobredispersão) +
    correção de baixa pontuação de Dixon-Coles. rho=0 e size=inf -> Poisson independente."""
    rho = _clamp_rho(la, lb, RHO if rho is None else rho)
    size = NB_SIZE if size is None else size
    pa = _marg(la, maxg, size); pb = _marg(lb, maxg, size)
    dist = {(i, j): pa[i] * pb[j] * _tau(i, j, la, lb, rho)
            for i in range(maxg + 1) for j in range(maxg + 1)}
    s = sum(dist.values())
    return {k: v / s for k, v in dist.items()}


def score_dist_ko(la, lb, maxg=10, rho=None, size=None):
    """Distribuição do placar QUE CONTA no KO = fim da prorrogação (pênaltis não contam).
    Mesma camada de risco no placar de 90' (NB + Dixon-Coles); prorrogação = λ·0.34."""
    rho = _clamp_rho(la, lb, RHO if rho is None else rho)
    size = NB_SIZE if size is None else size
    pa = _marg(la, maxg, size); pb = _marg(lb, maxg, size)
    ea = _marg(la * 0.34, maxg, size); eb = _marg(lb * 0.34, maxg, size)
    dist = {}
    for i in range(maxg + 1):                       # decidido nos 90 (i != j)
        for j in range(maxg + 1):
            if i != j:
                dist[(i, j)] = dist.get((i, j), 0) + pa[i] * pb[j] * _tau(i, j, la, lb, rho)
    for k in range(maxg + 1):                        # empate em (k,k) nos 90 -> prorrogação
        ptie = pa[k] * pb[k] * _tau(k, k, la, lb, rho)
        if ptie == 0:
            continue
        for x in range(maxg + 1 - k):
            for y in range(maxg + 1 - k):
                dist[(k + x, k + y)] = dist.get((k + x, k + y), 0) + ptie * ea[x] * eb[y]
    s = sum(dist.values())
    return {k: v / s for k, v in dist.items()}


def best_pick(dist, ko=False, max_guess=6):
    """Palpite EV-ótimo (SEGURO). Retorna (pick, ev, ranking[(pick,ev)] desc)."""
    ranking = []
    for gx in range(max_guess + 1):
        for gy in range(max_guess + 1):
            ev = 0.0
            for (ax, ay), p in dist.items():
                if p:
                    ev += p * dacopa_points((gx, gy), (ax, ay), ko)
            ranking.append(((gx, gy), ev))
    ranking.sort(key=lambda z: -z[1])
    return ranking[0][0], ranking[0][1], ranking


def lams_for(model, a, b):
    """λ de a,b a partir de R_cal + anfitrião, igual ao motor (_lams)."""
    meta = model["meta"]; HA = meta["HA"]; GD = meta["GOAL_DIV"]; MU = meta["MU"]
    R = model["teams"]
    ra = R[a]["R_cal"] + (HA if a in HOSTS else 0)
    rb = R[b]["R_cal"] + (HA if b in HOSTS else 0)
    sup = (ra - rb) / GD
    return max(0.15, MU / 2 + sup / 2), max(0.15, MU / 2 - sup / 2)


def _ev_of(pick, dist, ko):
    return sum(p * dacopa_points(pick, actual, ko) for actual, p in dist.items() if p)


def goleada_prob(dist):
    """P(diferença de gols ≥ 3) sob a distribuição — info de 'goleada' p/ exibir (não recomendar)."""
    return sum(p for (i, j), p in dist.items() if abs(i - j) >= 3)


def draw_prob(dist):
    """P(placar empatado) sob a distribuição. No KO a dist é a do fim da prorrogação — um empate
    aqui = jogo que foi decidido nos PÊNALTIS (sem somar gols). Logo isto é a P(ir aos pênaltis).
    Info p/ exibir como selo (o placar modal/Ousado segue decidido — um único placar exato não
    consegue ser empate quando a prorrogação redistribui a massa; o selo é como o empate aparece)."""
    return sum(p for (i, j), p in dist.items() if i == j)


def recommend(model, a, b, ko=False, maxg=10, max_guess=6):
    """Recomendação completa para o confronto a (mando) x b. Devolve dois palpites:
    'ev_pick' (SEGURO = maior pontos esperados) e 'bold_pick' (OUSADO = placar mais
    provável/modal; crava o exato ou zera — naturalmente devolve empates)."""
    la, lb = lams_for(model, a, b)
    dist = score_dist_ko(la, lb, maxg) if ko else score_dist_group(la, lb, maxg)
    safe_pick, safe_ev, ranking = best_pick(dist, ko, max_guess)
    ml_pick, ml_prob = max(dist.items(), key=lambda z: z[1])   # OUSADO = mais provável
    return {"a": a, "b": b, "ko": ko, "la": round(la, 3), "lb": round(lb, 3),
            "ev_pick": list(safe_pick), "ev": round(safe_ev, 2),
            "bold_pick": list(ml_pick), "bold_prob": round(ml_prob, 4),
            "bold_ev": round(_ev_of(ml_pick, dist, ko), 2),
            "bold_is_safe": list(ml_pick) == list(safe_pick),
            "ml_score": list(ml_pick), "ml_prob": round(ml_prob, 4),
            "ev_pick_is_ml": safe_pick == ml_pick,
            "goleada": round(goleada_prob(dist), 4),
            "draw": round(draw_prob(dist), 4),
            "top_ev": [[list(p), round(e, 2)] for p, e in ranking[:5]]}


def load_model(path=None):
    with open(path or f"{BASE}/wc2026_results.json") as f:
        return json.load(f)


if __name__ == "__main__":
    M = load_model()

    # (1) Dixon-Coles aumenta empates de baixa pontuação vs Poisson independente puro.
    la, lb = lams_for(M, "Brazil", "Morocco")
    pois = score_dist_group(la, lb, rho=0.0, size=float("inf"))   # baseline Poisson indep.
    dc = score_dist_group(la, lb)                                  # com τ + NB (defaults)
    print("=== (1) Dixon-Coles/NB vs Poisson (Brazil x Morocco, λ=%.2f/%.2f) ===" % (la, lb))
    for sc in [(0, 0), (1, 1), (1, 0), (2, 0), (3, 1), (4, 1)]:
        print(f"  {sc}: Poisson {pois[sc]*100:5.2f}%  ->  DC+NB {dc[sc]*100:5.2f}%")
    assert dc[(1, 1)] > pois[(1, 1)] and dc[(0, 0)] > pois[(0, 0)], "τ deveria elevar empates baixos"
    assert abs(sum(dc.values()) - 1.0) < 1e-9, "distribuição deve somar 1"

    # (2) Seguro (maior EV) vs Ousado (placar mais provável; crava ou zera).
    print("=== (2) Seguro vs Ousado ===")
    for a, b, ko in [("Brazil", "Morocco", False), ("United States", "Paraguay", False),
                     ("Mexico", "South Africa", False), ("Spain", "France", True)]:
        r = recommend(M, a, b, ko)
        tag = "KO" if ko else "grupo"
        print(f"[{tag}] {a} x {b}: SEGURO {r['ev_pick']} (EV {r['ev']}) | "
              f"OUSADO {r['bold_pick']} (crava {r['bold_prob']*100:.1f}% · EV {r['bold_ev']})"
              f"{'  [concordam]' if r['bold_is_safe'] else ''} | goleada {r['goleada']*100:.0f}%")
        assert r["bold_ev"] <= r["ev"] + 1e-9, "Ousado (modal) não pode ter EV > Seguro (EV-ótimo)"
        assert r["bold_pick"] == r["ml_score"], "Ousado deve ser o placar mais provável"
    print("OK — invariantes do recomendador conferem.")
