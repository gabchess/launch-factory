"""Seam 3, the gate page renderer: a run and a gate in, the Notion page payload out."""

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/launch-content"
sys.path.insert(0, str(SKILL / "scripts"))

import render_page  # noqa: E402

PAGES = ROOT / "tests/fixtures/pages"
STATUSES = ("Drafted", "Needs changes", "Ready to post", "Posted", "Rejected")

BLOG_BODY = """Door: two-way. Blast radius: One post page on the company's own site.

| Draft line | Claims and quotes |
| --- | --- |
| # Send the weekly report as a CSV file | No claim needed |
| Managers asked for a way to send the weekly report to their director or load it into a spreadsheet. | c1: "Managers asked for a way to send the weekly report to their director or load it into a spreadsheet." |
| The weekly report can now be saved as a CSV file. | c2: "The weekly report can now be saved as a CSV file with one row per stage and a total row at the end." |
| The file has one row per stage and a total row at the end. | c2: "The weekly report can now be saved as a CSV file with one row per stage and a total row at the end." |
| The file has the columns stage and deals, then a total row with the pipeline total. | c3: "The file has the columns stage and deals, then a total row with the pipeline total." |
| The download covers the weekly report only. | c4: "Adds a CSV download of the weekly report." |
| Open your weekly report and save it as a CSV file, released on 18 November 2026. | c2: "The weekly report can now be saved as a CSV file with one row per stage and a total row at the end."<br />c5: "Merged on 18 November 2026." |
"""


def test_the_blog_page_opens_with_its_door_line_then_each_draft_line_beside_its_quotes():
    page = render_page.render(PAGES / "pr-3", "blog", SKILL)
    assert page["content"] == BLOG_BODY


def test_the_blog_page_properties_name_the_key_owner_round_and_check_stamp():
    page = render_page.render(PAGES / "pr-3", "blog", SKILL)
    assert page["key"] == "pr-3/blog"
    assert page["properties"] == {
        "Name": "Add CSV export · blog", "Key": "pr-3/blog", "Gate": "blog", "Status": "Drafted",
        "Owner": "owner@example.com", "Owner sources": "", "Round": 1,
        "Check": "7 lines · 5 claims · 6/6 parts",
        "Run": "https://github.com/example-org/harbor-reports/tree/launch-log/runs/pr-3"}


def test_the_changelog_page_uses_its_own_contract_door_and_heading_rule():
    page = render_page.render(PAGES / "pr-3", "changelog", SKILL)
    lines = page["content"].splitlines()
    assert lines[0] == "Door: two-way. Blast radius: One entry on the /changelog/ page."
    assert lines[4] == "| # CSV export for the weekly report | No claim needed |"
    assert page["properties"]["Check"] == "4 lines · 4 claims · 4/4 parts"


@pytest.mark.parametrize("gate", ["blog", "changelog"])
def test_the_renderer_only_ever_outputs_the_status_drafted(gate):
    page = render_page.render(PAGES / "pr-3", gate, SKILL)
    assert page["properties"]["Status"] == "Drafted"
    others = [s for s in STATUSES if s != "Drafted"]
    assert not [s for s in others if s in json.dumps(page)]


def test_the_renderer_ignores_a_status_planted_in_the_run_record(tmp_path):
    folder = tmp_path / "pr-3"
    subprocess.run([sys.executable, "-c", "import shutil,sys; shutil.copytree(sys.argv[1], sys.argv[2])",
                    str(PAGES / "pr-3"), str(folder)], check=True)
    run = json.loads((folder / "run.json").read_text("utf-8"))
    run["gates"]["blog"]["status"] = "Ready to post"
    (folder / "run.json").write_text(json.dumps(run), "utf-8")
    assert render_page.render(folder, "blog", SKILL)["properties"]["Status"] == "Drafted"


@pytest.mark.parametrize("status", [s for s in STATUSES if s != "Drafted"] + ["drafted", "", None])
def test_the_notion_writer_refuses_every_status_but_drafted(status):
    page = copy.deepcopy(render_page.render(PAGES / "pr-3", "blog", SKILL))
    page["properties"]["Status"] = status
    with pytest.raises(render_page.NotionRefused):
        render_page.notion_write(page)


def test_the_notion_writer_refuses_a_page_with_no_status():
    page = copy.deepcopy(render_page.render(PAGES / "pr-3", "blog", SKILL))
    del page["properties"]["Status"]
    with pytest.raises(render_page.NotionRefused):
        render_page.notion_write(page)


def test_the_notion_writer_passes_a_drafted_page_through_unchanged():
    page = render_page.render(PAGES / "pr-3", "blog", SKILL)
    assert render_page.notion_write(page) == page


def test_the_blog_page_creates_eleven_blocks():
    page = render_page.render(PAGES / "pr-3", "blog", SKILL)
    # The page, the door line, the table, its header row and its 7 Draft rows.
    assert render_page.blocks(page) == 11


def test_the_command_prints_the_page_payload():
    result = subprocess.run([sys.executable, "-I", str(SKILL / "scripts/render_page.py"), str(PAGES / "pr-3"), "blog"],
                            capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["key"] == "pr-3/blog"


def test_the_round_property_is_the_round_the_run_record_holds(tmp_path):
    folder = tmp_path / "pr-3"
    subprocess.run([sys.executable, "-c", "import shutil,sys; shutil.copytree(sys.argv[1], sys.argv[2])",
                    str(PAGES / "pr-3"), str(folder)], check=True)
    run = json.loads((folder / "run.json").read_text("utf-8"))
    run["gates"]["blog"]["round"] = 2
    (folder / "run.json").write_text(json.dumps(run), "utf-8")
    assert render_page.render(folder, "blog", SKILL)["properties"]["Round"] == 2
