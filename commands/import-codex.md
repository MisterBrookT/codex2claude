---
description: Import Codex session(s) into Claude Code, then resume into them
argument-hint: "[all|<session-id>]  (default: all)"
allowed-tools: Bash(bash "${CLAUDE_PLUGIN_ROOT}/bin/import-codex.sh":*)
---

!`bash "${CLAUDE_PLUGIN_ROOT}/bin/import-codex.sh" $ARGUMENTS`
