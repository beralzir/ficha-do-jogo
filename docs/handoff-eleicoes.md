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
  318 senador (validador trava nesses números; mudou o raw, atualize junto).

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
- `situacao` vem verbatim do TSE ("Deferido", "Aguardando julgamento", "Renúncia"…).
  `concorrendo` é flag derivada: totalização "Concorrendo" e situação fora de
  {Renúncia, Cancelado, Indeferido seco, Pedido não conhecido}; **sub judice conta como
  concorrendo** (é como aparece na urna até o TSE decidir).
- Warns conhecidos do validador (29/08): registro duplicado da mesma pessoa (GOV-MT nº 36,
  SEN-SP nº 144) e nº disputado sub judice (GOV-BA nº 27, SEN-PI nº 700). São estados reais
  do registro em fluxo, não bugs.

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
