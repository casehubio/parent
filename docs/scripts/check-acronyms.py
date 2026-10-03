#!/usr/bin/env python3
"""Flag acronyms not expanded on first use per file.

Checks each brief page for uppercase sequences (2-4 letters) that
appear without a parenthetical expansion on first occurrence.

Usage:
    python3 docs/scripts/check-acronyms.py
"""

import re
import sys
from pathlib import Path

BRIEF = Path(__file__).resolve().parent.parent / "brief"

ACRONYM_RE = re.compile(r'\b([A-Z]{2,4})\b')
EXPANSION_RE = re.compile(r'[A-Z]{2,4}\s*\([A-Z][a-z]')

KNOWN_OK = {
    "AI", "API", "EU", "IT", "ID", "UK", "US", "CI", "CD",
    "PR", "OR", "IF", "NOT", "AND", "THE", "FOR", "ALL",
    "SVG", "PDF", "CSS", "HTML", "JSON", "YAML", "XML",
    "SQL", "JVM", "JPA", "URL", "HTTP", "REST", "TLS",
    "AWS", "GCP", "OK", "II", "IV",
}


def check_file(filepath):
    text = filepath.read_text()
    lines = text.splitlines()
    seen = {}
    issues = []

    for lineno, line in enumerate(lines, 1):
        if line.startswith("#") or line.startswith("|"):
            continue
        for m in ACRONYM_RE.finditer(line):
            acr = m.group(1)
            if acr in KNOWN_OK:
                continue
            if acr not in seen:
                start = max(0, m.start() - 1)
                end = min(len(line), m.end() + 30)
                context = line[start:end]
                has_expansion = bool(re.search(
                    rf'{acr}\s*\([A-Z][a-z]', context))
                seen[acr] = (lineno, has_expansion)
                if not has_expansion:
                    issues.append((lineno, acr))

    return issues


def main():
    md_files = sorted(BRIEF.glob("*.md"))
    total = 0

    for f in md_files:
        issues = check_file(f)
        if issues:
            print(f"\n{f.name}:")
            for lineno, acr in issues:
                print(f"  L{lineno}: {acr} — not expanded on first use")
                total += 1

    if total:
        print(f"\n{total} unexpanded acronym(s) found.")
    else:
        print(f"All acronyms expanded on first use across {len(md_files)} files.")


if __name__ == "__main__":
    main()
