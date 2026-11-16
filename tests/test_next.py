"""next.py, the step runner: it owns the order of the gate loop, and the model answers only judgment steps.

Every test drives a run the way the cloud routine does. It asks next.py for the step, answers it from the
recorded model answers of one example, plays the Notion connector with a recorded stand-in, and repeats
until next.py prints done. No test calls a model or Notion.
"""

import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/launch-content"
sys.path.insert(0, str(SKILL / "scripts"))

import next as runner  # noqa: E402
import snapshot  # noqa: E402

RUNS = ROOT / "tests/fixtures/sources"
REPO = "example-org/harbor-reports"
NUMBERS = {"csv-export": 3, "totals-rounding": 4, "date-helpers-refactor": 5, "ignore-rules": 6}


class RecordedNotion:
    """Stands in for the Notion connector: the gates database by Key, and the comments on each page."""

    def __init__(self):
        self.pages, self.comments, self.creates = {}, [], 0

    def page(self, step):
        found = self.pages.get(step["key"])
        if found:
            return {"page_id": found["id"], "url": found["url"], "created": False}
        self.creates += 1
        page_id = f"page-{self.creates}"
        self.pages[step["key"]] = {"id": page_id, "url": f"https://notion.so/{page_id}", **step["page"]}
        return {"page_id": page_id, "url": f"https://notion.so/{page_id}", "created": True}

    def comment(self, step):
        comment_id = f"comment-{len(self.comments) + 1}"
        self.comments.append({"id": comment_id, "page_id": step["page_id"], "mention": step["mention"],
                              "markdown": step["markdown"]})
        return {"comment_id": comment_id}


def start(example, runs):
    def gh(args):
        folder = RUNS / example / "gh"
        return (folder / ("pull.diff" if "Accept: application/vnd.github.diff" in args else "pull.json")).read_text("utf-8")

    return snapshot.fetch(REPO, NUMBERS[example], runs, gh=gh)


def reply(step, example, notion):
    answers = RUNS / example / "answers"
    kind = step["step"]
    if kind == "verdict":
        return (answers / "verdict.txt").read_text("utf-8")
    if kind == "claims":
        return (answers / "claims.json").read_text("utf-8")
    if kind == "draft":
        return (answers / f"{step['gate']}.md").read_text("utf-8")
    if kind == "repair":
        return (answers / f"{step['gate']}.repair{step['repair']}.md").read_text("utf-8")
    if kind in ("push", "final_push"):
        return "pushed"
    if kind == "notion_page":
        return json.dumps(notion.page(step))
    if kind == "notion_comment":
        return json.dumps(notion.comment(step))
    raise AssertionError(f"unexpected step {kind}")


def drive(folder, example, notion, stop_at=None):
    """Answer steps until done or stopped, or until the step named stop_at is printed. Returns the steps."""
    steps = [runner.current(folder, SKILL)]
    while steps[-1]["step"] not in ("done", "stopped", stop_at):
        steps.append(runner.answer(folder, reply(steps[-1], example, notion), SKILL))
    return steps


def kinds(steps):
    return [s["step"] + (f":{s['gate']}" if "gate" in s else "") for s in steps]


def read_run(folder):
    return json.loads((folder / "run.json").read_text("utf-8"))


def test_the_csv_export_blog_gate_runs_end_to_end_to_one_drafted_page(tmp_path):
    notion = RecordedNotion()
    folder = start("csv-export", tmp_path)
    drive(folder, "csv-export", notion)
    page = notion.pages["pr-3/blog"]
    assert page["properties"]["Status"] == "Drafted"
    assert page["properties"]["Owner"] == "owner@example.com"
    assert page["properties"]["Round"] == 1
    assert page["properties"]["Check"] == "7 lines · 5 claims · 6/6 parts"
    assert page["content"].startswith("Door: two-way. Blast radius: One post page on the company's own site.\n")


def test_the_blog_page_gets_one_comment_that_mentions_its_owner(tmp_path):
    notion = RecordedNotion()
    drive(start("csv-export", tmp_path), "csv-export", notion)
    assert [(c["page_id"], c["mention"]) for c in notion.comments] == [("page-1", "owner@example.com")]
    assert "Content lead" in notion.comments[0]["markdown"]


def test_code_owns_the_order_of_steps(tmp_path):
    steps = drive(start("csv-export", tmp_path), "csv-export", RecordedNotion())
    assert kinds(steps) == ["verdict", "claims", "draft:blog", "push", "notion_page:blog", "notion_comment:blog",
                            "final_push", "done"]


def test_the_run_record_keeps_the_verdict_claims_and_an_untouched_baseline(tmp_path):
    folder = start("csv-export", tmp_path)
    drive(folder, "csv-export", RecordedNotion())
    run = read_run(folder)
    assert run["verdict"] == {"decision": "write", "tier": "launch", "rule": 5,
                              "quote": "The weekly report can now be saved as a CSV file",
                              "reason": "A new capability a user can name, a CSV download of the weekly report."}
    assert [c["id"] for c in run["claims"]] == ["c1", "c2", "c3", "c4", "c5"]
    blog = run["gates"]["blog"]
    baseline = folder / blog["rounds"][0]["baseline"]
    answered = (RUNS / "csv-export/answers/blog.md").read_bytes()
    assert baseline.name == "draft.agent.r1.md" and baseline.read_bytes() == answered
    assert blog["rounds"][0]["baseline_sha256"] == hashlib.sha256(answered).hexdigest()
    assert blog["rounds"][0]["check"] == {"ok": True, "lines": 7, "claims": 5, "parts": "6/6"}
    assert (blog["notion_page"], blog["notion_url"], blog["round"]) == ("page-1", "https://notion.so/page-1", 1)
