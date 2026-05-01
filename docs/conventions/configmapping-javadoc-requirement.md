# Convention: @ConfigMapping Interfaces Require Javadoc on Every Method

**Applies to:** All Quarkus extensions with @ConfigMapping interfaces  
**Severity:** Critical — missing Javadoc causes compile error, not a runtime warning

## Problem

Quarkus's config documentation processor requires Javadoc on every method in a `@ConfigMapping` interface, including group accessors. A missing Javadoc produces a compile-time error that can be mistaken for a dependency issue.

## Rule

Every method in a `@ConfigMapping` interface — including simple `boolean enabled()` accessors and group-returning accessors — must have a Javadoc comment.

## Example

```java
@ConfigMapping(prefix = "casehub.work")
public interface WorkConfig {
    /** Whether the work module is enabled. */
    boolean enabled();

    /** SLA configuration. */
    SlaConfig sla();

    interface SlaConfig {
        /** Default deadline in hours. */
        int defaultDeadlineHours();
    }
}
```
