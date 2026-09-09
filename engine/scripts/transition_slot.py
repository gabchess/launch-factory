#!/usr/bin/env python3
# STRUCTURAL_INTEGRITY_ONLY — applies permitted state transitions to one slot
# of a release-record. Never publishes. `approved`/`packaged` require
# --human-confirmed and are recorded as Reviewer gate decisions; the writer seat
# never self-approves.
"""transition_slot RECORD SLOT STATUS [--human-confirmed] [--reason TEXT]

SLOT: 1-7 or a slot name (social_video, blog, email_segments, changelog,
login_animation, in_app_popup, campaign_plan).
STATUS: drafted | reviewed | approved | packaged | held.

Permitted transitions:
  held      -> drafted      (un-hold: work begins; clears hold_reason)
  drafted   -> reviewed     (passed the four review gates)
  drafted   -> held         (--reason required)
  reviewed  -> approved     (--human-confirmed required; records Reviewer gate)
  reviewed  -> held         (--reason required)
  reviewed  -> drafted      (request changes: back to the writer)
  approved  -> packaged     (--human-confirmed required; records Reviewer gate)
  approved  -> reviewed     (request changes after approve, before packaging)
Everything else is refused.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SLOT_NAMES = {
    1: "social_video",
    2: "blog",
    3: "email_segments",
    4: "changelog",
    5: "login_animation",
    6: "in_app_popup",
    7: "campaign_plan",
}
NAME_TO_SLOT = {v: k for k, v in SLOT_NAMES.items()}

PERMITTED = {
    ("held", "drafted"),
    ("drafted", "reviewed"),
    ("drafted", "held"),
    ("reviewed", "approved"),
    ("reviewed", "held"),
    ("reviewed", "drafted"),
    ("approved", "packaged"),
    ("approved", "reviewed"),
}

HUMAN_CONFIRMED_TARGETS = {"approved", "packaged"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def resolve_slot(token: str) -> int:
    if token.isdigit() and int(token) in SLOT_NAMES:
        return int(token)
    if token in NAME_TO_SLOT:
        return NAME_TO_SLOT[token]
    raise SystemExit(f"unknown slot: {token} (use 1-7 or a slot name)")


def transition_slot(
    record: dict[str, Any], slot_token: str, status: str, *,
    human_confirmed: bool = False, reason: str | None = None,
) -> dict[str, Any]:
    n = resolve_slot(slot_token)
    slot = next((s for s in record["slots"] if s.get("slot") == n), None)
    if slot is None:
        raise SystemExit(f"record has no slot {n}")
    current = slot.get("state")
    if status not in ("drafted", "reviewed", "approved", "packaged", "held"):
        raise SystemExit(f"unknown status: {status}")
    if (current, status) not in PERMITTED:
        raise SystemExit(
            f"refused: transition {current} -> {status} on slot {n} is not permitted"
        )
    if status in HUMAN_CONFIRMED_TARGETS and not human_confirmed:
        raise SystemExit(
            f"refused: `{status}` requires --human-confirmed — only Reviewer (human) "
            "authorizes approved/packaged; the writer seat never self-approves"
        )
    if status == "held" and not reason:
        raise SystemExit("refused: held requires --reason (a hold without a reason is a gap, not a hold)")

    slot["state"] = status
    if status == "held":
        slot["hold_reason"] = reason
    elif status == "drafted":
        slot["hold_reason"] = None

    at = _now()
    if status in HUMAN_CONFIRMED_TARGETS:
        record["gates"].append(
            {
                "gate": f"slot-{n}",
                "decision": "approve",
                "decided_by": "reviewer",
                "at": at,
                "note": f"human-confirmed transition to {status}",
            }
        )
    record["run_log"].append(
        {"at": at, "entry": f"transition_slot: slot {n} ({SLOT_NAMES[n]}) {current} -> {status}"}
    )
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Apply a permitted state transition to one record slot")
    parser.add_argument("record", type=Path)
    parser.add_argument("slot")
    parser.add_argument("status")
    parser.add_argument("--human-confirmed", action="store_true",
                        help="required for approved/packaged — Reviewer's decision, recorded as a gate entry")
    parser.add_argument("--reason", default=None, help="hold_reason (required when status=held)")
    args = parser.parse_args(argv)
    record = json.loads(args.record.read_text(encoding="utf-8"))
    record = transition_slot(
        record, args.slot, args.status,
        human_confirmed=args.human_confirmed, reason=args.reason,
    )
    args.record.write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"slot {args.slot} -> {args.status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
