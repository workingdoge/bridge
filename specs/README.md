# Specs

`specs/` is the active normalized surface for the bridge domain stack.

Current layout:

- `bridge-adapter/` bridge adapter contract, schemas, examples, and mapping
- `secrets/secret-0001/` secret object and lifecycle core
- `secrets/secret-0002/` backend and materialization profile
- `secrets/secret-0003/` provider integration, attestation, audit, deployment
- `bridge-premath-0001/` bridge-specific Premath realization profile

Rules:

- preserve imported filenames inside each spec family unless there is a strong
  reason to normalize them
- keep domain doctrine and examples here, not in `references/`
- do not treat this repo as the home of Premath kernel doctrine
