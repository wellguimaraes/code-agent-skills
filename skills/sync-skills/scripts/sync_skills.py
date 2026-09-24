#!/usr/bin/env python3
"""Reconcile ~/.agents/skills (canonical) with agent skill dirs (Cursor, Claude, Codex, Command Code).

Mechanical cases are fixed automatically:
  - unique real dirs are moved into the canonical dir and symlinked back
  - byte-identical duplicates are deduplicated to one canonical copy
  - symlinks are (re)created so every canonical skill exists in every agent
  - lost skills listed in ~/.agents/.skill-lock.json are re-cloned from git
Reported for a human decision:
  - CONFLICT: same skill name with different content in two places
  - MISSING: broken symlink with no recoverable source
Exit status is 0 when fully in sync, 1 when problems remain.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HOME = os.path.expanduser("~")
CANON = os.path.join(HOME, ".agents", "skills")
AGENT_DIRS = [
    os.path.join(HOME, ".cursor", "skills"),
    os.path.join(HOME, ".codex", "skills"),
    os.path.join(HOME, ".claude", "skills"),
    os.path.join(HOME, ".commandcode", "skills"),
]
SKIP = {".system"}  # agent-owned extras, never touch
LOCK = os.path.join(HOME, ".agents", ".skill-lock.json")

actions = []
problems = []


def note(msg):
    actions.append(msg)
    print(msg)


def problem(msg):
    problems.append(msg)
    print(msg)


def entries(d):
    """name -> path for skill-like entries, skipping agent-owned extras."""
    out = {}
    if not os.path.isdir(d):
        return out
    for name in sorted(os.listdir(d)):
        if name in SKIP or name.startswith("."):
            continue
        out[name] = os.path.join(d, name)
    return out


def state(path):
    """Classify an entry: missing / broken-link / link-canonical /
    link-external / real-dir / other."""
    if os.path.islink(path):
        target = os.path.realpath(path)
        if not os.path.exists(target):
            return ("broken-link", None)
        canon_name = os.path.join(CANON, os.path.basename(path))
        if os.path.realpath(canon_name) == target if os.path.lexists(canon_name) else False:
            return ("link-canonical", target)
        if target == os.path.realpath(canon_name) if os.path.lexists(canon_name) else target == canon_name:
            return ("link-canonical", target)
        return ("link-external", target)
    if os.path.isdir(path):
        return ("real-dir", path)
    return ("other", path)


def identical(a, b):
    r = subprocess.run(["diff", "-r", "-q", a, b],
                       capture_output=True, text=True)
    return r.returncode == 0


def link_to(agent_dir, name):
    link = os.path.join(agent_dir, name)
    if os.path.islink(link) or os.path.exists(link):
        if os.path.islink(link) and os.path.realpath(link) == os.path.realpath(
                os.path.join(CANON, name)):
            return  # already correct
        if os.path.lexists(link):
            note(f"  replace {link} with canonical symlink")
            if os.path.isdir(link) and not os.path.islink(link):
                shutil.rmtree(link)
            else:
                os.remove(link)
    os.symlink(os.path.join(CANON, name), link)
    note(f"  linked {link}")


def reinstall(name):
    """Best-effort restore from the skills-manager lock file."""
    try:
        lock = json.load(open(LOCK))
        entry = lock.get("skills", {}).get(name)
    except (OSError, ValueError):
        return False
    if not entry or not entry.get("sourceUrl") or not entry.get("skillPath"):
        return False
    tmp = tempfile.mkdtemp(prefix="sync-skills-")
    try:
        subprocess.run(["git", "clone", "--depth", "1",
                        entry["sourceUrl"], "repo"],
                       cwd=tmp, check=True,
                       capture_output=True, text=True)
        src = os.path.join(tmp, "repo", os.path.dirname(entry["skillPath"]))
        if not os.path.isfile(os.path.join(src, "SKILL.md")):
            return False
        dst = os.path.join(CANON, name)
        if os.path.lexists(dst):
            return False
        shutil.copytree(src, dst)
        note(f"  reinstalled {name} from {entry['sourceUrl']}")
        return True
    except (subprocess.CalledProcessError, OSError):
        return False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    os.makedirs(CANON, exist_ok=True)
    for d in AGENT_DIRS:
        os.makedirs(d, exist_ok=True)

    canon = entries(CANON)
    per_agent = {d: entries(d) for d in AGENT_DIRS}
    names = set(canon) | {n for e in per_agent.values() for n in e}

    for name in sorted(names):
        print(f"## {name}")
        c_path = canon.get(name)
        c_state, c_target = state(c_path) if c_path else ("missing", None)

        # Collect real content locations (canonical + external link targets).
        real_dirs = []
        if c_state == "real-dir":
            real_dirs.append(("canonical", c_path))
        elif c_state == "link-external":
            real_dirs.append(("canonical-link", c_target))
        for d in AGENT_DIRS:
            p = per_agent[d].get(name)
            if not p:
                continue
            st, tgt = state(p)
            if st == "real-dir":
                real_dirs.append((d, p))
            elif st == "link-external":
                real_dirs.append((d + " (link)", tgt))

        # Ensure exactly one canonical copy of the content.
        if c_state in ("missing", "broken-link"):
            if c_state == "broken-link":
                os.remove(c_path)
                note("  removed broken canonical link")
            if real_dirs:
                keep = real_dirs[0][1]
                for loc, other in real_dirs[1:]:
                    if not identical(keep, other):
                        problem(f"  CONFLICT: {name} differs between "
                                f"{real_dirs[0][0]} and {loc}; kept neither, "
                                f"resolve manually")
                        keep = None
                        break
                    if loc.startswith(HOME) and os.path.isdir(other) and other != keep:
                        shutil.rmtree(other)
                        note(f"  removed identical duplicate {other}")
                if keep is None:
                    continue
                if keep == c_target or (c_target and os.path.realpath(keep) == c_target):
                    shutil.move(c_target, os.path.join(CANON, name))
                    os.remove(c_path) if os.path.islink(c_path) else None
                    note(f"  moved {c_target} into canonical")
                elif keep != os.path.join(CANON, name):
                    if os.path.isdir(keep):
                        shutil.move(keep, os.path.join(CANON, name))
                        note(f"  moved {keep} into canonical")
                canon = entries(CANON)
            else:
                # Nothing on disk anywhere: try the lock file.
                if reinstall(name):
                    canon = entries(CANON)
                else:
                    problem(f"  MISSING: {name} has no content anywhere and "
                            f"no reinstall source; install manually")
                    continue
        elif c_state == "real-dir":
            for loc, other in real_dirs:
                if loc == "canonical":
                    continue
                if identical(os.path.join(CANON, name), other):
                    if os.path.isdir(other):
                        shutil.rmtree(other)
                        note(f"  removed identical duplicate {other}")
                else:
                    problem(f"  CONFLICT: {name} differs between canonical "
                            f"and {loc}; resolve manually")
                    break
            else:
                pass  # no conflicts; fall through to linking
            if any(p.startswith("CONFLICT") and name in p for p in problems):
                continue

        # Link into every agent dir.
        for d in AGENT_DIRS:
            p = os.path.join(d, name)
            if os.path.islink(p) and not os.path.exists(os.path.realpath(p)):
                os.remove(p)
                note(f"  removed broken link {p}")
                link_to(d, name)
            elif not os.path.lexists(p):
                link_to(d, name)
            elif os.path.islink(p):
                if os.path.realpath(p) != os.path.realpath(os.path.join(CANON, name)):
                    # External link: fold its content in if canonical lacks it.
                    if identical(os.path.realpath(p), os.path.join(CANON, name)):
                        link_to(d, name)
                    else:
                        problem(f"  CONFLICT: {p} points outside canonical "
                                f"with different content; resolve manually")
            elif os.path.isdir(p):
                if os.path.realpath(p) == os.path.realpath(os.path.join(CANON, name)):
                    continue  # same dir (shouldn't happen), leave alone
                if identical(p, os.path.join(CANON, name)):
                    shutil.rmtree(p)
                    link_to(d, name)
                else:
                    problem(f"  CONFLICT: {p} is a real dir differing from "
                            f"canonical; resolve manually")

    print()
    leftovers = subprocess.run(
        ["find"] + AGENT_DIRS + ["-xtype", "l"],
        capture_output=True, text=True).stdout.strip()
    if leftovers:
        problem(f"Broken links remain:\n{leftovers}")

    if problems:
        print(f"\n{len(problems)} problem(s) need a human.")
        return 1
    print("All skills in sync, no broken links.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
