#!/usr/bin/env python3
"""
Empacota as FOTOS OFICIAIS do TSE para o Santinho Virtual.

Entrada: .cache/tse/fotos/foto_<UF>.zip (dados abertos do TSE, um zip por UF e "BR"):
  https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/fotos/foto_cand2026_<UF>_div.zip
Cada zip traz F<UF><SQ>_div.jpg (161x225).

Saída: dist/santinho/fotos/<GRUPO>-<k>.json = {"<sq>": "data:image/jpeg;base64,..."}
em blocos de BLOCO fotos, para a página carregar só o que aparece na tela e não
estourar o limite de arquivos do Cloudflare (seriam ~19 mil arquivos soltos).
A página acha o bloco sozinha: posição do candidato no grupo (ordem dos
arquivos de dados) dividida por BLOCO. Mesma conta nos dois lados.

Miniatura: `sips` (macOS) ou `mogrify` (ImageMagick, CI Linux) reduz para 96 px de altura. Sem nenhum, a foto
original entra como está (pacotes ~2x maiores). Sem zip, o candidato fica com as
iniciais, que é o fallback da página. NÃO versionado: dist/santinho/fotos é gerado.
"""
import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOTOS_DIR = os.environ.get("TSE_FOTOS_DIR", os.path.join(ROOT, ".cache", "tse", "fotos"))
BASE_DIR = os.path.join(ROOT, "data", "eleicoes", "santinho")
OUT = os.path.join(ROOT, "dist", "santinho", "fotos")
BLOCO = 200
ALTURA = 96

GRUPO_CARGO = {"presidente": "maj", "governador": "maj", "senador": "maj",
               "deputado_federal": "fed", "deputado_estadual": "est"}


def candidatos():
    base = json.load(open(os.path.join(BASE_DIR, "base.json"), encoding="utf-8"))
    for c in base["candidatos"]:
        yield c
    for uf in base["meta"]["ufs"]:
        for c in json.load(open(os.path.join(BASE_DIR, "dep", f"{uf}.json"), encoding="utf-8")):
            yield c


def ferramenta():
    """sips (macOS) ou mogrify (ImageMagick, Linux/CI); sem nenhuma, a foto entra original."""
    if shutil.which("sips"):
        return "sips"
    if shutil.which("mogrify"):
        return "mogrify"
    return None


def reduzir(uf, z, tmp, tool):
    """Extrai o zip da UF e reduz tudo em lote (uma chamada por 500 arquivos)."""
    d_in, d_out = os.path.join(tmp, uf), os.path.join(tmp, uf + "_out")
    os.makedirs(d_in)
    os.makedirs(d_out)
    z.extractall(d_in)
    arquivos = sorted(os.path.join(d_in, f) for f in os.listdir(d_in) if f.endswith(".jpg"))
    for i in range(0, len(arquivos), 500):
        lote = arquivos[i:i + 500]
        if tool == "sips":
            subprocess.run(["sips", "--resampleHeight", str(ALTURA), "-s", "format", "jpeg",
                            "-s", "formatOptions", "60", *lote, "--out", d_out], capture_output=True)
        elif tool == "mogrify":
            subprocess.run(["mogrify", "-path", d_out, "-resize", f"x{ALTURA}", "-strip",
                            "-quality", "60", *lote], capture_output=True)
    return d_in, d_out


def main():
    tool = ferramenta()
    grupos = {}  # "SP-fed" -> [cand...], na ordem dos arquivos de dados (a página repete a conta)
    for c in candidatos():
        grupos.setdefault(f'{c["uf"]}-{GRUPO_CARGO[c["cargo"]]}', []).append(c)

    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    total, sem_foto, bytes_, dirs = 0, 0, 0, {}
    tmp = tempfile.mkdtemp()
    try:
        for grupo in sorted(grupos):
            lista = grupos[grupo]
            for k in range(0, len(lista), BLOCO):
                pacote = {}
                for c in lista[k:k + BLOCO]:
                    uf = c["uf"]  # presidente -> BR
                    if uf not in dirs:
                        p = os.path.join(FOTOS_DIR, f"foto_{uf}.zip")
                        dirs[uf] = reduzir(uf, zipfile.ZipFile(p), tmp, tool) if os.path.exists(p) else None
                    if not dirs[uf]:
                        sem_foto += 1
                        continue
                    nome = f'F{uf}{c["sq"]}_div.jpg'
                    f = next((os.path.join(d, nome) for d in (dirs[uf][1], dirs[uf][0])
                              if os.path.exists(os.path.join(d, nome))), None)
                    if not f:
                        sem_foto += 1
                        continue
                    pacote[c["sq"]] = "data:image/jpeg;base64," + base64.b64encode(open(f, "rb").read()).decode()
                    total += 1
                if pacote:
                    s = json.dumps(pacote, separators=(",", ":"))
                    bytes_ += len(s)
                    open(os.path.join(OUT, f"{grupo}-{k // BLOCO}.json"), "w").write(s)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    n = len(os.listdir(OUT))
    print(f"fotos: {total} empacotadas, {sem_foto} sem foto no TSE, {n} arquivos, "
          f"{bytes_ / 1048576:.1f} MB ({tool or 'sem redução'})")


if __name__ == "__main__":
    sys.exit(main())
