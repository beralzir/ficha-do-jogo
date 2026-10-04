# Medição de audiência do Ficha do Jogo: avaliação de legítimo interesse

**Controlador:** Renato Beralzir (site pessoal bera.ia.br/ficha-do-jogo) · **Canal do titular:** privacidade@bera.ia.br
**Data:** 04/10/2026 · **Revisar:** a cada mudança no que o site mede, ou em 04/10/2027, o que vier antes.
**Não é parecer jurídico.** É o registro da avaliação que o controlador faz antes de tratar dado com base em
legítimo interesse, como pede o guia de cookies da ANPD (p. 23). Decisões do Bera, aplicadas na auditoria
tags-bera de 04/10/2026.

## 1. Finalidade

Saber quais páginas e seções do site são lidas, para decidir o que melhorar e o que retirar. Só estatística
agregada de navegação: páginas vistas, rolagem, tempo de aba ativa, seções alcançadas, acordeões abertos,
cliques entre páginas e saídas para outros sites (só o host).

## 2. Necessidade (o mínimo para a finalidade)

| Dado | Fica? | Por quê |
|---|---|---|
| Identificador aleatório do cookie `_ga` | sim | sem ele não há sessão nem contagem de usuário, e ele não carrega nome, e-mail ou documento |
| Página, seção, rolagem, tempo ativo | sim | é a finalidade |
| Host do link externo | sim | mede quanto o site leva às fontes (TSE, licença) |
| URL completa do link do TSE | **não** | traz o `sq` e identifica o candidato consultado |
| Candidato aberto, comparado ou escolhido, e o número | **não** | permitiria inferir opinião política (dado sensível, art. 5º, II, e art. 11) |
| Texto digitado, valores de filtro (espectro, pautas, partido, gênero) | **não** | texto livre pode ter dado pessoal, e filtro de espectro e pauta revela opinião |
| Escolhas e colinha do santinho | **não** | ficam só no `localStorage` do navegador |
| Endereço IP | não armazenado | o GA4 usa para derivar localização aproximada e [não registra nem armazena](https://support.google.com/analytics/answer/12017362) |

## 3. Balanceamento (expectativa do titular e risco)

- **Expectativa:** um site público de estatística eleitoral medir audiência de forma agregada é previsível,
  e a página `/privacidade` explica o que é e o que não é medido.
- **Risco principal:** inferir posição política a partir do que a pessoa consulta. Mitigado na origem: nenhum
  dado de candidato, filtro ou escolha sai do navegador (§2), com testes que reprovam se alguém reintroduzir.
- **O que agravaria e não acontece:** publicidade, perfil comportamental, rastreio entre sites de terceiros,
  cruzamento com outras bases, Google Signals (desligado), vínculo com Google Ads (não há).
- **Pendente de ajuste no painel:** o compartilhamento de dados da conta GA4 com o Google (4 itens) está ligado.
  O guia da ANPD, no exemplo de medição por legítimo interesse (p. 26), pressupõe dado não compartilhado.
  Desligar antes do deploy (ver `docs/ga4-setup.md` §8).

Conclusão: o interesse é legítimo e o risco fica baixo **com** as salvaguardas abaixo. Sem elas (em especial sem
o corte de candidato, filtro e URL do TSE), a conclusão não se sustentaria e o caminho seria consentimento.

## 4. Salvaguardas

1. Corte na origem (§2), guardado por `src/test_tagueamento.py` e pelo teste 7c de `src/test_santinho_pagina.py`,
   ambos com erros plantados e rodando no gate do cron.
2. Medição otimizada do GA4 sem cliques de saída e sem pesquisa no site.
3. Retenção de 2 meses (evento e usuário).
4. Oposição simples: botão "não medir neste navegador" em `/privacidade`. Com ele, o GTM não carrega e nada é
   empurrado. Também valem bloqueadores e o complemento de desativação do Google.
5. Transparência: `/privacidade` linkada no rodapé de toda página, com finalidade, retenção, base legal, como se
   opor e o canal do titular.

## 5. Referências

- LGPD, Lei 13.709/2018: art. 5º, II; art. 7º, IX; art. 10; art. 11; art. 18.
  <https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm>
- ANPD, Guia orientativo: Cookies e proteção de dados pessoais (out/2022), p. 23–26.
  <https://www.gov.br/anpd/pt-br/documentos-e-publicacoes/guia-orientativo-cookies-e-protecao-de-dados-pessoais.pdf>
- Resolução CD/ANPD nº 2/2022 (agentes de tratamento de pequeno porte: canal de comunicação com o titular).
- Google, "IP addresses in Google Analytics": <https://support.google.com/analytics/answer/12017362>
