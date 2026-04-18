#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: bridge-property-check.sh [--repo <path>]

Runs the repo-owned semantic property checks for the bridge-to-secret planner:
- non-accept bridge decisions deny usable materialization sessions
- burn mode denies new sessions
- host/process attestation failures deny
- request-to-binding mismatches deny
- zero secret-materialization budget denies
- issued TTL never exceeds the effective bound
- non-exportable authority does not widen into forbidden plaintext-capable surfaces
- non-admitted interpretation states never assemble into policy input
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

property_script="$repo_root/specs/secrets/secret-0002/python/reference_planner_properties.py"
[[ -f "$property_script" ]] || { echo "missing property script: $property_script" >&2; exit 1; }
adapter_property_script="$repo_root/specs/bridge-adapter/python/reference_adapter_properties.py"
[[ -f "$adapter_property_script" ]] || { echo "missing property script: $adapter_property_script" >&2; exit 1; }

run_property_python() {
  local script_path="$1"
  if python3 --version >/dev/null 2>&1 && python3 -c 'import hypothesis, jsonschema' >/dev/null 2>&1; then
    python3 "$script_path"
  else
    nix shell --impure \
      --expr '(let pkgs = import <nixpkgs> {}; in pkgs.python3.withPackages (ps: with ps; [ hypothesis jsonschema ]))' \
      --command python "$script_path"
  fi
}

run_property_python "$property_script"
run_property_python "$adapter_property_script"
