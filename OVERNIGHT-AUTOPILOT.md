# Overnight Autopilot

*Running the orchestrator unattended for hours - overnight, over a weekend, while the operator is in meetings - so the operator wakes up to finished analysis, held fixes, and ONE ranked list instead of a wall of chat. This pattern has now run multiple full nights across two orchestrators; everything below is field-tested.*

> **Revised for version 2 (September 2026).** This document was written in the copy-paste era, when the chair did the night's work itself. In the background era the night's work is dispatched as queue rows with the night's rails written into each dispatch prompt (chapters 3 and 4), the chair's hourly tick (chapter 8) is the heartbeat, and the morning report is the landed table plus the top ten (chapter 11). The rails, the phase plan, the evidence-chain discipline and the learning loop below still hold as written; "window verdicts" in the morning report have become on-me and on-you lines, since the operator no longer holds session windows. The learning loop's promotion rule (when a lesson becomes a rule, and when it must go to the operator instead) is chapter 13.


---

## The shape of a night

The operator says some version of: *"go on autopilot, work as long as you can, tackle the outstanding list or at least strategize it, break nothing, queue anything that needs my approval for the morning."*

The orchestrator then:

1. **Commits a rails + plan doc FIRST** (before any work) - the night's constraints and phases, in the repo, so the directive itself is durable and auditable.
2. Works in phases, appending to a **running night log** as it goes.
3. Ends with a **morning report**: one ranked list, decisions first.

## The rails (non-negotiable while unattended)

Write these at the top of the night log and hold them all night:

- **ZERO external sends.** No Slack, no email, no webhooks, nothing another human receives. Drafts are fine; sending is a morning decision.
- **ZERO new spend.** No metered API calls that cost money (research/data APIs you already pay for are fine if the operator has blessed them). No new signups or logins - account creation always needs the operator (which email, which identity).
- **Production writes: none**, beyond explicitly pre-recorded recipes (e.g. "backfill this one ledger row, recipe already approved"). Read-only against live systems otherwise.
- **Code changes ship as HELD DRAFT PRs, never merges.** The morning starts with the operator's 2-minute review, not a surprise deploy. Docs/analysis commits to main are fine (that is the orchestrator's normal surface).
- **Hands off live streams' surfaces.** If worktree sessions are running overnight too, the orchestrator does not touch the files/areas they own - it folds their merges from a distance.
- **Anything ambiguous or irreversible: queue it for the morning.** The night optimizes for "nothing to undo."

## The phase plan that works

- **Phase A - cleanup + hygiene.** The stale board header, the ledger gaps, the record drift. Cheap, zero-risk, and it makes every later phase's reads truthful.
- **Phase B - synthesis.** The highest-value unattended work: inventory everything the recent streams produced (a subagent can build the raw inventory; the orchestrator cross-checks it against git and the live systems), then write ONE review: what is closed, what is alive, what actually needs the operator. Expect to find record drift - claims that were superseded, items marked pending that already shipped. Correcting the record IS the deliverable.
- **Phase C - strategy + scoping on the outstanding list.** For each parked item: either do it (if it fits the rails), scope it (public recon, drafts, prep sheets - so the operator's morning step is minutes, not hours), or write down exactly what gates it.
- **Phase D - the morning report.** One file. Ranked. The single most important ask first (with a link and the 2-minute action), then the decision queue grouped by domain, then window verdicts (what to do with each open editor window), then "closed without you" as an FYI tail. The operator should be able to act top-to-bottom without reading anything else.

## Investigation discipline (the overnight superpower)

Unattended hours are perfect for the slow, evidence-chain work no interactive session has patience for. The night this doc was written, the chain "monitoring says feed stale -> is the data really missing? -> which of the two ingestion paths failed? -> reproduce the failure live -> read the code -> prove BOTH paths broken for different reasons -> fix both -> hold as one draft PR with the proof in the body" took ~90 minutes of polling, log-pulling, and local reproduction. The rules that made it trustworthy:

- **Evidence before conclusions, at every hop.** Reproduce the failure against the live system before reading code; prove the code path locally before writing the fix.
- **Distinguish "broken" from "quiet."** A stale feed may be genuinely quiet (nothing happened) rather than dead. Check the source of truth for whether there was anything TO ingest before declaring an outage.
- **Second-source alarming claims before relaying them.** A dramatic finding ("95% collapse!") gets verified against independent sources - the corrected verdict is usually smaller and differently-shaped than the first read.
- **Self-caught misses go in the log too.** The night log records the orchestrator's own mistakes (a banned pattern used, a self-inflicted side effect) with the lesson. The morning report includes them. Trust is the product.

## Pacing (if your harness supports scheduled wake-ups)

Long nights are not one continuous burn. The cadence that works: work a phase to completion, commit, then schedule the next wake-up around what you are actually waiting for - a cron job that fires at a known time gets a wake-up just after it; quiet watching gets 30-minute heartbeats. Each heartbeat: fetch main (fold any out-of-band merges from overnight streams), poll the relay folders (see [RELAY-PROTOCOL.md](RELAY-PROTOCOL.md)), append one log line, go back to sleep. Stop the cadence the moment the operator returns.

## One self-inflicted lesson, so you don't repeat it

If your repo auto-deploys on push (most PaaS setups do), **every docs commit the orchestrator pushes overnight triggers a full production redeploy.** One night here produced 11 deployments purely from orchestration-log pushes - harmless but wasteful, and it disguised itself as a "mystery restart loop" that cost a diagnosis detour. Fixes: batch the night's doc commits into a few pushes, go push-quiet once the substantive work is committed, and (best) configure your deploy's watch paths to ignore the orchestration/docs directories.

## Why it works

- The operator's absence stops being dead time - the backlog's analysis-shaped half moves without them.
- The rails make it safe to be wrong: nothing sent, nothing merged, nothing spent - every overnight conclusion is reversible at review time.
- The morning report converts a night of work into minutes of operator attention, decisions-first. That conversion ratio is the whole point.
