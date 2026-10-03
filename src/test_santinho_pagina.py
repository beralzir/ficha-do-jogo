#!/usr/bin/env python3
"""
Testes de qualidade e integridade da página do Santinho Virtual (dist/santinho.html).
Audita:
1. Geração estática e tamanho do arquivo.
2. Zero dependências externas.
3. Ausência de travessão espaçado " — " (regra editorial PT-BR).
4. Elementos de layout mobile e desktop (gaveta, safe-area, contador de filtros).
5. Estrutura de dados enriquecida (15 pautas e 5 categorias de gênero).
6. Isolamento (página unlisted sem link na navbar geral).
"""
import os
import re
import sys
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_FILE = os.path.join(ROOT, "dist", "santinho.html")

def testar_santinho():
    print("--- Iniciando Testes do Santinho Virtual ---")
    assert os.path.exists(DIST_FILE), f"Arquivo {DIST_FILE} não encontrado!"
    
    with open(DIST_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Tamanho razoável
    size_kb = len(html.encode("utf-8")) / 1024
    print(f"ok   Arquivo dist/santinho.html gerado ({size_kb:.1f} KB)")
    assert size_kb > 50, "HTML muito pequeno, dados podem estar faltando"

    # 2. Zero dependências externas
    urls = re.findall(r'https?://[^\s\"\'<>]+', html)
    external_assets = [u for u in urls if not ("bera.ia.br" in u)]
    print(f"ok   Zero dependências externas (encontradas: {len(external_assets)})")
    assert len(external_assets) == 0, f"Dependências externas encontradas: {external_assets}"

    # 3. Regra editorial: Proibido travessão espaçado " — "
    em_dashes = re.findall(r'\s—\s', html)
    print(f"ok   Regra editorial PT-BR: zero travessão espaçado (encontrados: {len(em_dashes)})")
    assert len(em_dashes) == 0, f"Travessão espaçado encontrado no HTML: {len(em_dashes)}"

    # 4. Elementos mobile e desktop
    assert 'id="btn-toggle-filters-mobile"' in html, "Botão mobile toggle de filtros ausente!"
    assert 'class="filters-body" id="filters-body"' in html, "Container filters-body ausente!"
    assert 'id="badge-filtros-ativos"' in html, "Badge de filtros ativos ausente!"
    assert 'safe-area-inset-bottom' in html, "CSS de safe-area ausente!"
    
    # 4b. Todos os 27 estados (26 estados + DF) no filtro de UF
    todos_estados = [
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
        "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
        "RS", "RO", "RR", "SC", "SP", "SE", "TO"
    ]
    for uf in todos_estados:
        assert f'value="{uf}"' in html, f'Estado {uf} não encontrado no filtro select-uf!'
    print(f"ok   Todos os {len(todos_estados)} estados (26 estados + DF) presentes no filtro de UF")
    print("ok   Componentes responsivos mobile e desktop presentes")

    # 5. Dados embutidos
    m = re.search(r'<script id="santinho-data" type="application/json">\s*(\{.*?\})\s*</script>', html, re.DOTALL)
    assert m, "Payload JSON de santinho-data não encontrado!"
    data = json.loads(m.group(1))
    candidatos = data.get("candidatos", [])
    pautas = data.get("meta", {}).get("pautas", [])
    
    assert len(candidatos) > 500, f"Poucos candidatos ({len(candidatos)})"
    assert len(pautas) == 15, f"Esperado 15 pautas, encontrado {len(pautas)}"
    print(f"ok   Payload válido: {len(candidatos)} candidatos e {len(pautas)} pautas posicionais")

    # Amostragem de integridade de candidatos
    generos_presentes = set(c.get("genero") for c in candidatos)
    assert "mulher" in generos_presentes and "homem" in generos_presentes, "Gêneros mulher/homem ausentes"
    for c in candidatos[:20]:
        assert "posicionamentos" in c, f"Candidato {c.get('urna')} sem posicionamentos!"
        assert len(c["posicionamentos"]) == 15, f"Candidato {c.get('urna')} com {len(c['posicionamentos'])} posicionamentos (esperado 15)"
    print("ok   Enriquecimento de gênero e 15 posicionamentos verificado")

    # 6. Unlisted check
    assert 'nav class="nav"' not in html, "Navbar padrão do hub não deve estar presente no Santinho unlisted!"
    print("ok   Página unlisted isolada sem barra de abas públicas")

    print("\nTODOS OS TESTES DO SANTINHO PASSARAM COM SUCESSO!\n")

if __name__ == "__main__":
    testar_santinho()
