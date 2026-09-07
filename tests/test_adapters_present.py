# tests/test_adapters_present.py
from pathlib import Path
import json


def test_six_adapter_files_exist_or_held(work_root: Path):
    camp = json.loads((work_root / "fixtures/demo-release/release_campaign.json").read_text())
    missing = []
    for art in camp["artifacts"]:
        if art.get("held"):
            continue
        path = art.get("path")
        if not path or not (work_root / path).exists():
            missing.append(art["type"])
    assert missing == [], f"missing adapters for: {missing}"
