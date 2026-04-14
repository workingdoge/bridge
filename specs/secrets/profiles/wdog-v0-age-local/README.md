# wdog-v0-age-local

Profile instance for workingdoge-LLC's v0 primary host operational secrets.

See `PROFILE.md` for the SECRET-0002 conformance shape:
- BackendProfile = age-encrypted files on local disk
- MaterializerProfile = file-backed handle
- BackendBinding schema = per-secret path/owner/group/mode/recipients
- MaterializationSession schema = v0 admits implicitly; live runtime is
  future retrofit

Consumed by:
- `fish/sites/workingdoge/cloud/host/secrets.nix` (workingdoge lane E.4).

Not consumed by home's `arj` darwin host (home uses a different profile
— agenix-rekey + Yubikey — which would be a separate profile instance
when it gets formalized).
