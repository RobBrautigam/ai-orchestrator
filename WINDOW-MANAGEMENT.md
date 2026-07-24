# Window Management & Worktree Teardown

*The division of labor between the orchestrator and the operator for worktree folders and editor windows - plus the safe teardown sequence and one hard-won warning about `git worktree remove --force` on Windows.*

The short version: **the orchestrator owns the worktree FOLDERS; the operator owns the editor WINDOWS.** The orchestrator creates, removes, renames, and prunes worktrees. The operator opens a window when told and closes it when told - and never runs worktree commands. Closing a window does NOT remove a worktree (only `git worktree remove` does); opening a window does NOT create one (only `git worktree add` does).

---

## The four rules

### 1. Create the folder BEFORE handing the prompt (the cardinal rule)

When the orchestrator hands the operator a starter prompt for a NEW worktree, it must run the creation first, in the same turn:

```bash
git worktree add C:/dev/myrepo-feature-a -b feat/a origin/main
git worktree list   # confirm it exists
```

…and only THEN deliver a prompt whose pre-flight *assumes the folder already exists*:

> "You are in `C:/dev/myrepo-feature-a` on `feat/a` - the orchestrator created it. Confirm with `git rev-parse --abbrev-ref HEAD` + `pwd`. Do NOT create a worktree."

Never write a prompt that tells the pasted session to `git worktree add` its own worktree. The operator can't open a window on a folder that doesn't exist yet, so there's nowhere to paste that prompt. (Continuing an already-open window needs no creation - just hand the continuation prompt.)

### 2. EVERY pasted briefing gets a window verdict - not just teardowns

When a stream finishes, the orchestrator (a) validates the briefing - "merged" ≠ "live", verify the claims - (b) folds it into the board, (c) runs the teardown sequence below, and (d) ends with ONE plain sentence for the operator:

- **"Close that window - I've retired the worktree."** or
- **"Keep it open - next is X."**

The rule broadened with use: it fires on **every briefing or update the operator pastes from another window - mid-stream or terminal, from any orchestrator.** The reply must always contain an explicit instruction for that window: close it, keep it open (with the next prompt delivered), or another named action. A pasted briefing IS the trigger; an operator juggling many windows should never have to ask "what do I do with that window?" Missing the verdict is a defect, not a style miss.

### 3. The operator never manages worktree folders

All `git worktree add / remove / prune`, branch archiving, and folder cleanup belong to the orchestrator. If a prompt or a teardown asks the operator to run worktree commands, that's a bug in the prompt.

### 4. Locked leftover folders are HARMLESS - never escalate them

On Windows, a lingering process (an editor, a language server, a file watcher) often memory-maps native `.node` binaries inside `node_modules` and holds a file lock on the worktree folder. When that happens, `git worktree remove` still *de-registers* the worktree git-side even though the physical folder can't be deleted yet. That leftover folder is purely cosmetic: it's off `git worktree list`, its branch is archived on the remote, nothing depends on it - and it clears on window-close or reboot.

So: record it on the board as a harmless orphan ("clears on reboot") and move on. Don't hand-delete it, don't hunt the process holding the lock, don't reboot for it - and above all don't reach for `--force` (see the caution below). The one exception: if the SAME path is needed for a new `git worktree add`, surface the folder-delete to the operator then, and only then.

---

## Standing worktrees (the churn-killer)

The original pattern created a worktree per stream and retired it at merge. That's still right for one-shot streams - but for a **multi-phase initiative** it produced pure waste: re-checking out thousands of files, re-copying env files, re-installing dependencies, and a fresh window for the operator, every phase, for no engineering benefit.

The evolved pattern:

- **One STANDING worktree per long-running initiative**, living until the initiative completes (or is parked). Named for the initiative, not the phase: `C:/dev/myrepo-payments`, not `C:/dev/myrepo-payments-phase3`.
- **Branches ROTATE inside it.** At each phase start, the session (not the orchestrator - one conversation per folder means the orchestrator never runs git inside a live worktree) branches fresh from the live main, from within the folder:

  ```bash
  git fetch origin
  git checkout -b feat/payments-phase3 origin/main   # you can't check out main itself inside a worktree
  ```

  The old phase branch is deleted after its merge; the folder and its bootstrap persist.
- **Bootstrap ONCE at creation:** copy env files, install dependencies, build shared packages. Never again for the initiative's lifetime.
- **Serial reuse is safe.** One conversation at a time in the folder never violates the one-conversation-per-folder law - that law is about CONCURRENT conversations.
- **The dispatch question:** *"will this thread need more than ~2 sessions?"* Yes or unsure → standing. Genuinely one-shot (a single audit, a spike) → ephemeral, torn down at merge.
- **Teardown** (the full archive-before-remove sequence below) runs once, when the initiative completes - not per phase.

---

## The teardown sequence (archive-before-remove)

Nothing should ever be lost to a teardown. Before removing any worktree, confirm its branch and any open PR are pushed to the remote. The canonical order:

1. Validate the briefing - every claimed PR/commit verified in `git log`; "merged" ≠ "live".
2. Confirm the branch is on the remote (`git log origin/<branch>` / `gh pr view`).
3. `git worktree remove <path>` - **plain, no `--force`**. If it fails on a lock, stop (see below).
4. `git worktree prune`.
5. `git branch -D <merged-branch>` only after confirming its content is on the remote.
6. Record any lingering folder as a harmless orphan (rule 4).

---

## ⚠️ Hard caution: never `--force` a locked or heavy worktree

**`git worktree remove --force` on a locked worktree can damage the SHARED MAIN CHECKOUT - not just the worktree.**

The failure mode, learned the hard way on Windows: a worktree holding a large gitignored working set (hundreds of MB of `node_modules` native addons and build output), locked by a lingering process. A forced removal began deleting the working tree, hit the Windows lock partway through, and the partially-interrupted delete cascaded into the shared git admin state - leaving BOTH the worktree folder AND the main checkout gutted (`.git` gone, most files deleted). The remote was fully intact - nothing committed and pushed was lost - but the local main checkout had to be re-cloned.

The trade `--force` offers is: win a cosmetic folder deletion, risk re-cloning the entire repo. Never take it.

**The safe pattern instead:**

- Try plain `git worktree remove <path>`. If it fails on a lock, **stop**.
- Have the operator close that window first (releases the lock), then retry the plain remove - it usually deletes cleanly.
- If a folder still lingers after clean de-registration, **leave it** (rule 4 - it clears on reboot).
- If you must retire a worktree whose tree stays locked, de-register it git-side only (a plain `git worktree remove` may de-register even when the physical delete fails - verify with `git worktree list`) and leave the folder behind.
- **After ANY worktree removal, verify the main checkout is intact:** `git -C C:/dev/myrepo rev-parse --is-inside-work-tree` + `git worktree list`. If the main checkout is ever damaged, the remote is the source of truth - re-clone; nothing committed + pushed is lost.

---

## Why this doc exists

An operator running 5-20 windows at once needs exactly two things from the system: to always be told what to do with each window in one plain sentence, and to never be handed folder plumbing. Everything above is in service of those two - plus the one `--force` scar that turned a cosmetic orphan folder into a full re-clone.
