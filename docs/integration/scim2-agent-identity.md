# SCIM2 Agent Identity Integration

**Stable URL:** `https://raw.githubusercontent.com/casehubio/parent/main/docs/integration/scim2-agent-identity.md`

**Purpose:** Canonical reference for resolving agent identity attributes (DID, public key, capabilities) across all casehub repos using SCIM 2.0. Load this document as context when implementing any component that resolves agent identity.

---

## SCIM Schema Extension

CaseHub defines a SCIM 2.0 schema extension for the `Agent` resource type:

```
urn:ietf:params:scim:schemas:extension:casehub:2.0:Agent
```

Based on IETF draft `draft-abbey-scim-agent-extension-00`, which defines a first-class `Agent` resource mapping directly to multi-agent system identity needs.

---

## Field Mapping Table

| SCIM Field | CaseHub Semantic | Format | Notes |
|-----------|-----------------|--------|-------|
| `externalId` | `actorId` convention string | `{model-family}:{persona}@{major}` — e.g. `claude:reviewer@v1` | Primary lookup key. **Must appear in filter values only — never URL path segments.** |
| `Agent.did` | DID URI | `did:key:...` or `did:web:...` | Agent's decentralised identifier |
| `x509Certificates[type=public]` | `agentPublicKey` | Base64-encoded DER bytes — same as `agentPublicKey` on `LedgerEntry` | Ed25519 or post-quantum successor algorithm |
| `clientId` | OAuth client ID | String | References signing credential in OIDC/Vault |
| `issuerUri` | OAuth issuer | URI | Token issuer for credential verification |
| `displayName` | Persona display name | String | Human-readable agent name |
| `roles[].value` | Capability tags | Comma-separated strings | e.g. `security-review,architecture-review` |

---

## Canonical Lookup Pattern

```java
// Filter by actorId using externalId — actorId value is URL-encoded
String filter = "externalId eq \"" + actorId + "\"";
String url = scimBaseUrl + "/Agents?filter=" + URLEncoder.encode(filter, UTF_8);
```

**URL-encoding rule:** The colon in actorId strings (`claude:reviewer@v1`) must appear in `filter=` query parameter values only. Never construct a URL where `actorId` appears as a path segment — the colon breaks URL parsing on many servers.

---

## Caching Expectations

- Cache TTL: agent identity attributes are stable; default 5-minute TTL acceptable
- Invalidation: on major version bump (`claude:analyst@v1` → `claude:analyst@v2`), the trust baseline resets — callers should invalidate their cache on major version change detection
- `@CacheResult` (Quarkus cache) with actorId as cache key is the recommended pattern

---

## What Must NOT Be Stored in SCIM

- **Private keys** — private keys never leave the agent process or secure key store (Vault, TPM)
- **Session tokens** — ephemeral; not identity attributes
- **Trust scores** — owned by casehub-ledger, not identity infrastructure

---

## Example SCIM Agent Resource (JSON)

```json
{
  "schemas": [
    "urn:ietf:params:scim:schemas:core:2.0:User",
    "urn:ietf:params:scim:schemas:extension:casehub:2.0:Agent"
  ],
  "externalId": "claude:reviewer@v1",
  "displayName": "Claude Code Reviewer",
  "urn:ietf:params:scim:schemas:extension:casehub:2.0:Agent": {
    "did": "did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK",
    "x509Certificates": [
      { "type": "public", "value": "MCowBQYDK2VdAyEA..." }
    ],
    "clientId": "casehub-reviewer-agent",
    "issuerUri": "https://auth.casehub.io",
    "roles": [
      { "value": "security-review" },
      { "value": "architecture-review" }
    ]
  }
}
```

---

## Related

- Protocol: [`docs/protocols/casehub/scim2-agent-identity-lookup.md`](../protocols/casehub/scim2-agent-identity-lookup.md)
- casehub-ledger#81 — first consumer (`ScimActorDIDProvider`)
- casehub-eidos `AgentRegistry` — natural SCIM service provider for internal deployments
- `casehub-platform-scim` — ships SCIM 2.0 `GroupMembershipProvider` (same SCIM server, different resource type)
