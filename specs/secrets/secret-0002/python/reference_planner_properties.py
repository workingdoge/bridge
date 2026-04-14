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

def analytics_seed():
    return (
        deepcopy(load_example("example.backend-profile.vault-dynamic.json")),
        deepcopy(load_example("example.materializer-profile.systemd-credential.json")),
        deepcopy(load_example("example.backend-binding.analytics-db.json")),
        deepcopy(load_example("example.plan-request.analytics-db.json")),
    )


def signing_seed():
    return (
        deepcopy(load_example("example.backend-profile.hsm-rooted-signing.json")),
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
    @given(seed=st.sampled_from(["analytics", "signing"]))
    def test_host_attestation_failure_denies_session(self, seed: str) -> None:
        backend, materializer, binding, request = seed_case(seed)
        request["consumer"]["host_attestation"]["verified"] = False

        session = plan_session(backend, materializer, binding, request)

        self.assertEqual(session["decision"], "deny")
        self.assertEqual(session["session_state"], "denied")
        self.assertIn("host attestation failed", session["deny_reasons"])
        self.assertEqual(session["handle"]["kind"], "deny")

    @settings(deadline=None, max_examples=8)
    def test_process_attestation_failure_denies_session(self) -> None:
        backend, materializer, binding, request = signing_seed()
        request["consumer"]["process_attestation"]["verified"] = False

        session = plan_session(backend, materializer, binding, request)

        self.assertEqual(session["decision"], "deny")
        self.assertEqual(session["session_state"], "denied")
        self.assertIn("process attestation failed", session["deny_reasons"])
        self.assertEqual(session["handle"]["kind"], "deny")

    @settings(deadline=None, max_examples=32)
    @given(
        seed=st.sampled_from(["analytics", "signing"]),
        mismatch=st.sampled_from(
            [
                "resource_binding.binding_id",
                "resource_binding.secret_id",
                "resource_binding.backend_profile_id",
                "resource_binding.materializer_profile_id",
                "secret.secret_id",
                "secret.secret_class",
                "requested_method",
            ]
        ),
    )
    def test_request_binding_mismatch_denies_session(self, seed: str, mismatch: str) -> None:
        backend, materializer, binding, request = seed_case(seed)

        if mismatch == "resource_binding.binding_id":
            request["resource_binding"]["binding_id"] = "binding.unexpected"
            expected_reason = "request binding_id does not match selected binding"
        elif mismatch == "resource_binding.secret_id":
            request["resource_binding"]["secret_id"] = "secret.unexpected"
            expected_reason = "resource binding secret_id does not match selected binding"
        elif mismatch == "resource_binding.backend_profile_id":
            request["resource_binding"]["backend_profile_id"] = "backend.unexpected"
            expected_reason = "request backend_profile_id does not match selected backend profile"
        elif mismatch == "resource_binding.materializer_profile_id":
            request["resource_binding"]["materializer_profile_id"] = "materializer.unexpected"
            expected_reason = "request materializer_profile_id does not match selected materializer profile"
        elif mismatch == "secret.secret_id":
            request["secret"]["secret_id"] = "secret.unexpected"
            expected_reason = "request secret_id does not match binding secret_id"
        elif mismatch == "secret.secret_class":
            request["secret"]["secret_class"] = "password"
            expected_reason = "request secret_class does not match binding secret_class"
        else:
            request["requested_method"] = "agent-proxy"
            expected_reason = "requested_method does not match selected materializer profile"

        session = plan_session(backend, materializer, binding, request)

        self.assertEqual(session["decision"], "deny")
        self.assertEqual(session["session_state"], "denied")
        self.assertIn(expected_reason, session["deny_reasons"])
        self.assertEqual(session["handle"]["kind"], "deny")

    @settings(deadline=None, max_examples=16)
    @given(seed=st.sampled_from(["analytics", "signing"]))
    def test_zero_materialization_budget_denies_session(self, seed: str) -> None:
        backend, materializer, binding, request = seed_case(seed)
        request["authority_bounds"]["max_secret_materializations"] = 0

        session = plan_session(backend, materializer, binding, request)

        self.assertEqual(session["decision"], "deny")
        self.assertEqual(session["session_state"], "denied")
        self.assertIn("bridge authority budget forbids secret materialization", session["deny_reasons"])
        self.assertEqual(session["handle"]["kind"], "deny")

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
