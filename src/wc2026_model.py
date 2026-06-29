#!/usr/bin/env python3
"""
2026 FIFA World Cup — ensemble Monte Carlo model.
Pipeline: market(de-vig) 45% + models(Opta/Elo) 35% + qualitative 20%
-> blended TARGET title distribution -> calibrate team strength ratings (IPF)
so a bracket-coherent simulation reproduces the target -> 50k-run Monte Carlo
-> per-stage probabilities for all 48 teams.
"""
import json, math, random, time, os
random.seed(42)
PASS0=int(os.environ.get("PASS0",6000))
CAL_ITERS=int(os.environ.get("CAL_ITERS",12))
CAL_SIMS=int(os.environ.get("CAL_SIMS",4000))
NFINAL=int(os.environ.get("NFINAL",50000))

import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE=os.path.join(ROOT,"data")
with open(f"{BASE}/worldcup2026_structure.json") as f:
    S = json.load(f)
GROUPS = S["groups"]

# --- Estado ao vivo (Frente 2): fixa jogos já ocorridos; vazio => forecast pré-torneio puro ---
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import state as _state
FIXED_GROUP, FIXED_KO, STATE_ASOF = {}, {}, None
try:
    _FX = _state.load_fixtures()
    _ST = _state.ManualFileSource(os.environ.get("STATE_FILE") or None).load()
    _ERRS = _state.validate_state(_ST, _FX)
    if _ERRS:
        print("ESTADO INVÁLIDO — abortando:")
        for _e in _ERRS:
            print("  -", _e)
        sys.exit(1)
    FIXED_GROUP, FIXED_KO = _state.build_fixed(_ST, _FX)
    STATE_ASOF = _ST.get("as_of")
    # (o aviso "Estado ao vivo" é impresso no __main__, não no import — evita ruído quando
    #  run_models.py/compare.py importam o motor como módulo)
except FileNotFoundError:
    pass  # sem fixtures.json => simulação pré-torneio

# ---------------------------------------------------------------------------
# TEAM DATA — coleta 9/jun/2026 (refresh pré-torneio; forecast anterior preservado
# em data/snapshots/2026-06-03.json).
# elo  = World Football Elo REAL (eloratings.net/World.tsv, 9/jun). CORREÇÃO DE FONTE:
#        a coleta de 1–3/jun usava aproximações que divergiam do site em até ±160 pts;
#        parte do delta deste refresh vem dessa correção, não de notícia.
# mkt  = % de título de-vigged, consenso de 6 casas com as 48 listadas
#        (FanDuel/DraftKings/bet365/Pinnacle/Unibet/Betfred, odds de 5–9/jun):
#        de-vig proporcional por casa, média entre casas, renormalizado p/ 100.
# opta = supercomputador Opta/The Analyst (números de 1/jun, artigo rev. 5/jun);
#        5 azarões com 0,0% no gráfico recebem piso 0,02 (ln(0) quebra o ensemble).
# qual = sinal qualitativo [-0.20,+0.20] curado do noticiário 4–9/jun (lesões, cortes,
#        convocações, amistosos), evitando dupla contagem com o que o mercado já precifica.
# ---------------------------------------------------------------------------
T = {
 "Spain":{"elo":2157,"mkt":14.99,"opta":16.1,"qual":0.00},
 "France":{"elo":2063,"mkt":14.26,"opta":13,"qual":-0.15},
 "England":{"elo":2021,"mkt":10.31,"opta":11.2,"qual":-0.20},
 "Brazil":{"elo":1991,"mkt":8.54,"opta":6.6,"qual":-0.20},
 "Argentina":{"elo":2114,"mkt":8.11,"opta":10.4,"qual":-0.10},
 "Portugal":{"elo":1986,"mkt":9.16,"opta":7,"qual":-0.10},
 "Germany":{"elo":1932,"mkt":5.74,"opta":5.1,"qual":-0.05},
 "Netherlands":{"elo":1948,"mkt":4.16,"opta":3.6,"qual":0.00},
 "Belgium":{"elo":1894,"mkt":2.42,"opta":2.4,"qual":0.00},
 "Norway":{"elo":1914,"mkt":2.71,"opta":3.5,"qual":-0.15},
 "Colombia":{"elo":1982,"mkt":2.19,"opta":2.1,"qual":0.05},
 "Japan":{"elo":1906,"mkt":1.5,"opta":1.2,"qual":-0.10},
 "Morocco":{"elo":1827,"mkt":1.57,"opta":1.9,"qual":0.05},
 "United States":{"elo":1726,"mkt":1.41,"opta":1.2,"qual":-0.20},
 "Uruguay":{"elo":1892,"mkt":1.21,"opta":1.7,"qual":-0.10},
 "Mexico":{"elo":1875,"mkt":1.21,"opta":1,"qual":-0.05},
 "Switzerland":{"elo":1891,"mkt":1.17,"opta":1.7,"qual":0.15},
 "Croatia":{"elo":1912,"mkt":0.99,"opta":1.6,"qual":-0.10},
 "Turkey":{"elo":1911,"mkt":0.91,"opta":0.9,"qual":0.15},
 "Ecuador":{"elo":1938,"mkt":0.89,"opta":1.4,"qual":0.20},
 "Senegal":{"elo":1860,"mkt":0.77,"opta":1,"qual":-0.15},
 "Sweden":{"elo":1712,"mkt":0.7,"opta":0.4,"qual":-0.10},
 "Austria":{"elo":1830,"mkt":0.63,"opta":0.5,"qual":0.00},
 "Canada":{"elo":1788,"mkt":0.55,"opta":0.5,"qual":-0.20},
 "Paraguay":{"elo":1834,"mkt":0.43,"opta":0.5,"qual":0.00},
 "Ivory Coast":{"elo":1695,"mkt":0.39,"opta":0.2,"qual":0.10},
 "Egypt":{"elo":1696,"mkt":0.28,"opta":0.4,"qual":-0.05},
 "Algeria":{"elo":1760,"mkt":0.23,"opta":0.2,"qual":0.10},
 "Scotland":{"elo":1782,"mkt":0.36,"opta":0.2,"qual":-0.05},
 "Czechia":{"elo":1740,"mkt":0.3,"opta":0.3,"qual":0.05},
 "Bosnia and Herzegovina":{"elo":1595,"mkt":0.26,"opta":0.3,"qual":-0.10},
 "Ghana":{"elo":1510,"mkt":0.24,"opta":0.2,"qual":-0.20},
 "South Korea":{"elo":1758,"mkt":0.25,"opta":0.4,"qual":-0.05},
 "Iran":{"elo":1772,"mkt":0.14,"opta":0.2,"qual":-0.10},
 "Tunisia":{"elo":1628,"mkt":0.15,"opta":0.1,"qual":-0.10},
 "Australia":{"elo":1777,"mkt":0.15,"opta":0.3,"qual":0.00},
 "DR Congo":{"elo":1652,"mkt":0.1,"opta":0.02,"qual":-0.10},
 "Cape Verde":{"elo":1578,"mkt":0.06,"opta":0.02,"qual":0.00},
 "Iraq":{"elo":1618,"mkt":0.06,"opta":0.1,"qual":0.05},
 "Jordan":{"elo":1680,"mkt":0.04,"opta":0.1,"qual":-0.05},
 "New Zealand":{"elo":1562,"mkt":0.05,"opta":0.1,"qual":-0.10},
 "Panama":{"elo":1730,"mkt":0.06,"opta":0.1,"qual":0.05},
 "Qatar":{"elo":1421,"mkt":0.06,"opta":0.02,"qual":-0.05},
 "Saudi Arabia":{"elo":1576,"mkt":0.07,"opta":0.1,"qual":0.00},
 "South Africa":{"elo":1517,"mkt":0.08,"opta":0.1,"qual":0.00},
 "Uzbekistan":{"elo":1714,"mkt":0.05,"opta":0.1,"qual":0.05},
 "Curacao":{"elo":1434,"mkt":0.04,"opta":0.02,"qual":0.00},
 "Haiti":{"elo":1548,"mkt":0.04,"opta":0.02,"qual":0.05},
}
TEAMS = list(T.keys())
GROUP_OF = {t:g for g,ts in GROUPS.items() for t in ts}
HOSTS = {"United States","Mexico","Canada"}

# ---------------------------------------------------------------------------
# MATCH ENGINE  (independent-Poisson goals from rating diff; host edge)
# ---------------------------------------------------------------------------
HA = float(os.environ.get("HA",30.0))   # host advantage in Elo points
GOAL_DIV = 130.0   # Elo per 1 goal of supremacy
MU = 2.65          # avg goals per match

def _pois(lam):
    L = math.exp(-lam); k = 0; p = 1.0
    while True:
        k += 1; p *= random.random()
        if p <= L: return k-1

def _lams(ra, rb, a, b):
    d = (ra + (HA if a in HOSTS else 0)) - (rb + (HA if b in HOSTS else 0))
    sup = d / GOAL_DIV
    return max(0.15, MU/2 + sup/2), max(0.15, MU/2 - sup/2)

def group_match(R, a, b):
    la, lb = _lams(R[a], R[b], a, b)
    return _pois(la), _pois(lb)

def ko_play(R, a, b):
    """returns (winner, total goals a, total goals b) — 90min + ET + pens"""
    la, lb = _lams(R[a], R[b], a, b)
    ga, gb = _pois(la), _pois(lb)
    if ga != gb: return (a if ga > gb else b), ga, gb
    ea, eb = _pois(la*0.34), _pois(lb*0.34)            # extra time
    ga += ea; gb += eb
    if ea != eb: return (a if ea > eb else b), ga, gb
    pa = min(0.80, max(0.20, 0.5 + (R[a]-R[b])/4000))  # penalties
    return (a if random.random() < pa else b), ga, gb

# ---------------------------------------------------------------------------
# THIRD-PLACE -> R32 SLOT MATCHING (FIFA Annex C constraint sets)
# ---------------------------------------------------------------------------
ALLOWED = {r["match"]: set(r["third_from"]) for r in S["r32"] if "third_from" in r}
THIRD_SLOTS = S["third_slot_match_order"]   # [79,85,81,74,82,77,87,80]
# Tabela OFICIAL da FIFA (Anexo C) por combinação dos 8 grupos classificados (chave alfabética).
# O pareamento por restrição admite vários casamentos válidos; quando a combinação realizada
# consta aqui, usamos o mapa oficial da FIFA em vez da aproximação. Ver structure.json.
THIRD_OFFICIAL = {k: {int(m): g for m, g in v.items()}
                  for k, v in S.get("third_slot_official", {}).items()}

def assign_thirds(qual_groups):
    matchR = {}  # group -> match
    def aug(m, seen):
        for g in sorted(ALLOWED[m]):   # sorted -> determinístico entre processos (sets têm ordem por hash)
            if g in qual_groups and g not in seen:
                seen.add(g)
                if g not in matchR or aug(matchR[g], seen):
                    matchR[g] = m; return True
        return False
    for m in THIRD_SLOTS:
        aug(m, set())
    return {m: g for g, m in matchR.items()}   # match -> group

# ---------------------------------------------------------------------------
# ONE FULL TOURNAMENT
# ---------------------------------------------------------------------------
R32 = S["r32"]; KO = {"R16":S["r16"],"QF":S["qf"],"SF":S["sf"]}
def sim_once(R, tally=None):
    winner={}; runner={}; third_team={}; third_rec={}
    for g, ts in GROUPS.items():
        pts={t:0 for t in ts}; gd={t:0 for t in ts}; gf={t:0 for t in ts}
        for i in range(4):
            for j in range(i+1,4):
                a,b = ts[i],ts[j]
                _k = frozenset((a,b))
                if _k in FIXED_GROUP:
                    _fg = FIXED_GROUP[_k]; ga,gb = _fg[a],_fg[b]
                else:
                    ga,gb = group_match(R,a,b)
                gf[a]+=ga; gf[b]+=gb; gd[a]+=ga-gb; gd[b]+=gb-ga
                if ga>gb: pts[a]+=3
                elif gb>ga: pts[b]+=3
                else: pts[a]+=1; pts[b]+=1
                if tally is not None:
                    tally["g_for"][a]+=ga; tally["g_for"][b]+=gb
                    tally["g_ag"][a]+=gb; tally["g_ag"][b]+=ga
                    tally["mp"][a]+=1; tally["mp"][b]+=1
        order = sorted(ts, key=lambda t:(pts[t],gd[t],gf[t],random.random()), reverse=True)
        winner[g]=order[0]; runner[g]=order[1]; third_team[g]=order[2]
        third_rec[g]=(pts[order[2]],gd[order[2]],gf[order[2]],random.random())
    # best 8 of 12 thirds
    ranked_thirds = sorted(GROUPS.keys(), key=lambda g: third_rec[g], reverse=True)
    qual_groups = set(ranked_thirds[:8])
    third_assign = THIRD_OFFICIAL.get("".join(sorted(qual_groups))) \
        or assign_thirds(qual_groups)   # match -> group (oficial FIFA se houver; senão aproximação)
    # qualifiers set for "advanced"
    advanced = set(winner.values()) | set(runner.values()) | {third_team[g] for g in qual_groups}
    def slot(s, mno):
        if s=="3rd": return third_team[third_assign[mno]]
        return winner[s[1]] if s[0]=="1" else runner[s[1]]
    def ko_t(mno,a,b):
        if mno in FIXED_KO:
            _fk=FIXED_KO[mno]; w=_fk["winner"]
            g1,g2=(_fk["hg"],_fk["ag"]) if a==_fk["home"] else (_fk["ag"],_fk["hg"])
        else:
            w,g1,g2=ko_play(R,a,b)
        if tally is not None:
            tally["g_for"][a]+=g1; tally["g_for"][b]+=g2
            tally["g_ag"][a]+=g2; tally["g_ag"][b]+=g1
            tally["mp"][a]+=1; tally["mp"][b]+=1
            mu=tally["mu"].setdefault(mno,{}); k=a+"|"+b; mu[k]=mu.get(k,0)+1
        return w
    mw={}
    for r in R32:
        a=slot(r["home"],r["match"]); b=slot(r["away"],r["match"])
        mw[r["match"]]=ko_t(r["match"],a,b)
    reach={"R16":set(),"QF":set(),"SF":set(),"Final":set()}
    for rd,key in (("R16","R16"),("QF","QF"),("SF","SF")):
        nxt={"R16":"QF","QF":"SF","SF":"Final"}[rd]
        for r in KO[rd]:
            a=mw[int(r["home"][1:])]; b=mw[int(r["away"][1:])]
            reach[rd].add(a); reach[rd].add(b)
            mw[r["match"]]=ko_t(r["match"],a,b)
    fr=S["final"]; a=mw[int(fr["home"][1:])]; b=mw[int(fr["away"][1:])]
    reach["Final"].add(a); reach["Final"].add(b)
    champ=ko_t(fr["match"],a,b)
    if tally is not None:
        for g in GROUPS: tally["gw"][winner[g]]+=1
        for t in advanced: tally["adv"][t]+=1
        for t in reach["R16"]: tally["r16"][t]+=1
        for t in reach["QF"]: tally["qf"][t]+=1
        for t in reach["SF"]: tally["sf"][t]+=1
        for t in reach["Final"]: tally["fin"][t]+=1
        tally["ch"][champ]+=1
    return champ

def run(R, n, full=False):
    if full:
        ty={k:{t:0 for t in TEAMS} for k in ("gw","adv","r16","qf","sf","fin","ch","g_for","g_ag","mp")}
        ty["mu"]={}
        for _ in range(n): sim_once(R, ty)
        return ty
    ch={t:0 for t in TEAMS}
    for _ in range(n): ch[sim_once(R)]+=1
    return ch

# ---------------------------------------------------------------------------
# BUILD TARGET TITLE DISTRIBUTION  (market 45 / models 35 / qual 20)
# ---------------------------------------------------------------------------
def norm(d):
    s=sum(d.values()); return {k:v/s for k,v in d.items()}
mkt = norm({t:T[t]["mkt"] for t in TEAMS})
opta = norm({t:T[t]["opta"] for t in TEAMS})

import statistics as st

# ---------------------------------------------------------------------------
# STRENGTH RATINGS  (no title forcing).
# Blend on the Elo scale: market + models[Opta + Elo] + bounded qualitative bump.
# Os PESOS são parâmetros do modelo (config); o baseline reproduz a fórmula
# histórica (market 0.5625 / models 0.4375 [Opta 0.65 + Elo 0.35] / QUALK 110, SLOPE 56).
# Title & per-stage probs are OUTPUTS of simulating the REAL bracket on these
# strengths, so draw effects (loaded bottom half; Spain & France sharing the
# top half) emerge and are reported.
# ---------------------------------------------------------------------------
MEAN_ELO=st.mean(T[t]["elo"] for t in TEAMS)

def to_strength(pm, slope):
    lm={t:math.log(max(pm[t],1e-6)) for t in TEAMS}; ml=st.mean(lm.values())
    return {t:MEAN_ELO+slope*(lm[t]-ml) for t in TEAMS}

def build_strengths(cfg, qual=None):
    """Força R por seleção a partir de um config (RNG-free). Baseline
    (w_market=0.5625, w_models=0.4375, opta_in_models=0.65, QUALK=110, SLOPE=56)
    reproduz EXATAMENTE a fórmula histórica — (1-0.65)==0.35 exato em float.
    qual=None usa T[t]['qual'] (congelado); um dict {team: valor} sobrepõe o sinal
    qualitativo (Fase C: sinal de elenco vivo). qual=None => baseline byte-idêntico."""
    Smkt=to_strength(mkt, cfg["SLOPE"]); Sopta=to_strength(opta, cfg["SLOPE"])
    oin=cfg["opta_in_models"]; wm=cfg["w_market"]; wo=cfg["w_models"]; qk=cfg["QUALK"]
    R={}
    for t in TEAMS:
        qt=T[t]["qual"] if qual is None else qual.get(t, T[t]["qual"])
        models=oin*Sopta[t]+(1-oin)*T[t]["elo"]
        R[t]=wm*Smkt[t]+wo*models+qk*qt
    return R


def strength_as_of(team, date, cfg):
    """Stub p/ Fase C: força de 'team' como estaria na véspera de 'date' (modelos que
    aprendem com os jogos até ali). Na Fase B a força é estática (congelada no 9/jun),
    então ignora 'date' e devolve build_strengths(cfg)[team]. A Fase C reimplementa isto
    caminhando os resultados em ordem de data e atualizando a força (ex.: Elo dinâmico)."""
    return build_strengths(cfg)[team]

# consensus title (market+Opta+qual) — benchmark de exibição fixo (independe dos pesos do modelo)
K=0.55
consensus=norm({t:(0.5625*mkt[t]+0.4375*opta[t])*math.exp(K*T[t]["qual"]) for t in TEAMS})

def run_model(cfg, n, generated, with_state=True, R=None, qual=None):
    """Roda o Monte Carlo de um config e devolve o dict de saída (schema results.json).
    Determinístico: re-semeia random.seed(42) antes da simulação. Seta os globais do
    motor de partida (HA/GOAL_DIV/MU) a partir do config. with_state=False ignora o
    estado ao vivo (forecast pré-torneio — usado pelo runner p/ backtest comparável).
    R sobrepõe a força (Fase C: modelo que aprendeu = R final do walk-forward); qual
    sobrepõe o sinal qualitativo (sinal de elenco vivo). R/qual=None => baseline."""
    global HA, GOAL_DIV, MU
    HA=cfg["HA"]; GOAL_DIV=cfg["GOAL_DIV"]; MU=cfg["MU"]
    if R is None:
        R=build_strengths(cfg, qual=qual)
    random.seed(42)
    ty=run(R,n,full=True)
    res={}
    for t in TEAMS:
        res[t]={"group":GROUP_OF[t],
                "group_win":ty["gw"][t]/n,"advance":ty["adv"][t]/n,
                "r16":ty["r16"][t]/n,"qf":ty["qf"][t]/n,"sf":ty["sf"][t]/n,
                "final":ty["fin"][t]/n,"champion":ty["ch"][t]/n,
                "elo":T[t]["elo"],"R_cal":round(R[t],1),
                "g_for":round(ty["g_for"][t]/n,2),"g_ag":round(ty["g_ag"][t]/n,2),
                "mp":round(ty["mp"][t]/n,2),
                "mkt":mkt[t],"opta":opta[t],"consensus":consensus[t],"qual":T[t]["qual"]}
    mus={}
    for m,c in ty["mu"].items():
        top=sorted(c.items(),key=lambda kv:kv[1],reverse=True)[:8]
        mus[str(m)]=[[k.split("|")[0],k.split("|")[1],round(v/n,4)] for k,v in top]
    meta={"N":n,"weights":cfg["weights_display"],
        "generated":generated,"HA":HA,"SLOPE":cfg["SLOPE"],"QUALK":cfg["QUALK"],
        "GOAL_DIV":GOAL_DIV,"MU":MU}
    if with_state and (FIXED_GROUP or FIXED_KO):
        meta["state"]={"as_of":STATE_ASOF,"group_fixed":len(FIXED_GROUP),"ko_fixed":len(FIXED_KO)}
    return {"teams":res,"matchups":mus,"meta":meta}


if __name__=="__main__":
    import models as _models
    cfg=_models.with_env(_models.get("baseline"))   # baseline + overrides de env (SLOPE/HA/QUALK/GOAL_DIV/MU)
    if FIXED_GROUP or FIXED_KO:
        print(f"Estado ao vivo: {len(FIXED_GROUP)} grupo + {len(FIXED_KO)} mata-mata fixados (as_of {STATE_ASOF}).")
    N=NFINAL
    # generated = data deste run (carimbada automaticamente). Override GENERATED=AAAA-MM-DD p/
    # reprodutibilidade em teste. Mantém snapshot/"O que mudou" coerentes (1 snapshot/dia).
    GENERATED=os.environ.get("GENERATED") or time.strftime("%Y-%m-%d")
    t0=time.time()
    print("Strengths built (market 45 / models 35 / qual 20). Running final Monte Carlo ...")
    print(f"Final Monte Carlo: {N} simulations ...")
    out=run_model(cfg, N, GENERATED)
    res=out["teams"]
    OUT=os.environ.get("OUT_FILE") or f"{BASE}/wc2026_results.json"
    if not os.environ.get("OUT_FILE"):  # run de teste não polui o histórico
        import snapshot as _snapshot
        _snap=_snapshot.snapshot_current(OUT)
        if _snap: print(f"Snapshot do forecast anterior: {_snap}")
    with open(OUT,"w") as f: json.dump(out,f,indent=1)

    # -----------------------------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------------------------
    def s(k): return sum(res[t][k] for t in TEAMS)
    print("\n=== VALIDATION (expected) ===")
    print(f"  sum champion = {s('champion')*100:6.1f}%  (100)")
    print(f"  sum final    = {s('final')*100:6.1f}%  (200)")
    print(f"  sum sf       = {s('sf')*100:6.1f}%  (400)")
    print(f"  sum qf       = {s('qf')*100:6.1f}%  (800)")
    print(f"  sum r16      = {s('r16')*100:6.1f}%  (1600)")
    print(f"  sum advance  = {s('advance')*100:6.1f}%  (3200)")
    print(f"  sum groupwin = {s('group_win')*100:6.1f}%  (1200)")
    print(f"\nElapsed {time.time()-t0:.0f}s")
    print("\n=== TOP 16 — model champion% vs market vs Opta vs consensus ===")
    print(f"{'Team':22s}{'champ%':>8}{'mkt%':>8}{'opta%':>8}{'cons%':>8}")
    for t in sorted(TEAMS,key=lambda x:res[x]["champion"],reverse=True)[:16]:
        print(f"{t:22s}{res[t]['champion']*100:8.2f}{mkt[t]*100:8.2f}{opta[t]*100:8.2f}{consensus[t]*100:8.2f}")
