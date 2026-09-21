# Adapter: Codex (OpenAI Codex CLI)

*Checked against OpenAI's Codex documentation (the CLI reference, the non-interactive `codex exec` page, the subagents page) on 2026-09-20. Codex has no built-in background-session supervisor equivalent to Claude Code's agent view; the chair supervises the processes itself. Where the documentation did not say, the line reads "not verified".*

---

## Start a session in the background, with model and effort

Codex's unattended entry point is `codex exec`. There is no `--bg`; the chair starts it as a background process from the worktree and keeps the process id:

```
codex exec -C <worktree> --model <model> -c model_reasoning_effort=<low|medium|high|xhigh|max|ultra> \
  --sandbox workspace-write --json --output-last-message <worktree>/tmp/last.md \
  "<the prompt body>" > <worktree>/tmp/session.jsonl 2>&1 &
```

Notes from the documentation:

- `--model, -m` overrides the configured model; reasoning effort is a config key (`model_reasoning_effort`) set with `-c key=value` or in a profile (`--profile, -p`). Whether every effort level is accepted on every model: not verified.
- `--sandbox, -s` chooses `read-only`, `workspace-write` or `danger-full-access`; `--full-auto` is kept as a deprecated alias for `workspace-write`. `--ask-for-approval, -a` sets the approval policy; in a non-interactive run an action that needs a fresh approval fails and the error surfaces, so the launch shape must pre-answer everything.
- `--json` streams JSONL events to stdout; `--output-last-message, -o <path>` writes the final message to a file, which is the natural place for the pointer block.
- `--ephemeral` skips saving the session to disk. `codex exec resume --last "<follow-up>"` (or `resume <session id>`) continues a run, which is the relay mechanism.
- Codex requires a git repository by default; `--skip-git-repo-check` overrides.
- `--oss` with `--local-provider ollama|lmstudio` runs against a local model (see the Ollama adapter).

## List, watch, stop

The chair keeps a small table of process ids it started and reads each run's JSONL for the last event. Stop by process id, never by image name. `codex resume` and `codex fork` operate on saved sessions from the TUI. A tmux-based supervisor (several public repositories wrap Codex this way) is the common shape when a screen per session is wanted; it is not required by this method.

## Worktrees

The chair's own `git worktree add` is the shape. In the interactive TUI, `/worktree` runs the chat in a new git worktree; whether `codex exec` has a worktree flag: not verified. Codex's documentation has a "Git worktrees" page under configuration; its exact flags were not readable at check time: not verified.

## Helper agents inside a session

Built in: current releases enable subagent workflows by default; Codex spawns them on a direct request or when `AGENTS.md` or a skill asks for delegation, and `/agent` in the interactive CLI switches between agent threads. Custom agents are TOML files in `.codex/agents/<name>.toml` with `name`, `description`, `model`, `model_reasoning_effort`, `sandbox_mode` and `developer_instructions`, which is exactly where the swarm law's "explicit cheap model on every agent" is written down. Subagents inherit the parent's sandbox and approval policy.

## Cross-session messages

`codex exec resume <session id> "<message>"` is the documented way to continue a saved non-interactive run with a new instruction. A message into a run that is still executing: not verified.

## Skills

Skills live in `.codex/skills/` (project) and are also read from the Claude-style folder by several installers; copy `skills/orchestrator-brief/` there. The frontmatter format Codex reads: not verified beyond `name` and `description`.
