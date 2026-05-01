# Convention: Avoid H2-Reserved Words as Column Names in Flyway Migrations

**Applies to:** All casehub modules with Flyway migrations  
**Severity:** Important — compiles and runs on PostgreSQL but silently fails on H2 in tests

## Problem

H2 reserves certain keywords as column names that PostgreSQL allows. Using them in migration SQL causes test failures that don't reproduce on the target database.

## Rule

Avoid these H2-reserved words as column names: `key`, `value`, `timestamp`, `date`, `time`, `year`, `month`, `day`, `hour`, `minute`, `second`, `name`, `type`, `group`, `order`, `index`, `row`, `schema`. Use descriptive alternatives.

## Example

```sql
-- Wrong — 'key' is reserved in H2
ALTER TABLE notification_rule ADD COLUMN key VARCHAR(255);

-- Right
ALTER TABLE notification_rule ADD COLUMN rule_key VARCHAR(255);
```
