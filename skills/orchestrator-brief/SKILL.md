---
name: orchestrator-brief
description: ON-DEMAND briefing for the chair (the orchestrator) from THIS session, mid-flight. Writes the eleven-section briefing to a committed, pushed markdown FILE and emits the short pointer block in chat, so the chair reads it from disk. Use when the operator or the chair says "/orchestrator-brief", "brief the chair", "brief the orchestrator", "deep status", "context dump", "write your briefing to a file", or any phrasing of "give me an orchestrator summary". NOT the session close: the close emits the same file and block as its terminal artifact through its own flow. Works in any repository or worktree, on any tool that reads a skills folder.
---

# Orchestrator brief (on demand)

Produce the standardized briefing and **persist it to a committed, pushed markdown file**, then emit the pointer block in chat. The file is the briefing; the block is a pointer to it. The chair folds from the file (`docs/07-folding-from-files.md` in the ai-orchestrator repository), never from the chat.

**Routing is hard:** ANY ask that means "a summary or briefing for the chair" routes through this skill (or through the session close, if the session is ending). Never a hand-rolled topical document. The output is always three things: (1) the committed, pushed file covering the WHOLE conversation; (2) the pointer block in chat inside a code fence; (3) the file's full path as a clickable link.

**This is the mid-flight case.** The canonical use is the chair asking several running sessions for a deep status at once (it sends the request into each session; each writes its file; the chair reads all the files). If the session is closing, use the close flow, not this skill.

## Two modes

- **`/orchestrator-brief`** (default): the eleven-section briefing, written to `docs/orchestration/briefings/<YYYY-MM-DD>-<arc>-s<N>-interim.md`.
- **`/orchestrator-brief context-dump`**: a full context dump for capturing a conversation's knowledge before it is closed for good: status, at-risk work and the command to secure it, decisive facts and mechanisms verbatim, reuse-elsewhere flags, a keep-or-close recommendation.

If the phrasing implies "capture everything before this is closed", prefer `context-dump`. Otherwise the default.

## Steps (both modes)

1. **Gather state first** (do not re-explore the codebase): `git status -s`, `git log --oneline -8`, the branch, the pull request if any (`gh pr view --json number,state,isDraft,mergedAt 2>/dev/null`), the worktree path, the arc's position.

2. **The completeness gate.** The brief covers everything that happened in this conversation, not the latest task. (a) Re-read the conversation from the first message and enumerate every distinct request. (b) Build the inventory from `git log <session-start>..HEAD`: every commit and every changed file accounted for, plus a "session at a glance" line (commit count, file count, work streams). (c) If an earlier interim brief exists, this one supersets it. (d) Answer explicitly: "does this cover every request and every commit from the start?"

3. **Write the file** with your file-write tool, never a shell heredoc. Content: the eleven sections in `templates/briefing.md` (or the context dump below), with deeper detail than a chat block would carry: verbatim prompts, specifications, decisions, numbers, paths. Every sentence whose subject is the operator carries its receipt or reads "not verified".

4. **Commit and push the file** (documents only). On a feature branch: commit and push the branch. On a protected main: a `docs/<slug>` branch, push, open a pull request, and say so; never force it. Verify the push (`git log origin/<branch> -1`).

5. **Emit the pointer block in chat**, inside a code fence, with the literal bookends from `templates/pointer-block.md`: `FILE:`, `PUSHED:` with the ref and short sha, the literal `READ:` command, `VERDICT:`, `FACTS:`, `SHIPPED:` (three bullets at most), `NEEDS OPERATOR:`, `BLOCKERS:`, `CONTRACTS:`, `NEXT:`. Everything material lives inside the fence.

6. **Then carry on with the work.** This skill does not end the session. Report, do not act on the report.

## The eleven sections (default mode)

```
1. INTENT vs WHAT HAPPENED: what was asked; what this session did; the divergence named, or "matched cleanly".
2. STATE: worktree, branch, pull request and state, git clean or not, pushed or not, live or not, versions; the EFFORT line.
3. WHAT SHIPPED + DECISIVE FACTS: what landed; the numbers; VERIFIED against ASSUMED per claim; the research with sources.
4. MISSES / LESSONS: honest; "None" if clean.
5. OPPORTUNITIES SURFACED: not acted on; time-sensitive ones flagged.
6. ROADMAP POSITION: where this sits; the next step; what follows.
7. NEEDS THE OPERATOR: each question in full with the recommendation and the best guess recorded; or NONE.
8. OWED / DEFERRED: bullets, each with its trigger; or NONE.
9. RECOMMENDATION: ranked, one line of why each.
10. CONTRACTS produced and consumed, and the table of what this session started and what stopped it.
11. MERGE TARGET & GATE: pull request, target, gate, deploy.
Loose-ends table: one row per line of the prompt's work, rails and close.
```

## The context dump (context-dump mode)

```
# Context dump: <title>
- One-line summary.
- Honest status (real project | research spike | throwaway; done | mid-flight | abandoned).
- At-risk work: uncommitted or chat-only material; secure it (commit and push what belongs in git; fold chat-only material into this file); state the one command to secure anything still at risk.
- Decisive facts, data, mechanisms, learnings: the substance; reusable prompts and specifications verbatim or by exact path.
- Reuse-elsewhere flags: what is leverageable in which other repositories, and why (honor any information wall).
- Recommendation: (a) nothing to keep, safe to close; (b) document only; (c) genuinely valuable, with the specific items flagged.
```

## Install

- Claude Code: copy this folder to `~/.claude/skills/orchestrator-brief/`; the `/orchestrator-brief` command works in every repository.
- Other tools: see `adapters/` in the ai-orchestrator repository for where each tool reads commands or skills; the procedure above is tool-agnostic.
