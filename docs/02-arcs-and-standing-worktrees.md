# 2. Arcs and standing worktrees

*An arc is a stream of work that takes more than one session. A standing worktree is the folder that arc lives in for its whole life. The plumbing is two git commands; the discipline is who runs them, when, and what never to type.*

---

## Words

- **Arc.** A named stream of work with a definition of done and, usually, several sessions: `payments`, `onboarding`, `observability`. An arc has one standing worktree, one row on the board, and a numbered sequence of sessions (`payments session 4`).
- **Standing worktree.** A sibling folder of the main checkout, named for the arc and not for the phase (`../myrepo-payments`, never `../myrepo-payments-phase3`), created once and kept until the arc completes or is parked.
- **Ephemeral worktree.** The same thing for a genuinely one-shot piece of work (one audit, one spike), torn down at its merge.
- **Rotation.** At each session start, a fresh branch is created inside the standing worktree off the live main; the previous branch is deleted after its merge. The folder and its bootstrap (environment files, installed dependencies, built packages) persist.

## Why one worktree per arc

A git worktree is a second working copy of the same repository, on its own branch, sharing the same history. Two sessions editing in two worktrees cannot corrupt each other. Two conversations in ONE folder can: a branch switch in one rewrites the files under the other. That is the one hard safety law of this whole method:

> **One conversation per folder.** Serial reuse is fine (session 4 after session 3 in the same folder). Concurrent use is not.

The July version created a worktree per session and tore it down at the merge. For a multi-phase arc that was pure waste: thousands of files re-checked-out, dependencies re-installed, environment files re-copied, every phase, for no engineering benefit. Standing worktrees killed the churn. The dispatch question is: **will this need more than about two sessions?** Yes or unsure: standing. Genuinely one-shot: ephemeral.

## The cardinal rule: the folder exists before the prompt

The chair creates the worktree, confirms it, and only then writes a prompt whose first lines assume the folder exists:

```
git -C /path/to/myrepo fetch origin
git -C /path/to/myrepo worktree add ../myrepo-payments -b feat/payments-s1 origin/main
git -C /path/to/myrepo worktree list
```

A prompt that tells its own session to create its worktree is a defect twice over: in the copy-paste era there was no window to paste it into, and in the background era the session's tool may answer a worktree request with a confirmation dialog nobody unattended can click. Every dispatch prompt's rails say so: **the worktree you are launched in IS the isolation; never call a worktree-creation tool from inside the session; write in place.**

## Rotation, exactly

At the start of session N of an arc whose worktree stands:

```
git -C ../myrepo-payments fetch origin
git -C ../myrepo-payments checkout -b feat/payments-s4 origin/main
```

You cannot check out `main` itself inside a worktree (the main checkout holds it), which is why the rotation is always `checkout -b` off `origin/main`. The old branch is deleted after its pull request merges. Bootstrap happens once, at creation: copy `.env` and its siblings, install dependencies, build shared packages. A dispatch prompt names what the chair confirmed is present ("`.env` and `node_modules` present") so the session does not re-install.

Before any branch operation in a standing worktree, the chair checks whether a session is live in it (the tool's session list, and the working tree's file times). Rotating under a live session is the concurrent-use defect by another route.

## Who does what

| Action | Who |
|---|---|
| `git worktree add`, `remove`, `prune`; branch rotation; folder cleanup | the chair |
| Opening or closing an editor window | the operator, only when the chair says, and in the background era almost never |
| Creating a worktree from inside a session | nobody |
| Deleting a leftover folder that will not remove | nobody; see below |

Closing a window never removes a worktree. Removing a worktree never closes a window. The two are unrelated operations owned by different parties.

## Teardown: archive before remove

When an arc completes:

1. Read and validate its last briefing file. "Merged" is not "live"; verify the deploy and the route (chapter 7).
2. Confirm the branch and any pull request are on the remote.
3. `git worktree remove <path>`, plain, **never `--force`**. If it fails on a lock, stop.
4. `git worktree prune`.
5. `git branch -D <branch>` only after its content is confirmed on the remote.
6. Record any lingering folder as a harmless orphan.
7. After ANY removal, verify the main checkout is intact: `git -C <main> rev-parse --is-inside-work-tree` and `git worktree list`.

## The force warning, kept from July because it was earned

On Windows, a lingering process (an editor, a language server, a file watcher) often holds a lock on native binaries inside `node_modules`. A plain `git worktree remove` still de-registers the worktree git-side even when the folder cannot be deleted; the leftover folder is cosmetic, off the worktree list, and clears on reboot.

`git worktree remove --force` on such a folder began deleting the working tree, hit the lock partway through, and the interrupted delete cascaded into the shared git administrative state, leaving the worktree AND the main checkout gutted (`.git` gone, most files deleted). The remote was intact; the main checkout had to be re-cloned. The trade `--force` offers is a cosmetic folder deletion against re-cloning the repository. Never take it. Leave the folder; write it down as an orphan; move on. The one exception is when the same path is needed for a new worktree, and even then the delete is done by hand with the lock released, not by force.

## The window verdict, kept and shrunk

In the copy-paste era every reply that handled a briefing ended with a verdict for that window: close it, keep it open and paste this, or another named action, so an operator holding fifteen windows never had to ask. In the background era the operator holds no session windows, so the verdict has shrunk to its essential form: every line that names a piece of work says who moves it next, **on me** (the chair, with the when) or **on you** (the operator, with the link and the action). Chapter 11 carries the law.
