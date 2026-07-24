---
name: orchestrator-brief
description: AD-HOC, ON-DEMAND brief - when the operator wants to send a spontaneous briefing or context-dump from THIS window back to the orchestrator mid-session. Writes it to a durable committed markdown FILE (+ emits it in chat) so the orchestrator reads it from disk instead of the operator copy-pasting it back. Use when the operator types "/orchestrator-brief", "orchestrator brief", "brief the orchestrator", "context dump", "write your briefing to a file" - and for ANY phrasing of "give me an orchestrator summary/briefing" (never answer that ask with a hand-rolled topical doc). NOT the session-close mechanism - the session close emits its own terminal briefing. Works in ANY repo/worktree.
---

# Orchestrator Brief (ad-hoc)

Produce the standardized orchestrator briefing and **persist it to a committed markdown file** so it becomes a permanent, deep-detail record the orchestrator can read from disk - instead of an ephemeral chat block the operator shuttles back by hand. Also emit the briefing in chat (fast read). The FILE is the durable layer; the chat block is the glance layer.

**ROUTING IS HARD (learned from a real self-documented failure):** ANY operator ask that means "orchestrator summary / briefing / update for the orchestrator" routes through THIS skill (or the session close, if the session is ending) - NEVER a hand-rolled topical/partial doc. The output is ALWAYS all three: (1) the comprehensive committed markdown file covering the WHOLE conversation (gate 1b below), (2) the copy-paste briefing block in chat, (3) the file's FULL absolute path rendered as a clickable markdown link. A topical relay doc in response to a summary ask is a defect.

**This is for the AD-HOC case only** - the operator wants, spontaneously and mid-session, to hand the current window's state to the orchestrator (the canonical case: a cross-repo sweep where the operator runs `/orchestrator-brief` in several windows at once and the orchestrator reads all the files). **It is NOT the end-of-session close** - your session-close flow already emits the terminal briefing and writes the same file. Do not use this skill to replace or duplicate the close; if the operator is closing out, route to your close flow, not here.

## Two modes

- **`/orchestrator-brief`** (default) - the **11-section briefing** (below). Use at a mid-flight status checkpoint, or whenever the orchestrator asks for a deep-status / the operator wants to hand this window's current state to the orchestrator on demand.
- **`/orchestrator-brief context-dump`** - a **full context-dump** for capturing a conversation's knowledge before the window is closed for good (status, at-risk work + the command to secure it, decisive facts/mechanisms/prompts/specs verbatim, reuse-elsewhere flags, keep-or-close recommendation). Use when a paused/finished conversation's knowledge must survive but it is NOT running a full close.

If the operator's phrasing implies "capture everything before I close this window", prefer `context-dump`. Otherwise default to the 11-section briefing.

## Steps (both modes)

1. **Gather state first** (don't re-explore the codebase): `git status -s`, `git log --oneline -8`, current branch, PR if any (`gh pr view --json number,state,isDraft,mergedAt 2>/dev/null`), and the session's roadmap position. Note the repo + worktree path.

1b. **FULL-SESSION COMPLETENESS GATE (mandatory before writing - recency bias is the named failure mode).** The brief covers EVERYTHING that happened in this conversation, not just the latest work-stream. (The canonical defect: a close briefing captured only the final task and silently dropped an entire nine-project run from the SAME conversation.) Do all of: (a) **scope reconstruction** - re-read the conversation from the FIRST operator message forward and enumerate EVERY distinct work-stream / phase / request; (b) **mechanical inventory, git-derived not memory** - `git log <session-start-head>..HEAD` for every commit this session + every file created/changed; the brief MUST account for all of them and include a "session at a glance" line (commit count, file count, work-streams) built from that git output; (c) **superset interim artifacts** - if this session already emitted an interim brief or handoff, this brief MUST SUPERSET them ("replace-with-latest" is forbidden); (d) **self-check before emitting** - answer explicitly: "Does this cover every operator request and every commit from the START of this conversation?" - re-read the first message to confirm. Long / multi-work-stream sessions get extra scrutiny.

2. **Write the briefing to a file:** `docs/orchestration/briefings/<YYYY-MM-DD>-<short-kebab-slug>.md` (create the directory if it doesn't exist; the slug describes this session/arc so multiple briefings in one repo don't collide). Use your file-write tool - never a bash heredoc (heredocs die on apostrophes in prose). Content = the full briefing (11-section or context-dump per mode), with DEEPER detail than a chat block would carry: reproduce verbatim any prompts, specs, decisions, numbers, and file paths that matter, so the file is a genuine permanent reference.

3. **Commit + push the file** (docs-only, safe). Respect the repo's convention:
   - Most repos: commit to the current branch and push.
   - PR-protected repos (a hook or branch protection refuses direct pushes to main): commit to the current feature branch and push it; if on main, create a `docs/<slug>` branch, push, open a PR, and tell the operator it needs merging - do NOT force it.
   - Report the committed file path + push/PR result.

4. **Emit the briefing in chat** as well - the same content, as a clean copy-paste block. **FENCE SELF-CONTAINMENT:** everything material lives INSIDE the fenced block - assume all surrounding prose is lost in the paste. Before emitting, re-read the block as if it is the ONLY thing the orchestrator receives: source window/worktree + branch, the committed file path, PR numbers + SHAs, verification results - all inside the fence.

5. **If this is a close-out**, end with the committed file path and one line: **"Safe to close."** so the operator knows the window can be closed and the orchestrator will read the file from disk.

## The 11-section briefing (default mode)

```
=== ORCHESTRATOR BRIEFING ===
1. INTENT vs WHAT HAPPENED (lead) - what was actually asked; what this session did; DIVERGENCE (over/wrong/cut scope, pivot, wasted cycles) or "matched intent cleanly".
2. STATE - stream/project / repo/worktree/branch / session state (mid-task | idle-awaiting-next | blocked-on-operator) / PR(s) #+draft|open|merged+SHA / git clean/N-uncommitted/pushed?/ahead-behind / prod live|dark|branch-only|n/a / versions+tags.
3. WHAT SHIPPED + DECISIVE FACTS - what landed; the key numbers/facts that drove decisions; VERIFIED-vs-ASSUMED flags on load-bearing/cross-stream claims.
4. MISSES / LESSONS - bugs, wrong assumptions, wasted effort, process lessons. "None" if clean.
5. OPPORTUNITIES SURFACED - high-value things exposed but not acted on; flag time-sensitive ones.
6. ROADMAP POSITION - where this sits -> immediate next step -> what's after.
7. NEEDS THE OPERATOR / BLOCKERS - decisions/credentials/approvals waiting, or NONE.
8. OWED / DEFERRED - each with the trigger that should resurface it, or NONE.
9. RECOMMENDATION - priority-ordered, one-line why each.
10. CONTRACTS (produced / consumed) - cross-stream glue as copy-paste named blocks (exact names/values), or NONE.
11. MERGE TARGET & GATE - PR# -> target -> gate (ready|draft|blocked-on-X|needs-operator) -> auto-deploy target.
=== END BRIEFING ===
```

## The context-dump (context-dump mode)

```
# Context Dump - <title>
- One-line summary.
- Honest status (real project / research spike / test / throwaway / concept; done | mid-flight | abandoned).
- At-risk work: uncommitted/gitignored/chat-only material - secure it (commit+push what belongs in git; fold chat-only material into this file) and state the one command to secure anything still at risk.
- Decisive facts, data, mechanisms, learnings - the substance; reproduce any reusable PROMPTS / specs / playbooks verbatim or by exact path.
- Reuse-elsewhere flags - what's leverageable in which other repos, and why. (Honor any information walls between your orchestrators' domains - see RELAY-PROTOCOL.md.)
- Recommendation - (a) nothing to keep, safe to close / (b) document-only / (c) genuinely valuable -> flag specific items for the orchestrator's knowledge base.
```

## Notes

- **The orchestrator should REMIND the operator to run `/orchestrator-brief`** in target windows instead of hand-authoring copy-paste dispatch/context-dump messages. That is the whole point - the operator types the slash command; the orchestrator reads the file.
- Install: copy this folder to `~/.claude/skills/orchestrator-brief/` and restart Claude Code - the `/orchestrator-brief` command then works in every repo and worktree window.
