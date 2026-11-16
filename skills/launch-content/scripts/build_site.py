"""The site builder: run records and Notion page states in, the board and the published pages out.

Usage: python build_site.py RUNS_FOLDER --notion NOTION_JSON --owners OWNERS_JSON --out SITE_FOLDER [--skill SKILL_FOLDER]

NOTION_JSON maps "<source>/<gate>" to {"status", "round", "url"}, recorded from the gates database.
A gate's Status is read only from it, never from run.json, and a gate whose Draft fails the Check is held.
"""

import argparse
import json
import re
import shutil
import sys
from datetime import datetime
from html import escape
from pathlib import Path
from string import Template
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check  # noqa: E402

GATES = {"blog": "Blog post", "changelog": "Changelog", "social": "Social post", "faq": "FAQ update"}
STATUS = {
    "Drafted": ("review", False),
    "Needs changes": ("back", False),
    "Ready to post": ("ok", True),
    "Posted": ("ok", True),
    "Rejected": ("skip", False),
}
NEXT = [("customer-email", "Customer email", "Lifecycle"),
        ("video-script", "Video script", "Video"),
        ("site-animation", "Site animation", "Design")]
KINDS = {"pull_request": ("Pull request", "is-pr", "merged pull request"),
         "briefing": ("Product brief", "is-brief", "product brief")}
COUNTS = re.compile(r"(\d+) lines, (\d+) claims, (\d+/\d+) parts")
PERSON = ('<svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">'
          '<circle cx="8" cy="5" r="3"/><path d="M2 15a6 6 0 0 1 12 0z"/></svg>')
SITE = Path(__file__).resolve().parents[1] / "site"


class BuildError(Exception):
    pass


class Shown(NamedTuple):
    """One Draft line as a reader sees it: its heading mark, its text without citations, and its claim ids."""
    mark: str
    text: str
    claims: tuple[str, ...]


class Cell(NamedTuple):
    run: dict
    gate: str
    stamp: str
    tone: str
    published: bool
    counts: str
    round: int
    url: str
    held: str


def plural(n, word):
    return f"{n} {word}" if n == "1" else f"{n} {word}s"


def shown_lines(text):
    lines = []
    for raw in text.replace("\r\n", "\n").split("\n"):
        line = raw.strip()
        if not line or check.PART.fullmatch(line):
            continue
        cited = check.CITATIONS.search(line)
        body = (line[:cited.start()] if cited else line).strip()
        mark = check.HEADING.match(body)
        lines.append(Shown(mark.group(0) if mark else "", body[mark.end():] if mark else body,
                           tuple(check.CLAIM_ID.findall(cited.group(0))) if cited else ()))
    return lines


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as problem:
        raise BuildError(f"{path.name} cannot be read: {problem}") from None


def owner_role(skill, gate):
    path = skill / "gates" / f"{gate}.md"
    block = check.CONTRACT.search(path.read_text(encoding="utf-8")) if path.is_file() else None
    return json.loads(block.group(1)).get("owner_role", "") if block else ""


def owner(owners, role):
    name = owners.get("roles", {}).get(role, {}).get("display_name", "")
    return " · ".join(part for part in (name, role.capitalize()) if part)


def page_state(notion, key):
    state = notion.get(key)
    if state is None:
        return None
    if not isinstance(state, dict):
        raise BuildError(f"{key} must be an object with status, round and url")
    if state.get("status") not in STATUS:
        raise BuildError(f"{key} has the Notion Status \"{state.get('status')}\", expected one of {', '.join(STATUS)}")
    rounds = state.get("round", 1)
    if isinstance(rounds, bool) or not isinstance(rounds, int) or rounds < 1:
        raise BuildError(f"{key} has the round \"{rounds}\", expected a whole number")
    return {"status": state["status"], "round": rounds, "url": str(state.get("url") or "")}


def resolve(folder, run, gate, skill, notion):
    """One cell: held when the Check fails, else the Status of its Notion page, else no page yet."""
    try:
        failures, stamps = check.check(folder, gate, skill)
    except check.Unreadable as problem:
        failures, stamps = [str(problem)], []
    state = page_state(notion, f"{run['id']}/{gate}")
    found = COUNTS.search(stamps[0]) if stamps else None
    counts = " · ".join((plural(found[1], "line"), plural(found[2], "claim"), f"{found[3]} parts")) if found else ""
    url = state["url"] if state else ""
    rounds = state["round"] if state else 1
    if failures:
        return Cell(run, gate, "HELD BY THE CHECK", "back", False, counts, rounds, url, failures[0])
    if state is None:
        return Cell(run, gate, "NO PAGE YET", "skip", False, counts, rounds, url, "")
    tone, published = STATUS[state["status"]]
    return Cell(run, gate, state["status"].upper(), tone, published, counts, rounds, url, "")


def when(stamp, layout):
    try:
        return datetime.fromisoformat(stamp.replace("Z", "+00:00")).strftime(layout)
    except (AttributeError, ValueError):
        return ""


def load_runs(folder):
    runs = []
    for path in sorted(folder.glob("*/run.json")):
        run = read_json(path)
        problems = check.record_problems(run)
        if problems:
            raise BuildError(f"{path.parent.name}: {problems[0]}")
        runs.append((path.parent, run))
    return sorted(runs, key=lambda item: item[1]["source"].get("received", ""), reverse=True)


def link(cell):
    if cell.published:
        return {"blog": f"blog/{cell.run['id']}/index.html", "changelog": "changelog/index.html",
                "faq": "faq/index.html", "social": "social/index.html"}[cell.gate]
    return cell.url or "#"


def cell_html(cell, owners, selected):
    key = f"{cell.run['id']}/{cell.gate}"
    role = cell.run["gates"][cell.gate].get("owner_role", "")
    attrs = ' class="cell is-selected" href="#open" aria-current="true"' if selected else f' class="cell" href="{escape(link(cell))}"'
    held = f'\n              <span class="cell-held">{escape(cell.held)}</span>' if cell.held else ""
    counts = f'\n              <span class="cell-n">{escape(cell.counts)}</span>' if cell.counts else ""
    return f"""            <a data-key="cell/{escape(key)}"{attrs}>
              <span class="cell-gate">{GATES[cell.gate]}</span>
              <span class="stamp {cell.tone}">{cell.stamp}</span>{counts}{held}
              <span class="cell-who">round {cell.round} · {escape(owner(owners, role))}</span>
            </a>"""


def row_html(run, cells, owners, selected):
    kind, kind_class, _ = KINDS[run["source"]["kind"]]
    decision = run["verdict"]["decision"]
    quiet = {"write": "", "ask": " is-ask", "skip": " is-quiet"}[decision]
    head = f"""          <li class="src{quiet}" data-key="row/{escape(run['id'])}">
            <div class="src-what">
              <span class="src-time">{when(run['source'].get('received'), '%a<br>%H:%M')}</span>
              <span class="src-body"><span class="src-title">{escape(run['source']['title'])}</span><span class="kind {kind_class}">{kind}</span></span>
            </div>"""
    if decision == "ask":
        questions = run["source"]["open_questions"]
        items = "".join(f"<li>{escape(q)}</li>" for q in questions)
        body = f"""            <a class="cell span" href="#">
              <span class="stamp ask">ASK</span>
              <span class="cell-text"><span class="cell-n">{plural(str(len(questions)), 'question')} for product</span><ul class="asks">{items}</ul></span>
            </a>"""
    elif decision == "skip":
        body = f"""            <span class="cell span">
              <span class="stamp skip">SKIP</span>
              <span class="cell-n">{escape(run['verdict'].get('reason', ''))}</span>
            </span>"""
    else:
        body = "\n".join(cell_html(cells[g], owners, cells[g] is selected) if g in cells
                         else f'            <span class="cell is-empty" data-key="cell/{escape(run["id"])}/{g}"></span>'
                         for g in GATES)
    return f"{head}\n{body}\n          </li>"


def clock_html(runs):
    writes = [run for _, run in runs if run["verdict"]["decision"] == "write"]
    asked = sum(run["verdict"]["decision"] == "ask" for _, run in runs)
    week = (f'<p class="week">This week <b>{len(runs)}</b> arrived<br><b>{len(writes)}</b> drafted · '
            f'<b>{asked}</b> asked · <b>{len(runs) - len(writes) - asked}</b> skipped</p>')
    took = ""
    for run in writes:
        times = run.get("times", {})
        try:
            start, end = (datetime.fromisoformat(times[k].replace("Z", "+00:00")) for k in ("received", "proposed"))
        except (KeyError, AttributeError, ValueError):
            continue
        n = str(len(run["gates"]))
        line = (f"one {KINDS[run['source']['kind']][2]} became {plural(n, 'draft')} for "
                f"{plural(str(len({g.get('owner_role') for g in run['gates'].values()})), 'owner')}")
        seconds = int((end - start).total_seconds())
        took = (f'\n    <div class="took">\n      <div class="took-n">{seconds}<small>s</small></div>\n'
                f'      <p class="took-what">{line}</p>\n    </div>')
        label = f"{seconds} seconds: {line}"
        break
    else:
        label = "This week"
    return f'  <section class="clock" aria-label="{escape(label)}">{took}\n    {week}\n  </section>'


def quote_where(folder, claim):
    """An owner claim's quote lives in the Owner sources of its gate, as check.py checks it; any other in the Snapshot."""
    if "gate" in claim:
        return "Owner sources"
    claim_words = check.plain_words(claim["quote"])
    for number, line in enumerate((folder / "snapshot.md").read_text(encoding="utf-8").split("\n"), 1):
        if check.find_run(check.source_words(line), claim_words) >= 0:
            return f"Snapshot, line {number}"
    return "Snapshot"


def slip_html(folder, cell, owners):
    run = cell.run
    claims = {c["id"]: (n, c["quote"]) for n, c in enumerate(run["claims"], 1)}
    places = {c["id"]: quote_where(folder, c) for c in run["claims"]}
    rows = []
    for index, line in enumerate(shown_lines((folder / "gates" / cell.gate / "draft.md").read_text(encoding="utf-8"))):
        ids = " ".join(str(claims[c][0]) for c in line.claims if c in claims)
        quotes = "".join(f'<p class="line-quote">"{escape(claims[c][1])}"</p>'
                         f'<p class="line-where">{places[c]}</p>'
                         for c in line.claims if c in claims)
        title = " is-title" if index == 0 and line.mark.startswith("#") else ""
        rows.append(f"""          <li class="line{title}">
            <p class="line-copy">{escape(line.text)}</p>
            {f'<span class="line-id" title="claim {escape(", ".join(line.claims))}">{ids}</span>' if ids else ""}
            <div class="line-src">{quotes}</div>
          </li>""")
    first, rest = rows[:2], rows[2:]
    more = (f'        <details class="more">\n          <summary>{plural(str(len(rest)), "more line")}</summary>\n'
            f'          <ol>\n' + "\n".join(rest) + "\n          </ol>\n        </details>\n") if rest else ""
    banned = "".join(f"<li>{escape(p)}</li>" for p in run["source"]["do_not_say"])
    ban = (f'        <div class="ban">\n          <h3>Banned phrases</h3>\n          <ul>{banned}</ul>\n'
           f'          <p>None found</p>\n        </div>\n') if banned else ""
    role = run["gates"][cell.gate].get("owner_role", "")
    return f"""      <article class="slip is-open" id="open">
        <div class="slip-head">
          <span class="stamp {cell.tone}">{cell.stamp}</span>
          <h2>{GATES[cell.gate]}<span>{escape(run['source']['title'])}</span></h2>
          <span class="owner">{PERSON}{escape(owner(owners, role))}</span>
        </div>
        <ol>
{chr(10).join(first)}
        </ol>
{more}{ban}        <div class="slip-foot">
          <a class="btn" href="{escape(cell.url or '#')}">Review in Notion</a>
        </div>
      </article>"""


def ref(claims, claim_id, linked):
    """A link to the quote list on a blog page; elsewhere the quote rides in the title, since no quote list is on the page."""
    number, quote = claims.get(claim_id, ("?", ""))
    if linked:
        return f'<a class="ref" href="#{escape(claim_id)}" aria-label="Source for claim {escape(claim_id)}">{number}</a>'
    return f'<span class="ref" title="{escape(quote)}">{number}</span>'


def sentence(line, claims, linked=True):
    return f"<p>{escape(line.text)}{''.join(ref(claims, c, linked) for c in line.claims)}</p>"


def post_page(owners, title, root, current, main, nav_links, script=""):
    pages = [("What is new", nav_links.get("blog")), ("Changelog", "changelog/index.html"),
             ("FAQ", "faq/index.html"), ("Social", "social/index.html")]
    nav = "\n".join(f'      <a href="{root}{escape(href)}"{" aria-current=\"page\"" if label == current else ""}>{label}</a>'
                    for label, href in pages if href)
    return Template((SITE / "post.html").read_text(encoding="utf-8")).substitute(
        title=escape(title), company=escape(owners.get("company", "")), root=root, nav=nav, main=main, script=script)


def blog_page(folder, cell, owners, also, nav_links):
    run = cell.run
    claims = {c["id"]: (n, c["quote"]) for n, c in enumerate(run["claims"], 1)}
    lines = shown_lines((folder / "gates/blog/draft.md").read_text(encoding="utf-8"))
    title = next((line.text for line in lines if line.mark == "# "), run["source"]["title"])
    body = "\n".join("      " + sentence(line, claims) for line in lines if line.mark != "# ")
    cited = list(dict.fromkeys(c for line in lines for c in line.claims if c in claims))
    kind = KINDS[run["source"]["kind"]][0]
    where = (f'<a href="{escape(run["source"]["link"])}">{kind}</a>' if run["source"].get("link") else kind)
    places = {c["id"]: quote_where(folder, c) if "gate" in c else f"{where}, {quote_where(folder, c).lower()}"
              for c in run["claims"]}
    sources = "\n".join(f"""      <li class="src" id="{escape(c)}" data-key="quote/{escape(c)}">
        <span class="src-id">{claims[c][0]}</span>
        <div>
          <p class="src-quote">"{escape(claims[c][1])}"</p>
          <p class="src-where">{places[c]}</p>
        </div>
      </li>""" for c in cited)
    links = [f'the <a href="../../{page}/index.html">{label}</a>' for gate, page, label in
             (("changelog", "changelog", "changelog"), ("faq", "faq", "FAQ")) if gate in also]
    via_also = f'\n    <span class="via-also">Also in {" and ".join(links)}</span>' if links else ""
    role = run["gates"]["blog"].get("owner_role", "")
    name = owners.get("roles", {}).get(role, {}).get("display_name", "")
    main = f"""  <p class="meta"><b>{escape(str(run['verdict'].get('tier') or 'Launch').capitalize())}</b>, arrived {when(run['source'].get('received'), '%A at %H:%M')}</p>
  <h1>{escape(title)}</h1>

  <div>
    <div class="body">
{body}
    </div>
  </div>

  <p class="via">
    <span class="via-ok">{escape(cell.stamp.capitalize())}</span>
    <span>Blog post · approved by <b>{escape(name)}</b>, {escape(role.capitalize())}</span>{via_also}
  </p>

  <aside class="sources" aria-labelledby="src-h">
    <h2 id="src-h">The quote behind each sentence</h2>
    <ol>
{sources}
    </ol>
  </aside>"""
    return post_page(owners, title, "../../", "What is new", main, nav_links)


def list_page(owners, title, current, entries, nav_links, script=""):
    main = f"""  <p class="meta"><b>{title}</b>, newest first</p>
  <h1>{title}</h1>

  <ol class="entries">
{entries}
  </ol>"""
    return post_page(owners, title, "../", current, main, nav_links, script)


def changelog_entry(folder, run):
    claims = {c["id"]: (n, c["quote"]) for n, c in enumerate(run["claims"], 1)}
    lines = shown_lines((folder / "gates/changelog/draft.md").read_text(encoding="utf-8"))
    body = "\n".join("        " + sentence(line, claims, linked=False) for line in lines)
    return f"""    <li data-key="changelog/{escape(run['id'])}">
      <p class="entry-when">{when(run['source'].get('received'), '%a %d %b %Y')}</p>
      <h2>{escape(run['source']['title'])}</h2>
      <div class="body">
{body}
      </div>
    </li>"""


def faq_entries(folder, run):
    claims = {c["id"]: (n, c["quote"]) for n, c in enumerate(run["claims"], 1)}
    groups = []
    for line in shown_lines((folder / "gates/faq/draft.md").read_text(encoding="utf-8")):
        if line.mark == "## ":
            groups.append((re.sub(r"^Q:\s*", "", line.text), []))
        elif groups:
            groups[-1][1].append(line)
    return "\n".join(f"""    <li data-key="faq/{escape(run['id'])}/{n}">
      <h2>{escape(question)}</h2>
      <div class="body">
{chr(10).join('        ' + sentence(line, claims, linked=False) for line in answer)}
      </div>
    </li>""" for n, (question, answer) in enumerate(groups, 1))


COPY_SCRIPT = """<script>
  document.addEventListener("click", function (event) {
    var button = event.target.closest("[data-copy]");
    if (!button) return;
    var text = document.getElementById(button.getAttribute("data-copy")).innerText;
    navigator.clipboard.writeText(text).then(function () { button.textContent = "Copied"; });
  });
</script>"""


def social_card(folder, run):
    lines = shown_lines((folder / "gates/social/draft.md").read_text(encoding="utf-8"))
    text = "\n".join(f"        <p>{escape(line.text)}</p>" for line in lines)
    return f"""    <li class="card" data-key="social/{escape(run['id'])}">
      <p class="entry-when">{escape(run['source']['title'])}</p>
      <div class="body" id="social-{escape(run['id'])}">
{text}
      </div>
      <button class="copy" type="button" data-copy="social-{escape(run['id'])}">Copy</button>
    </li>"""


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def build(runs_folder, notion_path, owners_path, skill, out):
    owners = read_json(owners_path)
    notion = read_json(notion_path)
    runs = load_runs(runs_folder)
    cells = {run["id"]: {g: resolve(folder, run, g, skill, notion) for g in run["gates"] if g in GATES}
             for folder, run in runs}
    selected = next((c for _, run in runs for c in cells[run["id"]].values() if c.tone in ("review", "back") and not c.held), None)
    folders = {run["id"]: folder for folder, run in runs}

    heads = "\n".join(f"""          <div data-key="head/{g}">
            <span class="gate-name">{label}</span>
            <span class="owner">{PERSON}{escape(owner(owners, owner_role(skill, g)))}</span>
          </div>""" for g, label in GATES.items())
    rows = "\n".join(row_html(run, cells[run["id"]], owners, selected) for _, run in runs)
    nexts = "\n".join(f"""        <li data-key="next/{key}">
          <span class="gate-name">{label}</span>
          <span class="next-owner">Owner: {role}</span>
          <span class="next-add">adds one file</span>
        </li>""" for key, label, role in NEXT)
    mode = str(runs[0][1]["mode"]).capitalize() if runs else "Suggest"
    write(out / "index.html", Template((SITE / "board.html").read_text(encoding="utf-8")).substitute(
        company=escape(owners.get("company", "")), mode=f"Mode: {escape(mode)} · Autonomous locked",
        clock=clock_html(runs), heads=heads, rows=rows, nexts=nexts,
        slip=slip_html(folders[selected.run["id"]], selected, owners) if selected else ""))

    published = {g: [c for _, run in runs for c in [cells[run["id"]].get(g)] if c and c.published] for g in GATES}
    shutil.rmtree(out / "blog", ignore_errors=True)
    nav_links = {"blog": f"blog/{published['blog'][0].run['id']}/index.html"} if published["blog"] else {}
    for cell in published["blog"]:
        also = {g for g, c in cells[cell.run["id"]].items() if c.published}
        write(out / "blog" / cell.run["id"] / "index.html", blog_page(folders[cell.run["id"]], cell, owners, also, nav_links))
    write(out / "changelog/index.html", list_page(owners, "Changelog", "Changelog", "\n".join(
        changelog_entry(folders[c.run["id"]], c.run) for c in published["changelog"]), nav_links))
    write(out / "faq/index.html", list_page(owners, "FAQ", "FAQ", "\n".join(
        faq_entries(folders[c.run["id"]], c.run) for c in published["faq"]), nav_links))
    write(out / "social/index.html", list_page(owners, "Social", "Social", "\n".join(
        social_card(folders[c.run["id"]], c.run) for c in published["social"]), nav_links, COPY_SCRIPT))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build the board and the published pages from run records.")
    parser.add_argument("runs", type=Path)
    parser.add_argument("--notion", type=Path, required=True)
    parser.add_argument("--owners", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--skill", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    try:
        build(args.runs, args.notion, args.owners, args.skill, args.out)
    except BuildError as problem:
        print(f"FAIL {problem}", file=sys.stderr)
        return 1
    print(f"built {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
