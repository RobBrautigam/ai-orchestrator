# 5. The background session and the close-out card

*A background session is a coding agent launched by the chair, in a worktree, with nobody at its keyboard. It has two ways to end and one final message. Everything about how it behaves follows from "nobody is at the keyboard."*

---

## Nobody is at the keyboard

The sentence appears in every dispatch prompt because every default of every coding tool assumes the opposite. A tool that is unsure asks; a tool that needs a permission prompts; a tool that finishes a thought ends its turn and waits. In the background, each of those is a stall: the session sits, the slot stays busy, and nothing tells the chair until the next tick. Measured across 101 background sessions on one estate over three days, twelve stopped before their close-out card and idled between 13 and 75 minutes each, seven and a half hours in total; four of them stopped in the same minute on the account's concurrent-session limit and waited 41 minutes for the hourly tick to notice.

So the session's laws are:

1. **Never ask a question.** Anything only the operator can decide goes in the briefing's section 7, with the session's best guess and what answering unlocks. Everything that does not depend on the answer is done.
2. **A progress note is never an end of turn.** The only two ends are the close-out card and a named blocker. A session that writes "next I will..." and stops has stalled.
3. **Unattended permissions.** The launch carries the tool's flags for a run nobody can answer (on Claude Code, `--permission-mode auto --permission-prompts none`; the adapters have the others). A tool prompt that cannot be pre-answered (a workspace trust dialog, an MCP approval, a worktree-creation confirmation) is avoided by the launch shape, not answered by a human.
4. **The worktree you are in is the isolation.** Never call the tool's own worktree-creation feature from inside the session; write in place.
5. **Model and effort are what the launch said.** The session does not switch models mid-run and does not spawn helpers on a model the prompt did not name.

## What a session does with its hour

From the same measurement: the part of a background session's wall time that the July copy-paste model called "the work" is about the same length in both models. The difference is what surrounds it. The copy-paste session felt fast because the operator only watched the working minutes and never counted the hours the window waited for a paste. The background session is about ten to twenty minutes slower on the same work (it reads more, because nobody is there to answer a two-second question) and it waits on nobody.

The chair's job with that hour is to not add to it: a session that ends its turn early is answered the same minute the tick finds it (a plan-limit refusal is a plan switch, never a wait; an early end of turn is a "carry on"; a question is an answer or a "record it in section 7 and carry on").

## The review at the close

One reviewer, named in the prompt, recorded in the briefing. Not seven. A session that reaches its ship gate and fans out a review armada has multiplied its own cost by the fleet size, and "no helper fleets" in the rails is read as being about research unless the prompt says the review too. A session never reports a clean review that did not run: "the reviewer could not read the tree" is a tooling failure, not a verdict, and it is written down as one.

## The two ways to end

**The close-out card.** The session's last message, in a fixed shape, after the briefing file is committed and pushed. Nothing comes after it.

**A named blocker.** When the session genuinely cannot continue (a credential it cannot reach, a live system down, a rail it would have to cross), it writes the briefing anyway with the blocker in section 7 and on the pointer block's `BLOCKERS:` line, and ends with the same card. A blocker is still a card; it is never a bare stop.

## The close-out card

One message, seven sections in this order, a blank line between each, the pointer block dead last. The template is [`templates/close-out-card.md`](../templates/close-out-card.md).

1. `# <arc> session <N>: <the outcome in one plain-English sentence>`
2. `## What we accomplished`: real bullets, what changed FOR THE OPERATOR (what they can now see, do, or stop worrying about). Engineering counts (pull requests, commits, migrations) are never the headline.
3. `## Needs you`: a numbered list, each item the full question with the recommendation and what answering unlocks; omitted when nothing needs them. Every answer is routed to the chair, never to this session, because this session is over.
4. `## Watch`: anything on fire, degraded, or deliberately left unfinished; omitted when clean.
5. `## Where things stand`: repository, branch, version, pull request and its state, deploy verified or not, the live link, what is merged.
6. `## Next`: a numbered list of what the chair dispatches next or what the operator does.
7. `## Orchestrator briefing`: one line ("copy this block to the chair"), then the pointer block inside a code fence. Nothing after it.

In the copy-paste era the operator carried the pointer block to the chair by hand. In the background era the chair finds the briefing file on main; the card is still emitted because it is the session's own record in its transcript, the tool's session list shows its first line, and an operator who does attach to a session reads it. The pointer block is still the machine-readable summary the chair's fold reads first.

## What a session never emits

A starter prompt for its successor. Only the chair holds the cross-arc map; a prompt written by a session goes stale the minute another arc lands. The July version of this repository said the same thing in its own words and it has not moved.
