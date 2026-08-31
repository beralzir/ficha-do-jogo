#!/usr/bin/env python3
"""
Páginas dos 5 públicos eleitorais (etapa C1c) -> dist/eleicoes_publico*.html

Gera, estático-primeiro e zero-dep, reusando shell.py/theme.py:
  - eleicoes_publicos.html          índice: a mão de 5 cartas, comparáveis lado a lado
  - eleicoes_publico_<slug>.html    5 fichas: carta grande + radar + perícias

Direção visual "B · Carta", escolhida pelo Bera em 31/08/2026 a partir de 3
direções em protótipo (risca-de-giz -> huashu-design). A carta com o radar como
brasão é a leitura mais literal da marca ("ficha de personagem"), e como os 5
públicos saem com radares visualmente opostos, o índice se explica sozinho.

RESTRIÇÕES DE CONTEÚDO (decisões do Bera, 31/08; não afrouxar sem ele):
  1. Publica só o DERIVADO. Nada de tabela de percentual e afinidade linha a
     linha: o dado bruto é licenciado e fica no repo privado.
  2. NUNCA nomear a fonte em página pública. Usar FONTE_PUBLICA abaixo.
  3. SEM figura humana em ilustração (risco de estereótipo político).
  4. A ressalva "não é pesquisa eleitoral" é obrigatória em toda página, visível,
     não em rodapé escondido: é ela que impede o leitor de ler a ficha como
     pesquisa de intenção de voto.
  5. NENHUM recorte por UF. O painel concentra 69% de um grupo no Sudeste e
     2,86M no Nordeste; é cobertura do painel, não eleitorado. Ligar público a
     estado seria erro grave (ver docs/plano-fase-c-eleicoes.md, C1c).

Lê data/publicos/audiencias.json, gerado por src/extrai_publicos.py (que roda
LOCAL, porque depende do PPTX no iCloud). Este builder roda no CI.
"""
import html
import json
import re
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_eleicoes          # reusa o CSS BASE da edição: mesmo design system
import shell
import theme

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
FONTE = os.path.join(ROOT, "data", "publicos", "audiencias.json")

D = json.load(open(FONTE, encoding="utf-8"))
PUB = D["publicos"]
TOTAL = sum(p["universo"] for p in PUB)

FONTE_PUBLICA = "Painel sindicalizado de consumo de mídia, base 2025."
RESSALVA = (
    "<b>Não é pesquisa eleitoral.</b> Os números descrevem perfil e hábitos "
    "declarados num painel de consumo de mídia, não intenção de voto nem amostra "
    "do eleitorado brasileiro. Os totais por grupo refletem a cobertura do painel. "
    "Nenhum recorte por estado é publicado: a base não sustenta esse corte.")

EIXOS = ["Digital", "TV/rádio", "Jovem", "Renda", "Fé", "Estudo"]


# ---------------------------------------------------------------- rótulos

# Jargão de janela de análise do painel de origem ("Leu-U7d" = leu nos últimos 7
# dias, "Recente", "Ouviu-U30d"...). Publicar isso entrega a fonte: a notação é
# reconhecível por quem trabalha com o painel. O dado no repo continua FIEL ao
# original de propósito, porque é contra ele que o gate cruzado confere; a
# limpeza é de VIEW, não de origem.
_JARGAO = re.compile(
    r"\s*(?::\s*(?:Leu|Ouviu|Viu|Assistiu|Acessou)\s*-\s*U\d+\s*[dhm]?"
    r"|\s*-\s*Recente"
    r"|\s*\((?:últimos?|ultimos?)[^)]*\))\s*$",
    re.IGNORECASE)


def rotulo(t):
    """Rótulo como vai para a página: sem a notação de janela do painel."""
    return _JARGAO.sub("", (t or "").strip()).strip(" :-")


def sem_jargao(labels):
    """Gate de view: nenhum rótulo publicado pode carregar notação da fonte."""
    resto = [t for t in labels if _JARGAO.search(t or "")
             or re.search(r"U\d+[dhm]\b", t or "", re.I)]
    return resto


def gate_jargao(paths):
    """Falha o build se notação do painel de origem sobrou em página publicada.

    Corrigir o rótulo uma vez não impede que ele volte: o dado é reimportado a
    cada rodada e um item novo do painel pode chegar com a mesma notação. O gate
    é o que torna a limpeza durável.
    """
    achados = []
    for path in paths:
        with open(path, encoding="utf-8") as f:
            html_ = f.read()
        for m in re.finditer(r"[^<>]{0,40}(?:U\d+[dhm]\b|Leu-U|Ouviu-U|- Recente)[^<>]{0,20}",
                             html_, re.I):
            achados.append((os.path.basename(path), m.group(0).strip()))
    return achados


def esc(s):
    """Escapa SEMPRE. Quick win #4 do plano de risco: o builder da edição não
    escapava nada, e isso só não era explorável porque nenhum texto de fonte
    externa chegava ao HTML. Aqui o texto vem de um PPTX de terceiro, então o
    escaping deixa de ser teórico. Escapar por padrão, não por exceção."""
    return html.escape(str(s if s is not None else ""), quote=True)


def num(n):
    return f"{n:,}".replace(",", ".")


# ---------------------------------------------------------------- derivados

def eixos(p):
    """6 atributos comparáveis entre os 5 grupos, normalizados 24..100.

    São DERIVADOS (média de afinidades, soma de faixas), nunca a tabela crua.
    O piso 24 evita que o polígono degenere numa linha quando o grupo é mínimo
    em quase tudo; a leitura continua ordinal e o eixo é rotulado.
    """
    def afi(k, nomes):
        v = [x["affinityScore"] for x in p.get(k, [])
             if (x.get("label") or x.get("description")) in nomes and x.get("affinityScore")]
        return sum(v) / len(v) if v else None

    def pct(k, nomes):
        return sum(x["percent"] for x in p.get(k, [])
                   if (x.get("label") or x.get("description")) in nomes)

    return [
        afi("habitos_midia", {"Internet", "Redes Sociais", "Streaming de Música", "VOD", "Podcast"}) or 0,
        afi("habitos_midia", {"TV Aberta", "Radio"}) or 0,
        pct("idades", {"12-19", "20-24", "25-34"}),
        pct("classes_sociais", {"A", "B"}),
        100.0 - pct("religioes", {"Não segue religião"}),
        p["percentHigherEducation"],
    ]


def normaliza(todos):
    """Min-max por eixo entre os 5 grupos -> 24..100. Determinístico."""
    out = {s: [] for s in todos}
    for i in range(len(EIXOS)):
        col = [todos[s][i] for s in sorted(todos)]
        lo, hi = min(col), max(col)
        for s in todos:
            v = todos[s][i]
            out[s].append(round(24 + 76 * ((v - lo) / (hi - lo)) if hi > lo else 62, 1))
    return out


BRUTOS = {p["slug"]: eixos(p) for p in PUB}
NORM = normaliza(BRUTOS)


def distintivos(p, n=5):
    """Os traços que mais AFASTAM o grupo da média do painel, para cima ou para
    baixo. Derivado, nunca a tabela.

    Ordenar por afinidade bruta (o óbvio) mente quando o grupo é baixo em quase
    tudo: os Bolsonaristas sairiam com "perícias" de índice 88, 90, 92, todas
    ABAIXO da média, apresentadas como se fossem forças. Ordenar por distância
    da média e mostrar o sinal diz a verdade nos dois sentidos.
    """
    # Piso de base: um item que só 1% do grupo declara produz afinidade extrema
    # por ruído, não por diferença real ("atenção com problemas sociais", 0% do
    # grupo, afinidade 30, viraria o traço mais distintivo). Abaixo de MIN_BASE
    # o índice não sustenta leitura.
    MIN_BASE = 10.0
    pool = []
    for k in ("interesses", "habitos_midia", "prioridades_voto"):
        pool += [x for x in p.get(k, [])
                 if x.get("affinityScore") and x.get("percent", 0) >= MIN_BASE]
    pool.sort(key=lambda x: (-abs(x["affinityScore"] - 100), x["description"]))
    return pool[:n]


# ---------------------------------------------------------------- SVG

def radar(e, size, fill=".18", rotulos=False):
    c, r = size / 2, size / 2 - size * 0.10
    grid = []
    for g in (1, 2, 3):
        rr, pts = r * g / 3, []
        for i in range(6):
            import math
            a = math.pi / 2 + i * math.pi / 3
            pts.append(f"{c + rr * math.cos(a):.1f},{c - rr * math.sin(a):.1f}")
        grid.append(f'<polygon points="{" ".join(pts)}" fill="none" stroke="var(--line)" stroke-width="1"/>')
    import math
    pts = []
    for i in range(6):
        a = math.pi / 2 + i * math.pi / 3
        rr = r * e[i] / 100
        pts.append(f"{c + rr * math.cos(a):.1f},{c - rr * math.sin(a):.1f}")
    poly = (f'<polygon points="{" ".join(pts)}" fill="var(--logo-bar)" fill-opacity="{fill}" '
            f'stroke="var(--logo-bar)" stroke-width="1.6" stroke-linejoin="round"/>')

    pad = size * 0.34 if rotulos else 0
    lb = ""
    if rotulos:
        out = []
        for i in range(6):
            a = math.pi / 2 + i * math.pi / 3
            rr = r + size * 0.075
            x, y = c + rr * math.cos(a), c - rr * math.sin(a)
            anc = "middle" if abs(x - c) < 3 else ("start" if x > c else "end")
            out.append(f'<text x="{x:.1f}" y="{y:.1f}" fill="var(--mut)" font-size="12" '
                       f'font-weight="800" text-anchor="{anc}" dominant-baseline="middle" '
                       f'class="rx">{esc(EIXOS[i])}</text>')
        lb = "".join(out)
    vb = f"{-pad:.0f} {-pad:.0f} {size + 2 * pad:.0f} {size + 2 * pad:.0f}"
    w = size + 2 * pad
    return (f'<svg class=rad viewBox="{vb}" width="{w:.0f}" height="{w:.0f}" role=img '
            f'aria-label="Radar de atributos: ' +
            ", ".join(f"{EIXOS[i]} {e[i]:.0f} de 100" for i in range(6)) + '">' +
            "".join(grid) + poly + lb + "</svg>")


# ---------------------------------------------------------------- CSS

# CSS base da edição (body/tipografia/.wrap/.rot/.foot/topbar...) vem do
# build_eleicoes: duplicar aqui divergiria na primeira mudança de design. O
# bloco abaixo tem SÓ o que é específico das páginas de público.
CSS = build_eleicoes.CSS + """
.rad{display:block;max-width:100%;height:auto}.rx{text-transform:uppercase;letter-spacing:.06em}
/* rótulo de seção: o token "rotulo" do schema da marca (10px, caixa alta,
   tracking .11em, peso 800). O CSS base da edição não expõe esse nome. */
.rot{font-size:10px;text-transform:uppercase;letter-spacing:.11em;font-weight:800;color:var(--mut)}
.deck{display:grid;grid-template-columns:repeat(auto-fit,minmax(184px,1fr));gap:13px;margin:16px 0 22px}
.carta{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:13px;
position:relative;overflow:hidden;text-decoration:none;color:inherit;display:block}
.carta::before{content:"";position:absolute;inset:5px;border:1px solid var(--ac);opacity:.28;
border-radius:8px;pointer-events:none}
.carta:hover,.carta:focus-visible{border-color:var(--ac)}
.carta .cs{font-size:10px;color:var(--mut);text-transform:uppercase;letter-spacing:.08em;font-weight:800}
.carta .cn{font-size:13px;font-weight:800;letter-spacing:-.01em;line-height:1.15;min-height:2.3em;margin-top:3px}
.carta .cu{font-size:20px;font-weight:800;margin:1px 0 6px;font-variant-numeric:tabular-nums}
.carta .cu span{font-size:11px;color:var(--mut);font-weight:400}
.carta .rad{margin:0 auto}
.pbficha{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px;
display:grid;grid-template-columns:auto 1fr;gap:26px;align-items:start}
.pbficha .brasao{text-align:center;max-width:100%}
.pbficha h1{font-size:23px;font-weight:800;letter-spacing:-.02em;margin:2px 0 4px;line-height:1.1}
.pbficha .sub{font-size:13.5px;color:var(--mut);line-height:1.45;margin-bottom:14px}
.pbkpis{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 16px}
.pbkpi{background:var(--box);border:1px solid var(--line);border-radius:8px;padding:8px 11px;min-width:84px}
.pbkpi .kv{font-size:16px;font-weight:800;font-variant-numeric:tabular-nums}
.pbkpi .kl{font-size:10px;color:var(--mut);text-transform:uppercase;letter-spacing:.08em;font-weight:800;margin-top:1px}
.per{display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding:8px 0;border-bottom:1px solid var(--line2);font-size:13.5px}
.per:last-of-type{border-bottom:0}
.per .pl{flex:1;line-height:1.35}
.per .pl em{font-style:normal;color:var(--mut);font-size:11.5px;display:block;margin-top:1px}
.afi{font:800 11px/1 inherit;padding:4px 6px;border-radius:5px;background:var(--acsoft);
color:var(--ac);border:1px solid var(--line);white-space:nowrap;font-variant-numeric:tabular-nums}
.lede{font-size:15px;line-height:1.55;margin:16px 0 0;max-width:62ch}
.aviso{border:1px dashed var(--line);border-radius:8px;padding:11px 13px;font-size:11.5px;
color:var(--mut);line-height:1.55;margin-top:18px}
.aviso b{color:var(--ink)}
.src{font-size:11.5px;color:var(--mut);margin-top:12px}
.outros{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
.outros a{font-size:12.5px;padding:6px 11px;border:1px solid var(--line);border-radius:20px;
color:var(--mut);text-decoration:none}
.outros a:hover,.outros a:focus-visible{border-color:var(--ac);color:var(--ac)}
@media(max-width:700px){.pbficha{grid-template-columns:1fr}.pbficha .brasao{margin:0 auto}}
"""

NAV = [("Corridas", "", "idx"), ("Presidencial", "presidencial", "pres"),
       ("Públicos", "publicos", "pub"), ("Modelos", "modelos", "mod")]


def topbar(active):
    links = "".join((f'<a class="on" aria-current="page">{l}</a>' if k == active
                     else f'<a href="./{h}">{l}</a>') for l, h, k in NAV)
    nav = f'<nav class="tabs" aria-label="Navegação entre páginas">{links}</nav>'
    return (shell.GTM_NOSCRIPT + '<a class="skip" href="#main">Pular para o conteúdo</a>'
            '<header class="topbar"><div class="bar">'
            '<a class="brand" href="./" aria-label="Ficha do Jogo, Eleições 2026, início">'
            + shell.LOGO + '<span class="nm">Ficha <span>do Jogo</span></span></a>'
            '<span class="ed">Eleições 2026</span><span class="sp"></span>'
            '<button class="tg" id="tg" type="button" onclick="cycleTheme()" '
            'title="Tema escuro · clique para alternar" aria-label="Alternar tema">☾</button>'
            '</div>' + nav + '</header>')


def page(fname, title, desc, slug, body, data_page, active="pub"):
    html_ = f"""<!DOCTYPE html><html lang=pt-BR><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
{shell.HEAD}{shell.meta(title, desc, slug)}
<style>{theme.PALETTE}{shell.CSS}{CSS}</style>
</head><body data-page="{data_page}">{topbar(active)}
<main id=main class=wrap>
{body}
<footer class=foot>Retrato de público a partir de painel de consumo de mídia. Não é pesquisa eleitoral · edição Eleições 2026 · {shell.CREDIT}</footer>
</main>{shell.JS}</body></html>"""
    with open(os.path.join(DIST, fname), "w", encoding="utf-8") as f:
        f.write(html_)


# ---------------------------------------------------------------- páginas

def carta(p, grande=False):
    e = NORM[p["slug"]]
    share = 100 * p["universo"] / TOTAL
    return (f'<a class=carta href="./publico-{esc(p["slug"])}">'
            f'<div class=cs>{share:.0f}% do painel</div>'
            f'<div class=cn>{esc(p["name"])}</div>'
            f'<div class=cu>{p["universo"] / 1e6:.1f}<span> mi</span></div>'
            f'{radar(e, 104)}</a>')


def build_index():
    cartas = "".join(carta(p) for p in PUB)
    body = (f'<h1>Públicos do eleitorado</h1>'
            f'<p class=lede>Cinco grupos de eleitores com perfis distintos de mídia, renda e '
            f'valores. Cada carta traz o radar de atributos do grupo: quanto mais cheio o eixo, '
            f'mais aquele traço distingue o público dos outros quatro.</p>'
            f'<div class=deck>{cartas}</div>'
            f'<div class=aviso>{RESSALVA}</div>'
            f'<p class=src>{esc(FONTE_PUBLICA)}</p>')
    page("eleicoes_publicos.html", "Públicos do eleitorado · Ficha do Jogo",
         "Cinco grupos de eleitores em fichas de atributos: mídia, renda, valores e prioridades.",
         "publicos", body, "publicos")


def build_ficha(p):
    e = NORM[p["slug"]]
    share = 100 * p["universo"] / TOTAL
    linhas = []
    for x in distintivos(p):
        d = round(x["affinityScore"] - 100)
        # sem cor de vitória/derrota: "acima da média" não é bom nem ruim quando
        # se descreve gente. O sinal e a palavra bastam.
        leg = "acima da média" if d > 2 else ("abaixo da média" if d < -2 else "na média")
        linhas.append(f'<div class=per><span class=pl>{esc(rotulo(x["description"]))}'
                      f'<em>{leg}</em></span>'
                      f'<span class=afi>{"+" if d > 0 else ""}{d}%</span></div>')
    per = "".join(linhas)
    kpis = "".join(f'<div class=pbkpi><div class=kv>{v}</div><div class=kl>{k}</div></div>'
                   for k, v in (("pessoas", num(p["universo"])),
                                ("renda familiar", f'R$ {num(p["rendaMediaFamiliar"])}'),
                                ("superior", f'{p["percentHigherEducation"]}%'),
                                ("trabalha", f'{p["percentWorking"]}%')))
    outros = "".join(f'<a href="./publico-{esc(q["slug"])}">{esc(q["name"])}</a>'
                     for q in PUB if q["slug"] != p["slug"])
    body = (f'<div class=pbficha>'
            f'<div class=brasao>{radar(e, 210, ".3", rotulos=True)}'
            f'<div class=rot style="margin-top:4px">Radar de atributos</div></div>'
            f'<div><div class=rot>Público eleitoral · {share:.0f}% do painel</div>'
            f'<h1>{esc(p["name"])}</h1>'
            f'<p class=sub>{esc(p["publicDefinition"])}</p>'
            f'<div class=pbkpis>{kpis}</div>'
            f'<div class=rot style="margin-bottom:2px">O que mais distingue este grupo</div>'
            f'{per}<p class=src>{esc(FONTE_PUBLICA)}</p></div></div>'
            f'<div class=rot style="margin:22px 0 4px">Outros públicos</div>'
            f'<div class=outros>{outros}</div>'
            f'<div class=aviso>{RESSALVA}</div>')
    page(f'eleicoes_publico_{p["slug"].replace("-", "_")}.html',
         f'{p["name"]} · Públicos · Ficha do Jogo',
         f'Ficha de atributos do público {p["name"]}: mídia, renda, valores e prioridades.',
         f'publico-{p["slug"]}', body, f'publico-{p["slug"]}')


def main():
    build_index()
    for p in PUB:
        build_ficha(p)
    gerados = [os.path.join(DIST, "eleicoes_publicos.html")]
    gerados += [os.path.join(DIST, f"eleicoes_publico_{p['slug']}.html") for p in PUB]
    gerados = [g for g in gerados if os.path.exists(g)]
    sobrou = gate_jargao(gerados)
    if sobrou:
        print("GATE REPROVADO: notação da fonte vazou para página publicada:")
        for f_, t in sobrou[:6]:
            print(f"  {f_}: {t!r}")
        sys.exit(4)
    print(f"OK: {1 + len(PUB)} páginas de públicos em dist/eleicoes_publico*.html "
          f"({len(PUB)} fichas + índice) · gate de jargão da fonte verde")


if __name__ == "__main__":
    main()
