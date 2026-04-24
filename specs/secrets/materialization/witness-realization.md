# Witness Realization

Canonical source:

- [`WITNESS-REALIZATION-CONTRACT.md`](../secret-0002/WITNESS-REALIZATION-CONTRACT.md)
- [`witness-realization-record.schema.json`](../secret-0002/schemas/witness-realization-record.schema.json)

`WitnessRealizationRecord` is bridge-local coherence metadata over existing
session, signer, audit, and validation artifacts.

It names:

- the challenge;
- state read before action selection;
- selected bridge-domain action;
- witness plan and artifact reference;
- validator profile;
- validation result;
- next session state or receipt reference.

It does not replace `MaterializationSession`, `SignatureRequest`,
`SignatureResponse`, audit records, or upstream Premath witness doctrine.
