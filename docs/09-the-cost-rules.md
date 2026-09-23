# 9. The cost rules

*Every rule here was written after a measured incident. The first two are the incidents; the rest are the rules, each with the number that justifies it.*

---

## Incident one: the fifty-agent sweep

A mechanical task: read 435 markdown files and extract their to-do items into a fixed schema. The workflow spawned fifty helper agents. Every one omitted `model` and `effort`, so every one inherited the session's model, which the operator had switched to the most expensive one minutes earlier.

Measured from the run's own transcripts: 127 million tokens of context moved (21.7 million written to cache, 105.6 million read back), 1.08 million tokens of output, about $430 at that model's list price. The same work on the mid-tier model would have cost about $86; on the small model about $43. The task did not need the top model. Reading a file and filling a schema is small-model work; the intelligence was in the orchestration (what to read, how to merge, what to verify), which is the main loop's job, not the fleet's.

Because the fleet ran through the subscription and not an API key, no invoice arrived; what it consumed was the account's five-hour window and its weekly allowance of the top model, and it stopped all the operator's other work for the day.

## Incident two: many long sessions, each on the long-context variant

Nine days later the same allowance ran out with no fleet involved. About 28 sessions in 33 hours, twenty of them interactive windows, every one on the top model's long-context variant because the machine default was set that way and nothing launched with an explicit `--model` overrode it. 2.86 billion tokens moved; 29 million of output; an average of about 560,000 tokens re-read per assistant turn. A long-context session does not compact at the usual boundary; it grows toward its ceiling and every later turn pays for the whole transcript. Twenty windows doing that for a day is billions of tokens without a single fan-out.

## The rules

### 1. Every launch names its model and its effort

In the command and in the chat line that reports it. A launch without `--model` inherits the machine default, which is a cost decision the operator made for their own window, not for a fleet. A launch without `--effort` inherits the default effort, which on the estate that wrote this was the highest setting, so every background session for a week ran at extra-high effort without anyone choosing it.

The register, by task:

| Task | Model | Effort | Slots |
|---|---|---|---|
| Design direction, mockup galleries, look and feel | the top model | its top effort | two |
| Implementation from a locked design; back-end builds; audits; document sessions | the strong implementation model | high or the top effort (measured, below) | one |
| Judgment that carries the result (a review of money or auth code; a contract) | the strong implementation model | the top effort | one |
| Mechanical extraction, sweeps, fixed-schema reads | the small model, or a local model | low | half |
| Anything the operator named a model or effort for | what they said | as asked | as above |

**The operator's word overrides the register, and stays in force until they say otherwise.** When a new model lands and the operator says "use it for everything", every row above runs on it, the chair's own window included, and the register waits. Write the word down with its date and clock beside the table so the next chair does not "correct" it back.

**An alias is not a model.** A short alias resolves to the newest model in its family on the day of the launch, so "opus" on Monday and "opus" on Friday may be different models with different prices. Read which model id each session actually ran on from its own usage record, and put that id, not the alias, on the effort line (chapter 6).

### 2. The cap is stated in slots, and it is the operator's word

An ordinary session is one slot; a design session on the top model is two. The number is written at the top of the queue file with the date it was set, and it changes only by the operator's word. It moves more than you would expect: on the estate that wrote this it moved more than twenty times in four days, between two slots and thirteen, and each move was quoted with its clock. The cap serves two purposes: cost, and the provider's concurrent-session limit. At the cap, the first refusal from the provider is reported to the operator the same minute rather than retried; a refusal is a plan switch, never a wait.

**Lowering the cap is a wind-down, not a stop.** When the operator lowers the cap below what is running, every running session finishes on its own and is folded as usual; a freed slot is simply not refilled while more than the new cap are busy. Once the count is at the new cap, it holds there and every freed slot is refilled as before. Stopping a working session to meet a new cap wastes the work it has done and is never what "fewer slots" means.

### 3. Never a long-context variant in the background

The long-context variant is for the one chair that genuinely holds the cross-arc map, and even there it is a choice to make out loud. A session should compact and stay cheap. A session that runs longer than about two hours is a cost event of its own; prefer ending it and dispatching a fresh one with a fresh prompt.

### 4. The swarm law

In play the moment more than about three helper agents run at once, whatever spawns them:

- **An explicit model on every agent.** Never let a fleet inherit the session's model.
- **The top models are never the fleet.** They are single-call, hardest-problem models. They may be the narrow tip of a swarm (one synthesis, one adversarial judge) when the judgment genuinely carries the result.
- **Effort is set per stage.** Mechanical stages get `low`; omitted means high on every agent.
- **Say the plan in one line before launching:** "forty readers on the small model at low effort, three mergers on the mid model, one synthesis." If the sentence would embarrass you on the invoice, change it before launching.
- **Size the context, not just the count.** The fifty-agent run's cost was cached context, not output. Narrow the corpus with search tools in the main loop, for free, before spawning readers; do not hand an agent a large file "for context" it will not use.
- **Kill a runaway at once.** A background workflow keeps spending after you have realized the mistake.

### 5. The review at the close is one reviewer

A session that reaches its ship gate and fans out a review armada has multiplied its own cost by the fleet size. "No fleets" in the rails is read as being about research unless the prompt says the review too, so the prompt says the review too.

### 6. Metered APIs only through a client with a cap

A research fan-out once called a scraping actor directly, eleven runs in ninety-five minutes, and hit the account's monthly hard limit; every other feature on that account answered `403` for the rest of the month. Any metered API is called only through the repository's own client with its per-run ceiling and its spend ledger; a dispatch prompt that touches one names the cap per call and the ceiling for the whole session, and the session stops at the ceiling.

### 7. Batch work over your own data never goes through a paid API when a subscription session can do it

Summarizing your own transcripts, classifying your own archive, extracting facts from your own files: the order is a local model, then a cheap open-weight model, then background sessions in batches on the subscription. The same verification code path (quotes checked against the source) guards all three.

### 8. A router is never the mechanism

Pointing a coding tool at a different provider through a gateway loses the tool's prompt caching. On a median implementation session on the estate that wrote this, 88 million of 88.7 million tokens were cache reads; without caching, the "cheaper" model behind the router cost more than the expensive model with its cache intact. When a different model is wanted, it is run by the CLI that supports it natively or called as a tool from inside a session, never by re-pointing the session.

### 9. Measure completion, not tokens

A trial that reports "40 percent fewer tokens" and not "the same task done, reviewed, with the same defect count" proves nothing. A public benchmark (Terminal-Bench 4.0, as read on 2026-09-19) measured a cheaper model resolving 12 percent of tasks for three times the tokens of a stronger model that resolved 54 percent: the cheap model cost more because it could not finish.

### 10. A long-context model in the chair's own window is a choice, stated

The one conversation that holds the cross-arc map may run on a long-context variant, because it genuinely reads more than any session. It is still a cost decision made out loud, re-examined when the chair's turns grow slow or its allowance runs short, and it never spreads to a background session by inheritance: every background launch names its own model (rule 1).

## The effort experiment

The default effort is re-set on data, not on opinion. The shape: two sessions of about the same kind (research and measure; an audit; a sweep) launched the same hour on the same model, one at `high` and one at the top effort, neither told to behave differently. At each fold the chair records tokens moved, wall time, the reviewer's findings, metered spend, and defects found later (a wrong fact, a page the chair had to fix, a follow-up session the miss caused). The reading, in plain words: what each level cost, what each produced, and whether the extra bought anything a reader can see. The first pair on the estate that wrote this: same wall time; the top effort moved about 58 percent more context and produced about 44 percent more output; both delivered every asked item and both caught a wrong number of their own before publishing it. Defects found later are still being filled in, and the default has not moved until they are.

The bar for moving it is the operator's, and on that estate it reads: **no savings bought with lower-quality output.** A cheaper setting earns the default only when the matched pairs show the same work done with the same defect count. Until then the default stays at the top effort, and every launch still names it.
