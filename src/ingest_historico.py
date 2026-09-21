#!/usr/bin/env python3
"""
Calibração do erro sistemático de eleição com 2018 e 2022 (M4 da Fase D).

POR QUE UM SCRIPT SEPARADO, e não o `ingest_polls.py`. Decisão do Bera em
21/09/2026, depois de o reconhecimento derrubar a premissa do plano ("as mesmas
páginas, o ingest já sabe ler"). Ele não sabe, em quatro pontos: o corte
`year < 2025` mata 2022 na entrada; o default silencioso `year = 2026` faz 2018
virar 2025 pelo guarda de data futura (dado errado GRAVADO, não erro); 2018 tem
outro perfil de coluna; e o 2º turno de 2022 é uma tabela única de 2019 a 2022
sem nenhum heading de ano. Ensinar tudo isso ao ingest significaria mexer, a 13
dias do 1º turno, na superfície exata que causou o incidente de 04/09, e o gate
de fonte é GLOBAL ao run: um erro ali derrubaria as 56 páginas de 2026 junto.

Então este script NÃO toca: `polls.json`, `race_key`, o gate de plausibilidade,
o gate de volume, nem o `ingest_polls.py`. Ele importa o parser de lá (leitura,
nunca escrita) e escreve dois arquivos próprios.

DUAS ETAPAS, de propósito:
  --fetch   vai à Wikipédia e congela o extrato em historico_2018_2022.json
            (com revid e data de acesso). É a ÚNICA etapa com rede.
  (sem flag) lê o extrato versionado e calcula calibracao_erro.json.
            Determinístico, offline, e é o que o gate roda.

Assim a calibração é auditável: o número publicado tem origem num extrato que
está no git, e não numa página que pode ser editada amanhã.

MÉTRICA PRÉ-ESPECIFICADA (escrita ANTES de olhar o resultado, mesma disciplina
do §5.4 da retrospectiva da Copa):
  - janela: pesquisa com campo_fim em [dia da eleição - 7 ; dia da eleição - 1];
  - por instituto, vale a ÚLTIMA pesquisa da janela (a mais próxima da urna);
  - candidatos: os 4 primeiros do resultado oficial no 1º turno, os 2 do 2º;
  - share normalizado ENTRE ESSES candidatos, dos dois lados, que é a mesma
    normalização do motor (invariante à base);
  - erro = share previsto - share apurado, em pontos percentuais;
  - ERRO_ELEICAO estimado = DESVIO-PADRÃO do erro do AGREGADO (média simples dos
    institutos) por (rodada, candidato), agrupando as 4 rodadas. É desvio e não
    média porque é assim que o parâmetro é usado no modelo: N(0, ERRO_ELEICAO).

TABELA ESCOLHIDA POR ASSINATURA DE COLUNA, nunca por heading. Em 2022 as tabelas
[13] (agregadores) e [14] (pesquisas de verdade) têm o MESMO contexto de
heading, porque o h4 "Agregação de pesquisas" vaza para a tabela seguinte, que
não tem heading próprio. Quem confia no heading lê o agregador achando que é
pesquisa.

FAIL-CLOSED: perfil que não casa, janela vazia ou candidato sem coluna derrubam
o run com exit != 0. Calibração pela metade é pior que calibração nenhuma,
porque vira número publicado com origem falsa.

Uso:
    python3 src/ingest_historico.py --fetch   # rede: congela o extrato
    python3 src/ingest_historico.py           # offline: calcula a calibração
"""
import datetime as dt
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)

import ingest_polls as ip   # SÓ leitura: parser reaproveitado, nada é alterado lá

BRUTO = os.path.join(ROOT, "data", "eleicoes", "historico_2018_2022.json")
OUT = os.path.join(ROOT, "data", "eleicoes", "calibracao_erro.json")

JANELA_D = 7          # dias antes da eleição
TOPN_1T = 4           # candidatos do 1º turno que entram na conta
AMOSTRA_MAX = 200000  # acima disso não é pesquisa: é resultado apurado disfarçado

PAG_2018 = "Pesquisas de opinião para a eleição presidencial no Brasil em 2018"
PAG_2022 = "Pesquisas de opinião para a eleição presidencial no Brasil em 2022"
RES_2018 = "Resultados da eleição presidencial no Brasil em 2018"
RES_2022 = "Resultados da eleição presidencial no Brasil em 2022"

# Assinatura = (índice da linha de cabeçalho que nomeia candidato, textos que
# TÊM de estar nela, textos que NÃO podem estar). Nada de heading.
PERFIS = [
    {"id": "2018-1T", "pagina": PAG_2018, "eleicao": "2018-10-07", "ano": 2018,
     "hdr_row": 0, "data_row": 2, "modo": "celula",
     # 'NOVO' e 'Sem filiação' separam esta tabela da de HIPÓTESES de 2º turno
     # coletadas ANTES do 1º (601 linhas), que tem o mesmo perfil de coluna e
     # datas na mesma janela. O fail-closed pegou as duas na primeira execução.
     "exige": ["Período da pesquisa", "PT", "PSL", "NOVO"],
     "proibe": ["Agregador", "Sem filiação"], "min_linhas": 100},
    {"id": "2018-2T", "pagina": PAG_2018, "eleicao": "2018-10-28", "ano": 2018,
     "hdr_row": 0, "data_row": 2, "modo": "cabecalho",
     "exige": ["Período da pesquisa", "Haddad (PT)", "Bolsonaro (PSL)"],
     "proibe": ["Agregador"], "min_linhas": 10},
    {"id": "2022-1T", "pagina": PAG_2022, "eleicao": "2022-10-02", "ano": 2022,
     "hdr_row": 1, "data_row": 3, "modo": "cabecalho",
     "exige": ["Contratante / Pesquisa", "LulaPT", "BolsonaroPL", "TebetMDB"],
     "proibe": ["Agregador"], "min_linhas": 50},
    {"id": "2022-2T", "pagina": PAG_2022, "eleicao": "2022-10-30", "ano": None,
     "hdr_row": 0, "data_row": 2, "modo": "cabecalho",
     "exige": ["Instituto de Pesquisa", "LulaPT", "BolsonaroPL", "Vantagem"],
     "proibe": ["Agregador"], "min_linhas": 100},
]

RE_PROTO = re.compile(r"\bBR[-\s]?\d+[/-]\d+\b", re.I)
RE_NOTA = re.compile(r"\[[^\]]*\]")
RE_ANO = re.compile(r"\b(20\d\d)\b")
RE_CEL = re.compile(r"^(\d+(?:[.,]\d+)?)\s*%?\s*\(([^)]+)\)")
# Bloco do candidato, PRÉ-ESPECIFICADO e declarado. O viés que interessa ao M5 é
# DIRECIONAL: "este instituto subestima a direita" é acionável, "este instituto
# tem viés médio de zero" é tautologia (ver ressalva sobre soma zero).
BLOCO_HIST = {"bolsonaro": "dir", "haddad": "esq", "lula": "esq", "gomes": "esq",
              "alckmin": "centro", "tebet": "centro"}

RE_CAND = re.compile(r"\([A-Za-zÀ-ÿ\.\s]{2,14}\)\s*$")
RE_NAO_PESQUISA = re.compile(r"elei[çc][õo]?e?s?\s+de\s+\d{4}|resultado|apura", re.I)


def txt(c):
    return " ".join(c["t"].split())


def limpa_instituto(s):
    s = RE_NOTA.sub("", s)
    s = RE_PROTO.sub("", s).strip(" .,-–/")
    if "/" in s:
        s = s.rsplit("/", 1)[1].strip()
    return " ".join(s.split())


def sobrenome(nome):
    """'Fernando Haddad (PT)' -> 'haddad'; 'LulaPT' -> 'lula'."""
    n = RE_NOTA.sub("", nome)
    n = re.sub(r"\(.*?\)", "", n)
    n = re.sub(r"[A-ZÇÃÕÁÉÍÓÚÂÊÔ]{2,}$", "", n.strip())   # partido colado no fim
    toks = [t for t in re.split(r"\s+", n.strip()) if t]
    return (toks[-1] if toks else n).lower()


# --------------------------------------------------------------- fetch (rede)

def _pagina(title, cache):
    f = os.path.join(cache, re.sub(r"[^\w]", "_", title)[:90] + ".json")
    if os.path.exists(f):
        return json.load(open(f, encoding="utf-8"))
    d = ip.api({"action": "parse", "page": title, "prop": "text|revid"})["parse"]
    os.makedirs(cache, exist_ok=True)
    json.dump(d, open(f, "w", encoding="utf-8"))
    return d


def acha_tabela(items, perfil):
    """Seleciona por ASSINATURA DE COLUNA. Fail-closed se não achar exatamente 1."""
    achados = []
    for i, (ctx, g) in enumerate(items):
        if len(g) < perfil["min_linhas"]:
            continue
        hr = perfil["hdr_row"]
        if hr >= len(g):
            continue
        cab = " | ".join(txt(c) for c in g[hr])
        todos = " | ".join(txt(c) for row in g[:max(hr + 1, 2)] for c in row)
        if any(e not in cab for e in perfil["exige"]):
            continue
        if any(p in todos for p in perfil["proibe"]):
            continue
        achados.append((i, ctx, g))
    if len(achados) != 1:
        raise SystemExit(
            f"FAIL-CLOSED [{perfil['id']}]: esperava 1 tabela com a assinatura "
            f"{perfil['exige']}, achei {len(achados)}. A fonte mudou de estrutura; "
            f"confira a página na Wikipédia antes de mexer aqui.")
    return achados[0]


def extrai(perfil, items):
    i, ctx, g = acha_tabela(items, perfil)
    hr, dr = perfil["hdr_row"], perfil["data_row"]
    cab = [txt(c) for c in g[hr]]
    cab0 = [txt(c) for c in g[0]]

    def col(*pats):
        for j, h in enumerate(cab0 + cab):
            for p in pats:
                if re.search(p, h, re.I):
                    return j % len(cab0)
        return None

    c_data = col(r"per[íi]odo da pesquisa", r"data\(s\)")
    c_inst = col(r"contratante", r"instituto de pesquisa", r"publica[çc][ãa]o")
    c_amo = col(r"total de entrevistados", r"tamanho")
    if c_data is None or c_inst is None:
        raise SystemExit(f"FAIL-CLOSED [{perfil['id']}]: coluna de data ({c_data}) ou "
                         f"de instituto ({c_inst}) não identificada no cabeçalho {cab0}")

    # colunas de candidato: pelo cabeçalho (2018-2T, 2022) ou pela célula (2018-1T)
    cands_col = {}
    if perfil["modo"] == "cabecalho":
        for j, h in enumerate(cab):
            if j in (c_data, c_inst, c_amo):
                continue
            if not h or re.search(r"outros|indeciso|absten|abst\.|margem|vantagem|"
                                  r"amostra|imagem|total", h, re.I):
                continue
            cands_col[j] = sobrenome(h)

    ini = (dt.date.fromisoformat(perfil["eleicao"]) - dt.timedelta(days=JANELA_D)).isoformat()
    fim = (dt.date.fromisoformat(perfil["eleicao"]) - dt.timedelta(days=1)).isoformat()
    linhas, descartes = [], {}

    def larga(motivo):
        descartes[motivo] = descartes.get(motivo, 0) + 1

    for row in g[dr:]:
        if len(row) <= max(c_data, c_inst):
            larga("linha curta")
            continue
        bruto_inst = txt(row[c_inst])
        if RE_NAO_PESQUISA.search(bruto_inst):
            larga("linha de resultado apurado (armadilha 'Eleições de AAAA')")
            continue
        cel_data = txt(row[c_data])
        ano = perfil["ano"]
        if ano is None:                      # 2022-2T: o ano só existe na célula
            m = RE_ANO.search(cel_data)
            if not m:
                larga("sem ano na célula (2022-2T)")
                continue
            ano = int(m.group(1))
        d1, d2, raw = ip.parse_dates(cel_data, ano)
        if not d2:
            larga("data não parseada")
            continue
        if not (ini <= d2 <= fim):
            larga("fora da janela")
            continue
        amo = ip.parse_amostra(txt(row[c_amo])) if c_amo is not None else None
        if amo and amo > AMOSTRA_MAX:
            larga(f"amostra > {AMOSTRA_MAX} (não é pesquisa)")
            continue
        nums = {}
        if perfil["modo"] == "celula":
            for c in row:
                m = RE_CEL.match(txt(c))
                if m:
                    nums[sobrenome(m.group(2))] = float(m.group(1).replace(",", "."))
        else:
            for j, nome in cands_col.items():
                if j < len(row):
                    v = ip.parse_pct(txt(row[j]))
                    if v is not None:
                        nums[nome] = v
        if not nums:
            larga("nenhum percentual")
            continue
        linhas.append({"instituto": limpa_instituto(bruto_inst),
                       "instituto_bruto": bruto_inst, "campo_ini": d1, "campo_fim": d2,
                       "campo_raw": raw, "amostra": amo, "numeros": nums})
    if not linhas:
        raise SystemExit(f"FAIL-CLOSED [{perfil['id']}]: janela {ini}..{fim} ficou vazia. "
                         f"Descartes: {descartes}")
    return {"rodada": perfil["id"], "eleicao": perfil["eleicao"], "tabela_idx": i,
            "contexto": [c for c in ctx if c], "janela": [ini, fim],
            "n": len(linhas), "descartes": descartes, "pesquisas": linhas}


def resultado_oficial(items, turno):
    """Tabela 'Geral': 0=candidato, 1=vice, 2/3=1T total/%, 4/5=2T total/%."""
    col = 3 if turno == 1 else 5
    for ctx, g in items:
        if not g or "Candidato" not in txt(g[0][0]):
            continue
        out = {}
        for row in g[3:]:
            if len(row) <= col:
                continue
            nome, pct = txt(row[0]), txt(row[col])
            # Critério ESTRUTURAL, não lista de palavras: candidato é linha que
            # termina em partido entre parênteses. A tabela fecha com oito linhas
            # de contabilidade (válidos, brancos, nulos, pendentes, total,
            # abstenções, não apurado, eleitores aptos a votar), e a primeira
            # versão deste código, que excluía por palavra, deixou passar duas:
            # "Não apurado" e "Eleitores aptos a votar" (100%) viraram candidatos
            # e destruíram a normalização.
            if not RE_CAND.search(nome):
                continue
            v = ip.parse_pct(pct)
            if v is not None:
                out[sobrenome(nome)] = v
        if out:
            return out
    raise SystemExit("FAIL-CLOSED: tabela 'Geral' de resultado oficial não encontrada")


def fetch(cache):
    paginas = {}
    for t in (PAG_2018, PAG_2022, RES_2018, RES_2022):
        d = _pagina(t, cache)
        w = ip.PageWalker()
        w.feed(d["text"]["*"])
        if w.hatnotes:
            # doutrina do R1: fonte que aponta para outra página é EVENTO.
            raise SystemExit(
                f"FAIL-CLOSED: '{t}' passou a ter {len(w.hatnotes)} hatnote(s). "
                f"A página foi dividida ou passou a transcluir conteúdo. Confira "
                f"antes de calibrar em cima dela.")
        paginas[t] = {"revid": d["revid"], "items": w.items}
        print(f"  {t[:62]:62s} revid={d['revid']} tabelas={len(w.items)}")

    rodadas = [extrai(p, paginas[p["pagina"]]["items"]) for p in PERFIS]
    oficial = {
        "2018-1T": resultado_oficial(paginas[RES_2018]["items"], 1),
        "2018-2T": resultado_oficial(paginas[RES_2018]["items"], 2),
        "2022-1T": resultado_oficial(paginas[RES_2022]["items"], 1),
        "2022-2T": resultado_oficial(paginas[RES_2022]["items"], 2),
    }
    doc = {
        "schema_version": 1,
        "gerado_por": "src/ingest_historico.py --fetch",
        "acesso": dt.date.today().isoformat(),
        "fontes": {t: {"url": "https://pt.wikipedia.org/wiki/" + t.replace(" ", "_"),
                       "revid": paginas[t]["revid"]} for t in paginas},
        "janela_dias": JANELA_D,
        "rodadas": rodadas,
        "resultado_oficial": oficial,
    }
    with open(BRUTO, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"\nOK -> {os.path.relpath(BRUTO, ROOT)}")
    for r in rodadas:
        print(f"  {r['rodada']}: {r['n']} pesquisas na janela {r['janela'][0]}..{r['janela'][1]}"
              f" · descartes {r['descartes']}")
    return doc


# ---------------------------------------------------------- calibrar (offline)

def calibrar(doc):
    oficial = doc["resultado_oficial"]
    por_rodada, erros_agregado, por_instituto = [], [], {}

    for r in doc["rodadas"]:
        rid = r["rodada"]
        ofi = oficial[rid]
        alvo = sorted(ofi, key=lambda k: -ofi[k])[:(2 if rid.endswith("2T") else TOPN_1T)]
        base_ofi = sum(ofi[k] for k in alvo)
        apurado = {k: 100.0 * ofi[k] / base_ofi for k in alvo}

        ultima = {}
        for p in r["pesquisas"]:
            inst = p["instituto"]
            if inst not in ultima or p["campo_fim"] > ultima[inst]["campo_fim"]:
                ultima[inst] = p
        linhas = []
        for inst in sorted(ultima):
            nums = ultima[inst]["numeros"]
            base = sum(nums.get(k, 0.0) for k in alvo)
            if base <= 0:
                continue
            prev = {k: 100.0 * nums.get(k, 0.0) / base for k in alvo}
            for k in alvo:
                e = prev[k] - apurado[k]
                linhas.append({"instituto": inst, "candidato": k,
                               "previsto_pp": round(prev[k], 2),
                               "apurado_pp": round(apurado[k], 2), "erro_pp": round(e, 2)})
                por_instituto.setdefault(inst, []).append(
                    {"rodada": rid, "candidato": k, "erro_pp": e})
        if not linhas:
            raise SystemExit(f"FAIL-CLOSED [{rid}]: nenhum instituto casou com os "
                             f"candidatos {alvo}")
        agre = {}
        for k in alvo:
            es = [x["erro_pp"] for x in linhas if x["candidato"] == k]
            agre[k] = round(sum(es) / len(es), 2)
            erros_agregado.append(agre[k])
        por_rodada.append({
            "rodada": rid, "eleicao": r["eleicao"], "janela": r["janela"],
            "candidatos": alvo, "institutos": sorted(ultima), "n_institutos": len(ultima),
            "apurado_pp": {k: round(apurado[k], 2) for k in alvo},
            "erro_do_agregado_pp": agre,
            "mae_institutos_pp": round(
                sum(abs(x["erro_pp"]) for x in linhas) / len(linhas), 2),
            "detalhe": linhas,
        })

    sd = statistics.pstdev(erros_agregado) if len(erros_agregado) > 1 else 0.0
    priors = {}
    for i, regs in sorted(por_instituto.items()):
        por_bloco = {}
        for reg in regs:
            b = BLOCO_HIST.get(reg["candidato"])
            if b:
                por_bloco.setdefault(b, []).append(reg["erro_pp"])
        priors[i] = {
            "mae_pp": round(sum(abs(r["erro_pp"]) for r in regs) / len(regs), 2),
            "n": len(regs),
            "rodadas": sorted({r["rodada"] for r in regs}),
            "vies_por_bloco_pp": {b: round(sum(v) / len(v), 2)
                                  for b, v in sorted(por_bloco.items())},
        }
    # o mesmo corte, no agregado: é o número que o M5 vai usar como prior
    vies_bloco = {}
    for r in por_rodada:
        for k, e in r["erro_do_agregado_pp"].items():
            b = BLOCO_HIST.get(k)
            if b:
                vies_bloco.setdefault(b, []).append(e)
    vies_bloco = {b: {"medio_pp": round(sum(v) / len(v), 2), "n": len(v),
                      "valores_pp": v}
                  for b, v in sorted(vies_bloco.items())}
    sd_por_turno = {}
    for t in ("1T", "2T"):
        es = [e for r in por_rodada if r["rodada"].endswith(t)
              for e in r["erro_do_agregado_pp"].values()]
        if len(es) > 1:
            sd_por_turno[t] = round(statistics.pstdev(es), 2)
    # ver "recomendacao_base": o parâmetro é usado no sorteio de 1º turno
    sd_rec = sd_por_turno.get("1T", sd)

    doc_out = {
        "schema_version": 1,
        "gerado_por": "src/ingest_historico.py",
        "origem": {"arquivo": "data/eleicoes/historico_2018_2022.json",
                   "acesso": doc["acesso"], "fontes": doc["fontes"]},
        "metrica_pre_especificada": (
            "janela de 7 dias antes da urna; por instituto vale a ÚLTIMA pesquisa da "
            "janela; candidatos = top-4 do resultado oficial no 1º turno e os 2 do 2º; "
            "share normalizado entre esses candidatos dos dois lados; erro = previsto "
            "menos apurado, em pp; ERRO_ELEICAO = desvio-padrão do erro do AGREGADO por "
            "(rodada, candidato), agrupando as 4 rodadas"),
        "n_rodadas": len(por_rodada),
        "n_erros_agregado": len(erros_agregado),
        "erro_sistematico": {
            "sd_pp": round(sd, 2),
            "sd_share": round(sd / 100.0, 4),
            "amplitude_pp": [round(min(erros_agregado), 2), round(max(erros_agregado), 2)],
            "recomendacao_ERRO_ELEICAO": round(sd_rec / 100.0, 4),
            "recomendacao_base": (
                "Usa o desvio do 1º TURNO, não o agrupado, e o motivo é onde o "
                "parâmetro entra no modelo: no eleicoes_model_v2 o ERRO_ELEICAO compõe "
                "o `sd` que o simulate() sorteia no 1º turno, e a probabilidade do par "
                "de 2º turno vem de runoff_prob_from_polls, onde ele não entra. O "
                "análogo certo de uma corrida de Senado ou de 1º turno é o erro de 1º "
                "turno. Agrupar com o 2º turno, que é muito mais previsível (0,86pp "
                "contra 2,55pp), diluiria para baixo o parâmetro justamente onde ele "
                "é usado. Custo declarado: n cai de 12 para 8."),
            "sd_por_turno_pp": sd_por_turno,
            "sd_agrupado_pp": round(sd, 2),
            "media_e_zero_por_construcao": (
                "A média simples dos erros é zero POR CONSTRUÇÃO, e não diz nada: dentro de "
                "cada rodada os shares são normalizados a 100 dos dois lados, então o "
                "que sobra num candidato falta no outro. Vale para o agregado e para "
                "cada instituto. O que informa é o DESVIO (acima) e o viés POR BLOCO "
                "(abaixo), que não sofre disso porque não soma o bloco inteiro."),
        },
        "vies_por_bloco_pp": vies_bloco,
        "ressalvas": [
            "n pequeno: 4 rodadas de eleição presidencial brasileira. É o universo "
            "disponível, não uma amostra grande.",
            "O erro é do AGREGADO desta métrica, não do agregador do site: aqui a média "
            "é simples entre institutos, e o motor pondera por recência e amostra.",
            "Erro de 1º e de 2º turno entram juntos. São regimes diferentes (2 "
            "candidatos contra muitos) e o n não permite separar.",
            "Elenco diferente em cada ano; o prior por instituto só vale para quem "
            "aparece em mais de uma rodada, e a coluna n diz quantas observações tem.",
            "Fonte é a Wikipédia, não o TSE: o resultado apurado vem da tabela 'Geral' "
            "das páginas de Resultados, conferida contra os percentuais publicados.",
            "O viés por bloco usa um mapa candidato->bloco PRÉ-ESPECIFICADO no código "
            "(BLOCO_HIST), e Alckmin e Tebet estão como centro, o que é discutível. "
            "Eles não entram no corte esq/dir por isso.",
        ],
        "prior_por_instituto": priors,
        "rodadas": por_rodada,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc_out, f, ensure_ascii=False, indent=1)
        f.write("\n")

    print(f"\n{'rodada':8s} {'inst':>5s} {'MAE inst':>9s}  erro do agregado por candidato")
    for r in por_rodada:
        e = " ".join(f"{k}:{v:+.2f}" for k, v in r["erro_do_agregado_pp"].items())
        print(f"{r['rodada']:8s} {r['n_institutos']:5d} {r['mae_institutos_pp']:8.2f}pp  {e}")
    print(f"\nERRO SISTEMÁTICO (o que o M4 vinha chutando em 2,5pp):")
    print(f"  desvio agrupado {sd:.2f}pp · 1º turno {sd_por_turno.get('1T')}pp · "
          f"2º turno {sd_por_turno.get('2T')}pp")
    print(f"  RECOMENDADO (usa o 1º turno, que é onde o parâmetro entra no modelo):")
    print(f"     ERRO_ELEICAO = {sd_rec/100:.4f}   ({sd_rec:.2f}pp)")
    print(f"  amplitude {min(erros_agregado):+.2f} a {max(erros_agregado):+.2f}pp · "
          f"n = {len(erros_agregado)}")
    print(f"  (a MÉDIA é zero por construção, não por ausência de viés: ver o JSON)")
    print(f"\nVIÉS POR BLOCO, que é o que o M5 vai usar:")
    for b, v_ in vies_bloco.items():
        print(f"  {b:7s} {v_['medio_pp']:+6.2f}pp  (n={v_['n']}, valores {v_['valores_pp']})")
    print(f"\nINSTITUTOS com mais observações (MAE e viés direcional):")
    for i, v_ in sorted(priors.items(), key=lambda kv: (-kv[1]["n"], kv[1]["mae_pp"]))[:8]:
        vb = " ".join(f"{b}:{x:+.2f}" for b, x in v_["vies_por_bloco_pp"].items())
        print(f"  {i[:26]:26s} mae {v_['mae_pp']:5.2f}pp n={v_['n']:2d}  {vb}")
    print(f"\nOK -> {os.path.relpath(OUT, ROOT)}")


def main():
    if "--fetch" in sys.argv:
        cache = os.environ.get("WIKI_CACHE", os.path.join(ROOT, ".api_cache", "hist"))
        doc = fetch(cache)
    else:
        if not os.path.exists(BRUTO):
            raise SystemExit(f"{os.path.relpath(BRUTO, ROOT)} não existe. Rode primeiro "
                             f"com --fetch (é a única etapa que usa rede).")
        doc = json.load(open(BRUTO, encoding="utf-8"))
    calibrar(doc)


if __name__ == "__main__":
    main()
