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
        "cadence",
        "provenance",
        "honesty",
    ]:
        assert (out / name).exists()
    assert (out / "honesty" / "still-needs-human.md").exists()
    manifest = json.loads((out / "MANIFEST.json").read_text())
    assert manifest["campaign_id"] == "camp_demo_001"
    assert manifest["auto_publish"] is False
