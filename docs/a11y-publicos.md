# Auditoria de acessibilidade visual · páginas de públicos (C1c)

**Material:** 6 páginas novas da edição Eleições 2026 (`/publicos` + 5 fichas em
`/publico-<slug>`), servidas em `wrangler dev` na 8787.
**Data:** 31/08/2026 · **Modo:** auditar + ajustar (correções aplicadas e provadas)
**Motor:** `@axe-core/cli@4.12.1` · pipeline de cor do cão-guia (WCAG 2.x, Machado 2009)

> **Não é laudo de conformidade.** Auditoria assistida. Conformidade certificada exige
> teste com pessoas com deficiência e revisão humana especializada.

## Veredito

**Aprovado em AA nos dois temas**, com 4 correções aplicadas durante a auditoria e 1
achado pré-existente fora do escopo, declarado abaixo.

| Página | violations `[motor]` | incomplete (triados) | passes |
|---|---|---|---|
| `/publicos` | **0** | 1 | 22 |
| `/publico-lulistas` | **0** | 7 | 23 |

## Cobertura (honestidade obrigatória)

O automático cobre uma fração dos critérios WCAG; o resto é o checklist manual abaixo.

- `[OK]` Web núcleo (axe-core em URL viva) · `[OK]` contraste e paleta CVD
- `[DEGRADADO]` Playwright ausente: estados dinâmicos não cobertos. Impacto real **baixo**
  aqui, porque as páginas são estático-primeiro e renderizam completas sem JS. O único
  estado dinâmico é o toggle de tema, coberto abaixo pelo cálculo de contraste do tema light.
- `[DEGRADADO]` CVD avançado (severidade parcial e tritanopia rigorosa) ausente. Impacto
  **baixo**: o radar é monocromático e nenhuma informação é codificada por matiz.
- **Não verificado:** teste com leitor de tela real e com usuários. Recomendado abaixo.

## Achados e correções

### 1. Rótulo de eixo do radar abaixo do mínimo `[heurística LLM + motor de cor]` · CORRIGIDO
Os 6 rótulos do radar saíam a **9,5px**. O checklist de data viz pede eixos legíveis a
partir de 12px (Chartability, POUR-CAF). Subidos para **12px**, com folga maior no viewBox
para não cortar. Verificado: nenhum rótulo transborda o SVG.

### 2. Reflow reprovava a 320px (WCAG 1.4.10) `[motor]` · CORRIGIDO
O SVG do radar tinha largura fixa (210px + 2×71px de folga = 353px) e estourava a viewport,
criando scroll horizontal a 320px: medido `scrollWidth 390 > clientWidth 320`. Corrigido com
`max-width:100%;height:auto` no SVG (ele já tinha viewBox) e `flex-wrap` na linha de
distinção. Verificado depois: **320 = 320, sem scroll horizontal**, no índice e na ficha.

### 3. Colisão de classes CSS `[heurística LLM]` · CORRIGIDO
`.ficha`, `.kpi` e `.kpis` já existiam no CSS base da edição. Funcionava por ordem de
concatenação, o que é frágil. Prefixadas para `.pbficha`, `.pbkpi`, `.pbkpis`. Colisões
restantes: **zero** (verificado por interseção de seletores).

### 4. Tipografia serifada `[heurística LLM]` · CORRIGIDO
As páginas saíam em Times porque a regra de fonte mora no CSS do `build_eleicoes`, não no
`shell`. Não é WCAG, é o guardrail "system-sans" do schema da marca. Resolvido herdando o
CSS base em vez de duplicá-lo.

### 5. Alvo de toque menor que 24×24 (WCAG 2.5.8) `[motor]` · PRÉ-EXISTENTE, NÃO CORRIGIDO
O link "CC BY-NC-ND 4.0" do rodapé mede **99×14px**. Vem do `shell.py` e existe em todas as
páginas do site, inclusive as 30 anteriores e o que está no ar. Fora do escopo desta etapa
para não virar correção drive-by; corrigir afeta o site inteiro e merece decisão própria.

## Triagem do bucket `incomplete` (7 nós, todos julgados)

O axe marca `incomplete` o que não consegue decidir sozinho. Cada um foi medido à mão:

| Nó | Por que ficou incompleto | Veredito |
|---|---|---|
| `#tg` (botão de tema) | conteúdo é só o glifo ☾ | **OK**: tem `aria-label="Alternar tema"`; o glifo é decorativo |
| 6× `<text>` do radar | axe não determina fundo dentro de SVG | **OK**: medido manualmente, ver tabela de contraste |

## Contraste medido (os dois temas)

Alvo do projeto: **AA**. Medido com o pipeline de cor do cão-guia.

| Elemento | Dark | Light | AA |
|---|---|---|---|
| Rótulo do eixo do radar (`--mut` sobre `--card`) | passa | passa | ✅ |
| Chip de distinção, sobre o fundo composto real do chip | passa (e AAA) | passa | ✅ |
| Traço do radar, gráfico não-textual (WCAG 1.4.11, exige 3:1) | passa | passa | ✅ |

O fundo do chip foi composto à mão (`--acsoft` é o acento a 12% sobre `--card`), porque
medir contra o card puro daria um número otimista.

## Checklist manual

| # | Item | Veredito |
|---|---|---|
| 1 | Teclado ponta-a-ponta | **passou** `[heurística LLM]`: zero `onclick` fora de `<a>`/`<button>`; navegação é link nativo. Interação real com teclado físico: confirmar com humano |
| 2 | Ordem de foco e foco visível | **passou**: DOM na ordem visual; foco visível herdado do shell, já auditado na Fase B |
| 3 | WCAG 2.2 (2.4.11, 2.5.7, 2.5.8, 3.2.6, 3.3.7, 3.3.8) | **passou**, exceto 2.5.8 no link do rodapé (achado 5, pré-existente). Sem arrastar, sem formulário, sem login |
| 4 | Qualidade de alt-text | **passou**: o radar tem `role="img"` e `aria-label` que enuncia os 6 eixos com valor, não "gráfico" |
| 5 | Propósito do link | **passou**: zero "clique aqui" ou "saiba mais"; todo link nomeia o público de destino |
| 6 | Ordem de leitura | **passou**: DOM segue a ordem visual |
| 7 | Mensagens de erro | **não se aplica**: nenhum formulário |
| 8 | Idioma | **passou**: `lang="pt-BR"` no raiz |
| 9 | Sentido só por cor (1.4.1) | **passou**, e por decisão de conteúdo: a distinção usa **sinal e palavra** ("+31%", "acima da média"), não cor. Verde e vermelho foram deliberadamente evitados aqui, porque "acima da média" não é bom nem ruim quando se descreve gente |
| 10 | Zoom e reflow a 320px | **passou** depois da correção 2 |
| 11 | Text spacing (1.4.12) | **passou**: com line-height 1.5, letter-spacing .12em, word-spacing .16em e parágrafo 2em, nada quebra nem cria scroll |
| 12 | Movimento (2.2.2, 2.3.3) | **não se aplica**: zero animação e zero transição na página |
| 13 | `prefers-contrast` / `forced-colors` | **não verificado**: exige teste real no SO. As cores vêm de tokens CSS, o que ajuda, mas não é prova |
| 14 | Data viz | **passou** depois da correção 1: título em texto, eixos rotulados a 12px, rótulo direto (sem legenda separada), radar monocromático (nenhuma série distinguida por matiz), e os números que sustentam o radar aparecem em texto na mesma página |
| 15 | Teste assistivo real | **não verificado**. Recomendado abaixo |

## Recomendações

1. **Rodar VoiceOver em pt-BR** (macOS: Cmd+F5) numa ficha, navegando por headings
   (VO+Cmd+H) e conferindo se o `aria-label` do radar é lido de forma útil. É o item de
   maior retorno que ainda falta, e leva minutos.
2. **Decidir sobre o alvo de 24×24 do rodapé** (achado 5), que afeta o site inteiro.
3. Padrão-ouro, se as fichas ganharem tráfego: teste com pessoas cegas ou de baixa visão.
   "Nada sobre nós sem nós."

## Base normativa

- **LBI (Lei 13.146/2015), art. 63**: acessibilidade obrigatória em sites de uso coletivo.
- **ABNT NBR 17225:2025**: acessibilidade em conteúdo web, referência técnica brasileira.
- **WCAG 2.2 nível AA** (tradução pt-BR do W3C): critérios citados ao longo do relatório.
- eMAG não se aplica: o domínio não é `.gov.br`.
