# Convention: Disable Reactive Datasource in H2 Tests When hibernate-reactive-panache Is on Classpath

**Applies to:** All modules where a transitive dependency pulls in hibernate-reactive-panache  
**Severity:** Critical — H2 tests fail to start entirely without this property

## Problem

If any transitive dependency pulls `hibernate-reactive-panache` onto the classpath, Quarkus attempts to configure a reactive datasource even when the module doesn't use one. H2 does not have a native reactive driver, so startup fails with a datasource configuration error.

## Rule

Add this to `src/test/resources/application.properties`:

```properties
%test.quarkus.datasource.reactive=false
```

This disables the reactive datasource configuration for the test profile only, without affecting production configuration.
