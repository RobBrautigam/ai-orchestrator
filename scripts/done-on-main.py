#!/usr/bin/env python3
"""done-on-main: before the chair writes a prompt for owed work, is that work already done on main?

An owed item (a briefing's section 8 bullet, a finding deferred, a follow-up) sits
in the registry while other sessions keep merging. By the time its prompt is
written, another arc may have fixed it in passing, and a session launched on it
spends an hour rediscovering that. This check reads git only; it changes nothing
but the remote-tracking refs when it fetches.

    python scripts/done-on-main.py --briefing docs/orchestration/briefings/2026-01-14-payments-s3.md \\
        --files src/refunds/retry.py src/refunds/view.py --title "retry button for failed refunds"
    python scripts/done-on-main.py --since 3f9a2c1 --files src/search/rank.py

Options:
    --root <dir>          the repository (default: the current directory)
    --ref <ref>           the main line to read (default origin/main)
    --briefing <path>     the briefing the owed item came from; its first commit on the ref is the start
    --since <rev>         the start, when there is no briefing
    --files <path> ...    the files the item names (a path the ref's tree does not hold is named and left out)
    --title <words>       the item's title; commits whose subjects share at least --min-shared of its
                          uncommon words are proposed too (a fix can land in a file the item never named)
    --min-shared <n>      default 2
    --no-fetch            do not fetch first (default: fetch origin, and REFUSE on a failed fetch rather
                          than answer from a stale ref)

Exit 0 nothing on the ref since the start touched the files or shares the words; 1 at least one commit
is named (read each before writing the prompt); 2 refused (no start, a start or ref that does not resolve,
a failed fetch or any failed git call, or no file resolved and no title, so a clean answer would claim a
check that saw nothing). Paths may be written with either slash.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys

COMMON = set("""a an and are as at be by for from in into is it its of on or that the this to with without
add adds added fix fixes fixed update updates updated docs doc feat chore refactor test tests make makes use
now new more one two all any not no when where which after before only also each every than then""".split())


def git(root: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, encoding="utf-8")


def ok_or_refuse(out: subprocess.CompletedProcess, what: str) -> str | None:
    """The command's output, or None after printing a refusal: a failed git call is never an empty answer."""
    if out.returncode:
        print(f"REFUSED: {what} failed, and an empty answer would read as clean: {out.stderr.strip()}")
        return None
    return out.stdout


def words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) >= 4 and w not in COMMON}


def main() -> int:
    ap = argparse.ArgumentParser(description="Is an owed item's work already on main? Read-only apart from a fetch.")
    ap.add_argument("--root", default=".")
    ap.add_argument("--ref", default="origin/main")
    ap.add_argument("--briefing")
    ap.add_argument("--since")
    ap.add_argument("--files", nargs="*", default=[])
    ap.add_argument("--title", default="")
    ap.add_argument("--min-shared", type=int, default=2)
    ap.add_argument("--no-fetch", action="store_true")
    args = ap.parse_args()
    root = args.root

    if not args.no_fetch:
        f = git(root, "fetch", "-q", "origin")
        if f.returncode:
            print(f"REFUSED: the fetch failed, and a stale {args.ref} would answer wrongly: {f.stderr.strip()}")
            return 2

    if git(root, "rev-parse", "--verify", "--quiet", args.ref).returncode:
        print(f"REFUSED: {args.ref} does not resolve here")
        return 2
    start = args.since
    if args.briefing:
        added = git(root, "log", "--first-parent", "--diff-filter=A", "--format=%H", args.ref, "--", args.briefing).stdout.split()
        if not added:
            print(f"REFUSED: {args.briefing} is not on {args.ref}")
            return 2
        start = added[-1]
    if not start:
        print("REFUSED: give --briefing or --since")
        return 2
    if git(root, "rev-parse", "--verify", "--quiet", f"{start}^{{commit}}").returncode:
        print(f"REFUSED: the start {start} is not a commit here")
        return 2

    listing = ok_or_refuse(git(root, "ls-tree", "-r", "--name-only", args.ref), f"reading {args.ref}'s tree")
    if listing is None:
        return 2
    tree = set(listing.splitlines())
    args.files = [p.replace("\\", "/") for p in args.files]
    files = [p for p in args.files if p in tree]
    for p in args.files:
        if p not in tree:
            print(f"NOT IN TREE: {p} (left out)")
    if not files and not args.title:
        print("REFUSED: no file resolved and no title given; a clean answer would claim a check that saw nothing")
        return 2

    rng = f"{start}..{args.ref}"
    named: dict[str, str] = {}
    if files:
        out = ok_or_refuse(git(root, "log", "--first-parent", "--format=%h %s", rng, "--", *files), "the files lens")
        if out is None:
            return 2
        for line in out.splitlines():
            sha, _, subject = line.partition(" ")
            named[sha] = f"BY FILES: {sha} {subject}"
    if args.title:
        want = words(args.title)
        out = ok_or_refuse(git(root, "log", "--first-parent", "--format=%h %s", rng), "the words lens")
        if out is None:
            return 2
        for line in out.splitlines():
            sha, _, subject = line.partition(" ")
            shared = want & words(subject)
            if len(shared) >= args.min_shared and sha not in named:
                named[sha] = f"BY WORDS: {sha} {subject} (shares: {', '.join(sorted(shared))})"

    print(f"done-on-main: {rng}, {len(files)} file(s), title words: {', '.join(sorted(words(args.title))) or 'none'}")
    for line in named.values():
        print(line)
    if not named:
        print("done-on-main: nothing on the main line since the start touched these files or shares these words")
        return 0
    print(f"done-on-main: {len(named)} commit(s) named; read each before the prompt is written")
    return 1


if __name__ == "__main__":
    sys.exit(main())
