# Provider Plane Deploy Templates

Canonical deploy templates live under [`../../secret-0003/deploy/`](../../secret-0003/deploy/):

- [`nixos/bridge-sidecar.nix`](../../secret-0003/deploy/nixos/bridge-sidecar.nix)
- [`nixos/agent-service.nix`](../../secret-0003/deploy/nixos/agent-service.nix)
- [`darwin/bridge-sidecar.nix`](../../secret-0003/deploy/darwin/bridge-sidecar.nix)
- [`kubernetes/agent-worker.yaml`](../../secret-0003/deploy/kubernetes/agent-worker.yaml)

These templates demonstrate attachment to the provider-plane sidecar. Production
deployments still own real provider bindings, secret backend credentials, trust
roots, audit storage, and operator policy.
