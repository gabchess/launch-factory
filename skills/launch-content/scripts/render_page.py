"""The gate page renderer and the Notion writer guard.

Usage: python render_page.py RUN_FOLDER GATE [--skill SKILL_FOLDER]

Prints the Notion page payload of one checked gate as JSON: its properties and its body, the door line
and the Draft as a two column table, each Draft line beside its claim ids and quotes. The renderer only
ever writes the Status Drafted, and notion_write refuses any page whose Status is anything else, so no
code path of the agent can set Ready to post, Needs changes, Posted or Rejected.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -I leaves the script folder off the path

import check  # noqa: E402

DRAFTED = "Drafted"
DATABASE = "Launch gates"
# The one statement that creates the gates database through the Notion connector.
DATABASE_SCHEMA = ("CREATE TABLE (\"Name\" TITLE, \"Key\" RICH_TEXT, \"Gate\" SELECT('blog':blue, 'changelog':green, "
                   "'social':pink, 'faq':purple), \"Status\" STATUS('Drafted':gray:to_do, 'Needs changes':orange:in_progress, "
                   "'Ready to post':green:complete, 'Posted':blue:complete, 'Rejected':red:complete), "
                   "\"Owner\" PEOPLE, \"Owner sources\" RICH_TEXT, \"Round\" NUMBER, \"Check\" RICH_TEXT, \"Run\" URL)")


class NotionRefused(Exception):
    pass


def owner(skill, role):
    """The display name and Notion person of one owner role. The only reader of owners.json."""
    entry = json.loads((Path(skill) / "owners.json").read_text("utf-8"))["roles"][role]
    return entry["display_name"], entry.get("notion_person", "")


def contract(skill, gate):
    text = (Path(skill) / "gates" / f"{gate}.md").read_text("utf-8")
    return json.loads(check.CONTRACT.search(text).group(1))


def draft_rows(text, quotes):
    rows = []
    for raw in text.replace("\r\n", "\n").split("\n"):
        line = raw.strip(" ")
        if not line or check.PART.fullmatch(line):
            continue
        cited = check.CITATIONS.search(line)
        body = (line[:cited.start()] if cited else line).strip(" ")
        ids = check.CLAIM_ID.findall(cited.group(0)) if cited else []
        backing = "<br />".join(f"{c}: \"{quotes.get(c, '')}\"" for c in ids) or "No claim needed"
        rows.append(f"| {body} | {backing} |")
    return rows


def render(folder, gate, skill):
    folder = Path(folder)
    run = json.loads((folder / "run.json").read_text("utf-8"))
    entry = run["gates"][gate]
    terms = contract(skill, gate)
    stamp = entry["rounds"][-1]["check"]
    quotes = {c["id"]: c["quote"] for c in run["claims"]}
    path = folder / "gates" / gate / "draft.md"
    body = path.read_bytes()
    if hashlib.sha256(body).hexdigest() != entry["rounds"][-1]["baseline_sha256"]:
        raise NotionRefused(f"{path.relative_to(folder).as_posix()} changed after the Check passed; only checked text is posted")
    draft = body.decode("utf-8")
    door = f"Door: {terms['door']}. Blast radius: {terms['blast_radius']}."
    table = ["| Draft line | Claims and quotes |", "| --- | --- |", *draft_rows(draft, quotes)]
    key = f"{run['id']}/{gate}"
    return {
        "key": key,
        "properties": {
            "Name": f"{run['source']['title']} · {gate}", "Key": key, "Gate": gate, "Status": DRAFTED,
            "Owner": owner(skill, entry["owner_role"])[1], "Owner sources": entry["rounds"][-1]["owner_sources"],
            "Round": entry["round"],
            "Check": f"{stamp['lines']} lines · {stamp['claims']} claims · {stamp['parts']} parts",
            "Run": run.get("record_link", "")},
        "content": "\n".join([door, "", *table]) + "\n",
    }


def notion_write(page):
    """The page exactly as the agent will post it, or NotionRefused when its Status is not Drafted."""
    status = page.get("properties", {}).get("Status")
    if status != DRAFTED:
        raise NotionRefused(f"the agent writes only the Status {DRAFTED}, not {status!r}")
    return page


def blocks(page):
    """Blocks the page adds: the page, the door line, the table and one block per table row."""
    rows = [line for line in page["content"].splitlines() if re.match(r"\| (?!--- )", line)]
    return 3 + len(rows)


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Print the Notion page payload of one gate.")
    parser.add_argument("run", type=Path)
    parser.add_argument("gate")
    parser.add_argument("--skill", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    print(json.dumps(notion_write(render(args.run, args.gate, args.skill)), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
