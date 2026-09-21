# Adapter: OpenCode

*Checked against OpenCode's documentation (CLI, agents) on 2026-09-20. Where the documentation did not say, the line reads "not verified".*

---

## Start a session in the background, with model and effort

```
opencode run --dir <worktree> --model <provider/model> --variant <effort variant> --agent <name> \
  --format json --auto --title "<arc>-s<N>" "<the prompt body>" > <worktree>/tmp/session.jsonl 2>&1 &
```

Notes from the documentation:

- `--model, -m` takes `provider/model`. `--variant` is the model variant, which is provider-specific reasoning effort: the model's own name for its effort levels applies.
- `--agent` selects a primary agent (Build and Plan are built in; Build has all tools).
- `--format json` emits raw JSON events; `--auto` auto-approves permissions that are not explicitly denied; `--title` names the session.
- `--continue`, `--session <id>` and the fork option continue an earlier session; `--file, -f` attaches files.
- **A headless server:** `opencode serve` runs a server; `opencode run --attach http://localhost:4096 "<prompt>"` runs against it, and `opencode attach <url>` opens the TUI on it. A remote machine can host the fleet this way.

## List, watch, stop

Local runs: by process id. Sessions are listed and resumed inside the TUI; a shell command that lists running sessions: not verified. `opencode serve` exposes an HTTP API; its session-listing endpoints: not verified.

## Worktrees

The chair's own `git worktree add`, with `--dir <worktree>` on the run. A worktree flag on OpenCode: not verified.

## Helper agents inside a session

Built in: primary agents (Build, Plan) and subagents (General, Explore, Scout), invoked by the primary agent or by `@<name>` in a message. Custom agents are Markdown files with frontmatter in `.opencode/agents/` (project) or `~/.config/opencode/agents/` (global): `description`, `mode: primary|subagent`, `model: provider/model`, `temperature`, and a `permission` block (`edit: deny`, per-command `bash` rules). The `model` field per agent is where the swarm law's explicit cheap model goes.

## Cross-session messages

Not verified. Relay by `--session <id>` with a new prompt.

## Skills

OpenCode reads `AGENTS.md`; custom commands live in `.opencode/commands/`. Put the `/orchestrator-brief` procedure in a command file.
