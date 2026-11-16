"""The Check, driven as a command: a run record and a gate in, an exit code and a message out."""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "skills/launch-content/scripts/check.py"
FIXTURES = ROOT / "tests/fixtures/check"


def check(record, gate=None):
    args = [sys.executable, str(CHECK), str(FIXTURES / "records" / record)]
    if gate:
        args.append(gate)
    args += ["--skill", str(FIXTURES / "skill")]
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8")


def test_windows_line_endings_pass():
    assert b"\r\n" in (FIXTURES / "records/crlf/snapshot.md").read_bytes(), "git converted the fixture"
    result = check("crlf", "test-post")
    assert result.returncode == 0, result.stderr
    assert "test-post: 4 lines, 3 claims, 3/3 parts" in result.stdout


def test_good_records_pass_and_print_counts():
    result = check("good-pr")
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        "test-post: 4 lines, 3 claims, 3/3 parts",
        "test-card: 2 lines, 2 claims, 2/2 parts",
        "run pr-csv: 3 claims verified",
    ]
    result = check("good-briefing", "test-card")
    assert result.returncode == 0, result.stderr
    assert "test-card: 2 lines, 3 claims, 2/2 parts" in result.stdout


def test_skip_and_ask_open_no_gate_and_pass():
    for record, run_id in (("skip", "pr-refactor"), ("ask", "brief-dashboards")):
        result = check(record)
        assert result.returncode == 0, result.stderr
        assert result.stdout.splitlines() == [f"run {run_id}: 0 claims verified"]


BAD = [
    ("quote-changed", None, 'claim c2: quote not found in the Snapshot: "The export keeps the filters the user chose."'),
    ("line-no-claim", "test-post", 'test-post line 7 cites no claim: "It is the fastest export on the market."'),
    ("claim-unused", None, "claim c4 is cited by no opened gate"),
    ("write-zero-claims", None, "verdict write has zero claims"),
    ("write-zero-claims", "test-post", "test-post line 5 cites unknown claim c1"),
    ("missing-field", None, "run.json is missing source.kind"),
    ("do-not-say", None, "test-post line 5 contains the Do not say phrase \"export   MENU\""),
    ("missing-part", "test-post", "test-post is missing the part proof"),
    ("too-short", "test-post", "test-post has 3 lines, below the minimum of 4"),
    ("too-long", "test-post", "test-post has 9 lines, above the maximum of 8"),
    ("too-long", "test-post", "test-post has 137 words, above the maximum of 120"),
    ("too-long", "test-card", "test-card has 423 chars, above the maximum of 280"),
    ("unknown-gate", None, "unknown gate test-video: no contract gates/test-video.md"),
    ("skip", "test-post", "gate test-post is not opened by run pr-refactor"),
    ("number-differs", "test-card", "test-card line 4: number 5000 is not in its cited claims c1, c3"),
    ("draft-zero-lines", "test-card", "test-card has zero lines"),
    ("draft-zero-claims", "test-post", "test-post cites zero claims"),
    ("ask-no-questions", None, "verdict ask lists no open questions"),
    ("skip-opens-gate", None, "verdict skip opens gate test-card"),
    ("ask-opens-gate", None, "verdict ask opens gate test-card"),
    ("unknown-values", None, "verdict.decision is \"publish\", expected one of ask, skip, write"),
    ("unknown-values", None, "source.kind is \"email\", expected one of briefing, pull_request"),
    ("number-uncited", "test-card", "test-card line 4: number 50000 is not in its cited claims c1"),
]


@pytest.mark.parametrize("record, gate, message", BAD, ids=[row[0] for row in BAD])
def test_bad_record_fails_naming_the_problem(record, gate, message):
    result = check(record, gate)
    assert result.returncode == 1
    assert f"FAIL {message}" in result.stderr.splitlines()
    assert result.stdout == ""
