# The pointer block

Emitted once, inside a code fence, as the last element of the close-out card, after the briefing file is committed, pushed and the push verified. Literal bookends; nothing appended to them; `NONE` where a line does not apply.

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

## The fallback (the only exception)

If the file could not be committed and pushed:

```
PUSHED: NOT PUSHED - <reason>. FULL BRIEFING INLINE BELOW
```

followed by all eleven sections inline, inside the same fence.

## The deep-status request (the chair pastes or sends this mid-flight)

```
CHAIR DEEP-STATUS REQUEST. Pause and give the chair a real briefing on this session: do NOT start new
work, do NOT ship, do NOT abandon in-progress work; just report. Write the eleven-section briefing to
docs/orchestration/briefings/<date>-<arc>-s<N>-interim.md, commit and push it, then emit the pointer
block. Lead with the single most important thing: did this session do what the prompt actually asked,
and did anything diverge? Be thorough where it is valuable (divergences, surprises, opportunities,
honest misses) and terse where it is routine (git plumbing).
```
