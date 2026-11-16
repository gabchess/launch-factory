"""The site builder, driven as a command: run records and Notion page states in, a static site out."""

import json
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "skills/launch-content/scripts/build_site.py"
FIXTURES = ROOT / "tests/fixtures/site"


def build(out, notion=None, runs=None, owners=None, skill=None):
    args = [sys.executable, str(BUILD), str(runs or FIXTURES / "records"),
            "--notion", str(notion or FIXTURES / "notion.json"),
            "--owners", str(owners or FIXTURES / "owners.json"),
            "--skill", str(skill or FIXTURES / "skill"),
            "--out", str(out)]
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8")


VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Keyed(HTMLParser):
    """Collects the visible text of every element that carries data-key, and the text of the whole page."""

    def __init__(self):
        super().__init__()
        self.open, self.text, self.classes, self.page = [], {}, {}, []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in VOID:
            self.handle_data(" ")
            return
        if "data-key" in attrs:
            self.open.append([attrs["data-key"], 0])
            self.text[attrs["data-key"]] = ""
            self.classes[attrs["data-key"]] = attrs.get("class", "")
        elif self.open:
            self.open[-1][1] += 1
        if tag in ("p", "li", "span", "div", "h1", "h2", "a", "b"):
            self.handle_data(" ")

    def handle_endtag(self, tag):
        if self.open:
            if self.open[-1][1]:
                self.open[-1][1] -= 1
            else:
                self.open.pop()

    def handle_data(self, data):
        self.page.append(data)
        for key, _ in self.open:
            self.text[key] += data


def squash(text):
    return re.sub(r"\s+", " ", text).strip()


def parse(path):
    parser = Keyed()
    parser.feed(path.read_text(encoding="utf-8"))
    return {k: squash(v) for k, v in parser.text.items()}, parser.classes, squash("".join(parser.page))


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    out = tmp_path_factory.mktemp("site")
    result = build(out)
    assert result.returncode == 0, result.stderr
    return out


@pytest.fixture(scope="module")
def board(site):
    return parse(site / "index.html")


def test_board_is_a_grid_of_sources_by_the_four_gates(board):
    text, classes, page = board
    heads = [text[f"head/{g}"] for g in ("blog", "changelog", "social", "faq")]
    assert [h.split(" Sandbox owner")[0] for h in heads] == ["Blog post", "Changelog", "Social post", "FAQ update"]
    assert all("Sandbox owner" in h for h in heads)
    rows = [k for k in text if k.startswith("row/")]
    assert rows == ["row/pr-csv", "row/brief-seats", "row/pr-rounding", "row/pr-pdf", "row/brief-dashboards", "row/pr-refactor"]
    assert [k for k in text if k.startswith("cell/pr-csv/")] == [f"cell/pr-csv/{g}" for g in ("blog", "changelog", "social", "faq")]
    assert "Thu 14:06" in text["row/pr-csv"]


def test_the_shipped_owners_and_gate_contracts_build_a_board_with_owner_names(tmp_path):
    shipped = ROOT / "skills/launch-content"
    result = build(tmp_path, owners=shipped / "owners.json", skill=shipped)
    assert result.returncode == 0, result.stderr
    text, _, _ = parse(tmp_path / "index.html")
    assert "Content lead" in text["head/blog"]
    assert text["head/blog"].endswith("· Content lead")
    assert "Support lead" in text["head/faq"]


def test_board_keeps_the_desk_log_look(site):
    design_tokens = ["--paper: #E9F0E0", "--slip: #FFFDF2", "Courier Prime", ".stamp.review", ".stamp.ask"]
    built = (site / "index.html").read_text(encoding="utf-8")
    assert all(token in built for token in design_tokens)


def test_each_cell_status_comes_from_notion_and_never_from_the_run_record(board):
    text, _, _ = board
    assert "READY TO POST" in text["cell/pr-csv/blog"]
    assert "POSTED" in text["cell/pr-csv/changelog"]
    assert "READY TO POST" in text["cell/pr-csv/social"]
    assert "DRAFTED" in text["cell/brief-seats/blog"]
    assert "NEEDS CHANGES" in text["cell/brief-seats/changelog"]
    assert "REJECTED" in text["cell/pr-pdf/changelog"]
    assert "DRAFTED" not in text["cell/pr-csv/social"]
    assert "REJECTED" not in text["cell/pr-csv/blog"]


def test_an_unknown_notion_status_fails_the_build(tmp_path):
    notion = json.loads((FIXTURES / "notion.json").read_text(encoding="utf-8"))
    notion["pr-csv/blog"]["status"] = "Approved"
    (tmp_path / "notion.json").write_text(json.dumps(notion), encoding="utf-8")
    result = build(tmp_path / "out", notion=tmp_path / "notion.json")
    assert result.returncode == 1
    assert 'pr-csv/blog has the Notion Status "Approved"' in result.stderr


def test_a_cell_shows_counts_round_owner_and_status_and_no_percentage(board):
    text, _, _ = board
    cell = text["cell/pr-csv/blog"]
    assert "4 lines · 3 claims · 2/2 parts" in cell
    assert "round 2" in cell
    assert "Sandbox owner" in cell
    assert "1 line · 2 claims · 1/1 parts" in text["cell/pr-csv/social"]
    assert all("%" not in value for key, value in text.items() if key.startswith("cell/"))


def test_a_gate_with_no_page_and_a_failed_check_is_held_by_the_check(board):
    text, _, _ = board
    cell = text["cell/pr-rounding/changelog"]
    assert "HELD BY THE CHECK" in cell
    assert 'changelog line 3 cites no claim: "it is the best report on the market"' in cell
    assert "DRAFTED" not in cell


def test_a_failed_check_holds_the_gate_even_when_notion_says_ready_to_post(tmp_path):
    notion = json.loads((FIXTURES / "notion.json").read_text(encoding="utf-8"))
    notion["pr-rounding/changelog"] = {"status": "Ready to post", "round": 1, "url": "https://www.notion.so/example"}
    (tmp_path / "notion.json").write_text(json.dumps(notion), encoding="utf-8")
    result = build(tmp_path / "out", notion=tmp_path / "notion.json")
    assert result.returncode == 0, result.stderr
    text, _, _ = parse(tmp_path / "out/index.html")
    assert "HELD BY THE CHECK" in text["cell/pr-rounding/changelog"]
    changelog = (tmp_path / "out/changelog/index.html").read_text(encoding="utf-8")
    assert "pipeline report" not in changelog


def test_a_gate_the_verdict_did_not_open_is_an_empty_cell(board):
    text, classes, _ = board
    assert text["cell/pr-rounding/blog"] == ""
    assert "is-empty" in classes["cell/pr-rounding/blog"]


def test_ask_and_skip_rows_span_the_gates_with_their_reason(board):
    text, classes, _ = board
    ask = text["row/brief-dashboards"]
    assert "ASK" in ask and "2 questions for product" in ask
    assert "Which plans get the faster dashboards?" in ask
    assert "Is the old dashboard still available?" in ask
    assert "is-ask" in classes["row/brief-dashboards"]
    skip = text["row/pr-refactor"]
    assert "SKIP" in skip and "Not user facing" in skip
    assert "is-quiet" in classes["row/pr-refactor"]
    assert not [k for k in text if k.startswith(("cell/brief-dashboards/", "cell/pr-refactor/"))]


def test_board_shows_the_mode_line_and_the_sandbox_line(board):
    _, _, page = board
    assert "Mode: Suggest · Autonomous locked" in page
    assert "In this sandbox one person plays every owner." in page


def test_the_three_roadmap_columns_are_greyed_with_owner_role_and_one_file(board):
    text, classes, _ = board
    nexts = [k for k in text if k.startswith("next/")]
    assert nexts == ["next/customer-email", "next/video-script", "next/site-animation"]
    for key in nexts:
        assert "adds one file" in text[key].lower()
        assert "Owner:" in text[key]
    assert "Customer email" in text["next/customer-email"]
    assert classes["next"].split() == ["next"], "the roadmap sits in the dashed grey Next block"
    assert all(text[key] in text["next"] for key in nexts)


def test_the_headline_counts_the_week(board):
    _, _, page = board
    assert "68s" in page.replace(" ", "")
    assert "6 arrived" in page and "4 drafted · 1 asked · 1 skipped" in page


def test_the_open_slip_sends_the_reader_to_notion_and_makes_no_undo_claim(board):
    _, _, page = board
    assert "Review in Notion" in page
    assert "cannot be undone" not in page


def test_a_blog_page_shows_each_line_next_to_its_quote(site):
    text, _, page = parse(site / "blog/pr-csv/index.html")
    html = (site / "blog/pr-csv/index.html").read_text(encoding="utf-8")
    assert "<h1>CSV export for every report</h1>" in html
    for sentence, claim, quote in [
        ("Any report now exports as CSV from the Export menu.", "c1", "Any report now exports as CSV from the Export menu."),
        ("The export keeps the filters you picked.", "c2", "The export keeps the filters the user picked."),
        ("In our tests, exports of up to 50000 rows finished in under 10 seconds.", "c3",
         "Exports up to 50000 rows finish in under 10 seconds in our tests."),
    ]:
        assert re.search(re.escape(sentence) + rf'<a class="ref" href="#{claim}"', html), sentence
        assert f'"{quote}"' in text[f"quote/{claim}"]
    assert "Ready to post" in page and "approved by Sandbox owner" in page


def test_an_owner_claim_names_the_owner_sources_on_the_blog_page_and_the_slip(tmp_path):
    runs = tmp_path / "records"
    shutil.copytree(FIXTURES / "records", runs)
    record = json.loads((runs / "pr-csv/run.json").read_text(encoding="utf-8"))
    record["claims"].append({"id": "c4", "gate": "blog", "quote": "CSV export ships to every plan this week."})
    record["gates"]["blog"]["owner_sources"] = "CSV export ships to every plan this week."
    (runs / "pr-csv/run.json").write_text(json.dumps(record), encoding="utf-8")
    with (runs / "pr-csv/gates/blog/draft.md").open("a", encoding="utf-8") as draft:
        draft.write("CSV export ships to every plan this week. [c4]\n")
    assert build(tmp_path / "out", runs=runs).returncode == 0
    page = (tmp_path / "out/blog/pr-csv/index.html").read_text(encoding="utf-8")
    assert re.search(r'id="c4".*?<p class="src-where">Owner sources</p>', page, re.S)
    notion = json.loads((FIXTURES / "notion.json").read_text(encoding="utf-8"))
    notion["pr-csv/blog"]["status"] = "Drafted"
    (tmp_path / "notion.json").write_text(json.dumps(notion), encoding="utf-8")
    assert build(tmp_path / "board", notion=tmp_path / "notion.json", runs=runs).returncode == 0
    slip = (tmp_path / "board/index.html").read_text(encoding="utf-8")
    assert 'every plan this week."</p><p class="line-where">Owner sources</p>' in slip


def test_only_a_ready_to_post_or_posted_blog_gate_gets_a_page(site):
    assert (site / "blog/pr-csv/index.html").is_file()
    assert not (site / "blog/brief-seats").exists(), "a Drafted gate is not published"


def test_the_changelog_lists_published_entries_newest_first(tmp_path):
    notion = json.loads((FIXTURES / "notion.json").read_text(encoding="utf-8"))
    notion["brief-seats/changelog"]["status"] = "Posted"
    (tmp_path / "notion.json").write_text(json.dumps(notion), encoding="utf-8")
    assert build(tmp_path / "out", notion=tmp_path / "notion.json").returncode == 0
    text, _, _ = parse(tmp_path / "out/changelog/index.html")
    assert [k for k in text if k.startswith("changelog/")] == ["changelog/pr-csv", "changelog/brief-seats"]
    assert "Reports export as CSV from the Export menu." in text["changelog/pr-csv"]
    assert "Managers can invite each rep to a team seat." in text["changelog/brief-seats"]
    assert "PDF" not in "".join(text.values()), "a Rejected gate is not published"


def test_the_faq_lists_each_question_with_its_answer(site):
    text, _, _ = parse(site / "faq/index.html")
    assert text["faq/pr-csv/1"] == "Can I export a report as CSV? Yes, from the Export menu on any report. 1"
    assert text["faq/pr-csv/2"] == "Does the export keep my filters? Yes, the export keeps the filters you picked. 2"


def test_a_social_card_has_its_text_and_a_copy_button(site):
    html = (site / "social/index.html").read_text(encoding="utf-8")
    text, _, _ = parse(site / "social/index.html")
    assert "Every report now exports as CSV, up to 50000 rows in under 10 seconds." in text["social/pr-csv"]
    assert re.search(r'<button class="copy" type="button" data-copy="social-pr-csv">Copy</button>', html)
    assert 'id="social-pr-csv"' in html and "navigator.clipboard.writeText" in html
    assert "social/brief-seats" not in text, "a Drafted gate is not published"


def test_a_passing_gate_with_no_notion_page_is_not_shown_as_drafted(tmp_path):
    notion = json.loads((FIXTURES / "notion.json").read_text(encoding="utf-8"))
    del notion["brief-seats/social"]
    (tmp_path / "notion.json").write_text(json.dumps(notion), encoding="utf-8")
    assert build(tmp_path / "out", notion=tmp_path / "notion.json").returncode == 0
    text, _, _ = parse(tmp_path / "out/index.html")
    assert "NO PAGE YET" in text["cell/brief-seats/social"]
    assert "DRAFTED" not in text["cell/brief-seats/social"]


def test_the_text_reader_closes_a_keyed_element_that_holds_a_line_break():
    parser = Keyed()
    parser.feed('<div data-key="a">A<br>B</div><div data-key="b">C</div>')
    assert squash(parser.text["a"]) == "A B"
    assert squash(parser.text["b"]) == "C"


def test_a_rebuild_removes_a_blog_page_whose_gate_is_no_longer_published(tmp_path):
    out = tmp_path / "out"
    assert build(out).returncode == 0
    assert (out / "blog/pr-csv/index.html").is_file()
    notion = json.loads((FIXTURES / "notion.json").read_text(encoding="utf-8"))
    notion["pr-csv/blog"]["status"] = "Rejected"
    (tmp_path / "notion.json").write_text(json.dumps(notion), encoding="utf-8")
    assert build(out, notion=tmp_path / "notion.json").returncode == 0
    assert not (out / "blog/pr-csv").exists()


def test_every_reference_on_a_published_page_reaches_a_target_on_that_page(site):
    for page in ("blog/pr-csv/index.html", "changelog/index.html", "faq/index.html"):
        html = (site / page).read_text(encoding="utf-8")
        targets = set(re.findall(r'\bid="([^"]+)"', html))
        anchors = re.findall(r'href="#([^"]+)"', html)
        assert all(anchor in targets for anchor in anchors), (page, anchors, targets)


@pytest.mark.parametrize("entry, problem", [
    ({"status": "Drafted", "round": "two"}, 'pr-csv/blog has the round "two", expected a whole number'),
    ({"status": "Drafted", "round": None}, 'pr-csv/blog has the round "None", expected a whole number'),
    ({"status": "Drafted", "round": 0}, 'pr-csv/blog has the round "0", expected a whole number'),
    ({"status": "Drafted", "round": True}, 'pr-csv/blog has the round "True", expected a whole number'),
    ("Drafted", "pr-csv/blog must be an object with status, round and url"),
])
def test_a_malformed_notion_page_state_fails_the_build_with_its_key(tmp_path, entry, problem):
    notion = json.loads((FIXTURES / "notion.json").read_text(encoding="utf-8"))
    notion["pr-csv/blog"] = entry
    (tmp_path / "notion.json").write_text(json.dumps(notion), encoding="utf-8")
    result = build(tmp_path / "out", notion=tmp_path / "notion.json")
    assert result.returncode == 1
    assert f"FAIL {problem}" in result.stderr
