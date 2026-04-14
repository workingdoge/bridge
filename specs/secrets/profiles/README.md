# Secret Profile Instances

This directory holds concrete BackendProfile × MaterializerProfile ×
BackendBinding profile instances that satisfy the SECRET-0002 conformance
requirement:

> A conforming implementation SHALL define
>   one `BackendProfile`,
>   one `MaterializerProfile`,
>   one `BackendBinding` for each managed secret or secret class,
>   one `MaterializationSession` record for each issued or denied session.

Each subdirectory is one profile instance, named for the consumer + version
+ dominant characteristic. Downstream repos (workingdoge, home, aac, etc.)
that operationalize secrets SHOULD name the profile they instantiate by
directory name, cross-referenced from their runtime code.

## Current instances

- `wdog-v0-age-local/` — workingdoge-LLC v0 primary host. Age-encrypted
  files on local disk, read-gated by OS file permissions, file-backed
  handle as the materialization artifact.

## Authoring a new profile

1. Pick a directory name: `<consumer>-<version>-<shape>`.
2. Author `PROFILE.md` naming the four SECRET-0002 concepts concretely.
3. Add a short `README.md` if the profile needs operator-facing context.
4. Cross-reference from the consuming repo's runtime code (NixOS module,
   application config, etc.) by profile directory name.
5. When the profile's scope expands beyond v0 (e.g. adds a second
   backend, or materializes sessions through a runtime), bump the
   version suffix and file a new directory rather than editing in place.
