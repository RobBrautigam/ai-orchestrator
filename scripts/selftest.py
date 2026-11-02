#!/usr/bin/env python3
"""selftest: the repository's scripts, proven on a throwaway repository in a temporary folder.

Needs only git (2.36 or later, for `git hook run`) and Python 3.9 or later. It builds a
toy "origin", a main checkout with a queue file, a standing worktree and a landed
briefing, then runs every script in scripts/ and the hook in hooks/ against it, the
refusals and the negative controls included. Nothing outside the temporary folder is
touched, and the folder is deleted at the end (--keep leaves it for reading).

    python scripts/selftest.py            # under two minutes on Windows (1 min 21 s and 1 min 43 s measured for 39 checks); one line per check
    python scripts/selftest.py --keep     # leave the toy repositories on disk and print where
    python scripts/selftest.py --scripts-dir <dir> --hook <file>   # run the checks against copies (a mutation test)

Exit 0 when every check passed, 1 otherwise.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
# Your system and global git configuration are shut out (GIT_CONFIG_GLOBAL, git 2.32 or later), so a global
# core.hooksPath, commit signing or template folder of yours is never read, used or touched by the toy repositories.
ENV = dict(os.environ, GIT_AUTHOR_NAME="selftest", GIT_AUTHOR_EMAIL="selftest", GIT_COMMITTER_NAME="selftest",
           GIT_COMMITTER_EMAIL="selftest", GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
           GIT_TERMINAL_PROMPT="0")

QUEUE = """# The dispatch queue

**At a glance:** 2 running in 2 of 4 slots | 0 waiting | 1 landed.

## Running: 2 sessions in 2 of 4 slots

| Slot | Repo | Session | Model | Worktree | Since | Expected | Hard stop | What it does |
|---|---|---|---|---|---|---|---|---|
| 1 | toy | demo-s1 1a2b3c4d | opus, high | ../toy-demo | 2026-01-15 08:40 | 45 min | 90 min | The demo arc's first session |
| 2 | toy | docs-s1 5e6f7a8b | sonnet, low | ../toy-docs | 2026-01-15 08:45 | | | A mechanical docs sweep |
| 3 | | (free) | | | | | | |

## Landed since 2026-01-08: 1 session

| Session | Repo | Launched | Landed | Result |
|---|---|---|---|---|
| search-s1 | toy | 2026-01-15 06:02 | 2026-01-15 09:10 | Search answers in under a second |
"""

results: list[tuple[bool, str]] = []
HOOK = os.path.join(REPO, "hooks", "commit-msg")
PRE_COMMIT = os.path.join(REPO, "hooks", "pre-commit")


def check(ok: bool, text: str, detail: str = "") -> None:
    results.append((ok, text))
    print(f"{'PASS' if ok else 'FAIL'} {len(results):2d}: {text}")
    if not ok and detail:
        print("        " + detail.strip().replace("\n", "\n        ")[:1500])


def git(cwd: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, encoding="utf-8", env=ENV)


def script(scripts: str, name: str, *args: str, cwd: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, os.path.join(scripts, name), *args], capture_output=True, text=True,
                          encoding="utf-8", env=ENV, cwd=cwd)


def write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def commit(cwd: str, message: str, *paths: str) -> None:
    git(cwd, "add", *(paths or (".",)))
    out = git(cwd, "-c", "commit.gpgsign=false", "commit", "-q", "-m", message)
    if out.returncode:
        raise RuntimeError(out.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description="Prove the repository's scripts on a throwaway repository.")
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--scripts-dir", default=HERE)
    ap.add_argument("--hook", default=os.path.join(REPO, "hooks", "commit-msg"))
    ap.add_argument("--pre-commit", default=os.path.join(REPO, "hooks", "pre-commit"))
    args = ap.parse_args()
    scripts = os.path.abspath(args.scripts_dir)
    global HOOK, PRE_COMMIT
    HOOK = os.path.abspath(args.hook)
    PRE_COMMIT = os.path.abspath(args.pre_commit)
    tmp = tempfile.mkdtemp(prefix="ai-orchestrator-selftest-")
    try:
        run_checks(tmp, scripts)
    finally:
        if args.keep:
            print(f"selftest: the toy repositories are in {tmp}")
        else:
            shutil.rmtree(tmp, onerror=lambda f, p, e: (os.chmod(p, stat.S_IWRITE), f(p)))
    passed = sum(1 for ok, _ in results if ok)
    print(f"selftest: {passed} of {len(results)} checks passed")
    return 0 if passed == len(results) else 1


def run_checks(tmp: str, scripts: str) -> None:
    origin, main, wt = (os.path.join(tmp, n) for n in ("origin.git", "toy", "toy-demo"))
    git(tmp, "init", "-q", "--bare", "-b", "main", origin)
    git(tmp, "clone", "-q", origin, main)
    git(main, "checkout", "-q", "-b", "main")
    write(os.path.join(main, "README.md"), "# toy\n")
    write(os.path.join(main, ".gitignore"), ".env\n")
    write(os.path.join(main, ".env"), "EXAMPLE=1\n")
    write(os.path.join(main, "docs/orchestration/prompts/QUEUE.md"), QUEUE)
    write(os.path.join(main, "src/app.txt"), "refunds\n")
    write(os.path.join(main, "src/other.txt"), "other\n")
    commit(main, "chore: the toy repository")
    git(main, "push", "-q", "-u", "origin", "main")

    # --- the commit-msg hook -------------------------------------------------------------
    hooks = git(main, "rev-parse", "--path-format=absolute", "--git-path", "hooks").stdout.strip()
    inside = os.path.commonpath([os.path.realpath(hooks), os.path.realpath(tmp)]) == os.path.realpath(tmp)
    check(inside, "the toy repository's hooks folder is inside the temporary folder (nothing of yours is touched)", hooks)
    if not inside:
        return
    os.makedirs(hooks, exist_ok=True)
    dst = os.path.join(hooks, "commit-msg")
    shutil.copy(HOOK, dst)
    os.chmod(dst, 0o755)
    write(os.path.join(main, "notes.txt"), "a note\n")
    git(main, "add", "notes.txt")
    bad = git(main, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "docs: a note", "-m", "Co-Authored-By: Some Tool")
    check(bad.returncode != 0, "the hook refuses a commit that carries a Co-Authored-By trailer", bad.stdout + bad.stderr)
    bad2 = git(main, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "docs: a note", "-m", "Generated with Some Tool")
    check(bad2.returncode != 0, "the hook refuses a commit that carries a \"Generated with\" line", bad2.stdout + bad2.stderr)
    bad3 = git(main, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "docs: a note", "-m", "🤖 Generated with Some Tool")
    check(bad3.returncode != 0, "the hook refuses the same line behind an emoji", bad3.stdout + bad3.stderr)
    ok = git(main, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "docs: a lockfile generated with the package manager")
    check(ok.returncode == 0, "the hook lets an honest commit through, even one that mentions something generated with a tool", ok.stdout + ok.stderr)
    git(main, "push", "-q", "origin", "main")

    # --- wall-check: the publish gate and its negative controls ---------------------------
    listfile = os.path.join(tmp, "wall-list.txt")
    write(listfile, "# a toy list, outside the toy repository\nacme corp\n=order_events\n")
    wc = ("wall-check.py", "--list", listfile, "--root", main, "--include-untracked")
    r = script(scripts, *wc)
    check(r.returncode == 0 and " 0 hits" in r.stdout, "wall-check reads a clean tree as 0 hits, exit 0", r.stdout + r.stderr)
    # The planted email and home path are assembled at run time so this file itself never carries them.
    email, home = "jane" + "@" + "example.invalid", "C:" + "\\Users\\" + "jane\\notes"
    write(os.path.join(main, "plant.md"), f"Acme-Corp owns the order_events table; mail {email}; {home}\n"
                                          "The order events are prose and pass.\n")
    r = script(scripts, *wc)
    hits = r.stdout
    check(r.returncode == 1 and "term 'acme corp'" in hits and "term '=order_events'" in hits and "email address" in hits
          and "home path" in hits and hits.count("plant.md:2") == 0,
          "wall-check catches a planted file (a listed name, a literal table name, an email, a home path) and passes the prose line",
          hits + r.stderr)
    os.remove(os.path.join(main, "plant.md"))
    r = script(scripts, *wc)
    check(r.returncode == 0, "wall-check is back to 0 hits once the planted file is removed", r.stdout + r.stderr)

    # --- fold-check -------------------------------------------------------------------------
    fc = ("fold-check.py", "--root", main, "--exit-code", "--now", "2026-01-15 09:00")
    r = script(scripts, *fc)
    check(r.returncode == 0 and "all clear: 2 session(s)" in r.stdout and "no hard stop recorded for docs-s1" in r.stdout,
          "fold-check reads all clear before anything landed, and names the session with no hard stop", r.stdout + r.stderr)
    fc_clock = ("fold-check.py", "--root", main, "--exit-code")
    r = script(scripts, *fc_clock, "--now", "2026-01-15 09:40")
    check(r.returncode == 1 and "OVER EXPECTED: demo-s1 (slot 1) is 15 minute(s) over" in r.stdout and "PAST HARD STOP" not in r.stdout,
          "fold-check names a session over its expected time while it is inside its hard stop", r.stdout + r.stderr)
    r = script(scripts, *fc_clock, "--now", "2026-01-15 10:30")
    check(r.returncode == 1 and "PAST HARD STOP: demo-s1 (slot 1) is 20 minute(s) past" in r.stdout and "OVER EXPECTED" not in r.stdout,
          "fold-check names a session past its hard stop, once, before anything else about its clock", r.stdout + r.stderr)
    with open(os.path.join(main, "docs/orchestration/prompts/QUEUE.md"), encoding="utf-8") as fh:
        queue_now = fh.read()
    write(os.path.join(main, "docs/orchestration/prompts/QUEUE.md"), queue_now.replace("| 45 min | 90 min |", "| 45 min | soonish |"))
    r = script(scripts, *fc_clock, "--now", "2026-01-15 09:00")
    check(r.returncode == 2 and "soonish" in r.stdout and "NOT an all clear" in r.stdout,
          "fold-check says it could not check when a hard stop cell cannot be read, never all clear", r.stdout + r.stderr)
    write(os.path.join(main, "docs/orchestration/prompts/QUEUE.md"), queue_now)
    r = script(scripts, *fc, "--ref", "origin/no-such-branch")
    check(r.returncode == 2 and "NOT an all clear" in r.stdout and "all clear:" not in r.stdout,
          "fold-check never says all clear when it could not read the ref", r.stdout + r.stderr)
    write(os.path.join(main, "docs/orchestration/briefings/2026-01-15-demo-s1-interim.md"), "# interim\n")
    commit(main, "docs: an interim briefing")
    git(main, "push", "-q", "origin", "main")
    r = script(scripts, *fc)
    check(r.returncode == 0, "fold-check does not read an interim briefing as a landing", r.stdout + r.stderr)
    write(os.path.join(main, "docs/orchestration/briefings/2026-01-15-demo-s1.md"), "# demo session 1\n")
    commit(main, "docs: the demo session 1 briefing")
    git(main, "push", "-q", "origin", "main")
    r = script(scripts, *fc)
    check(r.returncode == 1 and "FOLD OWED: demo-s1 landed" in r.stdout and "docs-s1" not in r.stdout,
          "fold-check names the landed session as a fold owed, and only that one", r.stdout + r.stderr)
    live = os.path.join(tmp, "live.json")
    with open(live, "w", encoding="utf-8") as fh:
        json.dump([{"name": "demo-s1", "id": "1a2b3c4d-0000", "state": "completed"},
                   {"name": "review-s1", "id": "9c9c9c9c-0000", "state": "working"},
                   {"name": "search-s1", "id": "7d7d7d7d-0000", "state": "idle"}], fh)
    r = script(scripts, *fc, "--sessions", live)
    out = r.stdout
    check("GONE: the running table shows docs-s1" in out and "UNTRACKED: the tool lists review-s1" in out
          and "search-s1" not in out,
          "fold-check with the tool's list names the gone session and the untracked one, and leaves an ended folded session alone",
          out + r.stderr)

    # --- rotate-worktree ------------------------------------------------------------------
    git(main, "worktree", "add", "-q", wt, "-b", "feat/demo-s1", "origin/main")
    rw = "rotate-worktree.py"
    r = script(scripts, rw, main, "feat/x", "--not-live")
    check(r.returncode == 2 and "is the main checkout" in r.stdout, "rotate-worktree refuses the main checkout", r.stdout + r.stderr)
    r = script(scripts, rw, wt, "feat/demo-s2")
    check(r.returncode == 2 and "may be live" in r.stdout, "rotate-worktree refuses a folder written minutes ago unless told nothing runs there", r.stdout + r.stderr)
    write(os.path.join(wt, "README.md"), "# toy, edited\n")
    r = script(scripts, rw, wt, "feat/demo-s2", "--not-live")
    check(r.returncode == 2 and "uncommitted changes" in r.stdout, "rotate-worktree refuses a worktree with uncommitted tracked changes", r.stdout + r.stderr)
    git(wt, "checkout", "-q", "--", "README.md")
    r = script(scripts, rw, wt, "feat/demo-s2", "--not-live", "--require-hook")
    check(r.returncode == 0 and "ROTATED: feat/demo-s2" in r.stdout and "COPIED: .env" in r.stdout and "PROVEN:" in r.stdout
          and git(wt, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip() == "feat/demo-s2",
          "rotate-worktree rotates, copies the ignored .env, and proves the commit-msg hook runs there", r.stdout + r.stderr)
    write(os.path.join(wt, "src/app.txt"), "refunds, unpushed\n")
    commit(wt, "feat: work nobody pushed", "src/app.txt")
    r = script(scripts, rw, wt, "feat/demo-s2", "--not-live")
    check(r.returncode == 2 and "on no remote branch" in r.stdout, "rotate-worktree refuses to reset a branch holding unpushed commits", r.stdout + r.stderr)
    os.remove(dst)
    r = script(scripts, rw, wt, "--hooks-only", "--require-hook")
    check(r.returncode == 1 and "no commit-msg hook runs" in r.stdout, "rotate-worktree says plainly when no hook runs in the worktree", r.stdout + r.stderr)

    # --- done-on-main ---------------------------------------------------------------------
    brief = "docs/orchestration/briefings/2026-01-15-demo-s1.md"
    write(os.path.join(main, "src/app.txt"), "refunds, with a retry button\n")
    commit(main, "fix: retry button for failed refunds", "src/app.txt")
    git(main, "push", "-q", "origin", "main")
    dm = ("done-on-main.py", "--root", main, "--briefing", brief)
    r = script(scripts, *dm, "--files", "src/app.txt")
    check(r.returncode == 1 and "BY FILES:" in r.stdout and "retry button" in r.stdout,
          "done-on-main names the commit that touched the owed item's file", r.stdout + r.stderr)
    r = script(scripts, *dm, "--files", "src/other.txt", "--title", "add a retry button to failed refunds")
    check(r.returncode == 1 and "BY WORDS:" in r.stdout, "done-on-main names a commit by its subject's words when the file differs", r.stdout + r.stderr)
    r = script(scripts, *dm, "--files", "src/other.txt")
    check(r.returncode == 0 and "nothing on the main line" in r.stdout, "done-on-main reads clean when nothing touched the file", r.stdout + r.stderr)
    r = script(scripts, *dm, "--files", "src/missing.txt")
    check(r.returncode == 2 and "REFUSED" in r.stdout, "done-on-main refuses rather than claim a check that saw nothing", r.stdout + r.stderr)
    r = script(scripts, "done-on-main.py", "--root", main, "--no-fetch", "--since", "deadbeef", "--files", "src/app.txt")
    check(r.returncode == 2 and "is not a commit here" in r.stdout, "done-on-main refuses a mistyped start instead of reading clean", r.stdout + r.stderr)

    block_checks(tmp, scripts)
    prompt_checks(tmp, scripts, main)
    publish_gate_checks(tmp, scripts)


GOOD_BLOCK = """RESULT: Refunds now show on the customer's statement the same day.
BOARD: payments session 4 landed, the refund posts to the ledger synchronously (PR 214, v1.41.3)
EFFORT: opus, high, 52 minutes, 3.1M tokens in, 41K out
FINDINGS: 2 from the reviewer, both fixed
SPEND: $0
OWED: Retry the stuck December refunds || twelve refunds stuck before the fix || the next payments session || next || null
OWED: Pick the statement wording || two wordings are live behind a flag || the operator answers || later || operator: answer
CARRY: 3f9a2c1e done: section 3.3
"""


def block_checks(tmp: str, scripts: str) -> None:
    # --- fold-lines: the briefing's fold block ---------------------------------------------
    good = os.path.join(tmp, "briefings", "2026-01-15-payments-s4.md")
    write(good, "# Payments session 4\n\n## 1. Intent\n\nMatched cleanly.\n\n```fold-lines\n" + GOOD_BLOCK + "```\n")
    r = script(scripts, "fold-lines.py", good, "--carry", "3f9a2c1e")
    check(r.returncode == 0 and "FOLD LINES OK" in r.stdout and "OWED (later, on the operator: answer): Pick the statement wording" in r.stdout
          and "CARRY 3f9a2c1e: done" in r.stdout,
          "fold-lines reads a whole block and prints what the fold will file", r.stdout + r.stderr)
    none = os.path.join(tmp, "briefings", "2026-01-15-payments-s5.md")
    write(none, "# Payments session 5\n\n```\nRESULT: a plain fence is not the block\n```\n")
    r = script(scripts, "fold-lines.py", none)
    check(r.returncode == 1 and "no ```fold-lines block" in r.stdout, "fold-lines refuses a briefing with no fold block", r.stdout + r.stderr)
    bad_block = (GOOD_BLOCK.replace("|| next || null", "|| soon || null")
                 .replace("BOARD: payments session 4 landed,", "BOARD: payments | session 4 landed,")
                 .replace("RESULT: Refunds", "RESULT: " + "Very long. " * 20 + "Refunds")
                 .replace("|| later || operator: answer", "|| later"))
    bad = os.path.join(tmp, "briefings", "2026-01-15-payments-s6.md")
    write(bad, "# Payments session 6\n\n```fold-lines\n" + bad_block + "```\n")
    r = script(scripts, "fold-lines.py", bad, "--carry", "91be07d4")
    out = r.stdout
    check(r.returncode == 1 and "band 'soon'" in out and "BOARD carries a pipe" in out and "RESULT is" in out
          and "needs five fields" in out and "carried 91be07d4" in out,
          "fold-lines refuses a bad band, a pipe in the board line, a long result, a four-field owed line and an uncarried row, naming each",
          out + r.stderr)


READY_PROMPT = """# Dispatch prompt: search session 2, the ranking behind a flag (opus, high, one slot; toy)

Read first, in full: `src/app.txt`, `docs/orchestration/prompts/QUEUE.md`.

---

You are search session 2 in ../toy-search on feat/search-s2. Nobody is at the keyboard: never ask the operator a question.

DONE MEANS: the ranking merged behind its flag, and the measurement beats the baseline on the fixture.

EXPECTED: 90 minutes. HARD STOP: 120 minutes after launch.
"""


def prompt_checks(tmp: str, scripts: str, main: str) -> None:
    # --- prompt-check: a dispatch prompt ready to launch, or refused ------------------------
    ready = os.path.join(tmp, "prompts", "ready.md")
    write(ready, READY_PROMPT)
    r = script(scripts, "prompt-check.py", ready, "--root", main)
    check(r.returncode == 0 and "OK DONE MEANS: the ranking merged" in r.stdout and "OK HARD STOP: 120 minutes after launch" in r.stdout
          and "OK EXPECTED: 90 minutes" in r.stdout and "read-first src/app.txt: ok" in r.stdout,
          "prompt-check passes a ready prompt (a done-means state, a timed stop, an expected time, read-first paths on main)", r.stdout + r.stderr)
    timed = READY_PROMPT.replace("DONE MEANS: the ranking merged behind its flag, and the measurement beats the baseline on the fixture.",
                                 "DONE MEANS: two hours after launch.").replace("HARD STOP: 120 minutes after launch.", "HARD STOP at 5:30 pm.")
    path = os.path.join(tmp, "prompts", "timed.md")
    write(path, timed)
    r = script(scripts, "prompt-check.py", path, "--root", main)
    check(r.returncode == 1 and "only a time" in r.stdout and "am, pm or a zone" in r.stdout,
          "prompt-check refuses a done-means line that is only a time, and a hard stop read in am or pm", r.stdout + r.stderr)
    head_only = READY_PROMPT.replace("`src/app.txt`", "`src/moved.txt`").replace(
        "DONE MEANS: the ranking", "Notes: the ranking").replace("---\n", "DONE MEANS: the ranking merged.\n\n---\n", 1)
    path = os.path.join(tmp, "prompts", "head-only.md")
    write(path, head_only)
    r = script(scripts, "prompt-check.py", path, "--root", main)
    check(r.returncode == 1 and "in the head only" in r.stdout and "read-first path not on origin/main and not on disk: src/moved.txt" in r.stdout,
          "prompt-check refuses a done-means line the session never receives and a read-first path that moved", r.stdout + r.stderr)
    asking = READY_PROMPT.replace("never ask the operator a question.", "ask the operator if anything is unclear.")
    path = os.path.join(tmp, "prompts", "asking.md")
    write(path, asking)
    r = script(scripts, "prompt-check.py", path, "--root", main)
    check(r.returncode == 1 and "tells the session to ask" in r.stdout,
          "prompt-check refuses a body that tells an unattended session to ask (and passes \"never ask\")", r.stdout + r.stderr)


def publish_gate_checks(tmp: str, scripts: str) -> None:
    # --- the publish gate at the moment of action: pre-commit, commit-msg, a pull request body --
    pub = os.path.join(tmp, "toy-public")
    git(tmp, "init", "-q", "-b", "main", pub)
    hooks = git(pub, "rev-parse", "--path-format=absolute", "--git-path", "hooks").stdout.strip()
    inside = os.path.commonpath([os.path.realpath(hooks), os.path.realpath(tmp)]) == os.path.realpath(tmp)
    check(inside, "the public toy repository's hooks folder is inside the temporary folder", hooks)
    if not inside:
        return
    os.makedirs(hooks, exist_ok=True)
    for name, src in (("pre-commit", PRE_COMMIT), ("commit-msg", HOOK)):
        shutil.copy(src, os.path.join(hooks, name))
        os.chmod(os.path.join(hooks, name), 0o755)
    listfile = os.path.join(tmp, "public-wall-list.txt")
    write(listfile, "acme corp\n")
    fwd = lambda p: p.replace("\\", "/")
    git(pub, "config", "wallcheck.list", fwd(listfile))
    git(pub, "config", "wallcheck.script", fwd(os.path.join(scripts, "wall-check.py")))
    git(pub, "config", "wallcheck.python", fwd(sys.executable))
    write(os.path.join(pub, "README.md"), "# a public toy\n")
    git(pub, "add", "README.md")
    ok = git(pub, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "docs: a clean readme")
    check(ok.returncode == 0, "the pre-commit gate lets a clean commit through", ok.stdout + ok.stderr)
    write(os.path.join(pub, "notes.md"), "Built for Acme Corp's launch.\n")
    git(pub, "add", "notes.md")
    bad = git(pub, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "docs: launch notes")
    check(bad.returncode != 0 and "notes.md:1: term 'acme corp'" in bad.stdout + bad.stderr,
          "the pre-commit gate refuses a commit that stages a listed name, naming the file and line", bad.stdout + bad.stderr)
    git(pub, "rm", "-q", "--cached", "notes.md")
    write(os.path.join(pub, "CHANGELOG.md"), "# changes\n")
    git(pub, "add", "CHANGELOG.md")
    bad = git(pub, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "docs: the acme-corp changelog")
    check(bad.returncode != 0 and "commit message" in bad.stdout + bad.stderr,
          "the commit-msg gate refuses a message that carries a listed name", bad.stdout + bad.stderr)
    body = os.path.join(tmp, "pr-body.md")
    write(body, "## Summary\n\nThe launch work for ACME CORP.\n")
    r = script(scripts, "wall-check.py", "--list", listfile, "--text-file", body)
    check(r.returncode == 1 and "term 'acme corp'" in r.stdout, "wall-check catches a listed name in a pull request body before it is posted", r.stdout + r.stderr)


if __name__ == "__main__":
    sys.exit(main())
