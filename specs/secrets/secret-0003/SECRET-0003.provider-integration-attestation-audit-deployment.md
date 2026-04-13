# SECRET-0003 — Provider Integration, Attestation, Audit, and Deployment Profile
Version: 0.1  
Status: Draft normative integration profile  
Date: 2026-04-13

## 1. Purpose

This document closes the remaining gap between:

- **Bridge Spec v0.2** authorization and burn/restore control,
- **SECRET-0001** secret object and lifecycle policy,
- **SECRET-0002** backend and materialization selection,

and the **real provider plane** that a working deployment must trust.

A conforming implementation SHALL specify:

1. a `ProviderCatalog`,
2. one or more `DeploymentProfile` records,
3. an authoritative attestation result contract,
4. an authoritative revocation snapshot contract,
5. a durable audit envelope and checkpoint contract,
6. a provider-side integration service or equivalent adapter,
7. operational runbooks for provider outage, burn, restore, rotation, and recovery.

## 2. Relationship to prior artifacts

- The **bridge** decides whether a request is admissible.
- **SECRET-0001** defines the lifecycle of the secret itself.
- **SECRET-0002** defines backend and materializer profiles.
- **SECRET-0003** defines **who supplies the authoritative facts**, **how those facts are transported**, and **how a deployment binds those providers into a trusted runtime**.

Without SECRET-0003, a system may have good policy and good lifecycle semantics but still lack:
- a trustworthy attestation signal,
- a trustworthy revocation signal,
- durable evidence,
- a concrete deployment profile,
- a recoverable provider control plane.

## 3. Conformance

A system conforms to SECRET-0003 only if all of the following hold:

- every authoritative fact used by bridge or planner logic is sourced from a declared provider in a `ProviderCatalog`;
- every deployment has an explicit `DeploymentProfile`;
- provider unavailability is fail-closed unless a narrower, explicitly declared safe-mode path exists;
- attestation, revocation, time, mode, and audit readiness are evaluated before a materialization or dynamic issuance path is accepted;
- durable audit emission or an emergency sealed queue exists before an allow decision is finalized;
- audit envelopes never contain raw plaintext secret values;
- provider facts are freshness-bounded and attributable to a concrete verifier or source;
- burn mode invalidates provider-dependent allow paths until restore preconditions are satisfied.

## 4. Provider SPI

A conforming deployment SHALL implement or bind to providers for the following roles.

### 4.1 TimeAuthority

The time authority is the sole authoritative source for decision time and freshness evaluation.

It SHALL provide:
- an authoritative current timestamp,
- an issuing source identifier,
- monotonic freshness semantics suitable for replay and expiry evaluation.

Caller-supplied time SHALL be ignored.

### 4.2 RevocationProvider

The revocation provider is the sole authoritative source for revocation and stale-epoch status.

It SHALL provide:
- a revocation snapshot identifier,
- issuer or key-epoch revocation state,
- witness or token revocation state,
- secret version or secret epoch revocation state,
- a freshness bound.

### 4.3 AttestationProvider

The attestation provider is the sole authoritative source for workload, host, or device posture used in the secret path.

It SHALL provide:
- the subject identity,
- the posture digest,
- the verifier identity,
- a status value,
- issue and expiry times,
- measurement or evidence references.

### 4.4 ModeController

The mode controller is the sole authoritative source for `normal`, `degraded`, `safe`, and `burn` mode.

It SHALL provide:
- the current mode,
- the current mode epoch,
- cut-set or scope information when burn is partial,
- the actor or automation basis that changed mode,
- restore prerequisites when mode is not `normal`.

### 4.5 AuditSink

The audit sink is the authoritative durability target for evidence.

It SHALL provide:
- append acceptance or rejection,
- a stream identifier,
- sequencing,
- checkpoint capability,
- health and durability status.

A deployment MAY also define an **emergency sealed queue** for temporary local buffering when the primary sink is unavailable, but the queue SHALL be:
- append-only,
- bounded,
- encrypted or otherwise protected according to local policy,
- drained and reconciled after sink recovery.

### 4.6 SecretBackendProvider

The backend provider is the authoritative boundary that stores, unwraps, issues, or proxies the secret class.

It SHALL expose only the operations consistent with the selected backend profile.
It SHALL NOT silently widen exportability beyond the binding and selected materializer profile.

### 4.7 Materializer

The materializer is the local last-mile component that binds a consumer to a bounded secret session.

It SHALL:
- create only the handle or bounded plaintext surface allowed by the selected materializer profile,
- enforce TTL and teardown,
- revalidate on burn, epoch change, or explicit revocation signals,
- emit audit events for session start and session teardown.

## 5. ProviderCatalog

A `ProviderCatalog` is the inventory of authoritative providers available to a deployment.

Each provider entry SHALL declare at least:
- provider id,
- provider kind,
- product family or implementation family,
- trust boundary,
- capabilities,
- fail-closed policy,
- health freshness limit,
- allowed operating modes,
- evidence expectations.

A provider entry SHALL NOT store raw plaintext secret values.

## 6. DeploymentProfile

A `DeploymentProfile` binds a concrete environment to a subset of providers and default secret-class bindings.

At minimum, a deployment profile SHALL define:
- environment type,
- platform,
- identity posture expectations,
- authoritative provider ids for time, revocation, attestation, mode control, and audit,
- default backend and materializer bindings by secret class,
- log and transcript redaction policy,
- burn and restore behavior,
- emergency queue behavior.

## 7. Durable audit transport

### 7.1 AuditEnvelope

Every allow, deny, burn, restore, rotate, materialize, revoke, suspend, archive, destroy, and recovery event SHALL produce an `AuditEnvelope`.

An audit envelope SHALL include:
- stream id,
- sequence number,
- previous event hash,
- event hash,
- event type,
- source id,
- trace id,
- timestamp,
- payload hash,
- labels,
- decision or lifecycle outcome,
- secrecy-preserving metadata only.

The payload hash MAY refer to a separately protected evidence object.
The envelope itself SHALL NOT inline raw plaintext secret material.

### 7.2 AuditCheckpoint

An audit checkpoint records the latest durable committed point in a stream.

A checkpoint SHALL include:
- stream id,
- last committed sequence,
- last committed event hash,
- checkpoint timestamp,
- sink identifier.

### 7.3 Emergency sealed queue

If the primary sink is unavailable, a deployment MAY use an emergency sealed queue only when:
- the deployment profile permits it,
- the queue is local to the trust boundary,
- the queue preserves ordering,
- the queue can be reconciled to the main sink,
- normal allow paths requiring durable evidence do not silently degrade into unaudited operation.

## 8. Deployment profiles

A conforming suite SHOULD define at least the following deployment classes.

### 8.1 `workstation-local`

For local developer or operator machines.  
Recommended patterns:
- user-facing bootstrap or human-held credentials,
- local keychain or equivalent only for bootstrap or workstation-local authority,
- agent-proxy or memfd-style last-mile paths,
- transcript redaction strict by default.

### 8.2 `nixos-service-host`

For long-lived Linux service hosts.  
Recommended patterns:
- system identity plus host/workload attestation,
- systemd-credential or unix-socket-proxy materialization,
- dynamic issuance for database credentials where feasible,
- strict unit binding and teardown.

### 8.3 `cloud-agent-worker`

For ephemeral or autoscaled agent workers.  
Recommended patterns:
- workload identity,
- short-lived dynamic credentials,
- sidecar or unix-socket proxy operation paths,
- aggressive revocation and replay bounds,
- memory-backed runtime surfaces only.

### 8.4 `ci-runner`

For build and release pipelines.  
Recommended patterns:
- no standing secrets in repository state,
- short-lived issuance per job,
- explicit provenance and audit,
- narrow output and egress scope.

## 9. Operational runbooks

A conforming deployment SHALL maintain operational procedures for:

- provider catalog change,
- secret rotation,
- revocation propagation failure,
- attestation failure,
- audit sink outage,
- burn activation,
- burn restore,
- recovery of archived versions,
- emergency queue reconciliation.

## 10. Required invariants

The following invariants SHALL hold.

### I1. Provider authority
Only declared providers may contribute authoritative facts.

### I2. Freshness
Attestation, revocation, mode, and time facts SHALL be freshness-bounded.

### I3. Audit before allow
If policy requires durable evidence for an allow path, the decision SHALL fail closed when no durable sink or permitted emergency queue is available.

### I4. No secret in evidence
Raw plaintext secret values SHALL NOT appear in provider catalog entries, deployment profiles, audit envelopes, or checkpoints.

### I5. Burn dominance
When mode is `burn`, new secret sessions SHALL NOT be issued from the affected cut-set.

### I6. Attestation mismatch denies
An attestation mismatch or expiry SHALL deny or burn according to local burn policy; it SHALL NOT be silently ignored.

### I7. Revocation dominates active use
A revoked issuer, revoked witness, revoked secret epoch, or revoked secret version SHALL dominate any stale local allow path.

## 11. Product binding guidance

This profile intentionally stays product-agnostic, but a deployment SHOULD document product families in the `ProviderCatalog`.
Examples include:
- dynamic secret backends,
- cloud envelope backends,
- HSM/PKCS#11 style non-exportable operations,
- OS keychain bootstrap stores,
- SPIFFE- or OIDC-like workload identity sources,
- append-only audit sinks.

## 12. Implementation order

A practical implementation sequence is:

1. adopt the bridge and secret object schemas,
2. choose backend and materializer profiles,
3. define the provider catalog,
4. define the deployment profiles,
5. wire durable audit,
6. wire attestation and revocation,
7. run burn and restore exercises,
8. freeze the production checklist.

## 13. Non-goals

SECRET-0003 does not define:
- a particular vendor product,
- a specific attestation format,
- a specific audit database,
- a specific cloud provider.

Those are deployment choices constrained by the contracts in this document.
