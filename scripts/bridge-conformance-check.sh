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
  if python3 --version >/dev/null 2>&1; then
    python3 - "$@"
  else
    nix shell nixpkgs#python3Minimal --command python3 - "$@"
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
require_path "specs/secrets/README.md"
require_path "specs/secrets/secret-0001/SECRET-0001.secret-object-and-lifecycle-core.md"
require_path "specs/secrets/secret-0002/SHA256SUMS.txt"
require_path "specs/secrets/secret-0002/SIGNER-SESSION-CONTRACT.md"
require_path "specs/secrets/secret-0002/schemas/materialization-plan-request.schema.json"
require_path "specs/secrets/secret-0002/schemas/materialization-session.schema.json"
require_path "specs/secrets/secret-0002/schemas/session-open-artifact.schema.json"
require_path "specs/secrets/secret-0002/schemas/signature-request.schema.json"
require_path "specs/secrets/secret-0002/schemas/signature-response.schema.json"
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
require_text "specs/TYPE-FAMILIES.md" "SessionOpenArtifact"
require_text "specs/TYPE-FAMILIES.md" "SignatureRequest"
require_text "specs/TYPE-FAMILIES.md" "SignatureResponse"
require_text "specs/bridge-adapter/adapter-contract.md" "MaterializationPlanRequest"
require_text "specs/bridge-adapter/adapter-contract.md" "input.interpretation"
require_text "specs/bridge-adapter/interpretation-binding.md" "Normative carrier surface"
require_text "specs/bridge-premath-0001/BRIDGE-PREMATH-0001.premath-gluing-profile.md" "MaterializationPlanRequest"
require_text "specs/bridge-premath-0001/BRIDGE-PREMATH-0001.premath-gluing-profile.md" "consumer_kind"
require_text "specs/bridge-premath-0001/BRIDGE-PREMATH-0001.premath-gluing-profile.md" "act_for"
require_text "specs/secrets/secret-0002/SECRET-0002.backend-and-materialization-profile.md" "Bridge-to-secret handoff"
require_text "specs/secrets/secret-0002/SIGNER-SESSION-CONTRACT.md" "types-first"
require_text "specs/secrets/secret-0002/SIGNER-SESSION-CONTRACT.md" "SessionOpenArtifact"
require_text "specs/secrets/secret-0002/SIGNER-SESSION-CONTRACT.md" "SignatureRequest"
require_text "specs/secrets/secret-0002/SIGNER-SESSION-CONTRACT.md" "SignatureResponse"

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
