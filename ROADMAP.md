# ROADMAP — evolução do projeto

Quatro frentes pedidas pelo usuário. Cada uma tem: **gap atual**, **abordagem recomendada**,
**tarefas**, **critérios de aceite** e **risco/esforço**. Sequência sugerida no fim.

> Princípios a preservar (ver `CLAUDE.md`): zero dependência externa no HTML, estático-primeiro,
> invariantes de soma/monotonicidade, determinismo, contrato de dados model↔build.

---

## Frente 1 — Melhorar a qualidade do resultado probabilístico

**Gap:** Poisson independente; rating único por seleção; força derivada de prob. de título (log-linear,
com leve dupla contagem do sorteio); `qual` manual; sem calibração formal. (Ver HANDOFF §6.)

**Abordagem recomendada (ordem de maior retorno):**
1. **Trocar o motor de gols por Dixon-Coles / Poisson bivariado** — adiciona correlação de baixos placares;
   melhora placares exatos e mercados derivados (over/under, ambas marcam). Mantém λ vindo da força.
2. **Usar odds de partida (match odds), não só de título** — quando houver mercado 1X2 por jogo (ou via
   provedor), calibrar λ para reproduzir o 1X2 do mercado por confronto. Remove a aproximação título→força.
3. **Separar ataque e defesa** por seleção (dois ratings) em vez de um só — capta perfis (Equador defende, Holanda equilibra).
4. **Calibração e backtesting**: rodar o motor sobre Copas/Eurocopas passadas e medir **Brier score** e
   **log-loss**; ajustar `SLOPE`, `GOAL_DIV`, `HA`, pesos do ensemble por otimização, não à mão.
5. **Shrinkage bayesiano** para a cauda (minnows com poucos dados) e para o `qual`.
6. **Tornar `qual` data-driven**: derivar de uma fonte estruturada (lesões, minutos, xG de clube) em vez de texto curado.
7. **Mando de campo mais fino**: por sede (altitude Cidade do México/Guadalajara, fuso, distância de viagem),
   não um `HA` único.

**Critérios de aceite:** Brier/log-loss documentados e ≤ baseline atual em validação histórica;
1X2 do modelo dentro de ~1–2pp do mercado de partida onde existir; somas/monotonicidade intactas;
processo de calibração reprodutível (script + relatório).

**Risco/esforço:** médio-alto. Risco principal: overfitting a poucos torneios; mitigar com validação cruzada temporal e mantendo o mercado como âncora.

---

## Frente 2 — Atualização contínua durante a Copa

**Gap:** dados são um snapshot (1–3/jun). Nada se atualiza com resultados/lesões/convocações.

**Abordagem recomendada:** uma **camada de estado** (resultados já ocorridos) + **re-simulação condicional**
do que falta. Fixa jogos jogados, recomputa grupos e chave, e roda o Monte Carlo só sobre o restante.
Agendar a re-execução (ex.: cron / GitHub Actions / serviço) após cada rodada de jogos.

> O usuário pediu para **NÃO** escolher a fonte aqui — abaixo ficam só os **critérios** para o Claude Code
> avaliar e decidir (pesquisar preço/cobertura atuais na hora da implementação).

**Critérios para a fonte de dados ao vivo (checklist de avaliação):**
- **Cobertura**: fixtures + placares ao vivo da Copa 2026; idealmente escalações, cartões, lesões, e
  estatísticas (xG, finalizações) por jogo.
- **Latência/atualização**: tempo real ou near-real-time; suporte a **webhook/push** é melhor que só polling.
- **Limites e custo**: rate limits compatíveis com a frequência desejada; plano gratuito/barato cabe no escopo de um bolão.
- **Licença/ToS**: permite uso derivado e exibição; atenção a cláusulas sobre **apostas/odds** (alguns proíbem).
- **Histórico**: dados de torneios passados disponíveis (necessário para o backtesting da Frente 1).
- **Estabilidade/SLA e formato** (JSON limpo, IDs estáveis de time/jogo).
- **Mapeamento de nomes**: precisa casar com as chaves EN do projeto (criar uma tabela de-para).

**Tarefas:** abstrair um `DataSource` (interface) → adaptador concreto para a fonte escolhida → cache local
versionado (`data/live/`) → job agendado → camada de re-simulação condicional → invalidação/rebuild do HTML.

**Critérios de aceite:** após cada rodada, `results.json` reflete os jogos já ocorridos (probabilidades
condicionais corretas: time eliminado = 0% dali pra frente; somas recoerentes); pipeline roda sem intervenção;
fonte trocável sem reescrever o motor (graças à interface).

**Risco/esforço:** médio. Riscos: ToS da fonte (especialmente p/ bet), de-para de nomes, fuso/horário dos jogos.

---

## Frente 3 — Tabela e chave que se atualizam (mobile-first)

**Gap:** não há visão de **classificação dos grupos** nem **bracket** que evoluam com os resultados; o HTML
atual é desktop-first em algumas seções (tabelão 48×, grids de 2 colunas).

**Abordagem recomendada:**
- **Standings por grupo**: derivar pontos/saldo/gols dos jogos já ocorridos (mesmos critérios de desempate do
  motor) + projeção das posições finais a partir das simulações.
- **Bracket interativo**: usar o mapeamento de `structure.json` (já tem R32→final e Anexo C). Slots preenchem
  conforme os grupos fecham; jogos de mata-mata mostram o confronto real quando definido, e o provável antes.
- **Mobile-first de verdade**: o usuário vê no **celular**. Repensar o tabelão (hoje rola horizontal) — opções:
  cards por seleção, colunas colapsáveis, ou uma visão "fase a fase". Bracket em mobile costuma virar
  acordeão vertical / scroll horizontal com snap. Considerar **PWA** (instalável, offline) e gestos.

**Critérios de aceite:** em viewport de ~390px tudo é legível e usável sem zoom; standings e bracket batem
com os resultados inseridos; a chave reflete corretamente as regras (2 + 8 melhores terceiros);
performance boa em celular (HTML continua leve, idealmente sem deps).

**Risco/esforço:** médio. Depende da Frente 2 para os dados ao vivo (pode começar com entrada manual de placares).

---

## Frente 4 — Redesign de design / UX / layout

**Gap:** UI funcional mas densa, tema "engenharia"; pensada para desktop; precisa de uma passada de design/UX,
sobretudo mobile.

**Abordagem recomendada:** usar os plugins/skills **`huashu-design`** e **`open-design`** no Claude Code
(não disponíveis neste ambiente — não pude verificá-los daqui; tratá-los como as ferramentas de design da etapa).
Partir do **`docs/DESIGN_BASELINE.md`** (tokens, componentes, breakpoints e estados do UI atual) como ponto de partida.

**Metas de UX:** mobile-first; hierarquia visual mais clara (favoritos, zebras, valor modelo×mercado);
acessibilidade (contraste AA, navegação por teclado, foco visível, ARIA na gaveta/calculadora);
dark/light já existem (manter como tokens); micro-interações sóbrias.

**A preservar no redesign:** estático-primeiro, zero dependência externa, o contrato de dados e os
invariantes; idealmente manter as duas paletas como design tokens.

**Critérios de aceite:** Lighthouse mobile bom (perf/acessibilidade); fluxos principais (ver favoritos,
abrir dossiê, calcular confronto, ver grupo/chave) confortáveis no celular; design tokens documentados.

**Risco/esforço:** médio. Risco: introduzir dependências/JS pesado que quebrem o requisito de "abrir em qualquer lugar".

---

## Sequência sugerida
1. **Frente 2** (camada de estado + fonte de dados) — destrava o "ao vivo" de que as outras dependem.
2. **Frente 3** (tabela + chave ao vivo, mobile-first) — usa os dados da Frente 2.
3. **Frente 1** (qualidade do modelo + backtesting) — pode correr em paralelo; o backtesting precisa do histórico (vem junto da Frente 2).
4. **Frente 4** (redesign) — por último ou em paralelo à 3, sobre a base estável.

> Nota sobre **bet**: se for usar para apostar de verdade, a Frente 1 (calibração/backtesting) e a
> licença da fonte (Frente 2) são pré-requisitos — sem calibração medida, não há edge comprovado; e
> jogo envolve risco financeiro real.
