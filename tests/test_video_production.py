"""One-rendition actor packet checks using local text/byte fixtures only."""
import copy
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import jsonschema
import pytest

from scripts.specialist_route import ROOT, REGISTRY

PRODUCTION = ROOT / "engine/specialists/video-production"
spec = importlib.util.spec_from_file_location("actor_production_check", PRODUCTION / "validate.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def put(workspace, name, data):
    if isinstance(data, str):
        data = data.encode()
    (workspace / name).write_bytes(data)
    return {"path": name, "sha256": hashlib.sha256(data).hexdigest(), "version": 1}


def decision(workspace, subject, name="fixture-decision"):
    return {"event_id": name, "actor": "fixture-reviewer", "decision": "accepted",
            "subject_digest": module.digest(subject),
            "reference": put(workspace, name + ".txt", "Synthetic decision fixture, no actual human approval.")}


@pytest.fixture
def job(tmp_path):
    shutil.copytree(PRODUCTION / "example-workspace", tmp_path, dirs_exist_ok=True)
    value = json.loads((PRODUCTION / "example.json").read_text())
    value["story_decision"] = decision(tmp_path, module.story_subject(value), "story")
    value["reference_decision"] = decision(tmp_path, module.reference_subject(value), "references")
    value["route"]["capability_reference"] = put(tmp_path, "capability.txt", "Synthetic fixture; no provider access tested.")
    value["budget"].update(per_call_ceiling=5, film_ceiling=50, film_spent=10)
    value["quote"] = {"producer": value["route"]["producer"], "model": value["route"]["model"],
                      "duration_ms": 5000, "quantity": 1, "unit": "USD", "amount": 2,
                      "usd_estimate": 2, "conversion_reference": None,
                      "reference": put(tmp_path, "quote.txt", "Synthetic two-dollar quote fixture.")}
    return value


def returned(job, tmp_path):
    value = copy.deepcopy(job)
    media = put(tmp_path, "take.bin", b"Synthetic provider bytes; not a playable clip.")
    manifest = json.loads((ROOT / "engine/specialists/finishing/generation-manifest.example.json").read_text())
    asset = manifest["assets"][0]
    asset.update(id="take", origin="generated", status="materialized", provider=value["route"]["producer"],
                 job_id="fixture-provider-job", provider_receipt={"provider": value["route"]["producer"], "job_id": "fixture-provider-job", "reference": "Synthetic fixture"},
                 media={k: media[k] for k in ("path", "sha256")})
    inputs = [value["story"]["script"]] + [ref["binding"] for ref in value["references"]]
    if value["shot"]["speech_input"] is not None:
        inputs.append(value["shot"]["speech_input"])
    input_assets = []
    for index, binding in enumerate(inputs):
        record = copy.deepcopy(asset)
        record.update(id="input-" + str(index), origin="authored", provider=None, job_id=None,
                      provider_receipt=None, input_asset_ids=[],
                      media={k: binding[k] for k in ("path", "sha256")})
        input_assets.append(record)
    asset["input_asset_ids"] = [a["id"] for a in input_assets]
    manifest["assets"] = input_assets + [asset]
    manifest["checks"] = []
    value["state"] = "returned"
    value["runtime"] = {"job_id": "fixture-provider-job", "output": {
        "output_id": "fixture-provider-output", "asset_id": "take", "version": 1,
        "producer": value["route"]["producer"], "model": value["route"]["model"],
        "media": media, "speech_audio": None,
        "manifest": put(tmp_path, "manifest.json", json.dumps(manifest))}}
    return value


def test_portable_example_starts_held_and_reaches_existing_video_lead(tmp_path):
    shutil.copytree(PRODUCTION / "example-workspace", tmp_path, dirs_exist_ok=True)
    value = json.loads((PRODUCTION / "example.json").read_text())
    result = module.validate(value, tmp_path)
    assert result["status"] == "held" and "quote_unknown" in result["holds"]
    assert not result["execution_authorized"] and value["runtime"] == {"job_id": None, "output": None}
    assert REGISTRY["roles"]["video_lead"]["production_protocol"] == "engine/specialists/video-production/PROTOCOL.md"
    for host in (".agents", ".claude"):
        wrapper = ROOT / host / "skills/lf-video-production/SKILL.md"
        assert "video-production/PROTOCOL.md" in wrapper.read_text()
    assert all(name in (PRODUCTION / "PROTOCOL.md").read_text() for name in ("PROMPTS.md", "production-job.schema.json", "validate.py"))
    assert "/Users/" not in json.dumps(value)


def test_sixty_second_film_keeps_five_second_first_sample_and_decisions(job, tmp_path):
    before = copy.deepcopy(job["story"])
    result = module.validate(job, tmp_path)
    assert result["status"] == "consistent_record" and job["story"] == before
    assert job["brief"]["film_duration_ms"] == 60000 and job["shot"]["edit_duration_ms"] == 5000
    assert result["next_gate"] == "operator_authority_check" and not result["execution_authorized"]
    job["brief"]["channel_max_duration_ms"] = 30000
    with pytest.raises(ValueError, match="channel cap"):
        module.validate(job, tmp_path)


def test_locked_words_and_reference_versions_cannot_reuse_old_binding(job, tmp_path):
    job["shot"]["speech"]["text"] = "Invented shorter line."
    with pytest.raises(ValueError, match="script span"):
        module.validate(job, tmp_path)
    job["shot"]["speech"] = copy.deepcopy(job["price_constraints"][0]["source"])
    job["story"]["script"]["version"] += 1
    assert "story_decision_missing_changed_or_requests_changes" in module.validate(job, tmp_path)["holds"]
    job["references"][1]["binding"]["version"] += 1
    assert "reference_decision_missing_changed_or_requests_changes" in module.validate(job, tmp_path)["holds"]
    job["shot"]["voice_reference_id"] = "identity-example"
    with pytest.raises(ValueError, match="wrong-role"):
        module.validate(job, tmp_path)


def test_dry_sample_cannot_erase_whole_film_audio_or_add_guessed_speech(job, tmp_path):
    assert job["shot"]["audio"]["music"]["mode"] == "off"
    del job["brief"]["audio"]["music"]
    with pytest.raises(jsonschema.ValidationError):
        module.validate(job, tmp_path)
    job["brief"]["audio"]["music"] = {"mode": "off", "plan": "User requests no music across this whole film."}
    assert "story_decision_missing_changed_or_requests_changes" in module.validate(job, tmp_path)["holds"]
    job["shot"]["dialogue_source"] = "silent"
    with pytest.raises(ValueError, match="Silent"):
        module.validate(job, tmp_path)


def test_approved_audio_branch_binds_actual_clip_audio_and_its_review(job, tmp_path):
    job["shot"]["dialogue_source"] = "approved_audio"
    with pytest.raises(ValueError, match="speech input"):
        module.validate(job, tmp_path)
    job["shot"]["speech_input"] = put(tmp_path, "speech.bin", b"Synthetic approved-audio fixture")
    assert "reference_decision_missing_changed_or_requests_changes" in module.validate(job, tmp_path)["holds"]
    job["reference_decision"] = decision(tmp_path, module.reference_subject(job), "references")
    assert module.validate(returned(job, tmp_path), tmp_path)["status"] == "consistent_record"


@pytest.mark.parametrize("field,value", [("count", 2), ("auto_retry", True), ("after_result", "generate_all_shots")])
def test_one_sample_cannot_become_batch_retry_or_auto_fanout(job, tmp_path, field, value):
    job["execution"][field] = value
    with pytest.raises(jsonschema.ValidationError):
        module.validate(job, tmp_path)


def test_quote_source_take_and_edit_trim_are_distinct(job, tmp_path):
    job["shot"].update(generation_duration_ms=10000, trim_start_ms=2000)
    with pytest.raises(ValueError, match="source duration"):
        module.validate(job, tmp_path)
    job["quote"]["duration_ms"] = 10000
    assert module.validate(job, tmp_path)["status"] == "consistent_record"
    job["shot"]["trim_start_ms"] = 6000
    with pytest.raises(ValueError, match="trim"):
        module.validate(job, tmp_path)


def test_unknown_prices_credits_and_budget_are_never_assumed_free(job, tmp_path):
    job["quote"]["amount"] = None
    assert "quote_cost_unknown" in module.validate(job, tmp_path)["holds"]
    job["quote"].update(amount=20, unit="provider_credits")
    assert "credit_to_usd_conversion_unverified" in module.validate(job, tmp_path)["holds"]
    job["quote"]["conversion_reference"] = put(tmp_path, "conversion.txt", "Synthetic credit conversion fixture.")
    assert module.validate(job, tmp_path)["status"] == "consistent_record"
    job["quote"]["usd_estimate"] = 6
    with pytest.raises(ValueError, match="budget"):
        module.validate(job, tmp_path)
    job["quote"]["usd_estimate"] = 2
    job["budget"]["film_spent"] = 49
    with pytest.raises(ValueError, match="budget"):
        module.validate(job, tmp_path)
    job["quote"]["amount"] = -1
    with pytest.raises(jsonschema.ValidationError):
        module.validate(job, tmp_path)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_values_fail_api_and_cli_loader(job, tmp_path, value):
    job["quote"]["amount"] = value
    with pytest.raises(ValueError, match="Non-finite"):
        module.validate(job, tmp_path)
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(job))
    with pytest.raises(ValueError, match="Non-finite"):
        module.read_json(path)


def test_strict_product_price_limit_is_separate_from_production_budget(job, tmp_path):
    price = job["price_constraints"][0]
    price["illustrative_values"] = [30]
    with pytest.raises(ValueError, match="price violates"):
        module.validate(job, tmp_path)
    price["illustrative_values"] = [29]
    price["amount"] = None
    assert "product_price_unknown:illustrative-lamp-budget" in module.validate(job, tmp_path)["holds"]


def test_planned_ids_and_returned_producer_must_be_honest(job, tmp_path):
    job["runtime"]["job_id"] = "invented"
    with pytest.raises(ValueError, match="Prepared"):
        module.validate(job, tmp_path)
    job["runtime"]["job_id"] = None
    value = returned(job, tmp_path)
    assert module.validate(value, tmp_path)["next_gate"] == "awaiting_human_review"
    value["runtime"]["output"]["producer"] = "different-producer"
    with pytest.raises(ValueError, match="producer"):
        module.validate(value, tmp_path)
    value["runtime"]["output"]["producer"] = job["route"]["producer"]
    (tmp_path / "take.bin").write_bytes(b"Changed bytes")
    with pytest.raises(ValueError, match="hash"):
        module.validate(value, tmp_path)


def test_review_replay_never_grants_authority_and_changed_subject_stays_held(job, tmp_path):
    value = returned(job, tmp_path)
    subject = module.validate(value, tmp_path)["subjects"]["rendition"]
    value["generation_review"] = decision(tmp_path, None, "render-review")
    value["generation_review"]["subject_digest"] = subject
    for _ in range(2):
        result = module.validate(value, tmp_path)
        assert result["review_binding_matches"]
        assert result["next_gate"] == "awaiting_human_review"
        assert not any(result[k] for k in ("event_applied", "human_approval_granted", "execution_authorized", "authentication_verified"))
    value["shot"]["wardrobe"] = "Changed shirt"
    assert "rendition_review_subject_mismatch" in module.validate(value, tmp_path)["holds"]
    value["generation_review"] = []
    with pytest.raises(jsonschema.ValidationError):
        module.validate(value, tmp_path)


@pytest.mark.parametrize("change", ["duration", "format", "disclosure", "comparator"])
def test_approved_brief_constraint_changes_reopen_only_the_story_binding(job, tmp_path, change):
    if change == "duration":
        job["brief"]["film_duration_ms"] = 30000
    elif change == "format":
        job["brief"]["aspect_ratio"] = "9:16"
    elif change == "disclosure":
        job["brief"]["disclosures"] = []
    else:
        job["price_constraints"][0]["comparator"] = "lte"
    result = module.validate(job, tmp_path)
    assert "story_decision_missing_changed_or_requests_changes" in result["holds"]
    assert "reference_decision_missing_changed_or_requests_changes" not in result["holds"]


def test_request_changes_can_prepare_one_bounded_revision_without_fake_acceptance(job, tmp_path):
    prior = module.validate(returned(job, tmp_path), tmp_path)
    review = decision(tmp_path, prior["rendition_binding"], "changes-requested")
    assert review["subject_digest"] == prior["subjects"]["rendition"]
    review["decision"] = "request_changes"
    original_review = copy.deepcopy(review)
    job.update(purpose="revision", previous_rendition={"subject": prior["rendition_binding"], "review": review},
               revision_scope="Correct the unwanted camera cut; preserve locked speech and references.")
    result = module.validate(job, tmp_path)
    assert result["status"] == "consistent_record" and not result["execution_authorized"]
    assert job["previous_rendition"]["review"] == original_review
    job["revision_scope"] = None
    with pytest.raises(ValueError, match="Revision requires"):
        module.validate(job, tmp_path)


def test_prior_accepted_rendition_review_round_trips_unchanged_to_next_shot(job, tmp_path):
    prior = module.validate(returned(job, tmp_path), tmp_path)
    review = decision(tmp_path, prior["rendition_binding"], "accepted-sample")
    original = copy.deepcopy(review)
    job.update(purpose="shot_rendition", job_key="next-authorized-shot",
               previous_rendition={"subject": prior["rendition_binding"], "review": review})
    assert module.validate(job, tmp_path)["status"] == "consistent_record"
    assert job["previous_rendition"]["review"] == original
    job["previous_rendition"]["subject"]["output"]["version"] += 1
    assert "previous_rendition_review_missing_changed_or_requests_changes" in module.validate(job, tmp_path)["holds"]


def test_returned_lineage_must_include_the_exact_script_and_role_references(job, tmp_path):
    value = returned(job, tmp_path)
    manifest = module.read_json(tmp_path / "manifest.json")
    manifest["assets"][-1]["input_asset_ids"] = []
    value["runtime"]["output"]["manifest"] = put(tmp_path, "manifest.json", json.dumps(manifest))
    with pytest.raises(ValueError, match="lineage omits"):
        module.validate(value, tmp_path)


def test_workspace_escape_unknown_fields_and_later_shot_hold(job, tmp_path):
    job["route"]["api_key"] = "unaccepted-field"
    with pytest.raises(jsonschema.ValidationError):
        module.validate(job, tmp_path)
    del job["route"]["api_key"]
    job["purpose"] = "shot_rendition"
    assert "previous_rendition_review_missing_changed_or_requests_changes" in module.validate(job, tmp_path)["holds"]
    job["story"]["script"]["path"] = "../outside.txt"
    with pytest.raises(ValueError, match="within"):
        module.validate(job, tmp_path)
