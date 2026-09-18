#!/usr/bin/env python3
"""
Detect circular repo entry from Maven dependency:tree output.

Uses artifact-repo-map.csv (artifact→repo mapping) to classify every
io.casehub artifact in the dependency tree to its owning repo. Fails if
any artifact from THIS repo appears as a transitive dependency under an
artifact from a DIFFERENT repo — meaning circular repo entry.

Usage:
    mvn dependency:tree | python3 check_repo_cycle_from_tree.py <this-repo-name> <artifact-repo-map.csv>

Example:
    mvn dependency:tree | python3 check_repo_cycle_from_tree.py neocortex build/artifact-repo-map.csv

Exit: 0 = clean, 1 = cycle detected, 2 = usage error
"""
import csv
import re
import sys

GROUP = 'io.casehub'


def load_artifact_map(path: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    with open(path) as f:
        for row in csv.reader(f):
            if len(row) >= 2:
                mapping[row[0].strip()] = row[1].strip()
    return mapping


def main() -> int:
    if len(sys.argv) < 3:
        print('Usage: mvn dependency:tree | python3 check_repo_cycle_from_tree.py '
              '<this-repo-name> <artifact-repo-map.csv>', file=sys.stderr)
        return 2

    this_repo = sys.argv[1]
    art_to_repo = load_artifact_map(sys.argv[2])

    current_module: str | None = None
    path_repos: list[tuple[str, str]] = []
    depth_stack: list[int] = []
    cycles: list[tuple[str, list[tuple[str, str]]]] = []

    for line in sys.stdin:
        line = line.rstrip()

        module_match = re.match(r'.*--- dependency:tree.*@ (\S+) ---', line)
        if module_match:
            current_module = module_match.group(1)
            path_repos = []
            depth_stack = []
            continue

        m = re.search(r'[| \\+\-]+(\S+):(\S+):\S+:(\S+)', line)
        if not m:
            continue

        group, artifact, _ = m.groups()
        if group != GROUP:
            continue

        depth = len(line) - len(line.lstrip(' |\\+-'))

        while depth_stack and depth_stack[-1] >= depth:
            depth_stack.pop()
            if path_repos:
                path_repos.pop()

        repo = art_to_repo.get(artifact, '?')
        path_repos.append((artifact, repo))
        depth_stack.append(depth)

        if repo == this_repo and len(path_repos) > 1:
            first_external = next(
                (i for i, (_, r) in enumerate(path_repos) if r != this_repo),
                None)
            if first_external is not None:
                cycles.append(
                    (current_module or '?', list(path_repos[first_external:])))

    if not cycles:
        print(f'✓ No circular repo entry for {this_repo}')
        return 0

    seen: set[str] = set()
    print(f'\n✗ Circular repo entry detected for {this_repo}!\n')
    for module, path in cycles:
        chain = ' → '.join(f'{a} [{r}]' for a, r in path)
        key = f'{module}:{chain}'
        if key in seen:
            continue
        seen.add(key)
        print(f'  in {module}: {chain}')

    return 1


if __name__ == '__main__':
    sys.exit(main())
