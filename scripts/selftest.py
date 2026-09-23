#!/usr/bin/env python3
"""selftest: the repository's scripts, proven on a throwaway repository in a temporary folder.

Needs only git (2.36 or later, for `git hook run`) and Python 3.9 or later. It builds a
toy "origin", a main checkout with a queue file, a standing worktree and a landed
briefing, then runs every script in scripts/ and the hook in hooks/ against it, the
refusals and the negative controls included. Nothing outside the temporary folder is
touched, and the folder is deleted at the end (--keep leaves it for reading).

    python scripts/selftest.py            # about ten seconds; prints one line per check
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
ENV = dict(os.environ, GIT_AUTHOR_NAME="selftest", GIT_AUTHOR_EMAIL="selftest", GIT_COMMITTER_NAME="selftest",
           GIT_COMMITTER_EMAIL="selftest", GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0")

QUEUE = """# The dispatch queue

**At a glance:** 2 running in 2 of 4 slots | 0 waiting | 1 landed.

## Running: 2 sessions in 2 of 4 slots

| Slot | Repo | Session | Model | Worktree | Since | What it does |
|---|---|---|---|---|---|---|
| 1 | toy | demo-s1 1a2b3c4d | opus, high | ../toy-demo | 2026-01-15 08:40 | The demo arc's first session |
| 2 | toy | docs-s1 5e6f7a8b | sonnet, low | ../toy-docs | 2026-01-15 08:45 | A mechanical docs sweep |
| 3 | | (free) | | | | |

## Landed since 2026-01-08: 1 session

| Session | Repo | Launched | Landed | Result |
|---|---|---|---|---|
| search-s1 | toy | 2026-01-15 06:02 | 2026-01-15 09:10 | Search answers in under a second |
"""

results: list[tuple[bool, str]] = []
HOOK = os.path.join(REPO, "hooks", "commit-msg")


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
    out = git(cwd, "commit", "-q", "-m", message)
    if out.returncode:
        raise RuntimeError(out.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description="Prove the repository's scripts on a throwaway repository.")
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--scripts-dir", default=HERE)
    ap.add_argument("--hook", default=os.path.join(REPO, "hooks", "commit-msg"))
    args = ap.parse_args()
    scripts = os.path.abspath(args.scripts_dir)
    global HOOK
    HOOK = os.path.abspath(args.hook)
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
    os.makedirs(hooks, exist_ok=True)
    dst = os.path.join(hooks, "commit-msg")
    shutil.copy(HOOK, dst)
    os.chmod(dst, 0o755)
    write(os.path.join(main, "notes.txt"), "a note\n")
    git(main, "add", "notes.txt")
    bad = git(main, "commit", "-q", "-m", "docs: a note", "-m", "Co-Authored-By: Some Tool")
    check(bad.returncode != 0, "the hook refuses a commit that carries a Co-Authored-By trailer", bad.stdout + bad.stderr)
    bad2 = git(main, "commit", "-q", "-m", "docs: a note", "-m", "Generated with Some Tool")
    check(bad2.returncode != 0, "the hook refuses a commit that carries a \"Generated with\" line", bad2.stdout + bad2.stderr)
    ok = git(main, "commit", "-q", "-m", "docs: a note")
    check(ok.returncode == 0, "the hook lets an honest commit through", ok.stdout + ok.stderr)
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
    fc = ("fold-check.py", "--root", main, "--exit-code")
    r = script(scripts, *fc)
    check(r.returncode == 0 and "all clear: 2 session(s)" in r.stdout, "fold-check reads all clear before anything landed", r.stdout + r.stderr)
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


if __name__ == "__main__":
    sys.exit(main())
