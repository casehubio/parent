# CaseHub Foundation Protocols

| File | Rule Summary | Applies To |
|------|-------------|------------|
| [message-dispatch-builder-validation.md](message-dispatch-builder-validation.md) | Speech-act builder validation is the contract — enforce at build(), not downstream | casehub-qhorus — MessageService.dispatch() callers |
| [message-service-dispatch-enforcement-gate.md](message-service-dispatch-enforcement-gate.md) | MessageService.dispatch() is the single enforcement gate — no caller may duplicate or bypass it | casehub-qhorus — any code sending a message to a Qhorus channel |
