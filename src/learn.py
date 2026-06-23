#!/usr/bin/env python3
"""Fase C — modelos que APRENDEM com os jogos (força que evolui durante a Copa).

Dois mecanismos, ambos WALK-FORWARD (a previsão do jogo G usa SÓ jogos ANTERIORES a G,
em ordem de data — sem look-ahead):

  type="dynamic"       — atualiza a FORÇA BLENDADA R no estilo Elo (zero-soma, K + multiplicador
                         de saldo). Parte de R0 = build_strengths(cfg) e caminha os resultados.
                         λ do jogo vem do R atualizado até a véspera. Tem forecast (run_models usa
                         o R final, condicionado ao estado ao vivo).
  type="poisson_form"  — multiplicadores de ataque/defesa por seleção, atualizados online (taxa η)
                         dos GOLS observados vs esperados. Ajusta λ direto. CALIBRAÇÃO-ONLY nesta
                         fase (não emite forecast de fase no Monte Carlo — só entra no leaderboard
                         de calibração; ver nota em run_models.py).

Interface única p/ o scorer (compare.py):
  lams_provider(cfg, fx, state) -> f(match_id, home, away) -> (la, lb)   # λ usando só info anterior

`sinal de elenco vivo` (dormant): load_squad() lê data/live/squad_signal.json (vazio => None,
sem efeito). build_strengths(cfg, qual=...) aplica o override quando um config pede.
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wc2026_model as M

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQUAD_PATH = os.path.join(ROOT, "data", "live", "squad_signal.json")


def _margin_mult(diff):
    """Multiplicador de K por saldo (estilo World Football Elo): ±1=1.0, ±2=1.5, ≥3=(11+d)/8."""
    if diff <= 1:
        return 1.0
    if diff == 2:
        return 1.5
    return (11 + diff) / 8.0


def _played_group(fx, state):
    """(jogos de grupo já disputados em ORDEM DE DATA, gmap por match). KO ignorado (λ de grupo)."""
    gmap = {f["match"]: f for f in fx["group"]}
    res = (state.get("results", {}) or {}).get("group", []) or []
    # ordena por (kickoff, match) — o match id é tiebreaker p/ jogos no mesmo horário, tornando
    # a sequência walk-forward determinística e independente da ordem de entrada no state.json.
    played = sorted(res, key=lambda r: (gmap[r["match"]]["kickoff_brt"], r["match"]))
    return played, gmap


def _lams_from_R(R, a, b, cfg):
    """λ de a (mando) x b a partir da força R + anfitrião — mesma fórmula do motor (_lams),
    parametrizada por cfg. R arredondado a 1 casa (convenção do R_cal) p/ casar com o resto."""
    ra = round(R[a], 1) + (cfg["HA"] if a in M.HOSTS else 0)
    rb = round(R[b], 1) + (cfg["HA"] if b in M.HOSTS else 0)
    sup = (ra - rb) / cfg["GOAL_DIV"]
    return max(0.15, cfg["MU"] / 2 + sup / 2), max(0.15, cfg["MU"] / 2 - sup / 2)


def dynamic_R_timeline(cfg, fx, state, qual=None):
    """before[match] = força R ANTES daquele jogo (só jogos anteriores aplicados);
    final = R após todos os jogos disputados. Atualização Elo sobre o R blendado."""
    R = M.build_strengths(cfg, qual=qual)
    played, gmap = _played_group(fx, state)
    K = float(cfg["learning"].get("K", 20.0))
    before = {}
    for r in played:
        f = gmap[r["match"]]; a, b = f["home"], f["away"]; ga, gb = r["hg"], r["ag"]
        before[r["match"]] = dict(R)  # snapshot ANTES de aplicar este jogo
        dr = (R[a] + (cfg["HA"] if a in M.HOSTS else 0)) - (R[b] + (cfg["HA"] if b in M.HOSTS else 0))
        exp_a = 1.0 / (1.0 + 10 ** (-dr / 400.0))
        res_a = 1.0 if ga > gb else (0.5 if ga == gb else 0.0)
        delta = K * _margin_mult(abs(ga - gb)) * (res_a - exp_a)
        R[a] += delta; R[b] -= delta
    return before, R


def poisson_form_timeline(cfg, fx, state, qual=None):
    """before[match] = (att, dfn) multiplicadores por time ANTES daquele jogo; final = (att,dfn).
    Online: ataque do autor e defesa do sofredor andam pela razão gols_obs/esperado (suavizada)."""
    R0 = M.build_strengths(cfg, qual=qual)
    played, gmap = _played_group(fx, state)
    eta = float(cfg["learning"].get("eta", 0.2))
    att = {t: 1.0 for t in M.TEAMS}; dfn = {t: 1.0 for t in M.TEAMS}
    before = {}
    for r in played:
        f = gmap[r["match"]]; a, b = f["home"], f["away"]; ga, gb = r["hg"], r["ag"]
        before[r["match"]] = (dict(att), dict(dfn))
        la0, lb0 = _lams_from_R(R0, a, b, cfg)
        ea = max(0.15, la0 * att[a] * dfn[b]); eb = max(0.15, lb0 * att[b] * dfn[a])
        ra_ = (ga + 0.5) / (ea + 0.5); rb_ = (gb + 0.5) / (eb + 0.5)
        att[a] *= (1 - eta) + eta * ra_; dfn[b] *= (1 - eta) + eta * ra_
        att[b] *= (1 - eta) + eta * rb_; dfn[a] *= (1 - eta) + eta * rb_
    return before, (att, dfn)


def lams_provider(cfg, fx, state, qual=None):
    """Devolve f(match_id, home, away) -> (la, lb) usando só info ANTERIOR ao jogo.
    Estático (sem learning): força constante. Learning: walk-forward."""
    learning = cfg.get("learning")
    if not learning:
        R = M.build_strengths(cfg, qual=qual)
        return lambda mid, a, b: _lams_from_R(R, a, b, cfg)
    typ = learning.get("type")
    if typ == "dynamic":
        before, _ = dynamic_R_timeline(cfg, fx, state, qual=qual)
        return lambda mid, a, b: _lams_from_R(before[mid], a, b, cfg)
    if typ == "poisson_form":
        before, _ = poisson_form_timeline(cfg, fx, state, qual=qual)
        R0 = M.build_strengths(cfg, qual=qual)

        def f(mid, a, b):
            att, dfn = before[mid]
            la0, lb0 = _lams_from_R(R0, a, b, cfg)
            return max(0.15, la0 * att[a] * dfn[b]), max(0.15, lb0 * att[b] * dfn[a])
        return f
    raise ValueError(f"learning.type desconhecido: {typ!r}")


def final_strength(cfg, fx, state, qual=None):
    """Força R 'ao vivo' (aprendida com TODOS os jogos disputados) — p/ o forecast do run_models.
    Só para type='dynamic' (poisson_form é calibração-only). None se não-learning/não-suportado."""
    learning = cfg.get("learning")
    if learning and learning.get("type") == "dynamic":
        _, R = dynamic_R_timeline(cfg, fx, state, qual=qual)
        return R
    return None


# DORMENTE — não integrado a nenhum config ainda (nenhum modelo passa qual=load_squad()).
# Ao ativar (fase futura), garanta que 'signal' contenha só info anterior (sem resultado futuro).
def load_squad(path=None):
    """Sinal de elenco vivo (DORMENTE): data/live/squad_signal.json -> {team: valor qual}.
    Arquivo ausente/vazio (ou {"signal":{}}) => None (sem efeito; build_strengths usa o qual congelado).
    Formato: {"as_of": "...", "signal": {"France": -0.15, ...}}  (mesma escala do qual: [-0.2,+0.2])."""
    p = path or SQUAD_PATH
    if not os.path.exists(p):
        return None
    with open(p) as f:
        data = json.load(f)
    sig = data.get("signal") or {}
    return sig or None


if __name__ == "__main__":
    import models, state as ST
    fx = ST.load_fixtures(); stt = ST.ManualFileSource().load()
    base = models.get("baseline")
    dyn = dict(base); dyn["id"] = "test_dynamic"; dyn["learning"] = {"type": "dynamic", "K": 20.0}

    # (1) sem look-ahead: força antes do 1º jogo == força pré-torneio (R0).
    R0 = M.build_strengths(base)
    before, final = dynamic_R_timeline(dyn, fx, stt)
    played, gmap = _played_group(fx, stt)
    m1 = played[0]["match"]
    assert all(abs(before[m1][t] - R0[t]) < 1e-9 for t in M.TEAMS), "1º jogo deve usar a força pré-torneio (sem look-ahead)"

    # (2) quem venceu sobe, quem perdeu desce (jogo 1).
    f1 = gmap[m1]; a, b = f1["home"], f1["away"]; r1 = played[0]
    if r1["hg"] != r1["ag"]:
        win, lose = (a, b) if r1["hg"] > r1["ag"] else (b, a)
        # força DEPOIS do jogo 1 = before do 2º jogo (se houver), senão final
        after = before[played[1]["match"]] if len(played) > 1 else final
        assert after[win] > R0[win] - 1e-9 and after[lose] < R0[lose] + 1e-9, "vencedor sobe, perdedor desce"

    # (3) determinismo: duas chamadas idênticas.
    b2, f2 = dynamic_R_timeline(dyn, fx, stt)
    assert all(abs(final[t] - f2[t]) < 1e-12 for t in M.TEAMS), "determinístico"

    # (4) poisson_form roda e devolve λ positivos.
    pf = dict(base); pf["id"] = "test_pf"; pf["learning"] = {"type": "poisson_form", "eta": 0.2}
    prov = lams_provider(pf, fx, stt)
    la, lb = prov(m1, a, b)
    assert la > 0 and lb > 0, "λ positivos"

    # (5) squad dormant.
    sq = load_squad()
    print(f"OK — dynamic (K=20): {win} {R0[win]:.1f}->{after[win]:.1f}, {lose} {R0[lose]:.1f}->{after[lose]:.1f} | "
          f"poisson_form λ {a}x{b} = {la:.2f}/{lb:.2f} | squad_signal: {'vazio/ausente' if not sq else len(sq)}")
