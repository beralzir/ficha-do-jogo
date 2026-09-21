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

PISO DE SHARE no gatilho de P(eleito) (M7, 21/09/2026). Numa corrida empatada,
P(eleito) é métrica de alarme ruim: ~1,7pp de share viram ~12 pontos de
probabilidade, e o alarme dispara por aritmética da corrida, não por movimento.
Medido nos 19 freezes do `baseline` (9.432 pares candidato-corrida consecutivos):
29 disparos pela regra antiga, e 20 deles (69%) vieram de P(eleito) SOZINHO, com
share de 0,60pp a 9,37pp. Alarme que dispara 20 vezes em 19 dias sem nada de
errado é alarme que vira ALARME_OK=1 automático, e aí não protege de nada.

A correção NÃO é trocar P(eleito) por share, como o catálogo da Fase D propôs:
isso removeria a detecção de movimento grande de probabilidade em corrida não
empatada. É exigir um PISO de share JUNTO do gatilho de P(eleito). O gatilho de
share continua sozinho, intacto.

Calibração do piso (8pp), nos casos reais medidos:
  - tem de SILENCIAR: SEN-ES 5,97pp share / 28,76pp P(eleito) (17->18/09)
                      SEN-PR 6,61pp share / 23,72pp P(eleito) (18->19/09)
  - tem de DISPARAR:  SEN-MG 40,73pp share  e  SEN-MG 15,67pp share (ambos pelo
                      gatilho de share, que o piso não toca)
  - o piso fica em (6,61 ; 10]: acima dos falsos positivos medidos, abaixo do
    gatilho de share (em 10 o ramo de P(eleito) viraria redundante e morreria).
    8pp deixa margem para os dois lados. Para situar: p99 do Δshare em todos os
    9.432 pares é 2,38pp e p99,9 é 9,66pp, ou seja, a faixa 8-10pp que o ramo de
    P(eleito) ainda cobre é movimento genuinamente raro.
  Efeito: 29 disparos caem para 11, e os 11 restantes têm share de verdade.

TROCA DECLARADA: uma entrada plantada que mova share menos de 8pp e ainda assim
vire P(eleito) deixa de disparar AQUI. Ela continua coberta pelo gate de
plausibilidade da entrada, pelo alarme de volume (D2) e pelo gatilho de share.
A troca é deliberada: 20 falsos positivos em 19 dias custam mais em fadiga de
alarme do que esse caso custa em cobertura.

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
# M7: piso de share exigido JUNTO do gatilho de P(eleito). Ver docstring.
PISO_SHARE = float(os.environ.get("MOV_PISO_SHARE_PP", "8"))
TOPN = int(os.environ.get("MOV_TOPN", "12"))


def dispara(d_share, d_eleito, lim_share=None, lim_eleito=None, piso_share=None):
    """Regra do alarme. Devolve o motivo ('share', 'eleito', 'ambos') ou None.

    Função separada de propósito: é o que `src/test_movimento_gate.py` exercita
    com erro plantado. Regra embutida no laço não se testa sem reconstruir o
    mundo inteiro em volta dela.
    """
    ls = LIM_SHARE if lim_share is None else lim_share
    le = LIM_ELEITO if lim_eleito is None else lim_eleito
    ps = PISO_SHARE if piso_share is None else piso_share
    por_share = d_share > ls
    # o ramo de P(eleito) exige o piso: sem ele, corrida empatada dispara por
    # aritmética da corrida e não por movimento (M7).
    por_eleito = d_eleito > le and d_share > ps
    if por_share and por_eleito:
        return "ambos"
    if por_share:
        return "share"
    if por_eleito:
        return "eleito"
    return None


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
    silenciados = 0
    for k in comuns:
        d_share = abs(a[k][0] - b[k][0]) * 100
        d_eleito = abs(a[k][1] - b[k][1]) * 100
        motivo = dispara(d_share, d_eleito)
        if motivo:
            movs.append((max(d_share, d_eleito), k[0], k[1], d_share, d_eleito, motivo))
        elif d_eleito > LIM_ELEITO:
            # dispararia pela regra ANTIGA e o piso calou. Contar e mostrar o
            # total é o que impede o piso de virar censura invisível.
            silenciados += 1
    movs.sort(reverse=True)

    print(f"check_movimento: {len(comuns)} pares comparados contra {ref} · "
          f"limiares {LIM_SHARE:.0f}pp share / {LIM_ELEITO:.0f}pp P(eleito) "
          f"(piso de {PISO_SHARE:.0f}pp share no ramo de P(eleito), M7) · "
          f"as_of {velho.get('meta', {}).get('as_of')} -> {novo.get('meta', {}).get('as_of')}")
    if silenciados:
        print(f"  ({silenciados} par(es) passaram de {LIM_ELEITO:.0f}pp em P(eleito) com "
              f"share abaixo do piso: corrida empatada, não movimento. Ver docstring M7.)")
    if not movs:
        print("OK: nenhum movimento atípico.")
        return

    print(f"\nALARME: {len(movs)} movimento(s) acima do limiar:")
    for _, race, sq, ds, de, motivo in movs[:TOPN]:
        print(f"  {race:9s} sq={sq:<14s} share {ds:6.2f}pp · P(eleito) {de:6.2f}pp "
              f"· por {motivo}")
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
