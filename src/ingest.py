#!/usr/bin/env python3
"""
ingest.py — Adaptador de ingestão de placares por API com GATES de segurança (Fase 2).

Puxa resultados de DUAS fontes independentes e só aceita um placar quando passa em todos
os gates. É o guarda da ENTRADA: o gate do atualizar.sh (somas/monotonicidade/zero-dep) só
valida a SAÍDA — garbage-in passaria por ele. Aqui, garbage NÃO entra silenciosamente.

Fontes: football-data.org (/v4/competitions/WC/matches, header X-Auth-Token) + ESPN
(site.api.espn.com .../soccer/fifa.world/scoreboard?dates=YYYYMMDD, sem chave).

Gates:
  1. nomes fail-closed     — nome de seleção que não mapeia para o canônico ABORTA o run.
  2. quorum de fonte dupla — só aceita (gols por time) quando AS DUAS fontes concordam.
  3. temporal              — só jogo com kickoff já passado E final nas duas fontes.
  4. home/away pelo fixtures — gols mapeados pelo mandante do fixtures.json, nunca pela API.
  5. plausibilidade        — placar atípico (gols>7 ou soma>10) ENTRA mas é sinalizado.
  6. diff-before-write     — escreve state.json.candidate + diff legível; promoção é explícita.

Uso:
  FOOTBALL_DATA_TOKEN=... python3 ingest.py            # dry-run ao vivo: busca, gates, diff
  FOOTBALL_DATA_TOKEN=... python3 ingest.py --promote   # idem + snapshot + grava state.json
  python3 ingest.py --from-cache .api_cache             # offline (respostas gravadas), p/ teste
  python3 ingest.py --now 2026-06-23T23:00              # fixa o "agora" do gate temporal (teste)

Integra o contrato DataSource (state.py): ApiQuorumSource().load() devolve o state dict.
Mata-mata (winner/decided_by/pênaltis) NÃO é auto-escrito — é sinalizado p/ revisão manual
(fail-closed no caso complexo; nenhum KO disputado ainda na fase de grupos).
"""
import json, os, sys, ssl, glob, subprocess, datetime as _dt
import urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "data")
STATE_PATH = os.path.join(BASE, "live", "state.json")
CAND_PATH = STATE_PATH + ".candidate"

FD_URL = "https://api.football-data.org/v4/competitions/WC/matches"
ESPN_URL = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard?dates={d}"

# Mapas de canonicalização (API -> nome EN canônico do projeto). Os 44 que já batem não
# precisam de entrada. Qualquer nome FORA do canônico E fora do mapa ABORTA (fail-closed).
CANON_FD = {
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Cape Verde Islands": "Cape Verde",
    "Congo DR": "DR Congo",
    "Curaçao": "Curacao",
}
CANON_ESPN = {
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Congo DR": "DR Congo",
    "Curaçao": "Curacao",
    "Türkiye": "Turkey",
}


class IngestAbort(Exception):
    """Erro fail-closed: aborta o run inteiro (nome desconhecido, fonte quebrada)."""


def load_fixtures():
    with open(os.path.join(BASE, "fixtures.json")) as f:
        return json.load(f)


def _canonset():
    return {f["home"] for f in load_fixtures()["group"]} | {f["away"] for f in load_fixtures()["group"]}


CANON = _canonset()


def canon(name, source):
    """Nome canônico ou ABORTA (fail-closed) — nunca match aproximado em dado de verdade."""
    if name in CANON:
        return name
    table = CANON_FD if source == "fd" else CANON_ESPN
    if name in table:
        return table[name]
    raise IngestAbort(f"[{source}] nome de seleção desconhecido: {name!r} — "
                      f"adicione ao mapa CANON_{source.upper()} antes de prosseguir.")


def _canon_or_none(name, source):
    """Como canon(), mas devolve None em vez de abortar. USO SÓ NO MATA-MATA: jogos futuros do KO
    trazem PLACEHOLDER de confronto ('Round of 32 X Winner', 'Winners Group A'…) no lugar do time —
    isso NÃO pode derrubar o run. Times reais resolvem (os 48 já passaram pelo ingest de grupo);
    nome não-resolvível = confronto ainda indefinido → pula o jogo. Grupo mantém o fail-closed."""
    try:
        return canon(name, source)
    except IngestAbort:
        return None


# ── HTTP (urllib p/ produção/CI; cache p/ teste offline) ──────────────────────
def _http_json(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return json.loads(r.read().decode("utf-8"))


def _fd_raw(cache=None):
    if cache:
        return json.load(open(os.path.join(cache, "footballdata.json")))
    tok = os.environ.get("FOOTBALL_DATA_TOKEN")
    if not tok:
        raise IngestAbort("FOOTBALL_DATA_TOKEN não definido (export ou .dev.vars).")
    return _http_json(FD_URL, {"X-Auth-Token": tok})


def _espn_raw(date_yyyymmdd, cache=None):
    if cache:
        p = os.path.join(cache, f"espn_{date_yyyymmdd}.json")
        return json.load(open(p)) if os.path.exists(p) else {"events": []}
    return _http_json(ESPN_URL.format(d=date_yyyymmdd))


# ── Fetchers → {frozenset({A,B}): {"goals": {A: ga, B: gb}, "final": bool}} ────
def fetch_fd_group(cache=None):
    """Resultados de GRUPO do football-data, por par de seleções (gols por time)."""
    out = {}
    for m in _fd_raw(cache).get("matches", []):
        if m.get("stage") != "GROUP_STAGE":
            continue
        hn, an = m["homeTeam"].get("name"), m["awayTeam"].get("name")
        if not hn or not an:
            continue
        h, a = canon(hn, "fd"), canon(an, "fd")
        ft = m.get("score", {}).get("fullTime", {})
        gh, ga = ft.get("home"), ft.get("away")
        final = m.get("status") == "FINISHED" and gh is not None and ga is not None
        out[frozenset((h, a))] = {"goals": {h: gh, a: ga}, "final": final}
    return out


def fetch_espn_group(dates, cache=None):
    """Resultados do ESPN por par de seleções, varrendo as datas dos jogos de grupo."""
    out = {}
    for d in dates:
        for e in _espn_raw(d, cache).get("events", []):
            comp = e.get("competitions", [{}])[0]
            cs = comp.get("competitors", [])
            if len(cs) != 2:
                continue
            try:
                teams = {canon(c["team"]["displayName"], "espn"): int(c["score"]) for c in cs}
            except (KeyError, ValueError, TypeError):
                continue
            final = e.get("status", {}).get("type", {}).get("name") == "STATUS_FULL_TIME"
            (a, ga), (b, gb) = list(teams.items())
            out[frozenset((a, b))] = {"goals": {a: ga, b: gb}, "final": final}
    return out


# ── Fetchers de MATA-MATA ──────────────────────────────────────────────────────
# goals = PLACAR NO FIM DA PRORROGAÇÃO (pênaltis NÃO somam gol; ver dacopa em bolao.py). No
# football-data, o fullTime de um jogo de PÊNALTIS já inclui a disputa (fullTime = reg+ET+pen),
# então p/ pens usa regularTime+extraTime; p/ reg/prorrogação, fullTime. winner/decided_by vêm do
# score. O ESPN traz score=fim-da-prorrogação + shootoutScore separado + flag winner (bate 1:1).
_ESPN_FINAL = {"STATUS_FULL_TIME", "STATUS_FINAL_PEN", "STATUS_FULL_TIME_AET", "STATUS_FINAL_AET"}


def fetch_fd_ko(cache=None):
    """KO do football-data por par de seleções: {goals{time:gols_fim_prorrog}, winner, decided_by, final}."""
    out = {}
    for m in _fd_raw(cache).get("matches", []):
        stg = m.get("stage")
        if not stg or stg in ("GROUP_STAGE", "THIRD_PLACE"):   # projeto não modela 3º lugar
            continue
        hn, an = (m.get("homeTeam") or {}).get("name"), (m.get("awayTeam") or {}).get("name")
        if not hn or not an:
            continue
        h, a = _canon_or_none(hn, "fd"), _canon_or_none(an, "fd")
        if h is None or a is None:                   # confronto de KO ainda indefinido — pula
            continue
        sc = m.get("score") or {}
        dur = sc.get("duration")
        if dur == "PENALTY_SHOOTOUT":                          # fullTime inclui pênaltis -> usa reg+ET
            rt, et = sc.get("regularTime") or {}, sc.get("extraTime") or {}
            gh = (rt.get("home") or 0) + (et.get("home") or 0)
            ga = (rt.get("away") or 0) + (et.get("away") or 0)
            decided = "pens"
        else:
            ft = sc.get("fullTime") or {}
            gh, ga = ft.get("home"), ft.get("away")            # reg/ET: fullTime = fim da prorrogação
            decided = "et" if dur == "EXTRA_TIME" else "reg"
        win = {"HOME_TEAM": h, "AWAY_TEAM": a}.get(sc.get("winner"))
        final = m.get("status") == "FINISHED" and gh is not None and ga is not None and win is not None
        out[frozenset((h, a))] = {"goals": {h: gh, a: ga}, "winner": win, "decided_by": decided, "final": final}
    return out


def fetch_espn_ko(dates, cache=None):
    """KO do ESPN por par: {goals{time:gols_fim_prorrog}, winner, final}. score já é o fim da
    prorrogação (pênaltis vão em shootoutScore, à parte); flag 'winner' dá quem avançou."""
    out = {}
    for d in dates:
        for e in _espn_raw(d, cache).get("events", []):
            comp = e.get("competitions", [{}])[0]
            cs = comp.get("competitors", [])
            if len(cs) != 2:
                continue
            names = [_canon_or_none((c.get("team") or {}).get("displayName", ""), "espn") for c in cs]
            if any(n is None for n in names):          # placeholder (confronto indefinido) — pula
                continue
            try:
                goals = {names[i]: int(cs[i]["score"]) for i in range(2)}
                winner = next((names[i] for i in range(2) if cs[i].get("winner")), None)
            except (KeyError, ValueError, TypeError):
                continue
            final = e.get("status", {}).get("type", {}).get("name") in _ESPN_FINAL
            (a, ga), (b, gb) = list(goals.items())
            out[frozenset((a, b))] = {"goals": {a: ga, b: gb}, "winner": winner, "final": final}
    return out


def ko_dates():
    """Datas (YYYYMMDD) dos jogos de KO p/ varrer o ESPN — do ko_schedule.json (utc e brt, cobre fuso)."""
    p = os.path.join(BASE, "ko_schedule.json")
    if not os.path.exists(p):
        return []
    ds = set()
    for m in json.load(open(p)).get("matches", []):
        for k in ("utc", "kickoff_brt"):
            v = m.get(k) or ""
            if len(v) >= 10:
                ds.add(v[:10].replace("-", ""))
    return sorted(ds)


# ── Build do candidato + gates ────────────────────────────────────────────────
def _parse_dt(s):
    return _dt.datetime.fromisoformat(s)


def build(fix, fd, espn, fd_ko, espn_ko, now, S=None):
    """Devolve (state_candidate, report). report = {accepted, holds, rejects, warns, ko_added, ko_rejects}."""
    group, holds, rejects, warns = [], [], [], []
    for f in sorted(fix["group"], key=lambda x: x["match"]):
        mno, home, away = f["match"], f["home"], f["away"]
        pair = frozenset((home, away))
        kickoff = _parse_dt(f["kickoff_et"])
        if now < kickoff:                       # gate temporal: jogo ainda não começou
            continue
        a, b = fd.get(pair), espn.get(pair)
        if not a or not b or not a["final"] or not b["final"]:
            if a or b:                          # passou do horário mas falta fonte/não-final
                holds.append((mno, f"{home} x {away}", "aguardando final nas DUAS fontes"))
            continue
        ah, aa = a["goals"][home], a["goals"][away]   # gols por mandante DO FIXTURES
        bh, ba = b["goals"][home], b["goals"][away]
        if (ah, aa) != (bh, ba):                # gate de quorum
            rejects.append((mno, f"{home} x {away}",
                            f"divergência: football-data {ah}-{aa} vs ESPN {bh}-{ba}"))
            continue
        if ah > 7 or aa > 7 or ah + aa > 10:    # plausibilidade: entra, mas sinaliza
            warns.append((mno, f"{home} {ah}-{aa} {away}", "placar atípico — confira"))
        group.append({"match": mno, "hg": ah, "ag": aa})

    # ── mata-mata: ingestão AUTOMÁTICA (decisão Bera 2026-06-30) ──────────────────
    # Placar que conta = fim da prorrogação (pênaltis não somam). winner vem do football-data, com
    # QUÓRUM de placar E de vencedor no ESPN. Cascata: resolve a chave, ingere a rodada pronta,
    # re-resolve p/ pegar a próxima se já jogada (robusto a run perdido). Append-only (ko_have).
    prev = json.load(open(STATE_PATH)) if os.path.exists(STATE_PATH) else {"results": {}}
    ko_list = [dict(r) for r in (prev.get("results", {}).get("knockout", []) or [])]
    ko_have = {r["match"] for r in ko_list}
    ko_added, ko_rejects = [], []
    if len(group) >= 72:
        if S is None:
            S = json.load(open(os.path.join(BASE, "worldcup2026_structure.json")))
        ko_defs = S["r32"] + S["r16"] + S["qf"] + S["sf"] + [S["final"]]
        ko_skip = set()                                        # jogo já resolvido/segurado/rejeitado neste run
        while True:
            rb = _bracket.resolve_bracket({"results": {"group": group, "knockout": ko_list}}, fix, S)
            if not rb:
                break
            progressed = False
            for rdef in ko_defs:
                mno = rdef["match"]
                if mno in ko_have or mno in ko_skip or mno not in rb["matchups"]:
                    continue
                H, A = rb["matchups"][mno]
                a, b = fd_ko.get(frozenset((H, A))), espn_ko.get(frozenset((H, A)))
                if not a or not b or not a["final"] or not b["final"]:
                    if a or b:                                 # tem em uma fonte mas não fechou nas duas
                        holds.append((mno, f"{H} x {A}", "KO: aguardando final nas DUAS fontes"))
                    ko_skip.add(mno); continue                 # sem dado nesta rodada → não re-tenta neste run
                try:
                    hg, ag, eh, ea = a["goals"][H], a["goals"][A], b["goals"][H], b["goals"][A]
                except KeyError:
                    ko_rejects.append((mno, f"{H} x {A}", "par de times não bate entre as fontes"))
                    ko_skip.add(mno); continue
                if (hg, ag) != (eh, ea):                        # quórum de placar (fim da prorrogação)
                    ko_rejects.append((mno, f"{H} x {A}",
                        f"placar (fim prorrog.) diverge: fd {hg}-{ag} vs ESPN {eh}-{ea}"))
                    ko_skip.add(mno); continue
                if a["winner"] != b["winner"] or a["winner"] not in (H, A):   # quórum de vencedor
                    ko_rejects.append((mno, f"{H} x {A}",
                        f"vencedor diverge/inválido: fd {a['winner']} vs ESPN {b['winner']}"))
                    ko_skip.add(mno); continue
                rec = {"match": mno, "home": H, "away": A, "hg": hg, "ag": ag,
                       "winner": a["winner"], "decided_by": a["decided_by"]}
                ko_list.append(rec); ko_have.add(mno); ko_added.append(rec); progressed = True
            if not progressed:
                break

    candidate = {
        "as_of": now.date().isoformat(),
        "tz": "America/Sao_Paulo",
        "note": (f"Ingestão automática (football-data + ESPN, quorum). {len(group)} jogos de grupo, "
                 f"{len(ko_list)} de mata-mata."),
        "results": {"group": group, "knockout": ko_list},
    }
    report = {"accepted": len(group), "holds": holds, "rejects": rejects, "warns": warns,
              "ko_added": ko_added, "ko_rejects": ko_rejects}
    return candidate, report


# ── Diff legível (o que muda vs state.json atual) ─────────────────────────────
def diff(old, new):
    om = {r["match"]: (r["hg"], r["ag"]) for r in (old.get("results", {}).get("group", []) or [])}
    nm = {r["match"]: (r["hg"], r["ag"]) for r in (new.get("results", {}).get("group", []) or [])}
    added = [(m, nm[m]) for m in sorted(nm) if m not in om]
    changed = [(m, om[m], nm[m]) for m in sorted(nm) if m in om and om[m] != nm[m]]
    removed = [m for m in sorted(om) if m not in nm]
    return added, changed, removed


# ── DataSource (contrato state.py) ────────────────────────────────────────────
import state as _state  # noqa: E402  (mesmo diretório)
import bracket as _bracket  # noqa: E402  (resolve a chave p/ casar cada jogo de KO ao seu match number)


class ApiQuorumSource(_state.DataSource):
    def __init__(self, cache=None, now=None):
        self.cache, self.now = cache, now or _dt.datetime.now()

    def load(self):
        fix = load_fixtures()
        dates = sorted({f["date"].replace("-", "") for f in fix["group"]})
        cand, _ = build(fix, fetch_fd_group(self.cache), fetch_espn_group(dates, self.cache),
                        fetch_fd_ko(self.cache), fetch_espn_ko(ko_dates(), self.cache), self.now)
        return cand


# ── CLI ───────────────────────────────────────────────────────────────────────
def main(argv):
    cache = None
    promote = "--promote" in argv
    allow_overwrite = "--allow-overwrite" in argv
    now = _dt.datetime.now()
    if "--from-cache" in argv:
        cache = argv[argv.index("--from-cache") + 1]
    if "--now" in argv:
        now = _parse_dt(argv[argv.index("--now") + 1])

    fix = load_fixtures()
    dates = sorted({f["date"].replace("-", "") for f in fix["group"]})
    try:
        fd = fetch_fd_group(cache)
        espn = fetch_espn_group(dates, cache)
        fd_ko = fetch_fd_ko(cache)
        espn_ko = fetch_espn_ko(ko_dates(), cache)
    except IngestAbort as e:
        print("ABORTADO (fail-closed):", e); return 2
    except (urllib.error.URLError, OSError) as e:
        print("ABORTADO (rede/fonte):", e); return 2

    cand, rep = build(fix, fd, espn, fd_ko, espn_ko, now)
    errs = _state.validate_state(cand, fix)
    old = json.load(open(STATE_PATH)) if os.path.exists(STATE_PATH) else {"results": {"group": []}}
    added, changed, removed = diff(old, cand)

    print(f"▸ Ingestão (now={now.isoformat(timespec='minutes')}) — aceitos {rep['accepted']} jogos de grupo")
    print(f"  novos: {len(added)} · alterados: {len(changed)} · removidos: {len(removed)}")
    for m, (hg, ag) in added:
        fx = next(f for f in fix["group"] if f["match"] == m)
        print(f"    + m{m}: {fx['home']} {hg}-{ag} {fx['away']}")
    for m, o, n in changed:
        print(f"    ~ m{m}: {o[0]}-{o[1]} -> {n[0]}-{n[1]}  (REVISAR: sobrescreve jogo já gravado)")
    for m, lbl, why in rep["rejects"]:
        print(f"    ✗ m{m} {lbl}: {why}")
    for m, lbl, why in rep["holds"]:
        print(f"    … m{m} {lbl}: {why}")
    for m, lbl, why in rep["warns"]:
        print(f"    ⚠ m{m} {lbl}: {why}")
    if rep["ko_added"] or rep["ko_rejects"]:
        print(f"  mata-mata: +{len(rep['ko_added'])} gravados · {len(rep['ko_rejects'])} rejeitados")
    for r in rep["ko_added"]:
        print(f"    + KO m{r['match']}: {r['home']} {r['hg']}-{r['ag']} {r['away']} "
              f"→ {r['winner']} ({r['decided_by']})")
    for m, lbl, why in rep["ko_rejects"]:
        print(f"    ✗ KO m{m} {lbl}: {why}")
    if errs:
        print("  ✗ validate_state FALHOU:", errs); return 2

    json.dump(cand, open(CAND_PATH, "w"), ensure_ascii=False, indent=1)
    print(f"  candidato escrito: {os.path.relpath(CAND_PATH, ROOT)}")

    problems = bool(rep["rejects"] or rep["ko_rejects"])
    changed_state = bool(added or changed or removed or rep["ko_added"])
    if problems:
        print("  ✗ há DIVERGÊNCIAS de fonte — NÃO promover sem revisar.")
    if promote:
        if problems:
            print("  promoção BLOQUEADA (divergências pendentes)."); return 3
        if changed and not allow_overwrite:
            print(f"  promoção BLOQUEADA: {len(changed)} jogo(s) já gravado(s) seriam SOBRESCRITOS "
                  f"(append-only). Revise o diff e use --allow-overwrite se for correção real."); return 3
        if not changed_state:
            print("  nada novo — state.json inalterado."); return 0
        subprocess.run([os.path.join(ROOT, "scripts", "snapshot_state.sh")], check=False)
        json.dump(cand, open(STATE_PATH, "w"), ensure_ascii=False, indent=1)
        print("  ✓ PROMOVIDO: state.json atualizado (backup feito).")
    else:
        print("  (dry-run; use --promote p/ gravar state.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
