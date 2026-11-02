#!/usr/bin/env python3
"""prompt-check: is a dispatch prompt ready to launch? READ-ONLY.

Chapter 4 lists what makes a prompt incomplete. Written as prose, that list was
applied by memory, and memory missed: sessions that knew when to stop but not
what finished meant, so they ran to the clock; a session that ran hours past
its stop because nothing read the stop; a session launched on a read-first file
that had moved. This check reads the prompt the way the launch does (only the
body below its `---` line reaches the session) and refuses what would launch
broken. It starts nothing, changes nothing and makes no network call.

    python scripts/prompt-check.py docs/orchestration/prompts/2026-01-15-search-s2-prompt.md
    python scripts/prompt-check.py docs/orchestration/prompts/*.md --root . --ref origin/main
    python scripts/prompt-check.py <prompt> --json

Options:
    --root <dir>     the repository the read-first paths are checked in (default: the current directory)
    --ref <ref>      where repository paths are looked for first (default origin/main; the disk is the fallback)
    --no-paths       skip the read-first paths
    --json           the findings as JSON

What it checks, in the BODY (everything below the first line that is exactly `---`, after any
front matter; outside fenced code blocks, so a quoted example never counts):

    DONE MEANS   a line starting `DONE MEANS:` (capitals; a list marker, heading marks or bold before it
                 are fine) naming the observable state that ends the work: "the PR merged and its deploy
                 read back", "the page read back by its bytes". With nothing after the colon, the list
                 items straight below it are its words. REFUSED when it is missing (and said plainly when
                 the head has one, because the head never reaches the session), when it is only an unfilled
                 <placeholder>, and when nothing is left once the numbers, clocks, time words and glue words
                 are taken out: a duration is not a finish condition. A time beside a state passes.
    HARD STOP    a timed outer bound: "HARD STOP: 160 minutes after launch", "HARD STOP two hours after
                 launch", "HARD STOP at 17:30" (a 24-hour clock), or both ("whichever is first"; both are
                 kept). REFUSED when missing, when no time can be read from it, or when its clock carries am,
                 pm or a zone (read wrong, a stop is worse than no stop).
    EXPECTED     optional: "EXPECTED: 120 minutes". Reported when present; the queue's Expected column
                 and fold-check.py use it to name a session that is over its time while inside its stop.
    NO ASKING    REFUSED when the body tells the session to ask ("ask the operator", "ask if unclear"):
                 nobody is at a background session's keyboard, so the prompt commits to one path.

And in the whole file: every backticked path on a line starting "Read first" exists, in the
repository at --ref or on disk. A URL is not fetched (named as not checked); a <placeholder> is skipped.

Exit 0 every prompt is ready; 1 at least one refusal; 2 a prompt could not be read.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "fifteen": 15, "twenty": 20, "thirty": 30, "forty": 40,
    "forty-five": 45, "fifty": 50, "sixty": 60, "seventy-five": 75, "ninety": 90, "a": 1, "an": 1,
}
TIME_WORDS = {"second", "seconds", "minute", "minutes", "min", "mins", "m", "hour", "hours", "h", "hr", "hrs",
              "day", "days", "week", "weeks", "half", "quarter", "and"} | set(NUMBER_WORDS)
GLUE = {"the", "in", "within", "after", "by", "at", "of", "about", "under", "over", "for", "before", "until",
        "launch", "launched", "start", "started", "starting", "hard", "stop", "expected", "time", "session",
        "runs", "run", "running", "when", "is", "are", "has", "have", "been", "it", "done", "finished",
        "elapsed", "passed", "up", "or", "whichever", "first", "later", "earlier", "most", "least", "no"}
DONE_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+|#+\s+)?(?:\*\*|__)?DONE MEANS(?:\*\*|__)?\s*:(?:\*\*|__)?(.*)$")
LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$")
HARD_RE = re.compile(r"HARD STOP", re.I)
# The half sits before the unit ("two and a half hours") or after it ("an hour and a half"); both read.
SPAN_RE = re.compile(r"(\d+(?:\.\d+)?|[a-z]+(?:-[a-z]+)?(?: and a half)?)\s*(minutes?|mins?|hours?|hrs?|h|m)\b(\s+and\s+a\s+half)?\s+after\s+(?:the\s+)?launch", re.I)
# am, pm, UTC and GMT in any case; a zone abbreviation (EST, CEST) only in capitals, so "17:30 that day" stays a clock.
CLOCK_RE = re.compile(r"(?<![\d:])([01]?\d|2[0-3]):([0-5]\d)(?![\d:])(\s*(?:(?i:a\.?m\.?|p\.?m\.?|utc|gmt)|[A-Z]{1,3}T)(?![A-Za-z]))?")
EXPECTED_RE = re.compile(r"\bEXPECTED\s*:?\s*(\d+(?:\.\d+)?|[a-z]+(?:-[a-z]+)?(?: and a half)?)\s*(minutes?|mins?|hours?|hrs?|h|m)\b(\s+and\s+a\s+half)?", re.I)
ASK_RES = [
    re.compile(r"\bask\b[^.;\n]{0,40}?\b(?:if|when|whether)\b[^.;\n]{0,24}?\b(?:unclear|unsure|in doubt|ambiguous|needed|necessary)\b", re.I),
    re.compile(r"\b(?:ask|check with|confirm with)\s+(?:the\s+)?(?:operator|me|user|human|owner)\b", re.I),
]
# A negation counts only when it governs the ask itself ("never ask", "do not stop to ask"). "If you are not
# sure, ask the operator" and "do not hesitate to ask the operator" are asks, and are refused.
NEGATION_RE = re.compile(r"\b(?:never|not|don't|do not|no need to|nor)\s+(?:(?:stop|pause|wait|need|have)\s+(?:to\s+)?)?$", re.I)
PATH_TOKEN_RE = re.compile(r"`([^`\s<>]+)`")


def split_body(text: str) -> tuple[list[str], list[str]] | None:
    """(head lines, body lines): the body starts after the first line that is exactly '---' (front matter skipped)."""
    lines = text.splitlines()
    start = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                start = i + 1
                break
    fence = None
    for i in range(start, len(lines)):
        s = lines[i].strip()
        if s.startswith("```") or s.startswith("~~~"):
            mark = s[:3]
            fence = None if fence == mark else (fence or mark)
            continue
        if fence is None and s == "---":
            return lines[:i], lines[i + 1:]
    return None


def unfenced(lines: list[str]) -> list[tuple[int, str, bool]]:
    """Each line with its index and whether it sits inside a fenced code block."""
    out, fence = [], None
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("```") or s.startswith("~~~"):
            mark = s[:3]
            out.append((i, line, True))
            fence = None if fence == mark else (fence or mark)
            continue
        out.append((i, line, fence is not None))
    return out


def words_left(text: str) -> list[str]:
    text = re.sub(r"\*\*|__|`", " ", text)
    text = CLOCK_RE.sub(" ", text)
    tokens = re.findall(r"[A-Za-z][A-Za-z'-]*|\d+(?:\.\d+)?", text.lower())
    return [t for t in tokens if not re.fullmatch(r"\d+(?:\.\d+)?", t) and t not in TIME_WORDS and t not in GLUE]


def read_done_line(head: list[str], body: list[str]) -> tuple[bool, str]:
    rows = unfenced(body)
    fenced_only = False
    for k, (i, line, inside) in enumerate(rows):
        m = DONE_RE.match(line)
        if not m:
            continue
        if inside:
            fenced_only = True
            continue
        words = m.group(1).strip().strip("*_ ").strip()
        if not words:
            items = []
            for _, nxt, nxt_inside in rows[k + 1:]:
                lm = LIST_ITEM_RE.match(nxt)
                if nxt_inside or not lm:
                    break
                items.append(lm.group(1).strip())
            words = "; ".join(items)
        if not words:
            return False, "the DONE MEANS line names nothing"
        if re.fullmatch(r"<[^>]*>[.;]?", words):
            return False, f"the DONE MEANS line is an unfilled placeholder: {words}"
        if not words_left(words):
            return False, f"the DONE MEANS line is only a time (a duration is not a finish condition): {words}"
        return True, words
    if fenced_only:
        return False, "the only DONE MEANS line is inside a fenced block (a quoted example is not the line)"
    if any(DONE_RE.match(line) for line in head):
        return False, "DONE MEANS is in the head only; the launch sends the body below the --- line, so the session never reads it"
    return False, "no DONE MEANS line in the body: name the observable state that ends the work"


def to_minutes(amount: str, unit: str, half_after: str | None = None) -> float | None:
    amount = amount.lower().strip()
    half = bool(half_after)
    if amount.endswith(" and a half"):
        half = True
        amount = amount[: -len(" and a half")]
    if re.fullmatch(r"\d+(?:\.\d+)?", amount):
        n = float(amount)
    elif amount in NUMBER_WORDS:
        n = float(NUMBER_WORDS[amount])
    else:
        return None
    if half:
        n += 0.5
    return n * 60 if unit.lower().startswith("h") else n


def hard_stop(body: list[str]) -> tuple[bool, str, dict]:
    """The HARD STOP line, read. Lines with HARD STOP in capitals are tried first (prose such as "before the hard
    stop" is not the line); the first that reads wins, and a clock with am, pm or a zone anywhere is refused."""
    lines = [line for _, line, inside in unfenced(body) if not inside and HARD_RE.search(line)]
    if not lines:
        return False, "no HARD STOP in the body: name the outer bound (\"HARD STOP: 120 minutes after launch\")", {}
    capitals = [line for line in lines if "HARD STOP" in line]
    tried = [stop_line(line) for line in (capitals or lines)]
    for ok, text, found in tried:
        if not ok and "am, pm or a zone" in text:
            return ok, text, found
    for result in tried:
        if result[0]:
            return result
    return tried[0]


def stop_line(line: str) -> tuple[bool, str, dict]:
    m = HARD_RE.search(line)
    if m:
        rest = line[m.end():]
        cut = re.search(r"[.;](\s|$)", rest)
        clause = rest[: cut.start()] if cut else rest
        found: dict = {}
        span = SPAN_RE.search(clause)
        if span:
            minutes = to_minutes(span.group(1), span.group(2), span.group(3))
            if minutes is None:
                return False, f"a HARD STOP whose length cannot be read: {line.strip()}", {}
            found["minutes_after_launch"] = minutes
        for c in CLOCK_RE.finditer(clause):
            if span and span.start() <= c.start() < span.end():
                continue
            if c.group(3):
                return False, f"a HARD STOP clock with am, pm or a zone is refused (a stop read wrong is worse than none): {line.strip()}", {}
            found["clock"] = f"{int(c.group(1)):02d}:{c.group(2)}"
            break
        if not found:
            return False, f"a HARD STOP with no time that can be read: {line.strip()}", {}
        parts = []
        if "minutes_after_launch" in found:
            parts.append(f"{found['minutes_after_launch']:g} minutes after launch")
        if "clock" in found:
            parts.append(f"at {found['clock']}")
        return True, " or ".join(parts) + (" (whichever is first)" if len(parts) > 1 else ""), found
    return False, f"a HARD STOP with no time that can be read: {line.strip()}", {}


def expected(body: list[str]) -> float | None:
    for _, line, inside in unfenced(body):
        if inside:
            continue
        m = EXPECTED_RE.search(line)
        if m:
            return to_minutes(m.group(1), m.group(2), m.group(3))
    return None


def asks(body: list[str]) -> list[str]:
    """Lines that tell the session to ask somebody; a negated ask ("never ask the operator") is not one."""
    hits = []
    for _, line, inside in unfenced(body):
        if inside:
            continue
        if any(not NEGATION_RE.search(line[: m.start()]) for rx in ASK_RES for m in rx.finditer(line)):
            hits.append(line.strip())
    return hits


def read_first_paths(lines: list[str]) -> list[str]:
    paths = []
    for line in lines:
        if re.match(r"^\s*(?:[-*+]\s+)?(?:\*\*)?read first", line, re.I):
            for tok in PATH_TOKEN_RE.findall(line):
                if "/" in tok or re.search(r"\.[A-Za-z0-9]{1,5}$", tok):
                    paths.append(tok.rstrip(".,;:"))
    return paths


def path_state(root: str, ref: str, path: str) -> str:
    if re.match(r"^[a-z]+://", path):
        return "not checked (a URL; no network call is made)"
    disk = os.path.expanduser(path)
    if os.path.isabs(disk) or path.startswith("~"):
        return "ok" if os.path.exists(disk) else "missing"
    rel = path.replace("\\", "/")
    if rel.startswith("./"):
        rel = rel[2:]
    on_ref = subprocess.run(["git", "-C", root, "cat-file", "-e", f"{ref}:{rel}"], capture_output=True)
    if on_ref.returncode == 0:
        return "ok"
    return "ok (on disk, not on the ref)" if os.path.exists(os.path.join(root, rel)) else "missing"


def check(path: str, root: str, ref: str, paths: bool) -> dict:
    result = {"prompt": path, "ok": [], "refused": [], "notes": []}
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as exc:
        result["error"] = f"read failed: {exc}"
        return result
    split = split_body(text)
    if split is None:
        result["refused"].append("no line that is exactly --- outside a fence: the launch sends the body below it, and there is none")
        return result
    head, body = split
    ok, words = read_done_line(head, body)
    (result["ok"] if ok else result["refused"]).append(f"DONE MEANS: {words}" if ok else words)
    ok, text_stop, stop = hard_stop(body)
    (result["ok"] if ok else result["refused"]).append(f"HARD STOP: {text_stop}" if ok else text_stop)
    result["hard_stop"] = stop
    exp = expected(body)
    result["expected_minutes"] = exp
    if exp is None:
        result["notes"].append("no EXPECTED line: the fold check cannot name this session OVER EXPECTED")
    else:
        result["ok"].append(f"EXPECTED: {exp:g} minutes")
        if stop.get("minutes_after_launch") is not None and exp > stop["minutes_after_launch"]:
            result["refused"].append(f"EXPECTED ({exp:g} minutes) is past the HARD STOP ({stop['minutes_after_launch']:g} minutes)")
        elif stop.get("clock") and stop.get("minutes_after_launch") is None:
            result["notes"].append("EXPECTED is in minutes and the HARD STOP is a clock: compare the two at the launch, when the clock is known")
    for line in asks(body):
        result["refused"].append(f"the body tells the session to ask; nobody is at its keyboard: {line[:160]}")
    if paths:
        for p in read_first_paths(text.splitlines()):
            state = path_state(root, ref, p)
            if state == "missing":
                result["refused"].append(f"read-first path not on {ref} and not on disk: {p}")
            elif state.startswith("not checked"):
                result["notes"].append(f"read-first {p}: {state}")
            else:
                result["ok"].append(f"read-first {p}: {state}")
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Refuse a dispatch prompt that would launch broken. Read-only.")
    ap.add_argument("prompts", nargs="+")
    ap.add_argument("--root", default=".")
    ap.add_argument("--ref", default="origin/main")
    ap.add_argument("--no-paths", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    results = [check(p, os.path.abspath(args.root), args.ref, not args.no_paths) for p in args.prompts]
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(f"prompt-check: {r['prompt']}")
            if "error" in r:
                print(f"  COULD NOT CHECK: {r['error']}")
                continue
            for line in r["ok"]:
                print(f"  OK {line}")
            for line in r["notes"]:
                print(f"  NOTE {line}")
            for line in r["refused"]:
                print(f"  REFUSED {line}")
        ready = sum(1 for r in results if "error" not in r and not r["refused"])
        print(f"prompt-check: {ready} of {len(results)} prompt(s) ready to launch")
    if any("error" in r for r in results):
        return 2
    return 1 if any(r["refused"] for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
