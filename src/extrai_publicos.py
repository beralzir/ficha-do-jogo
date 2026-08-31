#!/usr/bin/env python3
"""Extrator dos 5 públicos eleitorais (etapa C1a) -> data/publicos/audiencias.json

RODA LOCAL, NÃO NO CI: depende do PPTX na pasta iCloud, que o runner do GitHub não
acessa. O JSON gerado é versionado, e é dele que src/build_publicos.py (as páginas)
lê. Rode este script quando o PPTX mudar; o build das páginas roda sempre.

Fonte canônica: o PPTX "Perfil de grupos de eleitores" (Ibope Target Group Index,
TG BR 2025 R3), na pasta iCloud do projeto. Os `audiencia-*.json` que o Bera já
tinha são um SUBCONJUNTO dele: o PPTX traz ainda raça, estado civil, religião,
renda média familiar, % que trabalha e os universos absolutos (nacional e por
região). Por isso a fonte canônica passou a ser o PPTX, com os JSONs virando
GATE de conferência (src/test_publicos.py).

O PPTX guarda os números em tabelas de verdade (`<a:tbl>`), não em texto solto,
então a extração lê a estrutura e não depende de heurística de layout. Só stdlib.

CUIDADO com a regionalização: o slide 2 traz universos por região, e eles NÃO
representam o eleitorado (o TGI é painel de consumo de mídia, com cobertura
concentrada: 69% dos Lulistas no Sudeste, 2,86M no Nordeste). Ficam no JSON por
completude e com aviso, mas NÃO devem ligar público a UF em lugar nenhum.

Uso:  python3 src/extrai_publicos.py [--pptx CAMINHO]
      PPTX_PUBLICOS=/outro/caminho.pptx python3 src/extrai_publicos.py
"""
import html
import json
import os
import re
import sys
import unicodedata
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT = os.path.join(ROOT, "data", "publicos", "audiencias.json")
ICLOUD = os.path.expanduser(
    "~/Library/Mobile Documents/com~apple~CloudDocs/Almap/Projetos/Eleições 2026")
PPTX = os.environ.get("PPTX_PUBLICOS", os.path.join(ICLOUD, "Perfil de grupos de eleitores.pptx"))
REF_DIR = os.environ.get("PUBLICOS_REF_DIR", ICLOUD)   # audiencia-*.json (resumo curado)

FONTE = "Ibope Target Group Index · TG BR 2025 R3"

# Cada público ocupa 7 slides seguidos, a partir da capa. Ordem do documento.
PUBLICOS = [
    ("lulistas", "Lulistas", 3),
    ("esquerda-nao-lulista", "Esquerda não Lulista", 10),
    ("independentes", "Independentes", 17),
    ("direita-nao-bolsonarista", "Direita não Bolsonarista", 24),
    ("bolsonaristas", "Bolsonaristas", 31),
]
SLIDE_UNIVERSOS = 2
REGIOES = ["NORTE", "NORDESTE", "SUL", "SUDESTE", "CENTRO-OESTE"]

# header da 1ª célula -> chave no JSON. Gênero tem header vazio (é o default).
# As chaves são comparadas SEM acento (_norm decompõe e remove diacríticos, e o
# ç vira c), então ficam escritas já normalizadas de propósito.
POR_HEADER = {
    "raca": "racas", "faixa": "idades", "estado civil": "estados_civis",
    "estagio": "estagios_vida", "classe": "classes_sociais", "religiao": "religioes",
}


def _txt(frag):
    return " ".join(html.unescape(t) for t in re.findall(r"<a:t>(.*?)</a:t>", frag, re.S))


def _limpa(s):
    return re.sub(r"\s+", " ", s or "").strip()


def _norm(s):
    s = unicodedata.normalize("NFD", s or "")
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower().strip()


def _num(s, pct=False):
    """'41.4%' -> 41.4 · '1.234.567' -> 1234567 · 'R$ 3.680' -> 3680 · '' -> None."""
    t = _limpa(s).replace("%", "").replace("R$", "").strip()
    if not t:
        return None
    if pct:
        t = t.replace(",", ".")
        m = re.search(r"-?\d+(?:\.\d+)?", t)
        return float(m.group()) if m else None
    t = re.sub(r"[.\s]", "", t).replace(",", ".")
    m = re.search(r"-?\d+(?:\.\d+)?", t)
    if not m:
        return None
    v = float(m.group())
    return int(v) if v == int(v) else v


class Deck:
    def __init__(self, caminho):
        if not os.path.exists(caminho):
            sys.exit(f"ERRO: PPTX não encontrado em {caminho}\n"
                     f"Passe --pptx CAMINHO ou defina PPTX_PUBLICOS.")
        self.z = zipfile.ZipFile(caminho)
        self.caminho = caminho

    def xml(self, n):
        return self.z.read(f"ppt/slides/slide{n}.xml").decode("utf-8")

    def texto(self, n):
        return _limpa(_txt(self.xml(n)))

    def tabelas(self, n):
        """[[celula, ...], ...] por tabela, na ordem do documento."""
        out = []
        for tbl in re.findall(r"<a:tbl>.*?</a:tbl>", self.xml(n), re.S):
            linhas = []
            for tr in re.findall(r"<a:tr[ >].*?</a:tr>", tbl, re.S):
                celulas = [_limpa(_txt(tc)) for tc in
                           re.findall(r"<a:tc(?:\s[^>]*)?>(.*?)</a:tc>", tr, re.S)]
                if any(celulas):
                    linhas.append(celulas)
            if linhas:
                out.append(linhas)
        return out


def linhas_vert_afi(tabela, chave_rotulo="label"):
    """Tabela padrão do deck: [rótulo, Vert%, Afi]. Descarta o header."""
    itens = []
    for r in tabela[1:]:
        if len(r) < 3:
            continue
        rot = _limpa(r[0])
        pct, afi = _num(r[1], pct=True), _num(r[2])
        if not rot or pct is None:
            continue
        itens.append({chave_rotulo: rot, "percent": pct, "affinityScore": afi})
    return itens


def classifica(tabela):
    """Descobre o que a tabela é pelo header da primeira célula."""
    h = _norm(tabela[0][0]) if tabela and tabela[0] else ""
    if h in POR_HEADER:
        return POR_HEADER[h]
    rotulos = {_norm(r[0]) for r in tabela[1:] if r}
    if {"homem", "mulher"} & rotulos:
        return "generos"                      # única tabela de header vazio
    if "internet" in rotulos or "tv aberta" in rotulos:
        return "habitos_midia"
    if "melhorar a economia" in rotulos:
        return "prioridades_voto"
    return None


def universos(deck):
    """Slide 2: universo nacional e por região, por cluster."""
    txt = deck.texto(SLIDE_UNIVERSOS)
    out = {}
    for _, nome, _ in PUBLICOS:
        out[nome] = {"nacional": None, "regioes": {}}
    # o slide lista, por região, os pares (%, absoluto) na ordem dos 5 clusters
    for linha in ["NACIONAL"] + REGIOES:
        m = re.search(re.escape(linha) + r"\*?\s+((?:\d+%\s+[\d.]+\s*){5})", txt)
        if not m:
            continue
        pares = re.findall(r"(\d+)%\s+([\d.]+)", m.group(1))
        for (pct, absoluto), (_, nome, _) in zip(pares, PUBLICOS):
            v = _num(absoluto)
            if linha == "NACIONAL":
                out[nome]["nacional"] = v
            else:
                out[nome]["regioes"][linha] = v
    return out


def extrai_publico(deck, slug, nome, capa):
    d = {"slug": slug, "name": nome, "fonte": FONTE}

    # capa: "Lulistas 27.456.185 eleitores"
    m = re.search(r"([\d.]{7,})\s*eleitores", deck.texto(capa))
    d["universo"] = _num(m.group(1)) if m else None
    # O deck traz a definição LONGA; o export JSON traz um resumo curto curado.
    # São textos diferentes e os dois servem: o resumo vai no card do índice, a
    # definição longa vai na ficha. Por isso o extrator lê as duas fontes.
    d["definicaoDeck"] = _limpa(re.sub(r"^Definição do Público\s*" + re.escape(nome),
                                       "", deck.texto(capa + 1))).strip()
    ref = os.path.join(REF_DIR, f"audiencia-{slug}.json")
    if os.path.exists(ref):
        with open(ref, encoding="utf-8") as f:
            d["publicDefinition"] = _limpa(json.load(f).get("publicDefinition") or "")
    else:
        d["publicDefinition"] = None

    # tabelas: demográfico (capa+2), classe/religião (capa+3), interesses (+4),
    # mídia (+5), prioridades (+6)
    for off in (2, 3, 4, 5, 6):
        for tabela in deck.tabelas(capa + off):
            tipo = classifica(tabela)
            if tipo == "interesses" or (off == 4 and tipo is None):
                d["interesses"] = linhas_vert_afi(tabela, "description")
            elif tipo in ("habitos_midia", "prioridades_voto"):
                d[tipo] = linhas_vert_afi(tabela, "description")
            elif tipo:
                d[tipo] = linhas_vert_afi(tabela)

    # números soltos no texto dos slides de demografia e renda
    t = deck.texto(capa + 2) + " " + deck.texto(capa + 3)
    for chave, padrao in (
            ("percentWithChildren", r"(?:Pai\s*/?\s*M[ãa]e\s*/?\s*Respons[áa]vel[^:]*):\s*([\d.,]+)\s*%"),
            ("percentHigherEducation", r"Educa[çc][ãa]o Superior[^:]*:\s*([\d.,]+)\s*%"),
            ("percentWorking", r"Trabalha\s*:\s*([\d.,]+)\s*%"),
            ("rendaMediaFamiliar", r"Renda M[ée]dia Mensal Familiar:\s*R?\$?\s*([\d.,]+)")):
        m = re.search(padrao, t, re.I)
        d[chave] = _num(m.group(1), pct=chave != "rendaMediaFamiliar") if m else None
    return d


def main():
    caminho = PPTX
    if "--pptx" in sys.argv:
        caminho = sys.argv[sys.argv.index("--pptx") + 1]
    deck = Deck(caminho)

    uni = universos(deck)
    publicos = []
    for slug, nome, capa in PUBLICOS:
        p = extrai_publico(deck, slug, nome, capa)
        if p["universo"] is None:
            p["universo"] = uni.get(nome, {}).get("nacional")
        p["universoPorRegiao"] = uni.get(nome, {}).get("regioes", {})
        publicos.append(p)

    doc = {
        "schema_version": 1,
        "fonte": FONTE,
        "fonte_arquivo": os.path.basename(caminho),
        "avisos": [
            "TGI é painel de consumo de mídia, NÃO amostra do eleitorado brasileiro.",
            "universoPorRegiao reflete a cobertura do painel, não a distribuição do "
            "eleitorado (69% dos Lulistas no Sudeste, 2,86M no Nordeste). NÃO usar para "
            "ligar público a UF.",
            "prioridades_voto sai do campo 'purchaseReasons' do export original, cujo "
            "nome não descreve o conteúdo.",
            "publicDefinition é o resumo curado do export; definicaoDeck é o texto longo "
            "do PPTX. São dois textos diferentes, não versões do mesmo.",
        ],
        "publicos": publicos,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")

    print(f"OK -> {os.path.relpath(OUT, ROOT)}")
    for p in publicos:
        dims = [k for k in ("generos", "idades", "racas", "estados_civis", "estagios_vida",
                            "classes_sociais", "religioes", "interesses", "habitos_midia",
                            "prioridades_voto") if p.get(k)]
        print(f"  {p['slug']:26s} universo {p['universo']:>11,} · {len(dims)} dimensões"
              .replace(",", "."))


if __name__ == "__main__":
    main()
