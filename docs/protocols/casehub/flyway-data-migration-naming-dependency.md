---
id: PP-20260604-55a0aa
title: "Flyway data migrations that target rows by naming convention must document the coupling"
type: rule
scope: repo
applies_to: "casehub-qhorus — any Flyway migration that uses UPDATE ... WHERE name LIKE or similar pattern matching on channel/entity names"
severity: important
refs:
  - runtime/src/main/resources/db/qhorus/migration/V16__add_channel_denied_types.sql
violation_hint: "A migration UPDATE targets rows by a naming pattern (LIKE '%/oversight', WHERE name STARTS WITH ...) without a comment stating which naming convention the pattern depends on, what would break if the convention changes, and that the migration cannot be tested in an empty schema."
created: 2026-06-04
---

Any Flyway migration that uses a data-manipulation statement (UPDATE, DELETE, INSERT) matching rows by a name pattern must include a comment that: (1) names the convention it depends on (e.g. "CaseChannel.channelName(caseId, 'oversight') produces the '%/oversight' suffix"), (2) describes what would break if the convention changes without a companion migration, and (3) notes that schema tests (e.g. `FlywayMigrationSchemaTest`) run against an empty schema and cannot verify the data migration. The pattern is coupled to naming conventions established in application code — those conventions may change independently of the migration, making the migration silently wrong for rows created after a rename. The comment is the only documentation of this coupling that survives in the migration file itself.
