"""The Check, driven as a command: a run record and a gate in, an exit code and a message out."""

import json
import shutil
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


def test_naming_a_gate_counts_claims_cited_only_by_another_gate():
    result = check("good-pr", "test-card")
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == ["test-card: 2 lines, 2 claims, 2/2 parts", "run pr-csv: 3 claims verified"]


def test_skip_and_ask_open_no_gate_and_pass():
    for record, run_id in (("skip", "pr-refactor"), ("ask", "brief-dashboards")):
        result = check(record)
        assert result.returncode == 0, result.stderr
        assert result.stdout.splitlines() == [f"run {run_id}: 0 claims verified"]


BAD = [
    ("quote-changed", None, 'claim c2: quote not found in the Snapshot: "The export keeps the filters the user chose."'),
    ("line-no-claim", "test-post", 'test-post line 7 cites no claim: "it is the fastest export on the market"'),
    ("claim-unused", None, "claim c4 is cited by no opened gate"),
    ("write-zero-claims", None, "verdict write has zero claims"),
    ("write-zero-claims", "test-post", "test-post line 5 cites unknown claim c1"),
    ("missing-field", None, "run.json is missing source.kind"),
    ("do-not-say", None, "test-post line 5 contains the Do not say phrase \"export   MENU\""),
    ("missing-part", "test-post", "test-post is missing the part proof"),
    ("too-short", "test-post", "test-post has 3 lines, below the minimum of 4"),
    ("too-long", "test-post", "test-post has 9 lines, above the maximum of 8"),
    ("too-long", "test-post", "test-post has 137 words, above the maximum of 120"),
    ("too-long", "test-card", "test-card has 416 chars, above the maximum of 280"),
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
    ("claim-unused", "test-post", "claim c4 is cited by no opened gate"),
    ("quote-empty", None, 'claim c2: quote "   " is shorter than 3 words'),
    ("line-only-citation", "test-card", "test-card line 2 has no words"),
    ("do-not-say-split", None, "test-post lines 5 to 6 contain the Do not say phrase \"export   MENU\""),
    ("do-not-say-split", None, "test-post lines 5 to 6 contain the Do not say phrase \"the export menu\""),
    ("number-sign", "test-post", "test-post line 9: number -10 is not in its cited claims c3"),
    ("draft-missing", None, "gate test-card has no draft.md"),
    ("gate-name", None, "gate name \"../x\" is not a plain name"),
    ("good-pr", "../x", "gate name \"../x\" is not a plain name"),
    ("missing-gates", None, "run.json is missing gates"),
]


@pytest.mark.parametrize("record, gate, message", BAD, ids=[row[0] for row in BAD])
def test_bad_record_fails_naming_the_problem(record, gate, message):
    result = check(record, gate)
    assert result.returncode == 1
    assert f"FAIL {message}" in result.stderr.splitlines()
    assert result.stdout == ""


def test_do_not_say_on_one_line_is_reported_once():
    result = check("do-not-say")
    assert result.stderr.splitlines() == ['FAIL test-post line 5 contains the Do not say phrase "export   MENU"']


GOOD_CARD = "<!-- part: problem -->\n{problem}\n<!-- part: change -->\nEvery report exports as CSV, up to 50000 rows in under 10 seconds. [c1, c3]\n"


def variant(tmp_path, card=None, post=None, quotes=None, do_not_say=None):
    """A copy of good-pr with one change, so each case shows the one input that must fail."""
    folder = tmp_path / "run"
    shutil.copytree(FIXTURES / "records/good-pr", folder)
    if card is not None:
        (folder / "gates/test-card/draft.md").write_bytes(GOOD_CARD.format(problem=card).encode("utf-8"))
    if post:
        path = folder / "gates/test-post/draft.md"
        old, new = post
        text = path.read_bytes().decode("utf-8")
        assert old in text
        path.write_bytes(text.replace(old, new).encode("utf-8"))
    run = json.loads((folder / "run.json").read_text("utf-8"))
    for claim in run["claims"]:
        claim["quote"] = (quotes or {}).get(claim["id"], claim["quote"])
    if do_not_say is not None:
        run["source"]["do_not_say"] = do_not_say
    (folder / "run.json").write_text(json.dumps(run, ensure_ascii=False), "utf-8")
    return folder


def run_check(folder, gate=None):
    args = [sys.executable, str(CHECK), str(folder), *([gate] if gate else []), "--skill", str(FIXTURES / "skill")]
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8")


def test_a_variant_with_no_change_passes(tmp_path):
    result = run_check(variant(tmp_path))
    assert result.returncode == 0, result.stderr


WORDLESS = {
    "two-citations": "[c1] [c1]",
    "adjacent-citations": "[c1][c3]",
    "dash": "- [c1]",
    "dot": ". [c1]",
    "zero-width-space": "\u200b [c1]",
    "html-comment": "<!-- x --> [c1]",
    "emphasis-only": "** __ [c1]",
}


@pytest.mark.parametrize("problem", WORDLESS.values(), ids=WORDLESS.keys())
def test_a_line_with_no_words_fails(tmp_path, problem):
    result = run_check(variant(tmp_path, card=problem))
    assert result.returncode == 1
    assert "FAIL test-card line 2 has no words" in result.stderr.splitlines()


SHORT_QUOTES = {"one-char": "e", "dot": ".", "two-words": "user picked", "symbols": "** -- !!"}


@pytest.mark.parametrize("quote", SHORT_QUOTES.values(), ids=SHORT_QUOTES.keys())
def test_a_quote_shorter_than_three_words_fails_naming_the_claim(tmp_path, quote):
    result = run_check(variant(tmp_path, quotes={"c2": quote}))
    assert result.returncode == 1
    assert f'FAIL claim c2: quote "{quote}" is shorter than 3 words' in result.stderr.splitlines()


def test_a_quote_must_match_whole_snapshot_words(tmp_path):
    result = run_check(variant(tmp_path, quotes={"c2": "xport keeps the filters"}))
    assert 'FAIL claim c2: quote not found in the Snapshot: "xport keeps the filters"' in result.stderr.splitlines()


def test_a_quote_matches_across_snapshot_markup_case_and_line_breaks(tmp_path):
    result = run_check(variant(tmp_path, quotes={"c3": "*exports* UP to 50000 rows finish in under 10 seconds in our TESTS"}))
    assert result.returncode == 0, result.stderr


def test_a_unicode_minus_is_a_sign(tmp_path):
    result = run_check(variant(tmp_path, post=("under 10 seconds", "under \u221210 seconds")), "test-post")
    assert "FAIL test-post line 9: number -10 is not in its cited claims c3" in result.stderr.splitlines()


def test_a_number_glued_to_a_word_is_still_checked(tmp_path):
    result = run_check(variant(tmp_path, post=("50000 rows", "50001rows")), "test-post")
    assert "FAIL test-post line 9: number 50001 is not in its cited claims c3" in result.stderr.splitlines()


HIDDEN = {
    "emphasis": "at the beta **price**.",
    "hyphen": "at the beta-price.",
    "zero-width-space": "at the beta\u200bprice.",
    "html-comment": "at the beta <!-- x --> price.",
}


@pytest.mark.parametrize("hidden", HIDDEN.values(), ids=HIDDEN.keys())
def test_markup_does_not_hide_a_do_not_say_phrase(tmp_path, hidden):
    result = run_check(variant(tmp_path, post=("filters you picked.", f"filters you picked {hidden}")))
    assert 'FAIL test-post line 6 contains the Do not say phrase "beta price"' in result.stderr.splitlines()


def test_a_do_not_say_phrase_with_no_words_fails(tmp_path):
    result = run_check(variant(tmp_path, do_not_say=["   "]))
    assert result.stderr.splitlines() == ['FAIL Do not say phrase "   " has no words']


def test_a_gate_name_with_a_plain_prefix_is_still_rejected():
    result = check("good-pr", "test-card/../x")
    assert result.returncode == 1
    assert 'FAIL gate name "test-card/../x" is not a plain name' in result.stderr.splitlines()


def test_a_missing_snapshot_fails_with_a_fail_line(tmp_path):
    folder = variant(tmp_path)
    (folder / "snapshot.md").unlink()
    result = run_check(folder)
    assert result.returncode == 1
    assert result.stderr.splitlines() == ["FAIL run pr-csv has no snapshot.md"]


@pytest.mark.parametrize("content", ["{not json", ""], ids=["broken", "empty"])
def test_an_invalid_run_json_fails_with_a_fail_line(tmp_path, content):
    folder = variant(tmp_path)
    (folder / "run.json").write_text(content, "utf-8")
    result = run_check(folder)
    assert result.returncode == 1
    assert result.stderr.splitlines() == ["FAIL run.json is not valid JSON"]


def test_a_missing_run_json_fails_with_a_fail_line(tmp_path):
    result = run_check(tmp_path)
    assert result.returncode == 1
    assert result.stderr.splitlines() == ["FAIL the run folder has no run.json"]


@pytest.mark.parametrize("contract", ["# Test card\n\nNo block here.\n", "```json\n{broken\n```\n"], ids=["no-block", "bad-json"])
def test_a_contract_with_no_json_block_fails_with_a_fail_line(tmp_path, contract):
    skill = tmp_path / "skill"
    shutil.copytree(FIXTURES / "skill", skill)
    (skill / "gates/test-card.md").write_text(contract, "utf-8")
    args = [sys.executable, str(CHECK), str(FIXTURES / "records/good-pr"), "test-card", "--skill", str(skill)]
    result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 1
    assert result.stderr.splitlines() == ["FAIL contract gates/test-card.md has no valid JSON block"]
