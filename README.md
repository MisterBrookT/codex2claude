# codex2claude

Import any Codex session into Claude Code — quit, then `claude --resume` to continue.

把任意 Codex 会话导入 Claude Code——退出后 `claude --resume` 接着聊。

Codex imports from Claude; this is the missing reverse, as a one-command Claude Code plugin.

Codex 能从 Claude 导入，这条补上反方向——一个命令的 Claude Code 插件。

<p align="center"><img src="assets/hero.png" width="480" alt="codex2claude"></p>

## Install

Requires the [transession](https://github.com/inmzhang/transession) engine for transcoding:

```sh
cargo install transession
```

Install the plugin (inside Claude Code):

```
/plugin marketplace add MisterBrookT/codex2claude
/plugin install codex2claude
```

## Usage

Inside Claude Code:

```
/import-codex            # default: import ALL Codex sessions (the reverse of Codex's)
/import-codex all        # same, explicit
/import-codex <id>       # import a specific session id only
```

Each session is written into its matching project directory by its own `cwd`, with deduplication. Quit after importing, then run `claude -r` in any project — the picker lists the just-imported Codex sessions; pick one to continue. No manual transcoding commands.

> Zero-token option: the slash command still passes through the model once per call. To burn zero tokens, run `bash ~/.claude/bin/import-codex.sh` directly in the terminal (or wrap it in an alias). Claude Code's custom slash commands must pass through one model round — this is a platform limit.

## How it works

```
~/.codex/sessions/*.jsonl  ──transession──▶  ~/.claude/projects/<cwd>/<id>.jsonl  ──▶  claude -r <id>
```

- **detect**: by default grabs every Codex rollout; can also take a session id
- **transcode**: reuses transession's universal IR to interconvert between the two formats
- **normalize**: rewrites the output into a native-faithful transcript (fixes Codex content tags, image sources, picker title, missing native fields) so it loads and resumes without errors
- **dedup**: `~/.claude/codex-import-ledger.tsv` tracks `codex_sid → claude_sid` so the same session isn't re-imported

## Limitations

Converts messages / tool calls / timestamps / metadata; **drops** the reasoning payload and runtime cache — enough context to resume, not a token-perfect replica.

## License

MIT
