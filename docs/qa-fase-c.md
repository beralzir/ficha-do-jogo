# Roteiro de QA local · Fase C (públicos, hardening, synths)

> Rode com `wrangler dev` na 8787 (`.claude/launch.json`, config `ficha-do-jogo`).
> **Nada disto está no ar.** 21 commits à frente do `origin/main`, rebaseados sobre a
> última publicação do robô (18/09, commit `ca3684b`).
>
> **ATUALIZADO EM 18/09:** este QA agora acumula DUAS coisas. A Fase C, que nunca foi
> validada, e a correção do incidente da presidencial (bloco D, seção 0 abaixo). A
> seção 3 mudou: o forecast oficial **mudou** desta vez, de propósito, e o roteiro
> antigo mandava conferir o contrário.

## O que mudou nesta fase, em uma linha cada

| Bloco | O que você vai ver |
|---|---|
| C0-c | nada visível: hardening do pipeline (gate de entrada, alarme de saída, kill switch) |
| C1 | **aba Públicos nova**: índice com 5 cartas + 5 fichas |
| C3 | **página Modelos**: 2 competidores marcados SINTÉTICO (MOCK) e um aviso |
| D (incidente) | **gráfico da presidencial volta a 9 meses** e a base ganha 495 pesquisas |

## 0. Correção do incidente (o que é novo em 18/09)

Contexto em uma frase: em 04/09 a Wikipédia quebrou o 1º turno da presidencial em
subpáginas, o ingest passou a ler só a página-mãe, e o site publicou por 14 dias um
forecast sobre 58 pesquisas em vez de 510, sem nenhum alarme disparar.

- [ ] `/presidencial`: o gráfico "Evolução em 2026" tem **9 meses no eixo (jan a set)**.
      Se aparecerem só "ago" e "set", o build não pegou a correção.
- [ ] O cabeçalho diz **147 pesquisas de 22 institutos** (no ar hoje são 46 de 17).
- [ ] `/uf-ac`: o Senado do Acre deixou de estar com **1 pesquisa de agosto de 2025**
      e agora tem 20, de 11 institutos. É a corrida que mais se move nesta rodada, e é
      a que mais merece o seu olho, porque no dado no ar três candidatos diferentes
      estavam colapsados no mesmo registro do TSE.
- [ ] `/modelos`: o leaderboard saiu de "sem comparações suficientes" para **16 freezes
      e 724 comparações**. Era o objetivo do harness desde a Fase B.

## 1. Aba Públicos (o conteúdo novo)

- [ ] `/publicos`: as 5 cartas aparecem lado a lado, com radares **visivelmente
      diferentes** entre si (Lulistas e Independentes são quase espelhos).
- [ ] Clique em cada uma das 5 fichas. Confira em pelo menos duas:
  - [ ] O radar tem 6 eixos rotulados e o polígono não vira uma linha.
  - [ ] A ressalva **"Não é pesquisa eleitoral"** está visível na página, não
        escondida no rodapé.
  - [ ] A fonte aparece como **"Painel sindicalizado de consumo de mídia, base
        2025"**. Se em algum lugar aparecer TGI, Ibope, Kantar ou Almap, é bug.
  - [ ] Os rótulos de mídia estão **sem a notação da fonte**: deve ler "Jornal
        Online", nunca "Jornal Online: Leu-U7d".
  - [ ] **Nenhum recorte por estado** em lugar nenhum (a base não sustenta).
- [ ] Alterne o tema (botão ☾/☀) numa ficha: dark e light legíveis.
- [ ] Reduza a janela para largura de celular: nada corta nem rola na horizontal.

## 2. Página Modelos (a decisão editorial mais delicada da fase)

- [ ] `/modelos`: o aviso **"o campo sintético ainda não rodou"** aparece antes
      da tabela.
- [ ] `synths_solo` e `synths_mix` aparecem com o selo **SINTÉTICO (MOCK)**,
      tracejado, e com "sem dado ainda" no erro médio.
- [ ] O parágrafo explica que **nada do que eles produzem entra no forecast**.
- [ ] Os 5 modelos reais continuam com suas comparações normais.

> Se você achar que a linha sintética confunde mesmo com o aviso, dá para
> publicar sem ela: os competidores ficam no código, desligados, até o campo real.

## 3. O que pode e o que NÃO pode ter mudado (regressão)

O título desta seção mudou em 18/09. Antes era "o que NÃO pode ter mudado", porque a
Fase C não tocava no forecast. A correção do incidente toca, então aqui agora tem o
movimento ESPERADO, com número, e o critério de quando parar.

- [ ] `/` e `/presidencial`: os números **mudaram**, e pouco, de propósito. Esperado:
      Lula 43% (-0,34pp), Flávio Bolsonaro 39% (-0,72pp), e **P(eleito) idêntico ao do
      ar, 53% contra 47%**. Se a presidencial tiver se movido vários pontos, algo está
      errado e é para me chamar em vez de aprovar.
      Por que mudou tão pouco depois de recuperar 483 pesquisas: o agregador pondera
      por recência com meia-vida de 21 dias, então o histórico recuperado vale 10,4%
      do peso. O que estava quebrado era a série histórica, não o número de hoje.
- [ ] As outras 53 corridas: a mediana do movimento é **0,00pp**. Só SEN-AC passa de
      5pp (12,05pp), e só SEN-PI (2,84pp) e GOV-MG (2,26pp) passam de 2pp.
- [ ] `/uf-sp` e `/uf-rr`: continuam normais.
- [ ] `/copa2026/` responde, e `/dashboard` ainda dá 301 para o arquivo da Copa.

## 4. Decisões que ficaram com você, e que eu não posso resolver

1. **Norma do TSE sobre IA em 2026** (`[a verificar]`): é o único item capaz de
   bloquear a publicação da parte sintética. O site não é propaganda eleitoral,
   o que provavelmente o deixa fora do escopo, mas publicar "pesquisa sintética"
   em campanha pede a leitura da norma vigente.
2. **Escopo do `CLOUDFLARE_API_TOKEN`**: se for token de conta ampla em vez de
   "Edit Cloudflare Workers", o raio de dano de um vazamento passa muito além
   deste site. Não dá para verificar do meu lado.
3. **17 pesquisas com candidatos colapsados no mesmo registro do TSE** seguem no dado
   (SEN-MA 6, SEN-MG 4, SEN-RN 3, SEN-SP 2, GOV-BA 1, GOV-RJ 1). É dívida pré-existente,
   não foi corrigida aqui para não virar drive-by, e a presidencial não está entre elas.
4. **O ingest sobrescreve o `polls.json` inteiro** e não preserva a linha sintética, então
   o synth do C3 some a cada rodada. Hoje é inofensivo porque é mock; quando o campo real
   rodar, vira perda silenciosa.
5. **`--ac` no tema claro** dá 3,9:1 sobre o card, abaixo do 4,5:1 que texto
   pequeno exige. Dívida do design system, não desta fase; o selo novo contorna
   separando texto de borda, mas outros usos de `--ac` como texto no light
   merecem uma passada do cão-guia.

## 5. Se aprovar

O deploy é **pausa dura** e depende de você dizer com todas as letras. O merge na
`main` tem o mesmo peso: o cron diário publica sozinho no ciclo seguinte, então
mergear equivale a autorizar a publicação.
