# 13. Lessons into rules

*Every chapter in this repository is a lesson that became a rule. This chapter is how that happens on purpose rather than by accident: where a lesson is written, when it is promoted, what may never be promoted without the operator, and the one distinction that decides whether the fix is a sentence or a check.*

---

## Why this is its own chapter

A fleet makes the same mistake many times before anyone notices, because each session is new and none of them remembers the last. Section 4 of every briefing (misses and lessons) catches the mistake once. Without a path from there to the rules, the next session repeats it, and the one after, and the chair folds the same lesson every week in slightly different words.

## A lesson is a note about one run; a rule is what the next hundred runs obey

Every repeated procedure the chair relies on (a skill, a command, a checklist, the dispatch template itself) keeps two files beside it:

- **`LESSONS.md`**: one entry per lesson, each with its receipt (the briefing and section it came from), the date, and its class (below).
- **`RUNS.md`**: one line per run: the date, what ran, what it produced, and how many lessons it appended ("none appended" is a line too, with its reason).

At the close, the session re-reads its run against its own claims, appends its lessons, adds its run line, and may make **at most three mechanical self-edits** to the procedure it followed, each a dated delta shown in its briefing. Three is a cap on purpose: a procedure that rewrites itself freely after every run stops being a procedure.

## The promotion rule

The step from lesson to rule is mechanical, so nobody has to decide it:

1. **A lesson that appears in three runs of one procedure is promoted into that procedure's body** by the next session that closes it. It is folded into the step it belongs to, never appended to a growing list of warnings at the end, and the three entries are marked promoted with the date. The promotion counts as one of that run's three self-edits.
2. **A lesson about a RULE goes to the rule, never to the procedure.** If the same miss shows up in three runs of three different procedures, the defect is a rule that is not being applied, and a fourth procedure repeating it in its own words makes the whole thing harder to read, not safer. Write it once in the rule's own file, and put a check at the moment of action.
3. **A lesson that would change a rail, the operator's standing decisions, or what a procedure may do unattended is never promoted by a session.** It becomes a proposal in `LESSONS.md` with its recommendation and what answering it unlocks, and the briefing's section 7 carries it to the operator. A run that wants to change a rail is a run that stops and asks.
4. **Class every miss before promoting it.** Two classes:
   - **MISSING RULE**: nothing said not to. The fix is to write the rule.
   - **RULE NOT APPLIED**: a rule said not to, and it happened anyway. The fix is NEVER another sentence. It is a check at the moment of action: a line in the procedure's own checklist, a lint rule, a hook, a script that refuses.

When most of a procedure's misses are the second class, the honest finding is that the system has an application problem, and more prose makes it worse.

## What "a check at the moment of action" looks like

Every script in this repository is one:

- **The attribution trailer.** A rule said commits carry no AI co-author line. The tools add one by default on every commit, and a rule in memory loses to a default applied every time. The fix was not a louder rule; it was [`hooks/commit-msg`](../hooks/commit-msg), which refuses the commit.
- **The unfolded session.** A rule said fold within ten minutes. A chair deep in a long turn could not see the clock. The fix was [`scripts/fold-check.py`](../scripts/fold-check.py), run before each new ask (chapter 7).
- **The worktree with no hooks.** Nobody forgot a rule; a generated folder was simply absent. The fix was a rotation that ends on a proof, [`scripts/rotate-worktree.py`](../scripts/rotate-worktree.py) (chapter 2).
- **The owed item already done.** A rule said validate before dispatch. The fix was [`scripts/done-on-main.py`](../scripts/done-on-main.py), which reads git instead of memory (chapter 7).
- **The private word in a public file.** A rule said never publish a private name. The fix was [`scripts/wall-check.py`](../scripts/wall-check.py), the publish gate, with its list kept outside the repository. A check someone has to remember to run is still a rule, so it moved into [`hooks/pre-commit`](../hooks/pre-commit) and the commit-message hook, where it runs on every commit without anyone remembering to (chapter 12).
- **The prompt that launched broken.** Rules said every prompt has a definition of done, a hard stop, and no instruction to ask. A prompt copied from an older one carries the older one's gaps, and the chair reads prompts by eye. The fix was [`scripts/prompt-check.py`](../scripts/prompt-check.py), run before every launch (chapter 4).
- **The fold composed from prose.** A rule said fold every owed item and every carried row. A fold composed from eleven sections of prose depends on the chair noticing each item. The fix was the `fold-lines` block at the end of the file and [`scripts/fold-lines.py`](../scripts/fold-lines.py), which reads it the way the fold will (chapter 6).
- **The session nobody bounded.** A rule said every prompt has a hard stop. The chair could not see a running session cross it. The fix was the queue's `Expected` and `Hard stop` columns, read by the fold check (chapter 7).

Each one was proven the same way before it was trusted: a toy case where it must say yes, a toy case where it must say no, and a deliberately broken copy that the test catches ([`scripts/selftest.py`](../scripts/selftest.py)). **A test never seen red is not evidence.** A new check counts only after a copy of the code it guards has been broken on purpose (a condition flipped, a refusal switched off) and the test has failed on that copy. `selftest.py` takes `--scripts-dir`, `--hook` and `--pre-commit` so a broken copy can be tested without touching the real files, and [`scripts/mutation-pass.py`](../scripts/mutation-pass.py) does exactly that for 22 guards, one at a time, and names any the selftest missed.

## No new rule without its check, the same day

A rules folder that grows every week is a sign the estate has an application problem, not a knowledge problem: each new paragraph is one more thing the chair must remember at the moment it is busiest. So a line added to a rule file names, the same day, the check that refuses its miss (a hook, a script, a lint or a test), in one register beside the rules: the rule, the check, and the file the check lives in. When no check can be written yet, the change that added the rule says so and owes the check by name. The register is what an audit reads first: a rule with no check is a rule waiting to be broken.

## Folding the operator's corrections

The operator's corrections are the richest lessons and the easiest to lose. When the operator corrects how the chair works (say, a question they missed because it sat in the middle of a turn), the correction is written into the rule's own file the same day, with the operator's words verbatim and the date, and the fix is classed like any other miss. A correction the operator has to make twice is, by definition, a rule not applied, so the second time it gets a check.
