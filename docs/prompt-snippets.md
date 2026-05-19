# Prompt Snippets — casehubio

The base workflow snippet lives in cc-praxis: `docs/prompt-snippets.md`

casehubio extends it with two additional instructions covering design philosophy (#5) and
epic hygiene (#6).

---

## casehubio development workflow

Paste at the start of any session involving designing or building:

```
1) invoke work-start first. 2) superpowers:brainstorming before designing — any deferred concerns or out-of-scope items must be captured as GitHub issues before leaving brainstorming, not just noted in the spec. 3) superpowers:test-driven-development before implementing. [java-dev|python-dev|ts-dev] for all [Java|Python|TypeScript]. 4) superpowers:requesting-code-review before committing — any finding Minor or above that isn't fixed this session must be captured as a GitHub issue before sign-off; batch related minor findings into a single issue. implementation-doc-sync after. 5) Design for quality alone — bold, forward-looking, platform-coherent. Never let blast radius, call-site count, migration complexity, backwards compatibility, or time to implement constrain a design: these are the price of the right answer, not reasons to choose a lesser one. One distinction matters: cost (files, migrations, API breaks) is always worth paying; unnecessary complexity (abstractions or layers with no architectural benefit) is bad design regardless of cost. If "simpler is better" crosses your mind, ask whether the simplicity serves the architecture or just avoids work. 6) At work-end, ensure the design journal is merged into DESIGN.md before closing the branch.

[describe the issue or feature here]
```

Replace `[java-dev|python-dev|ts-dev]` with the appropriate dev skill for the project.

---

## What each instruction does

| # | Instruction | What it enforces |
|---|-------------|-----------------|
| 1 | `work-start` | Platform coherence, protocol checks, issue confirmation, IntelliJ MCP verification |
| 2 | `superpowers:brainstorming` | Explore problem space before committing to a design; deferred/out-of-scope items → GitHub issues before leaving brainstorming |
| 3 | `superpowers:test-driven-development` | Tests planned alongside code, not after |
| 3 | `java-dev` / `python-dev` / `ts-dev` | Language rules + loads `testing-principles` and `ide-tooling` as prerequisites |
| 4 | `superpowers:requesting-code-review` | Review gate before any commit; unfixed findings Minor or above → GitHub issue(s) before sign-off |
| 4 | `implementation-doc-sync` | Checks only docs touched this session, not the whole project |
| 5 | Design philosophy | Cost (blast radius, migrations, API breaks) is always worth paying for the right design. Unnecessary complexity is bad design regardless of cost — "simpler is better" must serve architecture, not avoid work. |
| 6 | Journal merge | Ensures design reasoning captured during the epic is merged into DESIGN.md at close, not lost on the branch |
