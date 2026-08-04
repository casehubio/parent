"""Tests for the cross-repo SPI implementation overlay generator."""
import tempfile
import textwrap
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api-catalogue'))
from generate_overlay import scan_api_docs, scan_source_implementations, build_matrix, render_markdown


def _create_api_docs(base, repo_name, types):
    """Create minimal jmarkdoc-style API docs for a repo."""
    api_dir = Path(base) / "docs" / "repos" / repo_name / "api" / "io" / "casehub"
    api_dir.mkdir(parents=True)
    for name, kind in types:
        (api_dir / f"{name}.md").write_text(
            f"# io.casehub.{name}\n\n"
            f"**Package:** `io.casehub`\n\n"
            f"**Kind:** `{kind}`\n"
        )


def _create_source(base, repo_name, filename, content):
    """Create a Java source file in a repo."""
    src_dir = Path(base) / repo_name / "src" / "main" / "java"
    src_dir.mkdir(parents=True, exist_ok=True)
    (src_dir / filename).write_text(content)


def test_scan_api_docs_finds_interfaces():
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_api_docs(tmpdir, "casehub-engine", [
            ("AgentRoutingStrategy", "interface"),
            ("CaseDefinition", "class"),
            ("WorkerProvisioner", "interface"),
        ])
        interfaces = scan_api_docs(Path(tmpdir) / "docs" / "repos")
        assert "AgentRoutingStrategy" in interfaces
        assert "WorkerProvisioner" in interfaces
        assert "CaseDefinition" not in interfaces


def test_scan_source_finds_implementations():
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_source(tmpdir, "blocks", "LlmStrategy.java", textwrap.dedent("""\
            package io.casehub.blocks;
            public class LlmStrategy implements AgentRoutingStrategy {
            }
        """))
        _create_source(tmpdir, "blocks", "CbrStrategy.java", textwrap.dedent("""\
            package io.casehub.blocks;
            public class CbrStrategy implements AgentRoutingStrategy {
            }
        """))
        _create_source(tmpdir, "engine", "DefaultStrategy.java", textwrap.dedent("""\
            package io.casehub.engine;
            public class DefaultStrategy implements AgentRoutingStrategy {
            }
        """))
        impls = scan_source_implementations(
            {"AgentRoutingStrategy"},
            [Path(tmpdir) / "blocks", Path(tmpdir) / "engine"],
        )
        assert len(impls["AgentRoutingStrategy"]) == 3


def test_build_matrix_filters_single_repo():
    impls = {
        "AgentRoutingStrategy": [
            {"repo": "blocks", "class": "LlmStrategy"},
            {"repo": "engine", "class": "DefaultStrategy"},
        ],
        "InternalSpi": [
            {"repo": "engine", "class": "OnlyImpl"},
        ],
    }
    matrix = build_matrix(impls)
    assert "AgentRoutingStrategy" in matrix
    assert "InternalSpi" not in matrix


def test_render_markdown_structure():
    matrix = {
        "AgentRoutingStrategy": [
            {"repo": "blocks", "class": "LlmStrategy"},
            {"repo": "engine", "class": "DefaultStrategy"},
        ],
    }
    md = render_markdown(matrix)
    assert "# Cross-Repo SPI Implementations" in md
    assert "## AgentRoutingStrategy" in md
    assert "| blocks | `LlmStrategy` |" in md
    assert "| engine | `DefaultStrategy` |" in md
    assert "<!-- Generated" in md


def test_ignores_test_classes():
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_source(tmpdir, "engine", "DefaultStrategy.java", textwrap.dedent("""\
            package io.casehub.engine;
            public class DefaultStrategy implements AgentRoutingStrategy {
            }
        """))
        test_dir = Path(tmpdir) / "engine" / "src" / "test" / "java"
        test_dir.mkdir(parents=True)
        (test_dir / "MockStrategy.java").write_text(textwrap.dedent("""\
            package io.casehub.engine;
            public class MockStrategy implements AgentRoutingStrategy {
            }
        """))
        impls = scan_source_implementations(
            {"AgentRoutingStrategy"},
            [Path(tmpdir) / "engine"],
        )
        assert len(impls["AgentRoutingStrategy"]) == 1
        assert impls["AgentRoutingStrategy"][0]["class"] == "DefaultStrategy"


def test_handles_implements_with_generics():
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_source(tmpdir, "neocortex", "SqliteCbrStore.java", textwrap.dedent("""\
            package io.casehub.neocortex;
            public class SqliteCbrStore implements CbrCaseMemoryStore<TypedFeatures> {
            }
        """))
        impls = scan_source_implementations(
            {"CbrCaseMemoryStore"},
            [Path(tmpdir) / "neocortex"],
        )
        assert len(impls["CbrCaseMemoryStore"]) == 1
