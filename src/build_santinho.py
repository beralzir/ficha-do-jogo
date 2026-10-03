#!/usr/bin/env python3
"""
Gera dist/santinho.html: "Meu Santinho", página pessoal e isolada (sem link no hub).

Dados (scripts/build_santinho_data.py, fonte TSE):
- data/eleicoes/santinho/base.json  -> embutido no HTML (presidente, governador, senador)
- data/eleicoes/santinho/dep/<UF>.json -> copiado para dist/santinho/dep/ e lido sob demanda
- dist/santinho/fotos/*.json (scripts/build_santinho_fotos.py) -> fotos oficiais, sob demanda

Navegação: o CARGO é a aba principal (fora dos filtros); a UF é escolhida uma vez no topo;
filtros só refinam a lista do cargo aberto. Estático-primeiro: a aba Presidente sai
pré-renderizada em HTML; o JS só adiciona busca, filtros, escolha e colinha.
Zero dependência externa: o único endereço externo é o link (hiperlink) para a ficha
oficial no TSE (divulgacandcontas.tse.jus.br), já liberado no gate `_ext`.
"""
import hashlib
import html
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shell
import theme

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "eleicoes", "santinho")
DIST = os.path.join(ROOT, "dist")
OUT_HTML = os.path.join(DIST, "santinho.html")
OUT_DEP = os.path.join(DIST, "santinho", "dep")

ELEICAO_DATA = "domingo, 4 de outubro de 2026"

UF_NOMES = {
    "AC": "Acre", "AL": "Alagoas", "AM": "Amazonas", "AP": "Amapá", "BA": "Bahia", "CE": "Ceará",
    "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão",
    "MG": "Minas Gerais", "MS": "Mato Grosso do Sul", "MT": "Mato Grosso", "PA": "Pará",
    "PB": "Paraíba", "PE": "Pernambuco", "PI": "Piauí", "PR": "Paraná", "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte", "RO": "Rondônia", "RR": "Roraima", "RS": "Rio Grande do Sul",
    "SC": "Santa Catarina", "SE": "Sergipe", "SP": "São Paulo", "TO": "Tocantins",
}

DISCLAIMER = (
    "<p><b>Aviso.</b> Esta página é uma ferramenta pessoal, feita pelo autor com o propósito "
    "único de organizar a própria decisão de voto. Não é propaganda eleitoral nem pesquisa "
    "eleitoral, e não pede, recomenda ou desaconselha o voto em nenhuma candidatura.</p>"
    "<p>Nome, número, partido, gênero, ocupação, situação na urna e foto vêm dos dados abertos do "
    "Tribunal Superior Eleitoral. Resumos, espectro e posicionamentos marcados como <i>detalhes "
    "públicos</i> foram compilados de declarações públicas e da cobertura da imprensa, sem "
    "verificação item a item e sem fonte vinculada a cada informação, e podem conter erros ou estar "
    "desatualizados. O espectro dos partidos segue a classificação usual, também sujeita a "
    "interpretação. A escolha de quais pautas e filtros aparecem reflete apenas os critérios "
    "pessoais do autor para decidir o próprio voto, e por isso pode parecer enviesada. A chance de "
    "ser eleito e os votos estimados vêm do modelo estatístico do Ficha do Jogo, calculado a partir "
    "de pesquisas publicadas, e são estimativas, não resultado.</p>"
    "<p>A referência oficial é sempre a ficha de cada candidatura no TSE, indicada em cada "
    "candidato. Quem usar esta página faz isso por conta e responsabilidade próprias: confira as "
    "informações nas fontes oficiais e decida o seu voto de forma independente. O autor não assume "
    "responsabilidade por decisões de voto de terceiros tomadas com base neste conteúdo. O voto é "
    "livre e secreto.</p>"
)

CSS = r"""
:root{--maxw:1120px;--mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;--r:12px}
/* cão-guia 03/10/2026: --mut do tema claro (#6f7259) dá 4,43:1 no fundo creme; ajuste SÓ nesta
   página (decisão do Bera). A correção no theme.py é pendência do site inteiro. */
:root[data-theme=light]{--mut:#63664e}
*{box-sizing:border-box}
html{scroll-padding-top:150px;scroll-padding-bottom:110px}
body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;line-height:1.5;-webkit-font-smoothing:antialiased}
button,input,select{font:inherit;color:inherit}
:focus-visible{outline:2px solid var(--ac);outline-offset:2px}
.skip{position:absolute;left:-999px}.skip:focus{left:8px;top:8px;z-index:99;background:var(--card);padding:8px 12px;border-radius:8px}
.wrap{max-width:var(--maxw);margin:0 auto;padding:0 16px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}

/* Cabeçalho */
.hero{padding-top:22px;padding-bottom:14px;display:flex;flex-wrap:wrap;gap:14px 24px;align-items:flex-end;justify-content:space-between}
.hero h1{margin:0;font-size:clamp(24px,4vw,32px);letter-spacing:-.02em;line-height:1.15}
.hero p{margin:6px 0 0;color:var(--mut);font-size:14px;max-width:560px}
.ufbox{display:flex;flex-direction:column;gap:4px;min-width:220px}
.ufbox label{font-size:11px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--mut)}
.ufsel{position:relative}
.ufsel::after{content:"";position:absolute;right:16px;top:50%;width:8px;height:8px;border-right:2px solid var(--mut);border-bottom:2px solid var(--mut);transform:translateY(-70%) rotate(45deg);pointer-events:none}
.ufbox select{appearance:none;-webkit-appearance:none;width:100%;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:11px 40px 11px 12px;font-size:16px;font-weight:700;min-height:46px;cursor:pointer}

/* Abas de cargo */
.cargos{position:sticky;top:51px;z-index:30;background:var(--bg);border-bottom:1px solid var(--line)}
.cargos .wrap{display:flex;gap:6px;overflow-x:auto;scrollbar-width:none;padding-top:8px;padding-bottom:8px}
.cargos .wrap::-webkit-scrollbar{display:none}
.tab{flex:none;display:flex;align-items:center;gap:8px;padding:9px 14px;border-radius:999px;border:1px solid var(--line);background:var(--card);font-size:14px;font-weight:700;color:var(--mut);cursor:pointer;min-height:42px;white-space:nowrap}
.tab:hover{color:var(--ink);border-color:var(--mut)}
.tab[aria-selected=true]{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.tab .st{width:18px;height:18px;border-radius:50%;border:1.5px solid currentColor;display:inline-flex;align-items:center;justify-content:center;font-size:11px;line-height:1;opacity:.55}
.tab.ok .st{background:var(--ac);border-color:var(--ac);color:var(--badge-ink);opacity:1}
.tab.parcial .st{border-color:var(--ac);color:var(--ac);opacity:1}
@media(max-width:640px){
  .cargos .wrap{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:4px;overflow:visible;padding-left:8px;padding-right:8px}
  .tab{flex-direction:column;gap:3px;padding:6px 1px;border-radius:10px;font-size:11px;letter-spacing:-.01em;line-height:1.15;white-space:normal;text-align:center;min-height:54px;min-width:0;justify-content:center}
  .tab .lb{overflow-wrap:anywhere}
  .tab .st{width:16px;height:16px;font-size:10px}
}

/* Cabeçalho do cargo */
.cargo-head{margin:18px 0 12px;display:grid;grid-template-columns:minmax(0,1fr);gap:12px}
.cargo-head>*{min-width:0}
@media(min-width:820px){.cargo-head{grid-template-columns:1fr minmax(300px,420px);align-items:start}}
.cargo-head h2{margin:0;font-size:22px;letter-spacing:-.01em}
.cargo-head .regra{margin:4px 0 0;color:var(--mut);font-size:14px}
.regra b{color:var(--ink)}
.escolha{background:var(--card);border:1px dashed var(--line);border-radius:var(--r);padding:10px 12px;display:flex;flex-direction:column;gap:8px}
.escolha .tt{font-size:11px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--mut)}
.escolha .vazio{font-size:14px;color:var(--mut)}
.pick{display:flex;align-items:center;gap:10px}
.pick .nm{flex:1;min-width:0;font-weight:700;font-size:14px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.pick .nm small{display:block;font-weight:500;color:var(--mut);font-size:12px}
.pick .num{font-family:var(--mono);font-weight:800;font-size:18px;letter-spacing:.06em}
.pick button{border:0;background:none;color:var(--mut);cursor:pointer;font-size:18px;width:32px;height:32px;border-radius:8px}
.pick button:hover{background:var(--rowhov);color:var(--ink)}
.escolha.cheia{border-style:solid;border-color:var(--ac)}

/* Barra de busca e filtros */
.tools{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:8px}
.busca{flex:1 1 260px;position:relative}
.busca input{width:100%;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:11px 12px 11px 38px;font-size:16px;min-height:46px}
.busca svg{position:absolute;left:12px;top:50%;transform:translateY(-50%);color:var(--mut)}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;border:1px solid var(--line);background:var(--card);border-radius:10px;padding:10px 14px;font-weight:700;font-size:14px;cursor:pointer;min-height:46px;color:var(--ink);text-decoration:none}
.btn:hover{border-color:var(--mut)}
.btn .n{background:var(--ac);color:var(--badge-ink);border-radius:999px;font-size:11px;padding:1px 7px;font-weight:800}
.btn.pri{background:var(--ac);border-color:var(--ac);color:var(--badge-ink)}
.ordem{max-width:100%;min-width:0;text-overflow:ellipsis;min-height:46px;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:0 10px;font-size:14px;font-weight:600}
.ativos{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 8px}
.ativos:empty{display:none}
.chip-x{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--ac);background:var(--acsoft);color:var(--ink);border-radius:999px;padding:5px 10px;font-size:13px;font-weight:600;cursor:pointer;min-height:34px}
.chip-x::after{content:"\00d7";font-size:16px;line-height:1;color:var(--mut)}
.chip-x.limpar{border-color:var(--line);background:none;color:var(--mut)}
.chip-x.limpar::after{content:""}
.contagem{font-size:13px;color:var(--mut);margin:0 0 10px}

/* Lista */
.lista{display:grid;grid-template-columns:1fr;gap:10px;align-items:start}
@media(min-width:720px){.lista{grid-template-columns:1fr 1fr}}
@media(min-width:1060px){.lista{grid-template-columns:1fr 1fr 1fr}}
.lista>*{min-width:0}
.card{min-width:0;background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:12px;display:flex;flex-direction:column;gap:10px;transition:border-color .15s,box-shadow .15s}
.card.sel{border-color:var(--ac);box-shadow:inset 0 0 0 1px var(--ac)}
.top{display:flex;gap:12px;align-items:center}
.av{width:56px;height:56px;border-radius:50%;flex:none;background:var(--box);border:1px solid var(--line);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:17px;color:var(--mut);overflow:hidden;position:relative}
.av img{width:100%;height:100%;object-fit:cover;object-position:50% 20%;position:absolute;inset:0;opacity:0;transition:opacity .25s}
.av img.ok{opacity:1}
.id{flex:1;min-width:0}
.id h3{margin:0;font-size:16px;line-height:1.25;letter-spacing:-.005em}
.id .sub{font-size:13px;color:var(--mut);margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.numero{font-family:var(--mono);font-weight:800;font-size:22px;letter-spacing:.06em;line-height:1;padding:8px 10px;border-radius:8px;background:var(--box);flex:none}
.tags{display:flex;flex-wrap:wrap;gap:6px}
.tag{font-size:11.5px;font-weight:700;padding:3px 8px;border-radius:6px;background:var(--box);color:var(--mut);border:1px solid var(--line2)}
.tag.pub{color:var(--ac);border-color:var(--ac);background:var(--acsoft)}
.acoes{display:flex;gap:8px}
.acoes .btn{flex:1;min-height:42px;font-size:14px}
.btn.escolher[aria-pressed=true]{background:var(--ac);border-color:var(--ac);color:var(--badge-ink)}
.btn[disabled]{opacity:.45;cursor:not-allowed}
.idn{font-size:12.5px;color:var(--mut);line-height:1.35;margin-top:-4px}
.resumo{margin:0;font-size:13.5px;line-height:1.45}
.posbox{border:1px solid var(--line2);background:var(--card2);border-radius:10px;padding:8px 10px}
.pb-h{display:flex;justify-content:space-between;align-items:baseline;gap:8px;font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--mut);margin-bottom:6px}
.lnk{border:0;background:none;color:var(--ac);font-size:12px;font-weight:700;letter-spacing:0;text-transform:none;cursor:pointer;padding:4px 0}
.pl{display:grid;grid-template-columns:auto 1fr;gap:3px 10px;font-size:13px;line-height:1.4;margin:0}
.pl dt{font-weight:800;color:var(--mut);white-space:nowrap}
.pl dt b{color:var(--ink);font-weight:800;margin-right:4px}
.pl dd{margin:0;font-weight:600}
.chance{display:flex;flex-direction:column;gap:5px}
.ch-top{display:flex;justify-content:space-between;align-items:baseline;font-size:12.5px;color:var(--mut);font-weight:600}
.ch-top b{font-size:20px;color:var(--ink);font-variant-numeric:tabular-nums;letter-spacing:-.01em}
.ch-sub{font-size:11.5px;color:var(--mut);font-variant-numeric:tabular-nums}
.ch-sub .mg{color:var(--draw);font-weight:700}
.exbar{position:relative;height:12px;background:var(--box);border-radius:5px;overflow:hidden}
.exbar i{position:absolute;left:0;top:0;bottom:0;border-radius:5px}
.b-win{background:var(--win)}
.exband{background:repeating-linear-gradient(-55deg,transparent 0 3px,var(--draw) 3px 5px);opacity:.75;border-radius:0!important}
.oficial.mini{font-size:12.5px;min-height:28px;padding:4px 0;color:var(--mut);font-weight:600;text-decoration-color:var(--line)}
.oficial.mini:hover{color:var(--ac)}
.fr{color:var(--mut);font-weight:500}
.fonte-det{font-size:12px;color:var(--mut);margin:8px 0 0}
.det{border-top:1px solid var(--line2);padding-top:10px;font-size:13.5px;display:none}
.card.aberto .det{display:block}
.det dl{display:grid;grid-template-columns:auto 1fr;gap:4px 12px;margin:0 0 10px}
.det dt{color:var(--mut)}
.det dd{margin:0;font-weight:600}
.det .bloco{border:1px solid var(--line2);border-radius:10px;padding:10px;margin:0 0 10px;background:var(--card2)}
.det .bloco h4{margin:0 0 6px;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--ac)}
.det .bloco p{margin:0 0 6px}
.pautas{display:grid;grid-template-columns:1fr;gap:4px}
@media(min-width:420px){.pautas{grid-template-columns:1fr 1fr}}
.pauta{display:flex;justify-content:space-between;gap:8px;font-size:12.5px;padding:3px 0;border-bottom:1px dotted var(--line2)}
.pos{font-weight:700;font-size:12px;white-space:nowrap;color:var(--ink)}
.pos.neutro{color:var(--mut);font-weight:500}
.pp{padding:0 4px;border-radius:4px;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.pos.v,.pos.r{padding:0 6px;border-radius:4px}
.pp.v,.pos.v{background:color-mix(in srgb,var(--win) 20%,transparent)}
.pp.r,.pos.r{background:color-mix(in srgb,var(--loss) 20%,transparent)}
@media(forced-colors:active){.pp.v,.pos.v,.pp.r,.pos.r{forced-color-adjust:none}}
.alerta{font-size:12.5px;line-height:1.4;padding:7px 9px;border-radius:8px;border:1px solid}
.alerta.nulo{color:var(--ink);background:color-mix(in srgb,var(--loss) 16%,transparent);border-color:var(--loss)}
.alerta.nulo::before{content:"⚠ ";color:var(--loss);font-weight:800}
.alerta.sub_judice{color:var(--ink);background:color-mix(in srgb,var(--draw) 14%,transparent);border-color:var(--draw)}
.alerta.sub_judice::before{content:"⚠ ";color:var(--draw);font-weight:800}
.alerta.info{color:var(--ink);background:var(--box);border-color:var(--line)}
.linha .av-w{font-size:11.5px;font-weight:700;margin-top:2px}
.linha .av-w{color:var(--ink)}
.oficial{display:flex;align-items:center;gap:6px;font-weight:700}
.nada{color:var(--mut);font-style:italic}
.mais{display:flex;justify-content:center;margin:16px 0}
.sem-uf .tools,.sem-uf .ativos,.sem-uf .contagem{display:none}
.pede-uf{grid-column:1/-1;background:var(--card);border:2px solid var(--ac);border-radius:var(--r);padding:18px 16px;display:flex;flex-direction:column;gap:8px;max-width:520px}
.pede-uf label{font-size:18px;font-weight:800;color:var(--ink)}
.pede-uf p{margin:0;color:var(--mut);font-size:14px}
.pede-uf select{appearance:none;-webkit-appearance:none;width:100%;background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:12px 40px 12px 12px;font-size:16px;font-weight:700;min-height:48px;cursor:pointer}
.vazia{background:var(--card);border:1px dashed var(--line);border-radius:var(--r);padding:24px;text-align:center;color:var(--mut)}
.carregando{padding:30px;text-align:center;color:var(--mut)}

/* Gaveta de filtros */
.veu{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:60;opacity:0;pointer-events:none;transition:opacity .2s}
.veu.on{opacity:1;pointer-events:auto}
.gaveta{position:fixed;z-index:61;background:var(--bg);border:1px solid var(--line);display:flex;flex-direction:column;transition:transform .25s ease;
  left:0;right:0;bottom:0;max-height:88vh;border-radius:16px 16px 0 0;transform:translateY(105%);visibility:hidden;transition:transform .25s ease,visibility 0s .25s}
.gaveta.on{transform:none;visibility:visible;transition:transform .25s ease}
@media(min-width:820px){.gaveta{left:auto;top:0;bottom:0;width:420px;max-height:none;border-radius:0;transform:translateX(105%)}}
.gaveta .g-head{display:flex;align-items:center;justify-content:space-between;padding:14px 16px;border-bottom:1px solid var(--line)}
.gaveta .g-head h2{margin:0;font-size:18px}
.gaveta .corpo{overflow-y:auto;padding:6px 16px 16px;overscroll-behavior:contain}
.gaveta .g-foot{display:flex;gap:8px;padding:12px 16px calc(12px + env(safe-area-inset-bottom,0px));border-top:1px solid var(--line)}
.gaveta .g-foot .btn{flex:1}
.grupo{padding:14px 0;border-bottom:1px solid var(--line2)}
.grupo h3{margin:0 0 8px;font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--mut)}
.grupo .nota{font-size:12.5px;color:var(--mut);margin:-2px 0 8px}
.op{display:flex;flex-wrap:wrap;gap:6px}
.op button{border:1px solid var(--line);background:var(--card);border-radius:999px;padding:7px 12px;font-size:13.5px;font-weight:600;cursor:pointer;min-height:38px}
.op button[aria-pressed=true]{background:var(--ac);border-color:var(--ac);color:var(--badge-ink)}
.gaveta select{width:100%;min-height:44px;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:0 10px;font-size:15px}
.pf{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:6px 8px;padding:6px 0}
.pf .seg{max-width:100%}
.pf span{font-size:13.5px;font-weight:600}
.seg{display:inline-flex;border:1px solid var(--line);border-radius:8px;overflow:hidden;flex:none}
.seg button{border:0;background:var(--card);padding:6px 9px;font-size:12px;font-weight:700;cursor:pointer;min-height:34px;color:var(--mut)}
.seg button+button{border-left:1px solid var(--line)}
.seg button[aria-pressed=true]{background:var(--ink);color:var(--bg)}

/* Barra inferior */
main{padding-bottom:calc(110px + env(safe-area-inset-bottom,0px))}
.dock{position:fixed;left:0;right:0;bottom:0;z-index:50;background:var(--card);border-top:1px solid var(--line);box-shadow:0 -8px 24px var(--dshadow);padding:10px 0 calc(10px + env(safe-area-inset-bottom,0px))}
.dock .wrap{display:flex;align-items:center;gap:12px}
.prog{flex:1;min-width:0}
.prog .lb{font-size:13px;font-weight:700}
.prog .lb span{color:var(--mut);font-weight:600}
.trilha{display:flex;gap:4px;margin-top:6px}
.trilha i{flex:1;height:6px;border-radius:3px;background:var(--box)}
.trilha i.ok{background:var(--ac)}

/* Colinha */
.modal{position:fixed;inset:0;z-index:70;display:none;align-items:center;justify-content:center;padding:16px;background:rgba(0,0,0,.55)}
.modal.on{display:flex}
.folha{background:var(--card);border:1px solid var(--line);border-radius:16px;width:100%;max-width:440px;max-height:92vh;overflow:auto;padding:18px}
.folha h2{margin:0;font-size:20px}
.folha .sub{color:var(--mut);font-size:13px;margin:2px 0 14px}
.linha{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:10px 0;border-bottom:1px dashed var(--line)}
.linha .c{font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--mut)}
.linha .q{font-weight:700;font-size:14px}
.digitos{flex:none}
.digitos .dg{display:flex;gap:3px}
.digitos b{width:26px;height:34px;border:1.5px solid var(--ink);border-radius:5px;display:flex;align-items:center;justify-content:center;font-family:var(--mono);font-size:18px}
.linha.vaz .q{color:var(--mut);font-weight:500;font-style:italic}
.linha.vaz .digitos b{border-color:var(--line)}
.folha .acoes{margin-top:14px;flex-wrap:wrap}
.folha .acoes .btn{flex:1 1 120px}
.cores{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:0 0 6px;font-size:12px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--mut)}
.folha.pb{background:#fff;color:#000;border-color:#000}
.folha.pb .sub,.folha.pb .c,.folha.pb .lembrete,.folha.pb .cores{color:#333}
.folha.pb .linha{border-color:#999}
.folha.pb .digitos b{border-color:#000;color:#000}
.folha.pb .linha.vaz .digitos b{border-color:#bbb}
.folha.pb .linha.vaz .q{color:#555}
.folha.pb .av-w{color:#000!important}
.folha.pb .btn{background:#fff;color:#000;border-color:#000}
.folha.pb .btn.pri{background:#000;color:#fff}
.folha.pb .seg button{background:#fff;color:#000}
.folha.pb .seg button[aria-pressed=true]{background:#000;color:#fff}
.folha .lembrete{font-size:12px;color:var(--mut);margin-top:12px}

/* Rodapé */
.rodape{margin-top:40px;border-top:1px solid var(--line2);padding:18px 0 8px;color:var(--mut);font-size:12px;line-height:1.55}
.rodape p{margin:0 0 8px;max-width:820px}


@media(forced-colors:active){
  .tab[aria-selected=true],.btn.escolher[aria-pressed=true],.op button[aria-pressed=true],.seg button[aria-pressed=true]{outline:3px solid CanvasText;outline-offset:-3px}
  .card.sel{outline:3px solid Highlight}
  .exband{forced-color-adjust:none}
}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
@media print{
  @page{margin:12mm}
  body{background:#fff!important}
  body *{visibility:hidden}
  #colinha,#colinha *{visibility:visible}
  #colinha{position:absolute;inset:0;display:block;background:#fff;padding:0}
  #colinha .folha{border:1.5px solid #1a7a43;max-width:9.5cm;box-shadow:none;background:#fffef9;color:#23271b;-webkit-print-color-adjust:exact;print-color-adjust:exact}
  #colinha .folha .c,#colinha .folha .sub{color:#1a7a43}
  #colinha .folha .q,#colinha .folha .lembrete,#colinha .folha .linha.vaz .q{color:#23271b}
  #colinha .folha .linha{border-color:#6f7259}
  #colinha .folha .digitos b{border-color:#1a7a43;color:#23271b}
  #colinha .folha .av-w.nulo{color:#b91c1c}#colinha .folha .av-w.sub_judice{color:#b45309}
  #colinha .folha.pb{border-color:#000;background:#fff;color:#000}
  #colinha .folha.pb .c,#colinha .folha.pb .sub,#colinha .folha.pb .av-w{color:#000!important}
  #colinha .folha.pb .digitos b{border-color:#000;color:#000}
  #colinha .acoes,#colinha .fechar,#colinha .cores{display:none}
}
"""

JS = r"""
(function(){
"use strict";
var BASE = JSON.parse(document.getElementById("dados").textContent);
var META = BASE.meta, VER = META.ver;
var CARGOS = META.cargos, PAUTAS = META.pautas;
var CARGO_BY = {}; CARGOS.forEach(function(c){ CARGO_BY[c.id] = c; });
var ESP_LBL = {"esquerda":"Esquerda","centro-esquerda":"Centro-esquerda","centro":"Centro","centro-direita":"Centro-direita","direita":"Direita"};
var ESP_ORD = {"esquerda":0,"centro-esquerda":1,"centro":2,"centro-direita":3,"direita":4};
var GRUPO = {presidente:"maj",governador:"maj",senador:"maj",deputado_federal:"fed",deputado_estadual:"est"};
var URNA_ORDEM = [["deputado_federal",0],["deputado_estadual",0],["senador",0],["senador",1],["governador",0],["presidente",0]];
var PASSO = 30;

function $(id){ return document.getElementById(id); }
function esc(s){ return String(s == null ? "" : s).replace(/[&<>"']/g, function(c){ return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]; }); }
function norm(s){ return String(s||"").normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase(); }
function ini(n){ var p = String(n).replace(/[^A-Za-zÀ-ÿ ]/g," ").trim().split(/\s+/); return ((p[0]||"")[0]||"").toUpperCase() + (p.length>1 ? (p[p.length-1][0]||"").toUpperCase() : ""); }
function ls(k, v){ try{ if (v === undefined) return JSON.parse(localStorage.getItem(k)); localStorage.setItem(k, JSON.stringify(v)); }catch(e){ return null; } }

// índice de foto: posição no grupo (mesma conta de scripts/build_santinho_fotos.py)
function indexar(lista){ var cont = {}; lista.forEach(function(c){ var g = c.uf + "-" + GRUPO[c.cargo], i = cont[g] || 0; cont[g] = i + 1; c._f = g + "-" + Math.floor(i / 200); }); }
indexar(BASE.candidatos);

var st = {
  uf: ls("fdj_sant_uf") || "",
  cargo: "presidente",
  q: "", limite: PASSO, ordem: "esp",
  f: { genero: "", esp: [], partido: "", det: false, pautas: {} },
  picks: ls("fdj_sant_picks") || {}
};
if (META.ufs.indexOf(st.uf) < 0) st.uf = "";
var DEP = {}, FOTOS = {}, aberto = {};

function picksUF(){ var k = st.uf || "_"; if (!st.picks[k]) st.picks[k] = {}; return st.picks[k]; }
function getPick(cargo){ var p = cargo === "presidente" ? (st.picks.BR = st.picks.BR || {}) : picksUF(); return p[cargo] || []; }
function setPick(cargo, arr){ var p = cargo === "presidente" ? (st.picks.BR = st.picks.BR || {}) : picksUF(); p[cargo] = arr; ls("fdj_sant_picks", st.picks); }
function vagas(cargo){ return CARGO_BY[cargo].vagas || 1; }
function cargoLabel(id, curto){ var c = CARGO_BY[id]; if (st.uf === "DF" && c.label_df) return curto ? c.curto_df : c.label_df; return curto ? c.curto : c.label; }

// ---------- dados por cargo ----------
function listaDoCargo(cb){
  var c = st.cargo;
  if (c === "presidente") return cb(BASE.candidatos.filter(function(x){ return x.cargo === c; }));
  if (!st.uf) return cb(null);
  if (c === "governador" || c === "senador") return cb(BASE.candidatos.filter(function(x){ return x.cargo === c && x.uf === st.uf; }));
  if (DEP[st.uf]) return cb(DEP[st.uf].filter(function(x){ return x.cargo === c; }));
  $("lista").innerHTML = '<div class="carregando" role="status">Carregando candidaturas de ' + esc(st.uf) + '…</div>';
  fetch("santinho/dep/" + st.uf + ".json?v=" + VER).then(function(r){ if (!r.ok) throw 0; return r.json(); }).then(function(d){
    indexar(d); DEP[st.uf] = d; render();
  }).catch(function(){ $("lista").innerHTML = '<div class="vazia">Não foi possível carregar a lista de deputados agora. Tente de novo em instantes.</div>'; });
}

function espDe(x){ return (x.detalhes && x.detalhes.espectro) || x.esp_partido || ""; }
function passa(x){
  var f = st.f;
  if (f.genero && x.genero !== f.genero) return false;
  if (f.esp.length && f.esp.indexOf(espDe(x)) < 0) return false;
  if (f.partido && x.partido !== f.partido) return false;
  if (f.det && !x.detalhes) return false;
  for (var p in f.pautas){ if (!x.detalhes || !x.detalhes.pautas || x.detalhes.pautas[p] !== f.pautas[p]) return false; }
  if (st.q){
    var q = norm(st.q);
    if (/^\d+$/.test(q)) return String(x.num).indexOf(q) === 0;
    if ((norm(x.urna) + " " + norm(x.nome) + " " + norm(x.nome_social) + " " + norm(x.partido)).indexOf(q) < 0) return false;
  }
  return true;
}
function ordenar(l){
  var o = st.ordem;
  return l.slice().sort(function(a,b){
    if (o === "nome") return a.urna.localeCompare(b.urna, "pt-BR");
    if (o === "esp"){ var ea = ESP_ORD[espDe(a)], eb = ESP_ORD[espDe(b)]; ea = ea == null ? 9 : ea; eb = eb == null ? 9 : eb; if (ea !== eb) return ea - eb; }
    if (o === "chance"){ var pa = a.modelo ? a.modelo.eleito || 0 : -1, pb = b.modelo ? b.modelo.eleito || 0 : -1; if (pb !== pa) return pb - pa; }
    return Number(a.num) - Number(b.num);
  });
}
function nFiltros(){ var f = st.f; return (f.genero?1:0) + f.esp.length + (f.partido?1:0) + (f.det?1:0) + Object.keys(f.pautas).length; }

// ---------- render ----------
var ICON_EXT = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="M14 4h6v6M20 4l-9 9M19 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h5"/></svg>';
function pct(v){ if (v === 0) return "≈ 0%"; if (v > 0 && v < .001) return "< 0,1%"; if (v > .999 && v < 1) return "> 99,9%"; return (v*100).toLocaleString("pt-BR",{maximumFractionDigits: v < .1 ? 1 : 0}) + "%"; }

function chanceHTML(m){
  // Mesmo padrão do site: a barra são os VOTOS estimados no 1º turno, com a faixa listrada
  // amarela de ±1 desvio na ponta; o número em destaque é a CHANCE de ser eleito.
  if (!m || m.eleito == null) return '';
  var h = '<div class="chance"><div class="ch-top"><span>Chance de ser eleito</span><b>' + pct(m.eleito) + '</b></div>';
  if (m.share != null){
    var sd = m.sd || 0, w = Math.max(Math.min(m.share * 100, 100), 0), left = Math.max(w - sd * 100, 0), band = Math.max(Math.min(sd * 200, 100 - left), 0);
    h += '<div class="exbar" role="img" aria-label="Votos estimados ' + pct(m.share) + ', margem de mais ou menos ' + Math.round(sd * 100) + ' pontos"><i class="b-win" style="width:' + w.toFixed(1) + '%"></i><i class="exband" style="left:' + left.toFixed(1) + '%;width:' + band.toFixed(1) + '%"></i></div>' +
         '<div class="ch-sub">Votos estimados no 1º turno: ' + pct(m.share) + (sd ? ' <span class="mg">±' + Math.round(sd * 100) + ' p.p.</span>' : '') + '</div>';
  }
  return h + '</div>';
}
var POS_LBL = {favor: "A favor", contra: "Contra", neutro: "Neutro"};
var PAUTA_BY = {}; PAUTAS.forEach(function(p){ PAUTA_BY[p.id] = p; });
// destaque discreto (referência visual pessoal): verde/vermelho de fundo conforme o lado da pauta
function tom(pid, v){ var lado = PAUTA_BY[pid] && PAUTA_BY[pid].verde; if (!lado || v === "neutro" || !v) return ""; return v === lado ? " v" : " r"; }
function destaques(pautas, n){
  var fav = [], con = [];
  PAUTAS.forEach(function(p){ var v = pautas[p.id]; if (v === "favor") fav.push(p); else if (v === "contra") con.push(p); });
  var out = [];
  while (out.length < n && (fav.length || con.length)){
    if (fav.length) out.push(["favor", fav.shift()]);
    if (out.length < n && con.length) out.push(["contra", con.shift()]);
  }
  return out;
}
function cardHTML(x){
  var picks = getPick(x.cargo), sel = picks.some(function(p){ return p.sq === x.sq; });
  var cheio = !sel && vagas(x.cargo) > 1 && picks.length >= vagas(x.cargo);
  var d = x.detalhes || {};
  var sub = esc(x.partido) + (x.federacao ? ' · Federação ' + esc(x.federacao) : '');
  var idn = esc(x.nome) + (x.ocupacao ? ' · ' + esc(x.ocupacao) : '');
  var tags = '';
  var e = espDe(x); if (e) tags += '<span class="tag" title="' + (d.espectro ? 'Espectro do candidato (detalhes públicos)' : 'Espectro usual do partido') + '">' + ESP_LBL[e] + (d.espectro ? '' : ' (partido)') + '</span>';
  if (x.genero) tags += '<span class="tag">' + (x.genero === "F" ? "Mulher" : "Homem") + '</span>';
  if (x.detalhes) tags += '<span class="tag pub" title="Tem resumo e posicionamentos compilados de declarações públicas e da imprensa">Detalhes públicos</span>';
  var corpo = '';
  if (d.resumo) corpo += '<p class="resumo">' + esc(d.resumo) + '</p>';
  if (d.pautas){
    var ds = destaques(d.pautas, 4), resto = Object.keys(d.pautas).length;
    var item = function(t){ return '<span class="pp' + tom(t[1].id, t[0]) + '">' + esc(t[1].label) + '</span>'; };
    var fav = ds.filter(function(t){ return t[0] === "favor"; }).map(item);
    var con = ds.filter(function(t){ return t[0] === "contra"; }).map(item);
    corpo += '<div class="posbox"><div class="pb-h"><span>Posicionamentos</span><button type="button" class="lnk" data-acao="det">ver as ' + resto + ' pautas</button></div>' +
      (ds.length ? '<dl class="pl">' + (fav.length ? '<dt><b aria-hidden="true">✓</b>A favor</dt><dd>' + fav.join(" · ") + '</dd>' : '') + (con.length ? '<dt><b aria-hidden="true">✗</b>Contra</dt><dd>' + con.join(" · ") + '</dd>' : '') + '</dl>'
                 : '<p class="pl">Neutro nas pautas levantadas.</p>') + '</div>';
  }
  return '<article class="card' + (sel ? ' sel' : '') + (aberto[x.sq] ? ' aberto' : '') + '" data-sq="' + x.sq + '">' +
    '<div class="top"><div class="av" data-f="' + x._f + '" data-sq="' + x.sq + '" aria-hidden="true">' + esc(ini(x.urna)) + '</div>' +
    '<div class="id"><h3>' + esc(x.urna) + '</h3><div class="sub">' + sub + '</div></div>' +
    '<div class="numero"><span class="sr">Número </span>' + esc(x.num) + '</div></div>' +
    '<div class="idn">' + idn + '</div>' +
    alertaHTML(x) + (tags ? '<div class="tags">' + tags + '</div>' : '') + corpo + chanceHTML(x.modelo) +
    '<a class="oficial mini" href="' + esc(x.link) + '" target="_blank" rel="noopener external">Ficha oficial no TSE: registro, bens e propostas ' + ICON_EXT + '</a>' +
    '<div class="acoes"><button type="button" class="btn escolher" data-acao="escolher" aria-pressed="' + sel + '"' + (cheio ? ' disabled title="Você já escolheu ' + vagas(x.cargo) + '. Remova uma escolha para trocar."' : '') + '>' + (sel ? '✓ Escolhido' : (vagas(x.cargo) === 1 && picks.length ? 'Trocar por este' : 'Escolher')) + '</button>' +
    '<button type="button" class="btn" data-acao="det" aria-expanded="' + (!!aberto[x.sq]) + '" aria-controls="det-' + x.sq + '">' + (aberto[x.sq] ? 'Fechar' : 'Detalhes') + '</button></div>' +
    '<div class="det" id="det-' + x.sq + '">' + detHTML(x) + '</div></article>';
}
function alertaHTML(x){
  var h = "";
  if (x.voto === "nulo") h += '<div class="alerta nulo" role="note"><b>Voto será anulado.</b> O nome está na urna, mas a candidatura consta como "' + esc(x.situacao) + '" no TSE e o voto não conta.</div>';
  if (x.voto === "sub_judice") h += '<div class="alerta sub_judice" role="note"><b>Voto pode não contar.</b> Candidatura "' + esc(x.situacao) + '" no TSE: o voto só vale se a Justiça Eleitoral reverter a decisão.</div>';
  if (x.substitui && x.substitui.na_urna) h += '<div class="alerta info" role="note">Substituiu <b>' + esc(x.substitui.urna) + '</b> depois da carga da urna. Na tela da urna ainda aparecem o nome e a foto de ' + esc(x.substitui.urna) + ', mas o voto no ' + esc(x.num) + ' vai para ' + esc(x.urna) + '.</div>';
  return h;
}
function detHTML(x){
  var d = x.detalhes || {};
  var h = '<dl>';
  if (x.nome_social) h += '<dt>Nome social</dt><dd>' + esc(x.nome_social) + '</dd>';
  h += '<dt>Gênero</dt><dd>' + (x.genero === "F" ? "Feminino" : x.genero === "M" ? "Masculino" : "Não informado") + ' <span class="fr">(declarado ao TSE)</span></dd>';
  if (x.situacao) h += '<dt>Situação</dt><dd>' + esc(x.situacao) + '</dd>';
  if (x.substitui && !x.substitui.na_urna) h += '<dt>Substituiu</dt><dd>' + esc(x.substitui.urna) + '</dd>';
  h += '<dt>Partido</dt><dd>' + esc(x.partido) + (x.esp_partido ? ' <span class="fr">· espectro usual: ' + ESP_LBL[x.esp_partido].toLowerCase() + '</span>' : '') + '</dd></dl>';
  if (d.pautas){
    h += '<div class="bloco"><h4>Posicionamentos nas 15 pautas</h4><div class="pautas">' + PAUTAS.map(function(p){ var v = d.pautas[p.id]; return v ? '<div class="pauta"><span title="' + esc(p.descricao) + '">' + esc(p.label) + '</span><span class="pos ' + v + tom(p.id, v) + '">' + {favor:"✓ A favor",contra:"✗ Contra",neutro:"Neutro"}[v] + '</span></div>' : ''; }).join("") + '</div>' +
         '<p class="fonte-det">Compilado de declarações públicas e da cobertura da imprensa. Não verificado item a item: confira nas fontes.</p></div>';
  } else {
    h += '<p class="nada">Sem posicionamentos levantados para esta candidatura.</p>';
  }
  if (x.modelo && x.modelo.eleito != null) h += '<p class="fonte-det">Chance de ser eleito e votos estimados vêm do modelo estatístico do Ficha do Jogo, calculado a partir de pesquisas publicadas. A faixa amarela na ponta da barra é a margem (±1 desvio).</p>';
  return h;
}

function headHTML(){
  var c = st.cargo, v = vagas(c), d = CARGO_BY[c].digitos, picks = getPick(c);
  var onde = c === "presidente" ? "Brasil" : (st.uf ? (UF_NOMES[st.uf] || st.uf) : "");
  var regra = 'Escolha <b>' + (v > 1 ? 'até ' + v + ' nomes' : '1 nome') + '</b>. Na urna, ' + (v > 1 ? 'cada voto tem' : 'são') + ' <b>' + d + ' dígitos</b>.';
  if (c === "senador") regra += ' Em 2026 são 2 vagas por estado, e a urna pede os dois votos em sequência.';
  var slots = '';
  for (var i = 0; i < v; i++){
    var p = picks[i];
    slots += p ? '<div class="pick"><div class="av" data-f="' + p.f + '" data-sq="' + p.sq + '" style="width:36px;height:36px;font-size:12px" aria-hidden="true">' + esc(ini(p.urna)) + '</div><div class="nm">' + esc(p.urna) + '<small>' + esc(p.partido) + '</small></div><span class="num">' + esc(p.num) + '</span><button type="button" data-rm="' + p.sq + '" aria-label="Remover ' + esc(p.urna) + '">×</button></div>'
               : '<div class="vazio">' + (v > 1 ? (i + 1) + 'º voto: ' : '') + 'nenhuma escolha ainda</div>';
  }
  return '<div><h2>' + esc(cargoLabel(c)) + (onde ? ' <span style="color:var(--mut);font-weight:600">· ' + esc(onde) + '</span>' : '') + '</h2><p class="regra">' + regra + '</p></div>' +
    '<div class="escolha' + (picks.length >= v ? ' cheia' : '') + '"><span class="tt">' + (v > 1 ? 'Suas escolhas' : 'Sua escolha') + '</span>' + slots + '</div>';
}

function ativosHTML(){
  var f = st.f, h = [];
  if (f.genero) h.push('<button type="button" class="chip-x" data-x="genero">' + (f.genero === "F" ? "Mulheres" : "Homens") + '</button>');
  f.esp.forEach(function(e){ h.push('<button type="button" class="chip-x" data-x="esp" data-v="' + e + '">' + ESP_LBL[e] + '</button>'); });
  if (f.partido) h.push('<button type="button" class="chip-x" data-x="partido">' + esc(f.partido) + '</button>');
  if (f.det) h.push('<button type="button" class="chip-x" data-x="det">Com detalhes públicos</button>');
  PAUTAS.forEach(function(p){ var v = f.pautas[p.id]; if (v) h.push('<button type="button" class="chip-x" data-x="pauta" data-v="' + p.id + '">' + esc(p.label) + ': ' + (v === "favor" ? "a favor" : "contra") + '</button>'); });
  if (h.length > 1) h.push('<button type="button" class="chip-x limpar" data-x="tudo">Limpar tudo</button>');
  return h.join("");
}

function render(){
  // abas
  [].forEach.call(document.querySelectorAll(".tab"), function(t){
    var c = t.getAttribute("data-cargo"), n = getPick(c).length, v = vagas(c);
    t.setAttribute("aria-selected", c === st.cargo ? "true" : "false");
    t.tabIndex = c === st.cargo ? 0 : -1;
    t.classList.toggle("ok", n >= v); t.classList.toggle("parcial", n > 0 && n < v);
    t.querySelector(".st").textContent = n >= v ? "✓" : (n ? n : "");
    t.querySelector(".lb").textContent = cargoLabel(c, true);
  });
  $("cargo-head").innerHTML = headHTML();
  $("ativos").innerHTML = ativosHTML();
  var nf = nFiltros(); $("n-filtros").textContent = nf; $("n-filtros").hidden = !nf;
  var temModelo = ["presidente","governador","senador"].indexOf(st.cargo) >= 0;
  $("op-chance").hidden = $("op-chance").disabled = !temModelo;
  if (st.ordem === "chance" && !temModelo) { st.ordem = "esp"; $("ordem").value = "esp"; }
  renderDock();
  listaDoCargo(function(lista){
    $("painel").classList.toggle("sem-uf", lista === null);
    if (lista === null){
      $("contagem").textContent = "";
      // sem UF: a escolha do estado aparece AQUI, dentro da aba (no celular, a frase "escolha
      // acima" parecia página vazia; o Bera achou que o site tinha quebrado em 03/10/2026)
      $("lista").innerHTML = '<div class="pede-uf"><label for="uf-inline">Onde você vota?</label>' +
        '<p>' + esc(cargoLabel(st.cargo)) + ' depende do estado. Escolha uma vez e vale para todas as abas.</p>' +
        '<div class="ufsel"><select id="uf-inline">' + $("uf").innerHTML + '</select></div></div>';
      $("uf-inline").value = "";
      $("mais").innerHTML = "";
      return;
    }
    var fil = ordenar(lista.filter(passa));
    var fora = 0;
    if (Object.keys(st.f.pautas).length) fora = lista.filter(function(x){ return !x.detalhes || !x.detalhes.pautas; }).length;
    $("contagem").innerHTML = '<b>' + fil.length.toLocaleString("pt-BR") + '</b> de ' + lista.length.toLocaleString("pt-BR") + ' candidaturas' +
      (fora ? ' · filtros de pauta só alcançam quem tem detalhes públicos (' + (lista.length - fora) + ' aqui)' : '');
    if (!fil.length){
      $("g-ver").textContent = "Nenhum resultado";
      $("lista").innerHTML = '<div class="vazia">Nenhuma candidatura com esses critérios.' + (nf ? '<br><button type="button" class="btn" style="margin-top:12px" data-x="tudo">Limpar filtros</button>' : '') + '</div>';
      $("mais").innerHTML = ""; return;
    }
    $("g-ver").textContent = "Ver " + fil.length.toLocaleString("pt-BR") + (fil.length === 1 ? " resultado" : " resultados");
    $("lista").innerHTML = fil.slice(0, st.limite).map(cardHTML).join("");
    $("mais").innerHTML = fil.length > st.limite ? '<button type="button" class="btn" id="btn-mais">Mostrar mais ' + Math.min(PASSO, fil.length - st.limite) + ' (faltam ' + (fil.length - st.limite).toLocaleString("pt-BR") + ')</button>' : '';
    fotos();
  });
  fotos();
}

function renderDock(){
  var tot = 0, ok = 0, tr = "";
  URNA_ORDEM.forEach(function(u){ tot++; var tem = !!getPick(u[0])[u[1]]; if (tem) ok++; tr += '<i class="' + (tem ? 'ok' : '') + '"></i>'; });
  $("dock-lb").innerHTML = 'Seu santinho: ' + ok + ' de ' + tot + ' <span>' + (st.uf ? '· ' + esc(st.uf) : '· escolha onde vota') + '</span>';
  $("trilha").innerHTML = tr;
}

// ---------- fotos sob demanda ----------
var obs = "IntersectionObserver" in window ? new IntersectionObserver(function(es){
  es.forEach(function(e){ if (e.isIntersecting){ obs.unobserve(e.target); carregaFoto(e.target); } });
}, {rootMargin: "300px"}) : null;
function fotos(){ [].forEach.call(document.querySelectorAll(".av[data-f]:not([data-ok])"), function(el){ el.setAttribute("data-ok", "1"); obs ? obs.observe(el) : carregaFoto(el); }); }
function carregaFoto(el){
  var b = el.getAttribute("data-f"), sq = el.getAttribute("data-sq");
  if (!FOTOS[b]) FOTOS[b] = fetch("santinho/fotos/" + b + ".json?v=" + VER).then(function(r){ return r.ok ? r.json() : {}; }).catch(function(){ return {}; });
  FOTOS[b].then(function(d){
    if (!d[sq]) return;
    var im = new Image(); im.alt = ""; im.decoding = "async";
    im.onload = function(){ im.className = "ok"; };
    im.src = d[sq]; el.appendChild(im);
  });
}

// ---------- ações ----------
function acharCand(sq){
  var l = BASE.candidatos.concat(DEP[st.uf] || []);
  for (var i = 0; i < l.length; i++) if (l[i].sq === sq) return l[i];
  return null;
}
function alternar(sq){
  var x = acharCand(sq); if (!x) return;
  var p = getPick(x.cargo).slice(), i = p.map(function(y){ return y.sq; }).indexOf(sq);
  if (i >= 0) p.splice(i, 1);
  else { if (vagas(x.cargo) === 1) p = []; else if (p.length >= vagas(x.cargo)) return; p.push({sq: x.sq, urna: x.urna, num: x.num, partido: x.partido, f: x._f, voto: x.voto || ""}); }
  setPick(x.cargo, p);
  avisar(i >= 0 ? x.urna + " removido" : x.urna + " escolhido para " + cargoLabel(x.cargo).toLowerCase());
  render();
}
function avisar(t){ $("aviso").textContent = t; }

document.addEventListener("click", function(ev){
  var t = ev.target.closest ? ev.target.closest("button,[data-x]") : null; if (!t) return;
  var a = t.getAttribute("data-acao");
  if (a === "escolher") return alternar(t.closest(".card").getAttribute("data-sq"));
  if (a === "det"){
    var card = t.closest(".card"), sq = card.getAttribute("data-sq"), bt = card.querySelector(".acoes [data-acao=det]");
    aberto[sq] = !aberto[sq]; card.classList.toggle("aberto", aberto[sq]);
    bt.setAttribute("aria-expanded", aberto[sq]); bt.textContent = aberto[sq] ? "Fechar" : "Detalhes";
    if (aberto[sq] && t !== bt) card.querySelector(".det").scrollIntoView({block: "nearest", behavior: "smooth"});
    return;
  }
  if (t.hasAttribute("data-rm")){
    var c = st.cargo; setPick(c, getPick(c).filter(function(p){ return p.sq !== t.getAttribute("data-rm"); })); render(); return;
  }
  if (t.classList.contains("tab")) return trocaCargo(t.getAttribute("data-cargo"));
  var x = t.getAttribute("data-x");
  if (x){
    var f = st.f, v = t.getAttribute("data-v");
    if (x === "genero") f.genero = "";
    if (x === "esp") f.esp = f.esp.filter(function(e){ return e !== v; });
    if (x === "partido") f.partido = "";
    if (x === "det") f.det = false;
    if (x === "pauta") delete f.pautas[v];
    if (x === "tudo") st.f = {genero:"", esp:[], partido:"", det:false, pautas:{}};
    st.limite = PASSO; syncGaveta(); render(); return;
  }
  if (t.id === "btn-mais"){ st.limite += PASSO; render(); return; }
});

function trocaCargo(c){
  st.cargo = c; st.limite = PASSO; st.q = ""; $("busca").value = ""; st.f.partido = "";
  syncGaveta(); render();
  try { history.replaceState(null, "", "#" + c); } catch(e){}
  var top = $("cargo-head").getBoundingClientRect().top + window.scrollY - 120;
  if (window.scrollY > top) window.scrollTo(0, top);
}
// teclado nas abas (setas)
$("abas").addEventListener("keydown", function(e){
  if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
  var ids = CARGOS.map(function(c){ return c.id; }), i = ids.indexOf(st.cargo) + (e.key === "ArrowRight" ? 1 : -1);
  i = (i + ids.length) % ids.length; trocaCargo(ids[i]); document.querySelector('.tab[data-cargo="' + ids[i] + '"]').focus();
});

var tq;
$("busca").addEventListener("input", function(){ clearTimeout(tq); var v = this.value; tq = setTimeout(function(){ st.q = v.trim(); st.limite = PASSO; render(); }, 180); });
$("ordem").addEventListener("change", function(){ st.ordem = this.value; render(); });
function trocaUF(v){ st.uf = v; $("uf").value = v; ls("fdj_sant_uf", st.uf); st.limite = PASSO; st.f.partido = ""; syncGaveta(); render(); }
$("uf").addEventListener("change", function(){ trocaUF(this.value); });
document.addEventListener("change", function(e){ if (e.target && e.target.id === "uf-inline" && e.target.value){ trocaUF(e.target.value); avisar("Estado escolhido: " + (UF_NOMES[st.uf] || st.uf)); } });

// ---------- gaveta de filtros ----------
function abreGaveta(){ syncGaveta(); $("veu").classList.add("on"); $("gaveta").classList.add("on"); $("gaveta").setAttribute("aria-hidden","false"); if (window.fdjDrawerOpen) fdjDrawerOpen($("gaveta")); }
function fechaGaveta(){ $("veu").classList.remove("on"); $("gaveta").classList.remove("on"); $("gaveta").setAttribute("aria-hidden","true"); if (window.fdjDrawerClose) fdjDrawerClose(); }
$("btn-filtros").addEventListener("click", abreGaveta);
$("veu").addEventListener("click", fechaGaveta);
$("g-fechar").addEventListener("click", fechaGaveta);
$("g-ver").addEventListener("click", fechaGaveta);
$("g-limpar").addEventListener("click", function(){ st.f = {genero:"", esp:[], partido:"", det:false, pautas:{}}; syncGaveta(); render(); });
document.addEventListener("keydown", function(e){ if (e.key === "Escape"){ if ($("gaveta").classList.contains("on")) fechaGaveta(); if ($("colinha").classList.contains("on")) fechaColinha(); } });

function syncGaveta(){
  var f = st.f;
  [].forEach.call(document.querySelectorAll("#f-genero button"), function(b){ b.setAttribute("aria-pressed", b.getAttribute("data-v") === f.genero); });
  [].forEach.call(document.querySelectorAll("#f-esp button"), function(b){ b.setAttribute("aria-pressed", f.esp.indexOf(b.getAttribute("data-v")) >= 0); });
  $("f-det").setAttribute("aria-pressed", f.det);
  [].forEach.call(document.querySelectorAll(".pf"), function(row){ var id = row.getAttribute("data-p"); [].forEach.call(row.querySelectorAll("button"), function(b){ b.setAttribute("aria-pressed", (f.pautas[id] || "") === b.getAttribute("data-v")); }); });
  listaDoCargo(function(l){
    var ps = {}; (l || []).forEach(function(x){ ps[x.partido] = 1; });
    var sel = $("f-partido"); sel.innerHTML = '<option value="">Todos os partidos</option>' + Object.keys(ps).sort().map(function(p){ return '<option' + (p === f.partido ? ' selected' : '') + '>' + esc(p) + '</option>'; }).join("");
    var na = (l || []).filter(function(x){ return x.detalhes && x.detalhes.pautas; }).length;
    $("f-pautas-nota").textContent = na ? "Só funciona para quem tem posicionamentos levantados em fontes públicas: " + na + " candidatura(s) neste cargo." : "Ninguém neste cargo tem posicionamentos levantados ainda.";
  });
}
$("f-genero").addEventListener("click", function(e){ var b = e.target.closest("button"); if (!b) return; st.f.genero = b.getAttribute("data-v"); st.limite = PASSO; syncGaveta(); render(); });
$("f-esp").addEventListener("click", function(e){ var b = e.target.closest("button"); if (!b) return; var v = b.getAttribute("data-v"), i = st.f.esp.indexOf(v); i >= 0 ? st.f.esp.splice(i,1) : st.f.esp.push(v); st.limite = PASSO; syncGaveta(); render(); });
$("f-det").addEventListener("click", function(){ st.f.det = !st.f.det; syncGaveta(); render(); });
$("f-partido").addEventListener("change", function(){ st.f.partido = this.value; st.limite = PASSO; render(); });
$("f-pautas").addEventListener("click", function(e){ var b = e.target.closest("button"); if (!b) return; var id = b.closest(".pf").getAttribute("data-p"), v = b.getAttribute("data-v"); if (v) st.f.pautas[id] = v; else delete st.f.pautas[id]; st.limite = PASSO; syncGaveta(); render(); });

// ---------- colinha ----------
function colinhaTexto(){
  return URNA_ORDEM.map(function(u){ var p = getPick(u[0])[u[1]], lb = cargoLabel(u[0]) + (u[0] === "senador" ? " (" + (u[1] + 1) + "º voto)" : ""); return lb + ": " + (p ? p.num + " " + p.urna + " (" + p.partido + ")" + (p.voto === "nulo" ? " [voto será anulado]" : p.voto === "sub_judice" ? " [sub judice]" : "") : "ainda não escolhi"); }).join("\n");
}
function abreColinha(){
  $("colinha-sub").textContent = (st.uf ? (UF_NOMES[st.uf] || st.uf) + " · " : "") + "na ordem em que a urna pede";
  $("colinha-lista").innerHTML = URNA_ORDEM.map(function(u){
    var c = u[0], p = getPick(c)[u[1]], d = CARGO_BY[c].digitos, lb = cargoLabel(c) + (c === "senador" ? " · " + (u[1] + 1) + "º voto" : "");
    var dig = ""; for (var i = 0; i < d; i++) dig += "<b>" + (p ? esc(String(p.num)[i] || "") : "") + "</b>";
    var w = p && p.voto ? '<div class="av-w ' + p.voto + '">' + (p.voto === "nulo" ? "⚠ Voto será anulado" : "⚠ Voto pode não contar (sub judice)") + '</div>' : '';
    return '<div class="linha' + (p ? '' : ' vaz') + '"><div><div class="c">' + esc(lb) + '</div><div class="q">' + (p ? esc(p.urna) + ' · ' + esc(p.partido) : 'ainda não escolhido') + '</div>' + w + '</div><div class="digitos"><span class="sr">' + (p ? 'Número ' + esc(p.num) : 'sem número') + '</span><span aria-hidden="true" class="dg">' + dig + '</span></div></div>';
  }).join("");
  $("colinha").classList.add("on"); aplicaPB(); if (window.fdjDrawerOpen) fdjDrawerOpen($("colinha"));
}
function fechaColinha(){ $("colinha").classList.remove("on"); if (window.fdjDrawerClose) fdjDrawerClose(); }
$("btn-colinha").addEventListener("click", abreColinha);
$("c-fechar").addEventListener("click", fechaColinha);
$("colinha").addEventListener("click", function(e){ if (e.target === this) fechaColinha(); });
$("c-imprimir").addEventListener("click", function(){ window.print(); });

// cores: colorida ou preto e branco (vale para a prévia, a impressão e a imagem)
var PB = ls("fdj_sant_pb") === true, IMG = null;
function aplicaPB(){
  document.querySelector("#colinha .folha").classList.toggle("pb", PB);
  [].forEach.call(document.querySelectorAll("#colinha [data-pb]"), function(b){ b.setAttribute("aria-pressed", (b.getAttribute("data-pb") === "1") === PB); });
  IMG = null; preparaImagem();
}
document.querySelector("#colinha .cores").addEventListener("click", function(e){
  var b = e.target.closest("[data-pb]"); if (!b) return; PB = b.getAttribute("data-pb") === "1"; ls("fdj_sant_pb", PB); aplicaPB();
});

// imagem da colinha em <canvas> (sem biblioteca): fica pronta antes do clique, para o
// compartilhamento do celular (Salvar imagem -> Fotos) rodar dentro do gesto do usuário
function linhasColinha(){
  return URNA_ORDEM.map(function(u){
    var c = u[0], p = getPick(c)[u[1]];
    return {cargo: (cargoLabel(c) + (c === "senador" ? " · " + (u[1] + 1) + "º voto" : "")).toUpperCase(), p: p, d: CARGO_BY[c].digitos};
  });
}
function rr(x, a, b, w, h, r){ x.beginPath(); x.moveTo(a + r, b); x.arcTo(a + w, b, a + w, b + h, r); x.arcTo(a + w, b + h, a, b + h, r); x.arcTo(a, b + h, a, b, r); x.arcTo(a, b, a + w, b, r); x.closePath(); }
function corta(x, t, max){ if (x.measureText(t).width <= max) return t; while (t.length > 1 && x.measureText(t + "…").width > max) t = t.slice(0, -1); return t + "…"; }
function desenhaColinha(){
  var K = PB ? {bg:"#ffffff", card:"#ffffff", ink:"#000000", mut:"#333333", ac:"#000000", box:"#000000", line:"#999999", nulo:"#000000", sj:"#000000", vazio:"#bbbbbb"}
             : {bg:"#0f1b13", card:"#18271d", ink:"#f1ece0", mut:"#9fae9d", ac:"#f3b03c", box:"#f1ece0", line:"#25382b", nulo:"#f87171", sj:"#eab308", vazio:"#3a5040"};
  var L = linhasColinha(), W = 1080, P = 64, RH = 168, H = 300 + L.length * RH + 190;
  var cv = document.createElement("canvas"); cv.width = W; cv.height = H;
  var x = cv.getContext("2d"), F = '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif', M = 'ui-monospace,SFMono-Regular,Menlo,Consolas,monospace';
  x.fillStyle = K.bg; x.fillRect(0, 0, W, H);
  x.fillStyle = K.ac; x.font = "800 26px " + F; x.fillText("ELEIÇÕES 2026 · 1º TURNO", P, 92);
  x.fillStyle = K.ink; x.font = "800 64px " + F; x.fillText("Minha colinha", P, 170);
  x.fillStyle = K.mut; x.font = "500 30px " + F;
  x.fillText("Domingo, 4 de outubro" + (st.uf ? " · " + (UF_NOMES[st.uf] || st.uf) : "") + " · ordem da urna", P, 222);
  var y = 280;
  L.forEach(function(l){
    x.strokeStyle = K.line; x.lineWidth = 2; x.setLineDash([10, 8]); x.beginPath(); x.moveTo(P, y); x.lineTo(W - P, y); x.stroke(); x.setLineDash([]);
    var bw = 74, bh = 96, gap = 10, dw = l.d * bw + (l.d - 1) * gap, dx = W - P - dw, by = y + (RH - bh) / 2;
    x.fillStyle = K.mut; x.font = "800 24px " + F; x.fillText(l.cargo, P, y + 50);
    x.fillStyle = l.p ? K.ink : K.mut; x.font = (l.p ? "700 38px " : "italic 500 34px ") + F;
    x.fillText(corta(x, l.p ? l.p.urna + " · " + l.p.partido : "ainda não escolhido", dx - P - 24), P, y + 98);
    if (l.p && l.p.voto){ x.fillStyle = l.p.voto === "nulo" ? K.nulo : K.sj; x.font = "800 26px " + F; x.fillText(l.p.voto === "nulo" ? "⚠ voto será anulado" : "⚠ voto pode não contar (sub judice)", P, y + 138); }
    for (var i = 0; i < l.d; i++){
      var bx = dx + i * (bw + gap);
      x.lineWidth = 4; x.strokeStyle = l.p ? K.box : K.vazio; rr(x, bx, by, bw, bh, 12); x.stroke();
      if (l.p){ x.fillStyle = K.ink; x.font = "800 60px " + M; x.textAlign = "center"; x.fillText(String(l.p.num)[i] || "", bx + bw / 2, by + 70); x.textAlign = "left"; }
    }
    y += RH;
  });
  x.strokeStyle = K.line; x.setLineDash([10, 8]); x.beginPath(); x.moveTo(P, y); x.lineTo(W - P, y); x.stroke(); x.setLineDash([]);
  x.fillStyle = K.mut; x.font = "500 26px " + F;
  x.fillText("Confira cada número na ficha oficial do TSE.", P, y + 62);
  x.fillText("Celular não pode ser usado na cabine: leve a colinha impressa ou escrita.", P, y + 102);
  return cv;
}
function preparaImagem(){
  try { desenhaColinha().toBlob(function(b){ IMG = b; }, "image/png"); } catch(e){ IMG = null; }
}
function salvaImagem(blob){
  var nome = "colinha-eleicoes-2026" + (st.uf ? "-" + st.uf.toLowerCase() : "") + (PB ? "-pb" : "") + ".png";
  var arq = null; try { arq = new File([blob], nome, {type: "image/png"}); } catch(e){}
  if (arq && navigator.canShare && navigator.canShare({files: [arq]})){
    navigator.share({files: [arq], title: "Minha colinha"}).catch(function(){});
    return "compartilhar";
  }
  var a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = nome;
  document.body.appendChild(a); a.click(); setTimeout(function(){ URL.revokeObjectURL(a.href); a.remove(); }, 2000);
  return "baixar";
}
$("c-imagem").addEventListener("click", function(){
  var b = this, feito = function(m){ b.textContent = m === "baixar" ? "✓ Imagem salva" : "Salvar como imagem"; setTimeout(function(){ b.textContent = "Salvar como imagem"; }, 2200); };
  if (IMG) return feito(salvaImagem(IMG));
  desenhaColinha().toBlob(function(bl){ if (bl){ IMG = bl; feito(salvaImagem(bl)); } else b.textContent = "Não deu para gerar a imagem"; }, "image/png");
});
$("c-copiar").addEventListener("click", function(){
  var b = this, txt = "Minha colinha · Eleições 2026\n" + colinhaTexto();
  var ok = function(){ b.textContent = "✓ Copiado"; setTimeout(function(){ b.textContent = "Copiar texto"; }, 1800); };
  if (navigator.clipboard) navigator.clipboard.writeText(txt).then(ok, function(){ b.textContent = "Não deu para copiar"; });
});

// ---------- início ----------
var UF_NOMES = META.uf_nomes;
$("uf").value = st.uf;
var h = (location.hash || "").slice(1); if (CARGO_BY[h]) st.cargo = h;
window.addEventListener("hashchange", function(){ var c = (location.hash || "").slice(1); if (CARGO_BY[c] && c !== st.cargo) trocaCargo(c); });
document.documentElement.classList.add("js");
render();
})();
"""


def tab_html(c, sel):
    return (f'<button type="button" role="tab" class="tab" data-cargo="{c["id"]}" '
            f'aria-selected="{"true" if sel else "false"}" aria-controls="painel" tabindex="{0 if sel else -1}">'
            f'<span class="st" aria-hidden="true"></span><span class="lb">{c["curto"]}</span></button>')


def card_estatico(x):
    """Card da aba Presidente pré-renderizado (página funciona sem JS)."""
    e = html.escape
    pal = x["urna"].split()
    ini = (pal[0][0] + (pal[-1][0] if len(pal) > 1 else "")).upper()
    alerta = ""
    if x.get("voto") == "nulo":
        alerta = f'<div class="alerta nulo"><b>Voto será anulado.</b> Situação no TSE: {e(x["situacao"])}.</div>'
    elif x.get("voto") == "sub_judice":
        alerta = f'<div class="alerta sub_judice"><b>Voto pode não contar.</b> Situação no TSE: {e(x["situacao"])}.</div>'
    resumo = ""
    d = x.get("detalhes") or {}
    if d.get("resumo"):
        resumo = f'<p class="resumo">{e(d["resumo"])}</p>'
    chance = ""
    m = x.get("modelo") or {}
    if m.get("eleito") is not None and m.get("share") is not None:
        sd = m.get("sd") or 0
        w = max(min(m["share"] * 100, 100), 0)
        left = max(w - sd * 100, 0)
        band = max(min(sd * 200, 100 - left), 0)
        pctf = lambda v: "≈ 0%" if v == 0 else "< 0,1%" if 0 < v < .001 else (f"{v * 100:.1f}".replace(".", ",") + "%" if v < .1 else f"{v * 100:.0f}%")
        chance = (f'<div class="chance"><div class="ch-top"><span>Chance de ser eleito</span><b>{pctf(m["eleito"])}</b></div>'
                  f'<div class="exbar"><i class="b-win" style="width:{w:.1f}%"></i><i class="exband" style="left:{left:.1f}%;width:{band:.1f}%"></i></div>'
                  f'<div class="ch-sub">Votos estimados no 1º turno: {pctf(m["share"])} <span class="mg">±{sd * 100:.0f} p.p.</span></div></div>')
    idn = e(x["nome"]) + (f' · {e(x["ocupacao"])}' if x.get("ocupacao") else "")
    return (f'<article class="card"><div class="top"><div class="av" aria-hidden="true">{e(ini)}</div>'
            f'<div class="id"><h3>{e(x["urna"])}</h3><div class="sub">{e(x["partido"])}</div></div>'
            f'<div class="numero"><span class="sr">Número </span>{e(x["num"])}</div></div><div class="idn">{idn}</div>{alerta}{resumo}{chance}'
            f'<a class="oficial mini" href="{e(x["link"])}" target="_blank" rel="noopener external">Ficha oficial no TSE</a></article>')


def render_html(base):
    meta = base["meta"]
    ordem_esp = {"esquerda": 0, "centro-esquerda": 1, "centro": 2, "centro-direita": 3, "direita": 4}
    def esp(c):
        return ordem_esp.get((c.get("detalhes") or {}).get("espectro") or c.get("esp_partido"), 9)
    pres = sorted((c for c in base["candidatos"] if c["cargo"] == "presidente"), key=lambda c: (esp(c), int(c["num"])))
    tabs = "".join(tab_html(c, c["id"] == "presidente") for c in meta["cargos"])
    ufs = '<option value="">Selecione o estado</option>' + "".join(
        f'<option value="{u}">{UF_NOMES[u]} ({u})</option>' for u in sorted(meta["ufs"], key=lambda u: UF_NOMES[u]))
    esp = "".join(f'<button type="button" data-v="{k}" aria-pressed="false">{v}</button>' for k, v in
                  [("esquerda", "Esquerda"), ("centro-esquerda", "Centro-esquerda"), ("centro", "Centro"),
                   ("centro-direita", "Centro-direita"), ("direita", "Direita")])
    pautas = "".join(
        f'<div class="pf" data-p="{p["id"]}"><span title="{html.escape(p["descricao"])}">{html.escape(p["label"])}</span>'
        f'<span class="seg" role="group" aria-label="{html.escape(p["label"])}">'
        f'<button type="button" data-v="" aria-pressed="true">Tanto faz</button>'
        f'<button type="button" data-v="favor" aria-pressed="false">A favor</button>'
        f'<button type="button" data-v="contra" aria-pressed="false">Contra</button></span></div>'
        for p in meta["pautas"])
    dados = json.dumps(base, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    estatico = "".join(card_estatico(x) for x in pres)
    geracao = html.escape(meta["geracao_tse"])

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<title>Meu Santinho · Eleições 2026</title>
<meta name="description" content="Ferramenta pessoal para montar a colinha de voto das Eleições 2026 com dados oficiais do TSE.">
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<style>{theme.PALETTE}{shell.CSS}{CSS}</style>
<script>(function(){{try{{if(localStorage.getItem("fdj-theme")==="light")document.documentElement.setAttribute("data-theme","light")}}catch(e){{}}}})();</script>
</head>
<body data-page="santinho">
<a class="skip" href="#painel">Pular para a lista</a>
<header class="topbar"><div class="bar"><div class="brand">{shell.LOGO}<span class="nm">Ficha <span>do Jogo</span></span></div>
<span class="sp"></span><button class="tg" id="tg" type="button" onclick="cycleTheme()" title="Tema escuro · clique para alternar" aria-label="Alternar tema">☾</button></div></header>

<main id="main">
<div class="wrap hero">
  <div><h1>Meu Santinho</h1>
  <p>Sua colinha para o 1º turno ({ELEICAO_DATA}). Escolha o cargo, compare e marque. Fica salvo só neste navegador.</p></div>
  <div class="ufbox"><label for="uf">Onde você vota?</label><div class="ufsel"><select id="uf">{ufs}</select></div></div>
</div>

<nav class="cargos" aria-label="Cargos"><div class="wrap" role="tablist" id="abas">{tabs}</div></nav>

<section class="wrap" id="painel" role="tabpanel" aria-labelledby="abas">
  <div class="cargo-head" id="cargo-head"><div><h2>Presidente <span style="color:var(--mut);font-weight:600">· Brasil</span></h2>
  <p class="regra">Escolha <b>1 nome</b>. Na urna, são <b>2 dígitos</b>.</p></div></div>
  <div class="tools">
    <div class="busca"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
      <label class="sr" for="busca">Buscar por nome, número ou partido</label><input id="busca" type="search" placeholder="Nome, número ou partido" autocomplete="off" enterkeyhint="search"></div>
    <button type="button" class="btn" id="btn-filtros" aria-controls="gaveta">Filtros <span class="n" id="n-filtros" hidden>0</span></button>
    <label class="sr" for="ordem">Ordenar</label>
    <select id="ordem" class="ordem"><option value="esp">Por espectro (esquerda → direita)</option><option value="nome">Por nome</option><option value="chance" id="op-chance">Por chance de ser eleito</option></select>
  </div>
  <div class="ativos" id="ativos" aria-label="Filtros ativos"></div>
  <p class="contagem" id="contagem" aria-live="polite">{len(pres)} candidaturas</p>
  <div class="lista" id="lista">{estatico}</div>
  <div class="mais" id="mais"></div>
  <noscript><p class="vazia">Para buscar, filtrar e montar a colinha, ative o JavaScript. A lista acima mostra as candidaturas a presidente.</p></noscript>

  <footer class="rodape">
    {DISCLAIMER}
    <p class="fonte">Fonte: TSE, dados abertos de candidaturas e fotos (geração {geracao}). Só aparecem candidaturas inseridas na urna. {shell.CREDIT}</p>
  </footer>
</section>
</main>

<div class="dock" role="region" aria-label="Seu santinho"><div class="wrap">
  <div class="prog"><div class="lb" id="dock-lb">Seu santinho: 0 de 6</div><div class="trilha" id="trilha" aria-hidden="true"></div></div>
  <button type="button" class="btn pri" id="btn-colinha">Ver colinha</button>
</div></div>
<div class="sr" role="status" aria-live="polite" id="aviso"></div>

<div class="veu" id="veu"></div>
<div class="gaveta" id="gaveta" aria-hidden="true" aria-labelledby="g-tt" role="dialog" aria-modal="true">
  <div class="g-head"><h2 id="g-tt">Filtros</h2><button type="button" class="btn" id="g-fechar" aria-label="Fechar filtros" style="min-height:38px;padding:6px 12px">Fechar</button></div>
  <div class="corpo">
    <div class="grupo"><h3>Gênero</h3><div class="op" id="f-genero">
      <button type="button" data-v="" aria-pressed="true">Todos</button><button type="button" data-v="F" aria-pressed="false">Mulheres</button><button type="button" data-v="M" aria-pressed="false">Homens</button></div>
      <p class="nota" style="margin-top:8px">Como declarado ao TSE.</p></div>
    <div class="grupo"><h3>Espectro</h3><p class="nota">Espectro do candidato quando há detalhes públicos. Quando não há, vale o espectro usual do partido.</p><div class="op" id="f-esp">{esp}</div></div>
    <div class="grupo"><h3>Partido</h3><label class="sr" for="f-partido">Partido</label><select id="f-partido"><option value="">Todos os partidos</option></select></div>
    <div class="grupo"><h3>Detalhes públicos</h3><div class="op"><button type="button" id="f-det" aria-pressed="false">Só quem tem detalhes públicos</button></div></div>
    <div class="grupo"><h3>Pautas</h3><p class="nota" id="f-pautas-nota"></p><div id="f-pautas">{pautas}</div></div>
  </div>
  <div class="g-foot"><button type="button" class="btn" id="g-limpar">Limpar</button><button type="button" class="btn pri" id="g-ver">Ver resultados</button></div>
</div>

<div class="modal" id="colinha" role="dialog" aria-modal="true" aria-labelledby="c-tt"><div class="folha">
  <h2 id="c-tt">Minha colinha</h2><p class="sub" id="colinha-sub"></p>
  <div class="cores" role="group" aria-label="Cores da colinha"><span>Cores</span><span class="seg"><button type="button" data-pb="0" aria-pressed="true">Colorida</button><button type="button" data-pb="1" aria-pressed="false">Preto e branco</button></span></div>
  <div id="colinha-lista"></div>
  <div class="acoes"><button type="button" class="btn pri" id="c-imagem">Salvar como imagem</button><button type="button" class="btn" id="c-imprimir">Imprimir ou PDF</button><button type="button" class="btn" id="c-copiar">Copiar texto</button></div>
  <button type="button" class="btn fechar" id="c-fechar" style="width:100%;margin-top:8px">Fechar</button>
  <p class="lembrete">Pode levar a colinha impressa ou escrita à mão. Celular não pode ser usado na cabine de votação.</p>
</div></div>

<script type="application/json" id="dados">{dados}</script>
{shell.JS}
<script>{JS}</script>
</body>
</html>
"""


def main():
    base = json.load(open(os.path.join(SRC, "base.json"), encoding="utf-8"))
    # versão = hash dos dados: cache-bust dos JSON sob demanda (worker cacheia assets por 1 dia)
    h = hashlib.sha256()
    for root, _, files in sorted(os.walk(SRC)):
        for fn in sorted(files):
            h.update(open(os.path.join(root, fn), "rb").read())
    # Modelo (chance de eleição, votos estimados ± sd) lido AGORA do results do dia, não do
    # base.json: o CI roda esta página todo dia, mas não o gerador de dados (que depende do
    # CSV do TSE local). Sem isto a chance do santinho congelaria enquanto o site atualiza.
    res = json.load(open(os.path.join(ROOT, "data", "eleicoes2026_results.json"), encoding="utf-8"))
    modelo = {str(c["sq"]): {"share": c.get("share"), "sd": c.get("sd"), "eleito": c.get("eleito")}
              for r in res.get("races", {}).values() for c in r.get("candidates", []) if c.get("sq") is not None}
    for c in base["candidatos"]:
        c.pop("modelo", None)
        if c["sq"] in modelo:
            c["modelo"] = modelo[c["sq"]]
    h.update(json.dumps(modelo, sort_keys=True).encode())
    base["meta"]["ver"] = h.hexdigest()[:10]
    base["meta"]["uf_nomes"] = UF_NOMES

    if os.path.isdir(OUT_DEP):
        shutil.rmtree(OUT_DEP)
    shutil.copytree(os.path.join(SRC, "dep"), OUT_DEP)
    doc = render_html(base)
    os.makedirs(DIST, exist_ok=True)
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(doc)
    tem_fotos = os.path.isdir(os.path.join(DIST, "santinho", "fotos"))
    print(f"dist/santinho.html ({len(doc.encode()) / 1024:.0f} KB) + {len(os.listdir(OUT_DEP))} UFs de deputados"
          f"{'' if tem_fotos else ' · SEM fotos (rode scripts/build_santinho_fotos.py): fallback = iniciais'}")


if __name__ == "__main__":
    main()
