# Adapter: Cursor (the `agent` CLI)

*Checked against Cursor's CLI documentation (overview and parameters) on 2026-09-20. Where the documentation did not say, the line reads "not verified".*

---

## Start a session in the background, with model and effort

Cursor's CLI installs as `agent` (`curl https://cursor.com/install -fsS | bash`; on Windows PowerShell, `irm 'https://cursor.com/install?win32=true' | iex`). Headless runs use `-p`/`--print`:

```
agent -p "<the prompt body>" --model <model> --output-format stream-json --force --trust \
  --workspace <worktree> > <worktree>/tmp/session.jsonl 2>&1 &
```

Notes from the documentation:

- `-p, --print` prints responses for scripts and has access to all tools, including write and shell. `--output-format` is `text`, `json` or `stream-json` (print only); `--stream-partial-output` adds text deltas.
- `--model <model>` sets the model; `--list-models` lists them. An effort or reasoning-level flag: not verified.
- `-f, --force` (alias `--yolo`) allows commands unless explicitly denied; `--trust` trusts the workspace without prompting (headless only); `--approve-mcps` pre-approves MCP servers; `--sandbox enabled|disabled` toggles the sandbox.
- `--resume [chatId]`, `--continue`, and `agent ls` list and resume conversations.
- **Cloud agents:** in an interactive session, prefixing a message with `&` hands the conversation to a Cloud Agent that keeps running after you leave (`cursor.com/agents` to pick it up). That is Cursor's own background mechanism; its command-line launch shape: not verified.

## List, watch, stop

Local headless runs: by process id, from the chair's table. Cloud agents: the web and mobile surface at `cursor.com/agents`; a CLI list of cloud agents: not verified.

## Worktrees

Cursor has a first-class flag:

```
agent -w <name> --worktree-base <branch>     # a new worktree under ~/.cursor/worktrees/<repo>/<name>
agent -w <name> --skip-worktree-setup        # skip the setup scripts in .cursor/worktrees.json
```

The chair's own `git worktree add` (sibling folders, standing per arc) works equally; `--workspace <path>` points a run at it.

## Helper agents inside a session

Not verified. Cursor's documentation describes subagents in the editor; a per-agent model setting reachable from the CLI was not found at check time.

## Cross-session messages

Not verified. Relay by `--resume <chatId>` with a new prompt.

## Skills

Cursor reads rules from `.cursor/rules/`; `--plugin-dir <path>` loads a local plugin directory. A skills folder in the Claude Code shape: not verified. Put the `/orchestrator-brief` procedure in a rule file.
