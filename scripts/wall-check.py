#!/usr/bin/env python3
"""wall-check: the publish gate.

Scans every tracked file in the repository for (1) a list of words that must not
appear, kept OUTSIDE the repository so the check itself leaks nothing, and (2) a
built-in set of generic secret and identifier shapes. Exit 0 at zero hits, 1 at
any hit, 2 when it could not run. Standard library only.

    python scripts/wall-check.py --list ~/wall-list.txt
    python scripts/wall-check.py --list a.txt --list b.txt --allow "Jane Doe" --include-untracked

The list file: one term per line; blank lines and lines starting with # are
ignored. Matching is case-insensitive, whole word at the front, and a space in a
term matches a space, a hyphen or an underscore, so one line "acme corp" catches
"Acme Corp", "acme-corp" and "acme_corp-staging". An --allow phrase is a
verbatim exception: a hit that lies entirely inside an allowed phrase is not a
hit (the author's own byline, for instance). A placeholder list is in
scripts/wall-list.example.txt.

The built-in shapes are conservative on purpose; a false positive costs a
minute, a leaked key costs a rotation.
"""
from __future__ import annotations

import argparse
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
    "private user path": re.compile(r"(?i)\b[A-Z]:[\\/]+Users[\\/]+[^\\/\s\"'`]+|/home/[a-z0-9_-]+/|/Users/[A-Za-z0-9_-]+/"),
    "supabase project host": re.compile(r"\b[a-z]{20}\.supabase\.(co|in)\b"),
    "railway host": re.compile(r"\b[a-z0-9-]+\.up\.railway\.app\b"),
    "env assignment with a value": re.compile(r"^\s*[A-Z][A-Z0-9_]{2,}\s*=\s*['\"]?[A-Za-z0-9+/_=.-]{12,}['\"]?\s*$", re.M),
}

# Files that are binary or generated are skipped by extension; everything else tracked is read as text.
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".gz", ".woff", ".woff2", ".ttf", ".otf", ".mp4", ".mov", ".pyc"}


def term_pattern(term: str) -> re.Pattern:
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
    ap.add_argument("--self", action="store_true", help="also scan this script and the list files (off by default: they name the shapes they look for)")
    args = ap.parse_args()

    root = args.root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    terms = load_terms(args.list)
    if not terms and args.no_built_in:
        print("wall-check: nothing to check (no --list and --no-built-in)", file=sys.stderr)
        return 2

    this_file = os.path.relpath(os.path.abspath(__file__), root).replace("\\", "/")
    list_files = {os.path.relpath(os.path.abspath(os.path.expanduser(p)), root).replace("\\", "/") for p in args.list}
    hits = 0
    scanned = 0
    for rel in tracked_files(root, args.include_untracked):
        if not args.self and (rel == this_file or rel in list_files):
            continue
        path = os.path.join(root, rel)
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
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
