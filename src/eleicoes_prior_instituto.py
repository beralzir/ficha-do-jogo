#!/usr/bin/env python3
"""
M5 · Prior de reputação por instituto (Fase D, Janela 2).

Transforma o viés histórico que o M4 mediu (`data/eleicoes/calibracao_erro.json`,
4 rodadas de 2018 e 2022) num ALVO DE ENCOLHIMENTO para o viés de casa do
competidor `v2_estado`. Hoje `eleicoes_model_v2.estimar_house()` encolhe para
ZERO: instituto com poucas pesquisas perde o viés inteiro e uma pesquisa nova de
instituto desconhecido move o agregado tanto quanto uma de Datafolha. Com o
prior, ele encolhe para o viés histórico DELE.

Escreve `data/eleicoes/prior_institutos.json`. Não toca o forecast OFICIAL: só o
v2, que é competidor.

Quatro decisões de desenho, cada uma com o motivo medido:

1. NOME, e por que o mapa NÃO vai no aliases.json.
   O prior do M4 é chaveado pelo nome como a Wikipédia de 2018 e 2022 escreve;
   o polls.json de 2026 usa outro. `RealTime Big Data` de 2018 é o
   `Real Time Big Data` que tem 161 pesquisas usáveis em 2026: sem o mapa, o
   maior instituto da base de 2026 ficaria sem prior. O mapa vive AQUI e não no
   `aliases.json` porque o aliases.json é lido pelo `ingest_polls.py`, que é o
   caminho que publica: um alias novo mudaria o polls.json na próxima rodada do
   cron e, com ele, o número no ar. O M4 já tinha tomado essa decisão (script
   separado, sem tocar o caminho do cron) e ela vale igual aqui.

2. ESCALA: logit por observação, não pp convertido depois.
   O `detalhe` do M4 guarda `previsto_pp` e `apurado_pp` de cada (instituto,
   candidato), então o viés pode ser medido direto no espaço onde o house effect
   do v2 vive: `logit(previsto) - logit(apurado)`. Isso dispensa delta method e,
   mais importante, evita repetir o defeito que o M2 achou: converter um viés
   médio em pp para logit com 1/(p(1-p)) explode embaixo, e um candidato de 2%
   herdaria um prior gigante de um viés medido em candidatos de 30%.

3. CENTRAGEM: só a parte RELATIVA do erro histórico entra.
   O viés do M4 é medido contra a URNA. O house effect do v2 é medido contra o
   CONSENSO dos institutos daquela corrida. São referências diferentes: se todos
   subestimam a direita, isso é viés COMUM, não viés de casa, e a identificação
   do `estimar_house` (média ponderada zero) o remove de qualquer jeito. Então o
   prior entra centrado pela média ponderada por n entre institutos, dentro de
   cada bloco. Sem isso, o prior injetaria um deslocamento de nível que a
   identificação depois tira de um jeito não controlado.

4. FORÇA DO PRIOR por n histórico.
   Um instituto com 2 observações não merece o mesmo puxão de um com 12. O prior
   entra multiplicado por n/(n + K_PRIOR), com K_PRIOR na mediana do n histórico.
   Instituto sem prior recebe 0,0, que é exatamente o comportamento de hoje: a
   mudança é compatível para trás por construção.

Uso:
    python3 eleicoes_prior_instituto.py            # escreve o JSON
    python3 eleicoes_prior_instituto.py --check    # só imprime, não escreve
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
CAL = os.path.join(ROOT, "data", "eleicoes", "calibracao_erro.json")
OUT = os.path.join(ROOT, "data", "eleicoes", "prior_institutos.json")

# Nome histórico (2018/2022) -> nome canônico de 2026, como o polls.json grava.
# CURADO À MÃO, e de propósito curto: só entra par que eu consegui confirmar como
# a MESMA casa. Quem não está aqui e não casa por nome exato simplesmente não
# ganha prior, que é o lado seguro do erro.
MAPA_HISTORICO = {
    "RealTime Big Data": "Real Time Big Data",  # só a grafia mudou; 161 pesquisas em 2026
    "Instituto Veritá": "Veritá",               # mesmo par já curado no aliases.json
    "IPEC": "Ipec",                             # caixa diferente na mesma rodada
    "FSB Pesquisa": "FSB",                      # idem, entre 2018 e 2022
}

# NÃO são instituto: vieram do parser do M4 lendo célula que não era nome de casa.
# Ficam declarados aqui em vez de serem apagados do calibracao_erro.json, que é
# extrato congelado com revid e auditável. Nenhum dos dois casa com instituto de
# 2026, então descartá-los não muda número nenhum; o valor é o registro.
NAO_INSTITUTO = {"2018"}

K_PRIOR_PADRAO = 6.0   # mediana do n histórico; recalculada em tempo de execução


def logit(p):
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def canoniza(nome):
    return MAPA_HISTORICO.get(nome, nome)


def bloco_de(cal):
    """{candidato: bloco} reconstruído do próprio extrato do M4.

    Lido do arquivo em vez de redeclarado: duas cópias do mapa divergiriam, e a
    do M4 é a que produziu os números que este módulo consome.
    """
    return {"bolsonaro": "dir", "haddad": "esq", "lula": "esq", "gomes": "esq",
            "alckmin": "centro", "tebet": "centro"}


def constroi(cal):
    """Devolve (prior, diagnostico). Determinístico: toda iteração é ordenada."""
    bl = bloco_de(cal)
    # 1) coleta viés em LOGIT por (instituto canônico, bloco)
    bruto = {}
    descartados = {}
    for rodada in cal["rodadas"]:
        for obs in rodada["detalhe"]:
            inst_orig = obs["instituto"]
            if inst_orig in NAO_INSTITUTO:
                descartados.setdefault(inst_orig, 0)
                descartados[inst_orig] += 1
                continue
            b = bl.get(obs["candidato"])
            if b is None:
                continue
            prev, apur = obs["previsto_pp"] / 100.0, obs["apurado_pp"] / 100.0
            if prev <= 0 or apur <= 0:
                continue
            inst = canoniza(inst_orig)
            bruto.setdefault(inst, {}).setdefault(b, []).append(
                logit(prev) - logit(apur))

    # 2) média por (instituto, bloco) e n total do instituto
    med, n_inst, fontes = {}, {}, {}
    for rodada in cal["rodadas"]:
        for obs in rodada["detalhe"]:
            if obs["instituto"] in NAO_INSTITUTO:
                continue
            inst = canoniza(obs["instituto"])
            fontes.setdefault(inst, set()).add(obs["instituto"])
    for inst in sorted(bruto):
        med[inst] = {b: sum(v) / len(v) for b, v in sorted(bruto[inst].items())}
        n_inst[inst] = sum(len(v) for v in bruto[inst].values())

    # 3) CENTRAGEM por bloco, ponderada por n: tira o viés COMUM a todos os
    #    institutos e deixa só a parte relativa, que é o que house effect é.
    centro_bloco = {}
    for b in ("esq", "centro", "dir"):
        num = sum(med[i][b] * n_inst[i] for i in sorted(med) if b in med[i])
        den = sum(n_inst[i] for i in sorted(med) if b in med[i])
        centro_bloco[b] = (num / den) if den else 0.0

    # 4) força do prior por n histórico
    ns = sorted(n_inst[i] for i in sorted(n_inst))
    k_prior = float(ns[len(ns) // 2]) if ns else K_PRIOR_PADRAO

    prior = {}
    for inst in sorted(med):
        n = n_inst[inst]
        forca = n / (n + k_prior)
        prior[inst] = {
            "n": n,
            "fontes": sorted(fontes.get(inst, {inst})),
            "vies_logit": {b: round(med[inst][b], 4) for b in sorted(med[inst])},
            "vies_centrado_logit": {
                b: round(med[inst][b] - centro_bloco[b], 4)
                for b in sorted(med[inst])},
            "forca": round(forca, 4),
            "prior_logit": {
                b: round((med[inst][b] - centro_bloco[b]) * forca, 4)
                for b in sorted(med[inst])},
        }
    diag = {
        "k_prior": round(k_prior, 2),
        "vies_comum_removido_logit": {b: round(centro_bloco[b], 4)
                                      for b in sorted(centro_bloco)},
        "descartados_nao_instituto": descartados,
    }
    return prior, diag


def main():
    cal = json.load(open(CAL, encoding="utf-8"))
    prior, diag = constroi(cal)
    doc = {
        "schema_version": 1,
        "gerado_por": "src/eleicoes_prior_instituto.py",
        "origem": "data/eleicoes/calibracao_erro.json",
        "consumidor": "src/eleicoes_model_v2.py :: estimar_house (competidor v2_estado)",
        "metodo": (
            "viés = média de (logit(previsto) - logit(apurado)) por (instituto, bloco) "
            "nas 4 rodadas do M4; CENTRADO pela média ponderada por n entre institutos "
            "dentro de cada bloco (só a parte relativa é house effect); multiplicado por "
            "n/(n+k_prior) para que instituto com histórico curto puxe menos."),
        "k_prior": diag["k_prior"],
        "vies_comum_removido_logit": diag["vies_comum_removido_logit"],
        "descartados_nao_instituto": diag["descartados_nao_instituto"],
        "mapa_historico_2026": MAPA_HISTORICO,
        "ressalvas": [
            "n pequeno: 4 rodadas presidenciais. É o universo disponível, não amostra grande.",
            "O viés histórico é contra a URNA; o house effect do v2 é contra o CONSENSO. "
            "Por isso o prior entra CENTRADO: o componente comum a todos os institutos não "
            "é viés de casa e a identificação do estimar_house o removeria de qualquer jeito.",
            "Só vale para instituto que aparece em 2018 ou 2022 E em 2026. Quem não casa "
            "recebe prior 0,0, que é o comportamento de hoje: a mudança é compatível para trás.",
            "O mapa de nome NÃO está no aliases.json de propósito: aliases.json é lido pelo "
            "ingest, que é o caminho que publica.",
            "Bloco vem de BLOCO_HIST do M4 (Alckmin e Tebet como centro, o que é discutível "
            "e está declarado lá).",
            "'2018' aparece como instituto no calibracao_erro.json e NÃO é instituto: é "
            "célula mal lida pelo parser do M4. Declarado e descartado aqui, não apagado lá, "
            "porque aquele extrato é congelado com revid. Não casa com nenhum instituto de "
            "2026, então descartar não muda número.",
        ],
        "n_institutos": len(prior),
        "prior": prior,
    }
    if "--check" not in sys.argv:
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1, sort_keys=False)
            f.write("\n")
    print(f"prior de reputação: {len(prior)} institutos · k_prior={diag['k_prior']}")
    print(f"viés comum removido (logit): {diag['vies_comum_removido_logit']}")
    if diag["descartados_nao_instituto"]:
        print(f"descartado (não é instituto): {diag['descartados_nao_instituto']}")
    print()
    print(f"{'instituto':22s} {'n':>3s} {'força':>6s} {'esq':>8s} {'centro':>8s} {'dir':>8s}")
    for i in sorted(prior, key=lambda k: -prior[k]["n"]):
        p = prior[i]["prior_logit"]
        print(f"{i:22s} {prior[i]['n']:3d} {prior[i]['forca']:6.2f} "
              f"{p.get('esq', 0.0):8.4f} {p.get('centro', 0.0):8.4f} {p.get('dir', 0.0):8.4f}")
    if "--check" not in sys.argv:
        print(f"\nOK: {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
