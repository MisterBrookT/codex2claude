#!/usr/bin/env bash
# codex2claude — import Codex session(s) into Claude Code, then `claude --resume` into them.
#
# transession transcodes each Codex rollout into a Claude jsonl, routed into the
# project dir that matches the session's own cwd. A ledger dedups re-imports.
#
# Usage:
#   import-codex.sh                 import ALL codex sessions (default)
#   import-codex.sh all             same as default
#   import-codex.sh <SESSION_ID>    import one specific session
set -euo pipefail

command -v transession >/dev/null || {
  echo "missing engine: transession"
  echo "install: cargo install transession   (https://github.com/inmzhang/transession)"
  exit 1
}

LEDGER="$HOME/.claude/codex-import-ledger.tsv"   # codex_sid <tab> claude_sid
SESSIONS="$HOME/.codex/sessions"
UUID='[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
touch "$LEDGER"

# import one codex session id. echoes "ok <claude_sid>" / "skip" / "fail".
import_one() {
  local sid="$1" existing out csid path
  existing=$(awk -F'\t' -v s="$sid" '$1==s{print $2; exit}' "$LEDGER")
  if [[ -n "$existing" ]]; then echo "skip $existing"; return 0; fi
  out=$(transession --from codex --to claude "$sid" --no-open 2>&1) || { echo "fail"; return 1; }
  csid=$(echo "$out" | grep -oE "$UUID" | tail -1)
  path=$(echo "$out" | grep -oE '/[^ ]*\.jsonl' | head -1)
  [[ -z "$csid" || -z "$path" ]] && { echo "fail"; return 1; }
  # normalize transession output into a native-faithful transcript (else it spins
  # forever on "Loading..." in the Claude Code / Zed session viewer)
  python3 "$SCRIPT_DIR/normalize-claude.py" "$path" >/dev/null 2>&1 || { echo "fail"; return 1; }
  printf "%s\t%s\n" "$sid" "$csid" >> "$LEDGER"
  echo "ok $csid"
}

ARG="${1:-all}"

# --- single specific session ---
if [[ "$ARG" =~ ^$UUID$ ]]; then
  res=$(import_one "$ARG"); kind=${res%% *}; csid=${res#* }
  case "$kind" in
    ok)   echo "imported codex $ARG -> claude $csid"; echo; echo "NEXT: quit, then run:  claude -r $csid" ;;
    skip) echo "already imported codex $ARG"; echo "resume: claude -r $csid" ;;
    *)    echo "transcode failed for $ARG"; exit 1 ;;
  esac
  exit 0
fi

# --- batch: import all ---
[[ "$ARG" != "all" ]] && { echo "usage: import-codex.sh [all|<session-id>]"; exit 1; }

imported=0 skipped=0 failed=0
while IFS= read -r f; do
  sid=$(basename "$f" | grep -oE "$UUID" | head -1)
  [[ -z "$sid" ]] && continue
  case "$(import_one "$sid")" in
    ok*)   imported=$((imported+1)) ;;
    skip*) skipped=$((skipped+1)) ;;
    *)     failed=$((failed+1)) ;;
  esac
done < <(find "$SESSIONS" -name '*.jsonl' 2>/dev/null | sort)

echo "imported $imported · skipped $skipped (already) · failed $failed"
echo
echo "NEXT: quit, then run  claude -r  in any project — the picker now lists the imported Codex sessions."
