# Automação da atualização (GitHub Actions) — setup

O workflow [`.github/workflows/atualizar-copa.yml`](../.github/workflows/atualizar-copa.yml)
roda sozinho 1x/dia: busca placares novos de grupo E de mata-mata (football-data + ESPN, com
quorum), e **só quando entra jogo novo sem divergência** re-simula, rebuilda, passa no gate e publica no
Cloudflare. Sem jogo novo → não republica. Divergência/gate reprovado → **não publica** e o
GitHub te manda e-mail (falha do workflow). Sucesso → resumo na aba **Summary** do run.

## O que você precisa fazer uma vez (2 secrets no GitHub)

No repositório **privado** `beralzir/ficha-do-jogo` → **Settings → Secrets and variables →
Actions → New repository secret**:

### 1. `FOOTBALL_DATA_TOKEN`
- Valor: sua chave do football-data.org (a que está em `docs/Football-data.md`, fora do git).

### 2. `CLOUDFLARE_API_TOKEN` (escopado — não use o token global)
1. Cloudflare Dashboard → ícone do perfil → **My Profile → API Tokens → Create Token**.
2. Use o template **"Edit Cloudflare Workers"** (ou crie um Custom Token com as permissões
   *Account → Workers Scripts → Edit* e *Account → Workers Scripts → Read*).
3. Em **Account Resources**, restrinja à sua conta (a do `account_id` em `wrangler.toml`).
4. **Continue → Create Token**, copie o valor e cole no secret `CLOUDFLARE_API_TOKEN`.
   - Token escopado só publica Workers — não dá acesso ao resto da conta.

## Primeiro teste (manual, pra assistir)
- GitHub → aba **Actions → atualizar-copa → Run workflow** (`workflow_dispatch`).
- Como já há jogos novos no momento da escrita (m41-45+), o primeiro run deve **promover →
  publicar** e mostrar o resumo. Confira o site no ar depois.
- Se algo falhar, o run fica vermelho e você recebe e-mail; me mande o log do passo que falhou.

## Como ele se comporta no dia a dia
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

## Rodar localmente (opcional)
```bash
set -a; source .dev.vars; set +a          # carrega FOOTBALL_DATA_TOKEN
python3 src/ingest.py                      # dry-run: mostra o que entraria + diff
python3 src/ingest.py --promote            # grava state.json (backup antes); bloqueia em divergência
./atualizar.sh                             # re-simula+build+gate (sem publicar)
```
