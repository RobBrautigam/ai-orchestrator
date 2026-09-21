# Adapter: Hermes Agent

*Checked against Hermes Agent's documentation (CLI commands reference, subagent delegation, quickstart) on 2026-09-20. Hermes runs as a gateway with chat-platform front ends as well as a CLI, so a fleet can be steered from a phone. Where the documentation did not say, the line reads "not verified".*

---

## Start a session in the background, with model and effort

```
hermes --in <worktree> chat --oneshot -q "<the prompt body>" --provider <provider> --model <model> \
  --format stream-json > <worktree>/tmp/session.jsonl 2>&1 &
```

Notes from the documentation:

- `hermes chat -q "<prompt>"` seeds an interactive session; `--oneshot` answers and exits; `--query-file <path>` reads the prompt from a file (the committed dispatch prompt); `--quiet` prints only the answer; `--format stream-json` gives structured JSONL. `hermes -z <prompt>` is the scripted one-shot shorthand.
- `--provider` and `--model` set the model for the run; `hermes model` picks the default interactively. An effort flag: not verified.
- `--in <dir>` changes into the worktree before starting and scopes session lookup to it. `--resume <session>` and `-c` continue sessions; `--yolo` bypasses dangerous-command approval.
- The gateway (`hermes gateway`) delivers completions to Telegram, Discord, Slack and the rest; a run started through the gateway reports there.

## List, watch, stop

Local runs: by process id. Session listing: `--resume latest` and `-c` operate on saved sessions; a listing command was not found on the CLI reference: not verified.

## Worktrees

Hermes has a first-class flag: `hermes -w` (`--worktree`) starts in an isolated git worktree for parallel-agent workflows. The chair's own `git worktree add` with `--in <dir>` works equally. The naming and location of Hermes-created worktrees: not verified.

## Helper agents inside a session

The `delegate_task` tool spawns child agents with isolated context, inherited tools and their own terminal sessions; each child gets a fresh conversation and only its final summary enters the parent's context. A `tasks=[...]` batch runs in parallel, up to ten concurrent by default (`delegation.max_concurrent_children`). Children know nothing of the parent's conversation, so the call carries `goal` and `context` in full. A cheaper model for all children is set in `~/.hermes/config.yaml` under `delegation.model` (there is no per-task model parameter), which is the swarm law's explicit cheap model written once. Background processes belong to the agent that started them, and a child's processes are terminated when the child closes: kill-what-you-start is built in at the child level.

## Cross-session messages

Not verified. Relay by `--resume <session>` with a new query.

## Skills

Hermes has its own skills system with a learning loop (it creates and improves skills from experience). Put the `/orchestrator-brief` procedure in a Hermes skill; the folder layout: not verified beyond the documentation's skills section.
