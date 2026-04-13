#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

BASE = Path(__file__).resolve().parent.parent
EX = BASE / "examples"


def run_case(attestation: str, revocation: str, mode: str) -> dict:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        decision = td / "decision.json"
        audit = td / "audit.json"
        subprocess.run(
            [
                sys.executable,
                str(BASE / "python" / "reference_sidecar.py"),
                "--catalog", str(EX / "provider-catalog.example.json"),
                "--deployment", str(EX / "deployment-profile.nixos-host.json"),
                "--request", str(EX / "provider-request.allow.json"),
                "--attestation", str(EX / attestation),
                "--revocation", str(EX / revocation),
                "--mode", str(EX / mode),
                "--decision-out", str(decision),
                "--audit-out", str(audit),
                "--now", "2026-04-13T14:30:30Z",
            ],
            check=True,
        )
        return json.loads(decision.read_text())


def main() -> None:
    allow = run_case("attestation-result.good.json", "revocation-snapshot.clean.json", "mode-state.normal.json")
    assert allow["status"] == "accept", allow

    burn = run_case("attestation-result.good.json", "revocation-snapshot.clean.json", "mode-state.burn.json")
    assert burn["status"] == "burn", burn

    deny = run_case("attestation-result.failed.json", "revocation-snapshot.clean.json", "mode-state.normal.json")
    assert deny["status"] == "deny", deny
    assert "attestation not verified" in deny["reasons"], deny

    print("reference_sidecar tests passed")


if __name__ == "__main__":
    main()
