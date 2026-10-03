#!/usr/bin/env python3
"""Enrich docs-inventory.yaml with structural semantic fields.

Classifies type and audience from file path patterns. Extracts topic
keywords from headings. Does NOT generate summaries (that requires
LLM content reading).

Usage:
    python3 docs/scripts/enrich-docs-inventory.py --inventory docs/audit/docs-inventory.yaml
"""

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml")
    sys.exit(1)

TYPE_RULES = [
    (r"consumer-guide\.md$", "guide", "consumer"),
    (r"contributor-guide\.md$", "guide", "contributor"),
    (r"ARC42STORIES\.MD$", "guide", "both"),
    (r"CLAUDE\.md$", "config", "contributor"),
    (r"DESIGN\.md$", "spec", "both"),
    (r"HANDOFF\.md$", "handoff", "internal"),
    (r"LAYER-LOG\.md$", "log", "internal"),
    (r"README\.md$", "readme", "both"),
    (r"MODULES\.md$", "index", "contributor"),
    (r"docs/adr/", "adr", "contributor"),
    (r"docs/specs/", "spec", "contributor"),
    (r"docs/guides/", "guide", "both"),
    (r"docs/research/", "research", "contributor"),
    (r"docs/blog/", "blog", "both"),
    (r"docs/plans/", "plan", "internal"),
    (r"docs/api/", "api", "consumer"),
    (r"specs/", "spec", "contributor"),
    (r"plans/", "plan", "internal"),
    (r"blog/", "blog", "both"),
    (r"_articles/", "blog", "both"),
    (r"_posts/", "blog", "both"),
    (r"_notes/", "blog", "internal"),
    (r"docs/audit/", "guide", "contributor"),
    (r"docs/brief/", "brief", "both"),
    (r"docs/platform/", "guide", "both"),
    (r"docs/integration/", "guide", "both"),
    (r"docs/slides/", "presentation", "both"),
    (r"docs/archive/", "archive", "internal"),
    (r"LEGAL\.md$", "legal", "both"),
    (r"LICENSE", "legal", "both"),
    (r"CHANGELOG", "log", "both"),
]

TOPIC_KEYWORDS = {
    "cdi": "CDI", "spi": "SPI", "routing": "routing",
    "tenant": "tenancy", "tenancy": "tenancy",
    "ledger": "audit", "audit": "audit", "merkle": "audit",
    "trust": "trust", "attestation": "trust",
    "cbr": "CBR", "case-based": "CBR",
    "rag": "RAG", "retrieval": "RAG",
    "worker": "workers", "dispatch": "workers",
    "yaml": "YAML", "dsl": "DSL",
    "mcp": "MCP", "tool": "MCP",
    "agent": "agents", "eidos": "agents",
    "qhorus": "communication", "speech act": "communication",
    "channel": "communication", "commitment": "communication",
    "case": "orchestration", "plan": "orchestration",
    "desired.state": "reconciliation", "reconcil": "reconciliation",
    "situation": "situational-awareness", "ganglion": "situational-awareness",
    "test": "testing", "junit": "testing",
    "gdpr": "privacy", "erasure": "privacy",
    "compliance": "compliance", "regulatory": "compliance",
    "notification": "notifications", "event": "events",
    "simulation": "simulation", "scenario": "simulation",
    "docker": "deployment", "container": "deployment",
    "flyway": "persistence", "hibernate": "persistence",
    "jpa": "persistence", "database": "persistence",
    "oidc": "auth", "authentication": "auth",
    "rest": "API", "graphql": "API", "endpoint": "API",
    "ui": "UI", "component": "UI", "panel": "UI",
    "spring": "spring", "quarkus": "quarkus",
    "neocortex": "AI", "inference": "AI", "onnx": "AI",
    "llm": "AI", "cognitive": "AI", "memory": "AI",
    "aml": "AML", "investigation": "AML",
    "clinical": "clinical", "trial": "clinical",
    "soc": "SOC", "incident": "SOC",
    "trading": "trading", "fsi": "trading",
    "iot": "IoT", "device": "IoT",
    "playbook": "playbooks", "yaml-core": "playbooks",
    "deliberation": "deliberation", "debate": "deliberation",
}


def classify_entry(entry):
    path = entry.get("path", "")
    for pattern, doc_type, audience in TYPE_RULES:
        if re.search(pattern, path, re.IGNORECASE):
            return doc_type, audience
    if path.endswith(".md"):
        return "doc", "both"
    return "unknown", "unknown"


def extract_topics(entry):
    headings = entry.get("headings", [])
    if not headings:
        return []
    heading_text = " ".join(h.get("text", "") for h in headings).lower()
    topics = set()
    for keyword, topic in TOPIC_KEYWORDS.items():
        if keyword in heading_text:
            topics.add(topic)
    return sorted(topics)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Enrich docs-inventory with semantic fields")
    parser.add_argument("--inventory", required=True, help="Path to docs-inventory.yaml")
    args = parser.parse_args()

    inventory = Path(args.inventory)
    print(f"Reading {inventory}...")
    with open(inventory) as f:
        data = yaml.safe_load(f)

    entries = data.get("entries", [])
    print(f"Processing {len(entries)} entries...")

    classified = 0
    topics_added = 0

    for entry in entries:
        doc_type, audience = classify_entry(entry)
        entry["type"] = doc_type
        entry["audience"] = audience
        classified += 1

        topics = extract_topics(entry)
        if topics:
            entry["topics"] = topics
            topics_added += 1

        entry["extraction_pct"] = 20

    print(f"Writing {inventory}...")
    with open(inventory, "w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, width=120, sort_keys=False)

    print(f"Done. {classified} entries classified, {topics_added} with topics.")


if __name__ == "__main__":
    main()
