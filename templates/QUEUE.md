# The dispatch queue (the chair's, in order; the hourly tick launches the top READY row when a slot is free)

Rewritten by the chair on 2026-01-15 at 09:12 (machine clock). **Cap: six slots** (the operator's word, 2026-01-10; an ordinary session counts one, a design session counts two). Every launch carries an explicit model and effort, the unattended permission flags for the tool, and the prompt body after the `---` line of its committed prompt file.

**At a glance (2026-01-15 09:12):** 3 running in 3 of 6 slots | 4 waiting to start (1 READY) | 12 landed since 2026-01-08. On the chair: a free slot is filled the same minute it opens.

## Running: 3 sessions in 3 of 6 slots

The first column is the slot; a design session takes two. Since is the machine clock at the launch line.

| Slot | Repo | Session | Model | Worktree | Since | What it does |
|---|---|---|---|---|---|---|
| 1 | myrepo | payments-s4 3f9a2c1e | opus, high | ../myrepo-payments | 2026-01-15 08:40 | The operator's drop 7 (08:14: "refunds should show up on the customer's statement the same day"): the refund path posts to the ledger synchronously, the statement view reads it, and the two are proven on a test account; ships with a patch bump and the live route probed |
| 2 | myrepo | onboarding-s2 91be07d4 | opus, high | ../myrepo-onboarding | 2026-01-15 07:55 | The three empty states the audit found on the first-run screens get real copy and a real action each; walked at phone and desktop width in both themes |
| 3 | | (free since 2026-01-15 09:10) | | | | on the chair: freed by the search-s1 fold; filled with the next authored prompt |
| 4 | docs-site | docs-refresh-s1 c07d55aa | sonnet, low | ../docs-site-refresh | 2026-01-15 06:30 | Mechanical: every page's "last reviewed" line re-dated from git history, every dead link listed in a report; no prose rewritten |
| 5 | | (free) | | | | |
| 6 | | (free) | | | | |

## Next, in order: 4 waiting to start (1 READY)

Rows are the launch order, top first. The first column is the badge: the number the item got when it joined the queue, kept for life; it is not a rank.

| Badge | Repo | Arc | Worktree | Model | Prompt | Gate | Queued |
|---|---|---|---|---|---|---|---|
| 14 | myrepo | Search session 2: the ranking the operator picked on card D3 ("relevance first, then recency") built behind the flag, measured against the fixture from session 1, the flag flipped only when the measurement beats the baseline | ../myrepo-search rotated | opus, high | docs/orchestration/prompts/2026-01-15-search-s2-prompt.md | none (READY) | 2026-01-14 |
| 9 | myrepo | Billing page redesign: five clickable mockups on the real invoice data, both themes, phone and desktop, one decision card for the operator's pick | new at launch: ../myrepo-billing | design model at its top effort (two slots) | to author | none | 2026-01-12 |
| 17 | myrepo | Billing page build: the operator's pick from badge 9 implemented from the locked design | ../myrepo-billing | opus, high | to author | card from badge 9 unanswered | 2026-01-12 |
| 11 | myrepo | Concept only: a weekly digest email of what shipped; research first on how three comparable products word theirs; nothing is sent to anyone | none yet | research on opus, high | to author | bottom of the queue by the operator's word ("not this month") | 2026-01-11 |

## Landed since 2026-01-08: 12 sessions (folded from their files, newest first, every row dated)

Launched and Landed are the machine clock at the chair's launch line and at the fold from the session's briefing file.

| Session | Repo | Launched | Landed | Result |
|---|---|---|---|---|
| search-s1 | myrepo | 2026-01-15 06:02 | 2026-01-15 09:10 | Search now answers in under a second on the 40,000-row index that used to take four; the ranking question is on card D3 with a recommendation, and nothing about the order of results changed yet (PR #212, v1.41.2) |
| payments-s3 | myrepo | 2026-01-14 20:15 | 2026-01-14 23:02 | A refund that fails no longer reads as pending forever: it reads as failed with the reason and a retry button, and the twelve stuck refunds from December were retried through the same button (PR #209, v1.41.1) |
| hygiene-s1 | myrepo | 2026-01-14 18:00 | 2026-01-14 18:44 | The 51 leftover processes from finished sessions were stopped by id after their parent chains were read; the census script that found them is committed and runs at every tick (PR #207, documents and scripts only) |
