---
id: PP-20260530-bf919d
title: "Resolve agent identity attributes via SCIM2 Agent endpoint using actorId as externalId"
type: rule
scope: platform
applies_to: "Any casehub component resolving agent identity attributes (DID, public key, capabilities, status) — casehub-ledger, casehub-eidos, casehub-engine, consumers"
severity: important
refs:
  - https://www.ietf.org/archive/id/draft-abbey-scim-agent-extension-00.html
  - https://github.com/casehubio/parent/issues/107
violation_hint: "Hardcoding actorId→DID mappings in application.properties instead of querying SCIM; placing actorId in a URL path segment (colon in claude:reviewer@v1 causes silent split); different repos implementing incompatible lookup mechanisms for the same identity attribute"
created: 2026-05-30
---

When any casehub component needs to resolve agent identity attributes (DID, public
key, capabilities, or lifecycle status), it MUST query the SCIM2 Agent endpoint using
`actorId` as the `externalId` filter:
`GET /scim/v2/Agents?filter=externalId eq "{actorId}"`. The casehub custom schema
extension `urn:ietf:params:scim:schemas:extension:casehub:2.0:Agent` carries the DID
URI; `x509Certificates` carries the public key material; OAuth metadata (`clientId`,
`issuerUri`) references the signing credential location — private keys are NEVER stored
in SCIM. Because `actorId` strings contain colons (`claude:reviewer@v1`), they MUST
appear only in filter values (quoted), never in URL path segments. Implementations
MUST cache resolved attributes with a configurable TTL (default 5 minutes) and
invalidate on CDI `KeyRotationEntry` events. Direct `application.properties`
configuration is permitted for development and small deployments only.
