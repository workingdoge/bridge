#!/usr/bin/env python3
"""Property checks for the reference bridge adapter interpretation boundary."""
from __future__ import annotations

import unittest
from pathlib import Path

import reference_adapter as adapter


HERE = Path(__file__).resolve().parent
EXAMPLES = HERE.parent / "examples"


class ReferenceAdapterInterpretationPropertyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = adapter.SchemaStore()
        self.authorize_request = adapter.load_json(EXAMPLES / "example.authorize-request.json")

    def test_admitted_interpretation_assembles(self) -> None:
        provider_results = adapter.load_json(EXAMPLES / "example.provider-results.accept.json")
        assembled = adapter.assemble(self.authorize_request, provider_results)
        adapter.validate(assembled, "policy-input.schema.json", self.store)
        audit = adapter.audit_stub(assembled, "time-authority://core/ntp-primary")
        adapter.validate(audit, "audit-record.schema.json", self.store)

    def test_non_admitted_interpretation_never_assembles(self) -> None:
        for name in ("unknown", "ambiguous", "stale"):
            provider_results = adapter.load_json(EXAMPLES / f"example.provider-results.{name}.json")
            with self.assertRaises(ValueError):
                adapter.assemble(self.authorize_request, provider_results)


if __name__ == "__main__":
    unittest.main()
