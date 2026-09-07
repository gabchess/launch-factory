import json

REQUIRED_CHANNELS = [
    "changelog",
    "email_interrupt",
    "story_video",
    "linkedin_written",
    "x_written",
    "threads_written",
    "instagram_video",
    "tiktok_video",
]


def test_fixture_cadence_has_tier_blast_cells(work_root):
    from scripts.validate_campaign import validate_cadence_binder

    path = work_root / "fixtures/demo-release/cadence_binder.json"
    binder = json.loads(path.read_text(encoding="utf-8"))
    result = validate_cadence_binder(binder)
    assert result["ok"] is True
    channels = {c["channel"] for c in binder["cells"]}
    for ch in REQUIRED_CHANNELS:
        assert ch in channels
    assert binder["campaign_id"] == "camp_demo_001"
