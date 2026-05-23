# CaseHub Foundation Protocols

| File | Rule Summary | Applies To |
|------|-------------|------------|
| [message-dispatch-builder-validation.md](message-dispatch-builder-validation.md) | Speech-act builder validation is the contract — enforce at build(), not downstream | casehub-qhorus — MessageService.dispatch() callers |
| [message-service-dispatch-enforcement-gate.md](message-service-dispatch-enforcement-gate.md) | MessageService.dispatch() is the single enforcement gate — no caller may duplicate or bypass it | casehub-qhorus — any code sending a message to a Qhorus channel |
| [ledger-algorithm-transparent-signing.md](ledger-algorithm-transparent-signing.md) | Signing and verification code must derive the algorithm from the key — never hardcode a string | casehub-ledger — io.casehub.ledger.runtime.service signing/verification/key-loading |
| [cross-repo-optional-dep-table-registration.md](cross-repo-optional-dep-table-registration.md) | Register optional cross-repo deps in both the build order and the Cross-Repo Dependency Map table | All casehubio repos when adding an optional cross-repo compile dependency |
