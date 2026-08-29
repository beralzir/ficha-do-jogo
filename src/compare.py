#!/usr/bin/env python3
"""Pontua CADA modelo do registro (data/model_configs.json) vs realidade (data/live/state.json)
e monta o leaderboard de CALIBRAÇÃO -> data/model_scores.json + tabela no terminal.

A pontuação é computada direto dos CONFIGS (não dos forecasts congelados), via um provider de λ
walk-forward (src/learn.py): para cada jogo, modelos estáticos usam força constante; modelos
'learning' usam a força da véspera (só info anterior — sem look-ahead).

Métricas (jogos de grupo já disputados):
  - Calibração 1X2: Brier + log-loss (menor = melhor). Sinal principal.
  - Acerto de placar: cravadas exatas (Seguro/EV e Ousado/modal) + pontos dacopa.
  - vs mercado: Brier(modelo) − Brier(market_only); negativo = melhor que o consenso de odds.

RESSALVAS DE HONESTIDADE (emitidas em model_scores.json["caveats"]; usar na UI da Fase D):
  1. Amostra pequena (~40/72 grupos): diferenças de Brier desta ordem estão DENTRO do ruído —
     ranking PRELIMINAR, pode mudar com mais dados ou outro torneio.
  2. Medição incompleta: só calibração de GRUPOS; avanço/título (mata-mata + fim da Copa) ainda
     não entraram — não decida apostas de finalista por este ranking.
  3. Mercado × Opta NÃO são independentes: odds (5-9/jun) coletadas DEPOIS do Opta (1/jun) e já o
     incorporam (corr ~0,98). 'market_only' é o CONSENSO DE ODDS (com Opta embutido), não 'mercado
     puro'. 'market_only bate o baseline' = 'o consenso calibra melhor que diluí-lo no blend 45/35/20'
     — NÃO refuta Opta/Elo isoladamente.
  4. Pesos pré-especificados: nada foi ajustado a estes jogos (sem p-hacking); baseline = 45/35/20.
  5. Modelos 'learning' são walk-forward (preveem cada jogo com a força da véspera). poisson_form é
     CALIBRAÇÃO-only (entra no Brier, mas não emite forecast de fase no Monte Carlo).
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bolao, learn, models as CFG, state as ST

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "model_scores.json")

# Ressalvas que VIAJAM com os dados (model_scores.json["caveats"]) e aparecem impressas.
CAVEATS = [
    "Amostra pequena (~40/72 jogos de grupo): diferenças de Brier desta ordem estão dentro do ruído estatístico — ranking PRELIMINAR, pode mudar com mais dados ou outro torneio.",
    "Medição incompleta: só calibração de grupos. Avanço/título (mata-mata + fim da Copa) ainda não entraram — não decida apostas de finalista por este ranking.",
    "market_only = consenso de odds, que já incorpora o Opta (odds coletadas depois do Opta, corr ~0,98) — não é 'mercado puro sem modelos'. 'market_only bate o baseline' = 'o consenso calibra melhor que diluí-lo no blend 45/35/20', e NÃO refuta Opta/Elo isoladamente.",
    "Pesos pré-especificados: nenhum parâmetro foi ajustado a estes jogos (sem p-hacking); baseline = fórmula histórica 45/35/20.",
    "Modelos 'learning' são walk-forward (preveem cada jogo com a força da véspera, sem look-ahead). poisson_form é calibração-only (sem forecast de fase).",
    "O ganho dos modelos 'learning' sobre o baseline (~0,0005 de Brier) é MENOR que o erro-padrão (~0,008 em n=40) — ainda é ruído. Só dá pra afirmar 'aprender ajuda' com mais jogos (72 grupos + mata-mata).",
]


def score_config(cfg, fx, state):
    """Scorecard de calibração de um config nos jogos de grupo disputados (walk-forward p/ learning)."""
    gmap = {f["match"]: f for f in fx["group"]}
    res = (state.get("results", {}) or {}).get("group", []) or []
    lams = learn.lams_provider(cfg, fx, state)
    brier = ll = 0.0
    n = seguro = ousado = exact_ev = exact_bold = 0
    for r in res:
        f = gmap[r["match"]]; a, b = f["home"], f["away"]; actual = (r["hg"], r["ag"])
        la, lb = lams(r["match"], a, b)
        dist = bolao.score_dist_group(la, lb)
        ph = sum(p for (i, j), p in dist.items() if i > j)
        pd = sum(p for (i, j), p in dist.items() if i == j)
        pa = max(0.0, 1 - ph - pd)
        p = {"H": ph, "D": pd, "A": pa}
        o = "H" if actual[0] > actual[1] else ("A" if actual[0] < actual[1] else "D")
        brier += sum((p[k] - (1.0 if k == o else 0.0)) ** 2 for k in ("H", "D", "A"))
        ll += -math.log(max(p[o], 1e-12))
        n += 1
        ev_pick = bolao.best_pick(dist, False)[0]
        ml_pick = max(dist.items(), key=lambda z: z[1])[0]
        seguro += bolao.dacopa_points(ev_pick, actual, False)
        ousado += bolao.dacopa_points(ml_pick, actual, False)
        exact_ev += 1 if tuple(ev_pick) == actual else 0
        exact_bold += 1 if tuple(ml_pick) == actual else 0
    return {
        "label": cfg["label"],
        "learning": (cfg.get("learning") or {}).get("type"),
        "n_matches": n,
        "brier": round(brier / n, 4) if n else None,
        "logloss": round(ll / n, 4) if n else None,
        "calib_n": n,
        "seguro_pts": seguro, "ousado_pts": ousado,
        "exact_ev": exact_ev, "exact_bold": exact_bold,
        "exact_ev_rate": round(exact_ev / n, 4) if n else None,
        "has_forecast": (cfg.get("learning") or {}).get("type") != "poisson_form",
    }


def build(fx, state):
    cards = {cfg["id"]: score_config(cfg, fx, state) for cfg in CFG.load_configs()}
    mkt_brier = cards.get("market_only", {}).get("brier")
    for c in cards.values():
        c["value_vs_market"] = (round(c["brier"] - mkt_brier, 4)
                                if (mkt_brier is not None and c["brier"] is not None) else None)
    return cards


def _f(x):
    return "—" if x is None else f"{x:.4f}"


def print_table(cards, n, asof):
    print(f"\n=== LEADERBOARD (PRELIMINAR) — {n} jogos de grupo (as_of {asof}) · ranqueado por Brier (menor = melhor) ===")
    print(f"{'modelo':16s}{'Brier':>8}{'logloss':>9}{'vs_mkt':>8}{'Seguro':>7}{'Ousado':>7}{'exato':>7}  tipo")
    order = sorted(cards, key=lambda m: (cards[m]["brier"] is None, cards[m]["brier"] or 0))
    for m in order:
        c = cards[m]
        vm = c["value_vs_market"]
        vm_s = "—" if vm is None else f"{vm:+.4f}"
        typ = c.get("learning") or "estático"
        exact = f"{c['exact_ev']}/{c['n_matches']}"
        print(f"{m:16s}{_f(c['brier']):>8}{_f(c['logloss']):>9}{vm_s:>8}"
              f"{c['seguro_pts']:>7}{c['ousado_pts']:>7}{exact:>7}  {typ}")
    print("vs_mkt = Brier(modelo) − Brier(market_only=consenso de odds, já c/ Opta embutido); negativo = melhor que o mercado.")
    print("tipo: 'dynamic' = força aprende (Elo) · 'poisson_form' = forma de gols (calibração-only) · 'estático' = congelado.")
    print("fase (avanço/título): medida ao fim da Copa a partir dos forecasts em data/models/ (agora: aguardando os 72 grupos).")
    print("\nRESSALVAS (n pequeno — leitura honesta):")
    for cv in CAVEATS:
        print(f"  • {cv}")


def main():
    # Depois do fechamento (finalize_scores.py), este script NÃO sobrescreve a medição final
    # com um preliminar de grupos — proteção do arquivo histórico da edição.
    if os.path.exists(OUT):
        prev = json.load(open(OUT))
        if prev.get("measurement_complete") and os.environ.get("FORCE_PRELIM") != "1":
            sys.exit("model_scores.json já é a medição FINAL (measurement_complete=true). "
                     "compare.py não sobrescreve; use FORCE_PRELIM=1 só se souber o que está fazendo.")
    fx = ST.load_fixtures()
    state = ST.ManualFileSource().load()
    errs = ST.validate_state(state, fx)
    if errs:
        sys.exit("ESTADO INVÁLIDO: " + "; ".join(errs))
    cards = build(fx, state)
    n = next(iter(cards.values()))["n_matches"]
    out = {"as_of": state.get("as_of"), "n_matches": n,
           "measurement_complete": False, "ranking": "preliminar",
           "caveats": CAVEATS, "models": cards}
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    print_table(cards, n, state.get("as_of"))
    print(f"\nescrito: {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
