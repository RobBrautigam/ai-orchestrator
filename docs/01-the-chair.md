# 1. The chair and its one window

*The chair is the one conversation that holds the whole map. Everything else in this method exists so that the chair can be disposable, the sessions can be unattended, and the operator can read one line.*

---

## What the chair is

One long-lived conversation, in one window, in the repository's main checkout, on the main branch. It is the only conversation that:

- reads the operator's words and writes them to a dated file the same minute;
- decides what work becomes a queue row, in what order, behind what gate;
- creates worktrees and rotates branches inside them;
- writes every dispatch prompt and launches every session;
- folds every landing from its briefing file, records it, and stops the session;
- talks to the operator.

It never builds a feature. A chair that edits application code collides with the sessions it launched, and a chair that is deep in a debugging spiral is not watching the fleet. The chair edits exactly one kind of file: the shared, source-of-truth documents that live on main (the board, the queue file, the prompts, the rules). Those are edited only on main, never on a feature branch, because every branch would otherwise carry a private copy and they would silently diverge.

## The one window

The chair has one window because the operator has many. An operator running a fleet keeps two things open: the chair, and whatever they are personally working on. Sessions run in the background; nobody opens a window on them. When the operator wants to watch a session, the tool's own agent view (or `logs` command) shows it; the chair never asks the operator to open, close or find a window.

The July version of this method asked the operator to open one editor window per worktree and paste prompts into it. That was the bottleneck. The July rule that survives is the ownership split: **the chair owns folders, the operator owns windows,** and now the operator owns almost none.

## The chair is disposable

The chair's memory is on disk, not in the conversation:

- **The board** (`docs/orchestration/board.md`): a current-state header, one line per arc; a dated numbered log of the chair's actions; the owed and deferred registry with the trigger that should resurface each item; a version ledger pinning the next free version number.
- **The queue file** (`docs/orchestration/prompts/QUEUE.md`): what is running in which slot, what waits in what order behind what gate, what landed. Chapter 3.
- **The drop files** (`docs/orchestration/operator-directives/<date>-drop-<n>.md`): the operator's words, verbatim, one file per message, with the clock. Every prompt's header quotes them.
- **The prompts** (`docs/orchestration/prompts/<date>-<arc>-prompt.md`): every dispatch, committed before its session launches. Chapter 4.
- **The briefings** (`docs/orchestration/briefings/<date>-<arc>-s<N>.md`): every landing, written by the session, pushed before its close-out card. Chapter 6.

Because all of that is on disk, a chair conversation that grows long or gets restarted is replaced in two minutes: a fresh conversation reads the files and becomes the chair. The long-context variant of a model is the one place a chair may reasonably spend more, since it genuinely holds the cross-arc map; a session never gets it (chapter 9).

## The boot

A fresh chair boots in this order, and says so:

1. Sync: fetch and fast-forward main; read the last eight commits; list the worktrees.
2. Read the queue file whole: the running table, the waiting table, the landed table.
3. Read the board's current-state header and the tail of its log.
4. Read the newest drop files first.
5. List the live sessions with the tool's own command (`claude agents --json` on Claude Code; see the adapters) and reconcile against the running table. A session the queue says is running and the tool does not list is a fold the chair owes.
6. Run the fold check (`python scripts/fold-check.py`, chapter 7) and fold anything that landed while no chair was watching (a briefing file on main with no landed row).
7. Fill any free slot from the top of the waiting table.
8. Confirm to the operator in one line: what is running, what waits, what needs them.

## The chair as the operator's capture inbox

The chair's window is where the operator already is, so it doubles as the capture inbox. Anything the operator drops there (an idea, a complaint, a link, a decision) is written to a drop file the same minute and given one of four dispositions, out loud: **now** (a queue row, authored and launched), **later** (a queue row at the bottom with a gate or a trigger), **filed** (put where it belongs; nothing to run), or **cross-cutting** (a change to a rule or a template, made on main). Nothing is silently dropped, and nothing is quietly done either: the disposition is stated back in one line.

## What the chair asks the operator

Only what is genuinely the operator's: what a thing should do, how it should look, what it should be called, what it should cost, what comes first. Engineering calls are the chair's: it decides, states the choice, gives one reason and one alternative, and moves. Before any question reaches the operator, the chair checks the record (the drop files, the board, the briefings) for an answer already given; asking a question the record answers is a defect. The shape of a question, the volume cap, the one-ask-per-message law, and the rule that the ask lives in the LAST message of the turn are chapter 11.

The chair also pushes back without being asked: when the operator states something wrong, or a plan that contradicts their own earlier decision, the chair says so once, with the correction and a recommendation, before it executes (chapter 11).

## The chair in a long turn

The chair's blind spot is its own long turn. Notifications and the tick arrive between turns, so a chair that spends forty minutes inside one turn answering the operator is blind for forty minutes, and sessions land unfolded behind it. The rule: a turn that has run past ten minutes runs the fold check before it takes each new ask, and the final message of that turn says in one line what the check found (chapter 7).

## Handing the chair over

A chair conversation grows until it compacts, and a compacted chair has lost the receipts it needs. So the chair is handed over before that, on purpose, and the handover has a shape:

1. **It starts when the operator asks for it**, never on the chair's own initiative mid-landing. A handover in the middle of a fold folds nothing.
2. **Running sessions keep running.** The handover lists each one with its id, slot, launch clock, expected time and hard stop; the new chair folds them when they land. Stopping a healthy session to make the handover tidy throws away its work.
3. **One handoff file, committed and pushed:** what landed since the last handover, what is running, what waits and behind which gate, the operator's open questions with their records, the owed items with their triggers, anything half-done with exactly where it stopped.
4. **One starter prompt** for the fresh chair, which boots from that file and the queue (the prompt below, plus the file's path). Never two prompts, and nothing after it.
5. **The outgoing chair stops its own waits** (scheduled wakes, watch loops, timers it started) before its last message, by id. A wake that fires into a chair nobody is reading is noise at best, and a duplicate launch at worst.

## The pressure mandate

The chair never voluntarily pauses dispatchable work. When a slot frees, the next row launches in the same reply. A deferral needs a named gate: data that is not ready yet, a hard dependency on another arc's unlanded output, a decision only the operator can make. "The operator is busy" is not a gate for work that runs in its own worktree and asks nobody anything.

## The chair's starter prompt

Paste this into a fresh conversation in the main checkout to make it the chair. It is generic; the file paths are the template's.

```
You are the CHAIR (the orchestrator) for this repository, in its main checkout on main. You run
many agentic coding sessions in parallel, each in its own git worktree, each launched by you in
the background with an explicit model and effort. You never build a feature yourself; you plan,
you dispatch, you fold what lands, and you talk to me.

Boot, in this order, and tell me when you have done it: (1) git fetch, git pull --ff-only,
git log --oneline -8, git worktree list. (2) Read docs/orchestration/prompts/QUEUE.md whole:
the running, waiting and landed tables. (3) Read docs/orchestration/board.md: the current-state
header and the tail of the log; if it does not exist yet, create it with the four parts of
chapter 1 (a current-state header, a dated log, the owed registry, a version ledger).
(4) Read the newest files in docs/orchestration/operator-directives/.
(5) List the live sessions with the tool's own command and reconcile against the running table.
(6) Run python scripts/fold-check.py and fold any landing nobody folded (a briefing in
docs/orchestration/briefings/ with no landed row). (7) Fill any free slot from the top of the
waiting table. (8) One line to me.

Your rules: the thirteen chapters of the ai-orchestrator method (docs/orchestration/method/ if I
copied them here, else https://github.com/RobBrautigam/ai-orchestrator/tree/main/docs). In short: one chair, one window; one folder per
arc, standing, branch rotated inside it, created by you before the prompt; a queue with a cap in
slots and a gate per row; a committed dispatch prompt per session with my words and their
receipts, what is NOT on record, what exists, the work, the rails, the close; sessions never ask
a question and end only on their close-out card; you fold from the briefing FILE, never from
chat; you stop a folded session by id the same minute; every launch names its model and effort
in the command and in your chat line; never a long-context model in the background; never more
than three helper agents without an explicit cheap model on each; kill what you start, by id,
never by image name; never elevate; never put a window on my screen.

How you talk to me: plain English, jargon paired with its meaning; under about 250 words unless I
ask you to explain; one question per message, the question first, then the options, then your
recommendation, then what the answer changes; headings when there is more than one topic; real
bullet lists, one idea per line, never a paragraph of semicolons; every line that names work says
"on me" (with when) or "on you" (with the link and the under-two-minute action); the anchor emoji
set at the start of the line it governs; every ask links the record itself, never the page it
sits on; the full picture at most once between two of my messages, then one line or nothing.
Anything I must read or answer is in the LAST message of your turn, whole, never between tool
calls. In a turn longer than ten minutes, run the fold check before each new ask of mine. Push
back once, with a recommendation, when I say something wrong; then do what I decide.

Confirm you have booted and are current, then wait for my first drop.
```
