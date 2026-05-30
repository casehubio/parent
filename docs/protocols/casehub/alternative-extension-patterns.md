# Protocol: @Alternative Extension Patterns

**Applies to:** Any casehubio repo extending a persistence SPI or overriding a default
implementation via CDI `@Alternative`.

---

## Two Patterns, Different Contexts

Two repos use opposite `@Alternative` conventions for the same extensibility goal — replacing
a default persistence implementation. Both are correct; which to use depends on the ambiguity
risk.

---

### Pattern A — casehub-ledger: base is `@Alternative`, extension is default bean

`JpaLedgerEntryRepository` is annotated `@Alternative`. A domain-specific extension
(e.g. `CaseLedgerEntryRepository`) **subclasses** it WITHOUT adding `@Alternative` — the
subclass is the active bean; the base stays dormant.

```
base class:      @Alternative (dormant — never resolved directly)
extension class: no @Alternative (active — CDI resolves this)
```

**Why this pattern:** the ledger base and the domain extension are both implementations of
`LedgerEntryRepository`. If both were default beans in the same CDI context, CDI would throw
`AmbiguousResolutionException` at startup. Making the base `@Alternative` eliminates the
ambiguity — only the subclass is visible to the injection point.

**When to use:** when the base implementation and the extension co-exist in the same CDI
context (same deployment classpath) and both satisfy the same injection point type.

**Common mistake:** applying `@Alternative @Priority(1)` to the extension (work pattern)
gets `AmbiguousResolutionException` because the base is also a candidate.

---

### Pattern B — casehub-work: base is default bean, override is `@Alternative @Priority(1)`

Default JPA implementations in casehub-work are NOT `@Alternative`. Overrides (MongoDB,
InMemory test, `SemanticWorkerSelectionStrategy`) are `@Alternative @Priority(1)`.

```
base class:     @ApplicationScoped (active by default)
override class: @Alternative @Priority(1) (activated by classpath presence — beats base)
```

**Why this pattern:** each SPI in casehub-work has exactly one base implementation. There is
no ambiguity risk. The standard Quarkus `@Alternative @Priority` pattern — "activates when on
the classpath, wins by priority" — is the correct and idiomatic approach here.

**When to use:** when the base is the only active implementation by default, and the override
is an opt-in replacement added by including a module or test dependency.

---

### Pattern C — casehub-ledger identity SPIs: `@DefaultBean` no-op + optional `@Alternative` implementations

`NoOpDIDResolver` is `@DefaultBean`. Optional implementations (`KeyDIDResolver`, `WebDIDResolver`)
are `@ApplicationScoped @Alternative`.

```
no-op class:     @DefaultBean (active when no other candidate)
optional impls:  @Alternative (dormant unless activated via quarkus.arc.selected-alternatives)
```

**Why this pattern:** `@DefaultBean` is replaced by any `@ApplicationScoped` bean that
satisfies the same type — including `@Alternative` beans activated at runtime. If optional
implementations are `@ApplicationScoped` but not `@Alternative`, CDI sees multiple candidates
and throws `AmbiguousResolutionException` at startup, even though they were intended to be
opt-in. Marking them `@Alternative` keeps them dormant unless explicitly selected.

**When to use:** when the default is a no-op (`@DefaultBean`) and optional full implementations
should only activate when explicitly selected — not simply by being on the classpath.

**Common mistake:** adding a second `@ApplicationScoped` impl alongside a `@DefaultBean`
without `@Alternative` causes `AmbiguousResolutionException` at boot. The `@DefaultBean` is
only a fallback when NO other candidate exists — it does not suppress ambiguity.

---

## Decision Rule

| Question | Answer | Pattern |
|---|---|---|
| Are the base and extension both candidates for the same injection point in the same deployment? | Yes | A — make base `@Alternative`, extension is default |
| Is the base the only default, and the extension is opt-in by classpath presence? | Yes | B — base is default, extension is `@Alternative @Priority(1)` |
| Is the default a no-op `@DefaultBean` and optional impls should be explicit-activation-only? | Yes | C — no-op is `@DefaultBean`, optional impls are `@Alternative` |

---

## Priority Ladder (Pattern B)

When multiple `@Alternative` backends stack:

| Priority | Wins when | Example |
|---|---|---|
| `@DefaultBean` | Nothing else on classpath | No-op / mock |
| `@ApplicationScoped` (unmarked) | Default production impl | JPA impl |
| `@Alternative @Priority(1)` | Explicitly opted-in | MongoDB, InMemory test |

See also: `docs/protocols/universal/persistence-backend-cdi-priority.md`

---

**Refs:** casehubio/parent#58
