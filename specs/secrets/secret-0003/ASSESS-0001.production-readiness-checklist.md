# ASSESS-0001 — Production Readiness Checklist
Version: 0.1  
Status: Draft checklist  
Date: 2026-04-13

Use this checklist only after Bridge Spec v0.2, SECRET-0001, SECRET-0002, and SECRET-0003 have all been adopted.

## A. Policy and object model
- [ ] Every managed secret has a `SecretObject` and at least one `SecretVersion`.
- [ ] Every secret class has an explicit backend binding and materializer binding.
- [ ] No raw plaintext secret appears in metadata, logs, traces, or audit envelopes.
- [ ] Only `active` versions are eligible for runtime materialization.
- [ ] Rotation, revocation, archive, restore, and destroy are all defined per class.

## B. Provider plane
- [ ] A `ProviderCatalog` exists and all authoritative providers are declared in it.
- [ ] Every deployment has a `DeploymentProfile`.
- [ ] Time, revocation, attestation, mode, and audit providers are all authoritative and fail-closed.
- [ ] Provider freshness limits are documented and enforced.
- [ ] Provider outages have tested runbooks.

## C. Attestation and revocation
- [ ] Attestation mismatch denies or burns according to policy.
- [ ] Revoked issuers, JTIs, secret epochs, and secret versions dominate stale local allow paths.
- [ ] Restore requires fresh attestation and a new epoch where policy requires it.
- [ ] Replay windows are bounded and tested.

## D. Materialization
- [ ] Materialization is local, bounded, TTL-limited, and auditable.
- [ ] Teardown occurs on exit, expiry, burn, and revocation events.
- [ ] Non-exportable classes are delivered by handle/proxy only.
- [ ] Any tmpfs/file path use is explicit, justified, and cleaned up.

## E. Audit and evidence
- [ ] Every allow/deny/burn/restore/materialize event emits an audit envelope.
- [ ] Audit streams are sequenced and hash-linked.
- [ ] A checkpoint process exists and is tested.
- [ ] Emergency queue use is bounded, protected, and reconciled.
- [ ] Audit deletion or movement is separately authorized.

## F. Burn and restore
- [ ] Burn triggers are documented and tested.
- [ ] Burn propagation time is measured and within target.
- [ ] Restore requires documented approvals and fresh provider facts.
- [ ] Evidence survives burn and restore.
- [ ] Known-compromised material never silently returns to active use.

## G. Deployment hardening
- [ ] The sidecar or bridge runs with minimal privileges.
- [ ] Model runtime has no standing nonlocal secret credentials.
- [ ] Deployment templates enforce narrow surfaces and transcript redaction.
- [ ] CI and developer workflows scan for hardcoded secrets and accidental logs.

## H. Exercises
- [ ] Rotation exercise completed.
- [ ] Revocation propagation failure exercise completed.
- [ ] Attestation failure exercise completed.
- [ ] Audit sink outage exercise completed.
- [ ] Burn and restore exercise completed.
- [ ] Recovery from archived version exercise completed.

## Exit criterion
A deployment is not production-ready unless every MUST-level item above is complete or has an approved compensating control.
