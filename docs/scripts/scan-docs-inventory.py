#!/usr/bin/env python3
"""Scan all CaseHub repos and generate docs-inventory.yaml.

Produces a flat YAML index of every .md file across product repos,
workspace repos, blog sites, and the parent repo. Extracts headings
and git last-modified dates. No content interpretation.

Usage:
    python3 docs/scripts/scan-docs-inventory.py --slot /path/to/slot207
"""

import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml")
    sys.exit(1)

PRODUCT_REPOS = [
    "aml", "blocks", "blocks-ui", "casehub-langchain4j", "chat-app",
    "claudony", "clinical", "connectors", "desiredstate", "devtown",
    "drafthouse", "eidos", "engine", "examples", "fsitrading", "iot",
    "ledger", "life", "neocortex", "openclaw", "ops", "pages",
    "platform", "qhorus", "quarkmind", "ras", "scaffold", "soc",
    "work", "worker", "workers",
]

WORKSPACE_NAME_MAP = {
    "quarkmind": "wsp-quarkmind",
}

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

EXCLUDE_PATTERNS = [
    "/api/",
    "/node_modules/",
    "/target/",
    "/.git/",
]


def git_last_modified_batch(repo_path, file_paths):
    """Get last-modified dates for all files in one git call per repo."""
    if not file_paths:
        return {}
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "log", "--format=%aI",
             "--name-only", "--diff-filter=ACDMR", "--", "*.md"],
            capture_output=True, text=True, timeout=60
        )
        dates = {}
        current_date = None
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("20") and "T" in line:
                current_date = line[:10]
            elif current_date and line.endswith(".md"):
                if line not in dates:
                    dates[line] = current_date
        return dates
    except Exception:
        return {}


def extract_headings(filepath):
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    return [
        {"level": len(m.group(1)), "text": m.group(2).strip()}
        for m in HEADING_RE.finditer(text)
    ]


def should_exclude(filepath):
    s = str(filepath)
    return any(pat in s for pat in EXCLUDE_PATTERNS)


def find_md_files(base, patterns):
    found = []
    for pattern in patterns:
        found.extend(sorted(base.glob(pattern)))
    seen = set()
    deduped = []
    for f in found:
        if should_exclude(f):
            continue
        resolved = f.resolve()
        if resolved not in seen:
            seen.add(resolved)
            deduped.append(f)
    return deduped


def scan_product_repo(name, slot, canonical):
    repo_path = slot / name
    if not repo_path.exists():
        repo_path = canonical / name
    if not repo_path.exists():
        print(f"  SKIP {name}: not found", flush=True)
        return []
    patterns = ["docs/**/*.md", "README.md", "CLAUDE.md"]
    files = find_md_files(repo_path, patterns)
    git_dates = git_last_modified_batch(repo_path, files)
    entries = []
    for f in files:
        rel = f.relative_to(repo_path)
        entries.append({
            "path": str(rel),
            "repo": name,
            "source": "project",
            "headings": extract_headings(f),
            "last_modified": git_dates.get(str(rel)),
        })
    return entries


def scan_workspace_repo(name, slot):
    wsp_name = WORKSPACE_NAME_MAP.get(name, f"wsp-casehub-{name}")
    repo_path = slot / wsp_name
    if not repo_path.exists():
        wsp_name = f"wsp-{name}"
        repo_path = slot / wsp_name
    if not repo_path.exists():
        return []
    patterns = ["blog/**/*.md", "specs/**/*.md"]
    files = find_md_files(repo_path, patterns)
    git_dates = git_last_modified_batch(repo_path, files)
    entries = []
    for f in files:
        rel = f.relative_to(repo_path)
        entries.append({
            "path": str(rel),
            "repo": f"{name} (workspace)",
            "source": "project",
            "headings": extract_headings(f),
            "last_modified": git_dates.get(str(rel)),
        })
    return entries


def scan_parent(slot, canonical):
    repo_path = slot / "parent"
    if not repo_path.exists():
        repo_path = canonical / "parent"
    if not repo_path.exists():
        print("  SKIP parent: not found", flush=True)
        return []
    all_files = sorted(repo_path.glob("docs/**/*.md"))
    files = [f for f in all_files
             if not str(f.relative_to(repo_path)).startswith("docs/repos/")
             and not should_exclude(f)]
    git_dates = git_last_modified_batch(repo_path, files)
    entries = []
    for f in files:
        rel = f.relative_to(repo_path)
        entries.append({
            "path": str(rel),
            "repo": "parent",
            "source": "project",
            "headings": extract_headings(f),
            "last_modified": git_dates.get(str(rel)),
        })
    return entries


def scan_blog_site(dir_name, source_value, patterns, search_paths):
    for base in search_paths:
        if base.exists():
            break
    else:
        print(f"  SKIP {dir_name}: not found", flush=True)
        return []
    files = find_md_files(base, patterns)
    git_dates = git_last_modified_batch(base, files)
    entries = []
    for f in files:
        rel = f.relative_to(base)
        entries.append({
            "path": str(rel),
            "repo": dir_name,
            "source": source_value,
            "headings": extract_headings(f),
            "last_modified": git_dates.get(str(rel)),
        })
    return entries


def dedup(entries):
    blog_filenames = set()
    for e in entries:
        if e["source"] in ("blog-casehub", "blog-mdproctor"):
            blog_filenames.add(Path(e["path"]).name)
    result = []
    skipped = 0
    for e in entries:
        if e["source"] == "project" and "blog/" in e["path"]:
            if Path(e["path"]).name in blog_filenames:
                skipped += 1
                continue
        result.append(e)
    if skipped:
        print(f"  Dedup: skipped {skipped} workspace blog entries (blog-site version exists)")
    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Scan CaseHub repos for docs inventory")
    parser.add_argument("--slot", required=True, help="Path to slot directory (e.g. slots/207)")
    parser.add_argument("--canonical", default=None, help="Path to canonical casehub dir (default: slot parent)")
    parser.add_argument("--output", default=None, help="Output path (default: canonical parent/docs/audit/docs-inventory.yaml)")
    args = parser.parse_args()

    slot = Path(args.slot).resolve()
    canonical = Path(args.canonical).resolve() if args.canonical else slot.parent.parent
    mdproctor = canonical.parent

    all_entries = []

    print("Scanning product repos...", flush=True)
    for name in PRODUCT_REPOS:
        entries = scan_product_repo(name, slot, canonical)
        if entries:
            print(f"  {name}: {len(entries)} files", flush=True)
        all_entries.extend(entries)

    print("Scanning workspace repos...", flush=True)
    for name in PRODUCT_REPOS:
        entries = scan_workspace_repo(name, slot)
        if entries:
            print(f"  {name} (workspace): {len(entries)} files", flush=True)
        all_entries.extend(entries)

    print("Scanning parent...", flush=True)
    entries = scan_parent(slot, canonical)
    print(f"  parent: {len(entries)} files", flush=True)
    all_entries.extend(entries)

    print("Scanning blog sites...", flush=True)
    entries = scan_blog_site(
        "casehubio.github.io", "blog-casehub",
        ["_articles/*.md"],
        [slot / "casehubio.github.io", canonical / "casehubio.github.io"])
    print(f"  casehubio.github.io: {len(entries)} files", flush=True)
    all_entries.extend(entries)

    entries = scan_blog_site(
        "mdproctor.github.io", "blog-mdproctor",
        ["_articles/*.md", "_posts/*.md"],
        [mdproctor / "mdproctor.github.io"])
    print(f"  mdproctor.github.io: {len(entries)} files", flush=True)
    all_entries.extend(entries)

    print("Deduplicating...", flush=True)
    all_entries = dedup(all_entries)
    all_entries.sort(key=lambda e: (e["repo"], e["path"]))

    output = {
        "audit_status": [],
        "entries": all_entries,
    }

    out_path = Path(args.output) if args.output else canonical / "parent" / "docs" / "audit" / "docs-inventory.yaml"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w") as f:
        yaml.dump(output, f, default_flow_style=False, sort_keys=False,
                  allow_unicode=True, width=120)

    repo_counts = {}
    for e in all_entries:
        repo_counts[e["repo"]] = repo_counts.get(e["repo"], 0) + 1

    print(f"\nWritten {len(all_entries)} entries across {len(repo_counts)} repos to {out_path}", flush=True)


if __name__ == "__main__":
    main()
