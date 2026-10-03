"""Link para a ficha oficial da candidatura no DivulgaCandContas (TSE).

FONTE ÚNICA do formato, usada pelas páginas da edição (build_eleicoes.prop_link) e pelo
santinho (scripts/build_santinho_data.py). Em 03/10/2026 o TSE trocou o formato e o antigo,
`#/candidato/2026/<id eleição>/<UE>/<sq>`, passou a abrir "ERRO AO CARREGAR A PÁGINA".
O formato atual foi lido da própria interface do TSE (lista de candidatos → clique na
ficha) e conferido em presidente (BR), governador (NORTE/AM), deputado estadual
(SUDESTE/SP) e distrital (CENTROOESTE/DF):

    #/candidato/<REGIÃO>/<UF>/<id eleição>/<sq>/<ano>/<UE>

Presidente usa BR nos três lugares. Hiperlink não é dependência (invariante 4).
"""

TSE_ELEICAO = "20322002026"   # id da eleição geral de 2026 no DivulgaCandContas
ANO = "2026"

# Regiões como a interface do TSE escreve (select "Selecione uma regiao").
REGIAO = {
    **dict.fromkeys(["AC", "AM", "AP", "PA", "RO", "RR", "TO"], "NORTE"),
    **dict.fromkeys(["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"], "NORDESTE"),
    **dict.fromkeys(["DF", "GO", "MS", "MT"], "CENTROOESTE"),
    **dict.fromkeys(["ES", "MG", "RJ", "SP"], "SUDESTE"),
    **dict.fromkeys(["PR", "RS", "SC"], "SUL"),
}


def link_ficha(sq, ue):
    """URL da ficha do candidato `sq` na UE `ue` ("BR" para presidente, sigla da UF nos demais)."""
    ue = str(ue).upper()
    regiao, uf = ("BR", "BR") if ue == "BR" else (REGIAO[ue], ue)
    return (f"https://divulgacandcontas.tse.jus.br/divulga/#/candidato/"
            f"{regiao}/{uf}/{TSE_ELEICAO}/{sq}/{ANO}/{ue}")
