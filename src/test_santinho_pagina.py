#!/usr/bin/env python3
"""
Gates do Santinho Virtual (dist/santinho.html + dist/santinho/dep + data/eleicoes/santinho).

Integridade do dado (fonte TSE):
1. Só candidaturas na urna: confere contra eleicoes2026_structure.json (concorrendo=false fica de fora).
2. Número único por cargo e UE (a colinha nunca aponta para duas pessoas).
3. Dígitos do número batem com o cargo (2/3/4/5).
4. Link oficial do TSE em todas as candidaturas, com o sq e a UE certos.
5. Nada inferido: pauta e espectro do CANDIDATO só existem com detalhes públicos (santinho_detalhes.json).
6. Nenhum dado pessoal sensível do CSV do TSE (CPF, título, e-mail, nascimento) na saída.
Página:
3b. Voto anulado / sub judice sinalizado; substituído após a carga da urna fora da lista.
7. Zero dependência externa (só hiperlink TSE e o link CC do rodapé).
8. Sem travessão espaçado " — " (regra editorial PT-BR).
9. Navegação por cargo fora dos filtros (abas), 27 UFs, disclaimer no rodapé, isolamento (sem nav do hub).
10. Estático-primeiro: candidatos a presidente pré-renderizados no HTML.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tse import link_ficha  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
SRC = os.path.join(ROOT, "data", "eleicoes", "santinho")
UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA",
       "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"]
DIGITOS = {"presidente": 2, "governador": 2, "senador": 3, "deputado_federal": 4, "deputado_estadual": 5}
ok = lambda m: print("ok  ", m)


def main():
    base = json.load(open(os.path.join(SRC, "base.json"), encoding="utf-8"))
    todos = list(base["candidatos"])
    for uf in UFS:
        todos += json.load(open(os.path.join(DIST, "santinho", "dep", f"{uf}.json"), encoding="utf-8"))
    assert len(todos) > 15000, len(todos)

    # 1. só quem está na urna, conferido contra a structure do modelo (pipeline independente).
    # Desde 03/10/2026 o modelo tira da disputa o "Nulo técnico" (concorrendo=false), mas o nome
    # continua na tela da urna: o santinho mantém essas candidaturas com o alerta de voto anulado.
    st = json.load(open(os.path.join(ROOT, "data", "eleicoes2026_structure.json"), encoding="utf-8"))
    cands = [c for r in st["races"].values() for c in r["candidates"]]
    na_urna = {str(c["sq"]) for c in cands if c.get("concorrendo", True) or c.get("destino_voto") == "Nulo técnico"}
    fora = {str(c["sq"]) for c in cands} - na_urna
    sq_maj = {c["sq"] for c in base["candidatos"]}
    assert not (sq_maj & fora), f"candidatura fora da urna no santinho: {sq_maj & fora}"
    assert sq_maj == na_urna, f"majoritários divergem da structure: {len(sq_maj ^ na_urna)}"
    destino = {str(c["sq"]): c.get("destino_voto") for c in cands}
    if any(destino.values()):
        mapa = {"Nulo técnico": "nulo", "Anulado sub judice": "sub_judice"}
        for c in base["candidatos"]:
            assert c.get("voto") == mapa.get(destino[c["sq"]]), (c["urna"], c.get("voto"), destino[c["sq"]])
    ok(f"{len(sq_maj)} majoritários = os que estão na urna segundo a structure ({len(fora)} fora); selo de voto bate com destino_voto")

    # 2 e 3. número único por (cargo, UF) e com os dígitos do cargo
    vistos = {}
    for c in todos:
        k = (c["cargo"], c["uf"], c["num"])
        assert k not in vistos, f"número repetido: {k} {vistos[k]} / {c['urna']}"
        vistos[k] = c["urna"]
        assert len(c["num"]) == DIGITOS[c["cargo"]], (c["urna"], c["num"], c["cargo"])
    ok(f"{len(todos)} candidaturas, número único por cargo/UF e com os dígitos certos")

    # 3b. voto que não conta é sinalizado (erro plantado pela realidade: Avalanche, PRES,
    # renúncia com "Nulo técnico" no TSE de 03/10/2026; Gringo Loko substituído após a carga)
    for c in todos:
        if c.get("voto"):
            assert c["voto"] in ("nulo", "sub_judice") and c.get("situacao"), c["urna"]
    av = [c for c in base["candidatos"] if c["sq"] == "280002554479"]
    assert av and av[0].get("voto") == "nulo", "Avalanche deveria estar marcado com voto nulo"
    assert not any(c["urna"] == "Gringo Loko" for c in todos), "substituído após a carga não pode ficar na lista"
    js = open(os.path.join(DIST, "santinho.html"), encoding="utf-8").read()
    assert "Voto será anulado" in js and "Voto pode não contar" in js
    ok(f"{sum(1 for c in todos if c.get('voto'))} candidaturas com voto anulado ou sub judice sinalizadas")

    # 4. link oficial
    for c in todos:
        ue = "BR" if c["cargo"] == "presidente" else c["uf"]
        assert c["link"] == link_ficha(c["sq"], ue), c
    ok("link da ficha oficial do TSE em 100% das candidaturas, com sq e UE certos")

    # 5. nada inferido
    curados = [c for c in todos if "detalhes" in c]
    for c in todos:
        assert "posicionamentos" not in c and "espectro" not in c, f"campo inferido na raiz: {c['urna']}"
    assert 0 < len(curados) < 100, len(curados)
    ok(f"pauta/espectro do candidato só via detalhes públicos ({len(curados)} candidaturas)")

    # 6. sem dado pessoal sensível
    proibidos = {"cpf", "titulo", "email", "nascimento", "NR_CPF_CANDIDATO", "NR_TITULO_ELEITORAL_CANDIDATO", "DS_EMAIL"}
    for c in todos:
        assert not (set(c) & proibidos), c["urna"]
    html = open(os.path.join(DIST, "santinho.html"), encoding="utf-8").read()
    assert not re.search(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", html), "CPF formatado no HTML"
    csv_tse = os.path.join(ROOT, ".cache", "tse", "consulta_cand_2026_BRASIL.csv")
    if os.path.exists(csv_tse):  # local: prova direta contra os CPFs reais (no CI o CSV não existe)
        import csv
        cpfs = {r["NR_CPF_CANDIDATO"] for r in csv.DictReader(open(csv_tse, encoding="latin1"), delimiter=";")}
        saida = html + json.dumps(todos)
        achados = [x for x in re.findall(r"\d{11}", saida) if x in cpfs]
        assert not achados, f"{len(achados)} CPF(s) reais na saída"
        ok(f"nenhum dos {len(cpfs)} CPFs do CSV do TSE aparece na saída")
    ok("nenhum CPF, título, e-mail ou nascimento na saída")

    # 7. zero dependência externa
    origens = set(re.findall(r"https?://[a-z0-9.-]+", html))
    assert origens <= {"https://divulgacandcontas.tse.jus.br", "https://creativecommons.org"}, origens
    assert not re.search(r"<(script|link|img)[^>]+(src|href)=[\"']https?://", html), "recurso externo carregado"
    ok(f"zero dependência externa (hiperlinks: {sorted(origens)})")

    # 8. regra editorial
    # regra editorial vale para o TEXTO (visível + strings da UI e dos dados); comentário de
    # código compartilhado (shell.CSS/JS) é código e fica como está
    sem_coment = re.sub(r"(?ms)/\*.*?\*/|^\s*//.*?$", "", html)
    assert not re.search(r"\s—\s", sem_coment), "travessão espaçado no texto"
    assert not re.search(r"\s—\s", json.dumps(todos, ensure_ascii=False)), "travessão espaçado nos dados"
    ok("sem travessão espaçado no texto e nos dados")

    # 9. navegação e conteúdo
    for cid in DIGITOS:
        assert f'data-cargo="{cid}"' in html and 'role="tab"' in html, cid
    for uf in UFS:
        assert f'value="{uf}"' in html, uf
    assert 'class="rodape"' in html and "não assume responsabilidade por decisões de voto de terceiros" in html
    assert 'nav class="tabs"' not in html, "navbar do hub não deve aparecer na página isolada"
    assert "safe-area-inset-bottom" in html
    assert "avaliação do autor" not in html.lower(), "rótulo antigo 'avaliação do autor' ainda na página"
    assert 'value="num"' not in html, "ordenação só por número foi retirada"
    for k in ('value="esp"', 'value="nome"', 'value="chance"', 'id="c-imagem"', 'data-pb="1"'):
        assert k in html, k
    pautas = base["meta"]["pautas"]
    assert all(p.get("verde") in ("favor", "contra", None) for p in pautas), "campo 'verde' inválido nas pautas"
    assert not re.search(r"progressist|conservador", html, re.I), "a página não pode escrever rótulo progressista/conservador"
    ok("abas de cargo, 27 UFs, disclaimer, ordenação (espectro/nome/chance), colinha em imagem e P&B, destaque verde/vermelho sem rótulo")

    # 10. estático-primeiro
    for c in base["candidatos"]:
        if c["cargo"] == "presidente":
            assert f">{c['urna']}</h3>" in html, c["urna"]
    ok("candidatos a presidente pré-renderizados (funciona sem JS)")
    print("TESTES DO SANTINHO VERDES.")


if __name__ == "__main__":
    sys.exit(main())
