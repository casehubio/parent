# Prompt Snippets — casehubio

The base workflow snippet lives in cc-praxis: `docs/prompt-snippets.md`

casehubio extends it with: deliberation mode + no-end-users context (#1), GitHub issue
requirements in brainstorming and code review (#3, #5), and design philosophy (#7).

---

## casehubio development workflow

Paste at the start of any session involving designing or building:

```
Steps are sequential. If pasted mid-session, acknowledge completed steps and skip them — do not repeat work already done.

1) Think hard, be diligent, be systematic, be exhaustive. This platform has no end users — breaking
   changes cost nothing externally. Prefer fixing the design over protecting callers.

2) invoke work-start first.

3) superpowers:brainstorming before designing — design in tandem with `docs/PLATFORM.md` and relevant
   protocols in `casehub/garden/docs/protocols/`: read them before proposing anything, consult them
   throughout, and do a final coherence review of the complete design against both before leaving
   brainstorming. Any deferred concerns or out-of-scope items must be captured as GitHub issues before
   leaving brainstorming, not just noted in the spec.

4) superpowers:test-driven-development before implementing. [java-dev|python-dev|ts-dev] for all
   [Java|Python|TypeScript].

5) superpowers:requesting-code-review before committing — any finding Minor or above that isn't fixed
   this session must be captured as a GitHub issue before sign-off; batch related minor findings into
   a single issue.

6) implementation-doc-sync after committing.

7) Design for quality alone — bold, forward-looking, platform-coherent. Never let blast radius,
   call-site count, migration complexity, backwards compatibility, or time to implement constrain a
   design. It's OK if a change breaks method calls — the migration is mechanical and the breakage is
   the point, it forces every caller to be explicit. All of these are the price of the right answer,
   not reasons to choose a lesser one. One distinction matters: cost (files, migrations, API breaks)
   is always worth paying; unnecessary complexity (abstractions or layers with no architectural
   benefit) is bad design regardless of cost. Before proposing any workaround, wrapper, or
   backward-compatibility shim — stop and ask: is this the right design? If not, fix the design.
   Workarounds and wrappers are bad design unless explicitly asked to preserve backward compatibility
   for this task. If "simpler is better" crosses your mind, ask whether the simplicity serves the
   architecture or just avoids work.

[describe the issue or feature here]
```

Replace `[java-dev|python-dev|ts-dev]` with the appropriate dev skill for the project.

---

## What each instruction does

| # | Instruction | What it enforces |
|---|-------------|-----------------|
| 1 | Deliberation mode + no end users context | Sets thinking depth for the whole session; breaking changes cost nothing externally — prefer fixing the design over protecting callers |
| 2 | `work-start` | Platform coherence, protocol checks, issue confirmation, IntelliJ MCP verification |
| 3 | `superpowers:brainstorming` | Explore problem space before committing to a design; deferred/out-of-scope items → GitHub issues before leaving brainstorming |
| 4 | `superpowers:test-driven-development` + lang-dev | Tests planned alongside code; loads `testing-principles` and `ide-tooling` as prerequisites |
| 5 | `superpowers:requesting-code-review` | Review gate before any commit; unfixed findings Minor or above → GitHub issue(s) before sign-off |
| 6 | `implementation-doc-sync` | Checks only docs touched this session, not the whole project |
| 7 | Design philosophy | Cost (blast radius, migrations, API breaks) is always worth paying. Workarounds and wrappers are bad design — stop and fix the design instead. Simplicity must serve architecture, not avoid work. |

---

## Spec review

Paste when handing a spec to Claude for critical review before implementation begins:

```
Here is the spec. Review it critically — do not update it or start implementing.

Think hard, go deep, be systematic, exhaustive, and diligent. Cover:

- What's missing — requirements, edge cases, error paths, operational concerns not addressed
- What's wrong — incorrect assumptions, internal contradictions, mismatches with platform
  patterns or protocols
- What could be cleaner — abstractions that don't earn their keep, complexity that a different
  foundational choice would eliminate, naming or layering that will cause confusion later
- Early rearchitecting — for each significant concern, ask: would a different approach at the
  root eliminate this entire class of problem? Prefer raising these early over accepting a design
  that will need retrofitting

Review against `docs/PLATFORM.md` and relevant protocols in `casehub/garden/docs/protocols/`
— flag anything that contradicts or doesn't fit the platform's patterns.

Be skeptical of: claimed necessity vs convenience, accidental complexity, and abstractions that
exist to paper over a design gap. Prioritize architectural concerns over implementation details.
```
