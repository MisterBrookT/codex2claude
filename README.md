# codex2claude

把一条 Codex 会话导入 Claude Code，退出后 `claude --resume` 直接接着聊。

Codex 原生支持 import-from-Claude，反方向一直缺。`codex2claude` 补上这条——做成一个 Claude Code 插件，一个 slash 命令搞定。

![codex2claude](assets/hero.png)

## 安装

需要引擎 [transession](https://github.com/inmzhang/transession) 做转码：

```sh
cargo install transession
```

装插件（Claude Code 内）：

```
/plugin marketplace add MisterBrookT/codex2claude
/plugin install codex2claude
```

## 用法

在 Claude Code 里：

```
/import-codex            # 导入最新的 Codex 会话
/import-codex <id>       # 导入指定 session id
```

它会转码、写进当前项目目录、去重，然后吐一行：

```
NEXT: quit this session, then run:  claude -r <id>
```

退出当前会话，跑那行 `claude -r <id>`，就接进刚才那条 Codex 对话。全程不手敲转码命令。

## 原理

```
~/.codex/sessions/*.jsonl  ──transession──▶  ~/.claude/projects/<cwd>/<id>.jsonl  ──▶  claude -r <id>
```

- **detect**：默认抓最新一条 Codex rollout，也可传 session id
- **transcode**：复用 transession 的 universal IR 在两套格式间互转
- **dedup**：`~/.claude/codex-import-ledger.tsv` 记 `codex_sid → claude_sid`，同一条不重复导

## 限制

转 messages / tool calls / timestamps / metadata，**丢** reasoning payload 和 runtime cache——resume 的上下文够用，不是逐 token 复刻。

## License

MIT
