"""The Snapshot step: code fetches a merged pull request from GitHub and starts its run record."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/launch-content/scripts"))

import snapshot  # noqa: E402

RUNS = ROOT / "tests/fixtures/sources"


def recorded_gh(example):
    """A stand-in for `gh api`, answering from the recorded GitHub replies of one example."""
    calls = []

    def gh(args):
        calls.append(args)
        folder = RUNS / example / "gh"
        if "Accept: application/vnd.github.diff" in args:
            return (folder / "pull.diff").read_text("utf-8")
        return (folder / "pull.json").read_text("utf-8")

    gh.calls = calls
    return gh


def test_the_snapshot_holds_the_title_body_and_diff_github_returned(tmp_path):
    folder = snapshot.fetch("example-org/harbor-reports", 3, tmp_path, gh=recorded_gh("csv-export"))
    text = (folder / "snapshot.md").read_text("utf-8")
    assert text.startswith("# Add CSV export\n")
    assert "Managers asked for a way to send the weekly report to their director" in text
    assert "Merged on 18 November 2026." in text
    assert "+def write_csv(report, path):" in text


def test_the_snapshot_starts_a_run_record_with_the_source_and_no_verdict(tmp_path):
    folder = snapshot.fetch("example-org/harbor-reports", 3, tmp_path, gh=recorded_gh("csv-export"))
    run = json.loads((folder / "run.json").read_text("utf-8"))
    assert folder.name == "pr-3"
    assert run["source"] == {
        "kind": "pull_request", "title": "Add CSV export",
        "link": "https://github.com/example-org/harbor-reports/pull/3", "author": "example-engineer",
        "received": "2026-11-18T13:02:00Z", "do_not_say": [], "open_questions": []}
    assert run["record_link"] == "https://github.com/example-org/harbor-reports/tree/launch-log/runs/pr-3"
    assert run["steps"]["snapshot"] == "done"
    assert "verdict" not in run["steps"]


def test_every_github_read_goes_through_gh_api(tmp_path):
    gh = recorded_gh("csv-export")
    snapshot.fetch("example-org/harbor-reports", 3, tmp_path, gh=gh)
    assert gh.calls and all(call[:2] == ["api", "repos/example-org/harbor-reports/pulls/3"] for call in gh.calls)


def test_a_pull_request_that_is_not_merged_gets_no_snapshot(tmp_path):
    def gh(args):
        return json.dumps({"number": 9, "title": "Open work", "body": "", "merged": False, "merged_at": None,
                           "html_url": "", "user": {"login": "x"}})

    with pytest.raises(snapshot.NotMerged):
        snapshot.fetch("example-org/harbor-reports", 9, tmp_path, gh=gh)
    assert not (tmp_path / "pr-9").exists()


def test_a_second_wake_leaves_an_existing_run_record_untouched(tmp_path):
    folder = snapshot.fetch("example-org/harbor-reports", 3, tmp_path, gh=recorded_gh("csv-export"))
    (folder / "run.json").write_text('{"kept": true}', "utf-8")
    again = snapshot.fetch("example-org/harbor-reports", 3, tmp_path, gh=recorded_gh("csv-export"))
    assert again == folder
    assert (folder / "run.json").read_text("utf-8") == '{"kept": true}'
