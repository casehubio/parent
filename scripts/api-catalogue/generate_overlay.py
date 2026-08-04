#!/usr/bin/env python3
"""
Cross-repo SPI implementation overlay generator.

Scans aggregated API docs to discover interfaces, then scans repo source
trees to find implementations. Produces docs/api/cross-repo-implementations.md
with the implementation matrix.

Usage:
    python3 generate_overlay.py <parent-repo-root> <repo-dir-1> [<repo-dir-2> ...]

    parent-repo-root: path to the parent repo (reads docs/repos/*/api/)
    repo-dirs: paths to repo clones (scans src/main/java/ for implementations)
"""
import re
import sys
from pathlib import Path
from collections import defaultdict


def scan_api_docs(repos_dir: Path) -> set[str]:
    """Find all interface names from aggregated jmarkdoc output."""
    interfaces = set()
    for repo_dir in sorted(repos_dir.iterdir()):
        if not repo_dir.is_dir():
            continue
        api_dir = repo_dir / "api"
        if not api_dir.is_dir():
            continue
        for md_file in api_dir.rglob("*.md"):
            content = md_file.read_text()
            if "**Kind:** `interface`" in content:
                interfaces.add(md_file.stem)
    return interfaces


def scan_source_implementations(
    interfaces: set[str],
    repo_dirs: list[Path],
) -> dict[str, list[dict]]:
    """Grep repo source trees for classes implementing known interfaces."""
    implementations = defaultdict(list)
    pattern = re.compile(
        r'class\s+(\w+).*?\bimplements\b\s+.*?\b(' +
        '|'.join(re.escape(i) for i in interfaces) +
        r')\b'
    )

    for repo_dir in repo_dirs:
        repo_name = repo_dir.name
        src_dir = repo_dir / "src" / "main" / "java"
        if not src_dir.is_dir():
            for sub in repo_dir.iterdir():
                if sub.is_dir() and (sub / "src" / "main" / "java").is_dir():
                    _scan_src(sub / "src" / "main" / "java", sub.name, pattern, implementations)
            continue
        _scan_src(src_dir, repo_name, pattern, implementations)

    return dict(implementations)


def _scan_src(src_dir: Path, repo_name: str, pattern, implementations):
    """Scan a src/main/java directory for implementations."""
    for java_file in src_dir.rglob("*.java"):
        content = java_file.read_text(errors='replace')
        for match in pattern.finditer(content):
            class_name = match.group(1)
            interface_name = match.group(2)
            implementations[interface_name].append({
                "repo": repo_name,
                "class": class_name,
            })


def build_matrix(implementations: dict[str, list[dict]]) -> dict[str, list[dict]]:
    """Filter to SPIs with implementations in 2+ repos."""
    matrix = {}
    for interface_name, impls in sorted(implementations.items()):
        repos = {i["repo"] for i in impls}
        if len(repos) >= 2:
            matrix[interface_name] = sorted(impls, key=lambda i: (i["repo"], i["class"]))
    return matrix


def render_markdown(matrix: dict[str, list[dict]]) -> str:
    """Render the cross-repo implementation matrix as markdown."""
    lines = [
        "<!-- Generated — do not edit -->",
        "# Cross-Repo SPI Implementations",
        "",
        "SPIs with implementations across multiple repos. For each SPI:",
        "the interface and every implementation found across the platform.",
        "",
    ]

    if not matrix:
        lines.append("*No cross-repo SPI implementations found.*")
        return "\n".join(lines) + "\n"

    for interface_name in sorted(matrix.keys()):
        impls = matrix[interface_name]
        lines.append(f"## {interface_name}")
        lines.append("")
        lines.append("| Repo | Implementation |")
        lines.append("|------|---------------|")
        for impl in impls:
            lines.append(f"| {impl['repo']} | `{impl['class']}` |")
        lines.append("")

    return "\n".join(lines) + "\n"


def main():
    if len(sys.argv) < 3:
        print("Usage: generate_overlay.py <parent-repo-root> <repo-dir-1> [<repo-dir-2> ...]")
        sys.exit(1)

    root = Path(sys.argv[1])
    repo_dirs = [Path(d) for d in sys.argv[2:]]
    repos_dir = root / "docs" / "repos"

    if not repos_dir.is_dir():
        print(f"Error: {repos_dir} not found")
        sys.exit(1)

    interfaces = scan_api_docs(repos_dir)
    print(f"Found {len(interfaces)} interfaces in aggregated API docs")

    if not interfaces:
        print("No interfaces found — nothing to correlate")
        sys.exit(0)

    implementations = scan_source_implementations(interfaces, repo_dirs)
    matrix = build_matrix(implementations)
    markdown = render_markdown(matrix)

    output_dir = root / "docs" / "api"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "cross-repo-implementations.md"
    output_file.write_text(markdown)

    print(f"Generated {output_file} ({len(matrix)} cross-repo SPIs)")


if __name__ == "__main__":
    main()
