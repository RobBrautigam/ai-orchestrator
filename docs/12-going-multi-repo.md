# 12. Going multi-repo

*Three patterns for when the method outgrows a single repository, and one for when the chair runs alone for hours. The two longer documents this chapter points at are kept from July and revised where the model moved.*

---

## One chair across several repositories

One chair can coordinate arcs across several repositories: it holds the cross-repository map, creates worktrees in each, relays contracts and findings between them, and keeps the cross-cutting knowledge. Each repository still keeps its own board, its own queue rows, its own briefings folder and its own worktree discipline. The chair plans and relays; it does not edit the other repositories' application code. In the background era this is mostly a matter of the queue file's Repo column and the launch command's working directory: a row says which repository, the worktree is a sibling of that repository's main checkout, and the launch happens from there.

## One-directional information walls

Sometimes one chair's world must not be visible to another: separate businesses, separate teams, a client's confidentiality, a partnership where one side's finances never reach the other. The pattern: coordinate ONLY through self-contained relay messages. Each message carries everything the receiving side needs and never references anything from the hidden side. One chair may see everything; each walled chair sees only its own world. When drafting anything that crosses the wall, the test is: *could the receiving side infer the hidden side's existence from this message?* If yes, rewrite it.

A wall is also a publish gate. This repository's own [`scripts/wall-check.py`](../scripts/wall-check.py) is the mechanical form of the test: a list of words that must not appear, kept outside the repository, run over every tracked file, exit 0 at zero hits. The same script, with a different list, checks a client deliverable before it leaves the building.

**A gate run by hand is a gate skipped on the busy day, so the gate runs at the moment of action.** Three places, one script:

- **Before the commit:** [`hooks/pre-commit`](../hooks/pre-commit) runs `wall-check.py --staged`, which reads the staged copy of each added or changed file (what the commit will hold, not what is on disk), and refuses the commit on a hit.
- **On the commit message:** the optional [`hooks/commit-msg`](../hooks/commit-msg) runs `wall-check.py --commit-msg` when a list is configured, because a private name in a message is published the moment the branch is pushed.
- **On what no git hook sees:** a pull request's title and body, a release note, an issue comment. These are published too. Write the text to a file first and run `wall-check.py --text-file <file>` before it is posted.

Both hooks read the list's path from `git config wallcheck.list`, so the list itself never enters the repository; with no list they still check the built-in shapes (keys, emails, home paths) and say so. A hook that cannot find Python or the script refuses the commit with the reason rather than letting it through unchecked.

## The relay protocol

Once two chairs run daily, clipboard relaying breaks: the operator becomes the single point of failure for cross-domain dependencies. The evolved system:

- **Relays are committed files** in known inbound and outbound directories, each self-contained with a standard header (`relay-id`, `handles`, `action-owner`, `expects-reply`).
- **Each chair polls the other's outbox at every tick.** The poll is the delivery guarantee; an operator ping accelerates but is never load-bearing.
- **Acknowledgements carry a terminator,** so two polite chairs do not acknowledge each other forever.
- **A relay that NAMES an action does not ASSIGN it:** execution transfers only through an explicit `action-owner`.

The standing routing rule that fell out of it: work executable by the other chair's domain relays to it the same turn it surfaces, and the operator's own list holds only genuinely human judgment. Full specification: [RELAY-PROTOCOL.md](../RELAY-PROTOCOL.md).

## Running unattended

The chair can run alone for hours (overnight, over a weekend) under hard rails: nothing sent, nothing merged, nothing spent; code fixes held as draft pull requests; one ranked morning report at the end. The July document that describes it, [OVERNIGHT-AUTOPILOT.md](../OVERNIGHT-AUTOPILOT.md), still holds with one revision: in the background era the night's work is dispatched as queue rows with the night's rails written into each prompt, rather than done by the chair itself, and the morning report is the landed table plus the top ten. The learning loop at the end of the night (the lessons appended to a file, the run recorded, at most three mechanical self-edits to the night's own instructions shown in the report) is the part most worth copying.
