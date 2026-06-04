---
id: PP-20260604-c0a86d
title: "MCP tool methods must catch Exception broadly and return 'Failed: ...' — never propagate"
type: rule
scope: platform
applies_to: "Any @Tool-annotated method on a Quarkus MCP server exposed to LLM agents — casehub-connectors-mcp, casehub-qhorus (unless using @WrapBusinessError), and any future MCP surface"
severity: important
refs:
  - https://quarkiverse.github.io/quarkiverse-docs/quarkus-mcp-server/dev/index.html
  - casehub/qhorus-dispatch-exception-sanitization.md
violation_hint: "catch (IllegalArgumentException e) — only catches known connector-not-registered failures; any unexpected RuntimeException (NullPointerException, IllegalStateException from misconfigured credentials) propagates uncaught and produces a raw stack trace visible to the LLM caller"
created: 2026-06-04
---

Quarkus MCP server tools are called by LLM agents. An uncaught exception propagates to the MCP framework, which surfaces it to the LLM as a raw stack trace — leaking internal paths, class names, and potentially credential configuration errors. MCP tool methods must catch `Exception` (not just expected subtypes like `IllegalArgumentException`) and return a `"Failed: <message>"` string. The catch block must log at warn level with the exception class name for debuggability, but must not rethrow. The alternative — `@WrapBusinessError` from quarkus-mcp-server — only wraps `IllegalArgumentException` and `IllegalStateException`; catch-all is required for true propagation safety.
