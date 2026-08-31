# Automação da atualização (GitHub Actions) — setup

> **EDIÇÃO ATUAL (Eleições 2026, desde 29/08):** o workflow que roda hoje é o
> [`atualizar-eleicoes.yml`](../.github/workflows/atualizar-eleicoes.yml). Ele precisa de
> **UM secret só**: `CLOUDFLARE_API_TOKEN`. O `FOOTBALL_DATA_TOKEN` era da ingestão de
> placares da Copa (workflow `atualizar-copa` DESATIVADO): não é usado por nada ativo;
> pode ficar parado no GitHub ou ser apagado, tanto faz. A seção da Copa segue abaixo
> como histórico.

## Eleições 2026: o que roda e o que você mantém

O `atualizar-eleicoes.yml` roda 1x/dia (10:37 UTC = 07:37 BRT, até 01/11/2026): ingere
pesquisas novas (Wikipédia) e, **só quando o `polls.json` muda**, re-simula, congela os
modelos, rebuilda as 30 páginas, passa nos gates e publica. Sem pesquisa nova → não
republica. Gate reprovado ou erro → **não publica** e o GitHub te manda e-mail. Sucesso →
resumo na aba **Summary** (com o alarme de completude por corrida).

### Rotacionar o `CLOUDFLARE_API_TOKEN` (quando expirar, como em 29/08/2026)

1. Cloudflare Dashboard → ícone do perfil → **My Profile → API Tokens → Create Token**.
2. Template **"Edit Cloudflare Workers"**.
3. Em **Account Resources**: restrinja à sua conta (a do `account_id` em `wrangler.toml`).
   Em **Zone Resources**: inclua `bera.ia.br` (o deploy grava a rota do Worker na zona).
4. **Continue to summary → Create Token** e copie o valor (aparece uma vez só).
5. GitHub `beralzir/ficha-do-jogo` → **Settings → Secrets and variables → Actions** →
   clique em `CLOUDFLARE_API_TOKEN` → **Update secret** → cole → Save.
6. Teste: aba **Actions → atualizar-eleicoes → Run workflow**. Verde = ciclo completo;
   sem pesquisa nova ele para no "nada a republicar", que também é sucesso.

### Rodar a edição localmente (opcional)

```bash
python3 src/ingest_polls.py    # ingere pesquisas da Wikipédia -> data/live/polls.json
./atualizar_eleicoes.sh        # motor + harness + páginas + gates (NÃO publica)
```

O deploy continua sendo parada por padrão: o script só imprime o comando do
`wrangler deploy` no fim. Conteúdo NOVO de Eleições valida local com o Bera antes.

---

## Histórico: edição Copa 2026 (workflow desativado)

O `atualizar-copa.yml` rodava 1x/dia: buscava placares (football-data + ESPN, com quorum)
e, só com jogo novo sem divergência, re-simulava e publicava. Foi **desabilitado em
29/08/2026** no fechamento da edição; o texto abaixo fica como referência.

### Secrets que a Copa usava
- `FOOTBALL_DATA_TOKEN`: chave do football-data.org (a que está em `docs/Football-data.md`,
  fora do git). **Sem uso desde 29/08.**
- `CLOUDFLARE_API_TOKEN`: o mesmo secret de deploy que a edição atual usa (receita acima).

### Como a Copa se comportava no dia a dia
- **Cron:** `17 12 * * *` (1x/dia às 12:17 UTC = 09:17 BRT, após os jogos da véspera). Ajuste no `cron:` se quiser.
- **Idempotente:** sem jogo novo, sai sem publicar (não há "republicar à toa").
- **Auto-stop:** após 20/jul/2026 (fim da Copa) o workflow encerra sem fazer nada.
- **Trilha de auditoria:** cada publicação faz commit de volta (estado + saída) no repo.
- **Segurança da ingestão:** placar só entra com as DUAS fontes concordando (quorum), jogo
  finalizado, nome de seleção mapeado (senão **aborta**), e gols mapeados pelo `fixtures.json`.
  Divergência entre fontes **bloqueia** a publicação e te avisa. Ver `src/ingest.py`.
- **Mata-mata:** AUTO-ingerido (decisão Bera 2026-06-30). Placar gravado = **fim da prorrogação**
  (pênaltis NÃO somam gol); o `winner` vem do football-data e o ESPN confirma no quórum (placar E
  vencedor). Cascata: ao gravar uma rodada, a chave avança e a próxima é pega assim que jogada.
  As datas dos cards do KO são atualizadas junto (`ko_schedule.json`). Divergência de fonte num jogo
  de KO **bloqueia** a publicação e te avisa (e-mail), igual ao grupo. Ver `src/ingest.py`.

### Rodar a Copa localmente (histórico)
```bash
set -a; source .dev.vars; set +a          # carrega FOOTBALL_DATA_TOKEN
python3 src/ingest.py                      # dry-run: mostra o que entraria + diff
python3 src/ingest.py --promote            # grava state.json (backup antes); bloqueia em divergência
./atualizar.sh                             # re-simula+build+gate (sem publicar)
```
