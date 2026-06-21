#!/usr/bin/env bash
# codex2claude — import a Codex session into Claude Code, then `claude --resume` into it.
#
# Detect newest Codex rollout (or take a session-id arg) -> transcode via transession
# -> write a Claude jsonl into the CURRENT project dir. A ledger dedups re-imports.
#
# Usage: import-codex.sh [CODEX_SESSION_ID]
#   no arg -> newest codex session
set -euo pipefail

command -v transession >/dev/null || {
  echo "missing engine: transession"
  echo "install: cargo install transession   (https://github.com/inmzhang/transession)"
  exit 1
}

LEDGER="$HOME/.claude/codex-import-ledger.tsv"   # codex_sid <tab> claude_sid
touch "$LEDGER"

UUID='[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'

# 1. resolve codex session id + file
if [[ $# -ge 1 && -n "${1:-}" ]]; then
  SID="$1"
  FILE=$(find "$HOME/.codex/sessions" -name "*$SID*.jsonl" 2>/dev/null | head -1)
else
  FILE=$(find "$HOME/.codex/sessions" -name '*.jsonl' 2>/dev/null | sort | tail -1)
  SID=$(basename "${FILE:-}" | grep -oE "$UUID" | head -1)
fi
[[ -z "${FILE:-}" || ! -f "$FILE" ]] && { echo "no codex session found for '${1:-latest}'"; exit 1; }

# 2. dedup: already imported?
if EXIST=$(awk -F'\t' -v s="$SID" '$1==s{print $2; exit}' "$LEDGER"); [[ -n "$EXIST" ]]; then
  echo "already imported codex $SID"
  echo "resume: claude -r $EXIST"
  exit 0
fi

# 3. transcode (transession keys output by the current working dir's project)
OUT=$(transession --from codex --to claude "$SID" --no-open 2>&1)
CLAUDE_SID=$(echo "$OUT" | grep -oE "$UUID" | tail -1)
[[ -z "$CLAUDE_SID" ]] && { echo "transcode failed:"; echo "$OUT"; exit 1; }

printf "%s\t%s\n" "$SID" "$CLAUDE_SID" >> "$LEDGER"
echo "imported codex $SID -> claude $CLAUDE_SID"
echo
echo "NEXT: quit this session, then run:  claude -r $CLAUDE_SID"
