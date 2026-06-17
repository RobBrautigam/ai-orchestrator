# Orchestrator Briefing Template

The reusable prompt the orchestrator pastes into parallel sessions to extract
**decision-grade intelligence** — not a terse status line. Copy the block below into
each running session; paste the filled-in briefings back to the orchestrator for triage.

**This same briefing is also the standard close-out block** every session emits at the
end of its work (its own block, right before the next starter prompt) — so close-outs
stop being sporadic in size and placement.

> **Two obligations, every session:** (1) emit this briefing as a copy-paste block in
> the chat at close, AND (2) include that same requirement in **any starter prompt it
> writes** for a follow-up session (a close-out line: *"emit the orchestrator briefing
> block at session close"*). The second one is the root-cause fix — a starter prompt
> that omits that line gives the next session no idea it owes a briefing, and the
> discipline silently decays.

## The principle (why this beats a status line)

A terse "branch clean, PR merged, next is X" captures **state** but drops **judgment** —
which is the actually-valuable orchestrator intel:

- **Intent vs actual divergence** — did the session do what you meant? over-scope?
  wrong-scope? a pivot? wasted cycles? (Example: a data-pull session that fetched ~2,000
  records when you wanted ~150 — a multi-hour over-scope a status line would have hidden
  as "step done.")
- **Honest misses / process lessons.**
- **Time-sensitive opportunities the work surfaced** (e.g. a refactor that exposed a
  systemic gap well beyond the file you touched).

Extract the judgment. Be thorough where it's valuable; terse where it's routine.

## The prompt (paste verbatim into each running session)

```
ORCHESTRATOR DEEP-STATUS REQUEST. Pause and give the orchestrator a real briefing on this session — do NOT start new work, do NOT ship, do NOT abandon in-progress work; just report. I need intelligence to triage parallel sessions, NOT a terse status line. Be THOROUGH where it's valuable (divergences, surprises, opportunities, honest misses) and TERSE where it's routine (git plumbing). Lead with the single most important thing: did this session do what the operator actually intended, and did anything diverge?

Gather first (don't re-explore the codebase): git status -s, git log --oneline -8, your branch, your PR (gh pr view --json number,state,isDraft,mergedAt 2>/dev/null), and your roadmap position. Then reply with this briefing:

=== ORCHESTRATOR BRIEFING ===

1. INTENT vs WHAT HAPPENED (lead here — most important)
   • What the operator / the plan ACTUALLY asked for (the real intent, 1 line).
   • What this session ACTUALLY did.
   • DIVERGENCE: over-scope, wrong-scope, scope-cut, a pivot, wasted cycles, a misread — be honest. If it matched intent cleanly, say so plainly.

2. STATE (facts, terse)
   • Stream / project · repo / worktree / branch.
   • Session state: mid-task | idle-awaiting-next | blocked-on-operator.
   • PR(s): #num + draft|open|merged + SHA. Git: clean / N uncommitted / pushed? / ahead-behind.
   • Prod/live: live | shipped-dark | branch-only-unmerged | n/a. Versions/tags shipped.

3. WHAT SHIPPED + THE DECISIVE FACTS
   • What landed (bullets).
   • The key numbers/facts that drove the decisions (counts, costs, measurements, cross-checks) — the data the orchestrator should know.
   • VERIFIED vs ASSUMED: flag which load-bearing facts you VERIFIED against live code/DB vs ASSUMED — especially any cross-stream claim — and name what you did NOT verify. (The orchestrator re-validates anything that reshapes priorities or crosses streams before relaying it.)

4. MISSES / LESSONS / WHAT WENT SIDEWAYS (honest)
   • Bugs, wrong assumptions, wasted effort, anything you'd do differently, any process lesson worth carrying. "None" if clean.

5. OPPORTUNITIES SURFACED (flag time-sensitive ones)
   • Any high-value thing this work exposed that we have NOT acted on, and whether it's urgent. The operator decides whether to prioritize it.

6. ROADMAP POSITION
   • Where this sits in its stream → the immediate next step → what's after.

7. NEEDS THE OPERATOR / BLOCKERS
   • Decisions, credentials, approvals waiting — or NONE.

8. OWED / DEFERRED (with the trigger that should resurface each)
   • e.g. "adversarial code review — trigger: before merge." Or NONE.

9. YOUR RECOMMENDATION (priority-ordered, one-line why each)
   • What you think should happen next with this stream.

10. CONTRACTS (produced / consumed) — the cross-stream glue
   • PRODUCED: if another worktree must build against something you created (a schema column, a status value, a published/visibility rule, an API/route/heading/string both sides depend on), state it as a named, copy-paste CONTRACT block the orchestrator can lift VERBATIM into the consumer's prompt — exact names/values, not prose.
   • CONSUMED: name any contract you built against + confirm you matched it. NONE if standalone.

11. MERGE TARGET & GATE
   • PR # → target branch → the gate (ready-to-merge | draft | blocked-on-<X> | needs-operator-say-so) → auto-deploy target. So the orchestrator can merge the safe ones and hold the gated ones, and never double-assign a shared repo.

=== END BRIEFING ===
```

## Usage notes

- **Repo-agnostic** — paste the identical block into every parallel window.
- **Report, don't act** — a mid-task window snapshots its state, it doesn't barrel ahead or wrap up early.
- **As a close-out block:** every session ends with this filled in, as its own block, immediately before the next starter prompt. Same fields, same order, every time.
- **Route the orchestrator-owned bits:** if a session would otherwise edit a shared source-of-truth doc the orchestrator owns (e.g. `docs/architecture/PLATFORM.md`), it appends a separate `=== ORCHESTRATOR UPDATE ===` block instead of editing the doc on its own branch.

## Evolution log (keep improving this)

- **v1 (retired):** a fixed 12-field status block. Captured state but flattened judgment —
  it would have hidden an over-scoped data pull and a time-sensitive opportunity the work
  surfaced.
- **v2:** the 9-section briefing — leads with intent-vs-divergence, forces honest
  misses/lessons and surfaced opportunities. Validated across parallel sessions; it caught
  cross-cutting issues a status line would have dropped.
- **v3 (current):** added **§10 Contracts (produced/consumed)** + **§11 Merge target &
  gate** + a **verified-vs-assumed** line in §3. Driven by a multi-worktree day where
  (a) cross-stream dependencies were tracked ad-hoc and were error-prone, (b) two worktrees
  nearly made the same change to a shared repo, and (c) a briefing claim that reshaped
  priorities had to be re-verified against the actual code before relaying. §10 makes
  contracts copy-paste-able; §11 makes merges/ownership explicit; the §3 line forces
  honesty about what was actually verified.
- *Future improvements go here* — e.g. a token/cost line.
