# Changelog

## Version 2.2 (November 2, 2026): the fold, the prompt and the publish gate, checked

Version 2.1 turned the first rules into checks. In the weeks after it, the estate running the method kept finding the same thing: wherever a person (or the chair) had to compose, remember or notice something at the moment of action, it was sometimes not done. Version 2.2 moves four more of those moments into scripts, each with its selftest and each seen to fail on a deliberately broken copy.

### What changed, and why

1. **The fold lines.** A briefing ends with one fenced `fold-lines` block (`RESULT`, `BOARD`, `EFFORT`, `FINDINGS`, `SPEND`, one `OWED` line per deferred item with its band and owner, one `CARRY` line per row the prompt carried), and the chair folds by copying from it, never by composing. `scripts/fold-lines.py` reads it the way the fold will and refuses a bad band, an owner reason outside the six, a pipe in the board line, a result over 200 characters, two blocks in one file, or a carried row with no line. *Why:* a fold composed from eleven sections of prose depends on the chair noticing every owed item and every carried row. (Chapters 6, 7; `templates/briefing.md`.)
2. **The prompt check, before every launch.** `scripts/prompt-check.py` refuses a dispatch prompt with no `DONE MEANS` line in the body the session receives (a line above the `---` does not count, nor a line that is only a duration), no readable `HARD STOP` (a clock with am, pm or a zone is refused), an `EXPECTED` later than the hard stop, an instruction to ask somebody, or a read-first path that is neither on `origin/main` nor on disk. *Why:* a prompt copied from an older one carries the older one's gaps, and the chair reads prompts by eye. (Chapters 3, 4, 8; `templates/dispatch-prompt.md`.)
3. **The fold check knows the clock.** The queue's running table gains `Expected` and `Hard stop` columns copied from the prompt at the launch; `scripts/fold-check.py` names a row with no card `PAST HARD STOP` or `OVER EXPECTED`, with the minutes, says "could not check" (exit 2) for a cell it cannot read, takes `--now` for a given clock, and names any running row with no hard stop in its all clear. *Why:* the chair could not see a running session cross the hard stop its own prompt set. (Chapters 3, 7; `templates/QUEUE.md`.)
4. **The publish gate at the moment of action.** `scripts/wall-check.py` gains `--staged` (the staged copy of each added or changed file, which is what the commit holds), `--commit-msg` and `--text-file` (for a pull request body or a release note, which no git hook sees). The new `hooks/pre-commit` runs it on every commit, and `hooks/commit-msg` runs it on the message when `git config wallcheck.list` names a list. Both refuse the commit, with the reason, when they cannot find Python or the script. *Why:* a check someone has to remember to run is still a rule. (Chapters 12, 13.)

### Also, in the chapters

- **Handing the chair over:** asked for by the operator, running sessions handed over running with their ids and hard stops, one handoff file, one starter prompt, and the outgoing chair stops its own waits. (Chapter 1.)
- **A table written by hand drifts:** generate the running table from launch and fold records once the parity line keeps firing. (Chapter 3.)
- **Rails written once,** in one file the tool loads, so thirty prompts do not carry thirty drifting copies. (Chapter 4.)
- **A second reviewer only when the change asks for one:** over about 1,000 lines of code, or sign-in, page-security or money code. (Chapter 5.)
- **What wakes the chair:** a scheduled prompt that could not fire while a background task ran (fifteen due times, none fired), and the two things that did work; a bounded wait has a condition and a bound, and never reads a file another session is still writing. (Chapter 8.)
- **A test never seen red is not evidence:** `scripts/selftest.py` takes `--scripts-dir`, `--hook` and `--pre-commit`, so a broken copy is tested without touching the real files. (Chapter 13.)
- **The selftest** grew from 24 checks to 39.

## Version 2.1 (September 23, 2026): rules turned into checks

Version 2 described the background era. In the three days after it was written, the estate running it kept breaking the same few rules, not because the rules were unclear but because nothing checked them at the moment of action. Version 2.1 folds in what those days taught, generalized, and ships the checks as small scripts with a selftest.

### What changed, and why

1. **The ten-minute fold law, and a check that enforces it.** A fold is owed within ten minutes of a session's card, and a chair turn past ten minutes runs the fold check before each new ask. *Why:* notifications and the tick arrive between the chair's turns; a finished session read "running" for twenty-five minutes while the chair answered nine messages in one turn. (Chapters 1, 7, 8; `scripts/fold-check.py`.)
2. **The ask and the result live in the final message of the turn.** Text between tool calls is a progress marker only; anything the operator must read is restated whole at the end; a helper's final result is written for the operator, because the tool shows it to them. *Why:* a well-formed question written mid-turn was collapsed among the tool rows and never seen, and a helper's prose report for the chair landed on the operator's screen. (Chapter 11.)
3. **Rotation as one command, ending on a proof that the commit hook runs.** *Why:* ten worktrees on one estate ran no commit hook at all for weeks, because the hook folder was generated at install time and ignored by the repository, so it existed only in the main checkout. (Chapter 2; `scripts/rotate-worktree.py`.)
4. **Is the owed work already on main?** A check before a prompt is written for owed work, by the item's files and by its title's words. *Why:* twice in one day a session was dispatched on work two merges had already done. (Chapters 4, 7; `scripts/done-on-main.py`.)
5. **Lessons into rules, as a chapter.** A lesson file and a runs file per procedure; promotion after three runs; a lesson about a rule goes to the rule; a lesson that would change a rail goes to the operator; and the distinction that decides the fix: a missing rule gets written, a rule not applied gets a check, never another sentence. (Chapter 13.)
6. **The reviewer, specified.** One fresh agent, never a fork, read-only, told what the repository is and what must never appear in it; its scope echo read against the diff and its tool-use count read before any finding or "clean" is trusted. And evidence tightened: a test never seen red is not evidence; a 200 is not a probe; compute a claim about your own numbers before writing it. (Chapters 4, 5, 6.)
7. **The cost rules, updated.** The operator's word overrides the model register until they say otherwise; an alias is not a model (read the id the session ran on); a lowered cap is a wind-down, never a stop; the effort default stays at the top until matched pairs show a cheaper setting does the same work with the same defects. (Chapters 3, 9.)
8. **Hygiene, extended.** A browser build is a window too (a new headless binary can raise a firewall dialog on the operator's screen); a script's flags are read from its argument handling, never from a `--help` probe; a scripted edit keeps each file's line endings. (Chapters 4, 10.)

### Also

- **The README's first screen** now says what this is, who it is for, and how to start in five minutes with commands that run (`python scripts/selftest.py` builds a toy repository and proves every script against it).
- **The close-out card's headings carry fixed emojis** so each section is found by shape in a long transcript. (Chapter 5; `templates/close-out-card.md`.)
- **The dispatch template** gained the research step's rungs and ceiling, the reviewer's specification, a hard stop, and the helper-result line. The briefing template records the reviewer's form, tool-use count and scope echo.
- **Providers.** [`adapters/providers.md`](adapters/providers.md): Grok, GLM, DeepSeek and OpenRouter reached through the tools that have adapters, one table, with "not verified" where a tool's documentation did not say.
- **Adapters re-checked** on 2026-09-23: Claude Code (`--fallback-model`, `--bg --exec`, `claude rm` and its worktree refusal, `claude daemon status`, pinning, per-session cross-session messaging, `isolation: worktree` for helpers) and Codex (the agent command center and worktree sessions on by default, from release `rust-v0.156.0` of 2026-09-22).
- **The publish gate** gained a literal-match mode (a list line starting with `=`) and a stricter home-path shape.
- **`.gitattributes`** pins LF line endings for every text file.
- **The optional `hooks/commit-msg`** refuses a co-author trailer or a "generated with" line.
- **The name.** The repository is now `ai-orchestrator` on GitHub; the old address redirects.

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
- **The name.** The repository's working name became `ai-orchestrator`, because the method is not specific to one tool. The GitHub rename waited for the owner's word and shipped with version 2.1.

### What did not change

One conversation per folder. The chair owns folders, the operator owns windows. Contracts as copy-paste. Validate before you relay; merged is not live. Merge by default with three gated carve-outs. Re-sync before every triage. The capture inbox. The one-directional information wall. A session never writes its successor's prompt.

## Version 1 (July 2026)

The initial playbook:

- worktrees plus an orchestrator conversation;
- copy-paste starter prompts;
- the eleven-section briefing as a chat block;
- the durable board;
- window management and the teardown order;
- the relay protocol;
- overnight autopilot;
- the installable `/orchestrator-brief` skill.
