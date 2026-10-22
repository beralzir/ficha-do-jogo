#!/usr/bin/env python3
"""
Baixa a apuração oficial do 1º turno (04/10/2026) do resultados.tse.jus.br:
JSON "dados simplificados" de presidente (BR) e de governador e senador (27 UFs).

Os códigos saem do índice público `comum/config/ele-c.json` (em 22/10: 6257 =
Federal 1º turno, presidente; 6259 = Estadual 1º turno, governador e senador),
não são fixados no código. O nome do arquivo de resultado é tentado em variantes
(o índice só dá o diretório `dados/<uf>`). Grava os
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


def codigos(pasta):
    """{cargo: código da eleição} lido do índice: presidente na Federal, governador
    e senador na Estadual, ambas de 04/10/2026, 1º turno."""
    raw = get(f"{BASE}/comum/config/ele-c.json")
    open(os.path.join(pasta, "_ele-c.json"), "wb").write(raw)   # cru, para diagnóstico
    idx = json.loads(raw)
    out = {}
    for pl in idx.get("pl", []):
        if pl.get("dt") != "04/10/2026":
            continue
        for e in pl.get("e", []):
            if str(e.get("t")) != "1":
                continue
            for ab in e.get("abr", []):
                for cp in ab.get("cp", []):
                    if str(cp["cd"]) in ("1", "3", "5"):
                        out.setdefault(int(cp["cd"]), str(e["cd"]))
    if sorted(out) != [1, 3, 5]:
        raise SystemExit(f"códigos de eleição incompletos no ele-c.json: {out}")
    return out


def nomes(ab, cargo, cod):
    c, e = f"c{cargo:04d}", f"e{int(cod):06d}"
    return [(f"dados-simplificados/{ab}", f"{ab}-{c}-{e}-r.json"),
            (f"dados/{ab}", f"{ab}-{c}-{e}-r.json"),
            (f"dados/{ab}", f"{ab}-{c}-{e}-v.json"),
            (f"dados/{ab}", f"{ab}-{c}-{e}-u.json")]


def main():
    pasta = sys.argv[1]
    os.makedirs(pasta, exist_ok=True)
    log = {"ok": [], "falhou": []}
    cods = codigos(pasta)
    log["codigos"] = cods
    alvos = [("br", 1)] + [(uf.lower(), c) for uf in UFS for c in (3, 5)]
    for ab, cargo in alvos:
        tent = []
        for sub, nome in nomes(ab, cargo, cods[cargo]):
            url = f"{BASE}/ele2026/{cods[cargo]}/{sub}/{nome}"
            try:
                raw = get(url)
                json.loads(raw)
                open(os.path.join(pasta, nome), "wb").write(raw)
                log["ok"].append(url)
                break
            except Exception as e:  # noqa: BLE001
                tent.append([url, repr(e)[:120]])
        else:
            log["falhou"].append(tent)
    json.dump(log, open(os.path.join(pasta, "_indice.json"), "w"), ensure_ascii=False, indent=1)
    print(f"códigos {cods}: {len(log['ok'])}/55 arquivos, {len(log['falhou'])} falhas")


if __name__ == "__main__":
    main()
