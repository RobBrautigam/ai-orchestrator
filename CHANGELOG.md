# Changelog

## Version 2 (September 2026): the background era

The July 2026 version described a method where a human copied prompts from one "orchestrator" window into many worktree windows and copied briefings back. It worked, and the human was the bottleneck. Between July 24 and September 20 the model moved in eight ways, each after something measured. Version 2 rewrites the repository around them and generalizes it from one tool to any agentic coding tool.

### What changed, and why

1. **The chair launches sessions itself, in the background.** The operator no longer pastes a prompt or opens a window. A session is launched from its worktree by the chair with the tool's own background command, an explicit model and effort, and the unattended permission flags. *Why:* every session used to wait hours for a paste that took seconds; measured, a background session is ten to twenty minutes slower on the same work and waits on nobody. (Chapters 1, 5; the adapters.)
2. **A dispatch queue with slots, a cap, gates and badges.** One committed file holds the running, waiting and landed tables; a freed slot is refilled the same minute; the cap is stated in slots and is the operator's word. *Why:* "what is running and what waits" used to live in the chair's context and in chat; the queue file made it a fact anyone can read, and the cap made the account's concurrent-session limit a rule instead of a surprise. (Chapter 3; `templates/QUEUE.md`.)
3. **Dispatch prompts are committed files with a header of receipts.** The operator's words verbatim with the file and line they live in; **what is NOT on record**; what exists; the read-first list; then the work in order, the rails, the close. *Why:* a session that has to guess what the operator meant guesses wrong; a session that does not know what has not been decided decides it by accident. (Chapter 4; `templates/dispatch-prompt.md`.)
4. **Standing worktrees per arc, branch rotation inside them, created before the prompt.** *Why:* create-and-retire per session was pure churn (dependencies re-installed, environment files re-copied); and a session asked to create its own worktree stalls on a confirmation nobody unattended can answer. The `--force` warning is kept verbatim in spirit because it was earned. (Chapter 2; replaces `WINDOW-MANAGEMENT.md`.)
5. **The briefing is a file; the chat block is a pointer.** Eleven sections, pushed before the close-out card; the pointer block has fixed bookends and a literal `READ:` command; the completeness gate is mechanical. *Why:* a copy-paste briefing once dropped a nine-project run; a block that pointed at "the message above" arrived alone; a landing nobody pasted was a landing nobody folded. (Chapters 5, 6; `templates/briefing.md`, `templates/pointer-block.md`, `templates/close-out-card.md`; replaces `orchestrator-briefing-template.md`.)
6. **Folding from files, and the stop by id.** The chair reads the file, runs the close test, writes the landed row, and stops the session by id the same minute; the read ladder runs before anyone is asked. *Why:* a folded session left resident is about seven processes of pure cost, and one workstation reached 708 processes with 51 orphans before anyone counted. (Chapters 7, 10.)
7. **The cost rules.** Explicit model and effort on every launch; the cap in slots with a design session counting two; never a long-context variant in the background; the swarm law; metered APIs only through a capped client; the effort experiment. *Why:* a fifty-agent sweep that inherited the top model cost about $430 of allowance in one call; nine days later twenty long-context sessions moved 2.86 billion tokens in 33 hours with no fleet at all. (Chapter 9.)
8. **The communication standard is a chapter of its own.** Plain English with jargon paired to its meaning; the volume cap; one ask per message in a fixed shape; headings and real lists and never a semicolon paragraph; the on-me and on-you ownership law; the anchor emoji set with one meaning each; every ask links the record itself; the rolling top ten; one rolling picture between two operator messages, sent at most once. *Why:* the operator reads one window, on a phone, between other things, and only the latest message; every law here comes from a message that failed that reader. (Chapter 11.)

### Also

- **The picture.** The README opens with one SVG of one piece of work's whole life, ten stations, colored by who moves each. Two Mermaid diagrams and two ASCII drawings from July are retired in its favor.
- **Adapters.** One short file per tool (Claude Code, Codex, Gemini CLI, Cursor, OpenCode, Hermes, OpenClaw, a local model through Ollama), each checked against the tool's own documentation on the date at its top, with "not verified" wherever the documentation did not say.
- **The hourly tick** gets its own chapter with its twelve steps (chapter 8).
- **Process hygiene** gets its own chapter: kill what you start by id, never by image name, never elevate, never a window on the operator's screen (chapter 10).
- **The publish gate.** `scripts/wall-check.py` scans every tracked file for a list of words kept outside the repository and for generic secret shapes; this repository's own gate is that command at zero hits.
- **`RELAY-PROTOCOL.md` and `OVERNIGHT-AUTOPILOT.md`** are kept with a revision note each; both still hold.
- **The `/orchestrator-brief` skill** is rewritten for the file-first, pointer-block contract; its two modes are unchanged.
- **The name.** The repository's working name is `ai-orchestrator`, because the method is not specific to one tool. The GitHub repository's name, description and license are unchanged by this version; renaming is the owner's call.

### What did not change

One conversation per folder. The chair owns folders, the operator owns windows. Contracts as copy-paste. Validate before you relay; merged is not live. Merge by default with three gated carve-outs. Re-sync before every triage. The capture inbox. The one-directional information wall. A session never writes its successor's prompt.

## Version 1 (July 2026)

The initial playbook: worktrees plus an orchestrator conversation; copy-paste starter prompts; the eleven-section briefing as a chat block; the durable board; window management and the teardown order; the relay protocol; overnight autopilot; the installable `/orchestrator-brief` skill.
