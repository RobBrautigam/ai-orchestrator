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

The reviewer is a fresh agent with its own context, never a fork of the session: a fork inherits the session's reading of the problem, and its blind spots with it. It is read-only, it is told what the repository is and what must never appear in it, and it echoes its scope back before its findings. Two numbers are read before any finding is trusted, and both go in the briefing: **the scope echo against the diff** (did it look at what changed, all of it?) and **the tool-use count** (a reviewer that made three tool calls on a forty-file change did not review it). Every finding is fixed or answered in the briefing, one line each, and the checks that gate the ship are re-run after the fixes, not before.

**A second reviewer, only when the change asks for one.** One reviewer is the default because most changes are small and most findings come from the first pair of eyes. Two kinds of change earn a second, focused reviewer, named in the prompt: a change of more than about 1,000 lines of code, where one reviewer's attention runs out before the diff does; and any change to sign-in, page security (who can see what) or money, where a missed finding is a breach or a wrong charge rather than a bug. The second reviewer is told the first one's scope and hunts only its own question; it is never a second general pass.

## What counts as evidence

- **The exercised surface, never code that looks right.** A rendered page, a real response, the downstream side effect, captured. A "published" state means nothing until the thing exists at its destination.
- **A test never seen red is not evidence.** A new test counts only after a deliberate break of the code it guards has made it fail. One session's hydration test passed with its gate removed; the break caught it before the pull request. This repository's own [`scripts/selftest.py`](../scripts/selftest.py) was run against deliberately broken copies of every script before it was trusted.
- **A 200 is not a probe.** A route that answers 200 for anything (an application shell, a login page) proves the server is up and nothing else. The probe pulls the bytes back and finds a sentence only the new version has.
- **Compute a claim about your own numbers before writing it.** "Every total reconciles", "all rounding favors X": those are the sentences a sharp reader checks, so the session checks them first.
- **Say what was not covered.** "Everything verified" without the list of what was not is a claim nobody can audit.

## The two ways to end

**The close-out card.** The session's last message, in a fixed shape, after the briefing file is committed and pushed. Nothing comes after it.

**A named blocker.** When the session genuinely cannot continue (a credential it cannot reach, a live system down, a rail it would have to cross), it writes the briefing anyway with the blocker in section 7 and on the pointer block's `BLOCKERS:` line, and ends with the same card. A blocker is still a card; it is never a bare stop.

## The close-out card

One message, seven sections in this order, a blank line between each, the pointer block dead last. Each heading opens with a fixed emoji, the same in every card from every session, so an operator scrolling a long transcript finds each section by shape before reading a word. The template is [`templates/close-out-card.md`](../templates/close-out-card.md).

1. `# 🚢 <arc> session <N>: <the outcome in one plain-English sentence>`
2. `## ✅ What we accomplished`: real bullets, what changed FOR THE OPERATOR (what they can now see, do, or stop worrying about). Engineering counts (pull requests, commits, migrations) are never the headline.
3. `## 🔴 Needs you`: a numbered list, each item the full question with the recommendation and what answering unlocks; omitted when nothing needs them. Every answer is routed to the chair, never to this session, because this session is over.
4. `## ⚠️ Watch`: anything on fire, degraded, or deliberately left unfinished; omitted when clean.
5. `## 📍 Where things stand`: repository, branch, version, pull request and its state, deploy verified or not, the live link, what is merged.
6. `## 🧭 Next`: a numbered list of what the chair dispatches next or what the operator does.
7. `## 📋 Orchestrator briefing`: one line ("copy this block to the chair"), then the pointer block inside a code fence. Nothing after it.

The card is the one place in a session's output where headings and emojis are required rather than optional. The paragraph law of chapter 11 still holds inside it: nothing over two lines; bullets and numbered lists do the work.

In the copy-paste era the operator carried the pointer block to the chair by hand. In the background era the chair finds the briefing file on main; the card is still emitted because it is the session's own record in its transcript, the tool's session list shows its first line, and an operator who does attach to a session reads it. The pointer block is still the machine-readable summary the chair's fold reads first.

## What a session never emits

A starter prompt for its successor. Only the chair holds the cross-arc map; a prompt written by a session goes stale the minute another arc lands. The July version of this repository said the same thing in its own words and it has not moved.

Nor anything after the card. A session that has one more thing to say after its pointer block (one line to the chair through the tool's cross-session message, when the prompt asks for it) says it through that channel, not as more text under the block.

## When a session launches helpers

A helper's final result is often displayed to the operator verbatim by the tool, so the session's helper prompts follow chapter 11's rule: one anchored line, written for the operator, with the detail in a report file at a path the session fixes. And the swarm law of chapter 9 applies inside a session exactly as it does to the chair: more than about three helpers at once, each with an explicit model, the expensive models never the fleet.
