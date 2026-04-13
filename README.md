# Bridge

`bridge` is the domain home for the bridge adapter contract, the secret suite,
and bridge-specific realization profiles layered over Premath.

Boundary:

- Premath kernel doctrine stays upstream in `fish/sites/premath/`.
- This repo owns domain-specific bridge and secret specs plus their
  normalization and conformance surfaces.
- Live provider bindings, funded runtime, and first proof stay in downstream
  consumer repos until they generalize.

Repo map:

- `specs/` normalized active spec surface
- `references/source-bundles/` retained source bundles for provenance
- `scripts/bridge-conformance-check.sh` repo-owned conformance check
- `PROVENANCE.md` authority split and import record

Workflow:

- use `bd ready --json`
- claim with `bd update <id> --claim --json`
- close with `bd close <id> --reason "..." --json`
- run `scripts/bridge-conformance-check.sh` after spec-surface changes
