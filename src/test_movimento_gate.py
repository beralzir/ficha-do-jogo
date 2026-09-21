#!/usr/bin/env python3
"""Testes do piso de share no alarme de movimento (M7, Fase D).

Regra da casa: gate só vale depois de provado com ERRO PLANTADO. Aqui, como no
`test_volume_gate.py`, o erro mais forte não precisou ser inventado: os falsos
positivos REAIS estão nos 99 freezes versionados em data/eleicoes/models/. O
caso 2 os recalcula do dado (não os copia de uma tabela) e exige que o piso os
cale; o caso 3 planta movimento fabricado e exige que o alarme continue pegando.

Por que o piso existe: ver o docstring do `check_movimento.py`. Resumo: P(eleito)
numa corrida empatada é aritmética da corrida, não movimento. 20 dos 29 disparos
em 19 dias vieram daí, e alarme que grita 20 vezes à toa vira ALARME_OK=1
automático.

Usa rede? Não. Lê os freezes do próprio repositório.

Uso:  python3 src/test_movimento_gate.py
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_movimento as cm  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
MODELS = os.path.join(ROOT, "data", "eleicoes", "models")

# Os dois alarmes de 21/09 que o M7 tem de CALAR, e os dois que tem de PRESERVAR.
# Os de SEN-MG foram medidos contra o results.json publicado (não contra freezes
# consecutivos), por isso entram como constantes documentadas e não recalculadas.
DEVE_DISPARAR = [("SEN-MG", 40.73, 19.73), ("SEN-MG", 15.67, 34.44)]
# Piso admissível: acima do maior falso positivo medido, abaixo do gatilho de share.
PISO_MIN_EXCLUSIVO, PISO_MAX = 6.61, 10.0

FALHAS = []


def check(nome, cond, detalhe=""):
    print(f"  {'ok  ' if cond else 'FALHA'} {nome}" + (f"  ({detalhe})" if detalhe else ""))
    if not cond:
        FALHAS.append(nome)


def regra_antiga(d_share, d_eleito):
    """A regra ANTES do M7, para medir exatamente o que o piso mudou."""
    return d_share > cm.LIM_SHARE or d_eleito > cm.LIM_ELEITO


def pares_consecutivos(modelo="baseline"):
    """(d_share, d_eleito, corrida, sq, transicao) entre freezes consecutivos."""
    byday = {}
    for path in sorted(glob.glob(os.path.join(MODELS, "freeze-*.json"))):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        if d["model"] == modelo:
            byday[d["as_of"]] = d
    dias = sorted(byday)
    for a_day, b_day in zip(dias, dias[1:]):
        A, B = byday[a_day], byday[b_day]
        for race in sorted(set(A["races"]) & set(B["races"])):
            ca, cb = A["races"][race]["c"], B["races"][race]["c"]
            for sq in sorted(set(ca) & set(cb)):
                yield (abs(ca[sq][0] - cb[sq][0]) * 100,
                       abs(ca[sq][1] - cb[sq][1]) * 100,
                       race, sq, f"{a_day}->{b_day}")


def main():
    pares = list(pares_consecutivos())
    if len(pares) < 1000:
        print(f"REPROVADO: só {len(pares)} pares nos freezes; a base de calibração "
              f"sumiu. Teste que passa sem dado não prova nada.", file=sys.stderr)
        sys.exit(1)
    print(f"base real: {len(pares)} pares candidato-corrida em freezes consecutivos "
          f"do baseline\n")

    # 1. O piso está dentro da faixa que a calibração admite.
    print("1. o piso está na faixa calibrada")
    check("piso > maior falso positivo medido (6,61pp)", cm.PISO_SHARE > PISO_MIN_EXCLUSIVO,
          f"piso={cm.PISO_SHARE}pp")
    check("piso < gatilho de share (senão o ramo de P(eleito) morre)",
          cm.PISO_SHARE < PISO_MAX, f"piso={cm.PISO_SHARE}pp vs share={cm.LIM_SHARE}pp")

    # 2. ERRO PLANTADO PELA REALIDADE: os falsos positivos reais têm de calar.
    print("\n2. erro plantado real: os falsos positivos dos freezes")
    antes = [p for p in pares if regra_antiga(p[0], p[1])]
    depois = [p for p in pares if cm.dispara(p[0], p[1])]
    so_eleito_antes = [p for p in antes if p[0] <= cm.LIM_SHARE]
    check("a regra antiga disparava muito por P(eleito) sozinho", len(so_eleito_antes) >= 15,
          f"{len(so_eleito_antes)} de {len(antes)} disparos")
    check("o piso reduz o total de disparos", len(depois) < len(antes),
          f"{len(antes)} -> {len(depois)}")
    calados = [p for p in antes if not cm.dispara(p[0], p[1])]
    check("todo par calado tem share abaixo do piso",
          all(p[0] <= cm.PISO_SHARE for p in calados),
          f"{len(calados)} calados, share máx {max([p[0] for p in calados], default=0):.2f}pp")

    # os dois casos nomeados na calibração, localizados no dado e não copiados
    for corrida, ds_esperado in (("SEN-ES", 5.97), ("SEN-PR", 6.61)):
        achados = [p for p in so_eleito_antes
                   if p[2] == corrida and abs(p[0] - ds_esperado) < 0.05]
        check(f"{corrida} {ds_esperado}pp existe nos freezes", len(achados) == 1,
              f"{len(achados)} ocorrência(s)")
        check(f"{corrida} {ds_esperado}pp CALA com o piso",
              all(cm.dispara(p[0], p[1]) is None for p in achados))

    # 3. os que têm de continuar disparando
    print("\n3. o que NÃO pode calar")
    for corrida, ds, de in DEVE_DISPARAR:
        motivo = cm.dispara(ds, de)
        check(f"{corrida} share {ds}pp / P(eleito) {de}pp dispara", motivo is not None,
              f"por {motivo}")
    por_share_antes = {(p[2], p[3], p[4]) for p in antes if p[0] > cm.LIM_SHARE}
    por_share_depois = {(p[2], p[3], p[4]) for p in depois if p[0] > cm.LIM_SHARE}
    check("o piso não tocou em NENHUM disparo do gatilho de share",
          por_share_antes == por_share_depois, f"{len(por_share_antes)} disparos por share")

    # 4. ERRO PLANTADO FABRICADO: movimento que o alarme tem de pegar.
    print("\n4. erro plantado fabricado")
    # Valores ABSOLUTOS de propósito. Derivar os casos de `cm.PISO_SHARE` faria o
    # teste se mover junto com o parâmetro que ele deveria vigiar: com piso=0 o
    # caso "share abaixo do piso" virava share de -0,5pp, que não existe, e
    # passava. Caso fabricado só prova alguma coisa se for imóvel.
    casos = [
        # (d_share, d_eleito, tem_que_disparar, descrição)
        (12.0, 0.0, True, "share estourado, P(eleito) parado (adulteração de share)"),
        (9.0, 30.0, True, "share 9pp (acima do piso) + P(eleito) estourado"),
        (2.0, 30.0, False, "share 2pp com P(eleito) em 30pp: corrida empatada"),
        (9.0, 19.0, False, "nenhum limiar estourado"),
        (95.0, 50.0, True, "movimento absurdo (corrida trocada de candidato)"),
        (0.0, 0.0, False, "nada se moveu"),
    ]
    for ds, de, esperado, desc in casos:
        got = cm.dispara(ds, de) is not None
        check(f"{desc}: {'dispara' if esperado else 'silencia'}", got == esperado,
              f"share {ds:.1f}pp eleito {de:.1f}pp -> {cm.dispara(ds, de)}")

    # 5. o piso não pode ser desligável sem deixar rastro: com piso 0 os falsos
    #    positivos VOLTAM. Prova que é o piso que faz o trabalho, não um acaso.
    print("\n5. desligar o piso traz os falsos positivos de volta")
    com_piso_zero = [p for p in pares if cm.dispara(p[0], p[1], piso_share=0.0)]
    check("piso=0 reproduz exatamente a regra antiga",
          {(p[2], p[3], p[4]) for p in com_piso_zero} == {(p[2], p[3], p[4]) for p in antes},
          f"{len(com_piso_zero)} vs {len(antes)}")

    print()
    if FALHAS:
        print(f"REPROVADO: {len(FALHAS)} falha(s): {', '.join(FALHAS)}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: piso de {cm.PISO_SHARE:.0f}pp validado · disparos {len(antes)} -> "
          f"{len(depois)} em {len(pares)} pares, sem perder nenhum disparo de share.")


if __name__ == "__main__":
    main()
