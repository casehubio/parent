#!/usr/bin/env python3
"""
BOM drift detector — validates casehub-parent BOM against child repo reactors.

Checks that every library module declared in a child repo's reactor has a
corresponding entry in the parent BOM's <dependencyManagement>. Exits non-zero
if drift is found.

Usage:
  Local (reads from sibling clones):
    python3 scripts/bom-audit.py

  CI (fetches pom.xml from GitHub API):
    python3 scripts/bom-audit.py --github

Requires: GITHUB_TOKEN env var when using --github.
"""

import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

NS = {"m": "http://maven.apache.org/POM/4.0.0"}

ORG = "casehubio"

BUILD_REPOS = [
    "platform", "worker", "ledger", "work", "qhorus", "engine", "eidos",
    "connectors", "iot", "desiredstate", "ras", "openclaw", "claudony",
    "ops", "devtown", "workers", "life", "aml", "clinical", "soc",
    "fsitrading", "blocks", "neocortex", "quarkmind",
]

EXAMPLE_PATTERNS = ("example", "examples", "demo", "integration-test", "compat-test")


def is_example_module(artifact_id):
    lower = artifact_id.lower()
    return any(p in lower for p in EXAMPLE_PATTERNS)


def extract_bom_artifacts(bom_source):
    root = ET.parse(bom_source).getroot() if os.path.isfile(bom_source) else ET.fromstring(bom_source)
    artifacts = set()
    for dep in root.findall(".//m:dependencyManagement/m:dependencies/m:dependency", NS):
        gid = dep.find("m:groupId", NS)
        aid = dep.find("m:artifactId", NS)
        if gid is not None and aid is not None and gid.text == "io.casehub":
            artifacts.add(aid.text)
    return artifacts


def get_reactor_artifact_ids_local(repo_path):
    pom = os.path.join(repo_path, "pom.xml")
    if not os.path.exists(pom):
        return []
    tree = ET.parse(pom)
    root = tree.getroot()
    results = []
    for mod in root.findall(".//m:modules/m:module", NS):
        if mod.text:
            mod_pom = os.path.join(repo_path, mod.text, "pom.xml")
            if os.path.exists(mod_pom):
                mod_tree = ET.parse(mod_pom)
                aid = mod_tree.getroot().find("m:artifactId", NS)
                if aid is not None:
                    results.append(aid.text)
    return results


def fetch_github_file(repo, path):
    result = subprocess.run(
        ["gh", "api", f"repos/{ORG}/{repo}/contents/{path}",
         "--jq", ".content"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return None
    import base64
    return base64.b64decode(result.stdout.strip()).decode("utf-8")


def get_reactor_artifact_ids_github(repo):
    pom_content = fetch_github_file(repo, "pom.xml")
    if not pom_content:
        return []
    root = ET.fromstring(pom_content)
    results = []
    for mod in root.findall(".//m:modules/m:module", NS):
        if mod.text:
            mod_pom_content = fetch_github_file(repo, f"{mod.text}/pom.xml")
            if mod_pom_content:
                mod_root = ET.fromstring(mod_pom_content)
                aid = mod_root.find("m:artifactId", NS)
                if aid is not None:
                    results.append(aid.text)
    return results


def main():
    use_github = "--github" in sys.argv
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)

    bom_artifacts = extract_bom_artifacts(os.path.join(parent_dir, "pom.xml"))

    missing = {}
    total_missing = 0

    for repo in sorted(BUILD_REPOS):
        if use_github:
            reactor_aids = get_reactor_artifact_ids_github(repo)
        else:
            casehub_root = os.path.dirname(parent_dir)
            repo_path = os.path.join(casehub_root, repo)
            reactor_aids = get_reactor_artifact_ids_local(repo_path)

        repo_missing = []
        for aid in sorted(reactor_aids):
            if aid not in bom_artifacts and not is_example_module(aid):
                repo_missing.append(aid)

        if repo_missing:
            missing[repo] = repo_missing
            total_missing += len(repo_missing)

    if missing:
        print(f"BOM DRIFT DETECTED — {total_missing} library module(s) missing\n")
        for repo, aids in sorted(missing.items()):
            print(f"  {repo}/")
            for aid in aids:
                print(f"    + {aid}")
        print(f"\nAdd these to casehub-parent/pom.xml <dependencyManagement>.")
        sys.exit(1)
    else:
        print(f"BOM is in sync — {len(bom_artifacts)} artifacts, {len(BUILD_REPOS)} repos checked.")
        sys.exit(0)


if __name__ == "__main__":
    main()
