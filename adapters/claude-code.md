# Adapter: Claude Code

*Checked against Claude Code's own documentation (the CLI reference, agent view, worktrees and subagents pages) on 2026-09-20, and the CLI reference, agent view and subagents pages again on 2026-09-23 (release v2.1.280 was the newest). Where the documentation did not say, the line reads "not verified". This is the tool the model was built on, so it is the most complete adapter.*

---

## Start a session in the background, with model and effort

```
claude --bg --name <arc>-s<N> --model <sonnet|opus|haiku|fable|full id> --effort <low|medium|high|xhigh|max> \
  --permission-mode auto --permission-prompts none "<the prompt body>"
```

Run it from the worktree (the working directory is the session's repository). It returns immediately and prints the session id. Notes from the documentation:

- `--bg` cannot be combined with `-p` (print mode).
- `--permission-prompts none` denies any permission prompt nobody can answer instead of hanging on it (Claude Code v2.1.259 or later). The CLI reference describes it for print mode; its effect on a `--bg` session: not verified, so the launch shape still avoids every prompt it can. `--permission-mode auto` is the unattended mode; `--dangerously-skip-permissions` skips checks entirely and its mode persists across supervisor restarts of a background session.
- `--fallback-model <m1>,<m2>` names models to fall back to, in order, when the primary is overloaded or retired; the chair's launch line names the fallback too when one is set.
- `claude --bg --exec '<command>'` runs a shell command (a long test run, a build) as a background job the agent view lists beside the sessions, instead of starting a session.
- A repository whose project `.mcp.json` triggers an approval dialog blocks a background session at startup; launch with `--strict-mcp-config` (optionally with `--mcp-config <file>`) to bypass ambient MCP configuration.
- `--max-budget-usd` caps API spend, **print mode only**; not available for `--bg` sessions.
- `--name` sets the display name shown in the session list and terminal title; a duplicate name gets a variant.

## List, watch, stop, restart

```
claude agents --json            # active background sessions as JSON (add --all for completed ones)
claude logs <id>                # recent output of a background session
claude attach <id>              # take over the session in this terminal; the left arrow detaches
claude stop <id>                # stop it (alias: claude kill)
claude respawn <id>             # restart a running or stopped session with its conversation intact (--all: every running one, e.g. after an update)
claude rm <id>                  # remove a session from the list; refused over a worktree with unpushed work, and the refusal prints the flag to pass
claude daemon status            # the background-session supervisor's state; exits 1 when it is not running
claude agents                   # the interactive agent view: rows by state, Space to peek and reply, Enter to attach
```

The agent view's states: working, needs input, idle, completed, failed, stopped. The supervisor stops a session that has finished or is waiting for a prompt and stays unattached for about an hour; attaching or replying restarts it from where it left off. A session that ended its turn by asking a question counts as waiting, which is why this method's prompts say never to ask one.

Notification hooks `agent_needs_input` and `agent_completed` fire on those transitions; the chair can subscribe to them instead of polling. Pinning a session in the agent view (Ctrl+T) keeps its process running past the one-hour stop. Sessions survive the machine sleeping: their processes resume on wake and the supervisor reconnects to them.

A background session that isolated its own work in a worktree commits, pushes its own branch (never main) and opens a draft pull request when it finishes, instead of asking first. This method's sessions run in the chair's worktree and merge through their own pull request, so the prompt's close section, not this default, decides what happens.

## Worktrees

The chair's own `git worktree add ../<repo>-<arc> -b <branch> origin/main` is the shape this method uses (sibling folders, standing per arc, branch rotated inside). Claude Code also has its own:

```
claude -w <name>                # start Claude in .claude/worktrees/<name>/ on branch worktree-<name>
claude -w <name> --tmux         # the same, in a tmux session (iTerm2 native panes when available)
```

**Never call the in-session `EnterWorktree` tool from a background session.** It raises a confirmation nobody unattended can answer; a session once stalled forty minutes on it. The worktree the session is launched in IS the isolation.

## Helper agents inside a session

Built in (the Agent tool). Custom subagents are Markdown files with frontmatter in `.claude/agents/` (project) or `~/.claude/agents/` (user); the `model` field sets the model (`haiku`, `sonnet`, `opus`, or `inherit`); `isolation: worktree` gives a subagent its own worktree, removed automatically when it changes nothing. A background subagent's result reaches the session as a completion notification in a later turn. Built-in agents inherit the session's model unless `CLAUDE_CODE_SUBAGENT_MODEL` is set. The swarm law (chapter 9) applies: more than about three at once, each with an explicit cheap model.

## Cross-session messages

A running session can be reached with the session-messaging tools (`ListAgents`, `SendMessage`) from another session, which is how the chair relays a contract or an answer into a running session without a paste. Cross-session messaging has its own documentation page and is enabled per session; a background subagent does not keep the messaging tool, so a relay goes to the session, not to its helpers.

## Skills

Copy `skills/orchestrator-brief/` to `~/.claude/skills/orchestrator-brief/`; the `/orchestrator-brief` command is then available in every repository.

## Not verified

- Whether `--effort` is accepted on every model alias (the documentation says available levels depend on the model).
- Any cap on the number of concurrent background sessions (the documentation names none; the account's concurrent-session limit is the practical one).
