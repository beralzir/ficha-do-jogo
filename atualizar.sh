#!/usr/bin/env bash
# atualizar.sh — ação local única de atualização (Fase 4 do PLANO_EXECUCAO).
# Fluxo: state.json (editado à mão) -> re-simulação condicional -> modelos do harness -> rebuild das 6 páginas -> verificação.
# Por padrão PARA antes de publicar (deploy = parada). Use --deploy para publicar de fato.
#
#   ./atualizar.sh                 # re-simula, roda modelos, rebuilda, verifica e imprime o comando de deploy
#   ./atualizar.sh --deploy        # idem + wrangler deploy + checa 200 (publica no ar)
#   SKIP_MODELS=1 ./atualizar.sh   # pula o harness multi-modelo (~90s); reusa model_scores.json/data/models já gravados
#
# Pré-requisito: editar data/live/state.json com os jogos ocorridos (resultados). Sem dado pessoal.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
DEPLOY=0; [ "${1:-}" = "--deploy" ] && DEPLOY=1
WRANGLER="$HOME/.npm-global/bin/wrangler"
BASE="https://bera.ia.br/ficha-do-jogo"

echo "▸ 1/5 Re-simulação condicional (motor Monte Carlo)…"
python3 src/wc2026_model.py | tail -n 12

FINAL_SCORES=$(python3 -c "import json;print(1 if json.load(open('data/model_scores.json')).get('measurement_complete') else 0)" 2>/dev/null || echo 0)
if [ "$FINAL_SCORES" = "1" ]; then
  echo "▸ 2/5 Modelos do harness — PULADO (medição FINAL fechada por finalize_scores.py; compare.py não sobrescreve)."
elif [ "${SKIP_MODELS:-0}" != "1" ]; then
  echo "▸ 2/5 Modelos do harness (forecasts por modelo + leaderboard de calibração)…"
  python3 src/run_models.py | tail -n 12
  python3 src/compare.py | sed -n '/LEADERBOARD/,/vs_mkt =/p'
else
  echo "▸ 2/5 Modelos do harness — PULADO (SKIP_MODELS=1; reusa model_scores.json/data/models)."
fi

echo "▸ 3/5 Rebuild das páginas…"
for b in dashboard bolao resultados modelos index; do python3 "src/build_$b.py" >/dev/null; done
python3 src/make_generic.py >/dev/null
echo "  páginas geradas em dist/."

echo "▸ 4/5 Verificação (invariantes · zero-dep · baseline intacta)…"
python3 - <<'PY'
import json, glob, re, sys
d=json.load(open('data/wc2026_results.json'))['teams']
s=lambda k:round(sum(d[t][k] for t in d),2)
sums={k:s(k) for k in ['champion','final','sf','qf','r16','advance','group_win']}
exp={'champion':1.0,'final':2.0,'sf':4.0,'qf':8.0,'r16':16.0,'advance':32.0,'group_win':12.0}
viol=sum(1 for t in d if any(d[t][a]+1e-9<d[t][b] for a,b in
  [('advance','r16'),('r16','qf'),('qf','sf'),('sf','final'),('final','champion')]))
bad=[k for k in exp if abs(sums[k]-exp[k])>0.02]
def _ext(s):  # recursos CARREGADOS = dep. externa; CC (hyperlink) e GTM (googletagmanager) das páginas live são permitidos
    if re.search(r'cdnjs|<script src|@import|url\(\s*https?:', s): return True
    ALLOW=('creativecommons.org/licenses/','googletagmanager.com','bera.ia.br','github.com/beralzir/ficha-do-jogo')  # GTM = única dep CARREGADA; bera.ia.br = same-origin; CC e GitHub = hyperlinks (não carregam nada)
    return any(not any(a in u for a in ALLOW) for u in re.findall(r'https?://\S+', s))
dep=[f.split('dist/')[-1] for f in glob.glob('dist/*.html')+glob.glob('dist/copa2026/*.html') if _ext(open(f).read())]
ok = not bad and viol==0 and not dep
print(f"  somas {'OK' if not bad else 'FALHA '+str(bad)} · monotonicidade {viol} viol · dep externas {dep or 'nenhuma'}")
if not ok: sys.exit("VERIFICAÇÃO FALHOU — não publicar.")
PY

echo "▸ 5/5 Pronto."
if [ "$DEPLOY" -eq 1 ]; then
  echo "  publicando (wrangler deploy)…"
  "$WRANGLER" deploy | tail -n 4
  echo "  checando 200…"
  for p in "" dashboard resultados placares modelos; do
    code=$(curl -s -o /dev/null -w "%{http_code}" -L "$BASE/$p")
    printf "    %-34s %s\n" "/${p:-index}" "$code"
  done
  echo "✓ Publicado: $BASE/"
else
  echo "  NÃO publicado (deploy é parada). Revise dist/ e rode:  ./atualizar.sh --deploy"
fi
