#!/usr/bin/env python3
"""
Monta data/eleicoes/resultado_1t.json (apuração oficial do 1º turno, 04/10/2026).

O CDN do TSE devolve 403 Akamai fora de navegador (mesma barreira da captura de
candidatos, ver build_eleicoes_structure.py), então os arquivos são baixados NO
NAVEGADOR e este script é OFFLINE e determinístico.

Entradas aceitas (uma pasta, misturar é permitido):
  1. JSON "dados simplificados" do resultados.tse.jus.br, um por cargo e
     abrangência (presidente BR; governador e senador por UF). De cada
     candidato lê `sqcand` (SQ_CANDIDATO), `pvap` (% dos válidos, "43,20") e
     `st` ("Eleito", "2º turno", "Não eleito"...). A corrida NÃO é lida do
     cabeçalho: sai do sq, que pertence a uma corrida só na structure. Assim
     uma mudança de nome de campo no cabeçalho não troca uma corrida por outra.
  2. CSV manual (plano B), `;` como separador, com cabeçalho
     `corrida;sq;votos_validos_pct;situacao` (ex.: `GOV-DF;70002553055;41,2;2º turno`).

Saída: votos válidos como fração (Σ = 1 por corrida; o TSE arredonda a 2 casas,
então renormaliza e reprova se a soma bruta fugir de 100% por mais de 0,5pp).
Depois roda o MESMO gate do motor (`em.valida_resultado_1t`, completo=True): 55
corridas, sq da corrida, eleito = mais votado, 2º turno só com o 1º abaixo de 50%.
Gate reprovado: não escreve nada.

Uso:  python3 scripts/build_resultado_1t.py <pasta-com-os-arquivos> [--fonte "texto"]
"""
import csv
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
import eleicoes_model as em        # noqa: E402

OUT = em.RESULTADO_1T


def pct_br(x):
    return float(str(x).strip().replace("%", "").replace(".", "").replace(",", ".")) \
        if "," in str(x) else float(str(x).strip().replace("%", ""))


def situacao(st):
    t = (st or "").lower()
    if "2º turno" in t or "2o turno" in t or "segundo turno" in t:
        return "2t"
    if t.startswith("eleito") or "eleito por" in t:
        return "eleito"
    return "nao"


def linhas_json(path):
    """[(sq, pct, situacao)] de um JSON do TSE, procurando a lista `cand` em qualquer nível."""
    doc = json.load(open(path, encoding="utf-8"))
    out = []

    def anda(x):
        if isinstance(x, dict):
            if "sqcand" in x and "pvap" in x:
                out.append((int(x["sqcand"]), pct_br(x["pvap"]), situacao(x.get("st"))))
                return
            for k in sorted(x):
                anda(x[k])
        elif isinstance(x, list):
            for y in x:
                anda(y)
    anda(doc)
    return out


def linhas_csv(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter=";"):
            out.append((int(row["sq"]), pct_br(row["votos_validos_pct"]), situacao(row["situacao"]),
                        row["corrida"].strip()))
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    pasta = sys.argv[1]
    fonte = sys.argv[sys.argv.index("--fonte") + 1] if "--fonte" in sys.argv else \
        "resultados.tse.jus.br, dados simplificados, baixados no navegador"
    st = em.load(em.STRUCT)
    corrida_de = {c["sq"]: k for k, r in st["races"].items() for c in r["candidates"]}

    brutas = {}           # corrida -> {sq: (pct, situacao)}
    sem_corrida = []
    arquivos = sorted(glob.glob(os.path.join(pasta, "*.json")) + glob.glob(os.path.join(pasta, "*.csv")))
    for path in arquivos:
        rows = linhas_csv(path) if path.endswith(".csv") else [r + (None,) for r in linhas_json(path)]
        for sq, p, sit, corrida_csv in rows:
            k = corrida_de.get(sq)
            if k is None:
                sem_corrida.append((os.path.basename(path), sq))
                continue
            if corrida_csv and corrida_csv != k:
                sys.exit(f"REPROVADO: {path}: sq {sq} declarado em {corrida_csv}, mas é de {k}")
            ant = brutas.setdefault(k, {}).get(sq)
            if ant is not None and ant != (p, sit):
                sys.exit(f"REPROVADO: sq {sq} ({k}) aparece com valores diferentes em dois arquivos")
            brutas[k][sq] = (p, sit)
    if sem_corrida:
        print(f"AVISO: {len(sem_corrida)} sq fora da structure (ignorados): {sem_corrida[:5]}")

    races, bad = {}, []
    for k in sorted(brutas):
        b = brutas[k]
        tot = sum(p for p, _ in b.values())
        if abs(tot - 100.0) > 0.5:
            bad.append(f"{k}: Σ% dos válidos = {tot:.2f} (esperado 100)")
            continue
        vv = {str(sq): round(p / tot, 6) for sq, (p, _) in sorted(b.items())}
        sit = {sq: s for sq, (_, s) in b.items()}
        fin = sorted(sq for sq, s in sit.items() if s == "2t")
        ele = sorted(sq for sq, s in sit.items() if s == "eleito")
        if fin and ele:
            bad.append(f"{k}: tem eleito E 2º turno ao mesmo tempo")
        elif fin:
            races[k] = {"status": "segundo_turno", "finalistas": fin, "votos_validos": vv}
        else:
            races[k] = {"status": "decidida", "eleitos": ele, "votos_validos": vv}
    bad += em.valida_resultado_1t(races, st)
    if bad:
        for b in bad:
            print("REPROVADO:", b)
        sys.exit(1)

    doc = {"meta": {"fonte": fonte, "turno1": st["meta"]["dates"]["turno1"],
                    "arquivos": [os.path.basename(a) for a in arquivos],
                    "gerado_por": "scripts/build_resultado_1t.py"},
           "races": races}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    n2 = sum(1 for r in races.values() if r["status"] == "segundo_turno")
    print(f"OK -> data/eleicoes/resultado_1t.json · {len(races)} corridas · {n2} com 2º turno: "
          + ", ".join(sorted(k for k, r in races.items() if r["status"] == "segundo_turno")))


if __name__ == "__main__":
    main()
