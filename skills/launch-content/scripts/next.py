"""The step runner of the gate loop. Code owns the order of steps; the model answers only judgment steps.

Usage:
  python next.py RUN_FOLDER                 print the one next step as JSON
  python next.py RUN_FOLDER --answer FILE   give the answer to that step (FILE or - for stdin), then
                                            print the step after it

Start a run with snapshot.py, then call this until it prints {"step": "done"} or {"step": "stopped"}.
The model answers the verdict, the claim list and each Draft. Code parses every answer, runs the Check
with at most two repairs per Draft, and prints the exact Notion payloads the agent posts.

State rules. Notion owns Status and the owner's comments, so run.json never holds a Status value.
Each Draft is keyed <source>/<gate>/r<N>, and a done key is never written again. Each gate stores the id
of the last comment it handled, starting with the agent's own ping. The run record is pushed to
launch-log before any Notion write, and every wake continues at the first step that is not done.
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -I leaves the script folder off the path

import check  # noqa: E402
import render_page  # noqa: E402

STATUSES = ("Drafted", "Needs changes", "Ready to post", "Posted", "Rejected")
DECISIONS = ("write", "skip", "ask")
TIERS = ("launch", "changelog")
MAX_REPAIRS = 2
RULE = re.compile(r"^(\d+)\. (.+)$", re.M)
OUTCOME = re.compile(r"^\| `([a-z]+)` \|([^|\n]*)\|$", re.M)
STAMP = re.compile(r"^[a-z0-9-]+: (\d+) lines, (\d+) claims, (\d+/\d+) parts$")

VERDICT_FORMAT = ("One line. A write is: write | <tier launch or changelog> | <rule number> | <quote from the "
                  "Snapshot> | <one line reason>. A skip or an ask is: skip | <rule number> | <quote> | <reason>.")
CLAIMS_FORMAT = "A JSON list of {\"id\": \"c1\", \"quote\": \"<exact words from the Snapshot>\"}, one per claim."
DRAFT_FORMAT = ("The Draft as markdown: one sentence per line, each line ending in its claim ids such as [c1, c2], "
                "and a <!-- part: name --> marker before each part of the contract, in order.")
PAGE_FORMAT = ("Search the database \"Launch gates\" for a page whose Key is the key. If one exists in any Status, "
               "create nothing and answer {\"page_id\": \"<its id>\", \"url\": \"<its url>\", \"created\": false}. "
               "Otherwise create the page with exactly these properties and content, the Owner set to the Notion "
               "user with that email, and answer {\"page_id\": \"<id>\", \"url\": \"<url>\", \"created\": true}.")
COMMENT_FORMAT = ("Add one page level comment to page_id: a mention of the Notion user with the mention email, "
                  "then the markdown. Answer {\"comment_id\": \"<the new comment's id>\"}.")


class StepFailed(Exception):
    pass


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def holds_status(value):
    if isinstance(value, dict):
        return any(key.casefold() == "status" or holds_status(item) for key, item in value.items())
    if isinstance(value, list):
        return any(holds_status(item) for item in value)
    return value in STATUSES


def load(folder):
    return json.loads((folder / "run.json").read_text("utf-8"))


def save(folder, run):
    (folder / "run.json").write_text(json.dumps(run, indent=2, ensure_ascii=False) + "\n", "utf-8", newline="\n")


def policy(skill):
    """Each rule number with its decision and tier, and the gates each outcome opens, from content-policy.md."""
    text = (Path(skill) / "references/content-policy.md").read_text("utf-8")
    rules = {}
    for number, words in RULE.findall(text):
        marked = re.findall(r"`([a-z]+)`", words)
        rules[int(number)] = (next((w for w in marked if w in DECISIONS), None),
                              next((w for w in marked if w in TIERS), None))
    opens = {name: [g.strip() for g in gates.split(",") if g.strip()] for name, gates in OUTCOME.findall(text)}
    return rules, opens


def snapshot_words(folder):
    return check.source_words((folder / "snapshot.md").read_text("utf-8"))


def quote_problem(quote, folder):
    problem = check.not_plain(quote)
    if problem:
        return f"quote {problem}"
    words = check.plain_words(quote)
    if len(words) < check.MIN_QUOTE_WORDS:
        return f"quote \"{quote}\" is shorter than {check.MIN_QUOTE_WORDS} words"
    if check.find_run(snapshot_words(folder), words) < 0:
        return f"quote not found in the Snapshot: \"{quote}\""
    return None


def parse_verdict(text, folder, skill):
    lines = [line for line in text.replace("\r\n", "\n").split("\n") if line.strip()]
    if len(lines) != 1:
        raise StepFailed(f"the verdict must be one line, got {len(lines)}")
    fields = [field.strip() for field in lines[0].split(" | ")]
    decision = fields[0]
    if decision not in DECISIONS:
        raise StepFailed(f"the verdict must start with write, skip or ask, got \"{decision}\"")
    size = 5 if decision == "write" else 4
    if len(fields) != size or not all(fields):
        raise StepFailed(f"a {decision} verdict has {size} fields separated by \" | \", got: {lines[0]}")
    tier = fields[1] if decision == "write" else None
    rule, quote, reason = fields[size - 3:]
    if decision == "write" and tier not in TIERS:
        raise StepFailed(f"a write verdict needs the tier launch or changelog, got \"{tier}\"")
    rules, _ = policy(skill)
    if not rule.isdigit() or int(rule) not in rules:
        raise StepFailed(f"rule \"{rule}\" is not a rule of the content policy")
    if rules[int(rule)] != (decision, tier):
        expected = " ".join(w for w in rules[int(rule)] if w)
        raise StepFailed(f"rule {rule} gives {expected}, not {' '.join(w for w in (decision, tier) if w)}")
    problem = quote_problem(quote, folder)
    if problem:
        raise StepFailed(f"verdict {problem}")
    return {"decision": decision, "tier": tier, "rule": int(rule), "quote": quote, "reason": reason}


def parse_json(text, what):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise StepFailed(f"the {what} answer is not valid JSON") from None


def parse_claims(text, folder):
    claims = parse_json(text, "claims")
    if not isinstance(claims, list) or not claims:
        raise StepFailed("the claims answer must be a list with at least one claim")
    ids = []
    for n, claim in enumerate(claims, 1):
        if not (isinstance(claim, dict) and set(claim) == {"id", "quote"}
                and all(isinstance(claim[k], str) for k in claim) and check.CLAIM_ID.fullmatch(claim["id"])):
            raise StepFailed(f"claim {n} must hold only a plain text id and a quote")
        if claim["id"] in ids:
            raise StepFailed(f"claim id {claim['id']} is used twice")
        ids.append(claim["id"])
        problem = quote_problem(claim["quote"], folder)
        if problem:
            raise StepFailed(f"claim {claim['id']}: {problem}")
    return claims


def parse_reply(text, required):
    reply = parse_json(text, "Notion")
    if not isinstance(reply, dict) or not all(isinstance(reply.get(k), kind) and reply[k] != ""
                                              for k, kind in required.items()):
        raise StepFailed(f"the Notion answer must hold {', '.join(required)}")
    return reply


def open_gates(run, skill):
    _, opens = policy(skill)
    for gate in opens.get(run["verdict"]["tier"] or "", []):
        run["gates"][gate] = {"contract": f"gates/{gate}.md", "owner_role": render_page.contract(skill, gate)["owner_role"],
                              "notion_page": "", "notion_url": "", "round": 0, "last_comment_id": "", "rounds": []}
        run["steps"]["gates"][gate] = {"r1": "pending", "repairs": 0}


def draft_path(folder, gate):
    return folder / "gates" / gate / "draft.md"


def run_check(folder, run, gate, skill):
    """The Check on one drafted gate: a pass saves the baseline, a failure asks for a repair, at most twice."""
    failures, stamps = check.check(folder, gate, Path(skill))
    state = run["steps"]["gates"][gate]
    if not failures:
        body = draft_path(folder, gate).read_bytes()
        baseline = draft_path(folder, gate).with_name("draft.agent.r1.md")
        baseline.write_bytes(body)
        lines, claims, parts = STAMP.match(stamps[0]).groups()
        run["gates"][gate].update(round=1, rounds=[{
            "n": 1, "baseline": baseline.relative_to(folder).as_posix(),
            "baseline_sha256": hashlib.sha256(body).hexdigest(), "owner_sources": "",
            "check": {"ok": True, "lines": int(lines), "claims": int(claims), "parts": parts}}])
        state["r1"] = "checked"
        return None
    if state["repairs"] < MAX_REPAIRS:
        return {"step": "repair", "gate": gate, "repair": state["repairs"] + 1, "failures": failures,
                "draft": draft_path(folder, gate).as_posix(), "answer": DRAFT_FORMAT}
    run["gates"][gate]["failed_check"] = failures
    state["r1"] = "failed"
    return None


def gate_step(folder, run, skill):
    """The next step of the first gate that is not done, or None when every gate is done."""
    gates = run["steps"]["gates"]
    for gate, state in gates.items():
        if state["r1"] == "pending":
            return {"step": "draft", "gate": gate, "round": 1, "contract": f"gates/{gate}.md",
                    "snapshot": (folder / "snapshot.md").as_posix(), "claims": run["claims"], "answer": DRAFT_FORMAT}
    for gate, state in gates.items():
        if state["r1"] == "drafted":
            step = run_check(folder, run, gate, skill)
            save(folder, run)
            if step:
                return step
    if run["steps"].get("push") != "done":
        return push_step(folder, run, "push", "the run record, before any Notion write")
    for gate, state in gates.items():
        if state["r1"] == "checked":
            page = render_page.notion_write(render_page.render(folder, gate, skill))
            return {"step": "notion_page", "gate": gate, "key": page["key"], "database": render_page.DATABASE,
                    "page": page, "answer": PAGE_FORMAT}
        if state["r1"] == "paged":
            entry = run["gates"][gate]
            name, person = render_page.owner(skill, entry["owner_role"])
            stamp = entry["rounds"][-1]["check"]
            text = (f"{name}, round 1 of the {gate} Draft for \"{run['source']['title']}\" is ready for your review. "
                    f"Check: {stamp['lines']} lines, {stamp['claims']} claims, {stamp['parts']} parts. "
                    "Leave your notes as comments, then set the Status.")
            return {"step": "notion_comment", "gate": gate, "page_id": entry["notion_page"], "mention": person,
                    "markdown": text, "answer": COMMENT_FORMAT}
    return None


def push_step(folder, run, kind, what):
    root, path = folder.parent.parent.as_posix(), f"runs/{run['id']}"
    return {"step": kind, "what": what, "commands": [
        f"git -C \"{root}\" add \"{path}\"",
        f"git -C \"{root}\" commit -m \"Run {run['id']}: {kind}\"",
        f"git -C \"{root}\" push origin launch-log"], "answer": "pushed"}


def current(folder, skill):
    folder = Path(folder)
    run = load(folder)
    steps = run["steps"]
    if holds_status(run):
        return {"step": "stopped", "reason": "run.json holds a Notion Status; Notion owns Status"}
    if steps.get("snapshot") != "done":
        return {"step": "stopped", "reason": "the run has no Snapshot; run snapshot.py first"}
    if steps.get("error"):
        return {"step": "stopped", "reason": steps["error"]}
    if "verdict" not in run:
        return {"step": "verdict", "snapshot": (folder / "snapshot.md").as_posix(),
                "policy": (Path(skill) / "references/content-policy.md").as_posix(), "answer": VERDICT_FORMAT}
    if run["verdict"]["decision"] == "write":
        if steps.get("claims") != "done":
            return {"step": "claims", "snapshot": (folder / "snapshot.md").as_posix(), "answer": CLAIMS_FORMAT}
        step = gate_step(folder, run, skill)
        if step:
            return step
    if steps.get("final_push") != "done":
        return push_step(folder, run, "final_push", "the run record with the Notion page ids")
    return {"step": "done"}


def apply(folder, run, step, text, skill):
    kind, steps = step["step"], run["steps"]
    if kind == "verdict":
        run["verdict"] = parse_verdict(text, folder, skill)
        steps.update(verdict="done", gates={})
        if run["verdict"]["decision"] == "write":
            open_gates(run, skill)
        else:
            steps["claims"] = "not needed"
    elif kind == "claims":
        run["claims"] = parse_claims(text, folder)
        steps["claims"] = "done"
    elif kind in ("draft", "repair"):
        if not text.strip():
            raise StepFailed(f"the {step['gate']} Draft is empty")
        path = draft_path(folder, step["gate"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
        steps["gates"][step["gate"]]["r1"] = "drafted"
        if kind == "repair":
            steps["gates"][step["gate"]]["repairs"] += 1
    elif kind in ("push", "final_push"):
        if text.strip() != "pushed":
            raise StepFailed(f"the {kind} answer must be the word pushed")
        steps[kind] = "done"
    elif kind == "notion_page":
        reply = parse_reply(text, {"page_id": str, "url": str, "created": bool})
        run["gates"][step["gate"]].update(notion_page=reply["page_id"], notion_url=reply["url"])
        steps["gates"][step["gate"]]["r1"] = "paged" if reply["created"] else "exists"
    elif kind == "notion_comment":
        reply = parse_reply(text, {"comment_id": str})
        run["gates"][step["gate"]]["last_comment_id"] = reply["comment_id"]
        steps["gates"][step["gate"]]["r1"] = "pinged"
    run["times"][kind] = now()


def answer(folder, text, skill):
    """Apply the answer to the current step, save the run record, and return the step after it."""
    folder = Path(folder)
    step = current(folder, skill)
    if step["step"] in ("done", "stopped"):
        return step
    run = load(folder)
    try:
        apply(folder, run, step, text, skill)
    except StepFailed as problem:
        run = load(folder)
        run["steps"]["error"] = f"{step['step']}: {problem}"
    save(folder, run)
    return current(folder, skill)


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Print the next step of a run, or answer the current one.")
    parser.add_argument("run", type=Path)
    parser.add_argument("--answer", help="a file holding the answer, or - for stdin")
    parser.add_argument("--skill", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    if args.answer is None:
        step = current(args.run, args.skill)
    else:
        text = sys.stdin.read() if args.answer == "-" else Path(args.answer).read_text("utf-8")
        step = answer(args.run, text, args.skill)
    print(json.dumps(step, indent=2, ensure_ascii=False))
    return 1 if step["step"] == "stopped" else 0


if __name__ == "__main__":
    sys.exit(main())
