# Convention: Optional Module Pattern

**Applies to:** Any feature module that should not affect applications that don't use it  
**Examples:** `quarkus-work-reports`, `quarkus-work-notifications`, `quarkus-work-ai`, `quarkus-work-queues`

## Rule

Optional features must be packaged as **Jandex library modules**, not as part of the core extension runtime. Adding the module to a pom activates the feature; omitting it has zero impact on startup time, classpath, native image size, or CDI bean count.

## Structure

```xml
<!-- In the optional module's pom.xml -->
<parent>
  <groupId>io.quarkiverse.work</groupId>
  <artifactId>quarkus-work-parent</artifactId>
</parent>
<artifactId>quarkus-work-<feature></artifactId>

<dependencies>
  <!-- Depend on the core runtime for entity and CDI access -->
  <dependency>
    <groupId>io.quarkiverse.work</groupId>
    <artifactId>quarkus-work</artifactId>
  </dependency>
  <!-- Feature-specific deps only -->
</dependencies>

<build>
  <plugins>
    <!-- Required: Jandex index so CDI beans are discovered when consumed as a JAR -->
    <plugin>
      <groupId>io.smallrye</groupId>
      <artifactId>jandex-maven-plugin</artifactId>
      <version>3.3.1</version>
      <executions>
        <execution><id>jandex</id><phase>process-classes</phase>
          <goals><goal>jandex</goal></goals>
        </execution>
      </executions>
    </plugin>
  </plugins>
</build>
```

## Why Jandex is required

Without the Jandex index, Quarkus discovers CDI beans from optional modules by direct class scan during `@QuarkusTest` (works in the module's own tests) but NOT when the module is consumed as a JAR by another module or application. The `jandex-maven-plugin` generates `META-INF/jandex.idx` which Quarkus uses for bean discovery in JAR form.

## Flyway migrations

Optional modules that add database tables use high-version namespaces (see [flyway-migration-rules.md](flyway-migration-rules.md)). The migrations are included in the module JAR and discovered by Flyway's classpath scanner automatically when the module is on the classpath.

## Zero-cost guarantee

Test it: add the module to a minimal Quarkus application and verify that the startup time, native image size, and CDI bean count are not materially affected beyond the feature's own beans.
