# Specs

`specs/` is the active normalized surface for the bridge domain stack.

Current layout:

- `TYPE-FAMILIES.md` canonical map of the stable bridge type families
- `bridge-adapter/` bridge adapter contract, schemas, examples, and mapping
- `secrets/secret-0001/` secret object and lifecycle core
- `secrets/secret-0002/` backend and materialization profile
- `secrets/secret-0003/` provider integration, attestation, audit, deployment
- `bridge-premath-0001/` bridge-specific Premath realization profile

Rules:

- preserve imported filenames inside each spec family unless there is a strong
  reason to normalize them
- organize new exported interfaces around the stable type families in
  `TYPE-FAMILIES.md`, not around vendor names
- keep domain doctrine and examples here, not in `references/`
- do not treat this repo as the home of Premath kernel doctrine
- validate the staged surface with `scripts/bridge-conformance-check.sh`
