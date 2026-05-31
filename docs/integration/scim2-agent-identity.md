# CaseHub SCIM2 Agent Identity Integration

**Stable raw URL:**
`https://raw.githubusercontent.com/casehubio/parent/main/docs/integration/scim2-agent-identity.md`

Fetch this document before implementing any SCIM-based agent identity lookup in casehub-ledger, casehub-eidos, or casehub-engine.

**Protocol:** [PP-20260530-bf919d](../protocols/casehub/scim2-agent-identity-lookup.md)

---

## CaseHub Schema Extension

Schema URI: `urn:ietf:params:scim:schemas:extension:casehub:2.0:Agent`

| Field | Type | Required for #107 | Description |
|-------|------|--------------------|-------------|
| `did` | String | ✅ | DID URI for the agent (e.g. `did:web:example.com:agents:tarkus`) |
| `clientId` | String | No (deferred to #108) | OAuth client ID referencing the signing credential location |
| `issuerUri` | String | No (deferred to #108) | OAuth issuer URI for signing credential verification |

`clientId` and `issuerUri` are defined in the schema for IdP operators to configure ahead of JwtVCValidator (#108). The `ScimAgentResource` Java record does not currently parse these fields.

---

## Field Mapping

| SCIM Field | CaseHub Meaning |
|-----------|----------------|
| `externalId` | `actorId` — convention string `{model-family}:{persona}@{major}` (e.g. `claude:reviewer@v1`) |
| Extension `did` | DID URI — resolved by `ScimActorDIDProvider` |
| `x509Certificates[0].value` | DER-encoded X.509 certificate. **Note:** `LedgerEntry.agentPublicKey` stores `SubjectPublicKeyInfo` bytes — extraction requires `CertificateFactory`. Currently unused by `ScimAgentResource`. |
| `name` | Persona display name (not used by ledger extension) |
| `clientId` / `issuerUri` | OAuth signing credential reference — consumed by JwtVCValidator (#108) |

---

## Canonical Lookup Pattern

```
GET /scim/v2/Agents?filter=externalId eq "{actorId}"
Authorization: Bearer {authToken}
Accept: application/json
```

### URL Encoding Rules

`actorId` strings contain `:` and `@` which must be percent-encoded in filter values:

```java
String encodedActorId = URLEncoder.encode(actorId, StandardCharsets.UTF_8).replace("+", "%20");
String url = endpoint + "/scim/v2/Agents?filter=externalId%20eq%20%22" + encodedActorId + "%22";
```

**Critical:** actorId must appear in filter VALUES only, never in URL path segments. Colons in path segments are silently split by most HTTP frameworks. See protocol PP-20260530-bf919d.

### HTTP Status Handling

| Status | Meaning | Cache result |
|--------|---------|-------------|
| 200, `totalResults == 0` | Actor not registered | Yes (full TTL) |
| 200, `totalResults == 1` | Found — parse extension | Yes (full TTL) |
| 200, `totalResults > 1` | Data integrity violation — use first, log WARN | Yes (first result) |
| 401 | Auth failure | No — retry |
| 404 | Endpoint misconfiguration (wrong URL, unsupported resource type) | No — retry |
| Other | Unexpected error | No — retry |

---

## Caching

- TTL: configurable via `casehub.ledger.agent-identity.scim.cache-ttl-minutes` (default: 5 min)
- Invalidation: `AgentKeyRotatedEvent` CDI event triggers `ScimActorDIDProvider.invalidate(actorId)`

---

## Security Constraints

- **HTTPS required** by default — `casehub.ledger.agent-identity.scim.require-https=true`; set `false` only for tests
- **Private keys MUST NOT be stored in SCIM** — SCIM holds only public identity material
- **Auth token** is a static deploy-time credential configured via `casehub.ledger.agent-identity.scim.auth-token` (not a `Preferences` key)

---

## ConfiguredActorDIDProvider Interaction

When `ScimActorDIDProvider @Alternative` is activated via `quarkus.arc.selected-alternatives`, `ConfiguredActorDIDProvider @ApplicationScoped` is superseded. Any `casehub.ledger.agent-identity.dids.*` properties are silently ignored. Do not configure both.

---

## Configuration Reference

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `casehub.ledger.agent-identity.scim.endpoint` | `Optional<String>` | (empty) | Base URL of the SCIM2 server. Must use HTTPS. |
| `casehub.ledger.agent-identity.scim.auth-token` | `Optional<String>` | (empty) | Bearer token for `Authorization` header. |
| `casehub.ledger.agent-identity.scim.timeout-ms` | `int` | `5000` | HTTP connect + read timeout in milliseconds. |
| `casehub.ledger.agent-identity.scim.cache-ttl-minutes` | `int` | `5` | TTL for cached SCIM lookups. |
| `casehub.ledger.agent-identity.scim.require-https` | `boolean` | `true` | Enforce HTTPS. Set `false` only in tests. |

---

## IdP-Side Setup Requirements

The endpoint `/scim/v2/Agents` requires a **custom SCIM resource type**. Most enterprise IdPs do not enable custom resource types by default:

| IdP | Notes |
|-----|-------|
| **Okta** | Requires Lifecycle Management license + Schema Discovery app to define custom resource types |
| **Azure AD / Entra** | Custom SCIM resource types not natively supported — use Azure API Management or a custom SCIM proxy |
| **JumpCloud** | Supports custom attributes on User resource; native Agent type requires a custom SCIM application |
| **Self-hosted (Gluu, Keycloak, mid-point, UnboundID)** | Full custom resource type support — define schema + endpoint in IdP console |

For operators whose IdP does not support custom resource types, use a SCIM proxy that maps between standard SCIM Users (with custom attributes) and the CaseHub `Agent` endpoint.

---

## Example SCIM Agent Resource

```json
{
  "schemas": [
    "urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig",
    "urn:ietf:params:scim:schemas:extension:casehub:2.0:Agent"
  ],
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "externalId": "claude:tarkus-reviewer@v1",
  "name": "Tarkus PR Reviewer",
  "urn:ietf:params:scim:schemas:extension:casehub:2.0:Agent": {
    "did": "did:web:casehubio.github.io:agents:tarkus-reviewer"
  }
}
```
