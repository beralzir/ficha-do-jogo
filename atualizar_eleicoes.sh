#!/usr/bin/env bash
# Pipeline da edição Eleições 2026 (etapa B8): motor -> harness -> páginas -> GATES.
# NÃO ingere (rode src/ingest_polls.py antes, local ou no CI) e NÃO publica
# (deploy é parada por padrão, convenção da casa: imprime o comando no fim).
# Falha (exit != 0) se qualquer gate reprovar: no CI isso vira e-mail.
set -euo pipefail
cd "$(dirname "$0")"

echo "== 1/5 motor (agregador + Monte Carlo, invariantes no run) =="
( cd src && python3 eleicoes_model.py )

# ALARME de movimento atípico (C0-c). Segunda camada de defesa: o gate de
# plausibilidade do ingest filtra a ENTRADA, este olha a SAÍDA. Reprova (e o CI
# manda e-mail, sem publicar) quando um candidato se move além do limiar.
# Movimento legítimo grande se libera com ALARME_OK=1. Ver docs/plano-risco-eleicoes.md.
echo "== 2/5 alarme de movimento (saída vs último publicado) =="
python3 src/check_movimento.py

echo "== 3/5 harness (freezes por modelo + leaderboard walk-forward) =="
( cd src && python3 eleicoes_run_models.py && python3 eleicoes_compare.py )

echo "== 4/5 páginas =="
( cd src && python3 build_eleicoes.py )
# públicos (C1c): lê data/publicos/audiencias.json, versionado. O EXTRATOR
# (src/extrai_publicos.py) NÃO roda aqui: depende do PPTX no iCloud.
( cd src && python3 build_publicos.py )

echo "== 5/5 gates =="
( cd src && python3 test_eleicoes_structure.py )
( cd src && python3 test_ingest_polls_gate.py )
# zero-dep: única origem externa tolerada nas páginas live é GTM (+ link CC do rodapé)
bad=$(grep -oh 'https\?://[a-z0-9.-]*' dist/eleicoes_*.html | sort -u \
      | grep -v -e '^https://bera\.ia\.br$' -e '^https://www\.googletagmanager\.com$' \
                -e '^https://creativecommons\.org$' || true)
if [[ -n "$bad" ]]; then
  echo "GATE _ext REPROVADO: origem externa inesperada nas páginas:" ; echo "$bad" ; exit 3
fi
# sintaxe do JS embutido (toggle/track) e do worker. Arquivo temporário de
# propósito: node --check não lê pipe/process-substitution no Linux (CI).
JSTMP=$(mktemp /tmp/eleicoes_embedded.XXXXXX.js)
python3 - > "$JSTMP" <<'PY'
import re
print("\n".join(re.findall(r"<script>(.*?)</script>", open("dist/eleicoes_index.html").read(), re.S)))
PY
node --check "$JSTMP"
rm -f "$JSTMP"
node --check worker.js
echo "GATES VERDES."
echo
echo "Para publicar (parada por padrão): /Users/beralzir/.npm-global/bin/wrangler deploy"
