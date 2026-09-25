#!/usr/bin/env python3
"""Síntese dos retornos das três pesquisas de causa (P1, P2, P3).

Lê causas_P*_resultado.md, extrai TODOS os blocos ```json com arrays de eventos,
valida cada evento pelo validador da casa (eleicoes_eventos.validar), separa
exploratório (data < registrado_em) de pré-especificado (agenda futura), acusa
duplicatas entre períodos (mesma data + alvo) e imprime um quadro. Não escreve
no repo: a curadoria final é humana e vai para eventos.json por decisão.
"""
import glob, html, json, os, re, sys, datetime as dt
S = os.environ.get("CAUSAS_DIR", os.path.dirname(os.path.abspath(__file__)))  # pasta com causas_P*_resultado.md
# raiz do repo relativa ao próprio script (docs/causas/ -> raiz), para rodar de qualquer checkout
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
import eleicoes_eventos as ee  # noqa: E402

st = json.load(open(os.path.join(ROOT, "data", "eleicoes2026_structure.json"), encoding="utf-8"))
base = json.load(open(os.path.join(ROOT, "data", "eleicoes", "eventos.json"), encoding="utf-8"))
todos = []
for f in sorted(glob.glob(os.path.join(S, "causas_P*_resultado.md"))):
    md = html.unescape(open(f, encoding="utf-8").read())
    per = os.path.basename(f).split("_")[1]
    n_bl = 0
    for m in re.finditer(r"```json\s*(.*?)```", md, re.S):
        try:
            j = json.loads(m.group(1))
        except ValueError as e:
            print(f"  [{per}] bloco JSON inválido: {str(e)[:60]}")
            continue
        itens = j if isinstance(j, list) else [j]
        for e in itens:
            if isinstance(e, dict) and "data" in e and "tipo" in e:
                e["_periodo"] = per
                todos.append(e)
                n_bl += 1
    print(f"{per}: {n_bl} evento(s) extraído(s) de {os.path.basename(f)}")

print(f"\n=== {len(todos)} eventos no total ===")
vistos = {}
for e in todos:
    chave = (e.get("data"), tuple(sorted(e.get("alvo") or [])))
    vistos.setdefault(chave, []).append(e.get("id"))
dups = {k: v for k, v in vistos.items() if len(v) > 1}
if dups:
    print("duplicatas (mesma data + alvo):", dups)

# valida um a um dentro de um doc-cópia do registro real, para reaproveitar o validador
ok, ruins = [], []
for e in todos:
    doc = json.loads(json.dumps(base))
    ev = {k: v for k, v in e.items() if not k.startswith("_")}
    doc["eventos"].append(ev)
    sqs_validos = {c["sq"] for r in st["races"].values() for c in r["candidates"]}
    prob = ee.valida(doc, sqs_validos)          # o validador da casa: valida(doc, sqs_validos)
    prob = [p for p in prob if ev.get("id", "?") in str(p) or "repetido" in str(p)]
    (ruins if prob else ok).append((e, prob))
print(f"válidos pelo validador da casa: {len(ok)} · com problema: {len(ruins)}")
for e, prob in ruins[:12]:
    print(f"  - {e.get('id')}: {prob[:2]}")

hoje = dt.date(2026, 9, 25)
print("\n=== quadro ===")
print(f"{'data':10s} {'pré?':5s} {'tipo':18s} {'dir':3s} {'esc':8s} {'alvo':28s} {'id':40s} per")
for e, _ in sorted(ok, key=lambda t: t[0].get("data", "")):
    pre = "PRÉ" if dt.date.fromisoformat(e["data"]) >= hoje else "expl"
    print(f"{e['data']:10s} {pre:5s} {e['tipo'][:18]:18s} {e.get('direcao_esperada','?'):3s} {e.get('escopo','?')[:8]:8s} {str(e.get('alvo'))[:28]:28s} {e.get('id','')[:40]:40s} {e['_periodo']}")
json.dump({"validos": [e for e, _ in ok], "ruins": [{"evento": e, "problemas": p} for e, p in ruins]},
          open(os.path.join(S, "causas_sintese.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n-> {os.path.join(S, 'causas_sintese.json')}")
