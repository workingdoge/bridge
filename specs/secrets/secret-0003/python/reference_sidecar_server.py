#!/usr/bin/env python3
"""
Reference sidecar server for SECRET-0003.

This is a repo-owned runtime harness over the existing reference decision logic.
It is a bounded HTTP sidecar, not a production deployment surface.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
from typing import Any, Dict
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reference_sidecar import (
    build_audit_envelope,
    load_json,
    load_schema,
    make_decision,
    parse_ts,
    utc_now,
    validate,
)


def iso_now() -> str:
    return utc_now().isoformat().replace("+00:00", "Z")


class SidecarState:
    def __init__(
        self,
        *,
        catalog: Dict[str, Any],
        deployment: Dict[str, Any],
        attestation: Dict[str, Any],
        revocation: Dict[str, Any],
        mode: Dict[str, Any],
        schema_dir: Path,
        audit_log: Path | None,
        stream_id: str,
        now_override: str | None,
    ) -> None:
        self.catalog = catalog
        self.deployment = deployment
        self.attestation = attestation
        self.revocation = revocation
        self.mode = mode
        self.audit_log = audit_log
        self.stream_id = stream_id
        self.now_override = parse_ts(now_override) if now_override else None
        self.schemas = {
            "provider-request": load_schema(schema_dir, "provider-request.schema.json"),
            "provider-decision": load_schema(schema_dir, "provider-decision.schema.json"),
            "attestation-result": load_schema(schema_dir, "attestation-result.schema.json"),
            "audit-envelope": load_schema(schema_dir, "audit-envelope.schema.json"),
            "audit-checkpoint": load_schema(schema_dir, "audit-checkpoint.schema.json"),
        }

    def _read_audit_events(self) -> list[Dict[str, Any]]:
        if self.audit_log is None or not self.audit_log.exists():
            return []
        events: list[Dict[str, Any]] = []
        for line in self.audit_log.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            events.append(json.loads(line))
        return events

    def now(self):
        return self.now_override or utc_now()

    def append_audit(self, audit: Dict[str, Any]) -> None:
        validate(audit, self.schemas["audit-envelope"])
        if self.audit_log is None:
            return
        self.audit_log.parent.mkdir(parents=True, exist_ok=True)
        with self.audit_log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(audit, sort_keys=True) + "\n")

    def next_audit_position(self) -> tuple[int, str]:
        events = self._read_audit_events()
        if not events:
            return (
                1,
                "sha256:0000000000000000000000000000000000000000000000000000000000000000",
            )
        last = events[-1]
        return int(last["sequence"]) + 1, str(last["event_hash"])

    def checkpoint(self) -> Dict[str, Any]:
        events = self._read_audit_events()
        if events:
            last = events[-1]
            checkpoint = {
                "version": "0.1",
                "stream_id": self.stream_id,
                "last_sequence": int(last["sequence"]),
                "last_event_hash": last["event_hash"],
                "checkpointed_at": self.now().isoformat().replace("+00:00", "Z"),
                "sink_id": self.deployment["providers"]["audit_sink"],
            }
        else:
            checkpoint = {
                "version": "0.1",
                "stream_id": self.stream_id,
                "last_sequence": 0,
                "last_event_hash": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
                "checkpointed_at": self.now().isoformat().replace("+00:00", "Z"),
                "sink_id": self.deployment["providers"]["audit_sink"],
            }
        validate(checkpoint, self.schemas["audit-checkpoint"])
        return checkpoint

    def attestation_for_subject(self, subject_id: str) -> Dict[str, Any]:
        if subject_id == self.attestation["subject_id"]:
            result = deepcopy(self.attestation)
        else:
            result = deepcopy(self.attestation)
            result["attestation_id"] = f'{result["attestation_id"]}-subject-mismatch'
            result["subject_id"] = subject_id
            result["status"] = "failed"
            result["posture_digest"] = "sha256:subject-mismatch"
            claims = dict(result.get("claims", {}))
            claims["subject_mismatch"] = True
            result["claims"] = claims
        validate(result, self.schemas["attestation-result"])
        return result


class SidecarHandler(BaseHTTPRequestHandler):
    server: "SidecarServer"

    def log_message(self, format: str, *args: Any) -> None:  # pragma: no cover
        return

    @property
    def state(self) -> SidecarState:
        return self.server.state

    def _send_json(self, status: HTTPStatus, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8") + b"\n"
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_empty(self, status: HTTPStatus) -> None:
        self.send_response(status)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _read_json_body(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        data = self.rfile.read(length)
        return json.loads(data or b"{}")

    def do_GET(self) -> None:
        if self.path == "/v1/providers/catalog":
            self._send_json(HTTPStatus.OK, self.state.catalog)
            return

        if self.path.startswith("/v1/deployments/"):
            deployment_id = unquote(self.path.rsplit("/", 1)[-1])
            if deployment_id != self.state.deployment["deployment_profile_id"]:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "deployment profile not found"})
                return
            self._send_json(HTTPStatus.OK, self.state.deployment)
            return

        if self.path == "/v1/providers/time/now":
            self._send_json(
                HTTPStatus.OK,
                {
                    "now": self.state.now().isoformat().replace("+00:00", "Z"),
                    "source_id": self.state.deployment["providers"]["time_authority"],
                },
            )
            return

        if self.path == "/v1/providers/mode/current":
            self._send_json(HTTPStatus.OK, self.state.mode)
            return

        if self.path == "/v1/providers/revocation/snapshot":
            self._send_json(HTTPStatus.OK, self.state.revocation)
            return

        if self.path == "/v1/providers/audit/checkpoint":
            self._send_json(HTTPStatus.OK, self.state.checkpoint())
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})

    def do_POST(self) -> None:
        if self.path == "/v1/providers/attestation/verify":
            body = self._read_json_body()
            subject_id = body.get("subject_id")
            if not isinstance(subject_id, str) or not subject_id:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "subject_id is required"})
                return
            self._send_json(HTTPStatus.OK, self.state.attestation_for_subject(subject_id))
            return

        if self.path == "/v1/authorize/providers":
            request = self._read_json_body()
            validate(request, self.state.schemas["provider-request"])
            decision = make_decision(
                self.state.catalog,
                self.state.deployment,
                request,
                self.state.attestation_for_subject(request["subject_id"]),
                self.state.revocation,
                self.state.mode,
                now=self.state.now(),
            )
            validate(decision, self.state.schemas["provider-decision"])
            sequence, prev_hash = self.state.next_audit_position()
            audit = build_audit_envelope(
                decision=decision,
                source_id=self.state.deployment["providers"]["audit_sink"],
                stream_id=self.state.stream_id,
                sequence=sequence,
                prev_event_hash=prev_hash,
                now=self.state.now(),
            )
            self.state.append_audit(audit)
            status = HTTPStatus.CONFLICT if decision["status"] == "burn" else HTTPStatus.OK
            self._send_json(status, decision)
            return

        if self.path == "/v1/providers/audit/emit":
            audit = self._read_json_body()
            self.state.append_audit(audit)
            self._send_empty(HTTPStatus.ACCEPTED)
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})


class SidecarServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], state: SidecarState) -> None:
        super().__init__(server_address, SidecarHandler)
        self.state = state


def parse_listen(value: str) -> tuple[str, int]:
    host, sep, port = value.rpartition(":")
    if not sep or not host:
        raise argparse.ArgumentTypeError("listen must be in HOST:PORT format")
    try:
        port_value = int(port)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("listen port must be an integer") from exc
    return host, port_value


def main() -> None:
    parser = argparse.ArgumentParser(prog="bridge-sidecar")
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--deployment", required=True, type=Path)
    parser.add_argument("--attestation", required=True, type=Path)
    parser.add_argument("--revocation", required=True, type=Path)
    parser.add_argument("--mode", required=True, type=Path)
    parser.add_argument("--schema-dir", type=Path, default=Path(__file__).resolve().parent.parent / "schemas")
    parser.add_argument("--listen", type=parse_listen, default=("127.0.0.1", 8181))
    parser.add_argument("--audit-log", type=Path)
    parser.add_argument("--stream-id", default="audit-stream-main")
    parser.add_argument("--now", help="Override current time as RFC3339/ISO-8601 UTC timestamp")
    args = parser.parse_args()

    catalog = load_json(args.catalog)
    deployment = load_json(args.deployment)
    attestation = load_json(args.attestation)
    revocation = load_json(args.revocation)
    mode = load_json(args.mode)

    validate(catalog, load_schema(args.schema_dir, "provider-catalog.schema.json"))
    validate(deployment, load_schema(args.schema_dir, "deployment-profile.schema.json"))
    validate(attestation, load_schema(args.schema_dir, "attestation-result.schema.json"))
    validate(revocation, load_schema(args.schema_dir, "revocation-snapshot.schema.json"))
    validate(mode, load_schema(args.schema_dir, "mode-state.schema.json"))

    state = SidecarState(
        catalog=catalog,
        deployment=deployment,
        attestation=attestation,
        revocation=revocation,
        mode=mode,
        schema_dir=args.schema_dir,
        audit_log=args.audit_log,
        stream_id=args.stream_id,
        now_override=args.now,
    )
    server = SidecarServer(args.listen, state)
    host, port = args.listen
    print(f"bridge-sidecar listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:  # pragma: no cover
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
