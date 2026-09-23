# 10. Process hygiene

*What a session starts, a session stops. Measured on one workstation: 708 processes resident, 51 of them orphans holding 1.6 GB, every one a leftover of a coding-agent session that had already ended. Nothing had crashed. The sessions simply never cleaned up, and nobody counted.*

---

## Why this is a rule and not a chore

Coding agents do not reliably reap their children, particularly on Windows: each session spawns its own copy of every stdio tool server it is configured with and disconnects them only at exit, and a session stopped from outside often leaves its shell wrapper and that shell's child running. The upstream issue trackers say so; the reporters' own workaround is a cleanup step at the close. So the cleanup is ours, and it belongs in the close and in the tick, not in a monthly panic.

## The seven laws

1. **Every session kills what it started, before its close-out card.** Preview and development servers, the local back end, headless browsers, test servers, `sleep` and `tail` loops, any background helper. The close is not finished while one of them is running. A session that deliberately leaves something running names it in the briefing and says who stops it.
2. **The chair stops a folded session by id in the same minute it folds it.** A session that has delivered its briefing is done; its process tree is pure cost from that second on. Each one is about seven processes.
3. **The census runs at every tick and its counts go on the board.** Three numbers: resident sessions, tool-server processes, orphans. The census starts nothing, stops nothing and writes nothing, so it is safe to run as often as you like.
4. **Tool servers are scoped per project unless the operator names one global.** A stdio server in the user scope is launched again by every session on the machine, which at six sessions is six copies of everything. A remote HTTP server costs zero local processes and is always the better shape.
5. **NEVER kill by image name.** No `taskkill /IM`, no `Stop-Process -Name`, no `pkill -f`. The operator runs an editor, browsers, chat clients, note-takers and a browser bridge all day, and they share image names with what a session spawns. One session once ran `taskkill /F /IM python.exe` to clean up a single development server and terminated fifteen Python processes machine-wide, including other sessions' work. A process is stopped only by its id, only after its command line and parent chain prove it belongs to a finished session or a dead parent, and every stop is logged with the id, the command line and the proof.
6. **NEVER elevate.** A background session does not put a User Account Control prompt on the operator's screen. Before installing anything, take the path that needs no administrator: a user-scope package, or a release archive unpacked under the user's local programs folder with its published checksum verified. When a tool genuinely cannot be installed without elevation, the session stops, does not run the command, and puts the exact command in its briefing's needs-operator section. Measured: an install that fetched an unsigned installer threw a UAC dialog at the operator in the middle of an evening, from a publisher they had never heard of, with no session on screen to explain it.
7. **NEVER put a window on the operator's screen.** A background session invokes no windowed program. Windows Terminal's `--version` and `--help` open message boxes rather than printing; a session ran both, twice, and three "Help" dialogs with an OK button landed on the operator's desktop while they were in another window. The same class as law 6 for every windowed executable: a terminal, a file manager, `start`, a browser, an installer. The command line of a windowed tool is read from its documentation, never by running it. A session that genuinely needs a window (a signed-in browser, a file dialog) drives the operator's own browser through a bridge and says so in one line, or puts the step in its briefing.

   **A browser build is a window too.** A background session never downloads a new headless browser build (a test framework's `install` command, for instance). The first launch of a new browser binary can put a firewall dialog on the operator's screen, once per binary path: measured, a session's production walk installed a new headless shell late at night and the operator got the dialog with nothing on screen to explain it. A session that needs a browser uses the build already on the machine that its framework version names; if that build is missing, it stops, installs nothing, and puts the exact install command in its briefing for the chair to run in the day, with the operator warned.

   **A script is read, not probed.** A script's flags come from its own argument handling (its argument parser, or the lines that read its arguments), never from running it with `--help`: a script that does not know that flag runs its default action. Measured: `bump patch --help` on a hand-parsed version script was `bump patch`, and cut a second version.

## What counts as proof, before any stop

All four, every time:

- the parent is gone, or the parent chain reaches a process that is gone;
- the command line names a session id the tool's session list does not show, or a working directory no live session is running in;
- the process is at least five minutes old (a `sleep` a minute old belongs to a live session's shell call and exits on its own);
- the command line still matches what the census recorded, so a recycled process id cannot be mistaken for the one that was measured.

Re-verify every id against the live process table immediately before touching it, never against a snapshot taken minutes earlier. A census that flags a live session's helper as an orphan is a bug in the census, and it happened on the first run of the census script the estate that wrote this used (not included here: the census is your own tooling's job, and the four-part proof above is what it must apply).

**A stopped task is not a stopped process.** Stopping a long-running background command by the tool's task id routinely leaves the shell wrapper and its child resident on Windows. After stopping any such command, read the process table before believing it: two test runs stopped by task id were still running twenty minutes later with thousands of CPU-seconds on them, starving the measurement the close was waiting for. And the mirror: a session's children are found by parent chain from the session's own process id, never by a path match on a command line, because a test runner started from a script in a worktree does not carry the worktree's path and the negative proves nothing.

## Large downloads

Anything large (a model, a dataset, an installer over about a gigabyte, a bulk export) is asked about before it is fetched: what it is, how big, where it goes, one line. A background session that wants one puts it in its briefing's needs-operator section instead of pulling it. The destination is the drive the operator named for large files, under a named folder, never the user profile on the system drive.

## Never stopped, whatever the census says

Anything of the operator's own: the editor, the browsers, the chat and meeting clients, the note-takers, the sync clients, the password manager, the browser bridge their browsers launch, and every agent session the tool's own list shows with a process id. When in doubt, leave it and write it down.

## How to apply

- A session's close sequence gets one more line before the card: what did I start, and is it stopped.
- The chair's tick runs the census and puts the three counts on the board beside the running table.
- Adding a tool server is a scope decision, stated out loud: which repositories need it, and would a remote server do instead.
- A new orphan family the census does not recognize gets a role added to your census script rather than a one-off kill.
