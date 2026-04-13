# Provenance

This repo was bootstrapped from three source bundles already present in the
local workspace:

- `/Users/arj/irai/bridge_spec_v0_2_adapter_bundle.zip`
- `/Users/arj/irai/secret_suite_v1_full_bundle.zip`
- `/Users/arj/irai/fish/sites/premath/references/secret_suite_v1_full_plus_premath_bundle.zip`

Authority split:

- Premath kernel doctrine remains upstream in `fish/sites/premath/`.
- `bridge` owns the normalized domain surface imported under `specs/`.
- `references/source-bundles/` retains the original bundle artifacts for
  provenance and audit, not as the active authority surface.

Import policy:

- import `bridge_spec_v0_2_adapter/` from the standalone adapter bundle as the
  bridge adapter source of truth
- import `secret_0001/`, `secret_0002/`, and `secret_0003/` from the secret
  suite bundle
- import `bridge_premath_0001/` from the Premath-profile bundle
- do not re-import duplicated `bridge_spec_v0_2*` trees from the secret suite
  bundles when the standalone adapter bundle already provides the cleaner source
