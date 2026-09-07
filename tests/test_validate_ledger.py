def _minimal_ledger(**overrides):
    base = {
        "campaign_id": "camp_demo_001",
        "allowed": [
            {"claim_id": "c1", "text": "FEATURE_NAME lets teams schedule posts"}
        ],
        "forbidden": [
            {"claim_id": "f1", "text": "unlimited seats for $0", "reason": "pricing invention"}
        ],
        "needs_disclaimer": [],
        "evidence": [
            {
                "claim_id": "c1",
                "source": "github_outline",
                "path": "sources/github_outline.md",
                "span_start": 0,
                "span_end": 42,
                "quote": "FEATURE_NAME lets teams schedule posts",
            }
        ],
        "kill_switch": {"armed": False, "reason": None},
    }
    base.update(overrides)
    return base


def test_validate_ledger_pass_when_every_allowed_has_evidence():
    from scripts.validate_ledger import validate_ledger

    result = validate_ledger(_minimal_ledger())
    assert result["ok"] is True
    assert result["kill_switch"]["armed"] is False


def test_validate_ledger_fails_without_evidence_span_and_arms_kill_switch():
    from scripts.validate_ledger import validate_ledger

    ledger = _minimal_ledger(evidence=[])
    result = validate_ledger(ledger)
    assert result["ok"] is False
    assert result["kill_switch"]["armed"] is True
    assert any("c1" in e for e in result["errors"])


def test_validate_ledger_fails_on_forbidden_text_in_allowed():
    from scripts.validate_ledger import validate_ledger

    ledger = _minimal_ledger(
        allowed=[
            {"claim_id": "c1", "text": "FEATURE_NAME"},
            {"claim_id": "bad", "text": "unlimited seats for $0"},
        ],
        evidence=[
            {
                "claim_id": "c1",
                "source": "github_outline",
                "path": "sources/github_outline.md",
                "span_start": 0,
                "span_end": 12,
                "quote": "FEATURE_NAME",
            },
            {
                "claim_id": "bad",
                "source": "github_outline",
                "path": "sources/github_outline.md",
                "span_start": 0,
                "span_end": 5,
                "quote": "nope",
            },
        ],
    )
    result = validate_ledger(ledger)
    assert result["ok"] is False
    assert result["kill_switch"]["armed"] is True
    assert any("forbidden" in e.lower() for e in result["errors"])


def test_fixture_ledger_validates(work_root):
    from scripts.validate_ledger import validate_ledger
    import json

    path = work_root / "fixtures/demo-release/claim_ledger.json"
    ledger = json.loads(path.read_text(encoding="utf-8"))
    result = validate_ledger(ledger)
    assert result["ok"] is True
