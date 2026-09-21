# 8. The hourly tick

*The tick is the chair's clock. Every hour, whether or not anything landed, the chair runs the same twelve steps in the same order and writes the same three counts. A fleet that is only checked when something happens is a fleet that stalls quietly.*

---

## Why a fixed cadence

Landings are event-driven (chapter 7): the chair folds a session the minute its file appears. But three things do not raise events: a session that stopped early and is waiting for nobody; a slot that stayed free because the top waiting row's gate quietly opened; and a process left resident by a session that ended an hour ago. The tick exists for those. It is scheduled inside the chair's own tool (a recurring prompt on the chair's session, never a scheduled task or a daemon on the operator's machine) and it costs one short turn an hour.

## The twelve steps

1. **Sync.** `git fetch origin main`; read the commits since the last tick; list the worktrees.
2. **List the live sessions** with the tool's own command. Reconcile against the running table: every running row has a live session; every live session has a running row. A mismatch is written down before it is fixed.
3. **Find the stalls.** For each running session, read its state and its last output. Done with a card up: fold it (chapter 7). Idle with no card: read the last line. A provider refusal (a concurrent-session limit, a rate limit) is a plan switch or a re-queue, never a wait. A progress note or a question with the turn ended: answer it the same minute ("carry on; record the question in section 7"). Waiting on a permission nobody can answer: stop it by id, fix the launch shape, re-queue.
4. **Fold the landings** nobody folded: a briefing file on main with no landed row.
5. **Refill the slots.** Re-read the gates on the waiting table (a card answered, an arc landed, a date passed); move the un-gated rows to READY; launch top-first until the cap.
6. **Run the census** (chapter 10): resident sessions, helper processes, orphans. Stop the orphans that pass the four-part proof, by id, and log each. Put the three counts on the board beside the running table.
7. **Check the shared configuration** the sessions load (the rules, the skills, the hooks), read-only: is it on main, level with the remote, clean. A finding is fixed the same day on a branch with a pull request, never raised with the operator.
8. **Re-read the operator's open questions.** Anything answered in chat since the last tick is settled on its record the same turn. Anything asked three times moves from chat to the standing list the operator can open at any hour, and is not asked in chat again.
9. **Re-check the standing rails** that have a mechanical test: no scheduled task or startup entry the operator did not name; no session on a long-context model; every running row with a model and effort filled in.
10. **Rewrite the at-a-glance line** in the queue file with the clock.
11. **Commit** the queue file and the board, on main.
12. **One line to the operator, or nothing.** If something changed since the last operator message: one line per change, each opening with its anchor (chapter 11). If nothing changed: nothing. The full picture is sent at most once between two operator messages; the tick never re-sends it.

## What the tick never does

- Ask the operator a question it asked before.
- Launch a row whose gate is open only in the chair's opinion.
- Start anything that outlives the tick on the operator's machine.
- Elevate, or put a window on the screen, to learn something it could read from documentation.
- Kill by image name.

## Measuring the tick

Three numbers the tick writes each hour let the operator see the fleet's health without reading anything else: sessions busy over the cap; the median minutes from a session's card to its fold (three minutes on a well-run estate; forty when the tick is the only thing that folds); and orphan processes found. A weekly script over the tick's own log lists the three worst sessions by idle time before their card, so the dispatch template can be tightened where the stalls actually happen.
