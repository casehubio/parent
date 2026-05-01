# Convention: BroadcastProcessor.onNext() Throws on No Subscribers — Catch and Discard

**Applies to:** All modules using Quarkus reactive broadcast streams  
**Severity:** Important — unhandled BackPressureFailure propagates up and fails the calling thread

## Problem

`BroadcastProcessor.onNext()` throws `BackPressureFailure` (an unchecked exception) when there are no active subscribers. It does NOT return null or ignore the call.

## Rule

Wrap `onNext()` calls in a try-catch that silently discards `BackPressureFailure`. This is expected behaviour when no subscribers are connected.

## Example

```java
try {
    processor.onNext(payload);
} catch (Exception e) {
    // BackPressureFailure — no subscribers connected, discard silently
    Log.debugf("No subscribers for %s broadcast", payload.getClass().getSimpleName());
}
```
