#!/usr/bin/env python3
"""
Ingest de pesquisas eleitorais 2026 a partir das páginas da Wikipédia PT
(decisão da B2: fonte primária Wikipédia + âncora TSE; ver docs/fontes-eleicoes.md).

Lê as 28 páginas (presidencial + 26 estaduais + DF distrital), interpreta as
wikitables (1º turno, 2º turno por par, Senado) e grava data/live/polls.json
no schema v1 (docs/handoff-eleicoes.md). Só stdlib.

- Ingere seções de ano >= 2025 (campanha; o resto é ruído pré-candidatura).
- `pct` fica em ponto percentual COMO DIVULGADO; `base` é detectada pela soma
  (Senado 2 votos: >110 = bruta_2votos). Normalização é papel do motor.
- Candidato é casado com o structure (SQ) por partido+nome normalizado;
  não casou => sq null + fila em data/eleicoes/aliases_pendentes.json.
  data/eleicoes/aliases.json (curado à mão) tem precedência.
- Âncora TSE (tse_protocolo) fica null nesta fase; ativação na B8 (CI).

Uso: python3 ingest_polls.py [--cache DIR] (cache de HTML p/ reprodução/debug)
"""
import json
import os
import re
import ssl
import sys
import unicodedata
import urllib.parse
import urllib.request
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
STRUCT = os.path.join(ROOT, "data", "eleicoes2026_structure.json")
OUT = os.path.join(ROOT, "data", "live", "polls.json")
ALIASES = os.path.join(ROOT, "data", "eleicoes", "aliases.json")
PENDING = os.path.join(ROOT, "data", "eleicoes", "aliases_pendentes.json")

UA = {"User-Agent": "FichaDoJogo/1.0 (projeto pessoal de modelagem; beralzir@gmail.com)"}
_cafile = "/etc/ssl/cert.pem"
CTX = ssl.create_default_context(cafile=_cafile if os.path.exists(_cafile) else None)

# título exato por UF (preposição varia); presidencial e DF são casos próprios
UF_TITLES = {
    "AC": "no Acre", "AL": "em Alagoas", "AM": "no Amazonas", "AP": "no Amapá",
    "BA": "na Bahia", "CE": "no Ceará", "ES": "no Espírito Santo", "GO": "em Goiás",
    "MA": "no Maranhão", "MG": "em Minas Gerais", "MS": "em Mato Grosso do Sul",
    "MT": "em Mato Grosso", "PA": "no Pará", "PB": "na Paraíba", "PE": "em Pernambuco",
    "PI": "no Piauí", "PR": "no Paraná", "RJ": "no Rio de Janeiro",
    "RN": "no Rio Grande do Norte", "RO": "em Rondônia", "RR": "em Roraima",
    "RS": "no Rio Grande do Sul", "SC": "em Santa Catarina", "SE": "em Sergipe",
    "SP": "em São Paulo", "TO": "no Tocantins",
}
PRES_TITLE = "Pesquisas de opinião para a eleição presidencial no Brasil em 2026"
DF_TITLE = "Pesquisas eleitorais para a eleição distrital de 2026 no Distrito Federal"

MESES = {"janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3, "abril": 4, "maio": 5,
         "junho": 6, "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10,
         "novembro": 11, "dezembro": 12,
         "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6, "jul": 7,
         "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12}


def norm(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^A-Z0-9 ]", " ", s.upper()).split()


def api(params):
    params["format"] = "json"
    url = "https://pt.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
        return json.load(r)


# ---------------- HTML -> grid de tabelas com contexto de headings ----------------

class PageWalker(HTMLParser):
    """Percorre o HTML renderizado; devolve [(context, table_grid)] com
    context = lista de headings (h2/h3/h4) vigentes. Expande rowspan/colspan."""

    def __init__(self):
        super().__init__()
        self.heads = {2: None, 3: None, 4: None}
        self.items = []
        self._h = None          # heading aberto (nível)
        self._htxt = ""
        self._tdepth = 0
        self._rows = None       # tabela wikitable de nível 1 em captura
        self._row = None
        self._cell = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("h2", "h3", "h4") and self._tdepth == 0:
            self._h = int(tag[1]); self._htxt = ""
        elif tag == "table":
            self._tdepth += 1
            if self._tdepth == 1 and "wikitable" in (a.get("class") or ""):
                self._rows = []
        elif self._rows is not None and self._tdepth == 1:
            if tag == "tr":
                self._row = []
            elif tag in ("td", "th"):
                self._cell = {"t": "", "th": tag == "th",
                              "rs": int(a.get("rowspan") or 1), "cs": int(a.get("colspan") or 1)}
        if tag == "style" or tag == "script":
            self._skip = True

    def handle_endtag(self, tag):
        if tag in ("h2", "h3", "h4") and self._h == int(tag[1]):
            lvl = self._h
            txt = re.sub(r"\[.*?\]", "", self._htxt).strip()
            self.heads[lvl] = txt
            for deeper in range(lvl + 1, 5):
                self.heads[deeper] = None
            self._h = None
        elif tag == "table":
            if self._tdepth == 1 and self._rows is not None:
                grid = expand(self._rows)
                if grid:
                    self.items.append(([self.heads[2], self.heads[3], self.heads[4]], grid))
                self._rows = None
            self._tdepth -= 1
        elif self._rows is not None and self._tdepth == 1:
            if tag == "tr" and self._row is not None:
                if self._row:
                    self._rows.append(self._row)
                self._row = None
            elif tag in ("td", "th") and self._cell is not None:
                self._cell["t"] = re.sub(r"\s+", " ", self._cell["t"]).strip()
                if self._row is not None:
                    self._row.append(self._cell)
                self._cell = None
        if tag in ("style", "script"):
            self._skip = False

    def handle_data(self, d):
        if getattr(self, "_skip", False):
            return
        if self._h is not None and self._tdepth == 0:
            self._htxt += d
        elif self._cell is not None:
            self._cell["t"] += d


def expand(rows):
    """Expande rowspan/colspan numa matriz retangular de dicts {'t','th'}."""
    grid = []
    pend = {}  # col -> (restantes, cell)
    for row in rows:
        out = []
        col = 0
        ci = 0
        while ci < len(row) or col in pend:
            if col in pend:
                left, cell = pend[col]
                out.append(cell)
                left -= 1
                if left:
                    pend[col] = (left, cell)
                else:
                    del pend[col]
                col += 1
                continue
            if ci >= len(row):
                break
            c = row[ci]; ci += 1
            for _ in range(c["cs"]):
                cc = {"t": c["t"], "th": c["th"]}
                out.append(cc)
                if c["rs"] > 1:
                    pend[col] = (c["rs"] - 1, cc)
                col += 1
        grid.append(out)
    return grid


# ---------------- interpretação de uma tabela ----------------

PCT_RE = re.compile(r"^(\d+(?:[.,]\d+)?)\s*%?")
NUM_STRIP = re.compile(r"\[[^\]]*\]")  # footnotes [1] [a] [nota 2]


def parse_pct(text):
    t = NUM_STRIP.sub("", text).strip()
    if t in ("", "-", "–", "—", "?"):
        return None
    m = PCT_RE.match(t.replace("−", "-"))
    if not m:
        return None
    return float(m.group(1).replace(",", "."))


def parse_dates(text, year):
    """'25 Ago - 27 Ago' | '23 a 26 de agosto' | '10 de julho' | '28 Jul - 01 Ago'.
    Devolve (ini, fim, raw) ISO; None quando não parseia."""
    raw = NUM_STRIP.sub("", text).strip()
    t = unicodedata.normalize("NFD", raw.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = t.replace("º", "").replace("°", "").replace("de ", " ").replace(".", " ")
    parts = re.split(r"\s*(?:-|–|\be\b|\ba\b|\bate\b)\s*", t)
    parts = [p for p in parts if re.search(r"\d", p)]

    def one(p, fallback_month=None):
        p = p.strip()
        m = re.search(r"(\d{1,2})\s*([a-z]{3,9})?", p)
        if not m:
            return None, fallback_month
        day = int(m.group(1))
        mon = MESES.get((m.group(2) or "").strip()[:9]) or MESES.get((m.group(2) or "").strip()[:3]) or fallback_month
        return day, mon
    if not parts:
        return None, None, raw
    d2, m2 = one(parts[-1])
    d1, m1 = one(parts[0], fallback_month=None)
    if m1 is None:
        m1 = m2
    if m2 is None:
        m2 = m1
    if d1 is None or d2 is None or m1 is None or m2 is None:
        return None, None, raw
    y1 = y2 = year
    if m1 > m2:  # virada de ano dentro do campo (dez-jan)
        y1 = year - 1
    return f"{y1:04d}-{m1:02d}-{d1:02d}", f"{y2:04d}-{m2:02d}-{d2:02d}", raw


def parse_amostra(text):
    t = NUM_STRIP.sub("", text)
    digits = re.sub(r"[^\d]", "", t)
    return int(digits) if digits else None


META_MAP = [
    (re.compile(r"vantan?gem|lidera|\bcen\b|cen\.|cen[aá]rio", re.I), "skip"),
    (re.compile(r"data", re.I), "datas"),
    (re.compile(r"contratante|instituto|empresa|pesquisa", re.I), "instituto"),
    (re.compile(r"amostra", re.I), "amostra"),
    (re.compile(r"margem", re.I), "margem"),
    (re.compile(r"outros", re.I), "outros"),
    (re.compile(r"indecis|absten|abstens|branco|nulo|nao sabe|não sabe|ns/nr", re.I), "indefinidos"),
]

CAND_RE = re.compile(r"^(.*?)\(?\s*([A-ZÀ-Ü][A-Za-zÀ-ü]*)?\)?$")


def classify_header(grid):
    """Identifica linha(s) de cabeçalho, colunas meta e colunas de candidato.
    Devolve (cols, first_data_row_idx) com cols = lista (tipo, texto)."""
    header_rows = []
    for i, row in enumerate(grid[:4]):
        if any(c["th"] for c in row):
            header_rows.append(i)
        else:
            break
    if not header_rows:
        return None, None
    ncols = max(len(grid[i]) for i in header_rows)
    cols = []
    for col in range(ncols):
        texts = []
        for i in header_rows:
            if col < len(grid[i]):
                t = grid[i][col]["t"]
                if t and t not in texts:
                    texts.append(t)
        joined = " ".join(texts)
        kind = None
        if ".mw-parser-output" in joined or joined.strip() == "":
            kind = "skip"
        else:
            for rx, k in META_MAP:
                if rx.search(NUM_STRIP.sub("", joined)):
                    kind = k
                    break
        if kind is None:
            kind = "cand"
        cols.append((kind, NUM_STRIP.sub("", joined).strip()))
    return cols, header_rows[-1] + 1


def year_from_context(ctx):
    for h in reversed([c for c in ctx if c]):
        m = re.search(r"(20\d\d)", h)
        if m:
            return int(m.group(1))
    return None


def section_kind(ctx):
    """(cargo, turno) a partir dos headings: gov 1T, gov 2T (par em h2 ou h3),
    senado, pres. Variações reais: 'Primeiro Turno (Governador)', 'Governador
    (turno único)' (AP), 'Senador' sem subseção de ano (BA)."""
    top = (ctx[0] or "").lower()
    if "senad" in top:
        return "senado", 1, None
    if "segundo turno" in top:
        pair = None
        for h in (ctx[1], ctx[2]):
            if h and not re.match(r"^20\d\d$", h.strip()) and (" e " in h or " x " in h.lower()):
                pair = h
                break
        return "principal", 2, pair
    if "primeiro turno" in top or "governador" in top or "turno único" in top or "turno unico" in top:
        return "principal", 1, None
    return None, None, None


# ---------------- casamento candidato -> SQ ----------------

def load_json(path, default):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


def build_matcher(race, aliases):
    cands = race["candidates"]
    by_party = {}
    for c in cands:
        by_party.setdefault(tuple(norm(c["partido"])), []).append(c)
    amap = {k.upper(): v for k, v in aliases.get("candidatos", {}).items()}

    def match(header_text):
        raw = NUM_STRIP.sub("", header_text).strip()
        if raw.upper() in amap:
            return amap[raw.upper()], raw
        # separa "Nome (Partido)" ou "NomePARTIDO" (sem espaço)
        m = re.match(r"^(.*?)[\(\[]([^\)\]]+)[\)\]]?$", raw)
        name_part, party_part = (m.group(1), m.group(2)) if m else (raw, "")
        if not m:
            m2 = re.match(r"^(.*?[a-zà-ü])((?:[A-ZÀ-Ü]{2,}|Avante|Missão|Democrata|Republicanos|Novo|Podemos|Cidadania|Mobiliza|Solidariedade|União)(?:\s*\d*)?)$", raw)
            if m2:
                name_part, party_part = m2.group(1), m2.group(2)
        ntoks = set(norm(name_part))
        ptoks = tuple(norm(party_part))
        pool = cands
        if ptoks:
            # igualdade EXATA de tokens: substring faria PSD cair no pool do PSDB
            for pk, group in sorted(by_party.items()):
                if set(ptoks) == set(pk):
                    pool = group
                    break
        best, best_score = [], 0
        for c in pool:
            toks = set(norm(c["urna"])) | set(norm(c["nome"]))
            score = len(ntoks & toks)
            if score > best_score:
                best, best_score = [c], score
            elif score == best_score and score > 0:
                best.append(c)
        if best_score > 0 and len(best) == 1:
            return best[0]["sq"], raw
        return None, raw
    return match


# ---------------- pipeline ----------------

def instituto_canon(text, aliases):
    raw = NUM_STRIP.sub("", text).strip().rstrip(".")
    amap = aliases.get("institutos", {})
    for k, v in amap.items():
        if k.upper() == raw.upper():
            return v
    return raw


def detect_base(kind, soma):
    if soma is None:
        return "desconhecida"
    if kind == "senado" and soma > 110:
        return "bruta_2votos"
    if 90 <= soma <= 104:
        return "normalizada_100"
    return "desconhecida"


def ingest_page(title, race_key_principal, race_key_senado, structure, aliases, report, cache_dir=None):
    cache_file = cache_dir and os.path.join(cache_dir, re.sub(r"[^\w]+", "_", title) + ".json")
    if cache_file and os.path.exists(cache_file):
        d = load_json(cache_file, None)
    else:
        d = api({"action": "parse", "page": title, "prop": "text|revid"})
        if cache_file:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False)
    revid = d["parse"]["revid"]
    html = d["parse"]["text"]["*"]
    w = PageWalker()
    w.feed(html)
    url = "https://pt.wikipedia.org/wiki/" + title.replace(" ", "_")
    polls = []
    for ctx, grid in w.items:
        kind, turno, pair = section_kind(ctx)
        if kind is None:
            continue
        year = year_from_context(ctx)
        if year is None:
            year = 2026  # seções sem subseção de ano (ex.: Senador na BA) são da safra corrente
            report.setdefault("ano_assumido_2026", []).append(f"{title} :: {ctx}")
        if year < 2025:
            continue
        race_key = race_key_senado if kind == "senado" else race_key_principal
        if race_key is None:
            continue
        race = structure["races"][race_key]
        matcher = build_matcher(race, aliases)
        cols, data_start = classify_header(grid)
        if not cols:
            report["tabelas_sem_header"].append(f"{title} :: {ctx}")
            continue
        cand_cols = []
        for idx, (k, txt) in enumerate(cols):
            if k == "cand":
                sq, raw = matcher(txt)
                cand_cols.append((idx, sq, raw))
                if sq is None:
                    report["candidatos_sem_match"].setdefault(f"{race_key} :: {raw}", 0)
                    report["candidatos_sem_match"][f"{race_key} :: {raw}"] += 1
        par_sqs = None
        if turno == 2 and pair:
            par_sqs = sorted([sq for _, sq, _ in cand_cols if sq is not None])
        for row in grid[data_start:]:
            if all(c["th"] for c in row):
                continue
            vals = {}
            numeros = []
            outros = indef = None
            for idx, (k, _txt) in enumerate(cols):
                if idx >= len(row):
                    continue
                cell = row[idx]["t"]
                if k == "instituto":
                    vals["instituto"] = cell
                elif k == "datas":
                    vals["datas"] = cell
                elif k == "amostra":
                    vals["amostra"] = cell
                elif k == "margem":
                    vals["margem"] = cell
                elif k == "outros":
                    outros = parse_pct(cell)
                elif k == "indefinidos":
                    v = parse_pct(cell)
                    if v is not None:
                        indef = (indef or 0) + v
            for idx, sq, raw in cand_cols:
                if idx >= len(row):
                    continue
                pct = parse_pct(row[idx]["t"])
                if pct is not None:
                    numeros.append({"sq": sq, "alias": raw, "pct": pct})
            if not numeros or "instituto" not in vals:
                continue
            ini, fim, raw_dates = parse_dates(vals.get("datas", ""), year)
            if fim is None:
                report["datas_nao_parseadas"].append(f"{title} :: {vals.get('datas', '')!r}")
            soma = sum(n["pct"] for n in numeros) + (outros or 0) + (indef or 0)
            inst = instituto_canon(vals["instituto"], aliases)
            poll = {
                "id": f"{re.sub(r'[^a-z0-9]+', '-', inst.lower()).strip('-')}-{race_key.lower()}-{fim or 'sdata'}"
                      + (f"-2t" if turno == 2 else ""),
                "race": race_key,
                "instituto": inst,
                "contratante": None,
                "tse_protocolo": None,
                "campo_ini": ini, "campo_fim": fim, "campo_raw": raw_dates,
                "divulgacao": None,
                "amostra": parse_amostra(vals.get("amostra", "")),
                "margem_pp": parse_pct(vals.get("margem", "")),
                "metodo": None,
                "cenario": "segundo_turno" if turno == 2 else "estimulada",
                "par_segundo_turno": par_sqs if turno == 2 else None,
                "base": detect_base(kind, soma),
                "soma_publicada": round(soma, 1),
                "numeros": numeros,
                "indefinidos_pct": {"indecisos": indef, "outros": outros},
                "fonte": {"tipo": "wikipedia", "url": url, "revid": revid,
                          "acesso": None},
                "flags": (["senado_2votos"] if kind == "senado" else []),
            }
            polls.append(poll)
    return polls


def main():
    cache_dir = None
    if "--cache" in sys.argv:
        cache_dir = sys.argv[sys.argv.index("--cache") + 1]
        os.makedirs(cache_dir, exist_ok=True)
    structure = load_json(STRUCT, None)
    aliases = load_json(ALIASES, {"institutos": {}, "candidatos": {}})
    report = {"candidatos_sem_match": {}, "datas_nao_parseadas": [], "tabelas_sem_header": []}

    jobs = [(PRES_TITLE, "PRES", None)]
    for uf, prep in sorted(UF_TITLES.items()):
        jobs.append((f"Pesquisas eleitorais para a eleição estadual de 2026 {prep}",
                     f"GOV-{uf}", f"SEN-{uf}"))
    jobs.append((DF_TITLE, "GOV-DF", "SEN-DF"))

    all_polls = []
    import datetime
    acesso = datetime.date.today().isoformat()
    for title, rk_main, rk_sen in jobs:
        try:
            polls = ingest_page(title, rk_main, rk_sen, structure, aliases, report, cache_dir)
        except Exception as e:  # página fora do padrão não derruba o run inteiro
            report.setdefault("paginas_com_erro", []).append(f"{title}: {e!r}")
            continue
        for p in polls:
            p["fonte"]["acesso"] = acesso
            # data no futuro = ano de seção mal assumido (seções sem ano) ou erro da fonte:
            # rebaixa 1 ano; persistindo futura, invalida e reporta (nunca em silêncio)
            if p["campo_fim"] and p["campo_fim"] > acesso:
                ini, fim = p["campo_ini"], p["campo_fim"]
                fim2 = f"{int(fim[:4]) - 1}{fim[4:]}"
                if fim2 <= acesso:
                    p["campo_fim"] = fim2
                    if ini:
                        p["campo_ini"] = f"{int(ini[:4]) - 1}{ini[4:]}"
                    report.setdefault("ano_rebaixado", []).append(p["id"])
                else:
                    report.setdefault("data_futura_invalidada", []).append(f"{p['id']} :: {fim}")
                    p["campo_ini"] = p["campo_fim"] = None
        all_polls.extend(polls)
        print(f"  {rk_main:8s} {len(polls):4d} pesquisas  ({title[:52]}…)")

    all_polls.sort(key=lambda p: (p["race"], p["campo_fim"] or "", p["instituto"], p["id"]))
    out = {"schema_version": 1, "updated_at": acesso, "polls": all_polls}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")

    os.makedirs(os.path.dirname(PENDING), exist_ok=True)
    with open(PENDING, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")

    n_unmatched = sum(report["candidatos_sem_match"].values())
    races = {p["race"] for p in all_polls}
    print(f"\nOK: {len(all_polls)} pesquisas em {len(races)} corridas -> data/live/polls.json")
    print(f"Sem match: {len(report['candidatos_sem_match'])} nomes ({n_unmatched} células) | "
          f"datas não parseadas: {len(report['datas_nao_parseadas'])} | relatório: data/eleicoes/aliases_pendentes.json")


if __name__ == "__main__":
    main()
