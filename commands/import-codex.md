---
description: Import a Codex session into Claude Code, then resume into it
allowed-tools: Bash(bash "${CLAUDE_PLUGIN_ROOT}/bin/import-codex.sh":*)
---

Run the importer and report its output verbatim.

!`bash "${CLAUDE_PLUGIN_ROOT}/bin/import-codex.sh" $ARGUMENTS`

After it prints the resume command, tell the user: quit this session and run that
`claude -r <id>` to continue inside the imported Codex conversation.
