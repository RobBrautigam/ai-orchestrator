# Running Claude Code with Worktrees + an Orchestrator

*How I run many Claude Code conversations in parallel on one codebase, coordinated by a single "orchestrator" conversation. A general method, not tied to any one project — copy the prompt near the bottom into your own repo and go.*

---

## The big idea

A normal Claude Code session does one thing at a time. This setup runs **many sessions at once**, each in its own isolated copy of the repo, all coordinated by **one long-lived "orchestrator" conversation** that holds the big picture.

Think of it like a team:

- **The orchestrator** is the tech lead. It never writes feature code itself. It holds the roadmap, decides what each stream works on, writes the instructions, and keeps the master plan up to date.
- **Each worktree session** is an engineer. It owns one stream of work end-to-end (build → test → ship) and reports back when done.
- **I'm the operator.** I copy-paste prompts from the orchestrator into each worktree window, and copy the worktrees' reports back to the orchestrator. That's basically my whole job — relay messages and make the calls only I can make.

The result: 5–8 streams of work moving at the same time, without them stepping on each other.

---

## The one piece of plumbing: git worktrees

A **git worktree** is a second (third, fourth…) working copy of the same repo, each checked out to its own branch, all sharing the same underlying git history.

```
C:/dev/myrepo            ← main branch   = the ORCHESTRATOR window
C:/dev/myrepo-feature-a  ← branch feat/a = worktree session A
C:/dev/myrepo-feature-b  ← branch feat/b = worktree session B
C:/dev/myrepo-feature-c  ← branch feat/c = worktree session C
```

Why this matters: each Claude conversation gets its **own folder and branch**, so two sessions editing different things at the same time can't corrupt each other.

> **The one hard safety rule:** one Claude conversation per folder. Never run two conversations in the same working directory — branch switches in one will yank the other's files out from under it. Different worktree = safe. Same folder = corruption.

Claude can create and remove these for you on demand (it just runs the git commands):

```bash
git worktree add C:/dev/myrepo-feature-a -b feat/a   # spin one up
git worktree remove C:/dev/myrepo-feature-a          # tear it down when done
```

So you can literally say *"spin up a worktree for X"* and the orchestrator creates the folder + branch; say *"that one's merged, clean it up"* and it removes it.

---

## How it all fits together

```
                     ┌───────────────────────────────────────┐
                     │   ORCHESTRATOR  (main branch)           │
                     │   • holds the board + the master plan   │
                     │   • writes copy-paste starter prompts   │
                     │   • triages the briefings I paste back  │
                     │   • relays dependencies between streams │
                     │   • never does feature work itself      │
                     └─────────────────┬─────────────────────┘
            starter prompt  ▲          │          ▲  briefing
            (I paste in)    │          ▼          │  (I paste back)
            ┌───────────────┼──────────┼──────────┼───────────────┐
            ▼               ▼          ▼          ▼                ▼
      ┌──────────┐    ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
      │ worktree │    │ worktree │ │ worktree │ │ worktree │ │ worktree │
      │    A     │    │    B     │ │    C     │ │    D     │ │    E     │
      │ 1 convo  │    │ 1 convo  │ │ 1 convo  │ │ 1 convo  │ │ 1 convo  │
      └──────────┘    └──────────┘ └──────────┘ └──────────┘ └──────────┘
       own folder      own folder   own folder   own folder   own folder
       own branch      own branch   own branch   own branch   own branch
                       (all share one git history underneath)
```

---

## The loop (this is the whole workflow)

```
  ME (operator)               ORCHESTRATOR                 WORKTREE SESSION
       │                           │                             │
       │ "let's work on X"         │                             │
       ├──────────────────────────►│                             │
       │                           │ writes a starter prompt      │
       │ ◄─────────────────────────┤                             │
       │  copy-paste the prompt ───┼────────────────────────────►│
       │                           │                       does the work
       │                           │                   (brainstorm → build → ship)
       │                           │                             │
       │ ◄─────────────────────────┼──────────────  emits an
       │  copy-paste the briefing  │                ORCHESTRATOR BRIEFING
       ├──────────────────────────►│                             │
       │                  triages + updates the board             │
       │ ◄─────────────────────────┤ next starter prompt          │
       │           … repeat across every worktree …               │
```

Every cycle: **prompt out → work happens → briefing back → board updated → next prompt.** I'm just the courier between windows.

---

## The building blocks

**1. Copy-paste starter prompts.** When I want to start or continue a stream, the orchestrator hands me a complete prompt I drop into that worktree's window. A good one names the worktree + branch, has a quick git pre-flight, states the goal, commits to **one clear path** (no open questions the next session will bounce back to me), lists the guardrails, and ends with a standard close-out instruction.

**2. The orchestrator briefing.** Every worktree session ends by emitting a **standard 11-section "briefing"** as a copy-paste block:

1. Intent vs what actually happened
2. Current state (branch / PR / deploy)
3. What shipped + the decisive facts (and what was verified vs assumed)
4. Misses / lessons
5. Opportunities surfaced
6. Roadmap position
7. What needs me / blockers
8. Owed / deferred items + what should trigger them later
9. The session's recommendation
10. Contracts produced / consumed *(see #6 below — this is what matters most at scale)*
11. Merge target + gate *(see #10 below)*

I paste that back to the orchestrator, which triages it and tells me what's next. The full copy-paste block lives in [`orchestrator-briefing-template.md`](orchestrator-briefing-template.md). (It's just a fixed template plus the discipline that every session fills it in at close — that consistency is what makes the hand-offs clean.)

**3. The durable board (the orchestrator's memory).** The orchestrator keeps **one markdown file on the main branch** — a running, dated, numbered log of every meaningful event and the state of every stream. This is the key trick: because the plan lives in a file, not just in the chat, **the orchestrator conversation is disposable.** If it gets long or I restart it, a fresh conversation just reads the board and instantly becomes the orchestrator again.

**4. Cross-stream coordination ("contracts").** When stream A builds something stream B depends on, the orchestrator carries that "contract" between them through the prompts — so B builds against the real thing instead of guessing. Shared source-of-truth docs are only ever edited on the main branch, so they never fork across worktrees.

**5. Worktrees on demand.** Ask for a new stream → orchestrator runs `git worktree add` (new folder + branch). Stream's merged → `git worktree remove` cleans it up. Spin up and tear down as the work demands.

---

## The building blocks that make it scale past ~3 streams

The five above get you started. These five are what makes the difference between "parallel" and "parallel chaos" once 5–8 streams run at once.

**6. Contracts — the cross-stream glue.** The first thing that breaks at scale: stream B needs something stream A is building (a new database column, a status value, a shared string both sides parse). Don't let it live in anyone's memory. When a stream produces something another will consume, it writes a **named contract** — exact names and values, copy-paste-ready — in its briefing. The orchestrator lifts it *verbatim* into the consumer's prompt, so B builds against the real thing instead of guessing. Almost every cross-stream bug traces back to a dependency described in prose instead of pinned exactly.

**7. One owner per shared repo.** When several streams need to touch the *same* repo (e.g. a frontend everyone depends on), funnel ALL changes to it through ONE designated worktree. A stream that needs a change there **emits a contract** for the owning worktree instead of editing the repo itself. This stops two streams silently making conflicting edits. (On the day this section was written, two streams were about to make the same frontend change — this rule is why they didn't.)

**8. The orchestrator validates before it relays.** A briefing is a *claim*, not a fact. Before acting on anything that reshapes priorities or crosses streams, the orchestrator re-checks it against the actual code/DB — it never rubber-stamps, not even its own earlier decisions. (A "this only publishes to one platform" claim that would've re-ranked the whole roadmap turned out true — but I only knew that because I read the code, not because a briefing said so.) The briefing format asks each session to mark what it **verified vs assumed**, so the orchestrator knows exactly what to re-check.

**9. An owed/deferred registry + a "what's blocked on what" view.** Every briefing lists owed/deferred items + the trigger that should resurface each. Collect those in ONE place on the board, alongside a simple gate view (which stream is blocked on which). Otherwise a deferred item with a future trigger quietly evaporates and you lose the dependency graph.

**10. A merge protocol.** Each briefing states its PR + the merge gate (ready / draft / blocked-on-X / needs-your-say-so) + what auto-deploys on merge. The orchestrator merges the safe ones, holds the gated ones, and never merges something another stream still needs open.

---

## The generic prompt (paste this into your own Claude Code to set it up)

```
You are my ORCHESTRATOR for this repo. I run multiple Claude Code conversations at once,
each in its own git worktree, working on separate streams of work in parallel. You hold the
big picture and coordinate them. You do NOT write feature code yourself (that would collide
with the worktrees) — you plan, you write the prompts I paste into each worktree, you process
what they report back, and you keep one durable "board" file up to date.

Your responsibilities:

1. DURABLE BOARD. Maintain a single markdown file on the main branch (e.g.
   docs/orchestration/board.md) as your memory. Whenever something meaningful happens, append
   a short dated, numbered entry: what changed, what's in flight, what's blocked, and what each
   worktree is doing. Also keep an owed/deferred registry (each item + the trigger that should
   resurface it) and a simple "what's blocked on what" gate view. This file is the source of
   truth, so even if this conversation restarts, a fresh one can read it and become the orchestrator.

2. STARTER PROMPTS. When I want to start or continue a stream, give me a complete copy-paste
   starter prompt for that worktree's window. It must: name the worktree + branch, include a
   short git pre-flight, state the goal, commit to ONE clear path (never bury a decision inside
   it for the next session to bounce back to me), paste in any contracts it depends on (see #5),
   list the constraints, and end with a standard close-out instruction.

3. BRIEFINGS. Tell every worktree session to END by emitting a structured "orchestrator
   briefing" as a copy-paste block: (1) intent vs what happened, (2) state (branch/PR/deploy),
   (3) what shipped + key facts + what it VERIFIED vs ASSUMED, (4) misses/lessons,
   (5) opportunities, (6) roadmap position, (7) what needs me / blockers, (8) owed/deferred +
   triggers, (9) recommendation, (10) CONTRACTS produced/consumed, (11) merge target + gate.
   When I paste a briefing back, triage it, update the board, and give me the next prompt.

4. WORKTREES ON DEMAND. When a new parallel stream is needed, give me the exact
   `git worktree add <path> -b <branch>` command (or run it yourself); when one is done, the
   `git worktree remove` cleanup. One Claude conversation per worktree — never two in the same
   folder.

5. CONTRACTS + ONE OWNER PER SHARED REPO. When one worktree produces something another depends
   on, capture it as a NAMED contract (exact names/values, copy-paste-ready) and paste it
   verbatim into the consumer's prompt — don't paraphrase. When multiple streams need the same
   repo, funnel ALL changes to it through ONE designated worktree; the others emit contracts for
   it instead of editing it. Edit shared source-of-truth docs ONLY on the main branch so they never fork.

6. VALIDATE BEFORE YOU RELAY. A briefing is a claim, not a fact. Before acting on anything that
   reshapes priorities or crosses streams, re-check it against the actual code/DB yourself —
   never rubber-stamp, not even your own earlier calls. Handle merges per each briefing's stated
   gate: merge the safe ones, hold the gated ones, never merge something another stream still needs open.

7. ASK FIRST, THEN PROMPT. If a decision is genuinely mine, ask me one clear question first;
   don't make the next session ask it back through me.

Start by reading the repo, then propose how to split the current work into parallel worktree
streams. Maintain the board from here on. When I say "go," hand me the starter prompts.
```

---

## Why it works

- **Parallelism without chaos.** Worktrees give isolation; the orchestrator gives coordination. You get the speed of many sessions without them corrupting each other.
- **The plan outlives the chat.** Because the board and master docs live in files on the main branch, no context is lost when a conversation ends — you can always reboot the orchestrator from the board.
- **Low operator overhead.** Day to day, my job is mostly copy-pasting prompts out and briefings back, and answering the occasional "this one's your call" question. The system holds the complexity, not me.

**Tips:** keep the orchestrator out of feature work (it only edits shared docs on main); enforce one-conversation-per-folder; make every starter prompt commit to a single path; and make every session end with the briefing. Those four habits are what make it run smoothly.

---

## Files in this repo

- **[README.md](README.md)** — this playbook (the method, the diagrams, the orchestrator prompt).
- **[orchestrator-briefing-template.md](orchestrator-briefing-template.md)** — the full copy-paste briefing block every worktree session emits at close.

## License

[MIT](LICENSE). Use it, fork it, adapt it.
