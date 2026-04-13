#!/usr/bin/env python3
"""
Reference validator for SECRET-0001.
This is a contract/invariant harness, not a production cryptographic implementation.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {
    "secret_object": ROOT / "schemas" / "secret-object.schema.json",
    "secret_event": ROOT / "schemas" / "secret-event.schema.json",
    "mat_req": ROOT / "schemas" / "materialization-request.schema.json",
    "mat_grant": ROOT / "schemas" / "materialization-grant.schema.json",
}


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def load_schema(name: str) -> Dict[str, Any]:
    return load_json(SCHEMAS[name])


def iso_to_dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)


def validate_schema(name: str, payload: Dict[str, Any]) -> None:
    jsonschema.validate(payload, load_schema(name))


def walk_forbidden_plaintext(value: Any, path: str = "$") -> List[str]:
    """
    Reject common obvious plaintext field names in metadata-like records.
    This is intentionally conservative.
    """
    bad = []
    if isinstance(value, dict):
        for k, v in value.items():
            key = k.lower()
            if key in {"plaintext", "secret_value", "private_key", "password_value", "token_value"}:
                bad.append(f"{path}.{k}")
            bad.extend(walk_forbidden_plaintext(v, f"{path}.{k}"))
    elif isinstance(value, list):
        for i, item in enumerate(value):
            bad.extend(walk_forbidden_plaintext(item, f"{path}[{i}]"))
    return bad


def validate_secret_object(obj: Dict[str, Any]) -> List[str]:
    validate_schema("secret_object", obj)
    errors: List[str] = []

    bad_fields = walk_forbidden_plaintext(obj)
    if bad_fields:
        errors.append(f"forbidden plaintext-like field(s) present: {', '.join(bad_fields)}")

    versions = obj["versions"]
    active_versions = [v for v in versions if v["state"] == "active"]

    max_active = obj["lifecycle_policy"].get("max_simultaneous_active_versions", 1)
    if len(active_versions) > max_active:
        errors.append(
            f"active version count {len(active_versions)} exceeds policy max_simultaneous_active_versions {max_active}"
        )

    for v in versions:
        state = v["state"]
        created_at = iso_to_dt(v["created_at"])
        expires_at = iso_to_dt(v["expires_at"]) if "expires_at" in v else None
        if expires_at and expires_at < created_at:
            errors.append(f"version {v['version_id']} expires before it was created")

        if state == "active":
            if "activated_at" not in v:
                errors.append(f"active version {v['version_id']} lacks activated_at")
            if v["storage_ref"]["plaintext_persisted"] is not False:
                errors.append(f"active version {v['version_id']} must declare plaintext_persisted=false")
            if "mode" not in v["protection"]:
                errors.append(f"active version {v['version_id']} lacks protection mode")

        if state == "revoked" and "revoked_at" not in v:
            errors.append(f"revoked version {v['version_id']} lacks revoked_at")
        if state == "destroyed" and "destroyed_at" not in v:
            errors.append(f"destroyed version {v['version_id']} lacks destroyed_at")

    rcv = obj["recovery_policy"]
    if obj["secret_class"] in {"wrapping-key", "recovery-share"}:
        if rcv.get("restore_approval_mode") != "dual":
            errors.append(f"{obj['secret_class']} requires restore_approval_mode=dual")
        if rcv.get("escrow_mode") not in {"split-knowledge", "quorum-shares"}:
            errors.append(f"{obj['secret_class']} requires split-knowledge or quorum-shares escrow_mode")

    if "env-var" in obj["materialization_policy"]["allowed_methods"] and obj["materialization_policy"]["exportable"]:
        errors.append("env-var materialization cannot be combined with exportable=true")

    if not obj["materialization_policy"]["reentry_to_model_prohibited"]:
        errors.append("reentry_to_model_prohibited must be true for this reference profile")
    if not obj["materialization_policy"]["log_export_prohibited"]:
        errors.append("log_export_prohibited must be true for this reference profile")

    return errors


def authorize_materialization(secret_obj: Dict[str, Any], request: Dict[str, Any], bridge_epoch: int = 0) -> Dict[str, Any]:
    validate_schema("secret_object", secret_obj)
    validate_schema("mat_req", request)

    deny: List[str] = []

    if request["mode"] == "burn":
        deny.append("bridge mode burn denies materialization")

    allowed_methods = set(secret_obj["materialization_policy"]["allowed_methods"])
    if request["requested_method"] not in allowed_methods:
        deny.append("requested method not allowed by materialization policy")

    if request["requested_ttl_s"] > secret_obj["materialization_policy"]["max_ttl_s"]:
        deny.append("requested TTL exceeds policy maximum")

    allowed_consumers = set(secret_obj["materialization_policy"].get("allowed_consumers", []))
    if allowed_consumers and request["consumer"]["kind"] not in allowed_consumers:
        deny.append("consumer kind not allowed by materialization policy")

    if not request["consumer"]["host_attestation"]["verified"]:
        deny.append("host attestation failed")

    active = None
    requested_version_id = request.get("version_selector", {}).get("version_id")
    requested_epoch_min = request.get("version_selector", {}).get("epoch_min")
    for v in secret_obj["versions"]:
        if v["state"] != "active":
            continue
        if requested_version_id and v["version_id"] != requested_version_id:
            continue
        if requested_epoch_min and v["epoch"] < requested_epoch_min:
            continue
        active = v
        break

    if active is None:
        deny.append("no matching active version found")

    if request["requested_method"] == "env-var":
        deny.append("env-var method disabled by reference profile")

    if deny:
        grant = {
            "schema_version": "secret-0001-0.1",
            "grant_id": f"grant-deny-{request['request_id']}",
            "decision": "deny",
            "bridge_trace": request["bridge_trace"],
            "bridge_witness_jti": request["bridge_witness_jti"],
            "secret_id": request["secret_id"],
            "version_id": requested_version_id or "none",
            "secret_epoch": requested_epoch_min or 0,
            "bridge_epoch": bridge_epoch,
            "method": request["requested_method"],
            "handle": {"kind": "opaque-handle", "ref": "deny"},
            "consumer": {"kind": request["consumer"]["kind"], "id": request["consumer"]["id"]},
            "issued_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "expires_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "exportable": False,
            "destroy_on_consumer_exit": True,
            "deny_reasons": deny,
            "constraints": {
                "one_time": True,
                "refresh_prohibited": True,
                "model_reentry_prohibited": True,
                "log_export_prohibited": True
            }
        }
        validate_schema("mat_grant", grant)
        return grant

    grant = {
        "schema_version": "secret-0001-0.1",
        "grant_id": f"grant-{request['request_id']}",
        "decision": "allow",
        "bridge_trace": request["bridge_trace"],
        "bridge_witness_jti": request["bridge_witness_jti"],
        "secret_id": request["secret_id"],
        "version_id": active["version_id"],
        "secret_epoch": active["epoch"],
        "bridge_epoch": bridge_epoch,
        "method": request["requested_method"],
        "handle": {"kind": "opaque-handle", "ref": f"handle://{request['secret_id']}/{active['version_id']}/{request['request_id']}"},
        "consumer": {"kind": request["consumer"]["kind"], "id": request["consumer"]["id"]},
        "issued_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "expires_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "exportable": False,
        "destroy_on_consumer_exit": secret_obj["materialization_policy"].get("destroy_on_consumer_exit", True),
        "constraints": {
            "one_time": True,
            "refresh_prohibited": True,
            "model_reentry_prohibited": True,
            "log_export_prohibited": True
        }
    }
    validate_schema("mat_grant", grant)
    return grant


def main(argv: List[str]) -> int:
    if len(argv) < 3:
        print(
            "usage:\n"
            "  reference_validator.py validate-secret <secret-object.json>\n"
            "  reference_validator.py authorize <secret-object.json> <materialization-request.json>\n",
            file=sys.stderr,
        )
        return 2

    cmd = argv[1]
    if cmd == "validate-secret":
        obj = load_json(Path(argv[2]))
        errors = validate_secret_object(obj)
        if errors:
            print(json.dumps({"ok": False, "errors": errors}, indent=2))
            return 1
        print(json.dumps({"ok": True}, indent=2))
        return 0

    if cmd == "authorize":
        if len(argv) < 4:
            print("authorize requires <secret-object.json> <materialization-request.json>", file=sys.stderr)
            return 2
        obj = load_json(Path(argv[2]))
        req = load_json(Path(argv[3]))
        errors = validate_secret_object(obj)
        if errors:
            print(json.dumps({"ok": False, "errors": errors}, indent=2))
            return 1
        decision = authorize_materialization(obj, req)
        print(json.dumps(decision, indent=2))
        return 0

    print(f"unknown command: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
