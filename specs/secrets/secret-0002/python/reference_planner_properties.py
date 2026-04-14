#!/usr/bin/env python3
"""
Property checks for SECRET-0002 reference_planner.
This is the semantic harness for planner invariants, not a production runtime.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from pathlib import Path
import unittest

from hypothesis import given, settings, strategies as st

from reference_planner import load_json, plan_session


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def load_example(name: str):
    return load_json(EXAMPLES / name)


def normalize_backend_example_for_planner(example: dict) -> dict:
    normalized = deepcopy(example)
    capabilities = normalized.get("capabilities")
    if isinstance(capabilities, dict):
        # Current example profiles still use a boolean capability map while the
        # planner schema expects an explicit capability list. Normalize the
        # example seed here so this harness stays focused on planner laws.
        if normalized["backend_type"] == "vault-dynamic":
            normalized["capabilities"] = ["issue-dynamic", "lookup-reference", "revoke-lease"]
        elif normalized["backend_type"] == "hsm-rooted":
            normalized["capabilities"] = ["sign", "lookup-reference", "disable-key"]
        else:
            normalized["capabilities"] = ["lookup-reference"]
    audit = normalized.get("audit")
    if isinstance(audit, dict) and "emit_required" in audit:
        # Current example profiles still carry the older audit shape here.
        normalized["audit"] = {
            "backend_events_required": bool(audit.get("emit_required", True)),
            "authoritative_time_required": True,
        }
    return normalized


def analytics_seed():
    return (
        normalize_backend_example_for_planner(load_example("example.backend-profile.vault-dynamic.json")),
        deepcopy(load_example("example.materializer-profile.systemd-credential.json")),
        deepcopy(load_example("example.backend-binding.analytics-db.json")),
        deepcopy(load_example("example.plan-request.analytics-db.json")),
    )


def signing_seed():
    return (
        normalize_backend_example_for_planner(load_example("example.backend-profile.hsm-rooted-signing.json")),
        deepcopy(load_example("example.materializer-profile.unix-socket-proxy.json")),
        deepcopy(load_example("example.backend-binding.signing-key.json")),
        deepcopy(load_example("example.plan-request.signing-key.json")),
    )


def seed_case(name: str):
    if name == "analytics":
        return analytics_seed()
    if name == "signing":
        return signing_seed()
    raise ValueError(f"unknown seed: {name}")


def parse_z(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def issued_ttl_seconds(session: dict) -> int:
    return int((parse_z(session["expires_at"]) - parse_z(session["issued_at"])).total_seconds())


class ReferencePlannerPropertyTests(unittest.TestCase):
    @settings(deadline=None, max_examples=16)
    @given(
        seed=st.sampled_from(["analytics", "signing"]),
        effect=st.sampled_from(["deny", "burn"]),
    )
    def test_non_accept_decisions_deny_usable_sessions(self, seed: str, effect: str) -> None:
        backend, materializer, binding, request = seed_case(seed)
        request["bridge"]["decision_effect"] = effect
        request["bridge"]["deny_reasons"] = []
        request["bridge"]["burn_reasons"] = []
        if effect == "deny":
            request["bridge"]["deny_reasons"] = ["POLICY_DENIED"]
        else:
            request["bridge"]["burn_reasons"] = ["AUDIT_TAMPER_DETECTED"]

        session = plan_session(backend, materializer, binding, request)

        self.assertEqual(session["decision"], "deny")
        self.assertEqual(session["session_state"], "denied")
        self.assertEqual(session["handle"]["kind"], "deny")
        self.assertEqual(session["backend_operation"]["kind"], "none")
        if effect == "deny":
            self.assertIn("bridge deny: POLICY_DENIED", session["deny_reasons"])
        else:
            self.assertIn("bridge burn: AUDIT_TAMPER_DETECTED", session["deny_reasons"])

    @settings(deadline=None, max_examples=16)
    @given(seed=st.sampled_from(["analytics", "signing"]))
    def test_burn_mode_denies_new_sessions(self, seed: str) -> None:
        backend, materializer, binding, request = seed_case(seed)
        request["mode"] = "burn"
        request["bridge"]["decision_effect"] = "accept"
        request["bridge"]["deny_reasons"] = []
        request["bridge"]["burn_reasons"] = []

        session = plan_session(backend, materializer, binding, request)

        self.assertEqual(session["decision"], "deny")
        self.assertIn("bridge mode burn denies new materialization sessions", session["deny_reasons"])
        self.assertEqual(session["handle"]["kind"], "deny")

    @settings(deadline=None, max_examples=48)
    @given(
        seed=st.sampled_from(["analytics", "signing"]),
        requested_ttl_s=st.integers(min_value=1, max_value=1800),
        authority_ttl_s=st.integers(min_value=1, max_value=1800),
    )
    def test_issued_ttl_never_exceeds_effective_bound(
        self,
        seed: str,
        requested_ttl_s: int,
        authority_ttl_s: int,
    ) -> None:
        backend, materializer, binding, request = seed_case(seed)
        request["bridge"]["decision_effect"] = "accept"
        request["bridge"]["deny_reasons"] = []
        request["bridge"]["burn_reasons"] = []
        request["requested_ttl_s"] = requested_ttl_s
        request["authority_bounds"]["effective_ttl_s"] = authority_ttl_s

        ttl_limit = min(materializer["max_ttl_s"], authority_ttl_s)
        if "max_ttl_s_override" in binding:
            ttl_limit = min(ttl_limit, binding["max_ttl_s_override"])

        session = plan_session(backend, materializer, binding, request)

        if requested_ttl_s <= ttl_limit:
            self.assertEqual(session["decision"], "allow")
            self.assertEqual(issued_ttl_seconds(session), requested_ttl_s)
            self.assertLessEqual(issued_ttl_seconds(session), ttl_limit)
        else:
            self.assertEqual(session["decision"], "deny")
            self.assertIn("requested_ttl_s exceeds effective TTL limit", session["deny_reasons"])

    @settings(deadline=None, max_examples=8)
    @given(plaintext_surface=st.sampled_from(["tmpfs-bounded", "credential-dir-bounded"]))
    def test_non_exportable_authority_never_widens_to_forbidden_plaintext_surface(
        self,
        plaintext_surface: str,
    ) -> None:
        backend, materializer, binding, request = signing_seed()
        request["authority_bounds"]["non_exportable"] = True
        materializer["plaintext_surface"] = plaintext_surface

        session = plan_session(backend, materializer, binding, request)

        self.assertEqual(session["decision"], "deny")
        self.assertIn(
            "non-exportable rooted/reference secret cannot widen to file/path surface",
            session["deny_reasons"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
