# casehub-chat-app

> **Tier:** Integration
> **GitHub:** [casehubio/chat-app](https://github.com/casehubio/chat-app)

## Purpose

Chat workbench application — a runnable chat UI with SQLite-backed persistence, REST/WebSocket endpoints, and a casehub-pages frontend. Provides the app shell (workbench layout, WebSocket adapter, swipe gestures, JWT dev-auth) around `@casehubio/blocks-ui-channel-activity` components.

Migrated from `casehub-connectors/chat-demo` to separate the runnable application from the connector infrastructure library.

## Key Abstractions

- **QhorusWorkbench** — Lit element app shell with responsive layout (desktop/tablet/phone), dock strip, theme toggle
- **ChatDemoAdapter** — WebSocket protocol adapter: parses snapshot/append/replace/remove ops into typed arrays
- **SwipeController** — Lit reactive controller for edge-swipe drawer gestures
- **ChatResource** — JAX-RS REST endpoints for channels, messages, replies, reactions, members, presence
- **SqliteChatBackend** — SQLite ChatBackend implementation with HikariCP connection pooling
- **ChatWebSocket / ChatWebSocketBroadcaster** — WebSocket endpoint with dataset broadcast protocol

## Depends On

- `casehub-connectors` — chat-spi (ChatPlatform SPI, ChatBackend interface), chat-ref (reference implementation), connectors-core
- `casehub-pages` — pages-auth (JWT dev-auth), pages-runtime, pages-ui
- `casehub-blocks-ui` — channel-activity components (feed, nav, member panel, input, reactions, threading)

## Depended On By

None currently.

## Does NOT Do

- Does not define the ChatPlatform SPI — that stays in `casehub-connectors/chat-spi`
- Does not provide reusable UI components — those are in `casehub-blocks-ui/channel-activity`
- Does not provide production-grade persistence — SQLite is dev/demo only
- Does not send outbound messages to external platforms — that's the connectors' job

## Current State

Scaffold complete. Java backend (5 source files, 3 test files, 40 tests) and frontend app shell (workbench, adapter, swipe controller, auth, 79 tests) migrated from connectors/chat-demo.
