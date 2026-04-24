#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: bridge-conformance-check.sh [--repo <path>]

Checks the repo-owned bridge contract surface:
- required authority/shape files exist
- required shared-skill files exist
- authority split text is present
- JSON contracts and examples under specs/ parse cleanly
- checksum manifests match the files they govern
EOF
}

repo_root=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      [[ $# -ge 2 ]] || { echo "missing value for --repo" >&2; exit 2; }
      repo_root=$(cd "$2" && pwd)
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$repo_root" ]]; then
  repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
fi

cd "$repo_root"

require_path() {
  local path="$1"
  [[ -e "$path" ]] || { echo "missing required path: $path" >&2; exit 1; }
}

require_text() {
  local path="$1"
  local needle="$2"
  rg -Fq "$needle" "$path" || {
    echo "missing required text in $path: $needle" >&2
    exit 1
  }
}

run_python() {
  if python3 --version >/dev/null 2>&1 && python3 -c 'import jsonschema' >/dev/null 2>&1; then
    python3 - "$@"
  else
    nix shell --impure \
      --expr '(let pkgs = import <nixpkgs> {}; in pkgs.python3.withPackages (ps: with ps; [ jsonschema ]))' \
      --command python3 - "$@"
  fi
}

require_path "README.md"
require_path "PROVENANCE.md"
require_path "AGENTS.md"
require_path ".agents/skills/bridge/SKILL.md"
require_path ".agents/skills/bridge/references/BRIDGE-FLOW.md"
require_path "references/source-bundles/SHA256SUMS.txt"
require_path "specs/README.md"
require_path "specs/TYPE-FAMILIES.md"
require_path "specs/bridge-adapter/SHA256SUMS.txt"
require_path "specs/bridge-adapter/adapter-contract.md"
require_path "specs/bridge-adapter/interpretation-binding.md"
require_path "specs/bridge-adapter/schemas/source-context.schema.json"
require_path "specs/bridge-adapter/schemas/interpretation-binding.schema.json"
require_path "specs/bridge-adapter/schemas/interpreted-observation.schema.json"
require_path "specs/bridge-adapter/schemas/interpretation-result.schema.json"
require_path "specs/bridge-adapter/examples/example.provider-results.unknown.json"
require_path "specs/bridge-adapter/examples/example.provider-results.ambiguous.json"
require_path "specs/bridge-adapter/examples/example.provider-results.stale.json"
require_path "specs/bridge-premath-0001/SHA256SUMS.txt"
require_path "specs/bridge-premath-0001/BRIDGE-PREMATH-0001.premath-gluing-profile.md"
require_path "specs/bridge-premath-0001/secret-bound-execution-bundle.md"
require_path "specs/bridge-premath-0001/examples/example.glued-bundle.burn-obstruction.json"
require_path "specs/secrets/README.md"
require_path "specs/secrets/SUITE-FLOW.md"
require_path "specs/secrets/core/README.md"
require_path "specs/secrets/core/secret-object.md"
require_path "specs/secrets/core/lifecycle.md"
require_path "specs/secrets/core/class-policy.md"
require_path "specs/secrets/core/schemas/README.md"
require_path "specs/secrets/materialization/README.md"
require_path "specs/secrets/materialization/backend-profiles.md"
require_path "specs/secrets/materialization/materializer-profiles.md"
require_path "specs/secrets/materialization/bindings.md"
require_path "specs/secrets/materialization/plan-request.md"
require_path "specs/secrets/materialization/session.md"
require_path "specs/secrets/materialization/signer-session.md"
require_path "specs/secrets/materialization/witness-realization.md"
require_path "specs/secrets/materialization/schemas/README.md"
require_path "specs/secrets/materialization/examples/README.md"
require_path "specs/secrets/provider-plane/README.md"
require_path "specs/secrets/provider-plane/provider-catalog.md"
require_path "specs/secrets/provider-plane/deployment-profile.md"
require_path "specs/secrets/provider-plane/attestation.md"
require_path "specs/secrets/provider-plane/revocation.md"
require_path "specs/secrets/provider-plane/mode.md"
require_path "specs/secrets/provider-plane/audit.md"
require_path "specs/secrets/provider-plane/sidecar-api.md"
require_path "specs/secrets/provider-plane/schemas/README.md"
require_path "specs/secrets/provider-plane/examples/README.md"
require_path "specs/secrets/provider-plane/deploy/README.md"
require_path "specs/secrets/secret-0001/SECRET-0001.secret-object-and-lifecycle-core.md"
require_path "specs/secrets/secret-0002/SHA256SUMS.txt"
require_path "specs/secrets/secret-0002/SIGNER-SESSION-CONTRACT.md"
require_path "specs/secrets/secret-0002/WITNESS-REALIZATION-CONTRACT.md"
require_path "specs/secrets/secret-0002/schemas/materialization-plan-request.schema.json"
require_path "specs/secrets/secret-0002/schemas/materialization-session.schema.json"
require_path "specs/secrets/secret-0002/schemas/signature-request.schema.json"
require_path "specs/secrets/secret-0002/schemas/signature-response.schema.json"
require_path "specs/secrets/secret-0002/schemas/witness-realization-record.schema.json"
require_path "specs/secrets/secret-0002/examples/example.witness-realization.signing-key.json"
require_path "specs/secrets/secret-0003/SHA256SUMS.txt"
require_path "scripts/bridge-conformance-check.sh"

require_text "README.md" "Premath kernel doctrine stays upstream"
require_text "README.md" "Ingress"
require_text "PROVENANCE.md" '`bridge` owns the normalized domain surface imported under `specs/`.'
require_text "AGENTS.md" '`references/source-bundles/` holds imported source bundles for provenance only.'
require_text ".agents/skills/bridge/SKILL.md" "MaterializationPlanRequest"
require_text ".agents/skills/bridge/SKILL.md" "MaterializationSession"
require_text ".agents/skills/bridge/SKILL.md" "Realization"
require_text ".agents/skills/bridge/references/BRIDGE-FLOW.md" "scripts/bridge-conformance-check.sh"
require_text "specs/TYPE-FAMILIES.md" "Authority"
require_text "specs/TYPE-FAMILIES.md" "Interpretation"
require_text "specs/TYPE-FAMILIES.md" "Admission"
require_text "specs/TYPE-FAMILIES.md" "Secret Core"
require_text "specs/TYPE-FAMILIES.md" "Realization"
require_text "specs/TYPE-FAMILIES.md" "Audit"
require_text "specs/TYPE-FAMILIES.md" "SignatureRequest"
require_text "specs/TYPE-FAMILIES.md" "SignatureResponse"
require_text "specs/bridge-adapter/adapter-contract.md" "MaterializationPlanRequest"
require_text "specs/bridge-adapter/adapter-contract.md" "input.interpretation"
require_text "specs/bridge-adapter/interpretation-binding.md" "Normative carrier surface"
require_text "specs/bridge-premath-0001/BRIDGE-PREMATH-0001.premath-gluing-profile.md" "MaterializationPlanRequest"
require_text "specs/bridge-premath-0001/BRIDGE-PREMATH-0001.premath-gluing-profile.md" "consumer_kind"
require_text "specs/bridge-premath-0001/BRIDGE-PREMATH-0001.premath-gluing-profile.md" "act_for"
require_text "specs/bridge-premath-0001/secret-bound-execution-bundle.md" "fibre-bundle view"
require_text "specs/bridge-premath-0001/secret-bound-execution-bundle.md" "obstruction to a usable materialization section"
require_text "specs/secrets/README.md" "SECRET-0001 SecretObject / SecretVersion"
require_text "specs/secrets/SUITE-FLOW.md" "The order is not numeric at runtime"
require_text "specs/secrets/SUITE-FLOW.md" "Adjacent Request Types"
require_text "specs/secrets/core/README.md" "Secret Core"
require_text "specs/secrets/materialization/README.md" "bridge-to-secret realization"
require_text "specs/secrets/provider-plane/README.md" "authoritative runtime facts"
require_text "specs/secrets/secret-0002/SECRET-0002.backend-and-materialization-profile.md" "Bridge-to-secret handoff"
require_text "specs/secrets/secret-0002/SIGNER-SESSION-CONTRACT.md" "types-first"
require_text "specs/secrets/secret-0002/SIGNER-SESSION-CONTRACT.md" "SignatureRequest"
require_text "specs/secrets/secret-0002/SIGNER-SESSION-CONTRACT.md" "SignatureResponse"
require_text "specs/secrets/secret-0002/WITNESS-REALIZATION-CONTRACT.md" "WitnessRealizationRecord"
require_text "specs/secrets/secret-0002/WITNESS-REALIZATION-CONTRACT.md" "ValidationResult"

run_python "$repo_root" <<'PY'
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def check_json_tree(base: Path) -> int:
    count = 0
    for path in sorted(base.rglob("*.json")):
        try:
            json.loads(path.read_text())
        except Exception as exc:  # pragma: no cover - shell surfaced
            fail(f"invalid json: {path}: {exc}")
        count += 1
    return count


def verify_manifest(manifest_path: Path) -> int:
    base = manifest_path.parent
    lines = [line.strip() for line in manifest_path.read_text().splitlines() if line.strip()]
    listed: set[str] = set()
    checked = 0

    for line in lines:
        parts = line.split(None, 1)
        if len(parts) != 2:
            fail(f"malformed manifest line in {manifest_path}: {line}")
        expected_hash, rel = parts
        rel = rel.strip()
        if rel.startswith("./"):
            rel = rel[2:]
        if rel == manifest_path.name:
            # SECRET-0003 upstream includes a self-line; ignore it.
            continue
        target = base / rel
        if not target.is_file():
            fail(f"manifest entry missing file in {manifest_path}: {rel}")
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        if digest != expected_hash:
            fail(f"manifest hash mismatch in {manifest_path}: {rel}")
        listed.add(rel)
        checked += 1

    actual = {
        path.relative_to(base).as_posix()
        for path in base.rglob("*")
        if path.is_file()
        and path.name != manifest_path.name
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
    }
    missing = sorted(actual - listed)
    if missing:
        fail(f"manifest coverage gap in {manifest_path}: {', '.join(missing)}")
    return checked


json_count = check_json_tree(root / "specs")
manifest_count = 0
checked_entries = 0
for manifest in [
    root / "references/source-bundles/SHA256SUMS.txt",
    root / "specs/bridge-adapter/SHA256SUMS.txt",
    root / "specs/bridge-premath-0001/SHA256SUMS.txt",
    root / "specs/secrets/secret-0002/SHA256SUMS.txt",
    root / "specs/secrets/secret-0003/SHA256SUMS.txt",
]:
    manifest_count += 1
    checked_entries += verify_manifest(manifest)

print(
    json.dumps(
        {
            "ok": True,
            "json_files_checked": json_count,
            "manifests_checked": manifest_count,
            "manifest_entries_checked": checked_entries,
            "note": "secret-0001 is intentionally present without a checksum manifest",
        },
        indent=2,
    )
)
PY

run_python "$repo_root" <<'PY'
from __future__ import annotations

import json
import hashlib
import sys
from pathlib import Path

root = Path(sys.argv[1])
secret = root / "specs" / "secrets" / "secret-0002"
sys.path.insert(0, str(secret / "python"))

import reference_planner


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def load(name: str) -> dict:
    return json.loads((secret / "examples" / name).read_text())


CASES = [
    (
        "analytics allow",
        "example.backend-profile.vault-dynamic.json",
        "example.materializer-profile.systemd-credential.json",
        "example.backend-binding.analytics-db.json",
        "example.plan-request.analytics-db.json",
        "generated.materialization-session.allow.json",
    ),
    (
        "analytics burn",
        "example.backend-profile.vault-dynamic.json",
        "example.materializer-profile.systemd-credential.json",
        "example.backend-binding.analytics-db.json",
        "example.plan-request.burn.json",
        "generated.materialization-session.deny.json",
    ),
    (
        "signing allow",
        "example.backend-profile.hsm-rooted-signing.json",
        "example.materializer-profile.unix-socket-proxy.json",
        "example.backend-binding.signing-key.json",
        "example.plan-request.signing-key.json",
        "generated.materialization-session.signing-key.allow.json",
    ),
]

now = reference_planner.parse_utc("2026-04-13T14:30:00Z")

for label, backend_name, materializer_name, binding_name, request_name, expected_name in CASES:
    actual = reference_planner.plan_session(
        load(backend_name),
        load(materializer_name),
        load(binding_name),
        load(request_name),
        now=now,
    )
    expected = load(expected_name)
    if actual != expected:
        fail(f"SECRET-0002 generated fixture drift: {label} does not match {expected_name}")

signing_session = load("generated.materialization-session.signing-key.allow.json")
signature_request = load("example.signature-request.signing-key.json")
signature_response = load("generated.signature-response.signing-key.allow.json")
witness = load("example.witness-realization.signing-key.json")

if signature_request["session_id"] != signing_session["session_id"]:
    fail("SECRET-0002 signer request session_id does not match generated signing session")
if signature_request["bridge_trace"] != signing_session["bridge_trace"]:
    fail("SECRET-0002 signer request bridge_trace does not match generated signing session")
if signature_response["session_id"] != signing_session["session_id"]:
    fail("SECRET-0002 signature response session_id does not match generated signing session")
if signature_response["bridge_trace"] != signing_session["bridge_trace"]:
    fail("SECRET-0002 signature response bridge_trace does not match generated signing session")
if signature_response["signer_identity"]["key_ref"] != signing_session["backend_operation"]["ref"]:
    fail("SECRET-0002 signature response key_ref does not match generated signing backend operation")
if witness["bridge_trace"] != signing_session["bridge_trace"]:
    fail("SECRET-0002 witness bridge_trace does not match generated signing session")
if witness["state_read"]["materialization_session_ref"] != signing_session["session_id"]:
    fail("SECRET-0002 witness session ref does not match generated signing session")
signature_response_digest = hashlib.sha256((secret / "examples" / "generated.signature-response.signing-key.allow.json").read_bytes()).hexdigest()
if witness["witness_artifact"]["artifact_digest"]["value"] != signature_response_digest:
    fail("SECRET-0002 witness artifact digest does not match generated signature response")

print(json.dumps({
    "ok": True,
    "secret_0002_generated_sessions_checked": len(CASES),
    "secret_0002_signer_lineage_checked": True,
}, indent=2))
PY

run_python "$repo_root" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
secret = root / "specs" / "secrets" / "secret-0003"
examples = secret / "examples"
schema_dir = secret / "schemas"
sys.path.insert(0, str(secret / "python"))

import reference_sidecar


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def load(name: str) -> dict:
    return json.loads((examples / name).read_text())


def schema(name: str) -> dict:
    return json.loads((schema_dir / name).read_text())


SCHEMAS = {
    "catalog": schema("provider-catalog.schema.json"),
    "deployment": schema("deployment-profile.schema.json"),
    "request": schema("provider-request.schema.json"),
    "attestation": schema("attestation-result.schema.json"),
    "revocation": schema("revocation-snapshot.schema.json"),
    "mode": schema("mode-state.schema.json"),
    "decision": schema("provider-decision.schema.json"),
    "audit": schema("audit-envelope.schema.json"),
}

CASES = [
    (
        "accept",
        "provider-request.allow.json",
        "attestation-result.good.json",
        "revocation-snapshot.clean.json",
        "mode-state.normal.json",
        "generated.provider-decision.accept.json",
        "generated.audit-envelope.accept.json",
    ),
    (
        "burn",
        "provider-request.burn.json",
        "attestation-result.good.json",
        "revocation-snapshot.clean.json",
        "mode-state.burn.json",
        "generated.provider-decision.burn.json",
        "generated.audit-envelope.burn.json",
    ),
    (
        "deny",
        "provider-request.allow.json",
        "attestation-result.failed.json",
        "revocation-snapshot.clean.json",
        "mode-state.normal.json",
        "generated.provider-decision.deny.json",
        "generated.audit-envelope.deny.json",
    ),
]

catalog = load("provider-catalog.example.json")
deployment = load("deployment-profile.nixos-host.json")
reference_sidecar.validate(catalog, SCHEMAS["catalog"])
reference_sidecar.validate(deployment, SCHEMAS["deployment"])

now = reference_sidecar.parse_ts("2026-04-13T14:30:30Z")
prev_hash = "sha256:0000000000000000000000000000000000000000000000000000000000000000"

for label, request_name, attestation_name, revocation_name, mode_name, expected_decision_name, expected_audit_name in CASES:
    request = load(request_name)
    attestation = load(attestation_name)
    revocation = load(revocation_name)
    mode = load(mode_name)

    reference_sidecar.validate(request, SCHEMAS["request"])
    reference_sidecar.validate(attestation, SCHEMAS["attestation"])
    reference_sidecar.validate(revocation, SCHEMAS["revocation"])
    reference_sidecar.validate(mode, SCHEMAS["mode"])

    decision = reference_sidecar.make_decision(
        catalog,
        deployment,
        request,
        attestation,
        revocation,
        mode,
        now=now,
    )
    reference_sidecar.validate(decision, SCHEMAS["decision"])
    expected_decision = load(expected_decision_name)
    if decision != expected_decision:
        fail(f"SECRET-0003 generated decision fixture drift: {label} does not match {expected_decision_name}")

    audit = reference_sidecar.build_audit_envelope(
        decision=decision,
        source_id=deployment["providers"]["audit_sink"],
        stream_id="audit-stream-main",
        sequence=1,
        prev_event_hash=prev_hash,
        now=now,
    )
    reference_sidecar.validate(audit, SCHEMAS["audit"])
    expected_audit = load(expected_audit_name)
    if audit != expected_audit:
        fail(f"SECRET-0003 generated audit fixture drift: {label} does not match {expected_audit_name}")

print(json.dumps({
    "ok": True,
    "secret_0003_provider_decisions_checked": len(CASES),
    "secret_0003_audit_envelopes_checked": len(CASES),
}, indent=2))
PY
