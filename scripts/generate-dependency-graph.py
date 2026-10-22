"""Generate dependency-graph.json from Maven POM analysis across all CaseHub repos."""

import json
import os
import sys
import xml.etree.ElementTree as ET

REPOS = [
    'platform', 'worker', 'ledger', 'connectors', 'work', 'qhorus',
    'eidos', 'neocortex', 'engine', 'iot', 'ras', 'desiredstate',
    'agency', 'casehub-mosaic', 'claudony', 'openclaw', 'workers', 'ops',
    'pages', 'devtown', 'aml', 'clinical', 'life', 'drafthouse',
    'quarkmind', 'soc', 'fsitrading', 'chat-app', 'flow',
]

NS = {'m': 'http://maven.apache.org/POM/4.0.0'}


def extract_dependencies(pom_path: str) -> list[str]:
    """Extract casehub dependency artifactIds from a POM file."""
    try:
        tree = ET.parse(pom_path)
    except ET.ParseError:
        return []
    root = tree.getroot()
    deps = []
    for dep in root.findall('.//m:dependency', NS):
        group = dep.findtext('m:groupId', '', NS)
        artifact = dep.findtext('m:artifactId', '', NS)
        if group.startswith('io.casehub'):
            deps.append(artifact)
    return deps


def build_graph(repos_root: str) -> dict:
    """Build dependency graph from all repo POMs."""
    graph = {}
    for repo in REPOS:
        repo_dir = os.path.join(repos_root, repo)
        if not os.path.isdir(repo_dir):
            continue
        all_deps = set()
        for root, _, files in os.walk(repo_dir):
            if '.git' in root:
                continue
            for f in files:
                if f == 'pom.xml':
                    deps = extract_dependencies(os.path.join(root, f))
                    all_deps.update(deps)
        graph[f'casehub-{repo}'] = {
            'depends_on': sorted(all_deps),
            'depended_on_by': [],
        }

    for repo, data in graph.items():
        for dep in data['depends_on']:
            if dep in graph:
                graph[dep]['depended_on_by'].append(repo)

    return graph


if __name__ == '__main__':
    repos_root = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/claude/casehub')
    graph = build_graph(repos_root)
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'dependency-graph.json')
    with open(output_path, 'w') as f:
        json.dump(graph, f, indent=2)
        f.write('\n')
    print(f"Generated dependency graph: {len(graph)} repos, "
          f"{sum(len(d['depends_on']) for d in graph.values())} edges")
