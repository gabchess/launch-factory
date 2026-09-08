"""Offline finishing contracts and selective support-skill routing."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import jsonschema
import pytest

from scripts.specialist_route import ROOT, route_request
from test_specialist_routing import packet

FINISHING = ROOT / "engine/specialists/finishing"
spec = importlib.util.spec_from_file_location("motion_finishing_check", FINISHING / "validate.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
validate = module.validate


def load(name):
    return json.loads((FINISHING / name).read_text())


def test_finishing_is_selected_by_existing_media_owners_only(packet, tmp_path):
    for deliverable in ["social_video", "login_animation"]:
        result = route_request({**packet, "deliverable": deliverable, "stage": "review"}, tmp_path)
        assert [s["skill"] for s in result["support_skills"]] == ["lf-short-motion-finishing"]
        assert (ROOT / result["support_skills"][0]["skill_path"]).is_file()
    assert route_request({**packet, "stage": "review"}, tmp_path)["support_skills"] == []
    assert route_request({**packet, "deliverable": "social_video", "stage": "source"}, tmp_path)["support_skills"] == []


def test_ten_second_cue_sheet_and_new_duration_are_supported(tmp_path):
    cues = load("cue-sheet-10s.example.json")
    assert validate("cues", cues, tmp_path)["status"] == "passed"
    cues["duration_ms"] = 60000
    cues["brief_reference"] = "Separate user-approved restaurant brief"
    assert validate("cues", cues, tmp_path)["status"] == "passed"
    cues["cues"][0]["end_ms"] = 61000
    with pytest.raises(ValueError, match="outside"):
        validate("cues", cues, tmp_path)


def test_music_mode_rejects_added_speech_and_unresolved_media(tmp_path):
    cues = load("cue-sheet-10s.example.json")
    cues["cues"][0]["kind"] = "speech"
    with pytest.raises(ValueError, match="speech"):
        validate("cues", cues, tmp_path)
    cues["cues"][0]["kind"] = "music"
    cues["status"] = "resolved"
    with pytest.raises(ValueError, match="manifest"):
        validate("cues", cues, tmp_path)
    with pytest.raises(ValueError, match="unavailable"):
        validate("cues", cues, tmp_path, load("generation-manifest.example.json"))


def test_caption_json_uses_real_audio_binding_and_speech_purpose(tmp_path):
    data = b"fixture audio bytes, not a generated performance"
    (tmp_path / "speech.bin").write_bytes(data)
    captions = {"schema_version": "speech-captions/v1", "purpose": "speech",
                "audio": {"path": "speech.bin", "sha256": hashlib.sha256(data).hexdigest()},
                "captions": [{"text": " Hello", "startMs": 0, "endMs": 300, "timestampMs": None,
                              "confidence": None, "pageBreakAfter": True}]}
    assert validate("captions", captions, tmp_path)["status"] == "passed"
    wrong = copy.deepcopy(captions)
    wrong["purpose"] = "headline"
    with pytest.raises(jsonschema.ValidationError):
        validate("captions", wrong, tmp_path)
    wrong = copy.deepcopy(captions)
    wrong["captions"][0]["endMs"] = 0
    with pytest.raises(jsonschema.ValidationError):
        validate("captions", wrong, tmp_path)
    (tmp_path / "speech.bin").write_bytes(b"changed audio")
    with pytest.raises(ValueError, match="hash"):
        validate("captions", captions, tmp_path)


def test_chatcut_provenance_cannot_be_relabelled_heygen(tmp_path):
    manifest = load("generation-manifest.example.json")
    asset = manifest["assets"][0]
    asset.update(provider="chatcut", job_id="fixture-job", provider_receipt={"provider": "chatcut", "job_id": "fixture-job", "reference": "Fixture receipt; no provider called"})
    assert validate("manifest", manifest, tmp_path)["status"] == "passed"
    asset["provider"] = "heygen"
    with pytest.raises(ValueError, match="conflicts"):
        validate("manifest", manifest, tmp_path)


def test_materialized_asset_requires_bytes_and_license_claim_needs_reference(tmp_path):
    manifest = load("generation-manifest.example.json")
    asset = manifest["assets"][0]
    asset["status"] = "materialized"
    with pytest.raises(ValueError, match="file and hash"):
        validate("manifest", manifest, tmp_path)
    asset["status"] = "planned"
    asset["license"]["status"] = "verified"
    with pytest.raises(ValueError, match="evidence"):
        validate("manifest", manifest, tmp_path)


def test_motion_rule_count_and_unsafe_fades_are_refused(tmp_path):
    cues = load("cue-sheet-10s.example.json")
    cues["motion_rules"] = ["one"]
    with pytest.raises(jsonschema.ValidationError):
        validate("cues", cues, tmp_path)
    cues["motion_rules"] = ["one", "two"]
    cues["cues"][1]["fade_in_ms"] = 400
    with pytest.raises(ValueError, match="fades"):
        validate("cues", cues, tmp_path)


def test_review_evidence_cannot_transfer_to_changed_media(tmp_path):
    manifest = load("generation-manifest.example.json")
    media = tmp_path / "rendition.bin"
    media.write_bytes(b"fixture rendition one")
    sha = hashlib.sha256(media.read_bytes()).hexdigest()
    manifest["assets"][0].update(status="materialized", media={"path": media.name, "sha256": sha})
    manifest["checks"] = [{"kind": "decode", "status": "pass", "asset_id": manifest["assets"][0]["id"],
                           "sha256": sha, "reference": "Fixture check only; not a real decode"}]
    assert validate("manifest", manifest, tmp_path)["status"] == "passed"
    media.write_bytes(b"fixture rendition two")
    manifest["assets"][0]["media"]["sha256"] = hashlib.sha256(media.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="exact current media hash"):
        validate("manifest", manifest, tmp_path)


@pytest.mark.parametrize("field,value", [("start_ms", float("nan")), ("end_ms", float("inf")), ("gain_db", float("-inf"))])
def test_nonfinite_values_are_refused_by_api_and_json_loader(tmp_path, field, value):
    cues = load("cue-sheet-10s.example.json")
    cues["cues"][0][field] = value
    with pytest.raises(ValueError, match="Non-finite"):
        validate("cues", cues, tmp_path)
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(cues))
    with pytest.raises(ValueError, match="Non-finite"):
        module.read_json(path)
    path.write_text('{"value": 1e999}')
    with pytest.raises(ValueError, match="Non-finite"):
        module.read_json(path)
