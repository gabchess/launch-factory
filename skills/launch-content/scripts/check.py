"""The Check: confirm one run record, or one gate of it, against its gate contract.

Usage: python check.py RUN_FOLDER [GATE] [--skill SKILL_FOLDER]

Exits 0 when every rule holds and 1 with one line per failure otherwise.
"""

import argparse
import json
import re
import sys
from pathlib import Path

CITATION = re.compile(r"\s*\[([A-Za-z0-9_-]+(?:\s*,\s*[A-Za-z0-9_-]+)*)\]\s*$")
PART = re.compile(r"^<!--\s*part:\s*([A-Za-z0-9_-]+)\s*-->$")
CONTRACT = re.compile(r"```json\s*\n(.*?)\n```", re.S)
NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
WORD = re.compile(r"[\w'’-]+")

REQUIRED = {
    "id": None,
    "mode": None,
    "source.kind": ("briefing", "pull_request"),
    "source.title": None,
    "source.do_not_say": None,
    "source.open_questions": None,
    "verdict.decision": ("ask", "skip", "write"),
    "claims": None,
    "gates": None,
}

MEASURES = {
    "lines": lambda texts: len(texts),
    "words": lambda texts: sum(len(WORD.findall(text)) for text in texts),
    "chars": lambda texts: len(" ".join(texts)),
}

VERDICT_RULES = {
    "write": lambda run: [] if run["claims"] else ["verdict write has zero claims"],
    "skip": lambda run: shut(run),
    "ask": lambda run: shut(run) + ([] if run["source"]["open_questions"] else ["verdict ask lists no open questions"]),
}


def shut(run):
    return [f"verdict {run['verdict']['decision']} opens gate {g}" for g in run["gates"]]


def flat(text):
    return " ".join(text.split())


def read_text(path):
    return path.read_bytes().decode("utf-8")


def parse_draft(text):
    """One entry per content line: (line number, part, text without citation, cited claim ids)."""
    lines, part = [], None
    for number, raw in enumerate(text.split("\n"), 1):
        line = raw.strip()
        marker = PART.match(line)
        if marker:
            part = marker.group(1)
        elif line:
            cited = CITATION.search(line)
            ids = [c.strip() for c in cited.group(1).split(",")] if cited else []
            lines.append((number, part, CITATION.sub("", line), ids))
    return lines


def check_gate(run, gate, lines, skill):
    path = skill / "gates" / f"{gate}.md"
    if not path.is_file():
        return [f"unknown gate {gate}: no contract gates/{gate}.md"], None
    contract = json.loads(CONTRACT.search(read_text(path)).group(1))
    quotes = {c["id"]: c["quote"] for c in run["claims"]}
    cited = {c for _, _, _, ids in lines for c in ids}
    parts = [p for p in contract["parts"] if any(part == p for _, part, _, _ in lines)]
    failures = [] if lines else [f"{gate} has zero lines"]
    failures += [] if cited else [f"{gate} cites zero claims"]
    failures += [f"{gate} line {n} cites no claim: \"{text}\""
                for n, _, text, ids in lines if not ids and not text.startswith(tuple(contract["uncited"]))]
    failures += [f"{gate} line {n} cites unknown claim {c}" for n, _, _, ids in lines for c in ids if c not in quotes]
    failures += [f"{gate} line {n} contains the Do not say phrase \"{phrase}\""
                 for n, _, text, _ in lines for phrase in run["source"]["do_not_say"]
                 if flat(phrase).casefold() in flat(text).casefold()]
    failures += [f"{gate} line {n}: number {number} is not in its cited claims {', '.join(ids)}"
                 for n, _, text, ids in lines for number in NUMBER.findall(text)
                 if number not in {x for c in ids for x in NUMBER.findall(quotes.get(c, ""))}]
    failures += [f"{gate} is missing the part {p}" for p in contract["parts"] if p not in parts]
    for measure, count in MEASURES.items():
        if measure in contract:
            low, high, value = *contract[measure], count([text for _, _, text, _ in lines])
            if value < low:
                failures.append(f"{gate} has {value} {measure}, below the minimum of {low}")
            if value > high:
                failures.append(f"{gate} has {value} {measure}, above the maximum of {high}")
    return failures, f"{gate}: {len(lines)} lines, {len(cited)} claims, {len(parts)}/{len(contract['parts'])} parts"


def record_problems(run):
    problems = []
    for path, allowed in REQUIRED.items():
        value = run
        for key in path.split("."):
            if not isinstance(value, dict) or key not in value:
                problems.append(f"run.json is missing {path}")
                break
            value = value[key]
        else:
            if allowed and value not in allowed:
                problems.append(f"{path} is \"{value}\", expected one of {', '.join(allowed)}")
    return problems


def check(folder, gate, skill):
    run = json.loads(read_text(folder / "run.json"))
    problems = record_problems(run)
    if problems:
        return problems, []
    snapshot = flat(read_text(folder / "snapshot.md"))
    failures = VERDICT_RULES[run["verdict"]["decision"]](run)
    failures += [f"claim {c['id']}: quote not found in the Snapshot: \"{c['quote']}\""
                for c in run["claims"] if flat(c["quote"]) not in snapshot]
    drafts = {name: parse_draft(read_text(folder / "gates" / name / "draft.md")) for name in run["gates"]}
    used = {c for lines in drafts.values() for _, _, _, ids in lines for c in ids}
    failures += [f"claim {c['id']} is cited by no opened gate" for c in run["claims"] if c["id"] not in used]
    if gate and gate not in run["gates"]:
        return failures + [f"gate {gate} is not opened by run {run['id']}"], []
    stamps = []
    for name in [gate] if gate else list(run["gates"]):
        problems, stamp = check_gate(run, name, drafts[name], skill)
        failures += problems
        stamps += [stamp] if stamp else []
    stamps.append(f"run {run['id']}: {len(run['claims'])} claims verified")
    return failures, stamps


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check a run record against its gate contracts.")
    parser.add_argument("run", type=Path)
    parser.add_argument("gate", nargs="?")
    parser.add_argument("--skill", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    failures, stamps = check(args.run, args.gate, args.skill)
    for failure in failures:
        print(f"FAIL {failure}", file=sys.stderr)
    if failures:
        return 1
    for stamp in stamps:
        print(stamp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
