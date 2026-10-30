#!/usr/bin/env python3
"""Regenerate modules-core.csv and modules-applications.csv from actual POM dependencies.

Usage: python3 parent/build/sync-deps.py  (run from casehub-all root)

Scans all submodule directories for pom.xml files, extracts cross-repo
io.casehub dependencies, builds the dependency graph, and writes the CSVs.

Exit code 0 if CSVs are already up to date, 1 if changes were written.
"""
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # casehub-all root

CORE_REPOS = [
    "parent", "platform", "worker", "ledger", "connectors", "neocortex",
    "eidos", "desiredstate", "ras", "qhorus", "work", "engine", "pages",
    "agency", "casehub-langchain4j", "casehub-mosaic", "workers", "claudony",
    "ops", "iot", "chat-app", "drafthouse",
]

APP_REPOS = [
    "openclaw", "devtown", "aml", "clinical", "life",
    "soc", "fsitrading", "quarkmind", "scaffold",
]

ALL_REPOS = CORE_REPOS + APP_REPOS

# Longest-prefix-first mapping from artifactId prefix to repo name.
# Order matters: casehub-workers must match before casehub-worker.
PREFIX_MAP = [
    ("casehub-workers", "workers"),
    ("casehub-worker", "worker"),
    ("casehub-platform", "platform"),
    ("casehub-ledger", "ledger"),
    ("casehub-connectors", "connectors"),
    ("casehub-neocortex", "neocortex"),
    ("casehub-eidos", "eidos"),
    ("casehub-desiredstate", "desiredstate"),
    ("casehub-ras", "ras"),
    ("casehub-qhorus", "qhorus"),
    ("casehub-work", "work"),
    ("casehub-engine", "engine"),
    ("casehub-pages", "pages"),
    ("casehub-agency", "agency"),
    ("casehub-langchain4j", "casehub-langchain4j"),
    ("casehub-mosaic", "casehub-mosaic"),
    ("casehub-claudony", "claudony"),
    ("casehub-ops", "ops"),
    ("casehub-iot", "iot"),
    ("casehub-chat-app", "chat-app"),
    ("chat-app", "chat-app"),
    ("casehub-openclaw", "openclaw"),
    ("casehub-devtown", "devtown"),
    ("casehub-aml", "aml"),
    ("casehub-clinical", "clinical"),
    ("casehub-life", "life"),
    ("casehub-drafthouse", "drafthouse"),
    ("casehub-soc", "soc"),
    ("casehub-fsitrading", "fsitrading"),
    ("casehub-quarkmind", "quarkmind"),
    ("casehub-scaffold", "scaffold"),
    ("casehub-parent", "parent"),
    ("casehub-testing", "engine"),
    ("casehub-persistence", "engine"),
    ("casehub-spring-boot", "platform"),
]


def artifact_to_repo(artifact_id):
    for prefix, repo in PREFIX_MAP:
        if artifact_id.startswith(prefix):
            return repo
    return None


def find_pom_files(repo_dir):
    poms = []
    for dirpath, dirnames, filenames in os.walk(repo_dir):
        dirnames[:] = [d for d in dirnames if d != "target" and not d.startswith(".")]
        if "pom.xml" in filenames:
            poms.append(os.path.join(dirpath, "pom.xml"))
    return poms


def strip_dep_management(content):
    """Remove <dependencyManagement> sections so we only scan actual <dependencies>."""
    return re.sub(
        r"<dependencyManagement>.*?</dependencyManagement>",
        "",
        content,
        flags=re.DOTALL,
    )


def extract_deps(repo_name):
    repo_dir = os.path.join(ROOT, repo_name)
    if not os.path.isdir(repo_dir):
        return set()

    # parent is the root BOM — no actual build dependencies on other repos
    if repo_name == "parent":
        return set()

    # platform has internal modules that depend on downstream repos (eidos-api,
    # neocortex-memory-api, pages-push). These are API-level deps within specific
    # platform sub-modules — they don't affect cross-repo build ordering because
    # the platform reactor handles module ordering internally. Excluding them
    # prevents a false cycle in the cross-repo dependency graph.
    PLATFORM_EXCLUDE = {"eidos", "neocortex", "pages"} if repo_name == "platform" else set()

    deps = set()
    for pom_path in find_pom_files(repo_dir):
        try:
            content = open(pom_path).read()
        except OSError:
            continue
        # Strip dependencyManagement to avoid false positives from managed versions
        content = strip_dep_management(content)
        # Parse dependencies with scope awareness
        for dep_block in re.finditer(
            r"<dependency>(.*?)</dependency>", content, re.DOTALL
        ):
            block = dep_block.group(1)
            aid_m = re.search(r"<artifactId>(casehub-[^<]+)</artifactId>", block)
            if not aid_m:
                continue
            # Skip test and provided scope — they don't affect build ordering
            scope_m = re.search(r"<scope>(test|provided)</scope>", block)
            if scope_m:
                continue
            dep_repo = artifact_to_repo(aid_m.group(1))
            if dep_repo and dep_repo != repo_name and dep_repo in ALL_REPOS:
                if dep_repo not in PLATFORM_EXCLUDE:
                    deps.add(dep_repo)
    return deps


def write_csv(path, repos, graph, header_extra=""):
    lines = [
        f"# name,dep1,dep2,...  (deps reflect actual pom.xml cross-repo dependencies as of 2026-10-30){header_extra}\n"
    ]
    for repo in repos:
        deps = sorted(graph.get(repo, []))
        if deps:
            lines.append(f"{repo},{','.join(deps)}\n")
        else:
            lines.append(f"{repo}\n")
    return "".join(lines)


def main():
    graph = {}
    for repo in ALL_REPOS:
        graph[repo] = sorted(extract_deps(repo))

    core_content = write_csv(None, CORE_REPOS, graph)
    apps_content = write_csv(None, APP_REPOS, graph)

    core_path = os.path.join(SCRIPT_DIR, "modules-core.csv")
    apps_path = os.path.join(SCRIPT_DIR, "modules-applications.csv")

    changed = False

    for path, content, label in [
        (core_path, core_content, "modules-core.csv"),
        (apps_path, apps_content, "modules-applications.csv"),
    ]:
        try:
            old = open(path).read()
        except FileNotFoundError:
            old = ""

        if old != content:
            changed = True
            # Show diff
            old_lines = old.strip().splitlines()
            new_lines = content.strip().splitlines()
            print(f"\n{'='*60}")
            print(f"  {label}: CHANGED")
            print(f"{'='*60}")
            old_set = set(old_lines)
            new_set = set(new_lines)
            for line in sorted(old_set - new_set):
                if not line.startswith("#"):
                    print(f"  - {line}")
            for line in sorted(new_set - old_set):
                if not line.startswith("#"):
                    print(f"  + {line}")

            with open(path, "w") as f:
                f.write(content)
            print(f"  Written: {path}")
        else:
            print(f"{label}: up to date")

    # Summary
    print(f"\nDependency graph: {len(ALL_REPOS)} repos")
    total_deps = sum(len(v) for v in graph.values())
    print(f"Total dependency edges: {total_deps}")

    if changed:
        print("\nCSVs updated. Commit the changes.")
        return 1
    else:
        print("\nNo changes needed.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
