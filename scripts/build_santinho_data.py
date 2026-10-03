#!/usr/bin/env python3
"""
Gera a base do Santinho Virtual a partir dos DADOS ABERTOS DO TSE.

Fonte única de identidade (número, nome, partido, gênero declarado, ocupação,
situação na urna): consulta_cand_2026.zip + consulta_cand_complementar_2026.zip
(cdn.tse.jus.br). Os CSVs ficam em .cache/tse/ (gitignored: trazem CPF e título
de eleitor, que NUNCA entram na saída). Para atualizar:

  curl -o c.zip https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_2026.zip
  curl -o k.zip https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand_complementar/consulta_cand_complementar_2026.zip
  unzip -j c.zip '*BRASIL.csv' -d .cache/tse && unzip -j k.zip '*BRASIL.csv' -d .cache/tse

Regras:
- Só entra quem está na urna (ST_CANDIDATO_INSERIDO_URNA = SIM) e não foi substituído
  depois da carga (ST_SUBSTITUIDO = S sai; o substituto leva `substitui`).
- Destino do voto (NM_TIPO_DESTINACAO_VOTOS) diferente de "Válido" vira `voto`
  ("nulo" ou "sub_judice") + `situacao`: a página avisa que o voto pode não contar.
- Nada é inferido: sem detalhes públicos, pauta/espectro do candidato = sem informação.
  O espectro usual do PARTIDO vai separado, rotulado como tal.
- Detalhes públicos (`detalhes`) vêm de data/eleicoes/santinho_detalhes.json, indexados
  pelo SQ_CANDIDATO; o que está em `pendente_verificacao` não sai daqui.
- Modelo (votos estimados ± sd e chance de eleição) só para majoritários.

Saída (versionada, sem dado pessoal):
  data/eleicoes/santinho/base.json        meta + presidente/governador/senador
  data/eleicoes/santinho/dep/<UF>.json    deputados federais e estaduais/distritais
"""
import csv
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
TSE_DIR = os.environ.get("TSE_DIR", os.path.join(ROOT, ".cache", "tse"))
CAND_CSV = os.path.join(TSE_DIR, "consulta_cand_2026_BRASIL.csv")
COMP_CSV = os.path.join(TSE_DIR, "consulta_cand_complementar_2026_BRASIL.csv")
OUT_DIR = os.path.join(DATA, "eleicoes", "santinho")
DETALHES_PATH = os.path.join(DATA, "eleicoes", "santinho_detalhes.json")

TSE_ELEICAO = "20322002026"  # mesmo id usado em build_eleicoes.prop_link

UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA",
       "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"]

# cargo TSE -> id interno
CARGOS = {
    "PRESIDENTE": "presidente",
    "GOVERNADOR": "governador",
    "SENADOR": "senador",
    "DEPUTADO FEDERAL": "deputado_federal",
    "DEPUTADO ESTADUAL": "deputado_estadual",
    "DEPUTADO DISTRITAL": "deputado_estadual",  # DF: mesmo slot na urna (5 dígitos)
}
MAJORITARIOS = {"presidente", "governador", "senador"}

CARGOS_META = [
    {"id": "presidente", "label": "Presidente", "curto": "Presidente", "digitos": 2},
    {"id": "governador", "label": "Governador", "curto": "Governador", "digitos": 2},
    {"id": "senador", "label": "Senador", "curto": "Senador", "digitos": 3, "vagas": 2},
    {"id": "deputado_federal", "label": "Deputado Federal", "curto": "Dep. Federal", "digitos": 4},
    {"id": "deputado_estadual", "label": "Deputado Estadual", "curto": "Dep. Estadual", "digitos": 5,
     "label_df": "Deputado Distrital", "curto_df": "Dep. Distrital"},
]

# Espectro usual do PARTIDO (não é do candidato). Exibido como "espectro do partido".
PARTIDO_ESPECTRO = {
    "PT": "esquerda", "PC do B": "esquerda", "PCdoB": "esquerda", "PSOL": "esquerda",
    "PSTU": "esquerda", "PCB": "esquerda", "PCO": "esquerda", "UP": "esquerda",
    "PV": "centro-esquerda", "REDE": "centro-esquerda", "PDT": "centro-esquerda",
    "PSB": "centro-esquerda",
    "CIDADANIA": "centro", "PSDB": "centro", "MDB": "centro", "PSD": "centro",
    "SOLIDARIEDADE": "centro", "AVANTE": "centro", "PMB": "centro", "MOBILIZA": "centro",
    "PODE": "centro-direita", "PODEMOS": "centro-direita", "PRD": "centro-direita",
    "AGIR": "centro-direita", "DEMOCRATA": "centro-direita",
    "DC": "direita", "PRTB": "direita", "REPUBLICANOS": "direita", "PP": "direita",
    "PL": "direita", "UNIÃO": "direita", "NOVO": "direita", "MISSÃO": "direita",
}

# "verde": lado da pauta destacado em verde na página (o outro lado em vermelho; neutro sem cor).
# Referência visual pessoal do Bera (03/10/2026); a página não escreve rótulo nenhum sobre isso.
# Nossa Senhora Aparecida fica sem cor: não se encaixa no eixo.
PAUTAS = [
    {"id": "lgbtqia", "label": "Direitos LGBTQIA+", "descricao": "Defesa de direitos civis, igualdade e combate à homofobia e transfobia", "verde": "favor"},
    {"id": "maconha", "label": "Descriminalização da maconha", "descricao": "Descriminalização do porte para uso pessoal e regulação medicinal ou recreativa", "verde": "favor"},
    {"id": "aborto", "label": "Legalização do aborto", "descricao": "Legalização e autonomia reprodutiva como política de saúde pública", "verde": "favor"},
    {"id": "nossa_senhora", "label": "Nossa Senhora Aparecida", "descricao": "Devoção e valorização do feriado nacional e das tradições católicas marianas", "verde": None},
    {"id": "escala_6x1", "label": "Fim da escala 6x1", "descricao": "Redução da jornada máxima de trabalho sem redução de salário", "verde": "favor"},
    {"id": "vacinas", "label": "Vacinação e ciência", "descricao": "Defesa da imunização pública e de campanhas de saúde baseadas em ciência", "verde": "favor"},
    {"id": "educacao_publica", "label": "Educação pública e gratuita", "descricao": "Investimento público direto no ensino, sem vouchers ou terceirização escolar", "verde": "favor"},
    {"id": "privatizacao_luz", "label": "Privatização da energia", "descricao": "Concessão privada e desestatização de geradoras e distribuidoras de energia", "verde": "contra"},
    {"id": "privatizacao_agua", "label": "Privatização do saneamento", "descricao": "Privatização de empresas públicas de água e esgoto (modelo Sabesp)", "verde": "contra"},
    {"id": "privatizacao_petroleo", "label": "Privatização da Petrobras", "descricao": "Venda da Petrobras e concessão das bacias petrolíferas ao setor privado", "verde": "contra"},
    {"id": "submissao_eua", "label": "Alinhamento aos EUA", "descricao": "Alinhamento prioritário à política externa norte-americana", "verde": "contra"},
    {"id": "armas", "label": "Porte e posse de armas", "descricao": "Flexibilização do Estatuto do Desarmamento para civis e CACs", "verde": "contra"},
    {"id": "taxacao_ricos", "label": "Tributação dos super-ricos", "descricao": "Imposto sobre grandes fortunas, lucros, dividendos e altas rendas", "verde": "favor"},
    {"id": "marco_temporal", "label": "Demarcação indígena", "descricao": "Demarcação de terras indígenas contra a tese do marco temporal", "verde": "favor"},
    {"id": "anistia_8_jan", "label": "Anistia ao 8 de janeiro", "descricao": "Perdão aos condenados pelas invasões das sedes dos Três Poderes", "verde": "contra"},
]
PAUTA_IDS = {p["id"] for p in PAUTAS}
POSICOES = {"favor", "contra", "neutro"}


def ler_csv(path):
    if not os.path.exists(path):
        sys.exit(f"ERRO: {path} não encontrado. Baixe os dados abertos do TSE (ver docstring).")
    with open(path, encoding="latin1", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def titulo(s):
    """Caixa de título PT-BR para nomes de urna (mantém siglas curtas e partículas)."""
    min_ = {"da", "de", "do", "das", "dos", "e"}
    pos = [0]

    def cap(m):
        w = m.group(0).lower()
        pos[0] += 1
        return w if pos[0] > 1 and w in min_ else w[:1].upper() + w[1:]
    return re.sub(r"[^\W\d_]+", cap, s.strip())


def nulo(v):
    return None if v in ("", "#NULO", "#NE", "NÃO DIVULGÁVEL", "-1", "-3") else v


def main():
    cand = ler_csv(CAND_CSV)
    comp = {r["SQ_CANDIDATO"]: r for r in ler_csv(COMP_CSV)}
    geracao = f'{cand[0]["DT_GERACAO"]} {cand[0]["HH_GERACAO"]}'

    detalhes = json.load(open(DETALHES_PATH, encoding="utf-8"))["candidatos"]
    results = json.load(open(os.path.join(DATA, "eleicoes2026_results.json"), encoding="utf-8"))
    modelo = {}
    for race_id, race in results.get("races", {}).items():
        for c in race.get("candidates", []):
            if c.get("sq") is not None:
                modelo[str(c["sq"])] = {"share": c.get("share"), "sd": c.get("sd"), "eleito": c.get("eleito")}

    nomes = {r["SQ_CANDIDATO"]: r["NM_URNA_CANDIDATO"] for r in cand}
    maj, dep = [], {uf: [] for uf in UFS}
    vistos_cur = set()
    for r in sorted(cand, key=lambda r: (r["SG_UF"], r["DS_CARGO"], int(r["NR_CANDIDATO"]))):
        cargo = CARGOS.get(r["DS_CARGO"])
        if not cargo:
            continue  # vices e suplentes
        k = comp.get(r["SQ_CANDIDATO"])
        if not k or k["ST_CANDIDATO_INSERIDO_URNA"] != "SIM":
            continue
        if k["ST_SUBSTITUIDO"] == "S":
            continue  # substituído depois da carga da urna: o voto no número vai para o substituto
        sq = r["SQ_CANDIDATO"]
        uf = "BR" if cargo == "presidente" else r["SG_UF"]
        ue = "BR" if cargo == "presidente" else r["SG_UE"]
        partido = r["SG_PARTIDO"]
        g = {"FEMININO": "F", "MASCULINO": "M"}.get(r["DS_GENERO"])
        c = {
            "sq": sq,
            "cargo": cargo,
            "uf": uf,
            "urna": titulo(r["NM_URNA_CANDIDATO"]),
            "nome": titulo(r["NM_CANDIDATO"]),
            "num": r["NR_CANDIDATO"],
            "partido": partido,
            "genero": g,
            "ocupacao": (nulo(r["DS_OCUPACAO"]) or "").capitalize() or None,
            "esp_partido": PARTIDO_ESPECTRO.get(partido),
            "link": f"https://divulgacandcontas.tse.jus.br/divulga/#/candidato/2026/{TSE_ELEICAO}/{ue}/{sq}",
        }
        # destino do voto no dia (campo oficial): o que a colinha precisa saber
        destino = k["NM_TIPO_DESTINACAO_VOTOS"]
        if destino != "Válido":
            c["voto"] = {"Nulo técnico": "nulo", "Anulado sub judice": "sub_judice"}.get(destino, "nulo")
            c["situacao"] = k["DS_SITUACAO_CANDIDATO_TOT"].capitalize()
        sub = nulo(k["SQ_SUBSTITUIDO"])
        if sub and sub in nomes:
            antigo = comp.get(sub, {})
            c["substitui"] = {
                "urna": titulo(nomes[sub]),
                # troca depois da carga: a urna ainda mostra nome e foto de quem saiu
                "na_urna": antigo.get("ST_CANDIDATO_INSERIDO_URNA") == "SIM" and antigo.get("ST_SUBSTITUIDO") == "S",
            }
        social = nulo(r["NM_SOCIAL_CANDIDATO"])
        if social:
            c["nome_social"] = titulo(social)
        if nulo(r["NM_FEDERACAO"]):
            fed = nulo(r["SG_FEDERACAO"]) or r["NM_FEDERACAO"]
            c["federacao"] = re.sub(r"\d+-", "", fed).replace("/", " / ")
        cur = detalhes.get(sq)
        if cur:
            vistos_cur.add(sq)
            a = {}
            if cur.get("espectro"):
                a["espectro"] = cur["espectro"]
            if cur.get("resumo"):
                a["resumo"] = cur["resumo"]
            if cur.get("pautas"):
                assert set(cur["pautas"]) <= PAUTA_IDS, (sq, set(cur["pautas"]) - PAUTA_IDS)
                assert set(cur["pautas"].values()) <= POSICOES, sq
                a["pautas"] = cur["pautas"]
            if a:
                c["detalhes"] = a
        if cargo in MAJORITARIOS and sq in modelo:
            c["modelo"] = modelo[sq]
        (maj if cargo in MAJORITARIOS else dep[uf]).append(c)

    orfaos = sorted(set(detalhes) - vistos_cur)
    if orfaos:
        print(f"AVISO: {len(orfaos)} curados fora da urna/base: {orfaos}")

    os.makedirs(os.path.join(OUT_DIR, "dep"), exist_ok=True)
    meta = {
        "fonte": "TSE, dados abertos: consulta_cand_2026 e consulta_cand_complementar_2026 (cdn.tse.jus.br)",
        "geracao_tse": geracao,
        "sha256": {"consulta_cand": sha256(CAND_CSV), "complementar": sha256(COMP_CSV)},
        "regra": "somente candidaturas inseridas na urna (ST_CANDIDATO_INSERIDO_URNA = SIM)",
        "cargos": CARGOS_META,
        "ufs": UFS,
        "pautas": PAUTAS,
        "espectros": ["esquerda", "centro-esquerda", "centro", "centro-direita", "direita"],
        "contagem": {
            "majoritarios": len(maj),
            "deputados": {uf: len(v) for uf, v in dep.items()},
        },
    }
    with open(os.path.join(OUT_DIR, "base.json"), "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "candidatos": maj}, f, ensure_ascii=False, separators=(",", ":"))
    for uf, lst in dep.items():
        with open(os.path.join(OUT_DIR, "dep", f"{uf}.json"), "w", encoding="utf-8") as f:
            json.dump(lst, f, ensure_ascii=False, separators=(",", ":"))
    total_dep = sum(len(v) for v in dep.values())
    print(f"TSE {geracao}: {len(maj)} majoritários, {total_dep} deputados em {len(UFS)} UFs, "
          f"{len(vistos_cur)} com detalhes públicos")


if __name__ == "__main__":
    main()
