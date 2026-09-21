# Adapter: OpenClaw

*Checked against OpenClaw's documentation (`openclaw agent`, sub-agents, cron jobs) on 2026-09-20. OpenClaw is a gateway that runs agents and meets the operator in chat channels; model and agent harness are plugins. Where the documentation did not say, the line reads "not verified".*

---

## Start a session in the background, with model and effort

The unattended entry point is `openclaw agent exec`:

```
openclaw agent exec --message-file <the committed prompt file> --cwd <worktree> \
  --model <provider/model> --thinking <level> --json > <worktree>/tmp/session.jsonl 2>&1 &
```

Notes from the documentation:

- `--message-file <path>` reads the prompt from a file (`-` reads stdin); `--cwd <dir>` sets both the agent workspace and the tool working directory.
- `--model <provider/model>` is the explicit primary model; `--fallback <provider/model>` (repeatable) names ordered fallbacks; `--thinking <level>` is the one-run thinking level, which is OpenClaw's effort setting.
- `--json` writes structured output; plain output writes only the final assistant text to stdout with diagnostics on stderr.
- `--isolated` ignores the ambient config and uses exec defaults; `--config <path>` runs against a named config file; `--state-dir <dir>` reuses an existing state directory.
- `--local-model-lean` reduces the tool surface for a local model; `--code-mode direct|auto|code` selects the tool mode.

## List, watch, stop

Sessions live in the gateway's session tree; `openclaw sessions` and the `subagents` tool list and stop them. The sub-agent concurrency, recovery and stopping page documents a cascade stop of a child tree. A local `agent exec` run is also a process the chair started, stopped by id.

## Worktrees

OpenClaw has first-class worktree parameters on the spawn tool: `sessions_spawn` takes `worktree`, `worktreeName` and `worktreeBaseRef`. The chair's own `git worktree add` with `--cwd <worktree>` works equally for `agent exec`. A worktree flag on `agent exec` itself: not verified.

## Helper agents inside a session

The `sessions_spawn` tool spawns a sub-agent session with `task`, `agentId`, `cwd`, `model`, `thinking`, `runTimeoutSeconds`, `sandbox`, `mode`, `cleanup`, `visible` and the worktree parameters above; `sessions_yield` and `subagents` manage them. Completion is non-blocking and push-based: the result is announced back to the requester. Configuration: `agents.defaults.subagents.model` (the swarm law's explicit cheap model, written once), `allowAgents`, `requireAgentId`, `announceTimeoutMs`, depth levels for nested sub-agents and a per-agent spawn limit. The documentation's own guidance matches this method's: ordinary sub-agents for internal lanes with results returning to the parent; a persistent visible session only when the operator asks for one.

## Scheduled runs

`openclaw cron` runs isolated recurring jobs with `--message`, `--thinking` and a choice of main, current, isolated or custom session. On the operator's own machine this method prefers the chair's tick over a cron entry (chapter 10: nothing periodic on the operator's machine without their word); on a server OpenClaw's cron is the natural home for the tick.

## Cross-session messages

The gateway's session tree and thread-bound sessions carry follow-ups into a running child; the exact tool for a message into an `agent exec` run: not verified.

## Skills

OpenClaw has a skills ecosystem (a public collection of several thousand). Put the `/orchestrator-brief` procedure in an OpenClaw skill; the folder layout: not verified beyond the skills documentation.
