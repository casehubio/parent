---
id: PP-20260530-ffa77a
title: "Tmux pane state transitions in tests must use Await.until(), not Thread.sleep()"
type: rule
scope: repo
applies_to: "claudony-app; any @QuarkusTest that creates a tmux session and waits for a foreground command or state change"
severity: important
refs:
  - app/src/test/java/io/casehub/claudony/server/expiry/StatusAwareExpiryPolicyTest.java
violation_hint: "Thread.sleep(N) in a test that checks pane_current_command or tmux pane state after session creation — passes locally, fails under CI load"
created: 2026-05-30
---

tmux session startup is non-deterministic in duration — shell initialisation time varies with system load, profile scripts, and JVM test parallelism. Using `Thread.sleep()` to wait for a pane command to change produces tests that pass locally but fail under load. Use `Await.until(() -> <condition from tmux.displayMessage(...)>, Duration.ofSeconds(10), "<description>")` instead — polling with a bounded timeout rather than a fixed sleep. See `StatusAwareExpiryPolicyTest.neverExpiresWhenNonShellCommandRunning()` as the canonical pattern; `expiresAtShellPromptWhenLastActiveIsOld()` was fixed in this way (Closes #118 stabilisation).
