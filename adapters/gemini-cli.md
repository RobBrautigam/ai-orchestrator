# Adapter: Gemini CLI

*Checked against Gemini CLI's documentation (headless mode reference, subagents) on 2026-09-20. Gemini CLI has no background-session supervisor; the chair supervises the processes. Where the documentation did not say, the line reads "not verified".*

---

## Start a session in the background, with model and effort

Headless mode is triggered by `-p`/`--prompt` or by a non-TTY environment:

```
gemini -p "<the prompt body>" -m <model> --output-format stream-json --yolo \
  > <worktree>/tmp/session.jsonl 2>&1 &
```

Run from the worktree. Notes from the documentation:

- `--output-format json` returns one object (`response`, `stats`, optional `error`); `stream-json` returns JSONL events (`init`, `message`, `tool_use`, `tool_result`, `error`, `result` with per-model token usage), which is what the chair reads for the last event and the token counts on the effort line.
- Exit codes: `0` success, `1` error, `42` input error, `53` turn limit exceeded. A `53` is a stall the tick answers by resuming with a higher limit or by splitting the work.
- The model flag is `-m`/`--model`; an approval mode flag exists for unattended runs (`--yolo`, or `--approval-mode`): the exact set of values was not on the headless page: not verified.
- An effort or thinking-level flag for the CLI: not verified.

## List, watch, stop

By process id, from the chair's own table. Stop by id. No built-in session list for headless runs: not verified beyond the CLI's own `/chat` save and resume commands in interactive mode.

## Worktrees

The chair's own `git worktree add`. A worktree flag on the Gemini CLI: not verified.

## Helper agents inside a session

Built in. Subagents are exposed to the main agent as tools; the main agent delegates automatically when a task matches, and `@<name>` at the start of a prompt forces one. Built-in subagents: `codebase_investigator`, `cli_help`, `generalist`, `browser_agent`. Custom subagents are Markdown files with YAML frontmatter in `.gemini/agents/*.md` (project) or `~/.gemini/agents/*.md` (user). Per-agent model and run limits are set in `settings.json` under `agents.overrides` (`modelConfig.model`, `runConfig.maxTurns`), which is where the swarm law's explicit cheap model goes. Remote subagents over the Agent2Agent protocol exist; not used by this method.

## Cross-session messages

Not verified. The chair relays by writing a follow-up prompt file and starting a new headless run in the same worktree with the earlier run's briefing named in "what exists".

## Skills

Gemini CLI reads project context from `GEMINI.md`; a skills folder equivalent to Claude Code's: not verified. Put the `/orchestrator-brief` procedure in `GEMINI.md` or in a custom command file.
