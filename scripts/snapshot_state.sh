#!/usr/bin/env bash
# snapshot_state.sh — backup datado de data/live/state.json ANTES de qualquer escrita
# automática (ingestão via API). Rollback independente do git (belt-and-suspenders;
# no CI o rollback primário é o commit/revert, mas isto protege runs locais e o
# instante entre "escrever candidato" e "commitar").
#
#   scripts/snapshot_state.sh            # cria backup datado em data/live/backups/
#   scripts/snapshot_state.sh --restore  # restaura o backup mais recente sobre state.json
#
# Retém os 30 backups mais recentes. A pasta backups/ é gitignored (efêmera).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LIVE="$ROOT/data/live"
BK="$LIVE/backups"
mkdir -p "$BK"

if [ "${1:-}" = "--restore" ]; then
  last="$(ls -1t "$BK"/state-*.json 2>/dev/null | head -1 || true)"
  [ -n "${last:-}" ] || { echo "snapshot_state: sem backup para restaurar" >&2; exit 1; }
  cp "$last" "$LIVE/state.json"
  echo "snapshot_state: restaurado $last -> data/live/state.json"
else
  [ -f "$LIVE/state.json" ] || { echo "snapshot_state: nada a salvar (sem state.json)"; exit 0; }
  dst="$BK/state-$(date +%Y%m%dT%H%M%S).json"
  cp "$LIVE/state.json" "$dst"
  ls -1t "$BK"/state-*.json | tail -n +31 | xargs -I{} rm -f {} 2>/dev/null || true
  echo "snapshot_state: backup criado -> ${dst#$ROOT/}"
fi
