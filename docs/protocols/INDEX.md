# Protocols — Index Router

All protocol files live in this directory. Two separate indexes serve different audiences:

| Index | Who reads it | Scope values |
|-------|-------------|-------------|
| [FOUNDATION-INDEX.md](FOUNDATION-INDEX.md) | LLMs building the CaseHub platform (engine, ledger, work, qhorus, connectors, parent) | `platform`, `repo` |
| [HARNESS-INDEX.md](HARNESS-INDEX.md) | LLMs building apps on top of CaseHub (aml, clinical, devtown, QuarkMind, any new harness) | `application` |

CLAUDE.md files reference the correct index directly — not this router.

---

## Reconstituting an index from scratch

The `scope` frontmatter field in each protocol file is the discriminator.
Run these to enumerate which files belong in each index:

```bash
# Foundation protocols (scope: platform or scope: repo)
grep -rl "^scope: platform\|^scope: repo" docs/protocols/*.md

# Harness protocols (scope: application)
grep -rl "^scope: application" docs/protocols/*.md
```

Read each matched file's `id`, `title`, and `applies_to` fields to reconstruct the table rows.
Garden entries (GE-*) are not protocol files — they are referenced by ID from the knowledge garden
and listed in the indexes for discoverability only.
