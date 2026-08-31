#!/usr/bin/env python3
"""Alarme de movimento atípico no forecast (C0-c, docs/plano-risco-eleicoes.md).

SEGUNDA CAMADA de defesa. A primeira é o gate de plausibilidade do
`ingest_polls.py`, que filtra a ENTRADA. Esta olha a SAÍDA: compara o
`eleicoes2026_results.json` recém-gerado com o que está commitado no git e
reprova quando algum candidato se move além do limiar.

Por que as duas camadas: o gate de entrada é forte onde há muitas pesquisas
(presidencial) e fraco onde há poucas. Medido no plano de risco, uma entrada
forjada vale 67,9% do agregado em GOV-RR/SEN-RR, e ali um desvio que passe pelo
gate de entrada ainda move muito a saída. Esta camada pega exatamente esse caso.

Limiar CALIBRADO, não chutado: entre os freezes de 27/08 e 29/08 (524 pares
candidato-corrida), o movimento máximo real foi 2,11pp em share e 2,74pp em
P(eleito). Os limiares default (10pp e 20pp) ficam ~5x acima do observado: largos
para não gerar ruído em campanha normal, apertados para pegar adulteração.

Movimento legítimo grande existe (renúncia, evento de campanha, entrada de
candidato). Por isso o alarme NÃO some sozinho: ou o humano confirma com
ALARME_OK=1, ou investiga. Falso alarme é barato; publicar número plantado não é.

Uso:
  python3 src/check_movimento.py                 # compara com HEAD do git
  python3 src/check_movimento.py --ref <commit>  # compara com outro commit
  ALARME_OK=1 python3 src/check_movimento.py     # reconhece e libera
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
RESULTS = os.path.join(ROOT, "data", "eleicoes2026_results.json")
REL = "data/eleicoes2026_results.json"

LIM_SHARE = float(os.environ.get("MOV_SHARE_PP", "10"))
LIM_ELEITO = float(os.environ.get("MOV_ELEITO_PP", "20"))
TOPN = int(os.environ.get("MOV_TOPN", "12"))


def ref_json(ref):
    """Lê o results.json de um commit. None se não existir (1ª execução)."""
    try:
        out = subprocess.run(["git", "show", f"{ref}:{REL}"], cwd=ROOT,
                             capture_output=True, check=True)
        return json.loads(out.stdout.decode("utf-8"))
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None


def candidatos(doc):
    """{(corrida, sq): (share, P(eleito))} tolerante ao formato do results."""
    out = {}
    for race, r in (doc.get("races") or {}).items():
        for c in r.get("candidates", []):
            sq = str(c.get("sq"))
            out[(race, sq)] = (float(c.get("share") or 0.0),
                               float(c.get("eleito") or 0.0))
    return out


def main():
    ref = "HEAD"
    if "--ref" in sys.argv:
        ref = sys.argv[sys.argv.index("--ref") + 1]

    novo = json.load(open(RESULTS, encoding="utf-8"))
    velho = ref_json(ref)
    if velho is None:
        print(f"check_movimento: sem referência em {ref} (1ª execução). Nada a comparar.")
        return

    a, b = candidatos(velho), candidatos(novo)
    comuns = sorted(set(a) & set(b))
    if not comuns:
        print("check_movimento: nenhum candidato em comum; schema mudou? Nada a comparar.")
        return

    movs = []
    for k in comuns:
        d_share = abs(a[k][0] - b[k][0]) * 100
        d_eleito = abs(a[k][1] - b[k][1]) * 100
        if d_share > LIM_SHARE or d_eleito > LIM_ELEITO:
            movs.append((max(d_share, d_eleito), k[0], k[1], d_share, d_eleito))
    movs.sort(reverse=True)

    print(f"check_movimento: {len(comuns)} pares comparados contra {ref} · "
          f"limiares {LIM_SHARE:.0f}pp share / {LIM_ELEITO:.0f}pp P(eleito) · "
          f"as_of {velho.get('meta', {}).get('as_of')} -> {novo.get('meta', {}).get('as_of')}")
    if not movs:
        print("OK: nenhum movimento atípico.")
        return

    print(f"\nALARME: {len(movs)} movimento(s) acima do limiar:")
    for _, race, sq, ds, de in movs[:TOPN]:
        print(f"  {race:9s} sq={sq:<14s} share {ds:6.2f}pp · P(eleito) {de:6.2f}pp")
    if len(movs) > TOPN:
        print(f"  ... e mais {len(movs) - TOPN}")

    if os.environ.get("ALARME_OK"):
        print("\nALARME_OK setado: movimento reconhecido por um humano. Seguindo.")
        return
    print("\nREPROVADO. Movimento atípico não publica sozinho. Confira "
          "data/eleicoes/quarentena.json e data/eleicoes/ingest_diff.txt; se o "
          "movimento for legítimo, rode de novo com ALARME_OK=1.", file=sys.stderr)
    sys.exit(5)


if __name__ == "__main__":
    main()
