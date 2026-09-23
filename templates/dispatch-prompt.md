# Dispatch prompt: <arc> session <N>, <what it is and why now, in one long line that the queue's running table can quote; what the operator will be able to see when it lands> (<model>, <effort>, <one slot or two>; <repository>)

Authored by the chair (<chair session name>) on <YYYY-MM-DD> at <HH:MM> (machine clock). Worktree `<absolute path>` (<the arc's standing worktree, rotated | created at launch>) on `<branch>` off `origin/main` (`<sha7>`), with `<checkout -b>` only; `<.env and node_modules present | bootstrap done at creation>`. Board row `<id>` (resolve it at the close for the parts you ship, naming what stays). The operator is at the keyboard in other windows; nobody is at this session's keyboard.

## The operator's words, verbatim (each with its receipt), and what is NOT on record

- <YYYY-MM-DD HH:MMx>, drop <n> (`docs/orchestration/operator-directives/<file>.md`, line <n>; read it whole): "<the operator's sentence, exactly as written>"
- <another receipt, same shape>
- **NOT on record:** <the decisions the operator has not made: a pick on an open card, a name, whether to publish or send or rename>. So: <what this session therefore does not do>, and the chair carries <the one question> at the fold.

## What exists (read before you write; measure before you build)

- <the code: paths, the function or view names, what they do today>
- <the data: the table, the counts as measured, where the count came from>
- <the earlier briefings on this arc, with the sections to read twice>
- <the research already done, with its record's path>
- <the tools installed and how they are invoked>

Read first, in full: <ordered list of files>.

---

You are <arc> session <N>, <short title>, in `<worktree path>` on branch `<branch>` (a worktree of <repository>; the chair <created | rotated> it). FIRST, read your full dispatch prompt: `<this file's committed path>`; the header above its `---` line carries the operator's words with their receipts, what is NOT on record, what exists and the read-first list. Nobody is at the keyboard: never ask a question; anything only the operator can decide goes in the briefing's section 7 with a best guess. A progress note is never an end of turn: the only ends are the close-out card or a named blocker. Pre-flight: `pwd`, `git -C <worktree> rev-parse --abbrev-ref HEAD`, `git -C <worktree> status`, `git -C <worktree> log --oneline -3`, the machine clock. `git` takes `-C`; never `cd`.

THE WORK, in this order:

1. **The research pass, <N> minutes, cited:** <which rungs: the public repositories on the pattern (stars, last push, license, what their READMEs do well); the tool's own documentation for the exact command shapes; practitioner threads if opinion matters>. No metered call without the ceiling stated here: <ceiling or "none">. Findings in the briefing's section 3 with sources and dates; a skipped pass is a miss in section 4. <For owed work: the chair ran `scripts/done-on-main.py` at <clock> and it named <nothing | the commits listed here>.>
2. **<Measure or read first>:** <the before table; the tests that exist; the numbers>.
3. **<Build step>:** <the deliverable and how it is proven: the failing test then the passing one; the walk at phone and desktop width in both themes; the migration applied and read back>.
4. **<Build step>**
5. **Ship:** tests green, every new test seen red once against a deliberate break of the code it guards; ONE reviewer at the close: a FRESH agent (never a fork) on <model>, read-only, told <what the repository is and what must never appear in it>, told to echo its scope; read its scope echo against the diff and its tool-use count before trusting a finding or a clean; record all of it in the briefing; never report a clean review that did not run; rebase onto live `origin/main`; a pull request; merged by you unless the change is on the gated list (destructive production actions, schema migrations, cross-arc conflicts); the deploy watched read-only; the live route probed from the live address; the version read from the file and the tags immediately before the bump.

HARD STOP: <clock>. If the gate is not passed by then, do NOT <publish | merge | send>; write why in the briefing and close.

RAILS: nothing is sent to anyone, posted anywhere, published or renamed; no metered call beyond the ceiling above; no LLM API call for work you can do yourself; no new dependency without a stated reason and its license; no fleet of helper agents (at most <two>, each with an explicit cheap model); the queue file, the board, the rules and the chair's folders are read and never edited (lines for them go in the briefing for the chair); the live sessions' worktrees untouched (whatever the session list shows when you start); never call a worktree-creation tool from inside this session (the worktree you are in IS the isolation; write in place); never stop a process by image name; never elevate; never put a window on the operator's screen (no windowed program, no browser build download); kill what you start and prove it by process id; a script's flags come from its own argument handling, never a `--help` probe; a scripted edit keeps each file's line endings; every clock from the machine clock; any helper you launch is told its final result is displayed to the operator (one anchored line, plain words, detail in a file at <path>); `git -C` and absolute paths, never `cd`; <house spelling and punctuation rules>.

CLOSE: `docs/orchestration/briefings/<real date>-<arc>-s<N>.md` in this worktree (the machine clock's date; the eleven sections; the research with sources; the before-and-after numbers; each step's evidence; every sentence whose subject is the operator carrying its receipt inline or reading "not verified"; an `EFFORT` line in section 2 reading `EFFORT | <session kind> | model <m> | effort <e> | session <id> | started <iso> | tokens_input | tokens_output | cache_read | cache_write | reviewer_findings | subagents | metered_spend $` filled from the tool's own usage record; deferrals as BULLETS under section 8; the loose-ends table; what you started and what stopped it, by process id) committed and pushed through a pull request, merged; then the close-out card with the pointer block dead last; no starter prompt. Commits carry no AI co-author trailer and no "generated with" line.
