REQUIRED_TYPES = [
    "social_video",
    "blog",
    "email_segments",
    "changelog",
    "login_animation",
    "in_app_popup",
    "campaign_plan",
]


def _minimal_campaign(**overrides):
    artifacts = []
    for i, t in enumerate(REQUIRED_TYPES, start=1):
        artifacts.append(
            {
                "slot": i,
                "type": t,
                "version": 1,
                "path": f"adapters/{i:02d}_{t}.md",
                "validation": "pass",
                "reviewer_status": "pending",
                "held": False,
                "hold_reason": None,
            }
        )
    base = {
        "id": "camp_demo_001",
        "title": "FIXTURE — FEATURE_NAME launch",
        "folder_id": "fixture/demo-release",
        "status": "drafting",
        "fixture_label": "LABELLED_FIXTURE_GENERIC_PLACEHOLDER",
        "sources": {
            "loom": "sources/loom_transcript.txt",
            "transcript": "sources/loom_transcript.txt",
            "github_outline": "sources/github_outline.md",
            "footage": ["sources/footage_index.json"],
        },
        "claim_ledger_ref": "claim_ledger.json",
        "voice_pack_ref": "voice_pack/fixture_placeholder",
        "segments": {
            "leads": ["SMB", "Agency", "Reseller_Affiliate"],
            "customers": ["SMB", "Agency"],
            "affiliate_rules": "FIXTURE — legal TBD from the customer",
        },
        "artifacts": artifacts,
        "cadence_ref": "cadence_binder.json",
        "reviewer": {
            "seat": "Reviewer VP Marketing",
            "surface": "Notion + Drive pack",
            "wip": 1,
        },
        "hubspot_sandbox": {"draft_ids": [], "status": "not_started"},
        "still_needs_human": ["Claims Lock seed", "Final publish"],
    }
    base.update(overrides)
    return base


def test_validate_campaign_requires_seven_slots():
    from scripts.validate_campaign import validate_campaign

    result = validate_campaign(_minimal_campaign())
    assert result["ok"] is True


def test_validate_campaign_fails_when_slot_missing_and_not_held():
    from scripts.validate_campaign import validate_campaign

    camp = _minimal_campaign()
    camp["artifacts"][5]["path"] = None
    camp["artifacts"][5]["held"] = False
    result = validate_campaign(camp)
    assert result["ok"] is False
    assert any("slot 6" in e.lower() or "in_app_popup" in e.lower() for e in result["errors"])


def test_validate_campaign_allows_held_slot_without_path():
    from scripts.validate_campaign import validate_campaign

    camp = _minimal_campaign()
    camp["artifacts"][4]["path"] = None
    camp["artifacts"][4]["held"] = True
    camp["artifacts"][4]["hold_reason"] = "claim missing — hold on camera"
    camp["artifacts"][4]["reviewer_status"] = "held"
    result = validate_campaign(camp)
    assert result["ok"] is True


def test_validate_campaign_fails_when_campaign_plan_slot_missing():
    from scripts.validate_campaign import validate_campaign

    camp = _minimal_campaign()
    camp["artifacts"] = [a for a in camp["artifacts"] if a["slot"] != 7]
    result = validate_campaign(camp)
    assert result["ok"] is False
    assert any("slot 7" in e or "campaign_plan" in e for e in result["errors"])


def test_fixture_campaign_validates(work_root):
    from scripts.validate_campaign import validate_campaign
    import json

    path = work_root / "fixtures/demo-release/release_campaign.json"
    camp = json.loads(path.read_text(encoding="utf-8"))
    result = validate_campaign(camp)
    assert result["ok"] is True
    assert camp["fixture_label"].startswith("LABELLED_FIXTURE")
