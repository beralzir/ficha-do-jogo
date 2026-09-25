#!/usr/bin/env python3
"""Testes da LISTA PARCIAL (achado da pesquisa de causas de 25/09/2026).

O ERRO PLANTADO AQUI É REAL E ESTÁ NA BASE VERSIONADA. Três registros da Veritá
fabricavam destaques no detector de inflexões (docs/causas/causas_P3_resultado.md,
seção 2b): `verit-sen-go-2026-09-17` e `verit-sen-rj-2026-09-18` trazem só 3
candidatos em base bruta (somas 111 e 113,5, sem indecisos) e produziam três
destaques positivos simultâneos em cada corrida (SEN-GO: Gracinha, Gayer e Calil
com z +6; SEN-RJ: Portinho +7,8, Jordy +6,5, Benedita +3,0); `verit-pres-2026-09-12`
traz só Lula 41,5 e Flávio 43,9 e disparava Flávio z +9,7 e Lula z +8,8.

CONFERIDO NA FONTE (revisões exatas que o ingest leu, 73047276, 73048530 e
73050701, pela API da Wikipédia): não é truncamento da extração nem cenário mal
classificado. As duas do Senado são assim na tabela (travessão nas outras cinco
colunas; a citação é um post de Instagram "Intenção de voto para Senador ...
votos válidos", só o top-3). A presidencial é 1º turno estimulado com os outros
11 candidatos SOMADOS em "Outros" 14,5% (nota [c] da própria tabela). Reclassificar
como 2º turno seria errado.

O MECANISMO: o share é normalizado entre os CASADOS. Lista que deixa de fora
candidatos com massa infla os presentes por 1/(1-m): 1,56x no SEN-GO (m=36%),
1,17x na PRES (m=17%). O filtro de Kalman lê isso como salto de TODOS os listados
no mesmo dia, e o agregador oficial como nível.

DUAS CAMADAS NO MESMO PONTO DE CORTE (`em.usable_polls`), decisão de 25/09: o
ingest PRESERVA o registro (ver test_pesquisa_degenerada.py) e o motor julga:
  MIN_CASADOS   passa a contar candidatos DISTINTOS. Em SEN-MG, quatro pesquisas
                de agosto tinham as 7 colunas casadas no MESMO sq por contaminação
                do cabeçalho (mesma classe do achado do DF); contadas por coluna
                passavam, e o site publicava esse candidato com 55% de share.
  COBERTURA_MIN pesquisa cuja lista deixa de fora mais de 10% do CAMPO não entra.
                O limiar REAPROVEITA o MATCH_MIN (0,90): corte novo escolhido
                olhando o resultado seria racionalização. A massa ausente vem do
                consenso (mediana) das listas CHEIAS da vizinhança temporal, só
                entre concorrentes (`em.massa_ausente`).

Erro plantado rodado no código de PRODUÇÃO (25/09, __pycache__ limpo entre os
passos, mutação que muda o tamanho do arquivo), três mutações, as três reprovam:
COBERTURA_MIN=0 no DEFAULTS; COB_CHEIA=0 (toda lista vira "cheia", m=0 para
todas); contagem por coluna no lugar de distintos.

Usa rede? Não.

Uso:  python3 src/test_lista_parcial.py
"""
import copy
import datetime as dt
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eleicoes_model as em        # noqa: E402
import eleicoes_model_v2 as v2     # noqa: E402

ROOT = os.path.join(HERE, "..")
CONFIGS = os.path.join(ROOT, "data", "eleicoes", "model_configs.json")
ALVOS = {
    "verit-sen-go-2026-09-17": ("SEN-GO", 3, 0.30),
    "verit-sen-rj-2026-09-18": ("SEN-RJ", 3, 0.30),
    "verit-pres-2026-09-12": ("PRES", 2, 0.15),
}
SEN_MG_CONTAMINADAS = ["datatempo-sen-mg-2026-08-10", "datafolha-sen-mg-2026-08-20",
                       "quaest-sen-mg-2026-08-24", "real-time-big-data-sen-mg-2026-08-26"]
TETO_EXCLUSAO = 0.06   # o gate não pode reprovar o dado real em massa
FALHAS = []


def check(nome, cond, detalhe=""):
    print(f"  {'ok  ' if cond else 'FALHA'} {nome}" + (f"  ({detalhe})" if detalhe else ""))
    if not cond:
        FALHAS.append(nome)


def ids_de(by_race):
    return {p["id"] for v in by_race.values() for p in v}


def distintos(p):
    return len({n["sq"] for n in p["numeros"] if n.get("sq") and n["pct"] > 0})


def saltos_no_dia(race_key, race, plist, as_of, pv2, dia):
    """{sq: z} dos saltos do filtro v2 datados em `dia` para a corrida."""
    agg = v2.aggregate_race_v2(race_key, race, plist, as_of, pv2)
    out = {}
    for sq, lst in (agg.get("_saltos") or {}).items():
        for s in lst:
            if s["data"] == dia:
                out[sq] = s["z"]
    return out


def main():
    polls_doc = json.load(open(em.POLLS, encoding="utf-8"))
    polls = polls_doc["polls"]
    st = json.load(open(em.STRUCT, encoding="utf-8"))
    cfg = json.load(open(CONFIGS, encoding="utf-8"))
    p_def = dict(em.DEFAULTS)
    p_off = dict(em.DEFAULTS)
    p_off.update(cfg["models"][cfg["official"]]["params"])
    p_sem = dict(em.DEFAULTS)
    p_sem["COBERTURA_MIN"] = 0            # o erro plantado: sem a camada de cobertura

    print("1. o erro plantado pela realidade está na base versionada, como a fonte diz")
    reais = {}
    for pid, (race, n_nomes, _) in ALVOS.items():
        cands = [p for p in polls if p["id"] == pid and p["cenario"] == "estimulada"]
        check(f"{pid} existe, 1º turno estimulado, {n_nomes} nomes",
              len(cands) == 1 and distintos(cands[0]) == n_nomes and cands[0]["race"] == race,
              f"{len(cands)} ocorrência(s), distintos={distintos(cands[0]) if cands else '-'}")
        if cands:
            reais[pid] = cands[0]
    if len(reais) < 3:
        print("REPROVADO: sem os registros reais o teste não prova nada", file=sys.stderr)
        sys.exit(1)
    pres = reais["verit-pres-2026-09-12"]
    check("a presidencial traz os outros candidatos em 'Outros' (14,5), não é 2º turno",
          pres.get("par_segundo_turno") is None
          and abs((pres["indefinidos_pct"].get("outros") or 0) - 14.5) < 1e-9)
    for pid in ("verit-sen-go-2026-09-17", "verit-sen-rj-2026-09-18"):
        ind = reais[pid]["indefinidos_pct"]
        check(f"{pid}: sem indecisos nem outros (é o top-3 de 'votos válidos')",
              ind.get("indecisos") is None and ind.get("outros") is None
              and "senado_2votos" in reais[pid].get("flags", []))

    print("\n2. a massa ausente, medida pela função de PRODUÇÃO, passa do que o motor tolera")
    diag = {}
    by_def = em.usable_polls(polls, p_def, st, diag)
    excl = {x["id"]: x for x in diag.get("listas_parciais", [])}
    tol = 1.0 - em.DEFAULTS["COBERTURA_MIN"]
    for pid, (race, _, piso) in ALVOS.items():
        m = excl.get(pid, {}).get("massa_ausente")
        check(f"{pid}: massa ausente >= {piso:.0%} (e > {tol:.0%} tolerado)",
              m is not None and m >= piso and m > tol, f"m={m}")

    print("\n3. com o default do motor, nenhum dos três é usável")
    ids_def = ids_de(by_def)
    for pid in ALVOS:
        check(f"{pid} NÃO é usável", pid not in ids_def)
    check("o default do motor é COBERTURA_MIN=0,90, o MESMO 0,90 do MATCH_MIN (reaproveitado)",
          em.DEFAULTS["COBERTURA_MIN"] == em.DEFAULTS["MATCH_MIN"] == 0.90)

    print("\n4. ERRO PLANTADO: com COBERTURA_MIN=0 os três ENTRAM e fabricam os saltos")
    by_sem = em.usable_polls(polls, p_sem, st)
    ids_sem = ids_de(by_sem)
    for pid in ALVOS:
        check(f"{pid} ENTRA sem a camada (prova que o gate morde)", pid in ids_sem)
    pv2 = v2.params_v2(cfg["models"][v2.MODEL_ID].get("params", {}))
    vis = [p for p in polls if not p.get("sintetico") and p["campo_fim"]]
    as_of = dt.date.fromisoformat(max(p["campo_fim"] for p in vis))
    z0 = pv2["Z_SALTO"]
    casos = [("SEN-GO", "2026-09-17", 3), ("SEN-RJ", "2026-09-18", 3), ("PRES", "2026-09-12", 2)]
    for race, dia, n_esp in casos:
        pv2_sem = dict(pv2); pv2_sem["COBERTURA_MIN"] = 0
        sem = saltos_no_dia(race, st["races"][race], by_sem.get(race, []), as_of, pv2_sem, dia)
        com = saltos_no_dia(race, st["races"][race], by_def.get(race, []), as_of, pv2, dia)
        pos = [z for z in sem.values() if z > z0]
        check(f"{race} {dia}: SEM a camada, {n_esp} saltos positivos no mesmo dia (o artefato)",
              len(pos) >= n_esp and len(pos) == len(sem),
              f"z={sorted(round(z, 1) for z in sem.values())}")
        check(f"{race} {dia}: COM a camada, nenhum salto datado nesse dia",
              not com, f"{com}")

    print("\n5. MIN_CASADOS conta candidatos DISTINTOS (SEN-MG: 7 colunas num só sq)")
    for pid in SEN_MG_CONTAMINADAS:
        linha = next((p for p in polls if p["id"] == pid and p["cenario"] == "estimulada"), None)
        colunas = sum(1 for n in (linha or {"numeros": []})["numeros"] if n.get("sq") and n["pct"] > 0)
        check(f"{pid}: >=4 colunas casadas, 1 sq distinto, NÃO usável",
              linha is not None and colunas >= 4 and distintos(linha) == 1 and pid not in ids_def,
              f"colunas={colunas}, distintos={distintos(linha) if linha else '-'}")
    modelo = next(p for p in polls if p["race"] == "SEN-GO" and p["cenario"] == "estimulada"
                  and distintos(p) >= 6)
    dup = copy.deepcopy(modelo)
    dup["id"], dup["instituto"] = "TESTE-DUPLICADO", "INSTITUTO-TESTE-DUP"
    a, b = [dict(n) for n in modelo["numeros"] if n.get("sq")][:2]
    dup["numeros"] = [a, dict(b, sq=a["sq"])]      # duas colunas, o mesmo sq
    dois = copy.deepcopy(dup)
    dois["id"], dois["instituto"] = "TESTE-DOIS", "INSTITUTO-TESTE-DOIS"
    dois["numeros"] = [a, b]                       # duas colunas, dois sqs
    ids_x = ids_de(em.usable_polls(polls + [dup, dois], p_sem, st))
    check("duas colunas no MESMO sq contam como 1 casado: não entra", "TESTE-DUPLICADO" not in ids_x)
    check("duas colunas em sqs diferentes contam como 2: entra", "TESTE-DOIS" in ids_x)
    check("nenhuma usável tem menos de 2 candidatos DISTINTOS",
          all(distintos(p) >= 2 for v in by_def.values() for p in v))

    print("\n6. cirurgia e teto: o gate derruba só o que mede, e nunca o dado real em massa")
    caiu = ids_sem - ids_def
    check("o que caiu é EXATAMENTE o que a camada de cobertura mediu e declarou em `diag`",
          caiu == set(excl) and len(caiu) >= 3, f"{len(ids_sem)} -> {len(ids_def)}, caiu {len(caiu)}")
    check("toda exclusão tem massa ausente acima da tolerância",
          all(x["massa_ausente"] > tol for x in excl.values()))
    taxa = len(caiu) / max(len(ids_sem), 1)
    check(f"taxa de exclusão <= {TETO_EXCLUSAO:.0%} das usáveis", taxa <= TETO_EXCLUSAO,
          f"{taxa:.2%} ({len(caiu)} de {len(ids_sem)})")
    set26 = sorted(x["id"] for x in excl.values() if (x["campo_fim"] or "") >= "2026-09-01")
    print(f"       com campo em setembro/2026: {len(set26)}: {set26}")
    # a cirurgia não depende da ORDEM de entrada nem regrava o resultado
    emb = list(polls)
    random.Random(7).shuffle(emb)
    check("determinístico e independente da ordem de entrada",
          {r: [p["id"] for p in v] for r, v in em.usable_polls(emb, p_def, st).items()}
          == {r: [p["id"] for p in v] for r, v in by_def.items()})

    print("\n6b. o consenso vem das listas CHEIAS: inundar de top-3 não redefine o campo")
    # No dado real as listas cheias são maioria em toda vizinhança, então os
    # três alvos caem com QUALQUER COB_CHEIA (medido em 25/09: com 0,75 são 62
    # exclusões, com 0 seriam 48, e a diferença são 14 casos limítrofes de
    # m entre 10% e 16%). A mutação COB_CHEIA=0 passou pelo gate na 1ª versão
    # por isso. O caso em que a regra importa é CONSTRUÍDO numa corrida à parte:
    # 2 listas cheias e 6 listas de 3 nomes na mesma janela. Se a mediana lesse
    # todas as listas, a massa dos ausentes zeraria (6 zeros contra 2 valores)
    # e as parciais entrariam em bando; lendo só as cheias, elas caem.
    RACE_T = "SEN-GO-TESTE-CHEIAS"
    cheias_go = [p for p in by_def["SEN-GO"] if distintos(p) >= 8][-2:]
    check("há 2 listas cheias reais do SEN-GO para o cenário", len(cheias_go) == 2)
    sint = []
    for k, p in enumerate(cheias_go):
        c = copy.deepcopy(p)
        c["id"], c["race"], c["instituto"] = f"CHEIA-{k}", RACE_T, f"INSTITUTO-CHEIA-{k}"
        c["campo_fim"] = c["campo_ini"] = f"2026-09-{14 + k:02d}"
        sint.append(c)
    for k in range(6):
        c = copy.deepcopy(reais["verit-sen-go-2026-09-17"])
        c["id"], c["race"], c["instituto"] = f"TOP3-{k}", RACE_T, f"INSTITUTO-TOP3-{k}"
        c["campo_fim"] = c["campo_ini"] = f"2026-09-{16 + k:02d}"
        sint.append(c)
    ids_t = ids_de({RACE_T: em.usable_polls(polls + sint, p_def, st).get(RACE_T, [])})
    check("as 2 listas cheias da corrida sintética entram", {"CHEIA-0", "CHEIA-1"} <= ids_t)
    check("e NENHUMA das 6 listas de 3 nomes entra, mesmo sendo maioria na janela",
          not any(f"TOP3-{k}" in ids_t for k in range(6)),
          f"entraram: {sorted(i for i in ids_t if i.startswith('TOP3'))}")

    print("\n7. registro")
    check("o modelo OFICIAL declara COBERTURA_MIN=0,9, não herda do default",
          cfg["models"][cfg["official"]]["params"].get("COBERTURA_MIN") == 0.9)
    check("e continua declarando MIN_CASADOS=2",
          cfg["models"][cfg["official"]]["params"].get("MIN_CASADOS") == 2)
    check("o oficial e o default do motor coincidem no que este teste provou",
          ids_de(em.usable_polls(polls, p_off, st)) == ids_def)

    print()
    if FALHAS:
        print(f"REPROVADO: {len(FALHAS)} falha(s): {', '.join(FALHAS)}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: lista parcial validada · {len(caiu)} exclusões medidas ({taxa:.1%}), "
          f"os três registros da Veritá fora, SEN-MG contaminada fora, sem artefato datado.")


if __name__ == "__main__":
    main()
