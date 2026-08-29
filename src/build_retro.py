#!/usr/bin/env python3
"""Página "Retrospectiva" do ARQUIVO da edição -> dist/copa2026/retrospectiva.html
Resumo visual do fechamento da Copa 2026: campeã, leaderboard final (grupos+KO+fase),
trajetória de p(título) por congelamento diário, e os aprendizados da edição.

Fora do fluxo de build normal (a página é parte do arquivo congelado /copa2026): rode à mão
junto com make_snapshot.py. Fonte dos números: data/model_scores.json (measurement_complete).
Doc técnica completa: docs/retrospectiva-copa2026.md (linkada no rodapé, hyperlink != dependência).
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme, shell, flags
from pt import PT
from make_snapshot import BANNER

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "data")
OUTDIR = os.path.join(ROOT, "dist", "copa2026")

scores = json.load(open(f"{BASE}/model_scores.json"))
if not scores.get("measurement_complete"):
    sys.exit("model_scores.json ainda não é a medição final — rode finalize_scores.py antes.")
CARDS = scores["models"]
CHAMP = scores.get("champion", "Spain")
TRAJ = scores.get("trajectory", {})

def nm(t): return PT.get(t, ["", t])[1]
def fl(t): return PT.get(t, ["", t])[0]
def pct(p, nd=1):
    if p is None: return "—"
    if p > 0.995: return ">99%"
    if 0 < p < 0.005: return "<1%"
    return f"{p*100:.{nd}f}%"

DOC_URL = "https://github.com/beralzir/ficha-do-jogo/blob/main/docs/retrospectiva-copa2026.md"

# ── Leaderboard final (compacto) ──────────────────────────────────────────────
order = sorted(CARDS, key=lambda m: CARDS[m]["brier"])
best = order[0]
best_ph = min((m for m in CARDS if CARDS[m].get("phase")),
              key=lambda m: CARDS[m]["phase"]["brier_phase"])
rows = []
for i, mid in enumerate(order):
    c = CARDS[mid]
    ph = c.get("phase") or {}
    fase = f'{ph["brier_phase"]:.4f}' if ph else "—"
    ptit = pct(ph.get("champion_p")) if ph else "—"
    crown = "👑 " if mid == best else ""
    star = " ⚡" if mid == best_ph else ""
    rows.append(f'<tr class="{ "win" if mid==best else "" }"><td class=rk>{i+1}</td>'
                f'<td class=ml>{crown}{c["label"]}{star}</td>'
                f'<td class=num><b>{c["brier"]:.4f}</b></td>'
                f'<td class=num>{c["brier_group"]:.4f}</td>'
                f'<td class=num>{c["brier_ko"]:.4f}</td>'
                f'<td class=num>{fase}</td><td class=num>{ptit}</td></tr>')
LEAD = ('<table class=lb><caption class="sr-only">Leaderboard final de calibração (menor Brier = melhor)</caption>'
        '<thead><tr><th scope="col">#</th><th scope="col">modelo</th><th scope="col">Brier</th>'
        '<th scope="col">grupos</th><th scope="col">KO</th><th scope="col">fase</th>'
        f'<th scope="col">p({nm(CHAMP)} 🏆)</th></tr></thead><tbody>{"".join(rows)}</tbody></table>'
        f'<div class=kb>1X2 de {scores["n_matches"]} jogos ({scores["n_group"]} de grupos + {scores["n_ko"]} de mata-mata; '
        'o 3º lugar não foi capturado pela ingestão). <b>fase</b> = Brier dos marcadores oitavas→título no congelamento da '
        'véspera do mata-mata; <b>p(🏆)</b> = probabilidade dada à campeã nesse congelamento. '
        '👑 melhor 1X2 · ⚡ melhor leitura de fase.</div>')

# ── O que os dados dizem ──────────────────────────────────────────────────────
mkt, basec, mods = CARDS.get("market_only"), CARDS.get("baseline"), CARDS.get("models_only")
dyn_best = CARDS[best_ph]
FINDINGS = "".join(f"<li>{x}</li>" for x in [
    f'<b>O consenso de odds venceu o 1X2 da Copa inteira</b> ({mkt["brier"]:.4f} vs {basec["brier"]:.4f} do ensemble): diluir o mercado no blend não pagou. O aprendizado central, confirmado de ponta a ponta.',
    f'<b>No mata-mata isolado o quadro inverte</b>: só-modelos calibrou melhor ({mods["brier_ko"]:.4f}) que o consenso ({mkt["brier_ko"]:.4f}). Indício (31 jogos), não veredito.',
    f'<b>Reagir à Copa ajudou a ler o mata-mata</b>: os modelos que aprendem tiveram a melhor leitura de fase ({dyn_best["phase"]["brier_phase"]:.4f} vs {min(c["phase"]["brier_phase"] for c in CARDS.values() if c.get("phase") and c.get("learning") is None):.4f} do melhor estático), mesmo com o 1X2 no ruído.',
    f'<b>A campeã estava mais cotada nos modelos que no mercado</b>: {fl(CHAMP)} {nm(CHAMP)} a {pct(mods["phase"]["champion_p"],0)} no só-modelos e {pct(basec["phase"]["champion_p"],0)} no ensemble, contra {pct(mkt["phase"]["champion_p"],0)} no consenso, na véspera do mata-mata. Um caso, não evidência.',
    'Dobrar o <b>qualitativo</b> piorou a calibração; ele vale como narrativa (dossiês), não como peso. E a <b>forma de gols online</b> só adicionou ruído.',
])

# ── Trajetória p(campeã) por congelamento ─────────────────────────────────────
TRAJ_COLS = [("market_only", "Consenso"), ("baseline", "Ensemble"),
             ("models_only", "Só modelos"), ("dynamic_k20", "Aprende (Elo)")]
TRAJ_COLS = [(m, l) for m, l in TRAJ_COLS if m in TRAJ]
dates = sorted({p["date"] for m, _ in TRAJ_COLS for p in TRAJ[m]})
def _pt_at(m, d):
    for p in TRAJ[m]:
        if p["date"] == d: return p["p"]
    return None
trows = []
for d in dates:
    cells = []
    for m, _ in TRAJ_COLS:
        p = _pt_at(m, d)
        if p is None:
            cells.append('<td class=num>—</td>')
        else:
            w = max(1.5, p * 100)
            cells.append(f'<td class=num><span class=tbar style="width:{w:.1f}%"></span>{pct(p)}</td>')
    dd = f"{d[8:10]}/{d[5:7]}"
    trows.append(f'<tr><td class=dt>{dd}</td>{"".join(cells)}</tr>')
theads = "".join(f'<th scope="col">{l}</th>' for _, l in TRAJ_COLS)
TRAJT = ('<table class=tj><caption class="sr-only">Probabilidade de título da campeã por modelo, a cada congelamento diário</caption>'
         f'<thead><tr><th scope="col">freeze</th>{theads}</tr></thead><tbody>{"".join(trows)}</tbody></table>'
         f'<div class=kb>p({fl(CHAMP)} {nm(CHAMP)} campeã) a cada congelamento diário (23/jun a 20/jul, reconstruído do histórico git). '
         'Estáticos ficam parados por desenho; os que reagem caminham com o torneio (e colapsam em 100% após a final). '
         'A barra é a própria probabilidade.</div>')

# ── Aprendizados (acordeões) ──────────────────────────────────────────────────
AP_MODEL = ('<ul><li>Novo sinal entra como <b>modelo competidor</b> no leaderboard; só é promovido ao oficial se vencer fora do ruído.</li>'
            '<li>Uma edição é <b>uma amostra</b>: diferenças menores que ~2 erros-padrão são ruído, e o produto diz isso.</li>'
            '<li><b>Dupla contagem é sutil</b>: as odds já continham o Opta (corr ~0,98); consenso se mede como entidade única.</li>'
            '<li><b>Espaço de resultado definido antes de medir</b> (120 min; pênaltis = empate) manteve a medição coerente.</li>'
            '<li>Placares correlacionados pedem <b>Dixon-Coles + binomial negativa</b> (a camada de palpite mitigou; na v2, vai pro motor).</li>'
            '<li><b>Regras do torneio validadas na fonte oficial</b> cedo (o fix da chave dos 32-avos salvou a medição de fase por 1 dia).</li>'
            '<li><b>Completude de ingestão com alarme</b>: o 3º lugar se perdeu em silêncio por 40 dias.</li></ul>')
AP_ENG = ('<ul><li><b>Duas fontes + quorum + gates</b>: 27 atualizações automáticas, zero deploy ruim; falha vira e-mail, silêncio = sucesso.</li>'
          '<li><b>Estático-primeiro e zero-dep</b> seguram o produto em qualquer viewer; GTM como única exceção consciente.</li>'
          '<li><b>Determinismo por plataforma</b>: CI é a fonte dos bytes (float diverge no último dígito entre Linux e macOS).</li>'
          '<li><b>Freezes diários commitados</b> = auditoria retroativa de graça (esta página existe por causa deles).</li>'
          '<li><b>Ressalvas viajam nos dados</b> (caveats no JSON): a interface não consegue esquecer a leitura honesta.</li></ul>')
AP_V2 = ('<ul><li>Seleção → candidato/corrida · grupos → 1º turno · mata-mata → 2º turno · odds → <b>agregador de pesquisas</b> (recência, amostra, house effects).</li>'
         '<li><b>Leaderboard desde o dia 1</b>, prevendo a pesquisa seguinte e o resultado; pesquisas sintéticas entram como competidor, nunca no oficial sem vencer.</li>'
         '<li>Invariantes eleitorais (somas por corrida, coerência 1º/2º turno), ingest com quorum, caveats como dado e banner SINTÉTICO em tudo que vier de persona.</li>'
         f'<li>Doc técnica completa: <a href="{DOC_URL}" rel="noopener" target="_blank" data-context="retro_doc">retrospectiva-copa2026.md</a> no repositório.</li></ul>')

ACC = (shell.accordion("Aprendizados de modelagem", AP_MODEL, is_open=True)
       + shell.accordion("Aprendizados de engenharia e automação", AP_ENG)
       + shell.accordion("Receita para a edição Eleições 2026", AP_V2))

OUT = os.path.join(OUTDIR, "retrospectiva.html")
HTML = f"""<!DOCTYPE html><html lang=pt-BR><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>Retrospectiva · Ficha do Jogo</title>
{shell.HEAD}{shell.meta("Retrospectiva — Ficha do Jogo · Copa 2026", "O fechamento da edição Copa 2026: qual metodologia calibrou melhor (leaderboard final), a trajetória dos modelos e os aprendizados para a próxima edição.", "copa2026/retrospectiva", og="copa2026/og-cover.png")}
<style>
{theme.PALETTE}
{shell.CSS}
*{{box-sizing:border-box}}body{{margin:0;--maxw:920px;background:var(--bg);color:var(--ink);font-family:-apple-system,system-ui,"Segoe UI",Roboto,sans-serif;line-height:1.4;font-size:14px}}
.wrap{{max-width:920px;margin:0 auto;padding:14px}}
h1{{font-size:22px;font-weight:800;letter-spacing:-.02em;margin:0}}
.sub{{font-size:12px;color:var(--mut);margin:3px 0 14px}}
.sec{{font-size:11px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--ac);margin:22px 0 8px}}
.champ{{background:linear-gradient(135deg,var(--kpia,var(--card)),var(--kpib,var(--card)));border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:10px 0;font-size:14px}}
.champ b{{font-size:16px}}
.story{{background:var(--card);border-radius:11px;padding:6px 14px;margin:6px 0}}.story ul{{margin:0;padding-left:18px}}.story li{{font-size:13.5px;color:var(--ink);margin:8px 0;line-height:1.55}}.story b{{color:var(--ink)}}
.tw{{overflow-x:auto;-webkit-overflow-scrolling:touch}}
table{{border-collapse:collapse;width:100%;font-size:12.5px}}
.lb th,.tj th{{text-align:right;font-size:10px;text-transform:uppercase;letter-spacing:.05em;color:var(--mut);font-weight:800;padding:7px 7px;border-bottom:1px solid var(--line);white-space:nowrap}}
.lb th:nth-child(2),.tj th:first-child{{text-align:left}}
.lb td,.tj td{{padding:8px 7px;border-bottom:1px solid var(--line)}}
.num{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
.lb .rk{{color:var(--mut);width:18px}}
.ml{{font-weight:700;color:var(--ink)}}
.lb tr.win td{{background:var(--acsoft)}}.lb tr.win .num b{{color:var(--ac)}}
.dt{{color:var(--mut);font-variant-numeric:tabular-nums;white-space:nowrap}}
.tj td{{position:relative}}
.tbar{{display:inline-block;height:8px;border-radius:4px;background:var(--ac);opacity:.35;margin-right:6px;vertical-align:middle;max-width:70px}}
.kb{{font-size:11px;color:var(--mut);margin-top:8px;line-height:1.5}}.kb b{{color:var(--ink)}}
.foot{{color:var(--mut);font-size:11px;margin-top:20px;border-top:1px solid var(--line);padding-top:10px}}
</style></head><body data-page="retrospectiva">{BANNER}{shell.topbar("retro")}{flags.SPRITE}
<main class=wrap id=main tabindex=-1>
<div class=hero><h1>Retrospectiva</h1><div class=sub>O que a edição Copa do Mundo 2026 ensinou · medição fechada · {scores["n_matches"]} jogos + fase/título</div></div>

<div class=champ>🏆 <b>{fl(CHAMP)} {nm(CHAMP)} campeã</b> · 1x0 na prorrogação sobre a Argentina · 19/07/2026. No caminho, pênaltis eliminaram Alemanha (Paraguai), Holanda (Marrocos), Austrália (Egito) e Colômbia (Suíça).</div>

<h2 class=sec data-scene="achados">O que os dados dizem</h2>
<div class=story><ul>{FINDINGS}</ul></div>

<h2 class=sec data-scene="leaderboard">Leaderboard final · calibração (menor Brier = melhor)</h2>
<div class=tw>{LEAD}</div>

<h2 class=sec data-scene="trajetoria">Trajetória · p(título da campeã) por congelamento</h2>
<div class=tw>{TRAJT}</div>

<h2 class=sec data-scene="aprendizados">Aprendizados da edição</h2>
{ACC}

<footer class=foot>Edição arquivada: os dados desta página não mudam mais. Estimativas eram estimativas, não garantias · {shell.CREDIT}</footer>
</main>{shell.JS}</body></html>"""

os.makedirs(OUTDIR, exist_ok=True)
open(OUT, "w").write(HTML)
print("retrospectiva:", len(HTML), "chars | freezes:", len(dates), "| modelos no leaderboard:", len(CARDS),
      "| <script>:", HTML.count("<script"), "| OUT:", os.path.relpath(OUT, ROOT))
