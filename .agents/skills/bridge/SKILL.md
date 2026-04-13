---
name: bridge
description: >
  Use this skill when work touches the bridge adapter contract, bridge
  admission, secret materialization, bounded session issuance, burn/restore
  mode transitions, or the bridge-owned secret suite. Trigger it for questions
  about `AuthorizeRequest`, `ProviderResults`, `PolicyInput`,
  `MaterializationPlanRequest`, `MaterializationSession`, provider mapping,
  audit records, and bridge-specific realization profiles. Prefer the
  normalized bridge-owned spec surface under `specs/` first, keep Premath
  kernel doctrine upstream, and keep live provider bindings and local secret
  file details downstream.
---

# bridge

## What this skill is
This is the repo-local routing surface for the bridge domain stack.

It is not a generic security skill.
It is not a downstream runtime guide for local secret files, funded providers,
or deployment proof.

Read:
- `references/BRIDGE-FLOW.md` for the canonical bridge-to-secret flow and file
  map

## Core doctrine
Default order:

1. inspect the normalized bridge-owned specs under `specs/`
2. separate bridge admission from secret materialization
3. keep upstream Premath doctrine and downstream runtime truth out of the same
   answer
4. use the schemas and examples as the concrete surface
5. propose the smallest domain-correct next slice

The core bridge flow is:

- external `AuthorizeRequest`
- authoritative `ProviderResults`
- assembled `PolicyInput`
- bridge decision and mode result
- `MaterializationPlanRequest`
- bounded `MaterializationSession`, handle, proxy, or denied session

## Workflow buckets

### 1) Bridge admission
Use when the task asks:
- what is the adapter contract?
- where does a field come from?
- what is trusted versus untrusted?
- how do burn and restore appear at the bridge boundary?

Default moves:
1. read `references/BRIDGE-FLOW.md`
2. inspect `specs/bridge-adapter/adapter-contract.md`
3. inspect `specs/bridge-adapter/provider-mapping.yaml`
4. inspect the narrow schema or example at issue

Goal:
Explain how the adapter turns caller input plus authoritative facts into bridge
policy input and decision artifacts.

### 2) Secret materialization boundary
Use when the task asks:
- how does bridge hand off to secrets?
- what is a `MaterializationPlanRequest`?
- what does a `MaterializationSession` authorize?
- when do we issue a handle, proxy, or bounded plaintext surface?

Default moves:
1. read `references/BRIDGE-FLOW.md`
2. inspect `specs/secrets/secret-0002/SECRET-0002.backend-and-materialization-profile.md`
3. inspect the `materialization-plan-request` and `materialization-session`
   schemas and examples

Goal:
Keep the answer on bounded issuance and teardown, not on generic secret
management slogans.

### 3) Realization profile boundary
Use when the task asks:
- how does bridge relate to Premath?
- what is `BRIDGE-PREMATH-0001`?
- what belongs in bridge versus upstream Premath?

Default moves:
1. read `references/BRIDGE-FLOW.md`
2. inspect `specs/bridge-premath-0001/BRIDGE-PREMATH-0001.premath-gluing-profile.md`
3. keep kernel doctrine upstream and bridge-specific gluing here

Goal:
Explain the bridge-specific realization profile without recentering Premath
kernel meaning in this repo.

### 4) Conformance and examples
Use when the task asks:
- do these specs still line up?
- what fixtures define the current surface?
- what should we verify after changing bridge-owned docs?

Default moves:
1. inspect the narrow examples and schemas involved
2. run `scripts/bridge-conformance-check.sh` after repo changes

Goal:
Keep the normalized bridge-owned surface coherent and reviewable.

## Boundary rules
- Treat caller input as untrusted until authoritative provider facts are
  resolved.
- Do not treat `accept` as ambient permission to expose reusable plaintext.
- Prefer bounded handles, proxies, or sessions over ambient plaintext power.
- Burn and mode changes dominate new session issuance and teardown behavior.
- Keep Premath kernel doctrine upstream in `fish/sites/premath/`.
- Keep live provider bindings, secret file paths, funded runtime, and local
  deployment proof in downstream repos.

## Deliverable shape
When answering with this skill, produce:

1. which bridge surface is in scope
2. the exact flow stage
3. the narrow spec, schema, or example to inspect
4. the domain boundary that stays out of scope
5. the next concrete validation step

## References
- Read `references/BRIDGE-FLOW.md` before expanding into repo-specific
  examples.
