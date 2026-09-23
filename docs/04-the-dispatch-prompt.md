# 4. The dispatch prompt

*A dispatch prompt is a committed file the chair writes before it launches a session. Its header is for the record; its body is what the session reads first. A session that has to guess what the operator meant, what already exists, or where the edges are will guess wrong at least once an hour. The template is [`templates/dispatch-prompt.md`](../templates/dispatch-prompt.md).*

---

## Why a file, and why this shape

In the copy-paste era a starter prompt was a code block in chat. It was lost the moment the window closed, it could not be diffed, and when the chair revised it the operator had to hunt for the old one. A committed prompt file fixes all three, and it does one more thing: the header above its `---` line becomes the receipt. Six months later, "why did we build it this way" is answered by the prompt that asked for it, with the operator's own words and the drop file they came from.

The shape has two halves. Above the `---` line: the record (title, authorship, the operator's words with receipts, what is NOT on record, what exists, the read-first list). Below it: the body the session is launched with (who you are, the work in order, the rails, the close). The launch command passes only the body; the body's first instruction is to read the whole file.

## The header

### The title line

One long line: what the session is, why now, what it will change for the operator, and in parentheses the model, the effort and the slot count. It is the line the queue's running table quotes, so it is written to be read by the operator, not by the session.

### Authorship

Who wrote it (the chair, by its session name), when (the machine clock, with the date), the worktree and the branch and how they were prepared (created or rotated, off which main, what bootstrap is present), and the one sentence that governs the session's behavior: **nobody is at this session's keyboard.**

### The operator's words, verbatim, each with its receipt

Every sentence of the operator's that this session acts on, quoted exactly, with the file it lives in and the line or the clock. Not paraphrased: a paraphrase is the chair's reading, and the session should be able to read the operator's own reading. Where the operator's word was spoken and not written, the receipt is the file the chair wrote it into the same minute.

### What is NOT on record

The most useful section in the file, and the one the July model did not have. It names the decisions the operator has not made, so the session does not make them by accident: the pick on an open card, a name that has not been chosen, whether to publish, whether to send, whether to rename. A session that reaches one of these stops short of it, does everything that does not depend on it, and puts it in its briefing's section 7 with a best guess.

### What exists

The code, the files, the data, the earlier briefings, the research already done, the tools already installed, with paths. The session reads before it measures and measures before it builds. Where a fact is measured (a count, a size, a duration), the header gives the number so the session does not re-measure it, and says where the number came from.

### Read first, in full

An ordered list of files. "In full" is written out because a session that skims a briefing's headings and misses its section 8 will rebuild something already deferred for a reason.

## The body

### Who you are, and the pre-flight

One paragraph: the session's name, the worktree, the branch, who created it, the instruction to read this whole file first, the two behavioral laws (never ask a question; a progress note is never an end of turn, the only ends are the close-out card or a named blocker), and the pre-flight commands (`pwd`, the branch, the status, the last three commits, the machine clock). `git -C <path>` and absolute paths, never `cd`, because a working-directory change in one tool call is a surprise in the next.

### The work, in order

Numbered. Each step names its deliverable and how it is proven. Then the build, then the ship.

**The research pass comes first, and the prompt names it.** A build that starts from a blank page ignores the best work already published. The pass is sized to the build, and the prompt says which rungs to use and the spend ceiling:

- a small change skims the public repositories for the pattern (the hosting site's search, sorted by stars; the last push; the license);
- a page, a workflow or a system gets a fuller pass: the vendors' own documentation for exact command shapes, the top repositories' READMEs, practitioner threads when opinion matters, a rendered fetch for a page that needs one;
- a metered research API is called only through the repository's own client with its cap, and the ceiling for the whole pass is written in the prompt (chapter 9, rule 6).

The findings go in the briefing's section 3 with every source and its date. A session that skipped the pass says so in section 4, as a miss.

**Front-end work opens with mockups, never one design:** at least three, five to ten for a page or a flow that matters, clickable, on real data, in both themes, at phone and desktop widths, with one decision card for the operator's pick. A user flow is mocked as a flow, not a screen. Anything the operator has already collected (saved components, bookmarked animations, reference sites) is searched first, and the mockups cite what they used.

**The reviewer is specified, not implied.** One reviewer at the close, and the prompt says exactly what kind: a FRESH agent with its own context (never a fork of the session, which would share its blind spots), read-only, told what the repository is (public or private, and what must never appear in it), told what to hunt for, and told to echo its scope back. The session reads that scope echo against the diff and reads the reviewer's tool-use count before trusting a finding or a "clean": a reviewer that made three tool calls on a forty-file diff did not review it.

**A hard stop.** A prompt for work that ends in something irreversible (a publish, a rename, a send the operator authorized) names the clock after which the session does NOT do it, and writes why instead. A session that runs long is how a half-checked thing goes public.

### The rails

One paragraph of prohibitions, each specific. The recurring ones:

- nothing sent to anyone; nothing published; nothing renamed;
- no metered call without a stated ceiling; no LLM API call for work the session can do itself;
- no new dependency without a stated reason and its license;
- no fleet of helper agents (at most two or three, each with an explicit cheap model; one reviewer at the close, never an armada);
- the shared files (the queue, the board, the rules, the chair's own folders) read and never edited, with lines for them written into the briefing for the chair;
- the live sessions' worktrees untouched;
- never stop a process by image name; never elevate; never put a window on the operator's screen; kill what you start and prove it by process id;
- a script's flags are read from its own argument handling, never from a `--help` probe (a script that does not know `--help` runs its default action; one such probe cut a release);
- a scripted edit keeps each file's own line endings: count the carriage returns before and after, because the same edit tool writes different endings on different platforms (this repository pins LF in `.gitattributes`);
- `git -C` and absolute paths, never `cd`; the house spelling and punctuation.

A rail is written because something once went through the gap it closes. The rails paragraph is long because the list of things that went wrong is long.

### The close

The briefing file's path (the real date, the arc, the session number), its required contents beyond the eleven sections (the research with sources, the before-and-after numbers, each step's evidence, an effort line with the session's own token counts, deferrals as bullets, the loose-ends table, what the session started and what stopped it, by process id), the pull request and merge instruction, and then: the close-out card with the pointer block dead last; no starter prompt. Commits carry no AI co-author trailer.

## What makes a prompt incomplete

- A decision inside it for the session to "ask if unclear". There is nobody to ask; the prompt commits to one path.
- A research step missing. The first commit of a build without one is a build from a blank page.
- A model or effort missing from the title. The launch command must carry them and the title is where the chair checks that it did.
- A file path that does not exist. Before launch the chair confirms every path in the prompt (`git cat-file -e origin/main:<path>` for repository paths; `test -f` for the rest).
- Owed work that main already did. Before a prompt for an owed item is written, the chair runs [`scripts/done-on-main.py`](../scripts/done-on-main.py) (chapter 7) and reads every commit it names.
- A reviewer left unspecified, or a research step with no ceiling where a metered call is possible.
- A version number remembered rather than read. The chair reads the version file and the tags immediately before writing the ship line.
- A revision delivered as a diff. Any change to a prompt, however small, re-delivers the whole file.

## Relays into a running session

A session that needs something after launch (an answer the chair can give, a contract from another arc that just landed) gets it by the tool's cross-session message, never by a paste for the operator. The message is written like a prompt: complete, self-contained, with the receipt for anything it claims.
