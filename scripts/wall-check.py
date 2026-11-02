#!/usr/bin/env python3
"""wall-check: the publish gate.

Scans every tracked file in the repository for (1) a list of words that must not
appear, kept OUTSIDE the repository so the check itself leaks nothing, and (2) a
built-in set of generic secret and identifier shapes. Exit 0 at zero hits, 1 at
any hit, 2 when it could not run. Standard library only.

    python scripts/wall-check.py --list ~/wall-list.txt
    python scripts/wall-check.py --list a.txt --list b.txt --allow "Jane Doe" --include-untracked
    python scripts/wall-check.py --list ~/wall-list.txt --staged             # what the next commit adds
    python scripts/wall-check.py --list ~/wall-list.txt --text-file body.md  # a pull request body before it is posted
    python scripts/wall-check.py --list ~/wall-list.txt --commit-msg .git/COMMIT_EDITMSG

The last three are the gate at the moment of action: hooks/pre-commit runs --staged, and
hooks/commit-msg runs --commit-msg when a list is configured (git config wallcheck.list <path>).
A pull request title and body, a release note and an issue comment are published too, and no
git hook sees them: write the text to a file and run --text-file on it before it is posted.

The list file: one term per line; blank lines and lines starting with # are
ignored. Matching is case-insensitive, whole word at the front, and a space in a
term matches a space, a hyphen or an underscore, so one line "acme corp" catches
"Acme Corp", "acme-corp" and "acme_corp-staging". A line that starts with "=" is
matched literally instead, as a whole word on both sides with no space, hyphen or
underscore equivalence: "=order_events" catches a table name without also
catching the phrase "order events" in prose. An --allow phrase is a verbatim
exception: a hit that lies entirely inside an allowed phrase is not a hit (the
author's own byline, for instance). A placeholder list is in
scripts/wall-list.example.txt.

The built-in shapes are conservative on purpose; a false positive costs a
minute, a leaked key costs a rotation. "home path" catches an absolute path
under a named user's home folder on Windows, macOS or Linux (C:\\Users\\<name>,
/Users/<name>, /home/<name>); a path written with ~ names no user and passes.
"""
from __future__ import annotations

import argparse
import fnmatch
import os
import re
import subprocess
import sys

BUILT_IN = {
    "email address": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "uuid": re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I),
    "api key shape": re.compile(r"\b(sk-[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|xox[abprs]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,}|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,})"),
    "long hex token": re.compile(r"\b[0-9a-f]{40,}\b", re.I),
    "slack id": re.compile(r"\b[UCTWDG](?=[A-Z0-9]*[0-9])[A-Z0-9]{8,11}\b"),
    "home path": re.compile(r"(?i)\b[A-Z]:[\\/]+(Users|Documents and Settings)[\\/]+[^\\/\s\"'`<>]+|(?<![A-Za-z0-9.])/(home|Users)/[A-Za-z0-9._-]+"),
    "supabase project host": re.compile(r"\b[a-z]{20}\.supabase\.(co|in)\b"),
    "railway host": re.compile(r"\b[a-z0-9-]+\.up\.railway\.app\b"),
    "env assignment with a value": re.compile(r"^\s*[A-Z][A-Z0-9_]{2,}\s*=\s*['\"]?[A-Za-z0-9+/_=.-]{12,}['\"]?\s*$", re.M),
}

# Files that are binary or generated are skipped by extension; everything else tracked is read as text.
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".gz", ".woff", ".woff2", ".ttf", ".otf", ".mp4", ".mov", ".pyc"}


def term_pattern(term: str) -> re.Pattern:
    if term.startswith("="):
        return re.compile(r"(?<![A-Za-z0-9_])" + re.escape(term[1:].strip()) + r"(?![A-Za-z0-9_])", re.I)
    parts = [re.escape(p) for p in re.split(r"\s+", term.strip()) if p]
    body = r"[\s_-]+".join(parts)
    return re.compile(r"(?<![A-Za-z0-9])" + body, re.I)


def load_terms(paths: list[str]) -> list[tuple[str, re.Pattern]]:
    terms: list[tuple[str, re.Pattern]] = []
    for path in paths:
        try:
            with open(os.path.expanduser(path), encoding="utf-8") as fh:
                for raw in fh:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    terms.append((line, term_pattern(line)))
        except OSError as exc:
            print(f"wall-check: cannot read list {path}: {exc}", file=sys.stderr)
            sys.exit(2)
    return terms


def tracked_files(root: str, include_untracked: bool) -> list[str]:
    args = ["git", "-C", root, "ls-files", "-z"]
    if include_untracked:
        args += ["--cached", "--others", "--exclude-standard"]
    try:
        out = subprocess.run(args, check=True, capture_output=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"wall-check: git ls-files failed: {exc}", file=sys.stderr)
        sys.exit(2)
    files = [f.decode("utf-8", "replace") for f in out.split(b"\0") if f]
    return [f for f in files if os.path.splitext(f)[1].lower() not in SKIP_EXT]


def rel_or_none(path: str, root: str) -> str | None:
    """The path relative to the root, or None when it cannot be one of the root's files (another drive)."""
    try:
        return os.path.relpath(path, root).replace("\\", "/")
    except ValueError:
        return None


def git_or_exit(root: str, *args: str) -> bytes:
    try:
        return subprocess.run(["git", "-C", root, *args], check=True, capture_output=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = exc.stderr.decode("utf-8", "replace").strip() if isinstance(exc, subprocess.CalledProcessError) else exc
        print(f"wall-check: git {' '.join(args[:2])} failed: {detail}", file=sys.stderr)
        sys.exit(2)


def read_text_or_exit(path: str) -> str:
    try:
        with open(os.path.expanduser(path), encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError as exc:
        print(f"wall-check: cannot read {path}: {exc}", file=sys.stderr)
        sys.exit(2)


# git writes these itself; the object id in them is not a secret, so it is masked before the shapes run.
GIT_SHA_LINE_RE = re.compile(r"\b(This reverts commit|cherry picked from commit)\s+[0-9a-f]{7,64}\b")


def commit_message(text: str) -> str:
    """The message as it may be published: everything above git's --verbose scissors line. Lines that start
    with '#' are KEPT: git keeps them for a message given with -m or -F, so dropping them would let a published
    line through unread. The object id in git's own revert and cherry-pick lines is masked."""
    kept = []
    for line in text.splitlines():
        if line.startswith("# ------------------------ >8 ------------------------"):
            break
        kept.append(GIT_SHA_LINE_RE.sub(lambda m: m.group(1) + " <sha>", line))
    return "\n".join(kept)


def staged_texts(root: str, rels: list[str]):
    """(rel, text) for each staged path, read in ONE git process (cat-file --batch) rather than one per file."""
    batch = [r for r in rels if "\n" not in r]
    for rel in rels:
        if "\n" in rel:
            yield rel, git_or_exit(root, "show", f":{rel}").decode("utf-8", "replace")
    if not batch:
        return
    try:
        out = subprocess.run(["git", "-C", root, "cat-file", "--batch"], check=True, capture_output=True,
                             input=b"".join(b":" + r.encode("utf-8") + b"\n" for r in batch)).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"wall-check: git cat-file --batch failed: {exc}", file=sys.stderr)
        sys.exit(2)
    pos = 0
    for rel in batch:
        nl = out.find(b"\n", pos)
        header = out[pos:nl].split(b" ") if nl >= 0 else []
        if len(header) != 3 or not header[2].isdigit():
            print(f"wall-check: could not read the staged copy of {rel}: {out[pos:nl if nl >= 0 else None][:120]!r}", file=sys.stderr)
            sys.exit(2)
        size = int(header[2])
        start = nl + 1
        yield rel, out[start:start + size].decode("utf-8", "replace")
        pos = start + size + 1


def sources(args: argparse.Namespace, root: str):
    """(label, text) for every text this run scans: given files, the staged files, or the tracked tree."""
    if args.text_file or args.commit_msg:
        for path in args.text_file:
            yield path, read_text_or_exit(path)
        if args.commit_msg:
            yield "commit message", commit_message(read_text_or_exit(args.commit_msg))
        return
    if args.staged:
        names = git_or_exit(root, "diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR").split(b"\0")
        rels = [raw.decode("utf-8", "replace") for raw in names]
        yield from staged_texts(root, [r for r in rels if r and os.path.splitext(r)[1].lower() not in SKIP_EXT
                                       and not skipped(r, args.skip)])
        return
    for rel in tracked_files(root, args.include_untracked):
        if skipped(rel, args.skip):
            continue
        try:
            with open(os.path.join(root, rel), encoding="utf-8", errors="replace") as fh:
                yield rel, fh.read()
        except OSError:
            continue


def skipped(rel: str, globs: list[str]) -> bool:
    """A path the operator chose to leave out (a lockfile full of checksums), by a glob on its repository path."""
    return any(fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(os.path.basename(rel), g) for g in globs)


def inside_allowed(line: str, start: int, end: int, allowed: list[str]) -> bool:
    low = line.lower()
    for phrase in allowed:
        p = phrase.lower()
        i = low.find(p)
        while i != -1:
            if i <= start and end <= i + len(p):
                return True
            i = low.find(p, i + 1)
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Scan the tracked tree for words and shapes that must not be published.")
    ap.add_argument("--list", action="append", default=[], help="a list file (one term per line); repeatable")
    ap.add_argument("--allow", action="append", default=[], help="a verbatim phrase inside which hits are ignored; repeatable")
    ap.add_argument("--root", default=None, help="the repository root (default: the parent of this script's folder)")
    ap.add_argument("--include-untracked", action="store_true", help="also scan untracked, non-ignored files")
    ap.add_argument("--no-built-in", action="store_true", help="skip the built-in secret shapes")
    ap.add_argument("--skip", action="append", default=[], help="leave out paths matching this glob (a lockfile full of checksums); repeatable")
    ap.add_argument("--self", action="store_true", help="also scan this script and the list files (off by default: they name the shapes they look for)")
    ap.add_argument("--staged", action="store_true", help="scan what the next commit adds: the staged version of every added, copied, modified or renamed file (the pre-commit hook's mode)")
    ap.add_argument("--text-file", action="append", default=[], help="scan this file's text instead of the tree (a pull request body, a release note); repeatable")
    ap.add_argument("--commit-msg", default=None, help="scan a commit message file instead of the tree, git's comment lines and its --verbose diff left out (the commit-msg hook's mode)")
    args = ap.parse_args()

    root = args.root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    terms = load_terms(args.list)
    if not terms and args.no_built_in:
        print("wall-check: nothing to check (no --list and --no-built-in)", file=sys.stderr)
        return 2

    this_file = rel_or_none(os.path.abspath(__file__), root)
    list_files = {rel_or_none(os.path.abspath(os.path.expanduser(p)), root) for p in args.list} - {None}
    hits = 0
    scanned = 0
    for rel, text in sources(args, root):
        if not args.self and (rel == this_file or rel in list_files):
            continue
        scanned += 1
        for lineno, line in enumerate(text.splitlines(), 1):
            for term, pat in terms:
                for m in pat.finditer(line):
                    if inside_allowed(line, m.start(), m.end(), args.allow):
                        continue
                    hits += 1
                    print(f"{rel}:{lineno}: term '{term}': {line.strip()[:160]}")
            if not args.no_built_in:
                for name, pat in BUILT_IN.items():
                    for m in pat.finditer(line):
                        if inside_allowed(line, m.start(), m.end(), args.allow):
                            continue
                        hits += 1
                        print(f"{rel}:{lineno}: {name}: {line.strip()[:160]}")
    print(f"wall-check: {scanned} files scanned, {len(terms)} terms, {0 if args.no_built_in else len(BUILT_IN)} built-in shapes, {hits} hits")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
