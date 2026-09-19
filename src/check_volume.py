#!/usr/bin/env python3
"""Alarme de VOLUME por corrida (D2, docs/plano-incidente-presidencial.md).

TERCEIRA camada de defesa, e a que faltava. As outras duas olham o VALOR do dado:
o gate do `ingest_polls.py` filtra a entrada, o `check_movimento.py` olha a saída.
Nenhuma das duas percebe dado que simplesmente SOME.

Nasceu de um incidente real. Entre 31/08 e 18/09/2026 a corrida presidencial caiu
de 510 para 58 pesquisas estimuladas de 1º turno, e o site publicou um forecast
sobre 11% do dado por 14 dias sem que nada falhasse. Três razões para a cegueira, e
cada uma vira um requisito deste arquivo:

1. O alarme de completude do B8 checa `data_quality == "ok"`, que mede FRESCOR. A
   presidencial continuava recebendo pesquisa nova, então seguiu "ok" todo dia.
   => este alarme olha VOLUME, não frescor.
2. O total da base SUBIU no período (3.388 para 3.509), porque as outras 54
   corridas cresceram mais do que a presidencial perdeu.
   => a comparação é POR CORRIDA, nunca pelo total.
3. A perda foi só nas estimuladas: o 2º turno da mesma corrida continuou crescendo.
   => o corte é por (corrida, cenário), não por corrida inteira.

LIMIARES CALIBRADOS NO DADO REAL, não chutados. Nas 20 rodadas do robô entre 27/08
e 18/09 houve exatamente 3 quedas de volume por (corrida, cenário): duas legítimas
de UMA pesquisa (4,2% e 2,6%, GOV-PE em 05/09, edição na wiki) e o próprio
incidente, 558 pesquisas (99,1%) numa única rodada em 04/09. O default reprova
queda acima de 20% E de pelo menos 5 pesquisas: ~5x acima do ruído observado e
muito abaixo do incidente, e exigir as duas condições evita que corrida pequena
dispare por uma linha a menos.

Uso:
  python3 src/check_volume.py                  # compara com HEAD do git
  python3 src/check_volume.py --ref <commit>   # compara com outro commit
  VOLUME_OK=1 python3 src/check_volume.py      # reconhece e libera

`VOLUME_OK` é deliberadamente SEPARADO do `ALARME_OK` do check_movimento:
reconhecer que o forecast se moveu por um motivo legítimo não pode liberar, de
carona e em silêncio, uma perda de dado.
"""
import collections
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
POLLS = os.path.join(ROOT, "data", "live", "polls.json")
REL = "data/live/polls.json"

LIM_PCT = float(os.environ.get("VOL_QUEDA_PCT", "20"))   # queda relativa mínima
LIM_ABS = int(os.environ.get("VOL_QUEDA_MIN", "5"))      # e queda absoluta mínima
TOPN = int(os.environ.get("VOL_TOPN", "12"))


def ref_json(ref):
    """Lê o polls.json de um commit. None se não existir (1ª execução)."""
    try:
        out = subprocess.run(["git", "show", f"{ref}:{REL}"], cwd=ROOT,
                             capture_output=True, check=True)
        return json.loads(out.stdout.decode("utf-8"))
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
        return None


def volumes(doc):
    """{(corrida, cenário): n} contando só pesquisa REAL.

    Sintética fica de fora de propósito: ela entra e sai por decisão nossa
    (`synths_para_polls.py`), e contá-la deixaria o alarme de perda de dado
    refém do nosso próprio experimento.
    """
    c = collections.Counter()
    for p in doc.get("polls", []):
        if p.get("sintetico"):
            continue
        c[(p["race"], p["cenario"])] += 1
    return c


def quedas(velho, novo):
    """[(pct, n_perdidas, corrida, cenário, antes, depois)] acima dos dois limiares."""
    out = []
    for k in sorted(set(velho) | set(novo)):
        antes, depois = velho.get(k, 0), novo.get(k, 0)
        if antes <= 0 or depois >= antes:
            continue
        perdidas = antes - depois
        pct = perdidas / antes * 100
        if pct > LIM_PCT and perdidas >= LIM_ABS:
            out.append((pct, perdidas, k[0], k[1], antes, depois))
    out.sort(reverse=True)
    return out


def main():
    ref = "HEAD"
    if "--ref" in sys.argv:
        ref = sys.argv[sys.argv.index("--ref") + 1]

    novo_doc = json.load(open(POLLS, encoding="utf-8"))
    velho_doc = ref_json(ref)
    if velho_doc is None:
        print(f"check_volume: sem referência em {ref} (1ª execução). Nada a comparar.")
        return

    a, b = volumes(velho_doc), volumes(novo_doc)
    ruins = quedas(a, b)
    print(f"check_volume: {len(set(a) | set(b))} pares corrida/cenário comparados contra "
          f"{ref} · limiares queda > {LIM_PCT:.0f}% E >= {LIM_ABS} pesquisas · "
          f"total {sum(a.values())} -> {sum(b.values())}")
    if not ruins:
        print("OK: nenhuma corrida perdeu volume acima do limiar.")
        return

    print(f"\nALARME: {len(ruins)} corrida(s) perderam volume:")
    for pct, n, race, cen, antes, depois in ruins[:TOPN]:
        print(f"  {race:9s} {cen:14s} {antes:5d} -> {depois:5d}   "
              f"({n} pesquisas, {pct:.1f}%)")
    if len(ruins) > TOPN:
        print(f"  ... e mais {len(ruins) - TOPN}")

    if os.environ.get("VOLUME_OK"):
        print("\nVOLUME_OK setado: perda reconhecida por um humano. Seguindo.")
        return
    print("\nREPROVADO. Perda de volume não publica sozinha: é o sintoma de fonte que "
          "mudou de estrutura, e o forecast segue 'fresco' enquanto o histórico some. "
          "Veja docs/runbook-incidente.md, seção 'A fonte mudou de estrutura'. Se a "
          "perda for legítima, rode de novo com VOLUME_OK=1.", file=sys.stderr)
    sys.exit(6)


if __name__ == "__main__":
    main()
