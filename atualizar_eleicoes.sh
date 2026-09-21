#!/usr/bin/env bash
# Pipeline da edição Eleições 2026: volume -> motor -> movimento -> harness -> páginas -> GATES.
# NÃO ingere (rode src/ingest_polls.py antes, local ou no CI) e NÃO publica
# (deploy é parada por padrão, convenção da casa: imprime o comando no fim).
# Falha (exit != 0) se qualquer gate reprovar: no CI isso vira e-mail.
set -euo pipefail
cd "$(dirname "$0")"

# ALARME DE VOLUME (D2). Roda ANTES do motor de propósito: se uma corrida perdeu
# o histórico, não faz sentido gastar Monte Carlo nem publicar em cima do que
# sobrou. É a camada que faltava quando a presidencial perdeu 89% das estimuladas
# em 04/09/2026 e o pipeline seguiu verde por 14 dias, porque as outras duas
# camadas olham o VALOR do dado e nenhuma percebe dado que simplesmente some.
echo "== 1/6 alarme de volume (pesquisas por corrida vs último publicado) =="
python3 src/check_volume.py

echo "== 2/6 motor (agregador + Monte Carlo, invariantes no run) =="
( cd src && python3 eleicoes_model.py )

# ALARME de movimento atípico (C0-c). Segunda camada de defesa: o gate de
# plausibilidade do ingest filtra a ENTRADA, este olha a SAÍDA. Reprova (e o CI
# manda e-mail, sem publicar) quando um candidato se move além do limiar.
# Movimento legítimo grande se libera com ALARME_OK=1. Ver docs/plano-risco-eleicoes.md.
echo "== 3/6 alarme de movimento (saída vs último publicado) =="
python3 src/check_movimento.py

echo "== 4/6 harness (freezes por modelo + leaderboard walk-forward) =="
( cd src && python3 eleicoes_run_models.py && python3 eleicoes_compare.py )
# datação de movimento (M2): resíduo padronizado do filtro do competidor v2.
# Não roda Monte Carlo e não toca o forecast oficial: é diagnóstico, e alimenta
# a página de Inflexões e o estudo de evento do M3.
( cd src && python3 eleicoes_inflexoes.py )

echo "== 5/6 páginas =="
( cd src && python3 build_eleicoes.py )
# públicos (C1c): lê data/publicos/audiencias.json, versionado. O EXTRATOR
# (src/extrai_publicos.py) NÃO roda aqui: depende do PPTX no iCloud.
( cd src && python3 build_publicos.py )

echo "== 6/6 gates =="
( cd src && python3 test_eleicoes_structure.py )
( cd src && python3 test_ingest_polls_gate.py )
# anti-vazamento do sintético: prova que o modelo OFICIAL não lê pesquisa
# sintética, com erro plantado. Sem isso, a separação seria só disciplina.
( cd src && python3 test_synths_gate.py )
# alarme de volume: prova com ERRO PLANTADO PELA REALIDADE, reproduzindo a rodada
# de 04/09/2026 direto do histórico do git. Alarme que não pega o incidente que o
# motivou não serve, e isso tem de ser verificável a cada run, não uma vez.
( cd src && python3 test_volume_gate.py )
# piso de share no alarme de movimento (M7): prova, com os falsos positivos REAIS
# dos freezes versionados, que o piso cala corrida empatada e não cala nenhum
# disparo do gatilho de share. Reprova se o piso sair da faixa calibrada.
( cd src && python3 test_movimento_gate.py )
# competidor v2_estado (M1): invariantes, determinismo, zero-dep e, sobretudo, o
# as_of derivado de POLL_SOURCE. O erro plantado é o BUG que o pacote de
# modelagem trazia, executado lado a lado para provar que o teste morde.
( cd src && python3 test_v2_estado.py )
# detector de inflexão (M2): a corroboração é provada a quebrar nas três formas
# de vazar (mesmo instituto, sinal oposto, fora da janela), e o exemplar real do
# plano (o salto de Cury em 27/08) tem de continuar sendo encontrado.
( cd src && python3 test_inflexoes.py )
# calibração do erro sistemático (M4): NÃO refaz o fetch (o extrato de 2018 e 2022
# é congelado de propósito, com revid, para a calibração ser auditável). Confere o
# apurado contra fato público, prova que contabilidade não virou candidato, e trava
# o ERRO_ELEICAO do model_configs no número que a calibração produziu.
( cd src && python3 test_calibracao_erro.py )
# gate cruzado das fichas de público: confere o audiencias.json versionado contra o
# deck da fonte, número a número. Entrou no CI em 21/09/2026: antes era impossível,
# porque a fonte morava no iCloud e o runner não acessa. Enquanto esteve de fora,
# ninguém percebeu que os arquivos tinham mudado de pasta.
( cd src && python3 test_publicos.py )
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
