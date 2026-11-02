#!/usr/bin/env python3
"""mutation-pass: proves the selftest catches a broken guard, not only that the code is green.

A test never seen red is not evidence. This script breaks one guard at a time in a COPY of
scripts/ and hooks/ (a refusal switched off, a condition flipped, a read that returns nothing),
runs scripts/selftest.py against the copy with --scripts-dir, --hook and --pre-commit, and counts
the break as caught only when at least one named check FAILs. The real files are never touched;
each copy lives in its own temporary folder, deleted when its run ends.

    python scripts/mutation-pass.py              # every break, two at a time
    python scripts/mutation-pass.py --only M3 M9 # just these
    python scripts/mutation-pass.py --jobs 4     # more at once, on a machine with memory to spare

It takes several minutes: each break is one full selftest run. Exit 0 when every break was
caught; 1 when any survived (a guard the selftest does not prove); 2 when a break's anchor text
is no longer found exactly once (the code moved: update the table below, never skip the row).
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# (id, file, what the break does, the exact text, its replacement). Each text must occur exactly once.
BREAKS = [
    ("M1", "scripts/prompt-check.py", "a done-means line that is only a time passes",
     "        if not words_left(words):", "        if False and not words_left(words):"),
    ("M2", "scripts/prompt-check.py", "a hard stop in am or pm is read",
     "            if c.group(3):", "            if False and c.group(3):"),
    ("M3", "scripts/prompt-check.py", "a done-means line in the head counts",
     "    rows = unfenced(body)\n    fenced_only = False", "    rows = unfenced(head + body)\n    fenced_only = False"),
    ("M4", "scripts/prompt-check.py", "no instruction to ask is ever found",
     "        if any(not NEGATION_RE.search(line[: m.start()]) for rx in ASK_RES for m in rx.finditer(line)):", "        if False:"),
    ("M5", "scripts/prompt-check.py", "every read-first path is ok",
     "    return \"ok (on disk, not on the ref)\" if os.path.exists(os.path.join(root, rel)) else \"missing\"", "    return \"ok\""),
    ("M6", "scripts/prompt-check.py", "any negation within reach excuses an ask (the old, loose pattern)",
     "NEGATION_RE = re.compile(r\"\\b(?:never|not|don't|do not|no need to|nor)\\s+(?:(?:stop|pause|wait|need|have)\\s+(?:to\\s+)?)?$\", re.I)",
     "NEGATION_RE = re.compile(r\"\\b(?:never|not|don't|do not|no|nor|without)\\b[^.;\\n]{0,24}$\", re.I)"),
    ("M7", "scripts/prompt-check.py", "only the first line that mentions the hard stop is read",
     "    tried = [stop_line(line) for line in (capitals or lines)]", "    tried = [stop_line(line) for line in lines[:1]]"),
    ("M8", "scripts/prompt-check.py", "a half after the unit is dropped",
     "    half = bool(half_after)", "    half = False"),
    ("M9", "scripts/fold-lines.py", "any band passes",
     "    if band.lower() not in BANDS:", "    if False:"),
    ("M10", "scripts/fold-lines.py", "a pipe in the board line passes",
     "    if \"|\" in out.get(\"board\", \"\"):", "    if False:"),
    ("M11", "scripts/fold-lines.py", "a carried row with no line passes",
     "        if cid not in parsed[\"carries\"]:", "        if False:"),
    ("M12", "scripts/fold-lines.py", "a template placeholder passes",
     "        elif PLACEHOLDER_RE.search(out[key.lower()]):", "        elif False:"),
    ("M13", "scripts/fold-check.py", "the hard stop comparison is flipped",
     "        if stop is not None and now > stop:", "        if stop is not None and now < stop:"),
    ("M14", "scripts/fold-check.py", "an unreadable clock cell is not reported",
     "            if why:\n                notes.append", "            if False:\n                notes.append"),
    ("M15", "scripts/wall-check.py", "the staged copy reads as empty",
     "        yield rel, out[start:start + size].decode(\"utf-8\", \"replace\")", "        yield rel, \"\""),
    ("M16", "scripts/wall-check.py", "the batch read loses its place after the first file",
     "        pos = start + size + 1", "        pos = start + size"),
    ("M17", "scripts/wall-check.py", "a skipped path is still read",
     "                                       and not skipped(r, args.skip)])", "                                       and not False])"),
    ("M18", "scripts/wall-check.py", "a message line that starts with '#' is dropped",
     "        kept.append(GIT_SHA_LINE_RE.sub(lambda m: m.group(1) + \" <sha>\", line))",
     "        if not line.startswith(\"#\"):\n            kept.append(GIT_SHA_LINE_RE.sub(lambda m: m.group(1) + \" <sha>\", line))"),
    ("M19", "scripts/wall-check.py", "git's own revert id is not masked",
     "GIT_SHA_LINE_RE = re.compile(", "GIT_SHA_LINE_RE = re.compile(r\"(?!x)x\") or re.compile("),
    ("M20", "hooks/pre-commit", "a failed gate lets the commit through",
     "status=$?\nif [ $status -eq 0 ]; then", "status=0\nif [ $status -eq 0 ]; then"),
    ("M21", "hooks/pre-commit", "the skip setting is not passed on",
     "[ -n \"$v\" ] && set -- \"$@\" --skip \"$v\"; done", "[ -n \"$v\" ] && :; done"),
    ("M22", "hooks/commit-msg", "the message gate never runs",
     "if [ -n \"$list\" ]; then\n    script=", "if false; then\n    script="),
]


def run(row: tuple[str, str, str, str, str]) -> tuple[str, str, list[tuple[str, str]]]:
    mid, rel, _, old, new = row
    base = tempfile.mkdtemp(prefix=f"ai-orchestrator-{mid}-")
    try:
        shutil.copytree(os.path.join(REPO, "scripts"), os.path.join(base, "scripts"))
        shutil.copytree(os.path.join(REPO, "hooks"), os.path.join(base, "hooks"))
        target = os.path.join(base, rel)
        with open(target, "rb") as fh:
            data = fh.read().decode("utf-8")
        if data.count(old) != 1:
            return mid, f"ANCHOR FOUND {data.count(old)} TIMES", []
        with open(target, "wb") as fh:
            fh.write(data.replace(old, new).encode("utf-8"))
        r = subprocess.run([sys.executable, os.path.join(HERE, "selftest.py"),
                            "--scripts-dir", os.path.join(base, "scripts"),
                            "--hook", os.path.join(base, "hooks", "commit-msg"),
                            "--pre-commit", os.path.join(base, "hooks", "pre-commit")],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1200)
        fails = re.findall(r"^FAIL\s+(\d+): (.*)$", r.stdout, re.M)
        return mid, ("CAUGHT" if fails else "SURVIVED"), fails
    except subprocess.TimeoutExpired:
        return mid, "CAUGHT (the selftest timed out on the broken copy)", [("-", "timeout")]
    finally:
        shutil.rmtree(base, onerror=lambda f, p, e: (os.chmod(p, stat.S_IWRITE), f(p)))


def main() -> int:
    ap = argparse.ArgumentParser(description="Break one guard at a time in a copy and prove the selftest fails.")
    ap.add_argument("--only", nargs="+", default=[], help="run only these break ids (M1 M2 ...)")
    ap.add_argument("--jobs", type=int, default=2, help="selftest runs at once (1 to 4; default 2: each run starts many git processes)")
    args = ap.parse_args()
    rows = [b for b in BREAKS if not args.only or b[0] in args.only]
    unknown = sorted(set(args.only) - {b[0] for b in BREAKS})
    if unknown or not rows:
        print(f"mutation-pass: no such break: {' '.join(unknown) or '(none selected)'}")
        return 2
    jobs = min(max(args.jobs, 1), 4)
    caught = survived = moved = 0
    with cf.ThreadPoolExecutor(max_workers=jobs) as ex:
        for (mid, verdict, fails), row in zip(ex.map(run, rows), rows):
            names = "; ".join(f"FAIL {n} {t[:60]}" for n, t in fails[:3])
            print(f"{mid} {verdict}: {row[2]}" + (f" -> {names}" if names else ""), flush=True)
            if verdict.startswith("CAUGHT"):
                caught += 1
            elif verdict == "SURVIVED":
                survived += 1
            else:
                moved += 1
    print(f"mutation-pass: {caught} of {len(rows)} breaks caught"
          + (f"; {survived} survived" if survived else "") + (f"; {moved} could not be applied" if moved else ""))
    if moved:
        return 2
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main())
