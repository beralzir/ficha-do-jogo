# Copa do Mundo 2026 — Modelo Probabilístico + Dashboard

Modelo preditivo da Copa do Mundo 2026 (EUA · México · Canadá, 48 seleções) que estima,
por seleção, a probabilidade de avançar em **cada fase** até o título, além de **resultado
e gols de cada jogo**. Saída: um **site estático multipágina** (dashboard, resultados, bolão,
comparativo), interativo e sem dependências externas.

**No ar:** https://bera.ia.br/ficha-do-jogo/ (Cloudflare Workers · público).

## Origem e objetivo
Nasceu de um **bolão de futebol entre colegas de trabalho**. Está sendo usado como um
banco de provas para **modelagem probabilística aplicada a esporte e regras** — e para testar
o potencial dessa abordagem em **apostas (bet)**. Trate previsões como estimativas, não garantias.

## Quickstart
```bash
cd src
python3 wc2026_model.py        # roda o Monte Carlo (~10s) -> data/wc2026_results.json
python3 build_dashboard.py     # gera dist/copa2026_dashboard.html (dark) e copa2026_artifact.html (light)
python3 make_generic.py        # gera dist/copa2026_dashboard_generico.html (white-label, sem nomes de método/fonte)
```
Sem dependências de terceiros — só biblioteca padrão do Python 3. Abra qualquer `dist/*.html`
no navegador (duplo clique). O modelo é **determinístico** (seed fixa) e reprodutível.

> A sequência completa de build (5 páginas + white-label) e a re-simulação ficam empacotadas em
> `./atualizar.sh` — ver **Operação durante a Copa** abaixo.

## Operação durante a Copa (atualização por uma ação local)
Conforme os jogos acontecem, o forecast é **re-simulado condicionalmente** (fixa os resultados
já ocorridos e simula o resto) e o site é regerado:

```bash
# 1. Editar o estado com os jogos do dia (resultados; schema: HANDOFF.md §5)
#    data/live/state.json  ->  results.group [{match,hg,ag}] · results.knockout · results.awards
# 2. Re-simular + rebuildar + verificar (NÃO publica):
./atualizar.sh
# 3. Conferir o resultado localmente (open dist/copa2026_dashboard.html), e então publicar:
./atualizar.sh --deploy
```

`atualizar.sh` roda o motor, regenera as 5 páginas + white-label, **valida invariantes e zero-dep**,
e por padrão **para antes de publicar** (deploy é uma decisão consciente). A data de geração é
**carimbada automaticamente** a cada run (override `GENERATED=AAAA-MM-DD` só para testes), e um
**snapshot** do forecast vai para `data/snapshots/` — é o que alimenta a seção "O que mudou" do dashboard.

> **Duas datas distintas, não confundir:** a *data de coleta dos dados* ("Coletado 9/jun" — odds, Elo,
> notícias) é **estática durante a Copa** (os ratings das seleções não mudam); só a *data de geração*
> ("gerado em…") avança a cada `atualizar.sh`. Re-coletar dados de mercado é um passo manual à parte.

### ⚠️ Privacidade — antes de inserir palpites reais
O site é **público sem senha**. Enquanto `data/live/state.json` está vazio não há dado pessoal exposto.
**Antes de registrar qualquer palpite real** (placar ou prêmio), proteja `/bolao*` e `/comparativo*`
(Cloudflare Access ou basic-auth no `worker.js`) — Dashboard e Resultados podem seguir públicos.

## Estrutura
```
ficha-do-jogo/
├── README.md · CLAUDE.md · HANDOFF.md · HANDOFF_PROXIMA_SESSAO.md · SESSION.md · PLANO_EXECUCAO.md
├── atualizar.sh         ação local: re-simula + rebuilda + verifica (+ --deploy)
├── worker.js · wrangler.toml   roteador + config do deploy (Cloudflare Workers)
├── src/
│   ├── wc2026_model.py      motor: ratings -> Poisson -> Monte Carlo (re-sim condicional)
│   ├── snapshot.py          histórico de forecasts (data/snapshots/)
│   ├── awards.py            de-vig das odds de prêmios (artilheiro/luvas)
│   ├── bolao.py · metrics.py · bracket.py · state.py · build_fixtures.py · pt.py · theme.py
│   ├── build_{dashboard,bolao,comparativo,resultados,index}.py   builders das 5 páginas
│   └── make_generic.py      versão white-label do dashboard
├── data/
│   ├── worldcup2026_structure.json · fixtures.json · wc2026_dossiers.json · wc2026_awards.json
│   ├── wc2026_results.json          SAÍDA do modelo (probabilidades + gols + matchups)
│   ├── baseline/                    forecast pré-torneio CONGELADO (imutável — não sobrescrever)
│   ├── snapshots/                   histórico de forecasts por run
│   └── live/state.json              jogos ocorridos + meus palpites (entrada manual)
└── dist/                            as 5 páginas + artifact (light) + generico (white-label)
```

## O que está aberto (ver ROADMAP.md / HANDOFF_PROXIMA_SESSAO.md)
- ⚠️ **Proteger `/bolao*` + `/comparativo*`** antes de inserir palpites reais (ver Privacidade acima).
- Melhorar a qualidade probabilística do modelo (Poisson independente → correlação; calibração formal).
- Polimentos menores de UI (ver auditoria de design no `SESSION.md`).

> Coleta de dados: **9/jun/2026** (pré-torneio). Os números mudam com convocações e lesões até a
> estreia, e a partir de 11/jun com os resultados (via `atualizar.sh`).
