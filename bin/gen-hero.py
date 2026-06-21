#!/usr/bin/env python3
"""Generate README hero via OpenRouter gpt-image-2. One-shot, saves assets/hero.png."""
import os, sys, json, base64, urllib.request

KEY = os.environ["OPENROUTER_API_KEY"]
PROMPT = (
    "A minimal flat editorial illustration on a warm paper-ink background (#F4EEE2), "
    "tight composition that fills the frame with little empty margin. "
    "Two simple terminal windows side by side, large and centered. The left window is "
    "tinted neutral charcoal and clearly labeled 'Codex' in small clean lettering on its "
    "title bar. The right window is accented with persimmon orange (#F25C05) and clearly "
    "labeled 'Claude' on its title bar. A single bold persimmon arrow flows from the left "
    "(Codex) terminal into the right (Claude) one, carrying a small stylized stack of "
    "chat-bubble lines (a conversation transcript) along the arrow. Only the two words "
    "'Codex' and 'Claude' appear as text; no other text, no logos, no emoji. Calm, "
    "intentional, hand-crafted tech aesthetic, thin ink strokes. 16:9 composition."
)

def call(model):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": PROMPT}],
        "modalities": ["image", "text"],
    }).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)

for model in ("openai/gpt-5.4-image-2", "openai/gpt-5-image"):
    try:
        d = call(model)
        imgs = d["choices"][0]["message"].get("images") or []
        if not imgs:
            print(f"{model}: no image in response: {json.dumps(d)[:400]}", file=sys.stderr); continue
        url = imgs[0]["image_url"]["url"]
        raw = base64.b64decode(url.split(",", 1)[1])
        out = os.path.join(os.path.dirname(__file__), "..", "assets", "hero.png")
        open(out, "wb").write(raw)
        print(f"OK {model} -> {os.path.abspath(out)} ({len(raw)} bytes)")
        sys.exit(0)
    except Exception as e:
        print(f"{model} failed: {e}", file=sys.stderr)
sys.exit(1)
