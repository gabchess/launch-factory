"""Build Drive-ready package folder — never publishes."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

SLOT_DIRS = {
    1: "01_social_video",
    2: "02_blog",
    3: "03_email_segments",
    4: "04_changelog",
    5: "05_login_animation",
    6: "06_in_app_popup",
    7: "07_campaign_plan",
}

# Campaign statuses that mean Claims Lock has not been recorded yet.
PRE_CLAIMS_LOCK_STATUSES = {
    "idle",
    "ingested",
    "retrieving",
    "claims_gate",
    "needs_source_fix",
}


def manifest_status_for(campaign: dict[str, Any]) -> str:
    """Honest pack status: pre-Claims-Lock review bundle unless Claims Lock recorded."""
    status = campaign.get("status") or "claims_gate"
    if status in PRE_CLAIMS_LOCK_STATUSES:
        return "review_ready_pre_claims_lock"
    return "packaged"


def render_reviewer_card(campaign: dict[str, Any], *, package_status: str) -> str:
    """Fill a Reviewer review card from campaign + MANIFEST-facing state (not empty mustache)."""
    camp_id = campaign["id"]
    title = campaign["title"]
    seat = campaign.get("reviewer", {}).get("seat", "Reviewer VP Marketing")
    surface = campaign.get("reviewer", {}).get("surface", "Notion + Drive pack")
    claims_lock_done = campaign.get("status") not in PRE_CLAIMS_LOCK_STATUSES
    claims_state = (
        "RECORDED (campaign past claims_gate)"
        if claims_lock_done
        else "NOT DONE — campaign still at claims_gate / pre-Claims-Lock"
    )

    rows: list[str] = []
    first_real: dict[str, Any] | None = None
    for art in sorted(campaign.get("artifacts") or [], key=lambda a: a.get("slot", 0)):
        slot = art.get("slot")
        atype = art.get("type")
        held = bool(art.get("held"))
        dirname = SLOT_DIRS.get(slot, f"{slot:02d}_{atype}")
        if held:
            link = f"{dirname}/HELD.txt"
            spot = "skip (HELD)"
            state = f"HELD — {art.get('hold_reason') or 'held'}"
        else:
            link = dirname
            if first_real is None:
                first_real = art
                spot = "required first (first real non-HELD slot)"
            else:
                spot = "after first-real spot-check"
            state = "real draft"
        rows.append(f"| {slot} | {atype} | {link} | {spot} | {state} |")

    first_real_label = (
        f"O{first_real['slot']} {first_real['type']}"
        if first_real
        else "(none — all held)"
    )

    lines = [
        f"# Reviewer review card — {camp_id}",
        "",
        f"**Campaign:** {camp_id} — {title}",
        f"**Seat:** {seat} (writer ≠ Reviewer)",
        f"**Surface:** {surface}",
        f"**Package status:** `{package_status}`",
        f"**Campaign status:** `{campaign.get('status')}`",
        f"**Claims Lock:** {claims_state}",
        f"**First real (non-HELD) spot-check:** {first_real_label}",
        f"**Fixture label:** `{campaign.get('fixture_label') or '(real customer folder)'}`",
        "",
        "## Honesty",
        "",
        (
            "This package is a **pre-Claims-Lock review bundle**. "
            "Reviewer Claims Lock is still required before pack-approve."
            if not claims_lock_done
            else "Claims Lock is recorded on the campaign; proceed to pack-approve gates."
        ),
        "",
        "## Slots",
        "",
        "| Slot | Type | Package path | Spot-check | State |",
        "|---|---|---|---|---|",
        *rows,
        "| 7 | campaign_plan | 07_campaign_plan/ | in pack-approve gate | Campaign Plan |",
        "| — | cadence binder (Campaign Plan data shape) | cadence/ | after pack spot-check | binder |",
        "",
        "## Review links (real drafts)",
        "",
        "- Blog (slot 2): `02_blog/`",
        "- Email segments (slot 3): `03_email_segments/`",
        "- Changelog (slot 4): `04_changelog/`",
        "- Claim ledger + sources: `provenance/`",
        "- Honesty table: `honesty/still-needs-human.md`",
        "- Pack-approve template: repo `reviewer/approve-pack-template.md`",
        "- Claims Lock template: repo `reviewer/claims-lock-template.md`",
        "",
        "## Decision",
        "",
        "- [ ] **Claims Lock approve** (once per campaign) — required before adapters are treated as ship-gated",
        "- [ ] **Approve pack** — only after Claims Lock + first-real-slot spot-check",
        "- [ ] **Request changes** — name artifact slot(s) only (no silent rewrite-as-approve)",
        "",
        "## Forbidden",
        "",
        "- Slack thumbs / emoji as Claims Lock or pack approve",
        "- Auto-publish / one-click ship",
        "- HubSpot send (sandbox draft-only only after Reviewer pack approve)",
        "- Inventing pricing, seats, or dollar-savings claims",
        "",
    ]
    return "\n".join(lines)


def build_package(
    campaign_path: Path, out_dir: Path, *, work_root: Path | None = None
) -> Path:
    campaign_path = campaign_path.resolve()
    if work_root is None:
        # .../fixtures/demo-release/release_campaign.json → work/
        work_root = campaign_path.parents[2]
    campaign: dict[str, Any] = json.loads(campaign_path.read_text(encoding="utf-8"))
    camp_id = campaign["id"]
    root = out_dir / camp_id
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    for slot, dirname in SLOT_DIRS.items():
        d = root / dirname
        d.mkdir()
        art = next(a for a in campaign["artifacts"] if a["slot"] == slot)
        if art.get("held"):
            reason = art.get("hold_reason") or "held"
            (d / "HELD.txt").write_text(reason, encoding="utf-8")
            continue
        src = work_root / art["path"]
        if src.exists():
            shutil.copy2(src, d / src.name)
        else:
            (d / "MISSING.txt").write_text(str(src), encoding="utf-8")

    cadence_src = campaign_path.parent / campaign.get("cadence_ref", "cadence_binder.json")
    (root / "cadence").mkdir()
    if cadence_src.exists():
        shutil.copy2(cadence_src, root / "cadence" / cadence_src.name)

    prov = root / "provenance"
    prov.mkdir()
    for key in ("transcript", "github_outline"):
        rel = campaign["sources"][key]
        src = campaign_path.parent / rel
        if src.exists():
            shutil.copy2(src, prov / src.name)
    ledger = campaign_path.parent / campaign["claim_ledger_ref"]
    if ledger.exists():
        shutil.copy2(ledger, prov / ledger.name)

    honesty_src = work_root / "honesty" / "still-needs-human.md"
    (root / "honesty").mkdir()
    if honesty_src.exists():
        shutil.copy2(honesty_src, root / "honesty" / "still-needs-human.md")
    else:
        (root / "honesty" / "still-needs-human.md").write_text(
            "\n".join(campaign.get("still_needs_human", [])), encoding="utf-8"
        )

    pkg_status = manifest_status_for(campaign)
    note = "STOP — humans publish out of band"
    if pkg_status == "review_ready_pre_claims_lock":
        note = (
            "STOP — pre-Claims-Lock review bundle; Reviewer Claims Lock still required "
            "before pack-approve; humans publish out of band"
        )

    manifest = {
        "campaign_id": camp_id,
        "title": campaign["title"],
        "fixture_label": campaign.get("fixture_label"),
        "status": pkg_status,
        "auto_publish": False,
        "reviewer_seat": campaign["reviewer"]["seat"],
        "hubspot_sandbox": campaign.get("hubspot_sandbox"),
        "note": note,
    }
    (root / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (root / "REVIEWER.md").write_text(
        render_reviewer_card(campaign, package_status=pkg_status), encoding="utf-8"
    )
    return root


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("campaign_json", type=Path)
    p.add_argument("out_dir", type=Path)
    p.add_argument(
        "--work-root",
        type=Path,
        default=None,
        help="Repo/work root for resolving adapter paths (default: campaign_json.parents[2])",
    )
    args = p.parse_args(argv)
    root = build_package(args.campaign_json, args.out_dir, work_root=args.work_root)
    print(root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
