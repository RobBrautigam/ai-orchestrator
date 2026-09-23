# <Arc> session <N>: <the outcome in one plain-English sentence>

**Worktree** `<path>` | **branch** `<branch>` | **PR** [#<n>](<url>) <merged as sha7 | open> | **version** <x.y.z>, <deployed and verified live | not deployed: why> | **session** `<id>` (background, <model>, <effort>) | <YYYY-MM-DD>, <HH:MMZ> to <HH:MMZ>

**The dispatch prompt:** `docs/orchestration/prompts/<file>.md`. **The board row:** `<id>`.

> **The one line:** <what changed for the operator, in one sentence>.

Every sentence below whose subject is the operator quotes a drop file with its number or reads "not verified".

---

## 1. Intent against what happened

| The prompt asked for | What happened |
|---|---|
| 1. <work item> | DONE: <where the evidence is>. |
| 2. <work item> | DONE, wider than asked: <what and why>. |
| 3. <work item> | PARTIAL: <the gap, named>. |
| Rails: <the list> | HELD, with <n> misses recorded in section 4. |

**Nothing was changed anywhere it should not have been:** <the negative claims that matter: no message sent, no setting changed, no data touched>.

## 2. State at close

| | |
|---|---|
| Merged | PR [#<n>](<url>), squashed to `<sha>` on `main` at <HH:MM:SSZ> |
| Deployed | <platform>, deployment `<id>`, <state> at <clock>, watched read-only |
| Live | `GET <health route>` reads version <x.y.z> |
| The route | `<url>` answers <code> with <what> |
| Tests | <n> backend (<n> new) and <n> front end, all green |
| The walk | <n> checks, 0 failed, <n> captures, at <widths> in both themes |
| Commits | <n> on the branch, squashed into `<sha>` (<files>, <insertions>) |
| Metered spend | $<n>: <what, at what rate, under the $<ceiling> ceiling> |
| Local processes | everything started is stopped, each by id; section 10 has the table |

```
EFFORT | <session kind> | model <m> | effort <e> | session <id> | started <iso> | tokens_input <n> | tokens_output <n> | cache_read <n> | cache_write <n> | reviewer_findings <n> | subagents <n> | metered_spend $<n>
```

## 3. What shipped, and the decisive facts

### 3.1 The before table (read-only, measured <clock>)

| <what> | <before> | <source> |
|---|---|---|

### 3.2 The research pass, with sources and dates

- <repository or page>, <stars, last commit, license> (read <date>): <what it does well or what was taken from it>.

### 3.3 <what was built>, one fact per bullet

- <the fact, with the number and its source>

### 3.4 Verified against assumed

- VERIFIED: <claim>, by <how>.
- ASSUMED: <claim>; not verified because <why>.

## 4. Misses and lessons

- <the miss, its receipt, its class: a missing rule, or a rule not applied>

## 5. Opportunities noticed and not taken

- <each a bullet; none built; time-sensitive ones flagged>

## 6. Roadmap position

<where this sits in the arc; the immediate next step; what comes after>

## 7. Needs the operator, and the best guess recorded in their absence

**One question, restated in full:**

> **<The question?>**
>
> **What it is.** <plain words>
>
> **Recommended: <option>.** <one paragraph of why>
>
> **Alternative: <option>,** if <condition>.
>
> **What answering unlocks:** <the next session or the next step>.

**The best guess recorded in the operator's absence:** <option>. <What was and was not done on that guess.>

## 8. Owed and deferred

- **<item>.** Trigger: <what should resurface it>. [<source: reviewer finding n | prompt step n>]

## 9. Recommendation

<what should happen next with this arc, ranked, one line of why each>

## 10. Contracts, and what this session started

### 10.1 Contracts

PRODUCED: <named block with exact names and values, or NONE>. CONSUMED: <named contract and confirmation it was matched, or NONE>.

### 10.2 What this session started, and what stopped it

| Process | Id | Command line | Started | Stopped by |
|---|---|---|---|---|
| <dev server> | <pid> | `<cmd>` | <clock> | `<the stop command>` at <clock>, confirmed gone |

## 11. Merge target and gate

Merged to `main` through PR [#<n>](<url>) at <clock>, squashed to `<sha>`, deployed as <x.y.z> and verified live. The gate: <tests>, <the walk>, <the probe>, and the reviewer:

| | |
|---|---|
| Form | a fresh agent, never a fork; read-only; <model> |
| Tool uses | <n> |
| Scope echo | <what it said it read>, against the diff: <all of it | the gap> |
| Findings | <n>, each below with what was done |

- <finding 1>: <fixed in sha7 | answered: why no change>

---

## Loose-ends audit

| Item from the dispatch | Verdict |
|---|---|
| 1. <work item> | DONE: <section> |
| 2. <work item> | PARTIAL: <the gap> |
| Rails: <each> | HELD |
| Close: <each required element> | DONE |
| Never ask a question; operator-only items to section 7 with a best guess | DONE: one question, with the guess recorded |
