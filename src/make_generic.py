#!/usr/bin/env python3
"""White-label pass: produz dist/copa2026_dashboard_generico.html a partir do dashboard
já construído. O dashboard principal JÁ esconde o método (Odds / Opta / modelo proprietário /
escala probabilística, sem Elo/Sherman Kent/de-vig/params). Este generico é a variante
MAXIMAMENTE anônima — remove até os nomes próprios que o principal mantém de propósito
(Opta, Poisson, supercomputador, casas/veículos nas Fontes). Números, layout e interatividade
preservados 1:1. Rode DEPOIS de build_dashboard.py."""
import os, re
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST=os.path.join(ROOT,"dist")
h=open(f"{DIST}/copa2026_dashboard.html").read()
h=re.sub(r'<!-- Google Tag Manager.*?End Google Tag Manager[^>]*-->','',h,flags=re.S)  # generico sai SEM GTM — Opção B

REP=[
 ('<span><i style="background:#a78bfa"></i>Opta</span>','<span><i style="background:#a78bfa"></i>Modelo externo</span>'),
 ('<div class="rchip"><span>Opta</span><b>35%</b></div>','<div class="rchip"><span>Modelos ext.</span><b>35%</b></div>'),
 ('<b>Opta</b> (supercomputador) a 35%','<b>modelos estatísticos</b> (independentes) a 35%'),
 ("modelo de partida de <b>Poisson</b>","modelo de partida <b>probabilístico</b>"),
 ("em forma analítica (matriz de Poisson)","em forma analítica (matriz probabilística)"),
 ("Odds e Opta não são independentes (o Opta usa odds como insumo)","Odds e modelos externos não são totalmente independentes (usam odds como insumo)"),
 ("O modelo de gols é Poisson independente","O modelo de gols assume ataques independentes"),
 ("'alinhado ao consenso odds+Opta'","'alinhado ao consenso de referência'"),
 ('<div class="n">Opta</div>','<div class="n">Modelo ext.</div>'),
 (" · gols~Poisson",""),
]
for a,b in REP:
    if a not in h: raise SystemExit("token não encontrado (dashboard mudou?): "+a[:70])
    h=h.replace(a,b)
h=re.sub(r'Estrutura/chave:.*?Coletado 9/jun/2026\.',
 'Odds de casas de apostas dos EUA e da Europa (com remoção de margem); modelos estatísticos '
 'independentes; imprensa esportiva de referência internacional. Coletado 9/jun/2026.',h,flags=re.S)

BANNED=['Opta','Sherman','Kent','Elo','Poisson','Monte Carlo','de-vig','FanDuel','BetMGM','eloratings',
        'football-ranking','Athletic','supercomputador','SLOPE','Pinnacle','Betfair','DraftKings','Betano',
        'bet365','Unibet','Betfred','BettingOdds']
left=[(t,h.count(t)) for t in BANNED if h.count(t)]
if left: raise SystemExit("sobraram nomes: "+str(left))
open(f"{DIST}/copa2026_dashboard_generico.html","w").write(h)
print("generico OK:",len(h),"chars; nomes próprios de método/fonte: 0")
