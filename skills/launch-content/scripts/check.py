"""The Check: confirm one run record, or one gate of it, against its gate contract.

Usage: python check.py RUN_FOLDER [GATE] [--skill SKILL_FOLDER]

Exits 0 when every rule holds and 1 with one line per failure otherwise.
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import NamedTuple

CITATIONS = re.compile(r"(?:\s*\[[A-Za-z0-9_-]+(?:\s*,\s*[A-Za-z0-9_-]+)*\])+\s*$")
CLAIM_ID = re.compile(r"[A-Za-z0-9_-]+")
PART = re.compile(r"^<!--\s*part:\s*([A-Za-z0-9_-]+)\s*-->$")
MARK = re.compile(r"#{1,6} |[-*+>] ")
CONTRACT = re.compile(r"```json\s*\n(.*?)\n```", re.S)
MARKUP = re.compile(r"<!--.*?-->|<[^<>\n]*>", re.S)
MINUS = str.maketrans({c: "-" for c in "\u2010\u2011\u2012\u2013\u2014\u2015\u2212\u2796\ufe58"})
WORD = re.compile(r"(?:(?<![^\W_])-(?=\d))?[^\W_]+(?:[.,'][^\W_]+)*")
NUMBER = re.compile(r"-?\d+(?:[.,]\d+)*")
GATE_NAME = re.compile(r"[a-z0-9-]+")
MIN_QUOTE_WORDS = 3

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

VERDICT_RULES = {
    "write": lambda run: [] if run["claims"] else ["verdict write has zero claims"],
    "skip": lambda run: shut(run),
    "ask": lambda run: shut(run) + ([] if run["source"]["open_questions"] else ["verdict ask lists no open questions"]),
}


class Line(NamedTuple):
    """One content line of a Draft, parsed once. Every Draft guard reads these fields and nothing else."""
    number: int
    part: str | None
    mark: str
    words: tuple[str, ...]
    claims: tuple[str, ...]


MEASURES = {
    "lines": lambda lines: len(lines),
    "words": lambda lines: sum(len(line.words) for line in lines),
    "chars": lambda lines: len(" ".join(word for line in lines for word in line.words)),
}


class Unreadable(Exception):
    pass


def words(text):
    """The reader's words: Unicode NFKC, minus signs as "-", markup and other symbols dropped, lowercased."""
    text = unicodedata.normalize("NFKC", text).translate(MINUS)
    return tuple(WORD.findall(MARKUP.sub(" ", text).casefold()))


def find_run(haystack, needle):
    """Index where needle starts as a run of whole words in haystack, or -1."""
    size = len(needle)
    return next((i for i in range(len(haystack) - size + 1) if haystack[i:i + size] == needle), -1)


def shut(run):
    return [f"verdict {run['verdict']['decision']} opens gate {g}" for g in run["gates"]]


def read_text(path, missing):
    if not path.is_file():
        raise Unreadable(missing)
    return path.read_bytes().decode("utf-8")


def read_json(text, invalid):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise Unreadable(invalid) from None


def parse_draft(text):
    lines, part = [], None
    for number, raw in enumerate(text.split("\n"), 1):
        line = raw.strip()
        marker = PART.match(line)
        if marker:
            part = marker.group(1)
        elif line:
            cited = CITATIONS.search(line)
            body = line[:cited.start()] if cited else line
            mark = MARK.match(body)
            lines.append(Line(number, part, mark.group(0) if mark else "", words(body),
                              tuple(CLAIM_ID.findall(cited.group(0))) if cited else ()))
    return lines


def numbers(line_words):
    return [n for word in line_words for n in NUMBER.findall(word)]


def do_not_say(gate, lines, banned):
    stream = [(line.number, word) for line in lines for word in line.words]
    failures = []
    for phrase, phrase_words in banned.items():
        start = find_run(tuple(word for _, word in stream), phrase_words)
        if start >= 0:
            first, last = stream[start][0], stream[start + len(phrase_words) - 1][0]
            where = f"line {first} contains" if first == last else f"lines {first} to {last} contain"
            failures.append(f"{gate} {where} the Do not say phrase \"{phrase}\"")
    return failures


def check_gate(run, gate, lines, skill, quotes, banned):
    path = skill / "gates" / f"{gate}.md"
    if not path.is_file():
        return [f"unknown gate {gate}: no contract gates/{gate}.md"], None
    block = CONTRACT.search(read_text(path, ""))
    invalid = f"contract gates/{gate}.md has no valid JSON block"
    contract = read_json(block.group(1) if block else "", invalid)
    cited = {c for line in lines for c in line.claims}
    parts = [p for p in contract["parts"] if any(line.part == p for line in lines)]
    failures = [] if lines else [f"{gate} has zero lines"]
    failures += [] if cited else [f"{gate} cites zero claims"]
    failures += [f"{gate} line {line.number} has no words" for line in lines if not line.words]
    failures += [f"{gate} line {line.number} cites no claim: \"{' '.join(line.words)}\""
                 for line in lines if line.words and not line.claims and line.mark not in contract["uncited"]]
    failures += [f"{gate} line {line.number} cites unknown claim {c}" for line in lines for c in line.claims if c not in quotes]
    failures += do_not_say(gate, lines, banned)
    failures += [f"{gate} line {line.number}: number {number} is not in its cited claims {', '.join(line.claims)}"
                 for line in lines for number in numbers(line.words)
                 if number not in {n for c in line.claims for n in numbers(quotes.get(c, ()))}]
    failures += [f"{gate} is missing the part {p}" for p in contract["parts"] if p not in parts]
    for measure, count in MEASURES.items():
        if measure in contract:
            low, high, value = *contract[measure], count(lines)
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
    run = read_json(read_text(folder / "run.json", "the run folder has no run.json"), "run.json is not valid JSON")
    problems = record_problems(run) or [f"gate name \"{name}\" is not a plain name"
        for name in [*run["gates"], *([gate] if gate else [])] if not GATE_NAME.fullmatch(name)]
    if problems:
        return problems, []
    banned = {phrase: words(phrase) for phrase in run["source"]["do_not_say"]}
    empty = [f"Do not say phrase \"{phrase}\" has no words" for phrase, key in banned.items() if not key]
    if empty:
        return empty, []
    snapshot = words(read_text(folder / "snapshot.md", f"run {run['id']} has no snapshot.md"))
    quotes = {c["id"]: words(c["quote"]) for c in run["claims"]}
    failures = VERDICT_RULES[run["verdict"]["decision"]](run)
    failures += [f"claim {c['id']}: quote \"{c['quote']}\" is shorter than {MIN_QUOTE_WORDS} words"
                 for c in run["claims"] if len(quotes[c["id"]]) < MIN_QUOTE_WORDS]
    failures += [f"claim {c['id']}: quote not found in the Snapshot: \"{c['quote']}\""
                 for c in run["claims"] if find_run(snapshot, quotes[c["id"]]) < 0]
    missing = [f"gate {name} has no draft.md" for name in run["gates"]
               if not (folder / "gates" / name / "draft.md").is_file()]
    if missing:
        return failures + missing, []
    drafts = {name: parse_draft(read_text(folder / "gates" / name / "draft.md", "")) for name in run["gates"]}
    used = {c for lines in drafts.values() for line in lines for c in line.claims}
    failures += [f"claim {c['id']} is cited by no opened gate" for c in run["claims"] if c["id"] not in used]
    if gate and gate not in run["gates"]:
        return failures + [f"gate {gate} is not opened by run {run['id']}"], []
    stamps = []
    for name in [gate] if gate else list(run["gates"]):
        problems, stamp = check_gate(run, name, drafts[name], skill, quotes, banned)
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
    try:
        failures, stamps = check(args.run, args.gate, args.skill)
    except Unreadable as problem:
        failures, stamps = [str(problem)], []
    for failure in failures:
        print(f"FAIL {failure}", file=sys.stderr)
    if failures:
        return 1
    for stamp in stamps:
        print(stamp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
