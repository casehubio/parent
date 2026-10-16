#!/usr/bin/env python3
"""
Migrate a Maven repo to CI-friendly ${revision} versioning.

For each pom.xml in the repo:
  - Root: add <revision> property, change <version> to ${revision}
  - Child: change <parent><version> to ${revision}
  - Keep external parent (casehub-parent) version literal

Usage:
  migrate-ci-friendly.py <repo-path> <version>
  migrate-ci-friendly.py --all <version> [--push]
"""

import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PARENT_DIR = SCRIPT_DIR.parent

REPO_OVERRIDE = {
    "pages": "casehubio/casehub-pages",
    "worker": "casehubio/casehub-worker",
    "desiredstate": "casehubio/casehub-desiredstate",
    "ras": "casehubio/casehub-ras",
    "ops": "casehubio/casehub-ops",
    "flow": "mdproctor/flow",
}

CI_MODE = os.environ.get("GITHUB_ACTIONS") == "true"
CASEHUB_ROOT = PARENT_DIR / "casehub" if CI_MODE else PARENT_DIR.parent


def git(args, cwd=None, check=True):
    result = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result


def github_repo(name):
    return REPO_OVERRIDE.get(name, f"casehubio/{name}")


def load_repos():
    repos = []
    for csv_path in sorted(PARENT_DIR.glob("build/modules-*.csv")):
        with open(csv_path) as f:
            for row in csv.reader(f):
                if not row or row[0].startswith("#"):
                    continue
                repos.append(row[0].strip())
    return repos


def find_pom_files(repo_path):
    poms = []
    for pom in repo_path.rglob("pom.xml"):
        rel = pom.relative_to(repo_path)
        parts = rel.parts
        if any(p in ("target", ".git", ".claude", "node_modules", ".mvn") for p in parts):
            continue
        poms.append(pom)
    return poms


def migrate_repo(repo_path, version):
    """Migrate a single repo to ${revision} versioning. Returns number of files changed."""
    poms = find_pom_files(repo_path)
    if not poms:
        return 0

    root_pom = repo_path / "pom.xml"
    if not root_pom.exists():
        return 0

    changed = 0

    for pom in poms:
        with open(pom) as f:
            content = f.read()
        original = content

        is_root = pom == root_pom

        if is_root:
            # Add <revision> property if not present
            if "<revision>" not in content:
                content = re.sub(
                    r"(<properties>)",
                    rf"\1\n    <revision>{version}</revision>",
                    content,
                )

            # Change project's own <version> to ${revision} (direct child of <project>)
            # Match the version that's NOT inside a <parent> block or <dependency>
            # Strategy: replace the first <version>X</version> after <artifactId> but before <packaging> or <name>
            content = re.sub(
                r"(</artifactId>\s*\n\s*)<version>" + re.escape(version) + r"</version>",
                r"\1<version>${revision}</version>",
                content,
                count=1,
            )

        # Change <parent><version>CURRENT</version> to ${revision}
        # But ONLY for intra-repo parents (casehub-parent reference stays literal)
        def replace_parent_version(match):
            parent_block = match.group(0)
            if "casehub-parent" in parent_block:
                return parent_block
            return re.sub(
                r"<version>" + re.escape(version) + r"</version>",
                "<version>${revision}</version>",
                parent_block,
            )

        content = re.sub(
            r"<parent>.*?</parent>",
            replace_parent_version,
            content,
            flags=re.DOTALL,
        )

        if content != original:
            with open(pom, "w") as f:
                f.write(content)
            changed += 1

    return changed


def main():
    parser = argparse.ArgumentParser(description="Migrate to CI-friendly ${revision} versioning")
    parser.add_argument("version", help="Current version (e.g. 0.4-SNAPSHOT)")
    parser.add_argument("--all", action="store_true", help="Migrate all ecosystem repos")
    parser.add_argument("--push", action="store_true", help="Push changes to upstream")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--repo", help="Single repo only")
    args = parser.parse_args()

    version = args.version

    if args.all:
        repos = load_repos()
    elif args.repo:
        repos = [args.repo]
    else:
        parser.print_help()
        return 1

    tmpdir = tempfile.mkdtemp(prefix="casehub-migrate-")
    results = []

    try:
        for name in repos:
            local = CASEHUB_ROOT / name
            work_dir = None
            source = None

            if local.is_dir() and (local / "pom.xml").exists():
                branch = git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=local, check=False)
                if branch.returncode == 0 and branch.stdout.strip() == "main":
                    dirty = git(["status", "--porcelain"], cwd=local, check=False)
                    if not dirty.stdout.strip():
                        git(["pull", "upstream", "main"], cwd=local, check=False)
                        work_dir = local
                        source = "local"

            if not work_dir:
                repo_url = f"https://github.com/{github_repo(name)}.git"
                token = os.environ.get("GH_TOKEN", os.environ.get("GITHUB_TOKEN", ""))
                if token:
                    repo_url = f"https://x-access-token:{token}@github.com/{github_repo(name)}.git"
                dest = Path(tmpdir) / name
                result = git(["clone", "--depth=1", "--branch", "main", repo_url, str(dest)], check=False)
                if result.returncode != 0:
                    results.append((name, "SKIP", f"clone failed: {result.stderr.strip()[:60]}"))
                    continue
                work_dir = dest
                source = "cloned"
                git(["-C", str(work_dir), "config", "user.name", "Mark Proctor"], check=False)
                git(["-C", str(work_dir), "config", "user.email", "mdproctor@gmail.com"], check=False)

            if args.dry_run:
                poms = find_pom_files(work_dir)
                stale = sum(1 for p in poms if version in p.read_text())
                results.append((name, "DRY", f"{stale} pom.xml files to migrate ({source})"))
                continue

            changed = migrate_repo(work_dir, version)
            if changed == 0:
                results.append((name, "OK", f"already migrated ({source})"))
                continue

            git(["add", "-u"], cwd=work_dir)
            git(["commit", "-m", "build: migrate to CI-friendly ${revision} versioning"], cwd=work_dir)

            if args.push:
                remote = "upstream" if source == "local" else "origin"
                push_result = git(["push", remote, "main", "--no-verify"], cwd=work_dir, check=False)
                if push_result.returncode != 0:
                    results.append((name, "FAIL", f"push failed: {push_result.stderr.strip()[:60]}"))
                    continue
                if source == "local":
                    git(["push", "origin", "main", "--no-verify"], cwd=work_dir, check=False)

            results.append((name, "OK", f"{changed} files migrated ({source}{', pushed' if args.push else ''})"))

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    print(f"\n{'Repo':<30} {'Status':<8} Detail")
    print("-" * 80)
    for name, status, detail in results:
        print(f"{name:<30} {status:<8} {detail}")

    ok = sum(1 for _, s, _ in results if s == "OK")
    fail = sum(1 for _, s, _ in results if s == "FAIL")
    print(f"\n{ok} migrated, {fail} failed")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main() or 0)
