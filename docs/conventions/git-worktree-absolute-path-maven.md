# Convention: Use Absolute Paths When Running Maven in Git Worktrees

**Applies to:** All modules using git worktrees for parallel development  
**Severity:** Important — relative paths resolve incorrectly after directory context changes

## Problem

When working in a git worktree, shell context switches (e.g. from Claude tool calls) can reset the working directory. Relative paths then resolve to the wrong location, causing `mvn -f pom.xml` to target the main worktree instead of the feature branch.

## Rule

Always use the absolute path to the worktree's `pom.xml`:

```bash
# Wrong — breaks if cwd changes
mvn test -pl runtime

# Right — always targets the worktree
JAVA_HOME=$(/usr/libexec/java_home -v 26) mvn test \
  -f /Users/mdproctor/claude/casehub/qhorus/.claude/worktrees/feat-branch/pom.xml \
  -pl runtime
```
