#!/usr/bin/env python3
"""
Detect circular repo entry across casehub Maven repositories.

Reads repo list + declared deps from build/modules-*.csv.
Scans pom.xml to discover actual cross-repo dependencies.
Detects cycles that prevent clean independent builds.
Flags actual deps missing from the CSV.

Usage:  python3 check_repo_cycles.py <casehub-root>
Exit:   0 = clean, 1 = cycle or undeclared dep, 2 = usage error
"""
import csv
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict, deque
from pathlib import Path

NS = '{http://maven.apache.org/POM/4.0.0}'
GROUP = 'io.casehub'
SKIP_PARTS = frozenset({'target', '.git', '.claude', 'node_modules', '.mvn', 'src'})


def load_csv_graph(parent: Path) -> dict[str, set[str]]:
    declared: dict[str, set[str]] = {}
    for csv_path in sorted(parent.glob('build/modules-*.csv')):
        with open(csv_path) as f:
            for row in csv.reader(f):
                if not row or row[0].startswith('#'):
                    continue
                name = row[0].strip()
                deps = {d.strip() for d in row[1:] if d.strip()}
                declared[name] = deps
    return declared


def discover_repos(root: Path, names: list[str]) -> dict[str, Path]:
    repos = {}
    for name in names:
        p = root / name
        if p.is_dir() and (p / 'pom.xml').exists():
            repos[name] = p
    if 'parent' not in repos:
        p = root / 'parent'
        if p.is_dir():
            repos['parent'] = p
    return repos


def _is_module_pom(pom: Path, repo_root: Path) -> bool:
    for part in pom.relative_to(repo_root).parts[:-1]:
        if part in SKIP_PARTS:
            return False
    return True


def scan_artifacts(repo: Path) -> set[str]:
    arts: set[str] = set()
    for pom in repo.rglob('pom.xml'):
        if not _is_module_pom(pom, repo):
            continue
        try:
            r = ET.parse(pom).getroot()
        except ET.ParseError:
            continue
        aid = r.find(f'{NS}artifactId')
        if aid is not None and aid.text:
            arts.add(aid.text.strip())
    return arts


def scan_deps(repo: Path) -> list[tuple[str, str, str]]:
    results: list[tuple[str, str, str]] = []
    xpaths = [
        f'{NS}dependencies/{NS}dependency',
        f'{NS}profiles/{NS}profile/{NS}dependencies/{NS}dependency',
    ]
    for pom in repo.rglob('pom.xml'):
        if not _is_module_pom(pom, repo):
            continue
        try:
            r = ET.parse(pom).getroot()
        except ET.ParseError:
            continue
        mod_el = r.find(f'{NS}artifactId')
        if mod_el is None or not mod_el.text:
            continue
        mod = mod_el.text.strip()
        for xp in xpaths:
            for dep in r.findall(xp):
                gid = dep.find(f'{NS}groupId')
                aid = dep.find(f'{NS}artifactId')
                scp = dep.find(f'{NS}scope')
                if gid is None or aid is None:
                    continue
                g = (gid.text or '').strip()
                a = (aid.text or '').strip()
                s = (scp.text or 'compile').strip() if scp is not None else 'compile'
                if g == GROUP and a:
                    results.append((mod, a, s))
    return results


def find_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    cycles: list[list[str]] = []
    visited: set[str] = set()
    stack: set[str] = set()

    def dfs(node: str, path: list[str]) -> None:
        visited.add(node)
        stack.add(node)
        for nb in sorted(graph.get(node, ())):
            if nb not in visited:
                dfs(nb, path + [nb])
            elif nb in stack:
                cycles.append(path[path.index(nb):] + [nb])
        stack.discard(node)

    for n in sorted(graph):
        if n not in visited:
            dfs(n, [n])
    return cycles


def topo_sort(graph: dict[str, set[str]], nodes: set[str]) -> list[str] | None:
    indeg: dict[str, int] = {n: 0 for n in nodes}
    for tgts in graph.values():
        for t in tgts:
            if t in indeg:
                indeg[t] += 1
    q = deque(sorted(n for n, d in indeg.items() if d == 0))
    order: list[str] = []
    while q:
        n = q.popleft()
        order.append(n)
        for nb in sorted(graph.get(n, ())):
            if nb in indeg:
                indeg[nb] -= 1
                if indeg[nb] == 0:
                    q.append(nb)
    return order if len(order) == len(nodes) else None


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: check_repo_cycles.py <casehub-root>', file=sys.stderr)
        return 2

    root = Path(sys.argv[1]).resolve()
    parent = root / 'parent'
    if not parent.is_dir():
        print(f'parent repo not found at {parent}', file=sys.stderr)
        return 2

    csv_graph = load_csv_graph(parent)
    repos = discover_repos(root, list(csv_graph.keys()))

    art_to_repo: dict[str, str] = {}
    for name, path in repos.items():
        for a in scan_artifacts(path):
            art_to_repo[a] = name

    print(f'Scanned {len(repos)} repos, {len(art_to_repo)} artifacts\n')

    evidence: dict[tuple[str, str], list[tuple[str, str, str]]] = defaultdict(list)
    actual: dict[str, set[str]] = defaultdict(set)

    for rname, rpath in repos.items():
        for mod, dep_aid, scope in scan_deps(rpath):
            dep_repo = art_to_repo.get(dep_aid)
            if dep_repo and dep_repo != rname:
                evidence[(rname, dep_repo)].append((mod, dep_aid, scope))
                actual[rname].add(dep_repo)

    print('Inter-repo dependencies (from pom.xml):')
    for r in sorted(actual):
        print(f'  {r} → {", ".join(sorted(actual[r]))}')
    print()

    problems = False

    undeclared = []
    for r in sorted(actual):
        declared = csv_graph.get(r, set())
        for dep in sorted(actual[r] - declared):
            for mod, art, scope in evidence[(r, dep)]:
                undeclared.append((r, mod, dep, art, scope))
    if undeclared:
        problems = True
        print('Undeclared cross-repo dependencies (missing from modules-*.csv):')
        for r, mod, dep, art, scope in undeclared:
            print(f'  {r}/{mod} → {dep}/{art} ({scope})')
        print()

    cycles = find_cycles(dict(actual))
    seen: set[frozenset[tuple[str, str]]] = set()
    unique = []
    for c in cycles:
        key = frozenset(zip(c, c[1:]))
        if key not in seen:
            seen.add(key)
            unique.append(c)

    if unique:
        problems = True
        print(f'✗ {len(unique)} circular repo entry chain(s):\n')
        for cyc in unique:
            print(f'  CYCLE: {" → ".join(cyc)}\n')
            for i in range(len(cyc) - 1):
                for mod, art, scope in evidence[(cyc[i], cyc[i + 1])]:
                    print(f'    {cyc[i]}/{mod} → {art} ({scope})')
            print()
    else:
        order = topo_sort(dict(actual), set(repos))
        if order:
            print(f'Build order: {" → ".join(order)}')
        print('\n✓ No circular repo entries detected')

    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
