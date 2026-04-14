#!/usr/bin/env python3
"""
Reference planner for SECRET-0002.
This is a contract/invariant harness, not a production backend.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {
    "backend": ROOT / "schemas" / "backend-profile.schema.json",
    "materializer": ROOT / "schemas" / "materializer-profile.schema.json",
    "binding": ROOT / "schemas" / "backend-binding.schema.json",
    "request": ROOT / "schemas" / "materialization-plan-request.schema.json",
    "session": ROOT / "schemas" / "materialization-session.schema.json",
}


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def load_schema(name: str) -> Dict[str, Any]:
    return load_json(SCHEMAS[name])


def validate_schema(name: str, payload: Dict[str, Any]) -> None:
    jsonschema.validate(payload, load_schema(name))


USAGE = (
    "usage:\n"
    "  reference_planner.py validate <backend.json> <materializer.json> <binding.json>\n"
    "  reference_planner.py plan <backend.json> <materializer.json> <binding.json> <request.json>\n"
)


def _forbidden_plaintext_paths(value: Any, path: str = "$") -> List[str]:
    bad: List[str] = []
    if isinstance(value, dict):
        for k, v in value.items():
            kl = k.lower()
            if kl in {"plaintext", "secret_value", "private_key", "password_value", "token_value"}:
                bad.append(f"{path}.{k}")
            bad.extend(_forbidden_plaintext_paths(v, f"{path}.{k}"))
    elif isinstance(value, list):
        for i, item in enumerate(value):
            bad.extend(_forbidden_plaintext_paths(item, f"{path}[{i}]"))
    return bad


def validate_profiles(backend: Dict[str, Any], materializer: Dict[str, Any], binding: Dict[str, Any]) -> List[str]:
    validate_schema("backend", backend)
    validate_schema("materializer", materializer)
    validate_schema("binding", binding)

    errors: List[str] = []
    for name, obj in [("backend", backend), ("materializer", materializer), ("binding", binding)]:
        bad = _forbidden_plaintext_paths(obj)
        if bad:
            errors.append(f"{name} contains forbidden plaintext-like fields: {', '.join(bad)}")

    if binding["backend_profile_id"] != backend["profile_id"]:
        errors.append("binding.backend_profile_id does not match backend profile_id")
    if binding["materializer_profile_id"] != materializer["profile_id"]:
        errors.append("binding.materializer_profile_id does not match materializer profile_id")
    if binding["secret_class"] not in backend["allowed_secret_classes"]:
        errors.append("binding secret_class not allowed by backend profile")
    if binding["secret_class"] not in materializer["allowed_secret_classes"]:
        errors.append("binding secret_class not allowed by materializer profile")

    if "max_ttl_s_override" in binding and binding["max_ttl_s_override"] > materializer["max_ttl_s"]:
        errors.append("binding max_ttl_s_override exceeds materializer max_ttl_s")

    if backend["backend_type"] == "hsm-rooted":
        if backend["protection"]["export_policy"] not in {"non-exportable", "wrapped-only"}:
            errors.append("hsm-rooted backend requires non-exportable or wrapped-only export policy")
        if backend["protection"]["root_key_online"]:
            errors.append("hsm-rooted backend requires root_key_online=false")
        if binding["secret_class"] not in {"signing-key", "wrapping-key", "certificate-keypair", "asymmetric-private-key", "recovery-share"}:
            errors.append("hsm-rooted profile should only bind to high-assurance key classes in this reference profile")

    if backend["backend_type"] == "os-keychain-bootstrap":
        if not backend.get("constraints", {}).get("bootstrap_only", False):
            errors.append("os-keychain-bootstrap must declare bootstrap_only=true")
        if binding["secret_class"] not in {"bootstrap-secret", "api-token", "oauth-client-secret", "password"}:
            errors.append("os-keychain-bootstrap profile only supports local/bootstrap or user-side classes in this reference profile")

    if materializer["materializer_type"] == "systemd-credential":
        if materializer["platform"] != "linux-systemd":
            errors.append("systemd-credential requires platform=linux-systemd")
        if materializer["handle_kind"] != "credential-file":
            errors.append("systemd-credential requires handle_kind=credential-file")
        if binding["handle_binding"]["consumer_kind"] != "systemd-unit":
            errors.append("systemd-credential bindings should target consumer_kind=systemd-unit")

    if materializer["materializer_type"] in {"unix-socket-proxy", "agent-proxy"} and materializer["plaintext_surface"] != "remote-handle-only":
        errors.append("proxy materializers require plaintext_surface=remote-handle-only")

    if materializer["materializer_type"] == "os-keychain-ref":
        if materializer["platform"] != "macos":
            errors.append("os-keychain-ref requires platform=macos")
        if materializer["handle_kind"] != "keychain-ref":
            errors.append("os-keychain-ref requires handle_kind=keychain-ref")

    if not binding["direct_model_access_prohibited"]:
        errors.append("direct_model_access_prohibited must be true")

    if binding["non_exportable"] and materializer["plaintext_surface"] in {"tmpfs-bounded", "credential-dir-bounded"} and backend["backend_type"] in {"hsm-rooted", "external-reference"}:
        errors.append("non-exportable proxy/rooted backends must not widen to file/path plaintext surfaces")

    if materializer["env_var_allowed"]:
        errors.append("env_var_allowed must be false in the reference profile")

    if not materializer["model_reentry_prohibited"]:
        errors.append("model_reentry_prohibited must be true")

    if not materializer["log_redaction_required"]:
        errors.append("log_redaction_required must be true")

    return errors


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def _steps_for(backend_type: str, materializer_type: str) -> List[str]:
    common = ["resolve-binding", "verify-profiles", "verify-attestation"]
    if backend_type == "vault-dynamic":
        common.append("issue-dynamic-lease")
    elif backend_type == "kms-envelope":
        common.append("decrypt-ciphertext-reference")
    elif backend_type == "hsm-rooted":
        common.append("authorize-hsm-operation")
    elif backend_type == "os-keychain-bootstrap":
        common.append("lookup-keychain-reference")
    else:
        common.append("lookup-external-reference")

    if materializer_type == "systemd-credential":
        common.extend(["write-credential-directory", "chmod-consumer-only"])
    elif materializer_type == "memfd-pass":
        common.extend(["create-memfd", "pass-fd-to-consumer"])
    elif materializer_type == "unix-socket-proxy":
        common.extend(["open-unix-socket-proxy", "bind-socket-to-consumer"])
    elif materializer_type == "tmpfs-file":
        common.extend(["write-tmpfs-path", "chmod-consumer-only"])
    elif materializer_type == "cloud-kms-decrypt":
        common.extend(["bind-kms-operation-reference"])
    elif materializer_type == "os-keychain-ref":
        common.extend(["return-keychain-reference"])
    elif materializer_type == "agent-proxy":
        common.extend(["open-local-broker-session", "bind-opaque-handle"])
    common.append("emit-audit")
    return common


def _handle_for(materializer: Dict[str, Any], request: Dict[str, Any], binding: Dict[str, Any]) -> Dict[str, str]:
    mt = materializer["materializer_type"]
    secret = request["secret"]["secret_id"]
    rid = request["request_id"]
    cid = request["consumer"]["id"]
    if mt == "systemd-credential":
        return {"kind": "credential-file", "ref": f"/run/credentials/{cid}/{secret}/{rid}"}
    if mt == "memfd-pass":
        return {"kind": "fd-name", "ref": f"memfd:{secret}:{rid}"}
    if mt == "unix-socket-proxy":
        return {"kind": "socket-ref", "ref": f"unix:///run/bridge/{secret}/{rid}.sock"}
    if mt == "tmpfs-file":
        return {"kind": "credential-file", "ref": f"/run/secret-tmpfs/{secret}/{rid}"}
    if mt == "cloud-kms-decrypt":
        return {"kind": "kms-op-ref", "ref": f"kmsop://{binding['backend_profile_id']}/{secret}/{rid}"}
    if mt == "os-keychain-ref":
        return {"kind": "keychain-ref", "ref": f"keychain://{secret}/{rid}"}
    return {"kind": "opaque-handle", "ref": f"handle://bridge/{secret}/{rid}"}


def _backend_operation_for(backend: Dict[str, Any], binding: Dict[str, Any], request: Dict[str, Any]) -> Dict[str, str]:
    bt = backend["backend_type"]
    secret = request["secret"]["secret_id"]
    rid = request["request_id"]
    if bt == "vault-dynamic":
        return {"kind": "issue-dynamic", "ref": f"lease://{secret}/{rid}"}
    if bt == "kms-envelope":
        return {"kind": "decrypt-reference", "ref": f"cipherref://{secret}/{rid}"}
    if bt == "hsm-rooted":
        return {"kind": "sign-proxy" if binding["secret_class"] == "signing-key" else "unwrap", "ref": f"hsmop://{secret}/{rid}"}
    if bt == "os-keychain-bootstrap":
        return {"kind": "lookup-reference", "ref": f"keychain://{secret}/{rid}"}
    return {"kind": "lookup-reference", "ref": f"ref://{secret}/{rid}"}


def plan_session(backend: Dict[str, Any], materializer: Dict[str, Any], binding: Dict[str, Any], request: Dict[str, Any]) -> Dict[str, Any]:
    validate_schema("request", request)
    errors = validate_profiles(backend, materializer, binding)

    deny: List[str] = list(errors)
    bridge = request["bridge"]
    resource_binding = request["resource_binding"]
    secret = request["secret"]
    authority_bounds = request["authority_bounds"]

    if bridge["decision_effect"] != "accept":
        if bridge["decision_effect"] == "burn":
            deny.extend([f"bridge burn: {reason}" for reason in bridge["burn_reasons"]])
            if not bridge["burn_reasons"]:
                deny.append("bridge decision burn denies new materialization sessions")
        elif bridge["decision_effect"] == "deny":
            deny.extend([f"bridge deny: {reason}" for reason in bridge["deny_reasons"]])
            if not bridge["deny_reasons"]:
                deny.append("bridge decision deny forbids materialization")

    if request["mode"] == "burn":
        deny.append("bridge mode burn denies new materialization sessions")

    if resource_binding["binding_id"] != binding["binding_id"]:
        deny.append("request binding_id does not match selected binding")
    if resource_binding["secret_id"] != binding["secret_id"]:
        deny.append("resource binding secret_id does not match selected binding")
    if resource_binding["backend_profile_id"] != backend["profile_id"]:
        deny.append("request backend_profile_id does not match selected backend profile")
    if resource_binding["materializer_profile_id"] != materializer["profile_id"]:
        deny.append("request materializer_profile_id does not match selected materializer profile")

    if secret["secret_id"] != binding["secret_id"]:
        deny.append("request secret_id does not match binding secret_id")
    if secret["secret_class"] != binding["secret_class"]:
        deny.append("request secret_class does not match binding secret_class")
    if request["requested_method"] != materializer["materializer_type"]:
        deny.append("requested_method does not match selected materializer profile")
    if request["consumer"]["kind"] != binding["handle_binding"]["consumer_kind"]:
        deny.append("consumer kind not permitted by binding")
    if request["mode"] not in binding["allowed_modes"]:
        deny.append("request mode not permitted by binding")
    ttl_limit = materializer["max_ttl_s"]
    if "max_ttl_s_override" in binding:
        ttl_limit = min(ttl_limit, binding["max_ttl_s_override"])
    ttl_limit = min(ttl_limit, authority_bounds["effective_ttl_s"])
    if request["requested_ttl_s"] > ttl_limit:
        deny.append("requested_ttl_s exceeds effective TTL limit")
    if authority_bounds["max_secret_materializations"] < 1:
        deny.append("bridge authority budget forbids secret materialization")
    if authority_bounds["non_exportable"] and not binding["non_exportable"]:
        deny.append("binding widens a bridge non-exportable authority bound")

    need_host_attest = backend["trust_boundary"]["attestation_required"] or binding.get("policy_overrides", {}).get("require_host_attestation", False)
    if need_host_attest and not request["consumer"]["host_attestation"]["verified"]:
        deny.append("host attestation failed")

    need_proc_attest = binding.get("policy_overrides", {}).get("require_process_attestation", False)
    if need_proc_attest and not request["consumer"].get("process_attestation", {}).get("verified", False):
        deny.append("process attestation failed")

    if binding["non_exportable"] and materializer["plaintext_surface"] in {"tmpfs-bounded", "credential-dir-bounded"} and backend["backend_type"] in {"hsm-rooted", "external-reference"}:
        deny.append("non-exportable rooted/reference secret cannot widen to file/path surface")

    issued_at = _now()
    expires_at = issued_at if deny else issued_at + timedelta(seconds=request["requested_ttl_s"])
    session = {
        "schema_version": "secret-0002-0.1",
        "session_id": f"session.{request['request_id']}",
        "decision": "deny" if deny else "allow",
        "session_state": "denied" if deny else "issued",
        "bridge_trace": bridge["trace"],
        "bridge_decision_effect": bridge["decision_effect"],
        "request_id": request["request_id"],
        "binding_id": binding["binding_id"],
        "secret_id": secret["secret_id"],
        "secret_class": secret["secret_class"],
        "backend_profile_id": backend["profile_id"],
        "materializer_profile_id": materializer["profile_id"],
        "consumer": {"kind": request["consumer"]["kind"], "id": request["consumer"]["id"]},
        "mode": request["mode"],
        "session_epoch": request["bridge_epoch"],
        "secret_epoch": secret.get("secret_epoch_min", 0),
        "issued_at": _iso(issued_at),
        "expires_at": _iso(expires_at),
        "backend_operation": {"kind": "none", "ref": "deny"} if deny else _backend_operation_for(backend, binding, request),
        "handle": {"kind": "deny", "ref": "deny"} if deny else _handle_for(materializer, request, binding),
        "steps": ["deny"] if deny else _steps_for(backend["backend_type"], materializer["materializer_type"]),
        "revalidation_triggers": [k for k, v in {
            "bridge-burn": materializer["revalidation"]["on_bridge_burn"],
            "secret-epoch-change": materializer["revalidation"]["on_secret_epoch_change"],
            "attestation-loss": materializer["revalidation"]["on_attestation_loss"],
            "consumer-exit": materializer["revalidation"]["on_consumer_exit"],
        }.items() if v],
        "constraints": {
            "non_exportable": authority_bounds["non_exportable"],
            "model_reentry_prohibited": materializer["model_reentry_prohibited"],
            "log_redaction_required": materializer["log_redaction_required"],
            "destroy_on_exit": materializer["teardown"]["destroy_on_exit"],
        },
        "teardown_actions": [] if deny else [a for a, enabled in {
            "destroy-on-exit": materializer["teardown"]["destroy_on_exit"],
            "zeroize-local-plaintext": materializer["teardown"]["zeroize_local_plaintext"],
            "revoke-on-burn": materializer["teardown"]["revoke_on_burn"],
            "unlink-files-on-exit": materializer["teardown"].get("unlink_files_on_exit", False),
        }.items() if enabled],
    }
    if deny:
        session["deny_reasons"] = deny

    validate_schema("session", session)
    return session


def main(argv: List[str]) -> int:
    if len(argv) < 2 or argv[1] in {"help", "-h", "--help"}:
        print(USAGE, file=sys.stderr)
        return 0

    if len(argv) < 5:
        print(USAGE, file=sys.stderr)
        return 2

    cmd = argv[1]
    backend = load_json(Path(argv[2]))
    materializer = load_json(Path(argv[3]))
    binding = load_json(Path(argv[4]))

    if cmd == "validate":
        errs = validate_profiles(backend, materializer, binding)
        if errs:
            print(json.dumps({"ok": False, "errors": errs}, indent=2))
            return 1
        print(json.dumps({"ok": True}, indent=2))
        return 0

    if cmd == "plan":
        if len(argv) < 6:
            print("plan requires <backend.json> <materializer.json> <binding.json> <request.json>", file=sys.stderr)
            return 2
        request = load_json(Path(argv[5]))
        errs = validate_profiles(backend, materializer, binding)
        if errs:
            print(json.dumps({"ok": False, "errors": errs}, indent=2))
            return 1
        session = plan_session(backend, materializer, binding, request)
        print(json.dumps(session, indent=2))
        return 0

    print(f"unknown command: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
