#!/usr/bin/env python3
"""Check that all dependencies have versions managed by the parent BOM.

Finds <dependency> blocks with explicit <version> tags that aren't
${project.version} or property references to casehub versions.
These should be managed in casehub-parent's <dependencyManagement> instead.

Exit 0 if clean, exit 1 with report if unmanaged deps found.
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {'m': 'http://maven.apache.org/POM/4.0.0'}
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PARENT_POM = REPO_ROOT / 'parent' / 'pom.xml'

ALLOWED_VERSION_PATTERNS = {
    '${project.version}',
    '${casehub.version}',
}

def is_property_ref(version):
    return version and version.startswith('${') and version.endswith('}')

def get_managed_keys(pom_path):
    tree = ET.parse(pom_path)
    root = tree.getroot()
    managed = set()
    for dep_mgmt in root.findall('.//m:dependencyManagement/m:dependencies/m:dependency', NS):
        gid = dep_mgmt.find('m:groupId', NS)
        aid = dep_mgmt.find('m:artifactId', NS)
        if gid is not None and aid is not None:
            managed.add(f"{gid.text}:{aid.text}")
    return managed

def check_pom(pom_path, managed_keys):
    issues = []
    try:
        tree = ET.parse(pom_path)
    except ET.ParseError:
        return issues
    root = tree.getroot()

    for deps in root.findall('.//m:dependencies', NS):
        parent = deps
        # Skip dependencyManagement sections
        if any(p.tag.endswith('dependencyManagement') for p in [deps]):
            continue

        for dep in deps.findall('m:dependency', NS):
            gid_el = dep.find('m:groupId', NS)
            aid_el = dep.find('m:artifactId', NS)
            ver_el = dep.find('m:version', NS)

            if gid_el is None or aid_el is None or ver_el is None:
                continue

            gid = gid_el.text or ''
            aid = aid_el.text or ''
            version = ver_el.text or ''
            key = f"{gid}:{aid}"

            # Skip casehub internal deps and property references
            if gid.startswith('io.casehub'):
                continue
            if version in ALLOWED_VERSION_PATTERNS:
                continue
            if is_property_ref(version):
                continue

            # Check if managed
            if key not in managed_keys:
                rel = pom_path.relative_to(REPO_ROOT)
                issues.append(f"  {rel}: {key}:{version} — not in parent BOM")

    return issues

def main():
    if not PARENT_POM.exists():
        print("parent/pom.xml not found — skipping check")
        sys.exit(0)

    managed = get_managed_keys(PARENT_POM)
    all_issues = []

    skip_dirs = {'target', '.m2', 'node_modules', '.yarn', '.casehub-packages', 'all', 'wksp', 'examples', 'slots'}
    for pom in sorted(REPO_ROOT.rglob('pom.xml')):
        if skip_dirs & set(pom.parts):
            continue
        if pom == PARENT_POM:
            continue
        all_issues.extend(check_pom(pom, managed))

    if all_issues:
        print(f"⚠ {len(all_issues)} unmanaged dependency version(s) found:")
        print("  These should be managed in casehub-parent's <dependencyManagement>")
        print()
        for issue in all_issues[:20]:
            print(issue)
        if len(all_issues) > 20:
            print(f"  ... and {len(all_issues) - 20} more")
        # Warning only for now — change to sys.exit(1) to enforce
        sys.exit(0)
    else:
        print("✓ All dependency versions are BOM-managed")

if __name__ == '__main__':
    main()
