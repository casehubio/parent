# Convention: Quarkus Dev Mode Hot-Reload Breaks WebSocket Endpoint Registration

**Applies to:** All modules with WebSocket endpoints  
**Severity:** Important — WebSocket connections silently fail after hot-reload without restart

## Problem

Quarkus dev mode hot-reload re-registers most beans correctly, but WebSocket endpoint registration is not hot-reloaded. After any Java change that triggers a reload, existing WebSocket connections fail and new connections get `101 Switching Protocols` but receive no messages.

## Rule

After any Java commit in dev mode that triggers a reload, do a **full server restart** (Ctrl+C → restart), not just a hot-reload wait.
