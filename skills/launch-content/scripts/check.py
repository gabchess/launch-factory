"""The Check: confirm one run record, or one gate of it, against its gate contract.

Usage: python check.py RUN_FOLDER [GATE] [--skill SKILL_FOLDER]

Exits 0 when every rule holds and 1 with one line per failure otherwise.
"""

import argparse
import html
import json
import re
import string
import sys
import unicodedata
from pathlib import Path
from typing import NamedTuple

CITATIONS = re.compile(r"(?: *\[[A-Za-z0-9_-]+(?: *, *[A-Za-z0-9_-]+)*\])+ *$")
CLAIM_ID = re.compile(r"[A-Za-z0-9_-]+")
PART = re.compile(r"<!-- part: ([a-z0-9-]+) -->")
HEADING = re.compile(r"##? ")
CONTRACT = re.compile(r"```json\s*\n(.*?)\n```", re.S)
MARKUP = re.compile(r"<!--.*?-->|<[^<>]*>", re.S)
WORD = re.compile(r"(?:(?<![^\W_])-(?=\d))?[^\W_]+(?:[.,'][^\W_]+)*%?")
NUMBER = re.compile(r"-?\d+(?:[.,]\d+)*%?")
GATE_NAME = re.compile(r"[a-z0-9-]+")
MINUS_SIGNS = str.maketrans(dict.fromkeys("\u02d7\u2010\u2011\u2012\u2013\u2014\u2015\u2212\u2796", "-"))
MIN_QUOTE_WORDS = 3

# Draft lines and quotes are plain text, a closed format: ASCII letters and digits, the Latin-1 letters
# (so other scripts and their look-alike letters fail), the space and this punctuation. Every other
# character fails, so the Check never has to guess how markup, entities or invisible characters render.
PLAIN = frozenset(string.ascii_letters + string.digits + " .,;:!?'\"()-/%$+"
                  + "".join(chr(c) for c in range(0xC0, 0x100) if c not in (0xD7, 0xF7)))

REQUIRED = {
    "id": (str, None),
    "mode": (str, None),
    "source.kind": (str, ("briefing", "pull_request")),
    "source.title": (str, None),
    "source.do_not_say": (list, None),
    "source.open_questions": (list, None),
    "verdict.decision": (str, ("ask", "skip", "write")),
    "claims": (list, None),
    "gates": (dict, None),
}
KINDS = {str: "text", list: "a list", dict: "an object"}

VERDICT_RULES = {
    "write": lambda run: [] if run["claims"] else ["verdict write has zero claims"],
    "skip": lambda run: shut(run),
    "ask": lambda run: shut(run) + ([] if run["source"]["open_questions"] else ["verdict ask lists no open questions"]),
}


class Line(NamedTuple):
    """One content line of a Draft, parsed once. Every Draft guard reads these fields and nothing else."""
    number: int
    part: str | None
    heading: str
    words: tuple[str, ...]
    claims: tuple[str, ...]
    problem: str | None


MEASURES = {
    "lines": lambda lines: len(lines),
    "words": lambda lines: sum(len(line.words) for line in lines),
    "chars": lambda lines: len(" ".join(word for line in lines for word in line.words)),
}


class Unreadable(Exception):
    pass


def not_plain(text):
    """The first character outside plain text, named by its code point, or None."""
    bad = next((c for c in text if c not in PLAIN), None)
    if bad is None:
        return None
    name = unicodedata.name(bad, "")
    return f"has the character U+{ord(bad):04X}{' ' + name if name else ''}, which plain text does not allow"


def plain_words(text):
    """Words of text already checked to be plain: only case is folded."""
    return tuple(WORD.findall(text.casefold()))


def source_words(text):
    """Words of untrusted source text: a Snapshot, Owner sources or a Do not say phrase.

    Each step turns markup into a space, so it can split a word but never join two words: every tag and
    comment becomes a space, entities are decoded, every format or control character becomes a space,
    then NFKC and casefold. A quote that depends on markup to match therefore fails closed. Minus signs
    and dashes are read as "-", so a number keeps its sign and a quote that drops it fails.
    """
    text = html.unescape(MARKUP.sub(" ", text)).translate(MINUS_SIGNS)
    text = "".join(" " if unicodedata.category(c) in ("Cf", "Cc") else c for c in text)
    return tuple(WORD.findall(unicodedata.normalize("NFKC", text).casefold()))


def find_run(haystack, needle):
    """Index where needle starts as a run of whole words in haystack, or -1."""
    size = len(needle)
    return next((i for i in range(len(haystack) - size + 1) if haystack[i:i + size] == needle), -1)


def shut(run):
    return [f"verdict {run['verdict']['decision']} opens gate {g}" for g in run["gates"]]


def read_text(path, missing):
    if not path.is_file():
        raise Unreadable(missing)
    try:
        return path.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        raise Unreadable(f"{path.name} is not UTF-8 text") from None


def read_json(text, invalid):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise Unreadable(invalid) from None


def parse_draft(text):
    lines, part = [], None
    for number, raw in enumerate(text.split("\n"), 1):
        line = raw.removesuffix("\r").strip(" ")
        marker = PART.fullmatch(line)
        if marker:
            part = marker.group(1)
        elif line:
            cited = CITATIONS.search(line)
            body = line[:cited.start()] if cited else line
            heading = HEADING.match(body)
            body = body[heading.end():] if heading else body
            lines.append(Line(number, part, heading.group(0) if heading else "", plain_words(body),
                              tuple(CLAIM_ID.findall(cited.group(0))) if cited else (), not_plain(body)))
    return lines


def numbers(words):
    """Each number with its label, the word after it when that word holds no digit."""
    pairs = []
    for i, word in enumerate(words):
        label = words[i + 1] if i + 1 < len(words) and not any(c.isdigit() for c in words[i + 1]) else None
        pairs += [(number, label) for number in NUMBER.findall(word)]
    return pairs


def number_failures(gate, line, quotes):
    claimed = {pair for c in line.claims for pair in numbers(quotes.get(c, ()))}
    failures = []
    for value, label in numbers(line.words):
        if value not in {v for v, _ in claimed}:
            failures.append(f"{gate} line {line.number}: number {value} is not in its cited claims {', '.join(line.claims)}")
        elif label and (value, label) not in claimed:
            failures.append(f"{gate} line {line.number}: number {value} {label} is not in its cited claims {', '.join(line.claims)}")
    return failures


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


def contract_shape_ok(contract):
    return (isinstance(contract, dict)
            and all(isinstance(contract.get(key), list) for key in ("parts", "uncited"))
            and all(isinstance(contract[m], list) and len(contract[m]) == 2
                    and all(isinstance(n, int) for n in contract[m]) for m in MEASURES if m in contract))


def check_gate(run, gate, lines, skill, quotes, banned, owner):
    path = skill / "gates" / f"{gate}.md"
    if not path.is_file():
        return [f"unknown gate {gate}: no contract gates/{gate}.md"], None
    block = CONTRACT.search(read_text(path, ""))
    invalid = f"contract gates/{gate}.md has no valid JSON block"
    contract = read_json(block.group(1) if block else "", invalid)
    if not contract_shape_ok(contract):
        raise Unreadable(f"contract gates/{gate}.md must list parts and uncited, and give each limit as two numbers")
    cited = {c for line in lines for c in line.claims}
    parts = [p for p in contract["parts"] if any(line.part == p for line in lines)]
    failures = [] if lines else [f"{gate} has zero lines"]
    failures += [] if cited else [f"{gate} cites zero claims"]
    failures += [f"{gate} line {line.number} {line.problem}" for line in lines if line.problem]
    failures += [f"{gate} line {line.number} is a heading, which {gate} does not allow"
                 for line in lines if line.heading and line.heading not in contract["uncited"]]
    failures += [f"{gate} line {line.number} has no words" for line in lines if not line.words]
    failures += [f"{gate} line {line.number} cites no claim: \"{' '.join(line.words)}\""
                 for line in lines if line.words and not line.claims and not line.heading]
    failures += [f"{gate} line {line.number} cites unknown claim {c}" for line in lines for c in line.claims if c not in quotes]
    failures += [f"{gate} line {line.number} cites claim {c}, an owner claim of gate {owner[c]}"
                 for line in lines for c in line.claims if owner.get(c, gate) != gate]
    failures += do_not_say(gate, lines, banned)
    failures += [failure for line in lines for failure in number_failures(gate, line, quotes)]
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
    for path, (kind, allowed) in REQUIRED.items():
        value = run
        for key in path.split("."):
            if not isinstance(value, dict) or key not in value:
                problems.append(f"run.json is missing {path}")
                break
            value = value[key]
        else:
            if not isinstance(value, kind):
                problems.append(f"{path} must be {KINDS[kind]}")
            elif allowed and value not in allowed:
                problems.append(f"{path} is \"{value}\", expected one of {', '.join(allowed)}")
    if problems:
        return problems
    source = run["source"]
    problems += [f"source.{field} must be a list of text" for field in ("do_not_say", "open_questions")
                 if not all(isinstance(item, str) for item in source[field])]
    for n, claim in enumerate(run["claims"], 1):
        if not (isinstance(claim, dict) and isinstance(claim.get("id"), str) and isinstance(claim.get("quote"), str)):
            problems.append(f"claim {n} must have a text id and quote")
        elif not isinstance(claim.get("gate", ""), str):
            problems.append(f"claim {n} gate must be text")
    for name, entry in run["gates"].items():
        if not isinstance(entry, dict):
            problems.append(f"gates.{name} must be an object")
        elif not isinstance(entry.get("owner_sources", ""), str):
            problems.append(f"gates.{name}.owner_sources must be text")
    return problems


def quote_failures(run, snapshot):
    """Each claim's quote is plain text of at least 3 words, found as a run of whole words in the Snapshot,
    or, for an owner claim, in the Owner sources of its one gate."""
    failures = []
    for claim in run["claims"]:
        cid, quote, gate = claim["id"], claim["quote"], claim.get("gate")
        problem = not_plain(quote)
        if problem:
            failures.append(f"claim {cid}: quote {problem}")
            continue
        words = plain_words(quote)
        if len(words) < MIN_QUOTE_WORDS:
            failures.append(f"claim {cid}: quote \"{quote}\" is shorter than {MIN_QUOTE_WORDS} words")
        if gate is None:
            if find_run(snapshot, words) < 0:
                failures.append(f"claim {cid}: quote not found in the Snapshot: \"{quote}\"")
        elif gate not in run["gates"]:
            failures.append(f"claim {cid} belongs to gate {gate}, which run {run['id']} does not open")
        elif find_run(source_words(run["gates"][gate].get("owner_sources", "")), words) < 0:
            failures.append(f"claim {cid}: quote not found in the Owner sources of gate {gate}: \"{quote}\"")
    return failures


def check(folder, gate, skill):
    run = read_json(read_text(folder / "run.json", "the run folder has no run.json"), "run.json is not valid JSON")
    problems = record_problems(run) or [f"gate name \"{name}\" is not a plain name"
        for name in [*run["gates"], *([gate] if gate else [])] if not GATE_NAME.fullmatch(name)]
    if problems:
        return problems, []
    banned = {phrase: source_words(phrase) for phrase in run["source"]["do_not_say"]}
    empty = [f"Do not say phrase \"{phrase}\" has no words" for phrase, key in banned.items() if not key]
    if empty:
        return empty, []
    snapshot = source_words(read_text(folder / "snapshot.md", f"run {run['id']} has no snapshot.md"))
    ids = [c["id"] for c in run["claims"]]
    twice = sorted({i for i in ids if ids.count(i) > 1})
    if twice:
        return [f"claim id {i} is used by {ids.count(i)} claims" for i in twice], []
    quotes = {c["id"]: plain_words(c["quote"]) for c in run["claims"]}
    owner = {c["id"]: c["gate"] for c in run["claims"] if "gate" in c}
    failures = VERDICT_RULES[run["verdict"]["decision"]](run) + quote_failures(run, snapshot)
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
        problems, stamp = check_gate(run, name, drafts[name], skill, quotes, banned, owner)
        failures += problems
        stamps += [stamp] if stamp else []
    stamps.append(f"run {run['id']}: {len(run['claims'])} claims verified")
    return failures, stamps


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
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
