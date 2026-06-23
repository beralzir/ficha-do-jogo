# Baseline — forecast pré-torneio (IMUTÁVEL)

`forecast_pretorneio.json` é uma **cópia byte-idêntica** do `data/wc2026_results.json`
congelada em **2026-06-08** (janela pré-torneio; Copa começa 11/jun), para servir de
**base de comparação previsto × realizado**.

- Origem: `data/wc2026_results.json` (`meta.generated = 2026-06-03`, N=50.000, seed 42).
- Invariantes verificados na cópia: somas (Σtítulo=100% … Σavançar=3200%) e **0 violações de monotonicidade**.
- **Não editar nem regenerar.** Sobrescrever a baseline é uma parada obrigatória do plano
  (ver `PLANO_EXECUCAO.md` → Paradas obrigatórias). Re-simulações condicionais futuras vão para
  `data/snapshots/<timestamp>.json`, nunca aqui.
