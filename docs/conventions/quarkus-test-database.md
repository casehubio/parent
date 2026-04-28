# Convention: Database Configuration for @QuarkusTest Suites

**Applies to:** All modules with `@QuarkusTest` classes that use a datasource  
**Severity:** Important — wrong config causes intermittent failures or missed production bugs

## H2 Test Datasource (standard)

```properties
# application.properties in src/test/resources/
quarkus.http.test-port=0                          # prevents TIME_WAIT conflicts
quarkus.datasource.db-kind=h2
quarkus.datasource.jdbc.url=jdbc:h2:mem:<module>;MODE=PostgreSQL;DB_CLOSE_DELAY=-1
quarkus.hibernate-orm.database.generation=none
quarkus.flyway.migrate-at-start=true
quarkus.scheduler.enabled=false
```

**`MODE=PostgreSQL` is mandatory.** It makes H2 reject non-standard SQL types (e.g. bare `DOUBLE`) at test time, catching migration compatibility bugs before they reach production.

Use a unique database name per module (e.g. `testdb`, `reportstest`, `ledgertest`) to prevent state leakage when running tests from multiple modules in the same JVM.

## Multiple @QuarkusTest classes in one module

Add `quarkus.http.test-port=0` to prevent `TIME_WAIT` port conflicts when Quarkus restarts between test classes.

## PostgreSQL Testcontainers (dialect validation)

For modules with Flyway migrations, add a PostgreSQL dialect validation test using Testcontainers. Reference implementation: `quarkus-work/quarkus-work-reports/PostgresTestResource`.

Key constraints:
- `quarkus.datasource.db-kind=postgresql` must be a **Surefire system property**, not a test resource override — it must be visible before Quarkus augmentation bakes the JDBC driver class
- PostgreSQL Surefire execution must run **first** (before H2) — Quarkus caches the augmented artifact on disk; first execution wins
- Use `reuseForks=false` for the PostgreSQL execution to get a clean JVM

```xml
<execution>
  <id>postgres-dialect-test</id>
  <phase>test</phase>
  <goals><goal>test</goal></goals>
  <configuration>
    <includes><include>**/PostgresDialect*.java</include></includes>
    <reuseForks>false</reuseForks>
    <systemPropertyVariables>
      <quarkus.datasource.db-kind>postgresql</quarkus.datasource.db-kind>
      <quarkus.datasource.devservices.enabled>false</quarkus.datasource.devservices.enabled>
    </systemPropertyVariables>
  </configuration>
</execution>
```

## @TestTransaction + REST assertions

Do not mix `@TestTransaction` with REST Assured assertions in the same test class. A `@Transactional` CDI method called from within `@TestTransaction` joins the test transaction; subsequent HTTP calls run in their own transaction and cannot see the uncommitted data (returns 404). Remove `@TestTransaction` from test classes that mix direct service calls with REST Assured assertions.
