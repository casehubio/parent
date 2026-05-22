# Universal Protocols

| File | Rule Summary | Applies To |
|------|-------------|------------|
| [no-jpa-entities-across-requires-new.md](no-jpa-entities-across-requires-new.md) | No JPA entities cross a REQUIRES_NEW boundary — extract primitives before the call | Any Quarkus service with REQUIRES_NEW + outer @Transactional |
