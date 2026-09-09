import json
import pytest


def _load(record_path):
    return json.loads(record_path.read_text(encoding="utf-8"))


@pytest.fixture
def fresh_record(work_root, tmp_path):
    from scripts.init_release import init_release

    folder = work_root / "fixtures/demo-release"
    rec = init_release(folder, tmp_path / "ws")
    return rec


def test_init_release_creates_record_with_hashes(fresh_record):
    record = _load(fresh_record)
    assert record["record_id"] == "rec_demo-release"
    assert record["schema_version"] == "release-record/v1"
    files = {f["path"]: f for f in record["release_folder"]["files"]}
    assert "claim_ledger.json" in files
    assert len(files["claim_ledger.json"]["sha256"]) == 64
    # seven slots, held-by-default spine slots named
    assert len(record["slots"]) == 7
    assert record["slots"][6]["name"] == "campaign_plan"
    assert record["claims_lock"]["state"] == "drafted"


def test_init_release_refuses_to_overwrite(fresh_record):
    from pathlib import Path

    from scripts.init_release import init_release

    record = _load(fresh_record)
    folder = Path(record["release_folder"]["path"])

    with pytest.raises(SystemExit) as exc:
        init_release(folder, fresh_record.parent)
    assert "refusing to overwrite" in str(exc.value)


def test_fixture_example_record_validates(work_root):
    from scripts.validate_record import validate_record

    record = _load(work_root / "fixtures/demo-release/release-record.json")
    result = validate_record(record)
    assert result["ok"] is True, result["errors"]


def test_validate_record_blocks_self_approved_slot(fresh_record):
    from scripts.validate_record import validate_record

    record = _load(fresh_record)
    record["slots"][1]["state"] = "approved"  # writer moved itself — no Reviewer gate
    result = validate_record(record)
    assert result["ok"] is False
    assert any("authority" in e and "slot 2" in e for e in result["errors"])


def test_validate_record_blocks_fake_claims_lock(fresh_record):
    from scripts.validate_record import validate_record

    record = _load(fresh_record)
    record["claims_lock"] = {"state": "locked_by_reviewer", "locked_at": None}
    result = validate_record(record)
    assert result["ok"] is False
    assert any("claims_lock" in e for e in result["errors"])


def test_transition_slot_permitted_and_refused(fresh_record):
    from scripts.transition_slot import transition_slot

    record = _load(fresh_record)
    # held -> drafted (un-hold slot 2)
    record = transition_slot(record, "2", "drafted")
    assert record["slots"][1]["state"] == "drafted"
    # drafted -> reviewed
    record = transition_slot(record, "blog", "reviewed")
    assert record["slots"][1]["state"] == "reviewed"
    # reviewed -> approved WITHOUT --human-confirmed must be refused
    with pytest.raises(SystemExit) as exc:
        transition_slot(record, "2", "approved", human_confirmed=False)
    assert "human-confirmed" in str(exc.value)
    # an illegal transition must be refused
    with pytest.raises(SystemExit) as exc:
        transition_slot(record, "2", "packaged", human_confirmed=True)
    assert "not permitted" in str(exc.value)


def test_transition_slot_human_confirmed_records_reviewer_gate(fresh_record):
    from scripts.transition_slot import transition_slot
    from scripts.validate_record import validate_record

    record = _load(fresh_record)
    record = transition_slot(record, "2", "drafted")
    record = transition_slot(record, "2", "reviewed")
    record = transition_slot(record, "2", "approved", human_confirmed=True)
    assert record["slots"][1]["state"] == "approved"
    reviewer_gates = [
        g for g in record["gates"]
        if g["gate"] == "slot-2" and g["decided_by"] == "reviewer" and g["decision"] == "approve"
    ]
    assert len(reviewer_gates) == 1
    # now the authority gate passes because Reviewer's decision is recorded
    result = validate_record(record)
    assert result["ok"] is True, result["errors"]


def test_transition_slot_hold_requires_reason(fresh_record):
    from scripts.transition_slot import transition_slot

    record = _load(fresh_record)
    record = transition_slot(record, "2", "drafted")
    with pytest.raises(SystemExit) as exc:
        transition_slot(record, "2", "held")
    assert "--reason" in str(exc.value)
    record = transition_slot(record, "2", "held", reason="claim missing — hold")
    assert record["slots"][1]["hold_reason"] == "claim missing — hold"
