#!/usr/bin/env python3
"""
Baixa a apuração oficial do 1º turno (04/10/2026) do resultados.tse.jus.br:
JSON "dados simplificados" de presidente (BR) e de governador e senador (27 UFs).

O código da eleição sai do índice público `comum/config/ele-c.json` (eleição
ordinária federal, 1º turno, ano 2026), não é fixado no código. Grava os
arquivos crus em <pasta> para o `build_resultado_1t.py` ler, e um índice do que
baixou e do que falhou. Falha de rede numa UF não aborta: o conversor reprova
depois, com o gate de 55 corridas.

Uso:  python3 scripts/baixa_resultado_tse.py <pasta>
"""
import json
import os
import sys
import time
import urllib.request

BASE = "https://resultados.tse.jus.br/oficial"
UA = {"User-Agent": "Mozilla/5.0 (ficha-do-jogo; apuracao 1o turno)", "Accept": "application/json"}
UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA",
       "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"]


def get(url):
    for i in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(2 * (i + 1))
    raise err


def codigo_eleicao(log, pasta):
    raw = get(f"{BASE}/comum/config/ele-c.json")
    open(os.path.join(pasta, "_ele-c.json"), "wb").write(raw)   # cru, para diagnóstico
    idx = json.loads(raw)
    cands = []
    for pl in idx.get("pl", []):
        for e in pl.get("e", []):
            cands.append(e)
    # 1º turno da ordinária federal de 2026: tipo ordinária, turno 1, data 04/10/2026
    for e in cands:
        if str(e.get("t")) == "1" and "04/10/2026" in str(e.get("dt", "")) and str(e.get("tp")) in ("1", "0"):
            return str(e["cd"])
    for e in cands:
        if str(e.get("t")) == "1" and "04/10/2026" in str(e.get("dt", "")):
            return str(e["cd"])
    raise SystemExit("eleição de 04/10/2026, 1º turno, não achada no ele-c.json (salvo no índice)")


def main():
    pasta = sys.argv[1]
    os.makedirs(pasta, exist_ok=True)
    log = {"ok": [], "falhou": []}
    cod = codigo_eleicao(log, pasta)
    alvos = [("br", "0001")] + [(uf.lower(), c) for uf in UFS for c in ("0003", "0005")]
    for ab, cargo in alvos:
        nome = f"{ab}-c{cargo}-e{int(cod):06d}-r.json"
        url = f"{BASE}/ele2026/{cod}/dados-simplificados/{ab}/{nome}"
        try:
            raw = get(url)
            json.loads(raw)
            open(os.path.join(pasta, nome), "wb").write(raw)
            log["ok"].append(nome)
        except Exception as e:  # noqa: BLE001
            log["falhou"].append([url, repr(e)[:200]])
    log["codigo"] = cod
    json.dump(log, open(os.path.join(pasta, "_indice.json"), "w"), ensure_ascii=False, indent=1)
    print(f"eleição {cod}: {len(log['ok'])}/55 arquivos, {len(log['falhou'])} falhas")


if __name__ == "__main__":
    main()
