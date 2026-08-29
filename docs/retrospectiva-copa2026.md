# Retrospectiva — Ficha do Jogo · Copa do Mundo 2026

> Documento de fechamento da edição. Escrito em 29/08/2026, depois de fechada a medição
> (`src/finalize_scores.py`, `data/model_scores.json` com `measurement_complete: true`).
> Resumo visual público: <https://bera.ia.br/ficha-do-jogo/copa2026/retrospectiva>.
> Leitor-alvo: quem for construir a próxima edição (Eleições 2026) ou reusar o método.

## 1. O que foi

Um modelo probabilístico da Copa do Mundo 2026 (48 seleções, Monte Carlo de 50 mil simulações,
Python 3 puro) com dashboard HTML estático e zero dependências, nascido de um bolão de trabalho e
usado como laboratório de pesquisa: testar modelagem probabilística em esporte, regras de torneio e
o potencial da abordagem para apostas. Virou um produto completo: 5 páginas live (landing,
dashboard, resultados, placares, modelos) + 2 variantes (light para embed, white-label), atualização
diária automática hands-off durante o torneio, tagueamento GA4 e acessibilidade AA.

A Copa: 11/jun a 19/jul/2026. **Espanha campeã** (1x0 na prorrogação sobre a Argentina). Zebras de
pênaltis pelo caminho: Paraguai eliminou a Alemanha, Marrocos eliminou a Holanda, Egito eliminou a
Austrália, Suíça passou pela Colômbia.

## 2. Linha do tempo

| Data | Marco |
|---|---|
| 1 a 3/jun | Coleta dos dados pré-torneio (odds de título, Opta, Elo, qualitativo curado) |
| ~9/jun | Congelamento das forças pré-torneio (a "previsão a ser julgada") |
| 11/jun | Estreia da Copa; dashboard no ar |
| 23/jun | Repo consolidado + harness multi-modelo (registro de 10 modelos, freezes diários) |
| 26 a 28/jun | Automação: ingest football-data + ESPN com quorum, cron diário, deploy com gate |
| 29/jun | Correção da alocação dos 8 terceiros nos 32-avos (tabela oficial FIFA), na véspera exata do freeze usado na medição de fase |
| 30/jun | Mata-mata automático (pênaltis = placar do fim da prorrogação) + revisão UX de 6 pontos |
| 1 a 19/jul | Cruzeiro hands-off: 27 atualizações automáticas, zero intervenção manual |
| 19/jul | Final; último dado ingerido em 20/jul |
| 29/08 | Medição fechada (103 jogos + fase/título) e edição arquivada em `/copa2026` |

## 3. Arquitetura final (herdar na v2)

```
football-data.org ─┐                                      ┌─► dist/*.html (5 páginas live)
                   ├─► src/ingest.py ─► data/live/state.json                │
ESPN ──────────────┘   (gates+quorum)        │                              ▼
                                             ▼                    gate (somas, monotonicidade,
data/worldcup2026_structure.json ─► src/wc2026_model.py ─► results.json ─►  zero-dep) ─► wrangler
data/wc2026_dossiers.json (curado) ─► builders (build_*.py) ─► make_generic ─► deploy (CI 12:17 UTC)

harness: data/model_configs.json ─► run_models.py (freeze diário ─► data/models/*.json, commitado)
                                  ─► compare.py (durante) / finalize_scores.py (fechamento)
                                  ─► data/model_scores.json ─► página Modelos
```

Decisões estruturais que pagaram e devem ser herdadas:

- **Estático-primeiro, zero-dep** (GTM como única exceção consciente, removida das variantes):
  a página abre em qualquer lugar, inclusive viewers que bloqueiam script externo.
- **Contratos de dados explícitos** entre motor e view (schemas no HANDOFF): permitiu trocar
  qualquer lado sem quebrar o outro.
- **Determinismo** (seed fixa + iterações ordenadas): qualquer investigação é reproduzível.
- **Invariantes testáveis no gate de deploy** (somas por fase, monotonicidade): nenhum deploy
  ruim passou em 27 atualizações automáticas.
- **Honestidade como dado**: as ressalvas viajam DENTRO de `model_scores.json["caveats"]` e a UI
  as renderiza; a interface não consegue "esquecer" a leitura honesta.
- **Walk-forward em tudo que aprende** (prever o jogo G só com informação anterior a G).
- **Freezes diários commitados no git**: a medição de fase e a trajetória de título só foram
  possíveis porque cada congelamento ficou no histórico. Git como instrumento de auditoria.

## 4. As metodologias, medidas (o coração do projeto)

Leaderboard final, 103 dos 104 jogos (72 de grupos + 31 de mata-mata; o 3º lugar não foi capturado
pela ingestão), 1X2 com Brier/log-loss (menor = melhor), fase pelo congelamento da véspera do
mata-mata (28/jun: grupos completos, zero KO jogado):

| Modelo | Brier total | Grupos | KO | Brier fase | p(Espanha 🏆) véspera KO |
|---|---|---|---|---|---|
| Consenso de odds (market_only) | **0,4599** | **0,4925** | 0,3843 | 0,0572 | 16,0% |
| Pesos 70/30 | 0,4607 | 0,5011 | 0,3670 | 0,0561 | 21,1% |
| Pesos 85/15 | 0,4608 | 0,4979 | 0,3746 | 0,0570 | 19,6% |
| Ensemble 45/35/20 (baseline) | 0,4614 | 0,5047 | 0,3607 | 0,0553 | 22,8% |
| Aprende devagar (Elo K=20) | 0,4625 | 0,5062 | 0,3609 | **0,0448** | 19,3% |
| Pesos 30/70 | 0,4643 | 0,5133 | 0,3504 | 0,0542 | 25,7% |
| Só modelos (sem mercado) | 0,4647 | 0,5177 | **0,3416** | 0,0517 | 26,0% |
| Aprende rápido (Elo K=40) | 0,4649 | 0,5089 | 0,3627 | **0,0442** | 17,2% |
| Qualitativo reforçado | 0,4663 | 0,5108 | 0,3629 | 0,0576 | 24,2% |
| Forma de gols (calibração-only) | 0,4805 | 0,5109 | 0,4100 | (sem forecast) | (sem forecast) |

O que os números dizem (com as ressalvas de amostra única):

1. **O consenso de mercado venceu o 1X2 da Copa inteira.** Diluí-lo no blend 45/35/20 não pagou.
   É o resultado esperado pela literatura e agora está medido em casa, walk-forward e sem p-hacking.
2. **No mata-mata isolado, o quadro inverte**: só-modelos calibrou melhor (0,3416) que o consenso
   (0,3843). Com 31 jogos é indício, não veredito, mas sugere que a força estrutural leu o KO
   melhor que as odds pré-torneio.
3. **Na leitura de fase, os modelos que aprendem venceram com folga** (0,0442 e 0,0448 contra
   0,0517 a 0,0576 dos estáticos): **reagir ao torneio ajudou a ler o mata-mata**, mesmo com o
   ganho de 1X2 dentro do ruído. É o achado mais acionável da edição.
4. **A campeã estava mais cotada nos modelos que no mercado**: na véspera do KO, Espanha a 26%
   no só-modelos e 22,8% no ensemble contra 16% no consenso. Um caso não é evidência, mas é
   exatamente o tipo de discordância que o harness existe para registrar.
5. **Dobrar o qualitativo piorou a calibração** (0,4663). O qualitativo vale como narrativa (os
   dossiês são o conteúdo mais lido da página), não como peso no número.
6. **A forma de gols online, como implementada, só adicionou ruído** (pior 1X2 da mesa).
7. A **trajetória** diária de p(título) por modelo está em `model_scores.json["trajectory"]`
   (21 congelamentos, 23/jun a 20/jul), reconstruída do histórico git.

**Qual metodologia ajuda a interpretar o quê** (o mapa que a v2 deve herdar):

- **Consenso (mercado/odds)** responde "quem é favorito e quanto": âncora de calibração do 1X2.
- **Modelos estruturais** (Opta/Elo + Monte Carlo da chave) respondem "como o torneio se desdobra":
  caminho, chave, fase. Foi onde bateram o consenso.
- **Modelos dinâmicos** (Elo online) respondem "o que mudou desde ontem": melhor leitura reativa.
- **Qualitativo curado** responde "por quê" (lesões, contexto, narrativa): explicação, não número.
- **O harness multi-modelo é o instrumento que permite dizer tudo isso com número.** Maior
  aprendizado de método da edição: registrar modelos concorrentes, congelar previsões e medir
  walk-forward transforma opinião em dado.

## 5. Aprendizados de modelagem (para a v2)

1. **Não dilua o consenso sem prova.** Novo sinal entra como modelo competidor no leaderboard;
   só é promovido ao oficial se vencer com margem fora do ruído.
2. **Uma edição é UMA amostra.** Erro-padrão ~0,006 em n=103: diferenças menores que 2 EP são
   ruído, e o texto do produto precisa dizer isso (os caveats como dado resolveram).
3. **Dupla contagem é sutil**: odds já continham o Opta (corr ~0,98). Meça o consenso como
   entidade única em vez de somar fontes correlacionadas como se fossem independentes.
4. **Defina o espaço de resultado ANTES de medir.** Mata-mata em 120 minutos com "empate =
   pênaltis" foi decidido em 30/jun e a medição inteira ficou coerente com isso.
5. **Poisson independente subestima placares correlacionados**; a camada de palpite mitigou com
   Dixon-Coles (ρ=-0,13) + binomial negativa (r=8) sem mexer no motor. Na v2, correlação nasce
   dentro do motor.
6. **Valide as REGRAS do torneio contra a fonte oficial cedo.** O bug da alocação dos terceiros
   nos 32-avos foi corrigido na véspera exata do freeze que a medição de fase usa; um dia depois
   e a medição estaria contaminada.
7. **Cobertura de ingestão precisa de checagem de completude.** O jogo 103 (3º lugar) se perdeu
   em silêncio; ninguém notou por 40 dias. A v2 deve alarmar buraco na lista esperada de eventos.
8. **Freezes são o ativo de pesquisa.** Congelar previsão diária custa quase nada e é o que
   permite qualquer medição retroativa honesta.

## 6. Aprendizados de engenharia e automação

- **Duas fontes + quorum** (football-data + ESPN): só publica quando concordam; divergência
  vira falha de workflow com e-mail. Zero deploy ruim em 27 atualizações automáticas.
- **Deploy é parada por padrão** (`atualizar.sh` imprime o comando em vez de publicar); o CI só
  publica com jogo novo e gate verde. Silêncio = sucesso, e-mail = problema.
- **Determinismo tem pegadinha de plataforma**: byte-idêntico só na mesma máquina (CI Linux vs
  macOS divergem no último dígito de float por ordem de soma). Convenção: o CI é a fonte dos
  bytes publicados; local reverte ruído de float em vez de commitá-lo.
- **Cache no-store para páginas vivas** curou o "placar velho" no desktop (revisão de 30/jun);
  o arquivo congelado pode voltar a cachear (1h em `/copa2026`).
- **Worker de rotas** (slugs limpos, 301 dos legados, CSP, headers): infraestrutura mínima que
  deu URLs decentes a um site 100% estático.
- **Suite de testes offline do ingest** (15 checks) pagou no primeiro dia de mata-mata
  (placeholders da ESPN quebrariam o run; os fixes de 30/06 e 01/07 saíram com teste antes).
- **GA4 via GTM com spec única em `site.config.json`**: eventos derivados de um arquivo só,
  privacidade decidida no design (nunca texto livre no dataLayer).

## 7. O que faria diferente

- **Odds de partida (1X2 por jogo) como âncora**, em vez de derivar força só do mercado de
  título (Frente 1 do ROADMAP, nunca executada).
- **Ataque e defesa separados** por seleção; backtesting formal em torneios passados antes de
  fixar hiperparâmetros (SLOPE/HA/GOAL_DIV à mão funcionaram, mas não foram otimizados).
- **Planejar a medição de fase no dia 1** (o milestone da véspera do KO existiu por sorte
  operacional: freeze diário + fix da chave a tempo).
- **Completude de ingestão com alarme** (ver aprendizado 7 acima).
- **Sinal de elenco vivo** (`squad_signal.json`) ficou dormente a edição inteira.
- **Leaderboard público mais cedo**: a página Modelos só nasceu na fase C; a transparência do
  "quem está calibrando melhor" merecia acompanhar o torneio desde a estreia.

## 8. Receita para a edição Eleições 2026 (o de-para)

| Copa 2026 | Eleições 2026 |
|---|---|
| Seleção | Candidato (por corrida: presidência, 27 governos, 54 vagas de Senado) |
| Fase de grupos → mata-mata | 1º turno → 2º turno (condicional entre cenários de pareamento) |
| Odds de título / consenso de mercado | Agregador de pesquisas registradas (recência, amostra, instituto, house effects) |
| Opta/Elo (força estrutural) | Fundamentos: aprovação, economia, histórico eleitoral, rejeição |
| Qualitativo curado (dossiês) | Dossiês por candidato/corrida + leitura dos 5 públicos |
| `state.json` (jogos ocorridos) | Pesquisas novas registradas no TSE (ingest com 2+ fontes e quorum) |
| Monte Carlo da chave | Monte Carlo de cenários (incerteza entre institutos, correlação entre UFs) |
| Leaderboard walk-forward | Idem, desde o DIA 1, prevendo a pesquisa seguinte e o resultado final |
| Modelo novo no harness | **Pesquisas sintéticas (vox) como modelo competidor**, nunca no oficial sem vencer |
| Invariantes (somas por fase) | Somas por corrida = 100%, monotonicidade 1º/2º turno, coerência entre páginas |
| Pênaltis = empate (espaço definido) | Espaço definido antes: votos válidos, indecisos, margem de 2º turno |
| Caveats como dado | Idem + banner SINTÉTICO em tudo que vier de persona (fronteira do vox) |

Riscos novos que a Copa não tinha: pesquisas estaduais escassas e irregulares (incerteza honesta
por UF), house effects grandes entre institutos, universo mutável (intenção ≠ voto válido ≠
comparecimento), e a regra de ouro do vox: pesquisa sintética é hipótese, não medição.

## 9. Números da edição

54 commits (27 automáticos do cron) · ~5.400 linhas de Python (stdlib apenas) · 7 páginas geradas ·
50.000 simulações por rodada · 10 modelos no harness · 21 congelamentos diários · 103/104 jogos
medidos · 0 deploys com gate reprovado · dados até 20/07/2026.

## 10. Ponteiros

- [HANDOFF.md](../HANDOFF.md): arquitetura e schemas · [ROADMAP.md](../ROADMAP.md): frentes (F1 segue válida como backlog de motor)
- [docs/automacao-setup.md](automacao-setup.md) · [docs/ga4-setup.md](ga4-setup.md) · [docs/revisao-2026-06-30.md](revisao-2026-06-30.md)
- [src/finalize_scores.py](../src/finalize_scores.py): a medição · [data/model_scores.json](../data/model_scores.json): números finais + trajetória
- [src/make_snapshot.py](../src/make_snapshot.py): o congelamento do arquivo `/copa2026`
- `docs/arquivo/`: handoffs e planos históricos das sessões da edição (movidos da raiz no fechamento)
