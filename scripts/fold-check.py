#!/usr/bin/env python3
"""fold-check: does any session owe the chair a fold, a nudge or a stop? READ-ONLY.

The ten-minute fold law (chapter 7) says a landed session is folded within ten
minutes of its close-out card. Notifications and the hourly tick both arrive
BETWEEN the chair's turns, so a chair that spends forty minutes inside one turn
answering the operator is blind for forty minutes. This check is what the chair
runs before it takes each new ask in a long turn, as the first step of the tick,
and at the top of any turn a notification opened. It starts nothing, stops
nothing and writes nothing.

    python scripts/fold-check.py                        # from the repository's main checkout
    python scripts/fold-check.py --sessions live.json   # also compare with the tool's own session list
    python scripts/fold-check.py --json                 # the same findings as JSON

Options:
    --root <dir>          the repository (default: the current directory)
    --queue <path>        the queue file, relative to the root (default docs/orchestration/prompts/QUEUE.md)
    --briefings <path>    the briefings folder, relative to the root (default docs/orchestration/briefings)
    --ref <ref>           where landed briefings are looked for (default origin/main; run `git fetch` first)
    --sessions <file>     the tool's live session list as JSON, normalized to a list of objects with a
                          name (or id) and a state; "-" reads stdin. Keys read: name|title|displayName,
                          id|sessionId|session_id, state|status.
    --exit-code           exit 1 when anything is named (for a script's gate); default is always 0

What it names, one line each:
    FOLD OWED        the session's briefing file is on the ref and its row still holds a slot
    ROW STALE        a landed row already names the session and the running table still shows it
    STILL RESIDENT   the session is folded (a landed row) and the tool still lists it as live: stop it by id
    ENDED, NO CARD   the tool says the session ended (completed, failed, stopped, idle) with no briefing
                     on the ref: read its last output; fold only from a briefing
    NEEDS INPUT      the tool says it is waiting on a question or a permission: answer it the same minute
    GONE             the running table shows it and the tool no longer lists it at all
    UNTRACKED        the tool lists a live session the running table does not show

A row whose session cell reads "(free...)" is a free slot and is skipped. An interim
briefing (a file name ending in "-interim") is never a landing.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

ENDED = {"completed", "complete", "done", "failed", "error", "stopped", "idle", "exited"}
WAITING = {"needs input", "needs_input", "waiting", "blocked", "asking"}


def git(root: str, *args: str) -> str:
    out = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, encoding="utf-8")
    if out.returncode:
        raise RuntimeError(out.stderr.strip() or f"git {' '.join(args)} failed")
    return out.stdout


def tables(markdown: str) -> dict[str, list[dict[str, str]]]:
    """Every pipe table under a '## ' heading, keyed by the heading's first word, lower case."""
    found: dict[str, list[dict[str, str]]] = {}
    heading = ""
    header: list[str] | None = None
    for line in markdown.splitlines():
        if line.startswith("## "):
            heading = line[3:].split(":")[0].split()[0].lower() if line[3:].strip() else ""
            header = None
            continue
        if not line.lstrip().startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        found.setdefault(heading, []).append(dict(zip(header, cells)))
    return found


def session_of(cell: str) -> tuple[str, str] | None:
    cell = cell.strip()
    if not cell or cell.startswith("("):
        return None
    parts = cell.split()
    return parts[0], (parts[1] if len(parts) > 1 else "")


def landed_briefing(names: list[str], name: str) -> str | None:
    pat = re.compile(r"(^|-)" + re.escape(name.lower()) + r"$")
    for path in names:
        stem = os.path.splitext(os.path.basename(path))[0].lower()
        if stem.endswith("-interim"):
            continue
        if pat.search(stem):
            return path
    return None


def load_sessions(path: str) -> list[dict[str, str]]:
    raw = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    data = json.loads(raw)
    if isinstance(data, dict):
        data = data.get("sessions") or data.get("agents") or []
    rows = []
    for item in data:
        name = str(item.get("name") or item.get("title") or item.get("displayName") or "")
        sid = str(item.get("id") or item.get("sessionId") or item.get("session_id") or "")
        state = str(item.get("state") or item.get("status") or "").strip().lower()
        rows.append({"name": name, "id": sid, "state": state})
    return rows


def match_live(live: list[dict[str, str]], name: str, short_id: str) -> dict[str, str] | None:
    for s in live:
        if s["name"] and s["name"].lower() == name.lower():
            return s
        if short_id and s["id"].lower().startswith(short_id.lower()):
            return s
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Name every session that owes the chair a fold, a nudge or a stop. Read-only.")
    ap.add_argument("--root", default=".")
    ap.add_argument("--queue", default="docs/orchestration/prompts/QUEUE.md")
    ap.add_argument("--briefings", default="docs/orchestration/briefings")
    ap.add_argument("--ref", default="origin/main")
    ap.add_argument("--sessions", default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--exit-code", action="store_true")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    try:
        queue_text = open(os.path.join(root, args.queue), encoding="utf-8").read()
    except OSError as exc:
        print(f"fold-check: read failed: the queue file {args.queue}: {exc}")
        return 2
    t = tables(queue_text)
    running = [(r, session_of(r.get("session", ""))) for r in t.get("running", [])]
    running = [(r, s) for r, s in running if s]
    landed_names = {session_of(r.get("session", ""))[0].lower() for r in t.get("landed", []) if session_of(r.get("session", ""))}

    notes: list[str] = []
    try:
        listing = git(root, "ls-tree", "-r", "--name-only", args.ref, "--", args.briefings.rstrip("/") + "/").splitlines()
    except RuntimeError as exc:
        listing = []
        notes.append(f"read failed: briefings on {args.ref}: {exc}")

    live: list[dict[str, str]] | None = None
    if args.sessions:
        try:
            live = load_sessions(args.sessions)
        except (OSError, ValueError) as exc:
            notes.append(f"read failed: the session list {args.sessions}: {exc}")

    findings: list[dict[str, str]] = []

    def name(kind: str, session: str, text: str) -> None:
        findings.append({"kind": kind, "session": session, "text": text})

    seen_live: set[str] = set()
    for row, (sname, sid) in running:
        slot = row.get("slot", "?")
        brief = landed_briefing(listing, sname)
        state_row = match_live(live, sname, sid) if live is not None else None
        if state_row:
            seen_live.add(state_row["id"] or state_row["name"])
        if sname.lower() in landed_names:
            name("ROW STALE", sname, f"a landed row already names {sname} and slot {slot} still shows it: free the slot")
            continue
        if brief:
            name("FOLD OWED", sname, f"{sname} landed ({brief} on {args.ref}) and still holds slot {slot}: fold it from the file, then stop it by id")
            continue
        if live is None:
            continue
        if state_row is None:
            name("GONE", sname, f"the running table shows {sname} in slot {slot} and the tool no longer lists it: read its last output; fold only from a briefing")
        elif state_row["state"] in WAITING:
            name("NEEDS INPUT", sname, f"{sname} (slot {slot}) is waiting ({state_row['state']}): answer it the same minute, or tell it to record the question in section 7 and carry on")
        elif state_row["state"] in ENDED:
            name("ENDED, NO CARD", sname, f"{sname} (slot {slot}) reads {state_row['state']} with no briefing on {args.ref}: read its last output, then nudge or resume it")

    if live is not None:
        running_names = {s[0].lower() for _, s in running}
        for s in live:
            key = s["id"] or s["name"]
            if key in seen_live:
                continue
            label = s["name"] or s["id"]
            if s["name"].lower() in landed_names and s["state"] not in ENDED:
                name("STILL RESIDENT", label, f"{label} is folded and the tool still lists it as {s['state'] or 'live'}: stop it by id")
            elif s["name"].lower() not in running_names and s["state"] not in ENDED:
                name("UNTRACKED", label, f"the tool lists {label} ({s['state'] or 'live'}) and the running table does not: record it or stop it")

    if args.json:
        print(json.dumps({"running": len(running), "findings": findings, "notes": notes}, indent=2))
    else:
        for n in notes:
            print(f"fold-check: {n}")
        for f in findings:
            print(f"{f['kind']}: {f['text']}")
        if not findings:
            print(f"fold-check: all clear: {len(running)} session(s) in the running table, none owes the chair anything")
    return 1 if (findings and args.exit_code) else 0


if __name__ == "__main__":
    sys.exit(main())
