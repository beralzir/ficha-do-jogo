# HANDOFF · Ficha do Jogo · Eleições 2026

> Documento vivo da edição (começado na etapa B3, 29/08/2026). O HANDOFF.md da raiz é da
> edição Copa (arquivada); este cobre a v2. Plano da fase: `docs/plano-fase-b-eleicoes.md`.
> Fontes e decisão de ingestão: `docs/fontes-eleicoes.md`.

## Corridas da edição

55 corridas: `PRES` (presidente, BR) + `GOV-{UF}` (27) + `SEN-{UF}` (27, **2 vagas cada, sem
2º turno**; o eleitor vota em 2 nomes). Datas: 1º turno 04/10/2026, 2º turno 25/10/2026.

## Pipeline de dados (estado na B3)

```
[navegador real] DivulgaCandContas REST ──▶ data/live/candidatos_raw.json  (dump verificado)
                                                    │ src/build_eleicoes_structure.py (offline, determinístico)
                                                    ▼
                                      data/eleicoes2026_structure.json
                                                    │ src/test_eleicoes_structure.py (gate)
                                                    ▼
[Wikipédia + âncora TSE]  ──▶ data/live/polls.json  (B4: ingest do agregador)
```

- **403 Akamai**: cdn.tse.jus.br e a API do TSE recusam clientes não-navegador (TLS
  fingerprint; headers não bastam). A captura do raw foi feita com o navegador do painel
  (fetch same-origin na API) e transferida byte-exata (form POST top-level para receptor
  local; SHA-256 conferido). Refresh do raw = repetir a captura; testar o CI na B8.
- Contagens da captura 29/08 batem com o zip oficial: 13 presidente, 198 governador,
  318 senador. Captura vigente: **25/09**, 14 presidente, 201 governador, 318 senador
  (validador trava nesses números; mudou o raw, atualize junto). Detalhes na seção
  "Recaptura do raw" abaixo.

### Recaptura do raw (procedimento, refeito em 25/09/2026)

1. Abrir `https://divulgacandcontas.tse.jus.br/divulga/` no navegador embutido do painel
   e, na própria página, fazer `fetch` same-origin em
   `/divulga/rest/v1/candidatura/listar/2026/{UE}/20322002026/{cargo}/candidatos`:
   `BR/1`, depois `{UF}/3` e `{UF}/5` nas 27 UFs em ordem alfabética (55 chamadas).
2. Mapeamento das colunas de `c` (na ordem da API, que vem por nome de urna):
   `id`, `nomeUrna`, `nomeCompleto`, `numero`, `partido.sigla`, `descricaoSituacao`,
   `descricaoTotalizacao`. Objeto `{fetched_at, source, pres_gov, senado}` serializado
   com `JSON.stringify` compacto, sem quebra de linha no fim.
3. SHA-256 calculado na página (`crypto.subtle.digest`) e bytes transferidos por form POST
   top-level para um receptor local só-stdlib (registrado no `.claude/launch.json` local e
   subido por `preview_start`, nunca por Bash), que grava os bytes decodificados em
   binário e recalcula o SHA-256. Os dois hashes têm de bater antes de copiar o arquivo
   para `data/live/candidatos_raw.json`.
4. `python3 src/build_eleicoes_structure.py` e `python3 src/test_eleicoes_structure.py`
   (a trava de contagens reprova até ser atualizada: é a prova de que ela morde).
5. **Recasar o polls.json existente** contra a structure nova, sem rede, com o matcher do
   próprio ingest (`build_matcher` + `aliases.json`) e a mesma serialização (`indent=1`).
   Candidato novo passa a casar e candidato renomeado pode deixar de casar. O PR tem de
   levar polls, results e páginas regenerados: o `check_movimento` do CI compara com o
   results.json da HEAD, e sem isso o alarme dispara no primeiro cron depois do merge.
   ```python
   import json, sys; sys.path.insert(0, "src"); import ingest_polls as ip
   doc = json.load(open(ip.OUT, encoding="utf-8"))
   st = ip.load_json(ip.STRUCT, None); al = ip.load_json(ip.ALIASES, {"institutos": {}, "candidatos": {}})
   for p in doc["polls"]:
       if p.get("sintetico"): continue
       m = ip.build_matcher(st["races"][p["race"]], al)
       for n in p["numeros"]: n["sq"] = m(n["alias"])[0]
       if p.get("par_segundo_turno") is not None:
           p["par_segundo_turno"] = sorted(n["sq"] for n in p["numeros"] if n["sq"] is not None)
   open(ip.OUT, "w", encoding="utf-8").write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
   ```
6. Conferir no `consulta_cand_complementar_2026.zip` cada entrada de
   `EXCECOES_SUB_JUDICE` (builder): se a situação de urna deixou de ser a da fonte, a
   entrada sai. O builder já PARA sozinho se a situação da API mudar ou se o sq sumir.
7. `./atualizar_eleicoes.sh`. Movimento grande que vem da recaptura (candidato que sai da
   disputa) é liberado com `ALARME_OK=1` só depois de conferido um a um.

**Captura de 25/09/2026:** SHA-256 `b65393f689e034a5ac7a54f752c6c1ac9928a6bd070da3f56160c6e0c983c98e`,
54.780 bytes, 55 corridas, 533 candidaturas (14/201/318), zero erro HTTP, zero campo nulo.
Mudanças contra 29/08: entram 5 substitutos (Leonardo Avalanche na PRES, sq
280002554479; Aécio Neves no SEN-MG; Ruth Reis no GOV-PA; Godeiro Linharess no GOV-RN;
Siqueira Campos Jr no GOV-TO); 17 candidaturas passam a `concorrendo=false` (13
Indeferido, 3 Renúncia, 1 Pedido não conhecido) na API, entre elas Pablo Marçal (sq
280002553884, mantido na structure com `concorrendo=false`) e Arruda no GOV-DF, que segue
concorrendo pela exceção sub judice abaixo; 5 nomes de urna mudaram (dois deles perderam
o "Bolsonaro"); some Gustavo Galassi (SEN-MG, 130002553354).

**Conferência independente contra os dados abertos** (lidos no navegador embutido em
`cdn.tse.jus.br`, só as linhas de cargo 1, 3 e 5, transferidas com SHA-256):
- `consulta_cand_2026.zip`, geração 25/09/2026 12:31:26: 534 candidaturas (14/201/319).
  São as mesmas 533 da API, com número, cargo e UE iguais, mais Galassi, que o zip ainda
  traz e a API de listagem deixou de mostrar. Nomes de urna diferem só no apóstrofo (2).
- `consulta_cand_complementar_2026.zip`, mesma geração: Galassi está em RENÚNCIA e
  substituído (Aécio aponta para ele em SQ_SUBSTITUIDO); Avalanche substitui Marçal. A
  regra `concorrendo` coincide com `ST_CANDIDATO_INSERIDO_URNA` em 532 das 533
  candidaturas da API. A exceção é Arruda: julgamento "INDEFERIDO" (a API mostra
  "Indeferido"), mas situação na urna "INDEFERIDO EM PRAZO RECURSAL OU COM RECURSO",
  inserido na urna e com votos "Anulado sub judice". **Decisão do Bera (25/09): manter
  Arruda como sub judice por ora**, pela exceção explícita `EXCECOES_SUB_JUDICE` do
  builder (fonte e data na entrada, nota no `meta.notes`, WARN no validador a cada
  rodada). Com ela, a flag coincide com a urna nas 533. Tirá-lo teria levado Celina a
  56,7% com banda de ±14pp, porque o motor renormaliza a média entre quem concorre mas
  mede a dispersão nos shares que ainda incluem quem saiu; e teria tirado a métrica da
  hipótese h-2026-09-25-17 (share publicado de Arruda).

## Schema: eleicoes2026_structure.json

```
{ "meta": { edition, election_id: 20322002026, source, source_fetched_at,
            dates: {turno1, turno2}, notes[] },
  "races": {
    "PRES" | "GOV-UF" | "SEN-UF": {
      cargo: "presidente"|"governador"|"senador",
      uf: "BR"|sigla, seats: 1|2, two_round: bool,
      candidates: [ { sq, urna, nome, numero, partido, situacao, concorrendo } ]
} } }
```

- **`sq` (SQ_CANDIDATO do TSE) é a chave canônica** de candidato em toda a edição
  (equivalente ao nome EN das seleções na Copa). Nome de exibição fica na camada de view.
- `situacao` vem verbatim do TSE ("Deferido", "Aguardando julgamento", "Renúncia",
  "Pendente de julgamento" (substituição em julgamento, apareceu em 25/09)…).
  `concorrendo` é flag derivada: totalização "Concorrendo" e situação fora de
  {Renúncia, Cancelado, Indeferido seco, Pedido não conhecido}; **sub judice conta como
  concorrendo** (é como aparece na urna até o TSE decidir). Exceção explícita e datada:
  `EXCECOES_SUB_JUDICE` no builder, para quem a API já dá "Indeferido" mas a urna ainda
  traz em prazo recursal (hoje só Arruda, GOV-DF). `situacao` continua verbatim.
- Warns conhecidos do validador (29/08): registro duplicado da mesma pessoa (GOV-MT nº 36,
  SEN-SP nº 144) e nº disputado sub judice (GOV-BA nº 27, SEN-PI nº 700). São estados reais
  do registro em fluxo, não bugs. Na captura de 25/09 os quatro se resolveram: zero warn.

## Schema: data/live/polls.json (v1)

```
{ "schema_version": 1, "updated_at": ISO|null,
  "polls": [ {
    id: "instituto-UF-campoFim-cargo[-cenário]",   // interno, estável
    race: "PRES"|"GOV-UF"|"SEN-UF",
    instituto: "Quaest",              // nome canônico (tabela de aliases, B4)
    contratante: str|null,
    tse_protocolo: "TO-02161/2026"|null,  // âncora; null = ainda não casado com o PesqEle
    campo_ini: "AAAA-MM-DD", campo_fim: "AAAA-MM-DD", divulgacao: "AAAA-MM-DD"|null,
    amostra: int|null, margem_pp: float|null, metodo: str|null,
    cenario: "estimulada"|"espontanea"|"segundo_turno",
    par_segundo_turno: [sq, sq]|null,     // só em cenário segundo_turno
    base: "normalizada_100"|"bruta_2votos"|"validos"|"totais"|"desconhecida",
    numeros: [ { sq: int|null, alias: "NOME COMO SAIU", pct: float } ],
    indefinidos_pct: { indecisos, branco_nulo, ns_nr }|null,
    fonte: { tipo: "wikipedia"|..., url, revid|null, acesso },
    flags: ["senado_2votos", ...]
  } ] }
```

- **`pct` é ponto percentual como divulgado** (dado de intenção de voto), NÃO fração [0,1].
  A convenção de fração [0,1] do repo vale para PROBABILIDADES de saída do modelo; a
  conversão/normalização acontece no motor, guiada por `base`.
- **Senado (2 votos por eleitor)**: institutos divulgam ora soma bruta >100%
  (`bruta_2votos`, ex. Datafolha RJ 116%), ora consolidado normalizado
  (`normalizada_100`, ex. Quaest/RTBD). Detectar e registrar a base POR pesquisa; nunca
  misturar bases sem re-normalizar.
- `numeros[].sq` null = candidato ainda não casado com o structure (vai para a fila de
  aliases; linha nunca é descartada em silêncio).

## Invariantes da edição (espelham as da Copa)

1. Σ P(eleito) = 100% por corrida (200% nas de Senado, 2 vagas) na saída do modelo.
2. Monotonicidade: P(eleito) ≤ P(vai ao 2º turno) onde houver 2º turno.
3. Determinismo: seed 42, iterações ordenadas; builders offline reproduzíveis byte a byte.
4. Espaço de medição definido ANTES de medir (aprendizado da Copa, §5.4 da retrospectiva).
5. Corrida sem pesquisa: prior de alta incerteza DECLARADO na saída, nunca 50/50 silencioso.
6. HTML estático-primeiro e zero-dep (exceção GTM), como na Copa.

## Pendências conhecidas

- Tabela de aliases (instituto e candidato) nasce na B4 (`data/eleicoes/aliases.json`).
- Match pesquisa↔registro TSE: chave (instituto, UF, cargo, datas ±1 dia); colisões vão
  para fila manual (ver fontes-eleicoes.md §De-para).
- CI vs 403 do TSE: teste na B8; fallback documentado em fontes-eleicoes.md.
