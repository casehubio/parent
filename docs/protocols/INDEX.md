# Protocols — Index Router

All protocol files live in two subfolders. Read the index for your context:

| Folder | Index | Who reads it |
|--------|-------|-------------|
| `universal/` | [universal/INDEX.md](universal/INDEX.md) | Any Java/Quarkus project — staging area for Hortora community protocols |
| `casehub/` | [casehub/FOUNDATION-INDEX.md](casehub/FOUNDATION-INDEX.md) | LLMs building the CaseHub platform (engine, ledger, work, qhorus, parent) |
| `casehub/` | [casehub/HARNESS-INDEX.md](casehub/HARNESS-INDEX.md) | LLMs building apps on CaseHub (aml, clinical, devtown, QuarkMind) |

App-building sessions should read **both** `universal/INDEX.md` and `casehub/HARNESS-INDEX.md`.
Platform-building sessions should read **both** `universal/INDEX.md` and `casehub/FOUNDATION-INDEX.md`.

---

## Reconstituting an index from scratch

The `scope` frontmatter field is the discriminator:

```bash
# Universal protocols
grep -rl "^scope: universal" docs/protocols/universal/*.md

# CaseHub Foundation protocols (scope: platform or repo)
grep -rl "^scope: platform\|^scope: repo" docs/protocols/casehub/*.md

# CaseHub Harness protocols
grep -rl "^scope: application" docs/protocols/casehub/*.md
```

Read each matched file's `id`, `title`, and `applies_to` to reconstruct the table rows.

---

## Adding a new protocol

1. Decide which folder: is this universal (any Java/Quarkus project) or CaseHub-specific?
2. Write the file with correct `scope:` frontmatter (`universal`, `platform`, `repo`, or `application`)
3. Add a row to the appropriate index
4. If universal: it is a candidate for future contribution to the Hortora protocols repository
