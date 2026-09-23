# 3. The dispatch queue

*One committed file answers three questions at any hour: what is running, in which slot; what waits, in what order, behind what gate; what landed, and what changed for the operator. The chair writes it at every launch and every fold. A generic example is in [`templates/QUEUE.md`](../templates/QUEUE.md).*

---

## Words

- **Slot.** One unit of the cap. An ordinary session takes one; a design session (the model at its most expensive setting, doing look-and-feel work) takes two. The cap is stated in slots, not sessions.
- **Cap.** The number of slots that may be busy at once. It is the operator's word and is written at the top of the file with the date and clock it was set, and the word before it is kept underneath for the record. It is a cost decision and a shared-limit decision (chapter 9): at the cap the fleet stays inside the account's concurrent-session limit, and the first refusal from the provider is reported to the operator the same minute rather than retried. When the operator lowers it, the fleet winds down: running sessions finish, and freed slots are not refilled until the count is under the new cap.
- **Badge.** The number a row gets when it joins the queue, kept for life, so the board, the chat and the operator can point at it ("badge 28"). It is not a rank; the rank is the row's position.
- **Gate.** What a waiting row needs before it may launch: nothing; another arc's landing; a card the operator has not answered; data that is not fresh yet. A row with an open gate never launches, however free the slots.
- **READY.** A waiting row whose prompt is authored and whose gate is open. The tick launches READY rows top-first.

## The three tables

### Running

One row per busy slot, ordered by slot. Columns: slot, repository, session (its name and short id), model and effort, worktree, the clock at launch, and one plain-English sentence of what it does and what the operator will be able to see when it lands. A free slot is a row too, with the clock it freed at and the line "on the chair: filled with the next authored prompt."

The plain-English sentence is the point of the table. The operator reads it; the tool's own session list shows ids and states, never why a session exists.

### Waiting

Rows in launch order, top first. Columns: badge, repository, arc (one paragraph: what and why, with the operator's words that asked for it), worktree (an existing standing worktree, or "new at launch"), model and effort, prompt (its committed path, or "to author"), gate, the date queued.

The bottom of the queue is a real place. Work the operator has named as low priority sits there by their word and does not creep up because a slot happens to be free.

### Landed

Newest first, every row dated: session, repository, the clock at launch, the clock at the fold, and one sentence of the result in plain English, ending with the pull request and version where there is one. The sentence says what changed for the operator, not what the session did to get there ("every video you ever sent now says what was said in it, or says why it could not be read", not "added a transcription fallback").

## The at-a-glance line

Under the title: `N running in N of CAP slots | N waiting (N READY) | N landed since <date>`, with the clock it was written at. The chair rewrites it at every launch and fold. A reader who reads nothing else reads this.

## The launch

When a slot is free and a READY row is at the top of the waiting table, the chair, in one turn:

1. Confirms the worktree exists (or creates it) and rotates its branch (chapter 2).
2. Commits the dispatch prompt file if it is not already committed (chapter 4).
3. Launches the session from the worktree with the tool's own background command, **the model and effort explicit** (the adapters have the exact shape).
4. Moves the row from waiting to running with the session id and the clock.
5. Writes the arc's board line.
6. Says one line to the operator: `🚀 <arc> session N launched on <model> at <effort> in slot K: <what it does>`.

## The fold

When a session's briefing file lands (chapter 7), the chair, in one turn: reads the file; runs the close test; writes the landed row; frees the slot; stops the session by id; and fills the slot from the top of the waiting table. The same minute, not the next tick.

## What the file is not

It is not a task tracker. A queue row is a session-sized unit of dispatch, not a backlog item; the backlog lives wherever the operator keeps it, and the chair pulls rows from it when the operator says. It is not a log either; the board's dated log carries the chair's actions. The queue file is the fleet's current truth, rewritten in place, and its git history is the record of how the truth moved.

## The parity check

Because the file is as fresh as the chair's last write, anything that displays it alongside the tool's own live session list prints a parity line ("the queue file says 6 running; the machine says 5"). A mismatch is a fold the chair owes or a launch it forgot to record, and the tick (chapter 8) reconciles it every hour.
