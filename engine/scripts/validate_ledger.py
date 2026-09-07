"""Claim ledger validation — evidence spans + forbidden list + kill-switch."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "claim_ledger.schema.json"


def _load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_ledger(ledger: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    schema = _load_schema()
    validator = Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(ledger), key=lambda e: list(e.path)):
        errors.append(f"schema: {err.message}")

    allowed_ids = {c["claim_id"] for c in ledger.get("allowed", []) if "claim_id" in c}
    evidence_by_claim: dict[str, list[dict[str, Any]]] = {}
    for ev in ledger.get("evidence", []):
        evidence_by_claim.setdefault(ev.get("claim_id", ""), []).append(ev)

    for claim in ledger.get("allowed", []):
        cid = claim.get("claim_id")
        spans = evidence_by_claim.get(cid, [])
        if not spans:
            errors.append(f"allowed claim {cid!r} has no evidence span")
            continue
        for sp in spans:
            if sp.get("span_end", -1) <= sp.get("span_start", 0):
                errors.append(f"evidence for {cid!r} has non-positive span")
            if not (sp.get("quote") or "").strip():
                errors.append(f"evidence for {cid!r} has empty quote")

    forbidden_texts = {
        (f.get("text") or "").strip().lower()
        for f in ledger.get("forbidden", [])
        if (f.get("text") or "").strip()
    }
    for claim in ledger.get("allowed", []):
        text = (claim.get("text") or "").strip().lower()
        for ft in forbidden_texts:
            if ft and ft in text:
                errors.append(
                    f"forbidden claim text appears in allowed claim {claim.get('claim_id')!r}: {ft!r}"
                )

    for cid in evidence_by_claim:
        if cid and cid not in allowed_ids and cid not in {
            c.get("claim_id") for c in ledger.get("needs_disclaimer", [])
        }:
            errors.append(f"evidence references unknown claim_id {cid!r}")

    armed = bool(errors)
    reason = "; ".join(errors) if armed else None
    return {
        "ok": not armed,
        "errors": errors,
        "kill_switch": {"armed": armed, "reason": reason},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate ClaimLedger JSON")
    parser.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    ledger = json.loads(args.path.read_text(encoding="utf-8"))
    result = validate_ledger(ledger)
    print(json.dumps(result, indent=2))
    if result["kill_switch"]["armed"]:
        return 2
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
