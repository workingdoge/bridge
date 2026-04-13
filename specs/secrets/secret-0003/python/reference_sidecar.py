#!/usr/bin/env python3
"""
Reference sidecar for SECRET-0003.

This is a contract harness, not a production cryptographic implementation.
It validates JSON artifacts, checks provider/deployment consistency, and emits
a provider decision plus an audit envelope.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

import jsonschema


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_schema(schema_dir: Path, name: str) -> Dict[str, Any]:
    return load_json(schema_dir / name)


def validate(instance: Dict[str, Any], schema: Dict[str, Any]) -> None:
    jsonschema.validate(instance=instance, schema=schema)


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def parse_ts(ts: str) -> dt.datetime:
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return dt.datetime.fromisoformat(ts)


def canon(obj: Dict[str, Any]) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def find_binding(deployment: Dict[str, Any], secret_class: str) -> Dict[str, Any] | None:
    for binding in deployment["secret_class_bindings"]:
        if binding["secret_class"] == secret_class:
            return binding
    return None


def provider_by_id(catalog: Dict[str, Any], provider_id: str) -> Dict[str, Any] | None:
    for provider in catalog["providers"]:
        if provider["provider_id"] == provider_id:
            return provider
    return None


def check_provider_refs(catalog: Dict[str, Any], deployment: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    provider_ids = {p["provider_id"] for p in catalog["providers"]}
    required_refs = [
        deployment["providers"]["time_authority"],
        deployment["providers"]["revocation"],
        deployment["providers"]["attestation"],
        deployment["providers"]["mode_controller"],
        deployment["providers"]["audit_sink"],
    ]
    required_refs.extend(deployment["providers"].get("secret_backends", []))
    required_refs.extend(deployment["providers"].get("materializers", []))
    emergency = deployment["providers"].get("emergency_queue")
    if emergency:
        required_refs.append(emergency)
    for ref in required_refs:
        if ref not in provider_ids:
            errors.append(f"undeclared provider reference: {ref}")
    return errors


def make_decision(
    catalog: Dict[str, Any],
    deployment: Dict[str, Any],
    request: Dict[str, Any],
    attestation: Dict[str, Any],
    revocation: Dict[str, Any],
    mode: Dict[str, Any],
    now: dt.datetime | None = None,
) -> Dict[str, Any]:
    reasons: List[str] = []
    now = now or utc_now()

    # Deployment integrity checks.
    reasons.extend(check_provider_refs(catalog, deployment))

    if request["deployment_profile_id"] != deployment["deployment_profile_id"]:
        reasons.append("request deployment_profile_id does not match deployment profile")

    binding = find_binding(deployment, request["secret_class"])
    if not binding:
        reasons.append("no secret_class binding found")
        binding = {}

    mode_value = mode["mode"]

    # Burn dominates everything.
    if mode_value == "burn":
        return {
            "version": "0.1",
            "trace": request["trace"],
            "status": "burn",
            "deployment_profile_id": deployment["deployment_profile_id"],
            "mode": mode_value,
            "selected_backend_provider_id": binding.get("backend_provider_id"),
            "selected_materializer_provider_id": binding.get("materializer_provider_id"),
            "attestation_id": attestation.get("attestation_id"),
            "revocation_snapshot_id": revocation.get("snapshot_id"),
            "audit_required": True,
            "audit_sink_id": deployment["providers"]["audit_sink"],
            "reasons": sorted(set(reasons + ["burn mode active"])),
            "provider_facts": {
                "mode_epoch": mode["mode_epoch"],
                "controller_id": mode["controller_id"],
            },
        }

    if request["consumer_kind"] not in binding.get("allowed_consumer_kinds", []):
        reasons.append("consumer kind not allowed by binding")

    if request["requested_ttl_s"] > binding.get("max_ttl_s", 0):
        reasons.append("requested ttl exceeds binding limit")

    expected_method = None
    selected_materializer = binding.get("materializer_provider_id")
    if selected_materializer:
        materializer_provider = provider_by_id(catalog, selected_materializer)
        if materializer_provider:
            family = materializer_provider.get("product_family")
            mapping = {
                "systemd-credential": "systemd-credential",
                "unix-socket-proxy": "unix-socket-proxy",
                "memfd-pass": "memfd-pass",
                "agent-proxy": "agent-proxy",
                "tmpfs-file": "tmpfs-file",
                "os-keychain-ref": "os-keychain-ref",
            }
            expected_method = mapping.get(family)
    if expected_method and request["requested_method"] != expected_method:
        reasons.append("requested method does not match binding materializer")

    attestation_exp = parse_ts(attestation["expires_at"])
    if attestation["subject_id"] != request["subject_id"]:
        reasons.append("attestation subject mismatch")
    if attestation["status"] != "verified":
        reasons.append("attestation not verified")
    if attestation["posture_digest"] != request["required_posture_digest"]:
        reasons.append("posture digest mismatch")
    if attestation_exp <= now:
        reasons.append("attestation expired")

    rev_fresh_until = parse_ts(revocation["fresh_until"])
    if rev_fresh_until <= now:
        reasons.append("revocation snapshot stale")
    if request["secret_ref"] in set(revocation.get("revoked_secret_versions", [])):
        reasons.append("secret version explicitly revoked")
    for entry in revocation.get("revoked_secret_versions", []):
        if entry.startswith(request["secret_ref"] + "#"):
            reasons.append("secret ref has revoked version in active epoch")
            break

    # Provider readiness and fail-closed expectations.
    backend_provider_id = binding.get("backend_provider_id")
    if backend_provider_id and backend_provider_id not in deployment["providers"].get("secret_backends", []):
        reasons.append("backend provider not allowed by deployment")
    if selected_materializer and selected_materializer not in deployment["providers"].get("materializers", []):
        reasons.append("materializer provider not allowed by deployment")

    audit_sink_id = deployment["providers"]["audit_sink"]
    if not provider_by_id(catalog, audit_sink_id):
        reasons.append("audit sink missing from catalog")

    if reasons:
        return {
            "version": "0.1",
            "trace": request["trace"],
            "status": "deny",
            "deployment_profile_id": deployment["deployment_profile_id"],
            "mode": mode_value,
            "selected_backend_provider_id": backend_provider_id,
            "selected_materializer_provider_id": selected_materializer,
            "attestation_id": attestation.get("attestation_id"),
            "revocation_snapshot_id": revocation.get("snapshot_id"),
            "audit_required": True,
            "audit_sink_id": audit_sink_id,
            "reasons": sorted(set(reasons)),
            "provider_facts": {
                "mode_epoch": mode["mode_epoch"],
                "controller_id": mode["controller_id"],
                "attestation_status": attestation["status"],
                "revocation_snapshot_fresh_until": revocation["fresh_until"],
            },
        }

    expires = now + dt.timedelta(seconds=request["requested_ttl_s"])
    return {
        "version": "0.1",
        "trace": request["trace"],
        "status": "accept",
        "deployment_profile_id": deployment["deployment_profile_id"],
        "mode": mode_value,
        "selected_backend_provider_id": backend_provider_id,
        "selected_materializer_provider_id": selected_materializer,
        "attestation_id": attestation.get("attestation_id"),
        "revocation_snapshot_id": revocation.get("snapshot_id"),
        "audit_required": True,
        "audit_sink_id": audit_sink_id,
        "session_expires_at": expires.isoformat().replace("+00:00", "Z"),
        "reasons": [],
        "provider_facts": {
            "mode_epoch": mode["mode_epoch"],
            "controller_id": mode["controller_id"],
            "binding_secret_class": request["secret_class"],
            "requested_method": request["requested_method"],
        },
    }


def build_audit_envelope(
    decision: Dict[str, Any],
    source_id: str,
    stream_id: str,
    sequence: int,
    prev_event_hash: str,
    now: dt.datetime | None = None,
) -> Dict[str, Any]:
    decision_payload = {
        "trace": decision["trace"],
        "status": decision["status"],
        "deployment_profile_id": decision["deployment_profile_id"],
        "mode": decision["mode"],
        "selected_backend_provider_id": decision.get("selected_backend_provider_id"),
        "selected_materializer_provider_id": decision.get("selected_materializer_provider_id"),
        "reasons": decision["reasons"],
    }
    payload_hash = sha256_hex(canon(decision_payload))
    event_core = {
        "version": "0.1",
        "stream_id": stream_id,
        "sequence": sequence,
        "prev_event_hash": prev_event_hash,
        "emitted_at": (now or utc_now()).isoformat().replace("+00:00", "Z"),
        "source_id": source_id,
        "trace": decision["trace"],
        "event_type": {
            "accept": "decision.allow",
            "deny": "decision.deny",
            "burn": "decision.burn",
        }[decision["status"]],
        "payload_hash": payload_hash,
        "labels": [],
        "decision_status": decision["status"],
        "notes": "",
    }
    event_hash = sha256_hex(canon(event_core))
    event_core["event_hash"] = event_hash
    return event_core


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--deployment", required=True, type=Path)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--attestation", required=True, type=Path)
    parser.add_argument("--revocation", required=True, type=Path)
    parser.add_argument("--mode", required=True, type=Path)
    parser.add_argument("--schema-dir", type=Path, default=Path(__file__).resolve().parent.parent / "schemas")
    parser.add_argument("--decision-out", required=True, type=Path)
    parser.add_argument("--audit-out", required=True, type=Path)
    parser.add_argument("--stream-id", default="audit-stream-main")
    parser.add_argument("--now", help="Override current time as RFC3339/ISO-8601 UTC timestamp")
    parser.add_argument("--sequence", type=int, default=1)
    parser.add_argument("--prev-hash", default="sha256:0000000000000000000000000000000000000000000000000000000000000000")
    args = parser.parse_args()

    catalog = load_json(args.catalog)
    deployment = load_json(args.deployment)
    request = load_json(args.request)
    attestation = load_json(args.attestation)
    revocation = load_json(args.revocation)
    mode = load_json(args.mode)

    validate(catalog, load_schema(args.schema_dir, "provider-catalog.schema.json"))
    validate(deployment, load_schema(args.schema_dir, "deployment-profile.schema.json"))
    validate(request, load_schema(args.schema_dir, "provider-request.schema.json"))
    validate(attestation, load_schema(args.schema_dir, "attestation-result.schema.json"))
    validate(revocation, load_schema(args.schema_dir, "revocation-snapshot.schema.json"))
    validate(mode, load_schema(args.schema_dir, "mode-state.schema.json"))

    now_override = parse_ts(args.now) if args.now else None

    decision = make_decision(catalog, deployment, request, attestation, revocation, mode, now=now_override)
    validate(decision, load_schema(args.schema_dir, "provider-decision.schema.json"))

    audit = build_audit_envelope(
        decision=decision,
        source_id=deployment["providers"]["audit_sink"],
        stream_id=args.stream_id,
        sequence=args.sequence,
        prev_event_hash=args.prev_hash,
        now=now_override,
    )
    validate(audit, load_schema(args.schema_dir, "audit-envelope.schema.json"))

    args.decision_out.write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")
    args.audit_out.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
