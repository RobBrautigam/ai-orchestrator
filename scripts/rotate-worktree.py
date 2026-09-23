#!/usr/bin/env python3
"""rotate-worktree: the chair's branch rotation in a standing worktree, as one command, with its proof.

Rotation (chapter 2) is two git commands, and typed by hand at every launch it
drifts: a rotation under a live session, a branch reset off commits nobody pushed,
an environment file forgotten, and the one nobody sees, a worktree whose commit
hooks never run. Hook folders that a package manager GENERATES (and the
repository ignores) exist only where that install ran, so a fresh worktree can
run no hook at all while the main checkout runs all of them. This script
refuses the unsafe cases, rotates, copies what is missing, and ends on a proof
that the commit-msg hook really runs in that folder.

    python scripts/rotate-worktree.py <worktree> <branch>
    python scripts/rotate-worktree.py <worktree> <branch> --dry-run
    python scripts/rotate-worktree.py <worktree> --hooks-only

Options:
    --base <ref>           the branch point (default origin/main, else origin/master)
    --env <path>           a gitignored file to copy from the main checkout when missing (repeatable;
                           default .env and .env.local); its contents are never printed
    --live-minutes <n>     a file written in the last n minutes means a session may be live (default 10)
    --not-live             the chair has checked the tool's session list and nothing runs here
    --no-fetch             do not fetch before rotating
    --require-hook         exit 1 when no commit-msg hook runs in the worktree
    --dry-run              say what would be done; change nothing

In order, each step printed on its own line:
    1. REFUSED (exit 2, nothing changed) when the folder is the main checkout or not the top of a
       worktree; when a tracked file has uncommitted changes; when a file was written in the last
       --live-minutes and --not-live was not given; when <branch> exists holding commits that are on
       no remote branch (a reset would strand them).
    2. fetch, then `git checkout -q -B <branch> <base>`.
    3. each --env file copied from the main checkout when the worktree lacks it AND git ignores it.
    4. the proof: the commit-msg hook git would run in this worktree (core.hooksPath, else the
       repository's hooks folder) accepts an honest message and refuses one carrying a
       Co-Authored-By trailer, through `git hook run` (git 2.36 or later). No hook at all is said
       plainly; with --require-hook it is a failure.

Exit 0 done and proven; 1 a step failed or the hook did not behave; 2 refused.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time

HONEST = "docs: an honest message\n"
TRAILER = "docs: a message with a trailer\n\nCo-Authored-By: Some Tool\n"


def run(root: str, *args: str, check: bool = False) -> subprocess.CompletedProcess:
    out = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, encoding="utf-8")
    if check and out.returncode:
        raise RuntimeError(out.stderr.strip() or f"git {' '.join(args)} failed")
    return out


def say(step: str, text: str) -> None:
    print(f"{step}: {text}")


def main_checkout(wt: str) -> str:
    common = run(wt, "rev-parse", "--path-format=absolute", "--git-common-dir", check=True).stdout.strip()
    return os.path.dirname(common) if os.path.basename(common) == ".git" else common


def newest_write(wt: str) -> float:
    files = run(wt, "ls-files", "-z", "--cached", "--others", "--exclude-standard").stdout.split("\0")
    newest = 0.0
    for rel in files:
        if not rel:
            continue
        try:
            newest = max(newest, os.path.getmtime(os.path.join(wt, rel)))
        except OSError:
            pass
    return newest


def hook_proof(wt: str, require: bool) -> int:
    hooks_path = run(wt, "config", "--get", "core.hooksPath").stdout.strip()
    folder = os.path.join(wt, hooks_path) if hooks_path and not os.path.isabs(hooks_path) else hooks_path
    if not folder:
        folder = run(wt, "rev-parse", "--path-format=absolute", "--git-path", "hooks").stdout.strip()
    hook = os.path.join(folder, "commit-msg")
    if not os.path.isfile(hook):
        say("HOOK", f"no commit-msg hook runs in this worktree (looked in {folder})")
        return 1 if require else 0
    results = {}
    with tempfile.TemporaryDirectory() as tmp:
        for label, text in (("honest", HONEST), ("trailer", TRAILER)):
            path = os.path.join(tmp, f"{label}.txt")
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
            results[label] = run(wt, "hook", "run", "commit-msg", "--", path).returncode
    if results["honest"] == 0 and results["trailer"] != 0:
        say("PROVEN", f"the commit-msg hook at {hook} accepts an honest message and refuses a Co-Authored-By trailer")
        return 0
    say("HOOK FAILED", f"honest message exit {results['honest']}, trailer message exit {results['trailer']} (want 0 and non-zero)")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Rotate a standing worktree onto a fresh branch, refusing the unsafe cases, and prove its hook.")
    ap.add_argument("worktree")
    ap.add_argument("branch", nargs="?")
    ap.add_argument("--base", default=None)
    ap.add_argument("--env", action="append", default=None)
    ap.add_argument("--live-minutes", type=float, default=10.0)
    ap.add_argument("--not-live", action="store_true")
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--require-hook", action="store_true")
    ap.add_argument("--hooks-only", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    wt = os.path.abspath(args.worktree)
    if not args.hooks_only and not args.branch:
        say("REFUSED", "a branch name is required unless --hooks-only")
        return 2
    top = run(wt, "rev-parse", "--show-toplevel")
    if top.returncode or os.path.normcase(os.path.abspath(top.stdout.strip())) != os.path.normcase(wt):
        say("REFUSED", f"{wt} is not the top of a git worktree")
        return 2
    main = main_checkout(wt)
    if os.path.normcase(os.path.abspath(main)) == os.path.normcase(wt):
        say("REFUSED", f"{wt} is the main checkout; rotation happens only in a linked worktree")
        return 2
    if args.hooks_only:
        return hook_proof(wt, args.require_hook)

    dirty = run(wt, "status", "--porcelain", "--untracked-files=no").stdout.strip()
    if dirty:
        say("REFUSED", f"tracked files have uncommitted changes:\n{dirty}")
        return 2
    age_min = (time.time() - newest_write(wt)) / 60.0
    if age_min < args.live_minutes and not args.not_live:
        say("REFUSED", f"a file here was written {age_min:.1f} minutes ago; a session may be live. Check the tool's session list, then pass --not-live")
        return 2
    exists = run(wt, "rev-parse", "--verify", "--quiet", f"refs/heads/{args.branch}").returncode == 0
    if exists:
        stranded = run(wt, "rev-list", args.branch, "--not", "--remotes").stdout.split()
        if stranded:
            say("REFUSED", f"{args.branch} holds {len(stranded)} commit(s) on no remote branch; a reset would strand them")
            return 2
    say("CHECKED", f"linked worktree of {main}; no tracked changes; newest write {age_min:.1f} minutes ago; branch {'exists, fully pushed' if exists else 'new'}")

    if not args.no_fetch:
        if args.dry_run:
            say("DRY RUN", "would fetch origin")
        else:
            f = run(wt, "fetch", "-q", "origin")
            if f.returncode:
                say("FAILED", f"fetch: {f.stderr.strip()}")
                return 1
    base = args.base
    if not base:
        base = "origin/main" if run(wt, "rev-parse", "--verify", "--quiet", "origin/main").returncode == 0 else "origin/master"
    if args.dry_run:
        say("DRY RUN", f"would run: git checkout -q -B {args.branch} {base}")
    else:
        c = run(wt, "checkout", "-q", "-B", args.branch, base)
        if c.returncode:
            say("FAILED", f"checkout: {c.stderr.strip()}")
            return 1
        say("ROTATED", f"{args.branch} at {run(wt, 'rev-parse', '--short', 'HEAD').stdout.strip()} off {base}")

    for rel in args.env or [".env", ".env.local"]:
        src, dst = os.path.join(main, rel), os.path.join(wt, rel)
        if os.path.exists(dst) or not os.path.isfile(src):
            continue
        if run(wt, "check-ignore", "-q", rel).returncode != 0:
            say("SKIPPED", f"{rel} is not ignored here, so a copy would show as work; not copied")
            continue
        if args.dry_run:
            say("DRY RUN", f"would copy {rel} from the main checkout")
        else:
            shutil.copy2(src, dst)
            say("COPIED", f"{rel} from the main checkout (contents not printed)")

    return hook_proof(wt, args.require_hook)


if __name__ == "__main__":
    sys.exit(main())
