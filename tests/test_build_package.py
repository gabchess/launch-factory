from pathlib import Path
import json


def test_build_package_layout(work_root, tmp_path):
    from scripts.build_package import build_package

    out = build_package(
        work_root / "fixtures/demo-release/release_campaign.json",
        tmp_path / "drive_ready",
        work_root=work_root,
    )
    assert out.name == "camp_demo_001"
    for name in [
        "01_social_video",
        "02_blog",
        "03_email_segments",
        "04_changelog",
        "05_login_animation",
        "06_in_app_popup",
        "07_campaign_plan",
        "cadence",
        "provenance",
        "honesty",
    ]:
        assert (out / name).exists()
    assert (out / "honesty" / "still-needs-human.md").exists()
    assert (out / "REVIEWER.md").exists()
    manifest = json.loads((out / "MANIFEST.json").read_text())
    assert manifest["campaign_id"] == "camp_demo_001"
    assert manifest["auto_publish"] is False
    # demo-release is past claims_gate (drafting) → packaged
    assert manifest["status"] == "packaged"
    reviewer = (out / "REVIEWER.md").read_text(encoding="utf-8")
    assert "Approve pack" in reviewer
    assert "Slack thumbs" in reviewer


def test_seed_release_package_pre_claims_lock(work_root, tmp_path):
    from scripts.build_package import build_package

    out = build_package(
        work_root / "fixtures/seed-release/release_campaign.json",
        tmp_path / "drive_ready",
        work_root=work_root,
    )
    assert out.name == "camp_seed_001"
    manifest = json.loads((out / "MANIFEST.json").read_text())
    assert manifest["status"] == "review_ready_pre_claims_lock"
    assert manifest["auto_publish"] is False
    assert manifest["fixture_label"] == "reviewer-email-seed"
    assert "pre-Claims-Lock" in manifest["note"]
    assert (out / "REVIEWER.md").exists()
    reviewer = (out / "REVIEWER.md").read_text(encoding="utf-8")
    assert "NOT DONE" in reviewer
    assert "O2 blog" in reviewer or "first real" in reviewer.lower()
    assert "02_blog" in reviewer
    assert "auto-publish" in reviewer.lower() or "Auto-publish" in reviewer
    held = (out / "01_social_video" / "HELD.txt").read_text(encoding="utf-8")
    assert "NO video" in held or "Loom" in held
    honesty = (out / "honesty" / "still-needs-human.md").read_text(encoding="utf-8")
    assert "pre-Claims-Lock" in honesty


def test_manifest_status_helper():
    from scripts.build_package import manifest_status_for

    assert (
        manifest_status_for({"status": "claims_gate"})
        == "review_ready_pre_claims_lock"
    )
    assert manifest_status_for({"status": "drafting"}) == "packaged"
    assert manifest_status_for({"status": "approved"}) == "packaged"
