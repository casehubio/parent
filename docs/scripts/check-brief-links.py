#!/usr/bin/env python3
"""Validate all internal links and image references in the brief.

Usage:
    python3 docs/scripts/check-brief-links.py
"""

import re
import sys
from pathlib import Path

BRIEF = Path(__file__).resolve().parent.parent / "brief"

MD_LINK = re.compile(r'\]\(([^)]+)\)')
IMG_LINK = re.compile(r'!\[[^\]]*\]\(([^)]+)\)')


def check_file(filepath):
    text = filepath.read_text()
    issues = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for m in MD_LINK.finditer(line):
            target = m.group(1)
            if target.startswith("http") or target.startswith("#"):
                continue
            resolved = (filepath.parent / target).resolve()
            if not resolved.exists():
                issues.append((lineno, "broken link", target))
    return issues


def main():
    md_files = sorted(BRIEF.glob("*.md"))
    total_issues = 0

    for f in md_files:
        issues = check_file(f)
        if issues:
            print(f"\n{f.name}:")
            for lineno, kind, target in issues:
                print(f"  L{lineno}: {kind} → {target}")
                total_issues += 1

    if total_issues:
        print(f"\n{total_issues} broken link(s) found.")
        sys.exit(1)
    else:
        print(f"All links valid across {len(md_files)} files.")


if __name__ == "__main__":
    main()
