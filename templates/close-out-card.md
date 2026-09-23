# 🚢 <arc> session <N>: <the outcome in one plain-English sentence>

## ✅ What we accomplished

- <what the operator can now see, do, or stop worrying about; one idea per line>
- <another; plain English; the try-it form where there is one: "refunds show on the statement the same day: open /account/statement">
- <another>

## 🔴 Needs you

1. **<The one question, in full.>** What it is in plain words; what is wrong today; what will be done on each answer; what changes for you afterwards; the risk and how it is reversed. **Recommended:** <option>, because <one line>. **Alternative:** <option>, if <condition>. Answer to the CHAIR: this session is over. <link to the record itself>

## ⚠️ Watch

- <anything on fire, degraded, or deliberately left unfinished, with who moves it next>

## 📍 Where things stand

- Repository `<name>`, branch `<branch>`, version `<x.y.z>`.
- Pull request #<n>: <merged as sha7 | open | draft>.
- Deploy: <verified live at <url> | not verified: <why> | none owed (documents only)>.
- Everything started by this session is stopped, by process id; the table is in the briefing's section 10.

## 🧭 Next

1. <what the chair dispatches next, or what the operator does, one line each>
2. <...>

## 📋 Orchestrator briefing

Copy this block to the chair (or let the chair find the file on main).

```
=== ORCHESTRATOR BRIEFING ===
ARC: <arc> - session <N>
REPO: <repository> | WORKTREE: <path> | BRANCH: <branch>
FILE: docs/orchestration/briefings/<YYYY-MM-DD>-<arc>-s<N>.md
PUSHED: origin/<branch or main> @ <sha7>
READ: git -C <main checkout> fetch -q && git -C <main checkout> show <ref>:<file>
VERDICT: <shipped-live | merged-not-deployed | branch-only-unmerged | design-only | blocked>
FACTS: v<x.y.z> | PR #<n> <state> | squash <sha7> | deploy <verified | not-verified | n/a>
SHIPPED:
- <plain-English line, three bullets at most>
NEEDS OPERATOR: <full question or NONE>
BLOCKERS: <on-fire item or NONE>
CONTRACTS: <NONE | n in file>
NEXT: <one-line recommendation>
FULL DETAIL IS IN THE FILE. Read it line by line before triaging.
=== END BRIEFING ===
```
