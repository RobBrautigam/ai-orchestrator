# 6. The briefing file and the pointer block

*The file is the briefing. The block in chat is a pointer to it. The order is the safety model: write the file, commit, push, verify the push, and only then emit the block. Templates: [`templates/briefing.md`](../templates/briefing.md) and [`templates/pointer-block.md`](../templates/pointer-block.md).*

---

## Why the file comes first

In July the briefing was a copy-paste block. It was as long as the chat allowed, the operator carried it by hand, and the chair triaged from whatever survived the paste. Three things broke: a long session's block described only its last task and silently dropped a nine-project run from the same conversation; a block that pointed at "the message above" arrived alone; and a briefing the operator never pasted was a landing nobody folded.

The fix has two halves. The **file** is exhaustive and committed, so it cannot be lost and the chair reads it line by line. The **pointer block** is short and fixed-shape, so a machine can parse it and a human can glance at it, and it names the file and the exact command that reads it.

## The eleven sections

Every briefing has all eleven, in this order, with the number in the heading. `NONE` where a section genuinely has nothing; never omitted.

1. **Intent against what happened.** What was asked (the prompt's words), what was done, and the divergence named honestly: over-scope, under-scope, a pivot, wasted cycles, or "matched cleanly." A table works well: one row per item of the prompt's work list.
2. **State at close.** Branch, pull request and its state, the squash sha, the deploy and its verification, the live route probed, tests, the walk, the commits, metered spend, local processes stopped, and the effort line (below).
3. **What shipped and the decisive facts.** What landed; the numbers that drove decisions; the research pass with every source and its date; **verified against assumed**, named per claim.
4. **Misses and lessons.** The session's own, honest: a rail crossed, a wrong assumption, a tool that lied, a wasted hour. `None` if clean, and it rarely is.
5. **Opportunities noticed and not taken.** Each a bullet, none built. Time-sensitive ones flagged.
6. **Roadmap position.** Where this sits in its arc, the immediate next step, what comes after.
7. **Needs the operator.** Each question in full: what it is in plain words, what is wrong today, what will be done on each answer, the recommendation with one reason, the alternative, what answering unlocks; and **the best guess recorded in the operator's absence**, with what was and was not done on that guess. Every sentence whose subject is the operator carries its receipt (the drop file and line) or reads "not verified."
8. **Owed and deferred.** Bullets, each with the trigger that should resurface it.
9. **Recommendation.** What should happen next with this arc, ranked, one line of why each.
10. **Contracts, and what this session started.** Contracts produced (exact names and values another arc builds against, copy-paste ready) and consumed; the table of every process this session started, with its id, its command line, and what stopped it.
11. **Merge target and gate.** The pull request, the target branch, the gate that was passed (tests, the reviewer, the walk, the probe), what deploys and what does not. The reviewer is written down in full: its kind (a fresh agent, never a fork), its model, its tool-use count, its scope echo read against the diff, and every finding with what was done about it.

After the eleven: **the loose-ends table**, one row per line of the prompt's work, rails and close, each tagged done, partial (with the gap named), queued (with where), spun off, or dropped (said so).

## The effort line

Section 2 carries one fixed-shape line filled from the tool's own usage record, so the chair can re-set model and effort defaults on data rather than opinion:

```
EFFORT | <session kind> | model <m> | effort <e> | session <id> | started <iso> | tokens_input <n> | tokens_output <n> | cache_read <n> | cache_write <n> | reviewer_findings <n> | subagents <n> | metered_spend $<n>
```

On the estate that wrote this, the line fed a running experiment comparing two effort levels on matched pairs of sessions; chapter 9 has the shape. The model on the line is the id the session actually ran on, read from its usage record, never the alias it was launched with (an alias moves when a new model lands). When the numbers come from a table the session reads, it prints the table's column names first and fills the line from them, so a renamed column fails loudly instead of filling the line with the wrong number.

## The completeness gate

Before writing, the session re-reads the conversation from its first message and enumerates every request; builds the inventory from `git log <start>..HEAD` (every commit and changed file accounted for), not from memory; supersets any interim briefing it emitted; and answers, explicitly, "does this cover every request and every commit from the start?" Recency bias is the named failure mode, and the nine-project loss is why the gate is mechanical.

## The pointer block

Fixed bookends, fixed lines, delivered inside a code fence, emitted exactly once, after the push is verified. `NONE` where a line does not apply. It must locate and validate the work even if nothing else survives: the file path, the ref and sha it was pushed at, the literal `READ:` command, the verdict, the facts line, three bullets at most of what shipped, what needs the operator, blockers, contracts, and the one-line next. It never points at chat prose.

```
=== ORCHESTRATOR BRIEFING ===
ARC: <arc> - session <N>
REPO: <repo> | WORKTREE: <path> | BRANCH: <branch>
FILE: <repo-relative briefing path>
PUSHED: <origin/ref> @ <sha7>
READ: git -C <main-checkout> fetch -q && git -C <main-checkout> show <ref>:<file>
VERDICT: <shipped-live | merged-not-deployed | branch-only-unmerged | design-only | blocked>
FACTS: v<X.Y.Z> | PR #<n> <state> | squash <sha7> | deploy <verified|not-verified|n/a>
SHIPPED:
- <plain-English line, three bullets max>
NEEDS OPERATOR: <full question or NONE>
BLOCKERS: <on-fire item or NONE>
CONTRACTS: <NONE | n in file>
NEXT: <one-line recommendation>
FULL DETAIL IS IN THE FILE. Read it line by line before triaging.
=== END BRIEFING ===
```

**The fallback, the only exception:** if the file could not be committed and pushed, the block carries all eleven sections inline with `PUSHED: NOT PUSHED - <reason>. FULL BRIEFING INLINE BELOW`.

## The fold lines: the part of the file the chair folds from

The eleven sections are for a reader. The fold is a set of writes (the landed row, the board line, the owed items, the rows the prompt carried), and a chair that composes those writes from prose composes them differently every time: an owed item reworded, a carried row forgotten, a result line that names a file path the operator cannot open. So the file ends with one fenced block the chair copies from and never rewrites:

```fold-lines
RESULT: Refunds now show on the customer's statement the same day; proven on a test account.
BOARD: payments-s4 landed, refund path synchronous, version 1.8.3 live
EFFORT: model opus, effort high, 74 minutes, 2.1M tokens in, 61K out
FINDINGS: reviewer 3, all fixed before the merge
SPEND: $0
OWED: Refund email copy || the receipt email still says "within 5 days" || the next copy pass on emails || next || operator: answer
CARRY: 3f9a2c1e done: section 3.3
```

- `RESULT`, `BOARD`, `EFFORT`, `FINDINGS` and `SPEND` appear exactly once. `RESULT` is under 200 characters, plain words, no file path: it is the line the operator reads. `BOARD` carries no pipe character, because it lands in a table.
- One `OWED` line per deferred item, five fields split by `||`: the title, the detail, the trigger that resurfaces it, the band (`now`, `next`, `later` or `someday`), and the owner. The owner is `null` (the chair does it), `operator`, or `operator: <reason>` with one of six reasons only the operator can act on: `answer`, `sign_in`, `send`, `call`, `money`, `in_person`. Anything else is refused, because "on the operator" without one of those reasons is work the chair could do.
- One `CARRY` line per row the dispatch prompt carried: `<id> done: <section>`, `<id> open: <reason>`, or `<id> superseded: <id>`. A carried row with no line is a row that silently stays open forever.

**The check:** [`scripts/fold-lines.py`](../scripts/fold-lines.py) reads the block the way the fold will and prints what the fold would write. The session runs it before the commit; the chair runs it before the fold, with `--carry <id>` for each row the prompt carried.

```
python scripts/fold-lines.py docs/orchestration/briefings/2026-01-15-payments-s4.md --carry 3f9a2c1e
```

Exit 0 prints `FOLD LINES OK` and each write in plain words; exit 1 prints `FOLD LINES REFUSED` and every reason; exit 2 is a file it could not read. Two blocks in one file are refused: the chair would not know which one is the landing. A briefing written before the block existed is folded from the file by hand, as before.

## Two emitters

The session's close emits the briefing as its terminal artifact. The on-demand command `/orchestrator-brief` ([`skills/orchestrator-brief/`](../skills/orchestrator-brief/SKILL.md)) emits the same file and block mid-session when the chair wants a deep status without ending the session, and a `context-dump` mode for capturing a conversation's knowledge before it is closed for good. Same sections, same bookends, same order.

## Forbidden

- Pasting the briefing body into chat when the file pushed.
- Variant bookends. The chair's fold parses the literal ones.
- A rendered question alongside a terminal briefing: a question the session cannot settle lives in section 7 with a best guess, for the chair to surface. A session never ends on a question.
- A briefing that describes only the last task of a long session.
- A starter prompt after the block. Nothing comes after the block.
