#!/usr/bin/env python3
"""Normalize a transession-produced Claude jsonl into a native-faithful transcript.

transession 0.1.2 emits a structurally valid but incomplete Claude session: wrong
`version`, assistant messages missing `model`/`usage`/`requestId`/`message.type`,
a trailing non-node `{"type":"mode"}` record, and a synthetic first "user" turn that
dumps Codex's system instructions (which becomes an ugly resume-picker title).

This rewrites the file in place so Claude Code / the Zed extension can render it.

Usage: normalize-claude.py <claude_session.jsonl> [--version X.Y.Z] [--model ID]
"""
import json, uuid, argparse

ap = argparse.ArgumentParser()
ap.add_argument("path")
ap.add_argument("--version", default="2.1.183")
ap.add_argument("--model", default="claude-opus-4-8")
a = ap.parse_args()

rows = []
for line in open(a.path):
    line = line.strip()
    if line:
        rows.append(json.loads(line))

# 1. drop non-node trailing records (e.g. {"type":"mode"}) — they have no uuid and
#    show up as phantom roots / break leaf resolution.
rows = [r for r in rows if r.get("type") in ("user", "assistant", "system")]

# 2. drop the synthetic system-injection turns transession surfaces as leading
#    "user" messages (Codex's developer preamble, the host AGENTS.md, instruction
#    blocks). They are not real conversation and poison the resume-picker title,
#    which Claude derives from the first user message. Only strip while leading, so
#    the real first prompt becomes the root/title; never strip the whole file.
SYNTH_PREFIXES = ("[transession imported", "# AGENTS.md", "<INSTRUCTIONS>",
                  "<user_instructions>", "<system-reminder>")

def first_text(r):
    c = (r.get("message") or {}).get("content")
    if isinstance(c, list) and c and isinstance(c[0], dict):
        return str(c[0].get("text", ""))
    if isinstance(c, str):
        return c
    return ""

def is_synthetic(r):
    if r.get("type") != "user":
        return False
    t = first_text(r).lstrip()
    return any(t.startswith(p) for p in SYNTH_PREFIXES)

while len(rows) > 1 and rows[0].get("type") in ("user", "system") and is_synthetic(rows[0]):
    rows.pop(0)

# 3. re-root + relink into a clean linear chain, and backfill native fields.
prev_uuid = None
for r in rows:
    r["uuid"] = r.get("uuid") or str(uuid.uuid4())
    r["parentUuid"] = prev_uuid
    r["version"] = a.version
    r.setdefault("userType", "external")
    r.setdefault("isSidechain", False)
    r.setdefault("gitBranch", "")
    r.setdefault("cwd", r.get("cwd", ""))

    if r["type"] == "user":
        r.setdefault("permissionMode", "default")
        r.setdefault("entrypoint", "cli")
        r.setdefault("promptSource", "user")
        r.setdefault("promptId", str(uuid.uuid4()))
    elif r["type"] == "assistant":
        r.setdefault("requestId", "req_" + uuid.uuid4().hex[:24])
        m = r.setdefault("message", {})
        m["type"] = "message"
        m.setdefault("role", "assistant")
        m.setdefault("model", a.model)
        m.setdefault("id", "msg_" + uuid.uuid4().hex[:24])
        m.setdefault("stop_reason", m.get("stop_reason"))
        m.setdefault("stop_sequence", m.get("stop_sequence"))
        m.setdefault("usage", {
            "input_tokens": 0, "output_tokens": 0,
            "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
            "service_tier": "standard",
        })
    prev_uuid = r["uuid"]

with open(a.path, "w") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print(f"normalized {len(rows)} lines (1 root, version={a.version})")
