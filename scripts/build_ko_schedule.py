#!/usr/bin/env python3
"""Gera data/ko_schedule.json a partir do dump do football-data.org (wc_matches.json produzido por
scripts/fetch_wc_matches.py). Normaliza nomes ao canônico do projeto, converte UTC->BRT (UTC-3),
exclui o 3º lugar (o projeto não modela) e ordena cronologicamente. O build_bolao.py casa cada
confronto do mata-mata a uma data por frozenset({casa,fora}).

Uso:  python3 scripts/build_ko_schedule.py caminho/para/wc_matches.json  [AAAA-MM-DD-da-coleta]

Para ATUALIZAR quando a chave avançar (R16+ ganham times reais): rode de novo o fetch (GitHub Action
com o secret FOOTBALL_DATA_TOKEN, ou local) e este script; os confrontos novos passam a casar sozinhos.
Fonte validada contra o calendário oficial da FIFA (R32: Match 73-78 conferem no horário exato).
"""
import json, sys, os
from datetime import datetime, timedelta, timezone

# football-data.org -> nome canônico do projeto (só os que divergem)
ALIAS = {
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Cape Verde Islands": "Cape Verde",
    "Congo DR": "DR Congo",
}
SKIP_STAGES = {"GROUP_STAGE", "THIRD_PLACE"}  # projeto não modela 3º lugar


def norm(t):
    return ALIAS.get(t, t) if t else t


def to_brt(utc):
    d = datetime.strptime(utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return (d - timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M")


def main(src, fetched="?"):
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fd = json.load(open(src))["matches"]
    ko = sorted((m for m in fd if m["stage"] not in SKIP_STAGES), key=lambda m: m["utcDate"])
    out = {
        "provenance": (
            f"football-data.org /v4/competitions/WC/matches, colhido via GitHub Action com o secret "
            f"FOOTBALL_DATA_TOKEN ({fetched}). BRT = UTC-3. Validado contra o calendário oficial da FIFA "
            f"(R32: Match 73-78 conferem no horário exato). Nomes normalizados ao canônico do projeto. "
            f"Times de R16+ preenchem quando a chave avança (rode fetch + este script de novo)."
        ),
        "tz": "America/Sao_Paulo",
        "fetched": fetched,
        "matches": [
            {"stage": m["stage"], "utc": m["utcDate"], "kickoff_brt": to_brt(m["utcDate"]),
             "home": norm(m["home"]), "away": norm(m["away"])}
            for m in ko
        ],
    }
    dst = os.path.join(ROOT, "data", "ko_schedule.json")
    json.dump(out, open(dst, "w"), ensure_ascii=False, indent=1)
    dated = sum(1 for x in out["matches"] if x["home"] and x["away"])
    print(f"{dst}: {len(out['matches'])} jogos ({dated} com ambos os times).")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("uso: build_ko_schedule.py wc_matches.json [AAAA-MM-DD]")
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "?")
