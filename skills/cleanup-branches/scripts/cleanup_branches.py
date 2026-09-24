#!/usr/bin/env python3
"""List (and optionally delete) local branches whose GitHub PRs are already merged.

Default is dry-run: JSON on stdout, human summary on stderr.
Use --apply to remove safe worktrees and delete those branches.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from typing import Any


PROTECTED_BRANCHES = frozenset(
    {"main", "master", "develop", "staging", "production"}
)


class CmdError(RuntimeError):
    def __init__(self, cmd: list[str], returncode: int, stderr: str) -> None:
        self.cmd = cmd
        self.returncode = returncode
        self.stderr = stderr
        super().__init__(f"command failed ({returncode}): {' '.join(cmd)}\n{stderr}")


def run(
    cmd: list[str],
    *,
    cwd: str | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    if check and result.returncode != 0:
        raise CmdError(cmd, result.returncode, result.stderr.strip())
    return result


def git(cwd: str, *args: str, check: bool = True) -> str:
    return run(["git", "-C", cwd, *args], check=check).stdout


def eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


@dataclass
class Worktree:
    path: str
    branch: str | None  # None if detached
    locked: bool
    prunable: bool


def parse_worktrees(porcelain: str) -> list[Worktree]:
    trees: list[Worktree] = []
    path = ""
    branch: str | None = None
    locked = False
    prunable = False

    def flush() -> None:
        nonlocal path, branch, locked, prunable
        if path:
            trees.append(
                Worktree(
                    path=os.path.abspath(path),
                    branch=branch,
                    locked=locked,
                    prunable=prunable,
                )
            )
        path = ""
        branch = None
        locked = False
        prunable = False

    for line in porcelain.splitlines():
        if line == "":
            flush()
            continue
        if line.startswith("worktree "):
            flush()
            path = line[len("worktree ") :]
        elif line.startswith("branch "):
            ref = line[len("branch ") :]
            prefix = "refs/heads/"
            branch = ref[len(prefix) :] if ref.startswith(prefix) else ref
        elif line.startswith("detached"):
            branch = None
        elif line.startswith("locked"):
            locked = True
        elif line.startswith("prunable"):
            prunable = True
    flush()
    return trees


def local_branches(repo: str) -> list[str]:
    out = git(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads")
    return [b for b in out.splitlines() if b]


def worktree_dirty(path: str) -> bool:
    result = run(["git", "-C", path, "status", "--porcelain"], check=False)
    if result.returncode != 0:
        # Missing / broken worktree — treat as unsafe.
        return True
    return bool(result.stdout.strip())


def find_main_root(start: str | None) -> str:
    cwd = start or os.getcwd()
    out = run(["git", "-C", cwd, "rev-parse", "--show-toplevel"]).stdout.strip()
    return os.path.abspath(out)


def current_branch(repo: str) -> str:
    result = run(["git", "-C", repo, "branch", "--show-current"], check=False)
    name = result.stdout.strip()
    if name:
        return name
    return "(detached)"


def gh_json(args: list[str]) -> Any:
    result = run(["gh", *args])
    return json.loads(result.stdout) if result.stdout.strip() else None


def fetch_merged_prs() -> dict[str, dict[str, Any]]:
    """One API call: map headRefName -> most recently merged PR of that name."""
    prs = gh_json(
        [
            "pr",
            "list",
            "--state",
            "merged",
            "--limit",
            "500",
            "--json",
            "number,title,url,headRefName,mergedAt",
        ]
    )
    by_head: dict[str, dict[str, Any]] = {}
    if not isinstance(prs, list):
        return by_head
    # gh returns newest-first; keep the first (most recent) per head.
    for pr in prs:
        head = pr.get("headRefName")
        if not head or head in by_head:
            continue
        by_head[head] = {
            "number": pr.get("number"),
            "title": pr.get("title"),
            "url": pr.get("url"),
            "mergedAt": pr.get("mergedAt"),
        }
    return by_head


def protected_names(default_branch: str | None) -> frozenset[str]:
    names = set(PROTECTED_BRANCHES)
    if default_branch:
        names.add(default_branch)
    return frozenset(names)


def classify(
    *,
    branches: list[str],
    worktrees: list[Worktree],
    merged: dict[str, dict[str, Any]],
    protected: frozenset[str],
    main_root: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    main_root_abs = os.path.abspath(main_root)
    branch_to_wt: dict[str, Worktree] = {}
    for wt in worktrees:
        if wt.branch:
            branch_to_wt[wt.branch] = wt

    candidates: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    for branch in sorted(branches):
        if branch in protected:
            skipped.append({"branch": branch, "reason": "protected"})
            continue

        pr = merged.get(branch)
        if not pr:
            skipped.append({"branch": branch, "reason": "no-merged-pr"})
            continue

        wt = branch_to_wt.get(branch)
        worktree_path = wt.path if wt else None

        if wt and os.path.abspath(wt.path) == main_root_abs:
            skipped.append(
                {
                    "branch": branch,
                    "reason": "current-worktree",
                    "worktree": wt.path,
                    "pr": pr,
                }
            )
            continue

        if wt and wt.locked:
            skipped.append(
                {
                    "branch": branch,
                    "reason": "locked-worktree",
                    "worktree": wt.path,
                    "pr": pr,
                }
            )
            continue

        if wt and worktree_dirty(wt.path):
            skipped.append(
                {
                    "branch": branch,
                    "reason": "dirty-worktree",
                    "worktree": wt.path,
                    "pr": pr,
                }
            )
            continue

        candidates.append(
            {
                "branch": branch,
                "worktree": worktree_path,
                "pr": pr,
                "safe": True,
            }
        )

    return candidates, skipped


def print_human_summary(
    candidates: list[dict[str, Any]],
    skipped: list[dict[str, Any]],
) -> None:
    eprint(f"candidates: {len(candidates)}  skipped: {len(skipped)}")
    if candidates:
        eprint("")
        eprint("SAFE TO DELETE")
        for row in candidates:
            pr = row["pr"]
            wt = row["worktree"] or "(no worktree)"
            eprint(f"  {row['branch']}  PR#{pr['number']}  {wt}")
    blocked = [
        s
        for s in skipped
        if s["reason"]
        in {"dirty-worktree", "current-worktree", "locked-worktree"}
    ]
    if blocked:
        eprint("")
        eprint("SKIPPED (would match but unsafe)")
        for row in blocked:
            wt = row.get("worktree") or ""
            eprint(f"  {row['branch']}  {row['reason']}  {wt}".rstrip())


def remove_worktree(main_root: str, path: str) -> None:
    result = run(
        ["git", "-C", main_root, "worktree", "remove", path],
        check=False,
    )
    if result.returncode == 0:
        return
    # Clean porcelain but leftover ignored files (e.g. env copies) often need --force.
    if not worktree_dirty(path):
        run(["git", "-C", main_root, "worktree", "remove", "--force", path])
        return
    raise CmdError(
        ["git", "worktree", "remove", path],
        result.returncode,
        result.stderr.strip() or "worktree remove failed and tree is dirty",
    )


def apply_deletes(
    main_root: str,
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    deleted: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []

    for row in candidates:
        branch = row["branch"]
        path = row.get("worktree")
        try:
            if path and os.path.isdir(path):
                if worktree_dirty(path):
                    failed.append(
                        {
                            "branch": branch,
                            "reason": "dirty-worktree",
                            "worktree": path,
                        }
                    )
                    continue
                remove_worktree(main_root, path)
            run(["git", "-C", main_root, "branch", "-D", branch])
            deleted.append({"branch": branch, "worktree": path})
        except CmdError as err:
            failed.append(
                {
                    "branch": branch,
                    "reason": "error",
                    "error": str(err),
                    "worktree": path,
                }
            )

    run(["git", "-C", main_root, "worktree", "prune"], check=False)
    return {"deleted": deleted, "failed": failed}


def build_report(main_root: str) -> dict[str, Any]:
    repo_meta = gh_json(
        ["repo", "view", "--json", "nameWithOwner,defaultBranchRef"]
    ) or {}
    default_branch = None
    default_ref = repo_meta.get("defaultBranchRef")
    if isinstance(default_ref, dict):
        default_branch = default_ref.get("name")

    porcelain = git(main_root, "worktree", "list", "--porcelain")
    worktrees = parse_worktrees(porcelain)
    branches = local_branches(main_root)
    merged = fetch_merged_prs()
    protected = protected_names(default_branch)
    candidates, skipped = classify(
        branches=branches,
        worktrees=worktrees,
        merged=merged,
        protected=protected,
        main_root=main_root,
    )

    return {
        "mainRoot": main_root,
        "currentBranch": current_branch(main_root),
        "repo": repo_meta.get("nameWithOwner"),
        "defaultBranch": default_branch,
        "candidates": candidates,
        "skipped": skipped,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "List local branches with merged GitHub PRs; "
            "optionally delete them and their worktrees."
        )
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Delete safe candidates (default is dry-run)",
    )
    parser.add_argument(
        "--cwd",
        default=None,
        help="Git repo path (default: current directory)",
    )
    args = parser.parse_args(argv)

    try:
        main_root = find_main_root(args.cwd)
        report = build_report(main_root)
    except CmdError as err:
        eprint(str(err))
        return 1
    except json.JSONDecodeError as err:
        eprint(f"failed to parse gh JSON: {err}")
        return 1
    except FileNotFoundError as err:
        eprint(f"missing tool: {err.filename}")
        return 1

    print_human_summary(report["candidates"], report["skipped"])

    if args.apply:
        # Re-classify right before delete so safety stays current.
        try:
            report = build_report(main_root)
            result = apply_deletes(main_root, report["candidates"])
        except CmdError as err:
            eprint(str(err))
            return 1
        report["apply"] = result
        eprint("")
        eprint(
            f"deleted: {len(result['deleted'])}  failed: {len(result['failed'])}"
        )
        for row in result["deleted"]:
            eprint(f"  deleted {row['branch']}")
        for row in result["failed"]:
            eprint(
                f"  failed {row['branch']}: "
                f"{row.get('reason')} {row.get('error', '')}"
            )

    print(json.dumps(report, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
