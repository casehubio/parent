# Notifications

> **Scope:** Subscription engine, notification delivery pipeline, digest batching
> **Audience:** All (app builders who want to send notifications; platform builders extending the pipeline)
> **Key repos:** casehub-platform (subscription engine), casehub-connectors (delivery channels)

## Overview

The notification system provides a full pipeline from event matching through to multi-channel delivery. Events flow from domain modules through the subscription engine, which fires matches to the notification dispatcher. The dispatcher orchestrates target resolution, suppression evaluation, template resolution, channel routing, and delivery — with support for both immediate delivery and digest batching.

## Architecture

```
Domain Event (CDI @Observes)
    ↓
SubscriptionEngine (pattern matching)
    ↓
SubscriptionMatched (async CDI event)
    ↓
NotificationDispatcher (pipeline orchestration)
    ↓
├─ TargetResolver → user set
├─ SuppressionEvaluator → mute/snooze/quiet hours
├─ TemplateResolver → NotificationInput
├─ ChannelRouter → delivery channels
└─ Per-channel delivery:
    ├─ Immediate delivery → NotificationDeliverer.deliver()
    ├─ Digest buffer → DigestBuffer.add()
    └─ Suppressed → skip

DigestFlushScheduler (periodic tick)
    ↓
DigestBuffer.drain() → NotificationDeliverer.deliverDigest()
```

## Key Components

### EventTypeRegistry

SPIs for event type discovery. Domain bridges (casehub-work, casehub-engine, etc.) self-register their `EventTypeDescriptor` records at startup.

```java
public interface EventTypeRegistry {
    void register(EventTypeDescriptor descriptor);
    Optional<EventTypeDescriptor> resolve(String eventType);
    Set<EventTypeDescriptor> discover();
}
```

**Implementations:**
- `InMemoryEventTypeRegistry` (subscriptions module) — ConcurrentHashMap-backed, used in production
- `NoOpEventTypeRegistry` (platform module) — fallback when subscriptions are not active

### SubscriptionEngine

Matches incoming CDI events against active subscriptions. When a subscription's pattern matches an event, fires a `SubscriptionMatched` event asynchronously.

**Contract:**
- Observes domain events via CDI `@Observes`
- Queries `SubscriptionStore` for active subscriptions matching the event type
- Evaluates subscription predicates against the event POJO
- Fires `SubscriptionMatched` via CDI `fireAsync()`

**Decoupling:** The engine knows nothing about notification delivery. It stops at pattern matching. `NotificationDispatcher` observes `SubscriptionMatched` and handles the rest.

### NotificationDispatcher

Core orchestration pipeline. Observes `SubscriptionMatched` events and coordinates the seven-step delivery flow.

**Pipeline (per match):**

1. **Resolve targets** — `TargetResolver.resolve(subscription, pojo)` returns a deduplicated set of user IDs
2. **Pre-fetch per-user data** — one query each for preferences and suppression state (no redundant lookups)
3. **Evaluate suppression** — `SuppressionEvaluator.evaluate(activeMutes, activeSnooze, quietHours, entityType, entityId, category)` returns suppression state
4. **If muted → skip** — drop the notification entirely (all channels)
5. **Resolve template** — `TemplateResolver.resolve(template, pojo, userId, tenancyId)` returns `NotificationInput` or null
6. **Route to channels** — `ChannelRouter.route(channelDefaults, suppressionResult, severity)` returns `Set<ResolvedChannel>`
7. **Per-channel delivery** — three paths:
   - **Immediate:** `channel.deliverer().deliver(notificationInput)`
   - **Digest:** `digestBuffer.add(key, notificationInput)` — buffered for periodic flush
   - **Suppressed:** skip

**Error isolation:** Each channel delivery is wrapped in a try/catch. A failure on one channel does not block others.

### DigestBuffer

Temporary buffer for notifications awaiting digest delivery. Thread-safe. Implementations must use atomic operations (e.g. `ConcurrentHashMap.remove()`) to avoid lost updates during concurrent add/drain.

```java
public interface DigestBuffer {
    void add(DigestBufferKey key, NotificationInput notification);
    List<NotificationInput> drain(DigestBufferKey key);
    Set<DigestBufferKey> pendingKeys();
    Optional<Instant> oldestPendingTimestamp(DigestBufferKey key);
    int pendingCount(DigestBufferKey key);
    Set<DigestBufferKey> pendingKeysForUser(String userId, String tenancyId);
}
```

**Key:** `DigestBufferKey(userId, tenancyId, channelId)` — one buffer per user-channel pair.

**Implementations:**
- `InMemoryDigestBuffer` (notification-dispatch module) — `ConcurrentHashMap<DigestBufferKey, CopyOnWriteArrayList<NotificationInput>>`
- `NoOpDigestBuffer` (platform module) — fallback when digest is not active

### DigestFlushScheduler

Periodic scheduler (`@Scheduled(every = "1m")`) that flushes pending digest buffers.

**Tick logic (per buffer key):**

1. Look up user's `DigestSchedule` from preferences
2. If schedule is null → orphan drain (user disabled digest since buffering)
3. Check if flush is due: `schedule.isFlushDue(oldest, lastFlush, now)`
4. Evaluate user-level suppression (snooze / quiet hours)
5. If snoozed or in quiet hours → defer flush
6. Otherwise: `drain()` the buffer and deliver via `deliverer.deliverDigest(summary)`

**Error isolation:** Per-key try/catch — a failure processing one user's digest does not block others.

**Orphan handling:** If a user disables digest after items are buffered, the next tick flushes immediately (orphan drain) to avoid unbounded accumulation.

### DigestSchedule

Sealed interface with three schedule types:

- **`Immediate`** — flush on every tick (effectively immediate delivery but via the digest path)
- **`Periodic`** — flush every N seconds: `isFlushDue() = (now - lastFlush) >= period`
- **`WeeklyAt`** — flush at specific weekday + time: `isFlushDue() = next occurrence has passed since lastFlush`

**Example:**
```java
DigestSchedule.weeklyAt(DayOfWeek.MONDAY, LocalTime.of(9, 0), ZoneId.of("America/New_York"))
```

### NotificationDeliverer

SPI for channel-specific delivery. Each connector (email, SMS, Slack, webhook) implements this interface.

```java
public interface NotificationDeliverer {
    DeliveryResult deliver(NotificationInput notification);
    DeliveryResult deliverDigest(DigestSummary summary);
}
```

**Lookup:** `DeliveryChannelRegistry.resolveDeliverer(channelId)` returns the deliverer for a given channel. If no deliverer is registered, the notification is dropped with a warning.

### TargetResolver

Converts a subscription's `NotificationTarget` into a set of user IDs.

**Supported target types:**
- **USER** — single user ID
- **GROUP** — all users with a given role/group in the tenancy (via `GroupMembershipProvider`)
- **EVENT_FIELD** — resolve from a field in the event POJO (e.g. `assignee`, `createdBy`)
- **ENTITY_WATCHERS** — all users watching a specific entity (via `EntityWatcherProvider` SPI). `target.id()` is the entity type override (blank = use `template.entityType()`). Application-tier implementations provide the watcher tracking; `NoOpEntityWatcherProvider @DefaultBean` returns empty with WARN log.

**Deduplication:** Returns a `Set<String>` — if multiple rules resolve to the same user, they deliver once.

### SuppressionEvaluator

Pure function over pre-fetched suppression data. Evaluates mute rules, snooze state, and quiet hours.

**Contract:**
```java
SuppressionResult evaluate(
    Set<EntityMute> activeMutes,
    Optional<SnoozeState> activeSnooze,
    @Nullable QuietHours quietHours,
    String entityType,
    String entityId,
    String category)
```

**Result:**
- `isMuted()` — entity-level or category-level mute is active → drop entirely
- `isSnoozed()` — user has snoozed all notifications → defer digest flush
- `quietHoursActive()` — current time is in quiet hours → defer digest flush

**No I/O:** The evaluator is a pure function. All lookups happen before invocation (in `NotificationDispatcher`). All methods accept `Instant now` as a parameter for deterministic testing and consistent time evaluation across checks.

**Store-authoritative expiry:** The evaluator does NOT re-filter mute rules by expiry. The store layer (`InMemorySuppressionStore`, `JpaSuppressionStore`) is the single authority for mute expiry — it evicts/filters expired rules at query time. The evaluator trusts the list it receives.

## Delivery Paths

### Immediate Delivery

Channel is configured for immediate delivery, suppression check passes → call `deliverer.deliver(notificationInput)` synchronously.

**Error handling:** Try/catch per channel. Log failure, continue to next channel.

### Digest Delivery

Channel is configured for digest (user preference: `digestSchedule != null`) → add to `DigestBuffer`.

**Flush conditions:**
- Schedule's `isFlushDue()` returns true
- AND user is not snoozed
- AND not in quiet hours

**Flush mechanics:**
- `DigestFlushScheduler` drains the buffer: `List<NotificationInput> items = digestBuffer.drain(key)`
- Constructs `DigestSummary(userId, tenancyId, channelId, items, periodStart, periodEnd, groupBy)`
- Calls `deliverer.deliverDigest(summary)`
- Records `lastFlushTimes.put(key, now)` on success

### Suppressed Delivery

Channel is returned by `ChannelRouter` with `suppressed = true` → skip silently. Used when a channel is enabled but the current suppression state blocks delivery.

### Quiet Hours → Digest Integration

`QuietHoursAction` controls what happens to external notifications during quiet hours:

- **`SUPPRESS` (default):** Drop external notifications during quiet hours (pre-existing behavior)
- **`BUFFER_FOR_DIGEST`:** Route to digest buffer instead of dropping — even URGENT notifications. Requires at least one channel with a digest schedule; channels without a schedule are still suppressed (WARN logged).

**Transition flush:** When `BUFFER_FOR_DIGEST` defers a flush during quiet hours, `DigestFlushScheduler` tracks the key. On the next tick after quiet hours end, it flushes immediately regardless of the normal digest schedule. Guard chain: quiet hours check (no DB hit) → schedule gate (deferred overrides) → snooze check (DB only when flush imminent) → flush.

### Digest Grouping

`DigestGroupBy` enum (`FLAT`, `CATEGORY`, `ENTITY`) is a user preference on `ChannelPreference`. Carried through `DigestSummary.groupBy()` to deliverers, which use it to decide how to present the batch. No platform-level grouping logic — deliverers decide rendering.

## Stores

### SubscriptionStore

Persistence for subscriptions. Two variants:

- **Blocking:** `SubscriptionStore` (platform-api)
- **Reactive:** `ReactiveSubscriptionStore` (platform-api)

**Operations:**
- `create(SubscriptionInput)` → `Subscription`
- `update(String id, SubscriptionUpdate)` → `Subscription`
- `delete(String id)`
- `findById(String id)` → `Optional<Subscription>`
- `findByTenancy(String tenancyId, SubscriptionQuery)` → `SubscriptionPage`

**Events:** Fires `SubscriptionCreated`, `SubscriptionUpdated`, `SubscriptionDeleted` on mutation.

**Implementations:**
- `InMemorySubscriptionStore` / `InMemoryReactiveSubscriptionStore` (subscriptions-inmem module)
- JPA implementation (to be added)

### NotificationStore

Persistence for sent notifications (audit trail).

**Operations:**
- `create(NotificationInput)` → `Notification`
- `findById(String id)` → `Optional<Notification>`
- `findByUser(String userId, String tenancyId, NotificationQuery)` → `NotificationPage`
- `markRead(String id)` → `Notification`
- `markAllRead(String userId, String tenancyId)`

**Implementations:**
- JPA implementation (notifications module)
- In-memory fallback (platform module)

### NotificationPreferenceStore

Per-user notification preferences.

```java
public interface NotificationPreferenceStore {
    Optional<NotificationPreferences> get(String userId, String tenancyId);
    NotificationPreferences update(String userId, String tenancyId, NotificationPreferenceUpdate update);
}
```

**Preferences include:**
- `channelDefaults` — per-channel delivery settings (enabled/disabled, digest schedule)
- `quietHours` — daily time range when notifications are deferred

### SuppressionStore

Mute and snooze state.

**Operations:**
- `activeMutes(String userId, String tenancyId)` → `Set<EntityMute>` — entity-specific or category-specific mutes
- `activeSnooze(String userId, String tenancyId)` → `Optional<SnoozeState>` — global snooze (until timestamp)

**Mute types:**
- **Entity mute:** `(entityType="case", entityId="CASE-123")` — mute all notifications for this specific case
- **Category mute:** `(category="low_priority")` — mute all notifications in this category

## Configuration

### Tick Interval

Digest flush scheduler tick rate (default: 1 minute):

```properties
casehub.notification.digest.tick-interval=1m
```

### Channel Registration

Connectors register deliverers at startup via CDI:

```java
@ApplicationScoped
public class EmailDeliverer implements NotificationDeliverer {
    @Inject
    DeliveryChannelRegistry registry;

    @PostConstruct
    void register() {
        registry.register("email", this);
    }
}
```

## Extension Points

### Custom Suppression Rules

Extend `SuppressionEvaluator` or wrap it with a decorator to add domain-specific suppression logic.

### Custom Target Resolution

Implement `EntityWatcherProvider` SPI to provide entity-watcher expansion for `ENTITY_WATCHERS` targets. Application-tier implementations track who is watching what (cases, projects, work items). `NoOpEntityWatcherProvider @DefaultBean` returns empty — no watcher tracking without an implementation.

### Custom Digest Grouping

`DigestSummary` includes a `groupBy` field (`DigestGroupBy` enum: FLAT, CATEGORY, ENTITY). Deliverers use this to decide how to present the batch — section headers by category, grouped by entity, or flat chronological list.

### Custom Schedule Types

Extend `DigestSchedule` with new sealed subtypes (e.g. `BiWeeklyAt`, `MonthEnd`).

## Testing

### Contract Tests

- `SubscriptionStoreContractTest` — JUnit 5 `@TestTemplate` for all `SubscriptionStore` implementations
- `NotificationStoreContractTest` — JUnit 5 `@TestTemplate` for all `NotificationStore` implementations
- `NotificationDelivererContractTest` — JUnit 5 `@TestTemplate` for all `NotificationDeliverer` implementations

### Unit Tests

- `NotificationDispatcherTest` — mocked pipeline with capturing stubs for each collaborator
- `DigestFlushSchedulerTest` — tick scenarios (flush due, deferred, orphan drain)
- `InMemoryDigestBufferTest` — concurrent add/drain safety

## See Also

- [Connectors](https://github.com/casehubio/connectors) — delivery channel implementations (email, SMS, Slack)
- [Platform Preferences](https://github.com/casehubio/platform) — user preference store
