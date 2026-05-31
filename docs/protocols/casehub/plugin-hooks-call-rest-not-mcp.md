---
id: PP-20260531-43de8e
title: "Plugin hooks call Quarkus REST directly — MCP endpoint is LLM-facing only"
type: rule
scope: repo
applies_to: "casehub-openclaw plugin/ module; any extension adding plugin hooks"
severity: important
refs:
  - docs/specs/2026-05-31-epic7-skill-pack-design.md
  - docs/adr/0002-mcp-server-host-process.md
violation_hint: "Plugin hook (before_tool_call, agent_end, session_start) calling POST /mcp or adding mcp-client.ts"
created: 2026-05-31
---

The TypeScript plugin's lifecycle hooks (`before_tool_call`, `agent_end`, `session_start`) must call the Quarkus app's REST API directly — the same pattern used by `ChannelClient` for `GET /channel-context/{agentId}`. The `/mcp` endpoint is an LLM-facing protocol surface served via MCPorter: routing plugin hooks through it introduces a triple-hop (plugin → MCP protocol → Quarkus service) and misuses the MCP layer as internal middleware. Plugin hook calls are not LLM-sourced and must not traverse the MCP negotiation layer.
