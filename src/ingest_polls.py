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
import collections
import datetime as dt
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
    context = headings (h2/h3/h4) vigentes + títulos de blocos recolhíveis
    (`{{hidden begin|title=...}}`) abertos. Expande rowspan/colspan.

    Os recolhíveis vêm DEPOIS dos headings porque são um eixo de aninhamento
    independente: um `hidden begin` tanto pode envolver headings quanto morar
    dentro de um. Como `year_from_context` lê de dentro para fora, um ano
    explícito no recolhível ganha de uma faixa ambígua na seção, que é
    exatamente o caso de `Primeiro Turno/2023-2025` (seção diz "2023 - 2025",
    o recolhível diz 2025, 2024 ou 2023). Sem ler o recolhível, a página
    inteira era lida como 2023 e caía no filtro `>= 2025`.

    Também coleta `self.hatnotes` = [(context, [títulos linkados])] dos blocos
    "Ver artigo principal" / "Esta seção é um excerto de", que é como a
    Wikipédia sinaliza que o conteúdo mudou de página.
    """

    def __init__(self):
        super().__init__()
        self.heads = {2: None, 3: None, 4: None}
        self.items = []
        self.hatnotes = []
        self._h = None          # heading aberto (nível)
        self._htxt = ""
        self._tdepth = 0
        self._rows = None       # tabela wikitable de nível 1 em captura
        self._row = None
        self._cell = None
        self._ddepth = 0        # profundidade de <div>, para casar abre/fecha
        self._colls = []        # [[ddepth_de_abertura, título]] recolhíveis abertos
        self._captit = None     # ddepth do .hidden-title em captura
        self._titbuf = ""
        self._hat = None        # ddepth do .hatnote em captura
        self._hatlinks = []

    def ctx(self):
        return ([self.heads[2], self.heads[3], self.heads[4]]
                + [t for _, t in self._colls if t])

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "div":
            self._ddepth += 1
            cls = a.get("class") or ""
            if "hidden-begin" in cls:
                self._colls.append([self._ddepth, None])
            elif "hidden-title" in cls and self._colls:
                self._captit, self._titbuf = self._ddepth, ""
            elif "hatnote" in cls:
                self._hat, self._hatlinks = self._ddepth, []
        elif tag == "a" and self._hat is not None:
            if a.get("title"):
                self._hatlinks.append(a["title"])
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
        if tag == "div":
            if self._captit == self._ddepth:
                if self._colls:
                    self._colls[-1][1] = re.sub(r"\s+", " ", self._titbuf).strip()
                self._captit = None
            if self._hat == self._ddepth:
                if self._hatlinks:
                    self.hatnotes.append((self.ctx(), list(self._hatlinks)))
                self._hat, self._hatlinks = None, []
            if self._colls and self._colls[-1][0] == self._ddepth:
                self._colls.pop()
            self._ddepth -= 1
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
                    self.items.append((self.ctx(), grid))
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
        if self._captit is not None:
            self._titbuf += d
        elif self._h is not None and self._tdepth == 0:
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
    top = (ctx[0] or "").lower() if ctx else ""
    if "senad" in top:
        return "senado", 1, None
    if "segundo turno" in top:
        pair = None
        # só os dois níveis de heading logo abaixo do topo, como antes: o ctx
        # cresceu (recolhíveis, contexto herdado de subpágina) e varrer tudo
        # mudaria o pareamento do 2º turno, que hoje está saudável.
        for h in (ctx[1:2] + ctx[2:3]):
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


MAX_SUB_DEPTH = 2   # página -> subpágina -> subpágina. Além disso é laço ou lixo.
SUBPAGINAS_OK = os.path.join(ROOT, "data", "eleicoes", "subpaginas_permitidas.json")


def subpaginas_permitidas():
    """Títulos autorizados, do arquivo versionado. Ausente = conjunto vazio.

    Vazio NÃO é 'libera tudo': é 'nada autorizado', e toda subpágina encontrada
    vira desconhecida e derruba o run. Fail-closed também quando o arquivo some.
    """
    d = load_json(SUBPAGINAS_OK, {"permitidas": []})
    return {e["titulo"] for e in d.get("permitidas", []) if e.get("titulo")}


def subpaginas(w, title, permitidas=None, report=None):
    """Hatnotes que apontam para SUBPÁGINA da própria página ('Pai/Filho').

    DUAS travas, e elas defendem coisas diferentes:

    1. O PREFIXO impede seguir artigo alheio: a página linka as eleições de 2010,
       2014, 2018 e 2022, e sem o prefixo um 'Ver artigo principal' puxaria
       qualquer uma delas para dentro da corrida.
    2. A ALLOWLIST (`data/eleicoes/subpaginas_permitidas.json`) impede que uma
       subpágina RECÉM-CRIADA vire fonte sem ninguém olhar. Risco R1 do
       docs/plano-risco-eleicoes.md: seguir link lido do conteúdo da fonte não
       muda QUEM pode injetar, continua sendo qualquer editor da Wikipédia, mas
       muda a DETECTABILIDADE. Forjar tabela dentro de um dos 28 artigos fixos
       tende a ser revertido por quem vigia aquele artigo; criar um artigo novo,
       sem observadores, e apontar um hatnote de uma linha para ele, não.

    Subpágina fora da lista NÃO é ingerida e vai para `subpaginas_desconhecidas`,
    que derruba o run em main() com exit 7. Falhar é o comportamento certo: fonte
    nova é evento que pede revisão humana, não dado.
    """
    pref = title + "/"
    permitidas = subpaginas_permitidas() if permitidas is None else permitidas
    out, vistos = [], set()
    for ctx, links in w.hatnotes:
        for t in links:
            if not t.startswith(pref) or t in vistos:
                continue
            vistos.add(t)
            if t not in permitidas:
                if report is not None:
                    report.setdefault("subpaginas_desconhecidas", []).append(
                        f"{title} :: {t}")
                continue
            out.append((t, [c for c in ctx if c]))
    return out


def ingest_page(title, race_key_principal, race_key_senado, structure, aliases, report,
                cache_dir=None, ctx_base=(), depth=0, seen=None):
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
        # contexto herdado da seção que apontou para esta subpágina: sem ele a
        # subpágina não sabe que é "Primeiro turno" (ela começa direto nos meses).
        ctx = list(ctx_base) + list(ctx)
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

    # SUBPÁGINAS (incidente de 18/09/2026). Em setembro os editores quebraram o
    # 1º turno da presidencial em `.../Primeiro Turno/2026/Janeiro a Agosto` e
    # `.../Primeiro Turno/2023-2025`, deixando na página-mãe só Setembro mais
    # Agosto por transclusão. O ingest lia só a página-mãe e perdeu 452 das 510
    # estimuladas sem falhar, porque continuava recebendo pesquisa nova. Seguir o
    # hatnote é o que torna a quebra de página um não-evento em vez de perda muda.
    if seen is None:
        seen = {title}
    if depth < MAX_SUB_DEPTH:
        for sub, sub_ctx in subpaginas(w, title, report=report):
            if sub in seen:
                continue
            seen.add(sub)
            report.setdefault("subpaginas_seguidas", []).append(f"{title} :: {sub}")
            try:
                polls += ingest_page(sub, race_key_principal, race_key_senado, structure,
                                     aliases, report, cache_dir, ctx_base=sub_ctx,
                                     depth=depth + 1, seen=seen)
            except Exception as e:   # subpágina quebrada não derruba a página-mãe
                report.setdefault("paginas_com_erro", []).append(f"{sub}: {e!r}")
    return polls


# ---------------- GATE de plausibilidade (C0-c, plano-risco-eleicoes.md) ------
# O ingest lê a Wikipédia, que qualquer pessoa edita, e o cron publica sem humano
# no meio. Até 31/08/2026 não havia NENHUMA validação de entrada: medido no plano
# de risco, uma única linha forjada valia 67,9% do agregado em GOV-RR/SEN-RR e
# 4,4% na presidencial. Este gate fecha a porta. Espelha os gates do ingest.py da
# edição Copa (quorum/plausibilidade/diff-before-write), adaptados a pesquisa.
#
# Limiar CALIBRADO no dado real de 29/08 (3.373 pesquisas), não chutado: o desvio
# entre pesquisa real e consenso de CENÁRIO COMPATÍVEL tem p99 = 19,7pp, e 25pp
# reprova 0,42% das células legítimas. Comparar sem casar cenário dá p90 = 15pp
# (conjuntos de candidatos diferentes), e reprovaria 10% do que é legítimo.
QUARANTINE = os.path.join(ROOT, "data", "eleicoes", "quarentena.json")
DIFFOUT = os.path.join(ROOT, "data", "eleicoes", "ingest_diff.txt")
GATE_DEV_PP = float(os.environ.get("GATE_DEV_PP", "25"))      # desvio máx. vs consenso
GATE_DEV_INTER_PP = float(os.environ.get("GATE_DEV_INTER_PP", "40"))  # idem, modo interseção
GATE_MIN_INTER = int(os.environ.get("GATE_MIN_INTER", "3"))    # candidatos em comum mínimos
GATE_JACCARD = float(os.environ.get("GATE_JACCARD", "0.8"))   # cenário compatível
GATE_MIN_BASE = int(os.environ.get("GATE_MIN_BASE", "3"))     # pesquisas p/ ter consenso
GATE_WINDOW_D = int(os.environ.get("GATE_WINDOW_D", "60"))    # janela do consenso
GATE_MAX_QUAR = int(os.environ.get("GATE_MAX_QUAR", "3"))     # acima disso, run falha
GATE_AMOSTRA = (100, 100000)


def _shares(p):
    """{sq: share} entre os candidatos casados, base-independente."""
    tot = sum(n["pct"] for n in p["numeros"] if n.get("sq") and n["pct"] > 0)
    if tot <= 0:
        return {}
    return {n["sq"]: n["pct"] / tot for n in p["numeros"] if n.get("sq") and n["pct"] > 0}


def _keyset(s):
    """Candidatos com peso relevante: é o que define o 'cenário' da pesquisa."""
    return frozenset(k for k, v in s.items() if v >= 0.03)


def _consenso(p, base, s):
    """Consenso ponderado da corrida, em dois modos.

    Devolve (estrito, largo), cada um None ou (cons, n_pesquisas):
    - estrito: só pesquisas de CENÁRIO COMPATÍVEL (Jaccard >= GATE_JACCARD sobre
      os candidatos relevantes). Comparação direta, limiar GATE_DEV_PP.
    - largo: todas as pesquisas do mesmo cenário na janela, sem exigir a mesma
      lista de candidatos. Serve de fallback para o modo interseção, porque
      exigir cenário idêntico deixaria escapar quem simplesmente lista menos
      candidatos.
    """
    if not p.get("campo_fim") or not s:
        return None, None
    ks = _keyset(s)
    d0 = dt.date.fromisoformat(p["campo_fim"])
    acc_e = collections.defaultdict(float); w_e = 0.0; n_e = 0
    acc_l = collections.defaultdict(float); w_l = 0.0; n_l = 0
    for q in base:
        if not q.get("campo_fim") or q["cenario"] != p["cenario"]:
            continue
        age = (d0 - dt.date.fromisoformat(q["campo_fim"])).days
        if not (0 <= age <= GATE_WINDOW_D):
            continue
        sq_ = _shares(q)
        if not sq_:
            continue
        w = 0.5 ** (age / 21.0)
        n_l += 1; w_l += w
        for k, v in sq_.items():
            acc_l[k] += w * v
        kq = _keyset(sq_)
        if ks and kq and len(ks | kq) and len(ks & kq) / len(ks | kq) >= GATE_JACCARD:
            n_e += 1; w_e += w
            for k, v in sq_.items():
                acc_e[k] += w * v
    estrito = ({k: v / w_e for k, v in acc_e.items()}, n_e) if n_e >= GATE_MIN_BASE and w_e > 0 else None
    largo = ({k: v / w_l for k, v in acc_l.items()}, n_l) if n_l >= GATE_MIN_BASE and w_l > 0 else None
    return estrito, largo


def _pior_desvio(s, cons, intersecao):
    """Maior desvio (pp) entre a pesquisa e o consenso. (None, None) se não dá
    para comparar. No modo interseção, compara só os candidatos presentes nos
    dois lados, re-normalizados, e exige pelo menos 2 deles."""
    if intersecao:
        K = [k for k in s if k in cons]
        # Exigir >= 3 candidatos em comum. Com 2, re-normalizar amplifica qualquer
        # diferenca e o falso positivo pula de 2,3% para 8,7% no dado real. Com
        # menos que isso a pesquisa nao e bloqueada: sai corroborada=False.
        if len(K) < GATE_MIN_INTER:
            return None, None
        ts = sum(s[k] for k in K); tc = sum(cons[k] for k in K)
        if ts <= 0 or tc <= 0:
            return None, None
        pares = [(abs(s[k] / ts - cons[k] / tc) * 100, k) for k in K]
    else:
        pares = [(abs(v - cons.get(k, 0.0)) * 100, k) for k, v in s.items()
                 if cons.get(k, 0) > 0.02 or v > 0.02]
    if not pares:
        return None, None
    pior, quem = max(pares, key=lambda t: (t[0], t[1]))   # determinístico
    return pior, quem


def sanity_violations(p):
    """Sanidade absoluta: barata e pega adulteração grosseira. Roda em TODAS."""
    bad = []
    for n in p["numeros"]:
        if not isinstance(n["pct"], (int, float)) or not (0 <= n["pct"] <= 100):
            bad.append(f"pct fora de [0,100]: {n['alias']}={n['pct']}")
    a = p.get("amostra")
    if a is not None and not (GATE_AMOSTRA[0] <= a <= GATE_AMOSTRA[1]):
        bad.append(f"amostra implausível: {a}")
    soma = sum(n["pct"] for n in p["numeros"] if n["pct"] > 0)
    # bruta_2votos legitimamente passa de 100 (Senado, 2 votos por eleitor)
    teto = 240 if p.get("base") == "bruta_2votos" else 130
    if soma > teto:
        bad.append(f"soma {soma:.1f} acima do teto {teto} para base {p.get('base')}")
    # NÃO há guarda de "linha com um número só" aqui, e isso foi decidido em
    # 25/09/2026 depois de um erro meu: um guarda assim quarentenava linhas de
    # cenário "candidato × Outros" (legítimas: um candidato contra o campo, com
    # o resto em `indefinidos.outros`), e com GATE_MAX_QUAR=3 por rodada derrubou
    # o cron na primeira reestruturação de tabela da Wikipédia (5 linhas em
    # GOV-SE e GOV-AL). Quarentenada não vira "vista" (prev_ids vem do polls.json
    # gravado), então reprovaria de novo todo dia. Quem segura a linha de um
    # número só é o MIN_CASADOS do motor (eleicoes_model.usable_polls), e basta:
    # a variante de um candidato perde para a mais cheia no colapso por chave e,
    # quando é a única, é descartada. O ingest PRESERVA o registro.
    return bad


def plausibility_gate(all_polls, prev_ids, report):
    """Aplica o gate SÓ às pesquisas novas (as já publicadas não são reescritas).

    Devolve (aceitas, quarentenadas). Uma pesquisa nova é quarentenada quando
    falha a sanidade absoluta, ou quando desvia mais que GATE_DEV_PP do consenso
    ponderado de cenário compatível. Corrida sem base comparável não bloqueia:
    a pesquisa entra marcada com corroborada=False, e a incerteza é declarada,
    nunca silenciosa (invariante 5 da edição).
    """
    aceitas, quarentena = [], []
    por_corrida = collections.defaultdict(list)
    for p in all_polls:
        por_corrida[p["race"]].append(p)

    for race, ps in sorted(por_corrida.items()):
        ps.sort(key=lambda q: (q["campo_fim"] or "", q["id"]))
        base = []  # pesquisas já aceitas desta corrida, em ordem cronológica
        for p in ps:
            novo = p["id"] not in prev_ids
            if not novo:
                p.setdefault("corroborada", None)
                base.append(p)
                aceitas.append(p)
                continue

            motivos = sanity_violations(p)
            s_ = _shares(p)
            estrito, largo = _consenso(p, base, s_)

            if estrito:
                cons, n_comp = estrito
                pior, quem = _pior_desvio(s_, cons, intersecao=False)
                if pior is not None and pior > GATE_DEV_PP:
                    motivos.append(f"desvio {pior:.1f}pp vs consenso de {n_comp} pesquisas de "
                                   f"cenario compativel (limiar {GATE_DEV_PP:.0f}pp), sq={quem}")
                p["corroborada"] = not motivos
            elif largo:
                # Cenario diferente (lista de candidatos distinta) NAO e desculpa
                # para nao checar: listar menos candidatos seria fuga trivial do
                # gate (achado do erro plantado no test_ingest_polls_gate.py).
                # Compara sobre a intersecao RE-NORMALIZADA, com limiar proprio:
                # p99 = 42pp nesse modo, contra 19,7pp no estrito.
                cons, n_comp = largo
                pior, quem = _pior_desvio(s_, cons, intersecao=True)
                if pior is None:
                    p["corroborada"] = False        # menos de 2 candidatos em comum
                else:
                    if pior > GATE_DEV_INTER_PP:
                        motivos.append(f"desvio {pior:.1f}pp na intersecao re-normalizada vs "
                                       f"{n_comp} pesquisas da corrida (limiar "
                                       f"{GATE_DEV_INTER_PP:.0f}pp), sq={quem}")
                    p["corroborada"] = not motivos
            else:
                # base fraca de verdade: NAO bloqueia (senao corrida pouco
                # pesquisada some do site), mas a falta de corroboracao viaja
                # no dado (invariante 5: prior declarado, nunca silencioso).
                p["corroborada"] = False

            if motivos:
                quarentena.append({"id": p["id"], "race": race, "instituto": p["instituto"],
                                   "campo_fim": p["campo_fim"], "motivos": motivos})
            else:
                base.append(p)
                aceitas.append(p)

    report["gate_quarentena"] = quarentena
    report["gate_params"] = {"dev_pp": GATE_DEV_PP, "jaccard": GATE_JACCARD,
                             "min_base": GATE_MIN_BASE, "janela_d": GATE_WINDOW_D}
    aceitas.sort(key=lambda p: (p["race"], p["campo_fim"] or "", p["instituto"], p["id"]))
    return aceitas, quarentena


def write_diff(prev_polls, aceitas, quarentena):
    """Diff-before-write legível: o que este run mudou, para auditoria humana.

    Conta só pesquisa REAL nas duas pontas. A sintética não vem da fonte: main()
    a reanexa do arquivo anterior DEPOIS deste diff, então ela nunca está em
    `aceitas`. Até 25/09/2026 ela entrava no "antes" e nos sumidos, e toda rodada
    gravava "- sumiu da fonte" em falso para o mock da vox. O cabeçalho declara
    quantas ficaram fora da conta, para o "antes" fechar com o polls.json anterior.
    """
    prev_ids = {p["id"] for p in prev_polls}
    prev_reais = [p for p in prev_polls if not p.get("sintetico")]
    novos = [p for p in aceitas if p["id"] not in prev_ids]
    sumidos = ({p["id"] for p in prev_reais}
               - {p["id"] for p in aceitas} - {q["id"] for q in quarentena})
    linhas = [f"ingest_polls diff · {dt.date.today().isoformat()}",
              f"antes: {len(prev_reais)} | depois: {len(aceitas)} | "
              f"novas: {len(novos)} | quarentena: {len(quarentena)} | sumidas: {len(sumidos)} | "
              f"sintéticas fora da conta: {len(prev_polls) - len(prev_reais)}", ""]
    for p in sorted(novos, key=lambda p: (p["race"], p["campo_fim"] or "")):
        corr = "" if p.get("corroborada") else "  [NAO CORROBORADA]"
        linhas.append(f"+ {p['race']:8s} {p['campo_fim'] or '????-??-??'} {p['instituto']}{corr}")
    for q in quarentena:
        linhas.append(f"! QUARENTENA {q['race']:8s} {q['campo_fim']} {q['instituto']}")
        for m in q["motivos"]:
            linhas.append(f"    motivo: {m}")
    for i in sorted(sumidos):
        linhas.append(f"- sumiu da fonte: {i}")
    txt = "\n".join(linhas) + "\n"
    with open(DIFFOUT, "w", encoding="utf-8") as f:
        f.write(txt)
    return txt


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
    acesso = dt.date.today().isoformat()
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

    # FONTE NOVA derruba o run (R1). Antes de qualquer escrita: subpágina fora da
    # allowlist não foi ingerida, e o run falha para que um humano olhe a página
    # na Wikipédia e decida. Publicar o resto em silêncio esconderia o evento.
    desconhecidas = report.get("subpaginas_desconhecidas") or []
    if desconhecidas:
        print(f"\nGATE DE FONTE REPROVADO: {len(desconhecidas)} subpágina(s) não "
              f"autorizada(s) apontadas por hatnote. NADA foi escrito.", file=sys.stderr)
        for d in desconhecidas:
            print(f"  {d}", file=sys.stderr)
        print("\nAbra cada uma na Wikipédia, confira que é o histórico legítimo da "
              "corrida e, só então, acrescente o título em "
              "data/eleicoes/subpaginas_permitidas.json com a data da revisão. "
              "Ver R1 em docs/plano-risco-eleicoes.md.", file=sys.stderr)
        sys.exit(7)

    # A página-mãe transclui um excerto da subpágina (Agosto), então a MESMA
    # pesquisa chega duas vezes. Dedup por assinatura de conteúdo, não por `id`:
    # `id` não é único de propósito (variantes de cenário do mesmo instituto/data
    # compartilham id), então deduplicar por id apagaria cenário legítimo.
    vistas, unicas, repetidas = set(), [], 0
    for p in all_polls:
        par = p.get("par_segundo_turno")
        sig = (p["race"], p["cenario"], p["instituto"], p["campo_ini"], p["campo_fim"],
               tuple(par) if isinstance(par, list) else par,
               tuple(sorted((str(n["sq"]), n.get("alias") or "", n["pct"]) for n in p["numeros"])))
        if sig in vistas:
            repetidas += 1
            continue
        vistas.add(sig)
        unicas.append(p)
    if repetidas:
        report["duplicatas_removidas"] = repetidas
    all_polls = unicas

    all_polls.sort(key=lambda p: (p["race"], p["campo_fim"] or "", p["instituto"], p["id"]))

    # GATE de plausibilidade + diff-before-write (C0-c). O gate roda só nas
    # pesquisas NOVAS: o que já foi publicado não é reescrito retroativamente.
    prev = load_json(OUT, None) or {}
    prev_polls = prev.get("polls", [])
    prev_ids = {p["id"] for p in prev_polls}
    all_polls, quarentena = plausibility_gate(all_polls, prev_ids, report)
    diff_txt = write_diff(prev_polls, all_polls, quarentena)

    # PESQUISA SINTÉTICA NÃO É DO INGEST: preserva as linhas do run anterior.
    # Este arquivo produz pesquisa REAL lida da Wikipédia e reescreve o polls.json
    # inteiro; as linhas sintéticas nascem em `synths_para_polls.py` e não têm como
    # ser reproduzidas aqui. Sem este carry-forward, todo ingest apagava o synth, e
    # em 21/09/2026 isso deixou de ser inofensivo: com o harness fail-closed, o
    # `test_synths_gate` reprova na pré-condição ("existe ao menos 1 sintética para
    # testar") e o pipeline inteiro fica vermelho. O cron quebraria no primeiro
    # ciclo com ingestão de verdade.
    # Só carrega o que JÁ estava marcado `sintetico: true` no arquivo anterior, e o
    # gate de plausibilidade nem as vê, porque não são novas: nada aqui é caminho
    # para uma sintética entrar no forecast oficial, que segue barrado por
    # POLL_SOURCE no motor e provado pelo test_synths_gate.
    preservadas = [p for p in prev_polls if p.get("sintetico")]
    if preservadas:
        all_polls += preservadas
        report["sinteticas_preservadas"] = len(preservadas)

    # schema v2 (C3): a flag `sintetico` passa a ser OBRIGATÓRIA em toda pesquisa.
    # Estrutural, não convenção: o modelo recusa poll sem a flag em vez de assumir
    # que é real. Assumir seria o caminho pelo qual um synth entraria no oficial
    # num refactor futuro, exatamente o que a decisão do Bera proíbe.
    for _p in all_polls:
        _p["sintetico"] = bool(_p.get("sintetico", False))
    out = {"schema_version": 2, "updated_at": acesso, "polls": all_polls}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")

    os.makedirs(os.path.dirname(QUARANTINE), exist_ok=True)
    with open(QUARANTINE, "w", encoding="utf-8") as f:
        json.dump({"updated_at": acesso, "params": report["gate_params"],
                   "quarentena": quarentena}, f, ensure_ascii=False, indent=1)
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
    print(diff_txt.split("\n")[1])
    n_semcorr = sum(1 for p in all_polls if p.get("corroborada") is False)
    print(f"Gate: {len(quarentena)} em quarentena | {n_semcorr} sem corroboração (base fraca)")
    if len(quarentena) > GATE_MAX_QUAR:
        print(f"\nGATE REPROVADO: {len(quarentena)} pesquisas em quarentena numa só rodada "
              f"(teto {GATE_MAX_QUAR}). Isso é quebra da fonte ou adulteração: revise "
              f"data/eleicoes/quarentena.json ANTES de publicar.", file=sys.stderr)
        sys.exit(4)


if __name__ == "__main__":
    main()
