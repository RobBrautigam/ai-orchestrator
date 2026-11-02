#!/usr/bin/env python3
"""fold-lines: the briefing's fold block, read the way the chair's fold reads it. READ-ONLY.

A chair that composes the landed row, the board line and the owed items from an
eleven-section briefing composes them a little differently every time, and an
owed item paraphrased at the fold is an owed item half lost. So every briefing
ends with one fenced block the chair folds FROM and never writes itself:

    ```fold-lines
    RESULT: <one sentence: what changed for the operator, under 200 characters>
    BOARD: <the board's one line for this landing (no pipe character: it lands in a table)>
    EFFORT: <model, effort, wall clock, tokens, as the session's usage record reads them>
    FINDINGS: <the reviewer's count and what was done about them>
    SPEND: <the metered spend, or $0>
    OWED: <title> || <detail> || <trigger> || <now|next|later|someday> || <null|operator|operator: reason>
    CARRY: <row id> done: <section>        (or "open: <reason>", or "superseded: <row id>")
    ```

OWED is one line per owed item, five fields split on " || ": a title, the detail, the trigger that
should resurface it, a band, and who moves it: `null` (the chair or a session), `operator`, or
`operator: <reason>` where the reason is one of answer, sign_in, send, call, money, in_person (the
only things a background session cannot do for the operator). CARRY is one line per open item the
dispatch prompt handed to this session, with its verdict, so nothing carried is silently dropped.

A session runs this on its own briefing before its close-out card; a chair runs it before it folds.

    python scripts/fold-lines.py docs/orchestration/briefings/2026-01-15-payments-s4.md
    python scripts/fold-lines.py <briefing> --carry 3f9a2c1e --carry 91be07d4   # each must have a CARRY line
    python scripts/fold-lines.py <briefing> --json                              # the parsed block, for a fold script

Exit 0 the block is whole (what the fold will file is printed); 1 refused, every problem named;
2 the file could not be read. A file path in RESULT is a NOTE, not a refusal: the operator cannot
open a local path, so the line should say what changed instead.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

SINGLE = ("RESULT", "BOARD", "EFFORT", "FINDINGS", "SPEND")
BANDS = ("now", "next", "later", "someday")
REASONS = ("answer", "sign_in", "send", "call", "money", "in_person")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{2,63}$")
CARRY_RE = re.compile(r"^(\S+)\s+(done|open|superseded):\s*(.*)$")
PATHISH_RE = re.compile(r"(?:[A-Za-z]:[\\/]|(?<![\w.])/(?:[\w.-]+/)+[\w.-]+|\b[\w.-]+/[\w./-]+\.[A-Za-z0-9]{1,5}\b)")
RESULT_MAX = 200


def find_blocks(text: str) -> list[list[str]]:
    """The body lines of every fenced block whose info string is fold-lines."""
    blocks, current, fence = [], None, None
    for line in text.splitlines():
        s = line.strip()
        if fence is None:
            m = re.match(r"^(`{3,}|~{3,})\s*(\S*)", s)
            if m:
                fence = m.group(1)
                current = [] if m.group(2).lower() == "fold-lines" else None
            continue
        if s.startswith(fence[0] * len(fence)) and s.strip(fence[0]) == "":
            if current is not None:
                blocks.append(current)
            fence, current = None, None
            continue
        if current is not None:
            current.append(line)
    return blocks


def check_owed(raw: str) -> tuple[dict | None, list[str]]:
    fields = [f.strip() for f in raw.split("||")]
    if len(fields) != 5:
        return None, [f"an OWED line needs five fields split by ' || ', this one has {len(fields)}: {raw[:120]}"]
    title, detail, trigger, band, owner = fields
    problems = []
    if not title:
        problems.append(f"an OWED line with no title: {raw[:120]}")
    if not trigger:
        problems.append(f"OWED '{title}' has no trigger (what should resurface it)")
    if band.lower() not in BANDS:
        problems.append(f"OWED '{title}' band '{band}' is not one of {', '.join(BANDS)}")
    who = owner.strip()
    m = re.fullmatch(r"operator(?::\s*(\S+))?", who, re.I)
    if who.lower() == "null":
        on = None
    elif m and (m.group(1) is None or m.group(1).lower() in REASONS):
        on = "operator" + (f": {m.group(1).lower()}" if m.group(1) else "")
    else:
        on = None
        problems.append(f"OWED '{title}' fifth field '{who}' is not null, operator, or operator: <{'|'.join(REASONS)}>")
    return {"title": title, "detail": detail, "trigger": trigger, "band": band.lower(), "on": on}, problems


def parse(lines: list[str]) -> tuple[dict, list[str], list[str]]:
    out: dict = {"owed": [], "carries": {}}
    problems, notes = [], []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        key, sep, value = line.partition(":")
        key, value = key.strip().upper(), value.strip()
        if not sep or key not in SINGLE + ("OWED", "CARRY"):
            problems.append(f"a line the fold does not read: {line[:120]}")
            continue
        if key in SINGLE:
            if key.lower() in out:
                problems.append(f"{key} appears twice; the fold reads one")
            out[key.lower()] = value
        elif key == "OWED":
            item, owed_problems = check_owed(value)
            problems += owed_problems
            if item:
                out["owed"].append(item)
        else:
            m = CARRY_RE.match(value)
            if not m or not ID_RE.match(m.group(1)) or not m.group(3).strip():
                problems.append(f"a CARRY line is not '<id> done: <section>', '<id> open: <reason>' or '<id> superseded: <id>': {value[:120]}")
                continue
            if m.group(1) in out["carries"]:
                problems.append(f"CARRY {m.group(1)} appears twice")
            out["carries"][m.group(1)] = {"verdict": m.group(2), "why": m.group(3).strip()}
    for key in SINGLE:
        if not out.get(key.lower()):
            problems.append(f"{key} is missing or empty")
    result = out.get("result", "")
    if len(result) > RESULT_MAX:
        problems.append(f"RESULT is {len(result)} characters; the operator's line is at most {RESULT_MAX}")
    if result and PATHISH_RE.search(result):
        notes.append("RESULT carries a file path; the operator cannot open a local path, so say what changed instead")
    if "|" in out.get("board", ""):
        problems.append("BOARD carries a pipe character; the board line lands in a table, where a pipe splits the cell")
    return out, problems, notes


def main() -> int:
    ap = argparse.ArgumentParser(description="Read a briefing's fold-lines block the way the fold reads it. Read-only.")
    ap.add_argument("briefing")
    ap.add_argument("--carry", action="append", default=[], help="a row id the dispatch prompt carried; each needs a CARRY line")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        text = open(args.briefing, encoding="utf-8").read()
    except OSError as exc:
        print(f"fold-lines: could not read {args.briefing}: {exc}")
        return 2
    blocks = find_blocks(text)
    if not blocks:
        print(f"FOLD LINES REFUSED: {args.briefing}")
        print("  no ```fold-lines block: the fold reads the briefing's last block, and there is none")
        return 1
    parsed, problems, notes = parse(blocks[-1])
    if len(blocks) > 1:
        problems.insert(0, f"{len(blocks)} fold-lines blocks; the fold reads exactly one")
    for cid in args.carry:
        if cid not in parsed["carries"]:
            problems.append(f"the prompt carried {cid} and no CARRY line gives it a verdict")
    if args.json:
        print(json.dumps({"briefing": args.briefing, "ok": not problems, "problems": problems, "notes": notes, **parsed}, indent=2))
        return 1 if problems else 0
    if problems:
        print(f"FOLD LINES REFUSED: {args.briefing}")
        for p in problems:
            print(f"  {p}")
        for n in notes:
            print(f"  NOTE {n}")
        return 1
    print(f"FOLD LINES OK: {args.briefing}")
    print(f"  RESULT: {parsed['result']}")
    print(f"  BOARD: {parsed['board']}")
    for item in parsed["owed"]:
        who = f"on the {item['on']}" if item["on"] else "on the chair"
        print(f"  OWED ({item['band']}, {who}): {item['title']}; resurfaces when {item['trigger']}")
    for cid, c in parsed["carries"].items():
        print(f"  CARRY {cid}: {c['verdict']} ({c['why']})")
    for n in notes:
        print(f"  NOTE {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
