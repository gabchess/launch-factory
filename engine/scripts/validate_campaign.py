"""ReleaseCampaign validation — schema + six slots exist-or-held."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "release_campaign.schema.json"
CADENCE_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "cadence_binder.schema.json"

REQUIRED_TYPES = [
    "social_video",
    "blog",
    "email_segments",
    "changelog",
    "login_animation",
    "in_app_popup",
    "campaign_plan",
]

REQUIRED_CADENCE_CHANNELS = [
    "changelog",
    "email_interrupt",
    "story_video",
    "linkedin_written",
    "x_written",
    "threads_written",
    "instagram_video",
    "tiktok_video",
]

FORBIDDEN_STATUS_TRANSITIONS_NOTE = (
    "Validators do not publish. Forbidden: drafting→published; "
    "awaiting_reviewer→sandbox without Reviewer approve."
)


def validate_campaign(
    campaign: dict[str, Any], *, schema_path: Path | None = None
) -> dict[str, Any]:
    errors: list[str] = []
    path = schema_path or SCHEMA_PATH
    schema = json.loads(path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(campaign), key=lambda e: list(e.path)):
        errors.append(f"schema: {err.message}")

    artifacts = campaign.get("artifacts") or []
    by_slot = {a.get("slot"): a for a in artifacts if isinstance(a, dict)}
    types_seen = []
    for slot in range(1, 8):
        art = by_slot.get(slot)
        if art is None:
            errors.append(f"missing artifact slot {slot}")
            continue
        types_seen.append(art.get("type"))
        held = bool(art.get("held"))
        path_val = art.get("path")
        if not held and not path_val:
            errors.append(
                f"slot {slot} ({art.get('type')}) missing path and not held"
            )
        if held and not art.get("hold_reason"):
            errors.append(f"slot {slot} held without hold_reason")

    for required in REQUIRED_TYPES:
        if required not in types_seen:
            errors.append(f"missing required artifact type {required}")

    reviewer = campaign.get("reviewer") or {}
    if reviewer.get("wip") != 1:
        errors.append("reviewer.wip must be 1 (WIP=1 awaiting_reviewer)")
    if reviewer.get("seat") != "Reviewer VP Marketing":
        errors.append("reviewer.seat must be 'Reviewer VP Marketing'")

    segs = campaign.get("segments") or {}
    if not segs.get("leads"):
        errors.append("segments.leads must be present")
    if not segs.get("customers"):
        errors.append("segments.customers must be present")

    hs = campaign.get("hubspot_sandbox") or {}
    if hs.get("status") == "draft_only" and campaign.get("status") == "awaiting_reviewer":
        errors.append(
            "hubspot sandbox draft blocked while awaiting_reviewer (Apiana hygiene)"
        )

    return {"ok": len(errors) == 0, "errors": errors, "note": FORBIDDEN_STATUS_TRANSITIONS_NOTE}


def validate_cadence_binder(binder: dict[str, Any]) -> dict[str, Any]:
    """Used from Task 5 onward; defined here so one module owns campaign-adjacent checks."""
    errors: list[str] = []
    if not CADENCE_SCHEMA_PATH.exists():
        errors.append("cadence_binder.schema.json missing — complete Task 5")
        return {"ok": False, "errors": errors}
    schema = json.loads(CADENCE_SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(binder), key=lambda e: list(e.path)):
        errors.append(f"schema: {err.message}")
    channels = {c.get("channel") for c in binder.get("cells", [])}
    for ch in REQUIRED_CADENCE_CHANNELS:
        if ch not in channels:
            errors.append(f"missing cadence cell for channel {ch}")
    return {"ok": len(errors) == 0, "errors": errors}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate ReleaseCampaign JSON")
    parser.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    campaign = json.loads(args.path.read_text(encoding="utf-8"))
    result = validate_campaign(campaign)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
