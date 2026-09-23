# 7. Folding from files

*A fold is what the chair does when a session lands: read the briefing file, test that the session is really closed, write the landed row, free the slot, stop the session by id. It is done from the file, never from a paste, and it is done the same minute.*

---

## The landing signal

Two signals, either one starts a fold:

- the session's briefing file appears on the main branch (a merged pull request that added `docs/orchestration/briefings/<date>-<arc>.md`);
- the tool's own session list shows the session as done, and its last output carries the pointer block.

The first is the completion signal proper; the second is the earlier one. The chair watches both: the tick fetches main and lists sessions every hour, and a notification hook (where the tool has one) wakes the chair when a session finishes or needs input.

## The ten-minute fold law, and the check that enforces it

**A fold is owed within ten minutes of the close-out card.** That sounds like a promise; it is written as a check because the promise failed. Notifications and the hourly tick both arrive BETWEEN the chair's turns, so the chair is blind for exactly as long as its longest turn. Measured: a finished session read "running" for twenty-five minutes while the chair answered nine operator messages inside one turn, and in the same window two more sessions closed and a fourth stopped on a network error. Nothing was wrong with any session; the chair simply never looked up.

1. **A chair turn that runs past ten minutes runs the fold check before it takes each new ask**, and handles what it names before the ask.
2. **The fold check is the first step of every tick** (chapter 8) and the first command of any turn a notification opened.
3. **The final message of a turn over ten minutes states the check's result in one line**: "every running session is working", or what was found and what was done about it.
4. **The check is read-only and fast** (seconds, not minutes), so running it too often costs nothing and running it too rarely is the whole failure.

This repository's generic version is [`scripts/fold-check.py`](../scripts/fold-check.py). It reads the queue file's running table and the briefings folder on `origin/main`, and optionally the tool's own session list as JSON, and names every session that owes the chair something: a fold (the briefing landed and the row still holds a slot), a stale row, a folded session still resident, a session that ended without a card, one that needs input, one the tool no longer lists, and one the table does not know about. It prints "all clear" when nothing is owed. `python scripts/selftest.py` proves it on a toy repository. Where the tool can run a command on every operator message (a prompt-submit hook), wiring the check into it puts the list in front of the chair at the one moment a signal does reach it mid-turn.

## The close test

Before anything is written, four checks, every time:

1. **The card is up.** The session's last message is a close-out card with a pointer block between the literal bookends. A session whose last message is a progress note or a question has stalled, not landed (chapter 5); the chair answers it, and the fold waits.
2. **The file is readable.** The `READ:` command from the pointer block runs and returns the whole file. When it does not, the read ladder below runs before anyone is asked anything.
3. **The claims hold.** A briefing is a claim, not a fact. The pull request the file names is merged (`gh pr view`), the squash sha is on main, and where a deploy is claimed the live route answers with the new version from the live address. **Merged is not live.** A `200` from a route that answers `200` for anything is not a probe; the probe finds a sentence only the new version has.
4. **What it started is stopped.** Section 10's process table lists what the session started and what stopped each one. The tick's census (chapter 10) confirms it.

## The read ladder

When `READ:` fails, in order, and the operator is asked only at the last rung:

1. `git fetch --all`, retry against `origin/main` and `origin/<branch>`.
2. By the sha on the `PUSHED:` line: the hosting API's contents endpoint with `?ref=<sha7>` (a short sha works, and it resolves after the branch is deleted); then `git show <sha7>:<path>` after a fetch. Never `git fetch origin <sha7>`: fetch-by-sha wants the full 40 characters and the block carries seven.
3. Off disk, in the worktree: `<worktree>/<file>`. An unpushed worktree still has it.
4. `git log --all --diff-filter=A -- "**/<basename>"` for a rename or a move.
5. The other repositories on the machine, for the basename.
6. The hosting API for a repository not cloned locally.
7. Only then: "the briefing file at X is not reachable"; and meanwhile act on the pointer block's `SHIPPED`, `BLOCKERS` and `NEEDS OPERATOR` lines.

## The fold, in order

1. Read the whole file, top to bottom. Section 7 (needs the operator) and section 8 (owed and deferred) twice.
2. Act on a non-empty `BLOCKERS:` line before anything else.
3. Write the landed row: the clocks and one plain-English sentence of what changed for the operator, ending with the pull request and version.
4. Free the slot in the running table; move any waiting rows this landing un-gates to READY.
5. Fold section 7 into the operator's open questions, each with its recommendation, linked to its own record, never re-asked in chat if already asked once.
6. Fold section 8 into the owed registry with each item's trigger.
7. Lift any contract in section 10 verbatim into the prompts of the arcs that consume it.
8. Fold any `=== CHAIR UPDATE ===` block (a change the session wanted in a shared document it may not edit) into the board or the rules, on main.
9. Write the board's arc line and the dated log line.
10. **Stop the session by id, the same minute** (`claude stop <id>` on Claude Code; the adapters have the rest). A folded session left resident is pure cost: each one keeps its helper processes, its language servers and its shells alive.
11. Fill the freed slot from the top of the waiting table (chapter 3).
12. One line to the operator: `✅ <arc> session N folded: <what changed>.` And, in the same turn, `🚀 <next arc> launched on <model> at <effort> in slot K.`

## Re-sync before every triage

Sessions merge on their own schedule. Before folding anything, the chair fetches main and reads the new commits: a merge with no briefing yet is still a landing to record, and a task another arc already shipped is not dispatched again. **Validate the task is still outstanding before dispatching**; a session's own handoff can be stale by the time it is read.

That validation is a check, not a feeling. Twice in one day on the estate that wrote this, the chair dispatched an owed item whose work main had already done: once all three items had been fixed by two merges before the prompt was written, once four of five. Both sessions spent their first hour rediscovering it. [`scripts/done-on-main.py`](../scripts/done-on-main.py) is the check: given the briefing the item came from (or a start commit), the files it names and its title, it lists every commit on `origin/main` since then that touched those files, and every commit whose subject shares the title's uncommon words (a fix can land in a file the item never named). Exit 0 means nothing moved; exit 1 means read each named commit before writing the prompt. It refuses rather than answer from a failed fetch, and refuses rather than report "clean" when none of the files resolved, because a clean answer from a check that saw nothing is worse than no answer.

## Validate before you relay

A contract lifted from a briefing into a prompt is checked against the live code first (the column exists, the status value is spelled that way, the route answers). A version in a prompt is read from the version file and the tags at write time, never remembered. A path in a prompt exists on the target branch. Three of the last several relays on the estate that wrote this caught a real defect at this step: a taken version, a wrong path, a renamed script.

## What is gated, still

Self-merge is the default; the chair validates after the fact rather than approving before it. Three things stay gated, surfaced to the operator instead of merged by the session: irreversible or destructive production actions, database schema migrations, and a cross-arc conflict the chair's validation turns up. And nobody merges something another arc still needs open.
