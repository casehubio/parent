#!/usr/bin/env python3
"""
Ecosystem version management — bump, tag, or inspect versions across all repos.

Usage:
  release.py status                         Show current version of each repo
  release.py set-version <version> [opts]   Set all repos to <version>
  release.py tag <version> [opts]           Tag all repos at current HEAD

Options:
  --push          Push commits/tags to upstream after local changes
  --dry-run       Show what would change without doing it
  --include-apps  Include application repos (modules-applications.csv)
  --repo <name>   Operate on a single repo only

Detects whether each repo is cloned locally and on main with a clean tree.
If not, clones into a temp directory and works there.
"""

import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

NS = "http://maven.apache.org/POM/4.0.0"
ET.register_namespace("", NS)
ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")

REPO_OVERRIDE = {
    "pages": "casehubio/casehub-pages",
    "worker": "casehubio/casehub-worker",
    "desiredstate": "casehubio/casehub-desiredstate",
    "ras": "casehubio/casehub-ras",
    "ops": "casehubio/casehub-ops",
    "flow": "mdproctor/flow",
}

TOKEN_OVERRIDE = {"quarkmind", "flow"}

SCRIPT_DIR = Path(__file__).resolve().parent
PARENT_DIR = SCRIPT_DIR.parent
CASEHUB_ROOT = PARENT_DIR.parent

# CI mode: repos cloned under ./casehub/, parent is CWD
CI_MODE = os.environ.get("GITHUB_ACTIONS") == "true"
if CI_MODE:
    CASEHUB_ROOT = PARENT_DIR / "casehub"


def git(args, cwd=None, check=True):
    result = subprocess.run(
        ["git"] + args, cwd=cwd, capture_output=True, text=True
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result


def load_repos(include_apps):
    repos = []
    csvs = [PARENT_DIR / "build" / "modules-core.csv"]
    if include_apps:
        csvs.append(PARENT_DIR / "build" / "modules-applications.csv")
    for csv_path in csvs:
        if not csv_path.exists():
            continue
        with open(csv_path) as f:
            for row in csv.reader(f):
                if not row or row[0].startswith("#"):
                    continue
                repos.append(row[0].strip())
    return repos


def github_repo(name):
    if name in REPO_OVERRIDE:
        return REPO_OVERRIDE[name]
    return f"casehubio/{name}"


def get_local_path(name):
    p = CASEHUB_ROOT / name
    if p.is_dir() and (p / "pom.xml").exists():
        return p
    return None


def is_usable_local(path):
    """Check if local clone is on main with clean working tree."""
    branch = git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=path, check=False)
    if branch.returncode != 0 or branch.stdout.strip() != "main":
        return False, f"on branch '{branch.stdout.strip()}'"
    status = git(["status", "--porcelain"], cwd=path, check=False)
    if status.stdout.strip():
        return False, "dirty working tree"
    return True, "ok"


def clone_bare(name, tmpdir):
    """Shallow clone into temp directory."""
    repo = github_repo(name)
    dest = Path(tmpdir) / name
    token_env = os.environ.get("GH_TOKEN", os.environ.get("GITHUB_TOKEN", ""))
    if token_env:
        url = f"https://x-access-token:{token_env}@github.com/{repo}.git"
    else:
        url = f"https://github.com/{repo}.git"
    result = git(["clone", "--depth=1", "--branch", "main", url, str(dest)], check=False)
    if result.returncode != 0:
        return None, result.stderr.strip()
    return dest, "cloned"


def read_version(pom_path):
    tree = ET.parse(pom_path)
    root = tree.getroot()
    ver_el = root.find(f"{{{NS}}}version")
    if ver_el is not None and ver_el.text:
        return ver_el.text.strip()
    parent = root.find(f"{{{NS}}}parent")
    if parent is not None:
        pver = parent.find(f"{{{NS}}}version")
        if pver is not None and pver.text:
            return pver.text.strip()
    return None


def set_version_in_pom(pom_path, new_version, old_version=None):
    """Update version in pom.xml using text replacement to preserve formatting."""
    with open(pom_path) as f:
        content = f.read()

    original = content

    if old_version:
        ov = re.escape(old_version)
        content = re.sub(
            rf"(<version>){ov}(</version>)",
            rf"\g<1>{new_version}\2",
            content,
        )
        content = re.sub(
            rf"(<casehub\.version>){ov}(</casehub\.version>)",
            rf"\g<1>{new_version}\2",
            content,
        )

    changed = content != original
    if changed:
        with open(pom_path, "w") as f:
            f.write(content)
    return changed


def cmd_status(args):
    repos = ["parent"] + load_repos(args.include_apps)
    print(f"{'Repo':<30} {'Version':<20} {'Location'}")
    print("-" * 75)
    for name in repos:
        local = get_local_path(name)
        if name == "parent":
            local = PARENT_DIR
        if local:
            ver = read_version(local / "pom.xml")
            usable, reason = is_usable_local(local)
            loc = f"local ({'main, clean' if usable else reason})"
        else:
            loc = f"remote ({github_repo(name)})"
            ver = "?"
        print(f"{name:<30} {ver or '?':<20} {loc}")


def cmd_set_version(args):
    new_version = args.version
    repos = load_repos(args.include_apps)
    if args.repo:
        repos = [r for r in repos if r == args.repo]
        if not repos:
            repos = [args.repo]

    all_repos = ["parent"] + repos
    tmpdir = tempfile.mkdtemp(prefix="casehub-release-")
    results = []

    try:
        for name in all_repos:
            if name == "parent":
                local = PARENT_DIR
            else:
                local = get_local_path(name)

            work_dir = None
            source = None
            remote_for_push = None

            if local:
                usable, reason = is_usable_local(local)
                if usable:
                    work_dir = local
                    source = "local"
                    has_upstream = git(["remote", "get-url", "upstream"], cwd=local, check=False).returncode == 0
                    remote_for_push = "upstream" if has_upstream else "origin"
                else:
                    print(f"  {name}: local not usable ({reason}), cloning...")
                    work_dir, msg = clone_bare(name, tmpdir)
                    if not work_dir:
                        results.append((name, "SKIP", f"clone failed: {msg}"))
                        continue
                    source = "cloned"
                    remote_for_push = "origin"
            else:
                work_dir, msg = clone_bare(name, tmpdir)
                if not work_dir:
                    results.append((name, "SKIP", f"clone failed: {msg}"))
                    continue
                source = "cloned"
                remote_for_push = "origin"

            pom = work_dir / "pom.xml"
            if not pom.exists():
                results.append((name, "SKIP", "no pom.xml"))
                continue
            old_version = read_version(pom)

            if old_version == new_version:
                results.append((name, "OK", f"already at {new_version}"))
                continue

            if args.dry_run:
                results.append((name, "DRY", f"{old_version} -> {new_version} ({source})"))
                continue

            changed = set_version_in_pom(pom, new_version, old_version)
            if not changed:
                results.append((name, "SKIP", f"no version match for {old_version}"))
                continue

            git(["add", "pom.xml"], cwd=work_dir)
            git(["commit", "-m", f"Prepare {new_version}"], cwd=work_dir)

            if args.push:
                push_result = git(
                    ["push", remote_for_push, "main"], cwd=work_dir, check=False
                )
                if push_result.returncode != 0:
                    results.append((name, "FAIL", f"push failed: {push_result.stderr.strip()[:80]}"))
                    continue

            results.append((name, "OK", f"{old_version} -> {new_version} ({source}{', pushed' if args.push else ''})"))

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    print(f"\n{'Repo':<30} {'Status':<8} Detail")
    print("-" * 80)
    for name, status, detail in results:
        print(f"{name:<30} {status:<8} {detail}")

    ok = sum(1 for _, s, _ in results if s == "OK")
    skip = sum(1 for _, s, _ in results if s in ("SKIP", "DRY"))
    fail = sum(1 for _, s, _ in results if s == "FAIL")
    print(f"\n{ok} updated, {skip} skipped, {fail} failed")


def cmd_tag(args):
    version = args.version
    if "SNAPSHOT" in version:
        print("Cannot tag a SNAPSHOT version.", file=sys.stderr)
        return 1
    tag_name = f"v{version}"

    repos = load_repos(args.include_apps)
    if args.repo:
        repos = [r for r in repos if r == args.repo]
        if not repos:
            repos = [args.repo]

    all_repos = ["parent"] + repos
    tmpdir = tempfile.mkdtemp(prefix="casehub-tag-")
    results = []

    try:
        for name in all_repos:
            if name == "parent":
                local = PARENT_DIR
            else:
                local = get_local_path(name)

            work_dir = None
            remote_for_push = None

            if local:
                usable, reason = is_usable_local(local)
                if usable:
                    work_dir = local
                    has_upstream = git(["remote", "get-url", "upstream"], cwd=local, check=False).returncode == 0
                    remote_for_push = "upstream" if has_upstream else "origin"
                else:
                    work_dir, msg = clone_bare(name, tmpdir)
                    if not work_dir:
                        results.append((name, "SKIP", f"clone failed: {msg}"))
                        continue
                    remote_for_push = "origin"
            else:
                work_dir, msg = clone_bare(name, tmpdir)
                if not work_dir:
                    results.append((name, "SKIP", f"clone failed: {msg}"))
                    continue
                remote_for_push = "origin"

            existing = git(["tag", "-l", tag_name], cwd=work_dir, check=False)
            if tag_name in existing.stdout.strip().split("\n"):
                results.append((name, "OK", f"{tag_name} already exists"))
                continue

            if args.dry_run:
                results.append((name, "DRY", f"would create {tag_name}"))
                continue

            git(["tag", tag_name], cwd=work_dir)

            if args.push:
                push_result = git(
                    ["push", remote_for_push, tag_name], cwd=work_dir, check=False
                )
                if push_result.returncode != 0:
                    results.append((name, "FAIL", f"push failed: {push_result.stderr.strip()[:80]}"))
                    continue

            results.append((name, "OK", f"tagged {tag_name}{' (pushed)' if args.push else ''}"))

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    print(f"\n{'Repo':<30} {'Status':<8} Detail")
    print("-" * 80)
    for name, status, detail in results:
        print(f"{name:<30} {status:<8} {detail}")


def _resolve_work_dir(name, tmpdir):
    """Resolve a working directory for a repo — local if usable, cloned otherwise."""
    if name == "parent":
        local = PARENT_DIR
        if CI_MODE:
            return local, "local", "origin", None
    else:
        local = get_local_path(name)

    if local:
        usable, reason = is_usable_local(local)
        if usable:
            has_upstream = git(["remote", "get-url", "upstream"], cwd=local, check=False).returncode == 0
            remote = "upstream" if has_upstream else "origin"
            return local, "local", remote, None
        else:
            print(f"  {name}: local not usable ({reason}), cloning...")
            work_dir, msg = clone_bare(name, tmpdir)
            if not work_dir:
                return None, None, None, f"clone failed: {msg}"
            return work_dir, "cloned", "origin", None
    else:
        work_dir, msg = clone_bare(name, tmpdir)
        if not work_dir:
            return None, None, None, f"clone failed: {msg}"
        return work_dir, "cloned", "origin", None


def _bump_version(name, work_dir, source, remote, old_ver, new_ver, push, commit_msg):
    """Bump version in a repo's pom.xml, commit, and optionally push."""
    pom = work_dir / "pom.xml"
    if not pom.exists():
        return "SKIP", "no pom.xml"

    current = read_version(pom)
    if old_ver and current != old_ver:
        return "SKIP", f"expected {old_ver}, found {current}"
    if current == new_ver:
        return "OK", f"already at {new_ver}"

    changed = set_version_in_pom(pom, new_ver, current)
    if not changed:
        return "SKIP", f"no version match for {current}"

    git(["add", "pom.xml"], cwd=work_dir)
    git(["commit", "-m", commit_msg], cwd=work_dir)

    if push:
        push_result = git(["push", remote, "main"], cwd=work_dir, check=False)
        if push_result.returncode != 0:
            return "FAIL", f"push failed: {push_result.stderr.strip()[:80]}"

    return "OK", f"{current} -> {new_ver} ({source}{', pushed' if push else ''})"


def _tag_repo(name, work_dir, remote, tag_name, push):
    """Tag a repo at HEAD, optionally push the tag."""
    existing = git(["tag", "-l", tag_name], cwd=work_dir, check=False)
    if tag_name in existing.stdout.strip().split("\n"):
        return "OK", f"{tag_name} already exists"

    git(["tag", tag_name], cwd=work_dir)

    if push:
        push_result = git(["push", remote, tag_name], cwd=work_dir, check=False)
        if push_result.returncode != 0:
            return "FAIL", f"tag push failed: {push_result.stderr.strip()[:80]}"

    return "OK", f"tagged {tag_name}{' (pushed)' if push else ''}"


def cmd_release(args):
    """Full release: drop SNAPSHOT, commit, tag, push, then bump to next SNAPSHOT."""
    release_version = args.version
    if "SNAPSHOT" in release_version:
        print("Release version must not contain SNAPSHOT.", file=sys.stderr)
        return 1

    parts = release_version.split(".")
    next_minor = int(parts[-1]) + 1
    next_version = ".".join(parts[:-1] + [str(next_minor)]) + "-SNAPSHOT"
    tag_name = f"v{release_version}"

    include_apps = args.include_apps
    repos = load_repos(include_apps)
    all_repos = ["parent"] + repos
    push = args.push
    dry_run = args.dry_run

    print(f"Release plan:")
    print(f"  1. Set version: * -> {release_version}")
    print(f"  2. Tag: {tag_name}")
    print(f"  3. Prepare next: {release_version} -> {next_version}")
    print(f"  Push: {'yes' if push else 'no (local only)'}")
    print(f"  Repos: {len(all_repos)}")
    print()

    if dry_run:
        print("DRY RUN — no changes will be made.\n")

    tmpdir = tempfile.mkdtemp(prefix="casehub-release-")
    phase1_results = []
    phase2_results = []
    phase3_results = []
    repo_dirs = {}

    try:
        # Resolve all work dirs first
        for name in all_repos:
            work_dir, source, remote, err = _resolve_work_dir(name, tmpdir)
            if err:
                phase1_results.append((name, "SKIP", err))
                continue
            repo_dirs[name] = (work_dir, source, remote)

        # Phase 1: set release version
        print(f"── Phase 1: Set version to {release_version} ──")
        for name in all_repos:
            if name not in repo_dirs:
                continue
            work_dir, source, remote = repo_dirs[name]
            if dry_run:
                pom = work_dir / "pom.xml"
                if not pom.exists():
                    phase1_results.append((name, "SKIP", "no pom.xml"))
                    continue
                cur = read_version(pom)
                phase1_results.append((name, "DRY", f"{cur} -> {release_version} ({source})"))
            else:
                status, detail = _bump_version(
                    name, work_dir, source, remote, None,
                    release_version, push, f"Release {release_version}"
                )
                phase1_results.append((name, status, detail))
                if status == "FAIL":
                    print(f"  ABORT: {name} failed — {detail}")
                    break

        _print_results("Phase 1 — release version", phase1_results)
        if any(s == "FAIL" for _, s, _ in phase1_results):
            print("\nRelease aborted due to failure in Phase 1.")
            return 1

        # Phase 2: tag
        print(f"\n── Phase 2: Tag {tag_name} ──")
        for name in all_repos:
            if name not in repo_dirs:
                continue
            work_dir, source, remote = repo_dirs[name]
            if dry_run:
                phase2_results.append((name, "DRY", f"would tag {tag_name}"))
            else:
                status, detail = _tag_repo(name, work_dir, remote, tag_name, push)
                phase2_results.append((name, status, detail))
                if status == "FAIL":
                    print(f"  ABORT: {name} failed — {detail}")
                    break

        _print_results("Phase 2 — tag", phase2_results)
        if any(s == "FAIL" for _, s, _ in phase2_results):
            print("\nRelease aborted due to failure in Phase 2.")
            return 1

        # Phase 3: prepare next SNAPSHOT
        print(f"\n── Phase 3: Prepare {next_version} ──")
        for name in all_repos:
            if name not in repo_dirs:
                continue
            work_dir, source, remote = repo_dirs[name]
            if dry_run:
                phase3_results.append((name, "DRY", f"{release_version} -> {next_version} ({source})"))
            else:
                status, detail = _bump_version(
                    name, work_dir, source, remote, release_version,
                    next_version, push, f"Prepare {next_version}"
                )
                phase3_results.append((name, status, detail))

        _print_results("Phase 3 — next snapshot", phase3_results)

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    ok = sum(1 for _, s, _ in phase1_results + phase2_results + phase3_results if s == "OK")
    fail = sum(1 for _, s, _ in phase1_results + phase2_results + phase3_results if s == "FAIL")
    print(f"\nRelease {'(dry run) ' if dry_run else ''}complete: {ok} operations succeeded, {fail} failed")
    return 1 if fail > 0 else 0


def _print_results(heading, results):
    print(f"\n{heading}:")
    print(f"  {'Repo':<30} {'Status':<8} Detail")
    print(f"  {'-' * 75}")
    for name, status, detail in results:
        print(f"  {name:<30} {status:<8} {detail}")


def main():
    parser = argparse.ArgumentParser(description="CaseHub ecosystem version management")
    sub = parser.add_subparsers(dest="command")

    p_status = sub.add_parser("status", help="Show version of each repo")
    p_status.add_argument("--include-apps", action="store_true")

    p_set = sub.add_parser("set-version", help="Set version across all repos")
    p_set.add_argument("version", help="Target version (e.g. 0.4-SNAPSHOT)")
    p_set.add_argument("--push", action="store_true", help="Push to upstream")
    p_set.add_argument("--dry-run", action="store_true")
    p_set.add_argument("--include-apps", action="store_true")
    p_set.add_argument("--repo", help="Single repo only")

    p_tag = sub.add_parser("tag", help="Tag all repos at HEAD")
    p_tag.add_argument("version", help="Tag version (e.g. 0.3)")
    p_tag.add_argument("--push", action="store_true", help="Push tags to upstream")
    p_tag.add_argument("--dry-run", action="store_true")
    p_tag.add_argument("--include-apps", action="store_true")
    p_tag.add_argument("--repo", help="Single repo only")

    p_rel = sub.add_parser("release", help="Full release: drop SNAPSHOT, tag, prepare next")
    p_rel.add_argument("version", help="Release version (e.g. 0.4) — must not contain SNAPSHOT")
    p_rel.add_argument("--push", action="store_true", help="Push to upstream")
    p_rel.add_argument("--dry-run", action="store_true")
    p_rel.add_argument("--include-apps", action="store_true")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1

    if args.command == "status":
        cmd_status(args)
    elif args.command == "set-version":
        cmd_set_version(args)
    elif args.command == "tag":
        return cmd_tag(args)
    elif args.command == "release":
        return cmd_release(args)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
