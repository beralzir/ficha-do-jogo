# Roteiro de QA local · Fase C (públicos, hardening, synths)

> Rode com `wrangler dev` na 8787 (`.claude/launch.json`, config `ficha-do-jogo`).
> **Nada disto está no ar.** Branch `eleicoes-fase-c`, 15 commits à frente do
> `origin/main`, rebaseada sobre a última publicação do robô (31/08 17:43 UTC).

## O que mudou nesta fase, em uma linha cada

| Bloco | O que você vai ver |
|---|---|
| C0-c | nada visível: hardening do pipeline (gate de entrada, alarme de saída, kill switch) |
| C1 | **aba Públicos nova**: índice com 5 cartas + 5 fichas |
| C3 | **página Modelos**: 2 competidores marcados SINTÉTICO (MOCK) e um aviso |

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

## 3. O que NÃO pode ter mudado (regressão)

- [ ] `/` e `/presidencial`: números iguais aos do site no ar hoje. O forecast
      oficial **não** deve ter mudado por causa desta fase (as `races` foram
      conferidas byte a byte, mas confira com o olho).
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
3. **`--ac` no tema claro** dá 3,9:1 sobre o card, abaixo do 4,5:1 que texto
   pequeno exige. Dívida do design system, não desta fase; o selo novo contorna
   separando texto de borda, mas outros usos de `--ac` como texto no light
   merecem uma passada do cão-guia.

## 5. Se aprovar

O deploy é **pausa dura** e depende de você dizer com todas as letras. O merge na
`main` tem o mesmo peso: o cron diário publica sozinho no ciclo seguinte, então
mergear equivale a autorizar a publicação.
