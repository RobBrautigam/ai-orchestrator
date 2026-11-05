# ai-orchestrator

**Run many AI coding agents in parallel on one codebase, coordinated by one long-lived "chair" conversation.** Each agent works in its own git worktree, is launched in the background with an explicit model and effort, never stops to ask you a question, and ends by committing a briefing file that the chair reads back from disk. You read one short message that says what landed, what is running, and the one decision that is genuinely yours.

**Who it is for:** anyone already using an agentic coding tool who wants to run more than one session at a time without becoming the bottleneck. Solo builders running five to ten sessions a day, small teams sharing one repository, anyone whose agents keep colliding, stalling, or burning a week's allowance in an afternoon.

**What it is:** a method (thirteen short chapters), templates to copy, and a few small scripts that turn its rules into checks. It works with Claude Code, Codex, Gemini CLI, Cursor, OpenCode, Hermes, OpenClaw, and local models through Ollama. Nothing to install beyond git and Python. Every rule in it was written after something went wrong on a real fleet; the chapters call that fleet "the estate that wrote this" (the set of repositories and sessions one chair ran).

---

## Start in five minutes

The commands below are POSIX shell: on Windows run them in Git Bash, and on macOS type `python3` where they say `python`.

1. **See it work on a throwaway repository** (git 2.36 or later, Python 3.9 or later, nothing else):

   ```
   git clone https://github.com/RobBrautigam/ai-orchestrator.git
   cd ai-orchestrator
   python scripts/selftest.py
   ```

   Forty-seven checks run against a toy repository built in a temporary folder: a queue, a worktree, a landed briefing, the fold check naming it (and naming a session past its hard stop), the worktree rotation refusing the unsafe cases, the prompt check refusing a prompt with no definition of done, the fold lines read the way the fold reads them, the publish gate catching a planted private name, email and home path in the tree, and a listed name in a staged commit, a commit message and a pull request body. Your own git configuration is shut out and never touched. The folder is deleted at the end (`--keep` leaves it for you to look at). It takes about two minutes on Windows, where git starts slowly, and ends:

   ```
   PASS 47: both hooks are committed executable (mode 100755), so git runs them on Linux and macOS
   selftest: 47 of 47 checks passed
   ```

2. **Copy the kit into your repository:**

   ```
   cd /path/to/your-repo
   mkdir -p docs/orchestration/prompts docs/orchestration/briefings docs/orchestration/operator-directives scripts
   cp /path/to/ai-orchestrator/templates/QUEUE.md docs/orchestration/prompts/QUEUE.md
   cp -r /path/to/ai-orchestrator/templates docs/orchestration/templates
   cp -r /path/to/ai-orchestrator/docs docs/orchestration/method
   for f in fold-check fold-lines prompt-check rotate-worktree done-on-main wall-check; do cp /path/to/ai-orchestrator/scripts/$f.py scripts/; done
   ```

   Optional, the publish gate on every commit (the list stays outside the repository; [chapter 12](docs/12-going-multi-repo.md#one-directional-information-walls) has the details):

   ```
   cp /path/to/ai-orchestrator/hooks/pre-commit "$(git rev-parse --git-path hooks)/pre-commit"
   chmod +x "$(git rev-parse --git-path hooks)/pre-commit"
   git config wallcheck.list ~/wall-list.txt
   ```

   Then empty the three tables of the copied `QUEUE.md` (keep the headings and the cap line): the rows in it are an invented example. The chair creates `docs/orchestration/board.md` on its first boot.

3. **Open one conversation** in your tool, in the repository's main checkout, and paste [the chair's starter prompt](docs/01-the-chair.md#the-chairs-starter-prompt). It boots from those files.

4. **Tell it what you want, in one sentence.** It writes your words to a dated file, adds a queue row, creates the worktree, writes the dispatch prompt, and launches the session in the background, naming the model and effort in its reply.

5. **Read the one line it sends when the session lands.** Answer the one question, if there is one, at the link it gives you. From the repository's main checkout, after a `git fetch`, `python scripts/fold-check.py` shows whether anything is waiting on the chair.

Your tool's exact commands are in [adapters/](adapters/). The rest of this page is the map.

### Requirements

| Need | Version | Why |
|---|---|---|
| git | 2.36 or later | worktrees, and the selftest's toy repository |
| Python | 3.9 or later, standard library only | the scripts and the hooks |
| A POSIX shell | any (Git Bash on Windows) | the hooks and the quick start commands |
| An agentic coding tool | one with a background or headless mode | the sessions; [adapters/](adapters/) lists eight |

---

## What's new in 2.3

The operator's asks get a ledger and a verifier: a fresh, read-only reviewer that never did the work and never reads the session's own account of it opens the live result, checks it against the operator's own words, and only its MET resolves the ask. ([Chapter 7](docs/07-folding-from-files.md#the-operators-asks-checked-by-someone-who-did-not-do-the-work).) Also: no new rule without its check, the same day ([chapter 13](docs/13-lessons-into-rules.md#no-new-rule-without-its-check-the-same-day)), and keys in one place, with a pointer in each worktree instead of a copy ([chapter 2](docs/02-arcs-and-standing-worktrees.md#rotation-exactly)). No script changed; the selftest still runs 47 checks.

## What's new in 2.2

Four more rules that kept being broken became checks, each with its selftest, and [`scripts/mutation-pass.py`](scripts/mutation-pass.py) now ships, so anyone can break 22 guards one at a time in a copy and see which, if any, the selftest misses. The full list, with the why for each, is in the [changelog](CHANGELOG.md).

1. **The fold lines.** A briefing ends with one fenced block the chair copies from: the result, the board line, effort, findings, spend, every owed item with its band and owner, every carried row. [`scripts/fold-lines.py`](scripts/fold-lines.py) reads it the way the fold will. ([Chapter 6](docs/06-the-briefing-file-and-the-pointer-block.md#the-fold-lines-the-part-of-the-file-the-chair-folds-from).)
2. **The prompt check, before every launch.** [`scripts/prompt-check.py`](scripts/prompt-check.py) refuses a prompt with no `DONE MEANS` line in the body the session receives, no readable `HARD STOP`, an instruction to ask somebody, or a read-first path that does not exist. ([Chapter 4](docs/04-the-dispatch-prompt.md#what-makes-a-prompt-incomplete).)
3. **The fold check knows the clock.** The queue's running table carries each session's expected time and hard stop, and the fold check names a session past either one. ([Chapter 7](docs/07-folding-from-files.md#the-ten-minute-fold-law-and-the-check-that-enforces-it).)
4. **The publish gate at the moment of action.** A `pre-commit` hook checks what is staged, the `commit-msg` hook checks the message, and `--text-file` checks a pull request body before it is posted. ([Chapter 12](docs/12-going-multi-repo.md#one-directional-information-walls).)

And in the chapters: handing the chair over to a fresh conversation, a second reviewer only for large or sensitive changes, rails written once, and what actually wakes a chair (a scheduled prompt did not, on the estate that wrote this).

---

## The picture

<p align="center">
  <img src="docs/the-picture.svg" alt="One piece of work, its whole life: the operator's words, the chair, the queue row, the worktree, the dispatch prompt, the background session, review and ship, the briefing file and its pointer block, the fold, the slot refilled" width="1240">
</p>

One piece of work, its whole life, in ten stations:

1. **The operator's words.** Said once, written to a dated file the same minute. That file is the receipt every later step quotes.
2. **The chair.** One conversation in one window. It holds the map, writes every prompt, folds every landing, and never builds a feature itself.
3. **The queue row.** A badge, a repo, a worktree, a model and effort, a gate. It launches when a slot is free and the gate is open.
4. **The worktree.** One folder per arc, standing for the arc's whole life; a fresh branch rotates inside it. Created before the prompt, never by the session.
5. **The dispatch prompt.** A committed file: the operator's words with receipts, what is not on record, what exists, the research step, the work in order, the rails, the close.
6. **The background session.** Launched from the worktree with the model and effort spelled out. Nobody is at its keyboard, so it never asks a question.
7. **Review and ship.** Tests seen red before they are trusted, one fresh reviewer at the close, a rebase onto live main, a pull request the session merges itself, a deploy watched and a live route probed.
8. **The briefing file and the pointer block.** Eleven sections in a pushed file; then a close-out card whose last element points at the file.
9. **The fold.** Within ten minutes of the card, the chair reads the file (never the chat), runs the close test, writes one landed row in plain English, and stops the session by id.
10. **The slot refilled.** The next row whose gate is open launches the same minute. One line goes back to the operator, and that line says who moves next.

Everything between station 1 and station 10 is a file a fresh conversation can re-read. Nothing lives only in chat.

---

## Why this exists

A single coding agent does one thing at a time and asks you questions while it does it. The July 2026 version of this repository ran five to eight of them at once by having a human copy prompts out of one window and paste briefings back into it. It worked, and it made the human the bottleneck: every session waited hours for a paste that took seconds.

Version 2 removed the human from the loop everywhere a file can stand in for a paste:

- The chair launches sessions itself, in the background, from a queue with a cap.
- A session ends with a file, and the chair folds from the file. There is no paste.
- The operator is involved through exactly one surface: a short message that says what landed, what is running, and the one question that is genuinely theirs.

Version 2.1 turns the rules that kept being broken into checks: a fold check the chair runs before each new ask, a worktree rotation that proves its commit hook runs, a done-on-main check before owed work is dispatched again, and a publish gate with a literal-match mode and a home-path shape.

Version 2.2 does the same for the fold, the prompt and the publish moment: the fold copies from a checked block instead of composing from prose, a prompt is checked before it launches, the fold check reads each session's hard stop, and the publish gate runs on every commit instead of when someone remembers.

The cost of running many sessions is real and it is the reason half the chapters exist. A session launched without an explicit model inherits whatever the operator last selected, which is usually the most expensive model on the account. A swarm of fifty helper agents on that model burned a whole day's allowance in one call. A finished session sat unfolded for twenty-five minutes while the chair was busy answering questions inside one long turn. Every rule below was written after something like that happened and was measured.

---

## The model, in chapters

Each chapter is its own file. Read them in order the first time; after that, each stands alone.

| # | Chapter | What it settles |
|---|---|---|
| 1 | [The chair and its one window](docs/01-the-chair.md) | What the chair does and never does; the boot from files; the chair in a long turn; the capture inbox; the starter prompt |
| 2 | [Arcs and standing worktrees](docs/02-arcs-and-standing-worktrees.md) | One folder per arc for the arc's life; rotation as one command with its refusals and its hook proof; the cardinal rule (folder before prompt); the teardown order; the force warning |
| 3 | [The dispatch queue](docs/03-the-dispatch-queue.md) | Slots, the cap and its wind-down, gates, badges; the running, waiting and landed tables; the same-minute refill; the [generic example file](templates/QUEUE.md) |
| 4 | [The dispatch prompt](docs/04-the-dispatch-prompt.md) | The header (the operator's words with receipts; what is NOT on record; what exists); the research step with its ceiling; the reviewer specified; a hard stop; the rails; the [template](templates/dispatch-prompt.md) |
| 5 | [The background session and the close-out card](docs/05-the-background-session-and-the-close-out-card.md) | Nobody at the keyboard; the fresh reviewer and the two numbers read before trusting it; what counts as evidence; the card's seven sections; the [card template](templates/close-out-card.md) |
| 6 | [The briefing file and the pointer block](docs/06-the-briefing-file-and-the-pointer-block.md) | The file is the briefing, the chat block is a pointer; the eleven sections; the effort line; the completeness gate; the [briefing template](templates/briefing.md) and the [pointer block](templates/pointer-block.md) |
| 7 | [Folding from files](docs/07-folding-from-files.md) | The ten-minute fold law and the check that enforces it; the close test; the read ladder; the fold; the stop by id; is the owed work already done on main |
| 8 | [The hourly tick](docs/08-the-hourly-tick.md) | The chair's clock: twelve steps, in order, every hour, the fold check first |
| 9 | [The cost rules](docs/09-the-cost-rules.md) | Explicit model and effort on every launch; an alias is not a model; the cap in slots and its wind-down; never a long-context variant in the background; the swarm law; the two incidents behind it |
| 10 | [Process hygiene](docs/10-process-hygiene.md) | Kill what you start, by id; never by image name; never elevate; never a window on the operator's screen, a browser build included; read a script, never probe it |
| 11 | [The communication standard](docs/11-the-communication-standard.md) | Plain English; the volume cap; one ask per message, in the LAST message of the turn; real lists; on me and on you; the anchor emoji set; a helper's result is read by the operator; pushing back unprompted |
| 12 | [Going multi-repo](docs/12-going-multi-repo.md) | A chair across several repositories; one-directional information walls; the file relay protocol; running unattended |
| 13 | [Lessons into rules](docs/13-lessons-into-rules.md) | Where a lesson is written; when it is promoted; what only the operator may change; a rule not applied gets a check, never another sentence |

Two documents from July are kept where they still hold, revised where the model moved: [RELAY-PROTOCOL.md](RELAY-PROTOCOL.md) (two chairs coordinating through committed files across a confidentiality wall) and [OVERNIGHT-AUTOPILOT.md](OVERNIGHT-AUTOPILOT.md) (the chair running alone for hours under hard rails). What changed, and why, is in [CHANGELOG.md](CHANGELOG.md).

---

## Adapters: the same model on your tool

The model is tool-agnostic. What differs per tool is four commands: start a session in the background with a model and effort, list and stop sessions, put a session in its own worktree, and run a helper agent inside a session. Each adapter is a short file that maps those four to the tool's own flags, with **"not verified"** wherever the tool's documentation did not say, and the date it was checked at the top.

| Tool | Adapter | Background session | Worktree | Helper agents |
|---|---|---|---|---|
| Claude Code | [adapters/claude-code.md](adapters/claude-code.md) | `claude --bg --name <arc> --model <alias> --effort <level> "<prompt>"`; `claude agents --json`; `claude stop <id>` | `git worktree add` by the chair, or `claude -w <name>` | built in; `isolation: worktree` per agent |
| Codex | [adapters/codex.md](adapters/codex.md) | `codex exec` in a process you supervise; `--json`; `codex exec resume`; the agent command center in the interactive CLI | `/worktree` in the TUI, on by default; `git worktree add` by the chair | built in; custom agents in `.codex/agents/*.toml` |
| Gemini CLI | [adapters/gemini-cli.md](adapters/gemini-cli.md) | `gemini -p "<prompt>" --output-format stream-json` in a process you supervise | `git worktree add` by the chair | built in; custom agents in `.gemini/agents/*.md` |
| Cursor | [adapters/cursor.md](adapters/cursor.md) | `agent -p "<prompt>" --model <m> --output-format stream-json`; the `&` prefix hands off to a cloud agent | `agent -w <name> --worktree-base <branch>` | not verified |
| OpenCode | [adapters/opencode.md](adapters/opencode.md) | `opencode run --model <provider/model> --agent <name> --format json "<prompt>"`; `opencode serve` plus `--attach` | `git worktree add` by the chair | built in; agents in `.opencode/agents/*.md` |
| Hermes | [adapters/hermes.md](adapters/hermes.md) | `hermes chat --oneshot -q "<prompt>" --model <m> --format stream-json` | `hermes -w` | `delegate_task`, up to ten in parallel by default |
| OpenClaw | [adapters/openclaw.md](adapters/openclaw.md) | `openclaw agent exec --message-file <prompt> --cwd <worktree> --model <provider/model> --json` | `sessions_spawn` takes `worktree`, `worktreeName`, `worktreeBaseRef` | `sessions_spawn`, with depth caps |
| A local model through Ollama | [adapters/ollama.md](adapters/ollama.md) | `ollama serve`, then any tool above pointed at `http://localhost:11434/v1`; `ollama launch <tool>` | the tool's own | the tool's own |

The adapters that run a tool as a process write its output to `<worktree>/tmp/`: create that folder and add `tmp/` to `.gitignore` before the first launch.

**Grok, GLM, DeepSeek and other models** are reached through the tools above, not as tools of their own: [adapters/providers.md](adapters/providers.md) has one table of which tool reaches which model family, and how.

The rule that does not change per tool: **every launch names its model and its effort, in the command and in the chat line that reports it.** An unspecified model is the most expensive one.

---

## The scripts: rules turned into checks

Standard library Python, no dependencies, each proven by [`scripts/selftest.py`](scripts/selftest.py) on a toy repository (and [`scripts/mutation-pass.py`](scripts/mutation-pass.py) breaks their guards in a copy, one at a time, to show the selftest fails when they do). Each one refuses, or says "could not check", rather than report clean from a check that saw nothing.

| Script | What it checks | Chapter |
|---|---|---|
| [`scripts/fold-check.py`](scripts/fold-check.py) | Which sessions owe the chair a fold, a nudge or a stop, and which are past their expected time or hard stop. Read-only; run it before each new ask in a long turn and first in every tick | 7 |
| [`scripts/fold-lines.py`](scripts/fold-lines.py) | Reads a briefing's `fold-lines` block the way the fold will, and refuses a malformed one | 6 |
| [`scripts/prompt-check.py`](scripts/prompt-check.py) | Refuses a dispatch prompt with no definition of done, no readable hard stop, an instruction to ask, or a read-first path that does not exist | 4 |
| [`scripts/rotate-worktree.py`](scripts/rotate-worktree.py) | Rotates a standing worktree onto a fresh branch, refusing the unsafe cases, and proves the commit hook runs there | 2 |
| [`scripts/done-on-main.py`](scripts/done-on-main.py) | Whether an owed item's work already landed on main, by its files and by its title's words, before a prompt is written | 7 |
| [`scripts/wall-check.py`](scripts/wall-check.py) | The publish gate: a word list kept outside the repository, plus secret, email and home-path shapes, over every tracked file, the staged files (`--staged`), a commit message (`--commit-msg`) or any text about to be posted (`--text-file`) | 12 |
| [`scripts/mutation-pass.py`](scripts/mutation-pass.py) | Breaks one guard at a time in a copy of the scripts and hooks, runs the selftest on each copy, and names any break the selftest did not catch: a test never seen red is not evidence. Several minutes: one full selftest per break | 13 |
| [`hooks/pre-commit`](hooks/pre-commit) | Optional: runs the publish gate on what a commit stages, and refuses the commit on a hit or when it cannot check | 12 |
| [`hooks/commit-msg`](hooks/commit-msg) | Optional: refuses any Co-Authored-By trailer (human ones too) and any line that starts with "Generated with", for teams whose policy is that the tool is not a contributor; with `git config wallcheck.list` set, also runs the publish gate on the message | 12, 13 |

---

## Checking the tree before you publish

`scripts/wall-check.py` scans every tracked file for a list of words that must not appear (names, clients, domains, table names) and for generic shapes (keys, emails, long hex tokens, absolute paths under a named user's home folder). The list lives outside the repository so the check itself leaks nothing; a placeholder list is in [`scripts/wall-list.example.txt`](scripts/wall-list.example.txt). A list line starting with `=` is matched literally, so a table name is caught without catching the same words in prose.

```
python scripts/wall-check.py --list ~/wall-list.txt
```

Exit 0 is zero hits. This repository's own publish gate is that command at zero, with a planted file caught first so the zero means something.

The same check runs at the moment of action: `hooks/pre-commit` on what each commit stages, `hooks/commit-msg` on the message, both reading the list's path from `git config wallcheck.list`. A pull request body or a release note never passes through a git hook, so write it to a file and check it before posting:

```
python scripts/wall-check.py --list ~/wall-list.txt --text-file pr-body.md
```

---

## Where this fits

Other open-source projects run several coding agents at once; most of them are a terminal interface for watching and steering the agents. This repository is a method and a set of checks: the files that let one conversation dispatch, bound and fold many sessions without a human pasting between them. They combine; the method does not need any of them. Read on 2026-11-02:

| Project | What it is | License |
|---|---|---|
| [smtg-ai/claude-squad](https://github.com/smtg-ai/claude-squad) | A terminal app that manages several agents (Claude Code, Codex, OpenCode, Amp), each in its own tmux session and git worktree | AGPL-3.0 |
| [yohey-w/multi-agent-shogun](https://github.com/yohey-w/multi-agent-shogun) | A hierarchy of Claude Code agents in tmux panes (a lead, managers, workers) that coordinate through files | MIT |
| [kingbootoshi/codex-orchestrator](https://github.com/kingbootoshi/codex-orchestrator) | A command-line tool that lets Claude Code delegate tasks to Codex agents in tmux sessions | MIT |

What this repository adds that they do not set out to: the committed dispatch prompt with the operator's words and their receipts, the queue with a cap in slots, the briefing file and the fold, the cost rules, and checks that refuse at the moment a rule would be broken.

---

## Files in this repository

- **[README.md](README.md)**: this page.
- **[docs/](docs/)**: the thirteen chapters and the picture.
- **[templates/](templates/)**: the queue file, the dispatch prompt, the close-out card, the briefing, the pointer block. Copy them; do not link to them.
- **[adapters/](adapters/)**: one short file per tool, and the provider table.
- **[scripts/](scripts/)**: the checks above and their selftest.
- **[hooks/](hooks/)**: the optional pre-commit and commit-msg hooks.
- **[skills/orchestrator-brief/](skills/orchestrator-brief/SKILL.md)**: the on-demand briefing command.
- **[RELAY-PROTOCOL.md](RELAY-PROTOCOL.md)** and **[OVERNIGHT-AUTOPILOT.md](OVERNIGHT-AUTOPILOT.md)**: kept from July, revised.
- **[CHANGELOG.md](CHANGELOG.md)**: what moved, and why.

## Where to get help

Open an [issue](https://github.com/RobBrautigam/ai-orchestrator/issues) with what you ran, what you expected and what you saw; the selftest's output is the most useful thing to paste. Pull requests are welcome; run `python scripts/selftest.py` first.

## License

[MIT](LICENSE). Written by Rob Brautigam. Use it, fork it, adapt it.
