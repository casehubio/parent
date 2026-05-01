#!/usr/bin/env bats
# incremental-build-decision.bats
#
# Tests for scripts/incremental-build-decision.sh
#
# Prereq: brew install bats-core
# Run:    bats scripts/tests/incremental-build-decision.bats

SCRIPT="$(dirname "$BATS_TEST_FILENAME")/../incremental-build-decision.sh"

# ── Unit tests: decision logic in isolation ───────────────────────────────────

@test "U1: previous-sha=none → BUILD (first run)" {
  run "$SCRIPT" --module ledger --current-sha abc --previous-sha none
  [ "$status" -eq 0 ]
  [ "$output" = "BUILD" ]
}

@test "U2: own SHA changed → BUILD" {
  run "$SCRIPT" --module ledger --current-sha new --previous-sha old
  [ "$status" -eq 0 ]
  [ "$output" = "BUILD" ]
}

@test "U3: own SHA unchanged, no deps → SKIP" {
  run "$SCRIPT" --module ledger --current-sha abc --previous-sha abc
  [ "$status" -eq 0 ]
  [ "$output" = "SKIP" ]
}

@test "U4: own SHA unchanged, one dep changed → TEST" {
  run "$SCRIPT" --module work \
    --current-sha abc --previous-sha abc \
    --dep ledger:new:old
  [ "$status" -eq 0 ]
  [ "$output" = "TEST" ]
}

@test "U5: own SHA unchanged, multiple deps, one changed → TEST" {
  run "$SCRIPT" --module work \
    --current-sha abc --previous-sha abc \
    --dep ledger:same:same \
    --dep connectors:new:old
  [ "$status" -eq 0 ]
  [ "$output" = "TEST" ]
}

@test "U6: own SHA AND dep both changed → BUILD (own takes precedence)" {
  run "$SCRIPT" --module work \
    --current-sha new --previous-sha old \
    --dep ledger:new:old
  [ "$status" -eq 0 ]
  [ "$output" = "BUILD" ]
}

@test "U7: all SHAs identical → SKIP" {
  run "$SCRIPT" --module work \
    --current-sha abc --previous-sha abc \
    --dep ledger:xyz:xyz \
    --dep connectors:xyz:xyz
  [ "$status" -eq 0 ]
  [ "$output" = "SKIP" ]
}

@test "U8: two deps both changed → TEST" {
  run "$SCRIPT" --module claudony \
    --current-sha abc --previous-sha abc \
    --dep ledger:new:old \
    --dep work:new:old \
    --dep qhorus:new:old
  [ "$status" -eq 0 ]
  [ "$output" = "TEST" ]
}

# ── Integration scenarios: full module graph decisions ────────────────────────
#
# SHAs used in scenarios:
#   "same"    = SHA unchanged between runs
#   "new/old" = SHA changed (new is current, old is previous)
#
# Dependency graph:
#   ledger:     []
#   connectors: []
#   work:       [ledger, connectors]
#   qhorus:     [ledger, work]
#   engine:     [ledger, work]
#   claudony:   [ledger, work, qhorus]

# I1: Nothing changed → all SKIP
@test "I1: nothing changed — ledger=SKIP" {
  run "$SCRIPT" --module ledger --current-sha same --previous-sha same
  [ "$output" = "SKIP" ]
}
@test "I1: nothing changed — connectors=SKIP" {
  run "$SCRIPT" --module connectors --current-sha same --previous-sha same
  [ "$output" = "SKIP" ]
}
@test "I1: nothing changed — work=SKIP" {
  run "$SCRIPT" --module work --current-sha same --previous-sha same \
    --dep ledger:same:same --dep connectors:same:same
  [ "$output" = "SKIP" ]
}
@test "I1: nothing changed — qhorus=SKIP" {
  run "$SCRIPT" --module qhorus --current-sha same --previous-sha same \
    --dep ledger:same:same --dep work:same:same
  [ "$output" = "SKIP" ]
}
@test "I1: nothing changed — engine=SKIP" {
  run "$SCRIPT" --module engine --current-sha same --previous-sha same \
    --dep ledger:same:same --dep work:same:same
  [ "$output" = "SKIP" ]
}
@test "I1: nothing changed — claudony=SKIP" {
  run "$SCRIPT" --module claudony --current-sha same --previous-sha same \
    --dep ledger:same:same --dep work:same:same --dep qhorus:same:same
  [ "$output" = "SKIP" ]
}

# I2: Only ledger changed → ledger=BUILD, connectors=SKIP, work=TEST, qhorus=TEST, engine=TEST, claudony=TEST
@test "I2: only ledger changed — ledger=BUILD" {
  run "$SCRIPT" --module ledger --current-sha new --previous-sha old
  [ "$output" = "BUILD" ]
}
@test "I2: only ledger changed — connectors=SKIP" {
  run "$SCRIPT" --module connectors --current-sha same --previous-sha same
  [ "$output" = "SKIP" ]
}
@test "I2: only ledger changed — work=TEST" {
  run "$SCRIPT" --module work --current-sha same --previous-sha same \
    --dep ledger:new:old --dep connectors:same:same
  [ "$output" = "TEST" ]
}
@test "I2: only ledger changed — qhorus=TEST" {
  run "$SCRIPT" --module qhorus --current-sha same --previous-sha same \
    --dep ledger:new:old --dep work:same:same
  [ "$output" = "TEST" ]
}
@test "I2: only ledger changed — engine=TEST" {
  run "$SCRIPT" --module engine --current-sha same --previous-sha same \
    --dep ledger:new:old --dep work:same:same
  [ "$output" = "TEST" ]
}
@test "I2: only ledger changed — claudony=TEST" {
  run "$SCRIPT" --module claudony --current-sha same --previous-sha same \
    --dep ledger:new:old --dep work:same:same --dep qhorus:same:same
  [ "$output" = "TEST" ]
}

# I3: Only connectors changed → connectors=BUILD, ledger=SKIP, work=TEST, qhorus=SKIP, engine=SKIP, claudony=SKIP
@test "I3: only connectors changed — connectors=BUILD" {
  run "$SCRIPT" --module connectors --current-sha new --previous-sha old
  [ "$output" = "BUILD" ]
}
@test "I3: only connectors changed — ledger=SKIP" {
  run "$SCRIPT" --module ledger --current-sha same --previous-sha same
  [ "$output" = "SKIP" ]
}
@test "I3: only connectors changed — work=TEST" {
  run "$SCRIPT" --module work --current-sha same --previous-sha same \
    --dep ledger:same:same --dep connectors:new:old
  [ "$output" = "TEST" ]
}
@test "I3: only connectors changed — qhorus=SKIP" {
  run "$SCRIPT" --module qhorus --current-sha same --previous-sha same \
    --dep ledger:same:same --dep work:same:same
  [ "$output" = "SKIP" ]
}
@test "I3: only connectors changed — engine=SKIP" {
  run "$SCRIPT" --module engine --current-sha same --previous-sha same \
    --dep ledger:same:same --dep work:same:same
  [ "$output" = "SKIP" ]
}
@test "I3: only connectors changed — claudony=SKIP" {
  run "$SCRIPT" --module claudony --current-sha same --previous-sha same \
    --dep ledger:same:same --dep work:same:same --dep qhorus:same:same
  [ "$output" = "SKIP" ]
}

# I4: Only work changed → work=BUILD, qhorus=TEST, engine=TEST, claudony=TEST, ledger=SKIP, connectors=SKIP
@test "I4: only work changed — work=BUILD" {
  run "$SCRIPT" --module work --current-sha new --previous-sha old \
    --dep ledger:same:same --dep connectors:same:same
  [ "$output" = "BUILD" ]
}
@test "I4: only work changed — qhorus=TEST" {
  run "$SCRIPT" --module qhorus --current-sha same --previous-sha same \
    --dep ledger:same:same --dep work:new:old
  [ "$output" = "TEST" ]
}
@test "I4: only work changed — engine=TEST" {
  run "$SCRIPT" --module engine --current-sha same --previous-sha same \
    --dep ledger:same:same --dep work:new:old
  [ "$output" = "TEST" ]
}
@test "I4: only work changed — claudony=TEST" {
  run "$SCRIPT" --module claudony --current-sha same --previous-sha same \
    --dep ledger:same:same --dep work:new:old --dep qhorus:same:same
  [ "$output" = "TEST" ]
}

# I5: Only qhorus changed → qhorus=BUILD, claudony=TEST, all others=SKIP
@test "I5: only qhorus changed — qhorus=BUILD" {
  run "$SCRIPT" --module qhorus --current-sha new --previous-sha old \
    --dep ledger:same:same --dep work:same:same
  [ "$output" = "BUILD" ]
}
@test "I5: only qhorus changed — claudony=TEST" {
  run "$SCRIPT" --module claudony --current-sha same --previous-sha same \
    --dep ledger:same:same --dep work:same:same --dep qhorus:new:old
  [ "$output" = "TEST" ]
}
@test "I5: only qhorus changed — engine=SKIP" {
  run "$SCRIPT" --module engine --current-sha same --previous-sha same \
    --dep ledger:same:same --dep work:same:same
  [ "$output" = "SKIP" ]
}

# I6: Only engine changed → engine=BUILD, claudony=SKIP (engine is not a dep of claudony)
@test "I6: only engine changed — engine=BUILD" {
  run "$SCRIPT" --module engine --current-sha new --previous-sha old \
    --dep ledger:same:same --dep work:same:same
  [ "$output" = "BUILD" ]
}
@test "I6: only engine changed — claudony=SKIP" {
  run "$SCRIPT" --module claudony --current-sha same --previous-sha same \
    --dep ledger:same:same --dep work:same:same --dep qhorus:same:same
  [ "$output" = "SKIP" ]
}

# I7: Only claudony changed → claudony=BUILD only
@test "I7: only claudony changed — claudony=BUILD" {
  run "$SCRIPT" --module claudony --current-sha new --previous-sha old \
    --dep ledger:same:same --dep work:same:same --dep qhorus:same:same
  [ "$output" = "BUILD" ]
}
@test "I7: only claudony changed — engine=SKIP" {
  run "$SCRIPT" --module engine --current-sha same --previous-sha same \
    --dep ledger:same:same --dep work:same:same
  [ "$output" = "SKIP" ]
}

# I8: Ledger + work both changed → ledger=BUILD, work=BUILD, qhorus=TEST, engine=TEST, claudony=TEST, connectors=SKIP
@test "I8: ledger+work changed — ledger=BUILD" {
  run "$SCRIPT" --module ledger --current-sha new --previous-sha old
  [ "$output" = "BUILD" ]
}
@test "I8: ledger+work changed — work=BUILD" {
  run "$SCRIPT" --module work --current-sha new --previous-sha old \
    --dep ledger:new:old --dep connectors:same:same
  [ "$output" = "BUILD" ]
}
@test "I8: ledger+work changed — connectors=SKIP" {
  run "$SCRIPT" --module connectors --current-sha same --previous-sha same
  [ "$output" = "SKIP" ]
}
@test "I8: ledger+work changed — qhorus=TEST" {
  run "$SCRIPT" --module qhorus --current-sha same --previous-sha same \
    --dep ledger:new:old --dep work:new:old
  [ "$output" = "TEST" ]
}
@test "I8: ledger+work changed — engine=TEST" {
  run "$SCRIPT" --module engine --current-sha same --previous-sha same \
    --dep ledger:new:old --dep work:new:old
  [ "$output" = "TEST" ]
}
@test "I8: ledger+work changed — claudony=TEST" {
  run "$SCRIPT" --module claudony --current-sha same --previous-sha same \
    --dep ledger:new:old --dep work:new:old --dep qhorus:same:same
  [ "$output" = "TEST" ]
}

# I9: First run (all previous=none) → all BUILD
@test "I9: first run — ledger=BUILD" {
  run "$SCRIPT" --module ledger --current-sha abc --previous-sha none
  [ "$output" = "BUILD" ]
}
@test "I9: first run — connectors=BUILD" {
  run "$SCRIPT" --module connectors --current-sha abc --previous-sha none
  [ "$output" = "BUILD" ]
}
@test "I9: first run — work=BUILD" {
  run "$SCRIPT" --module work --current-sha abc --previous-sha none \
    --dep ledger:abc:none --dep connectors:abc:none
  [ "$output" = "BUILD" ]
}
@test "I9: first run — qhorus=BUILD" {
  run "$SCRIPT" --module qhorus --current-sha abc --previous-sha none \
    --dep ledger:abc:none --dep work:abc:none
  [ "$output" = "BUILD" ]
}
@test "I9: first run — engine=BUILD" {
  run "$SCRIPT" --module engine --current-sha abc --previous-sha none \
    --dep ledger:abc:none --dep work:abc:none
  [ "$output" = "BUILD" ]
}
@test "I9: first run — claudony=BUILD" {
  run "$SCRIPT" --module claudony --current-sha abc --previous-sha none \
    --dep ledger:abc:none --dep work:abc:none --dep qhorus:abc:none
  [ "$output" = "BUILD" ]
}
