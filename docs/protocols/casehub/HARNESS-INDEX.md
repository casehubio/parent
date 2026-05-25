# CaseHub Application Protocols

Protocols for applications built on the CaseHub harness (aml, clinical, devtown, etc.).

| File | Rule Summary | Applies To |
|------|-------------|------------|
| [coordinator-no-transactional-multi-datasource.md](coordinator-no-transactional-multi-datasource.md) | Do not use @Transactional at the coordinator level when the method spans default + qhorus datasources — per-service boundaries only | Any CaseHub application coordinator spanning multiple persistence units |
