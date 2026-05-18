---
id: PP-20260518-dffda8
title: "EPIC-CLOSED.md must include a deletion date of today + 14 days"
type: rule
scope: platform
applies_to: "Workspace and project repos — both epic branches"
severity: guidance
refs: []
violation_hint: "EPIC-CLOSED.md present but no 'Delete after:' line. Next session cannot determine whether the branch is safe to delete."
created: 2026-05-18
---

Every `EPIC-CLOSED.md` must include a `**Delete after:** YYYY-MM-DD` line set to today + 14 days. This gives a cross-repo review window while creating a clear expiry signal for branch cleanup. At each branch hygiene scan, check whether the deletion date has passed; if so, offer to delete the branch (only after verifying code is merged and artifacts are clean). Branches without a deletion date are treated as indefinitely retained, accumulating silently. Both the workspace and project epic branches need the marker.
