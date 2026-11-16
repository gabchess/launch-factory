"""The Check, driven as a command: a run record and a gate in, an exit code and a message out."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "skills/launch-content/scripts/check.py"
FIXTURES = ROOT / "tests/fixtures/check"


def check(record, gate=None):
    args = [sys.executable, str(CHECK), str(FIXTURES / "records" / record)]
    if gate:
        args.append(gate)
    args += ["--skill", str(FIXTURES / "skill")]
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8")


def test_windows_line_endings_pass():
    assert b"\r\n" in (FIXTURES / "records/crlf/snapshot.md").read_bytes(), "git converted the fixture"
    result = check("crlf", "test-post")
    assert result.returncode == 0, result.stderr
    assert "test-post: 4 lines, 3 claims, 3/3 parts" in result.stdout


def test_good_records_pass_and_print_counts():
    result = check("good-pr")
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        "test-post: 4 lines, 3 claims, 3/3 parts",
        "test-card: 2 lines, 2 claims, 2/2 parts",
        "run pr-csv: 3 claims verified",
    ]
    result = check("good-briefing", "test-card")
    assert result.returncode == 0, result.stderr
    assert "test-card: 2 lines, 3 claims, 2/2 parts" in result.stdout


def test_an_owner_claim_whose_quote_is_in_owner_sources_passes():
    result = check("owner-claim")
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        "test-post: 5 lines, 4 claims, 3/3 parts",
        "test-card: 2 lines, 2 claims, 2/2 parts",
        "run pr-csv-owner: 4 claims verified",
    ]


def test_naming_a_gate_counts_claims_cited_only_by_another_gate():
    result = check("good-pr", "test-card")
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == ["test-card: 2 lines, 2 claims, 2/2 parts", "run pr-csv: 3 claims verified"]


def test_skip_and_ask_open_no_gate_and_pass():
    for record, run_id in (("skip", "pr-refactor"), ("ask", "brief-dashboards")):
        result = check(record)
        assert result.returncode == 0, result.stderr
        assert result.stdout.splitlines() == [f"run {run_id}: 0 claims verified"]


BAD = [
    ("quote-changed", None, 'claim c2: quote not found in the Snapshot: "The export keeps the filters the user chose."'),
    ("line-no-claim", "test-post", 'test-post line 7 cites no claim: "it is the fastest export on the market"'),
    ("claim-unused", None, "claim c4 is cited by no opened gate"),
    ("write-zero-claims", None, "verdict write has zero claims"),
    ("write-zero-claims", "test-post", "test-post line 5 cites unknown claim c1"),
    ("missing-field", None, "run.json is missing source.kind"),
    ("do-not-say", None, "test-post line 5 contains the Do not say phrase \"export   MENU\""),
    ("missing-part", "test-post", "test-post is missing the part proof"),
    ("too-short", "test-post", "test-post has 3 lines, below the minimum of 4"),
    ("too-long", "test-post", "test-post has 9 lines, above the maximum of 8"),
    ("too-long", "test-post", "test-post has 137 words, above the maximum of 120"),
    ("too-long", "test-card", "test-card has 416 chars, above the maximum of 280"),
    ("unknown-gate", None, "unknown gate test-video: no contract gates/test-video.md"),
    ("skip", "test-post", "gate test-post is not opened by run pr-refactor"),
    ("number-differs", "test-card", "test-card line 4: number 5000 is not in its cited claims c1, c3"),
    ("draft-zero-lines", "test-card", "test-card has zero lines"),
    ("draft-zero-claims", "test-post", "test-post cites zero claims"),
    ("ask-no-questions", None, "verdict ask lists no open questions"),
    ("skip-opens-gate", None, "verdict skip opens gate test-card"),
    ("ask-opens-gate", None, "verdict ask opens gate test-card"),
    ("unknown-values", None, "verdict.decision is \"publish\", expected one of ask, skip, write"),
    ("unknown-values", None, "source.kind is \"email\", expected one of briefing, pull_request"),
    ("number-uncited", "test-card", "test-card line 4: number 50000 is not in its cited claims c1"),
    ("claim-unused", "test-post", "claim c4 is cited by no opened gate"),
    ("quote-empty", None, 'claim c2: quote "   " is shorter than 3 words'),
    ("line-only-citation", "test-card", "test-card line 2 has no words"),
    ("do-not-say-split", None, "test-post lines 5 to 6 contain the Do not say phrase \"export   MENU\""),
    ("do-not-say-split", None, "test-post lines 5 to 6 contain the Do not say phrase \"the export menu\""),
    ("number-sign", "test-post", "test-post line 9: number -10 is not in its cited claims c3"),
    ("draft-missing", None, "gate test-card has no draft.md"),
    ("gate-name", None, "gate name \"../x\" is not a plain name"),
    ("good-pr", "../x", "gate name \"../x\" is not a plain name"),
    ("missing-gates", None, "run.json is missing gates"),
    ("owner-claim-not-in-sources", None,
     'claim c4: quote not found in the Owner sources of gate test-post: "Exports also run on a schedule every night."'),
]


@pytest.mark.parametrize("record, gate, message", BAD, ids=[row[0] for row in BAD])
def test_bad_record_fails_naming_the_problem(record, gate, message):
    result = check(record, gate)
    assert result.returncode == 1
    assert f"FAIL {message}" in result.stderr.splitlines()
    assert result.stdout == ""


def test_do_not_say_on_one_line_is_reported_once():
    result = check("do-not-say")
    assert result.stderr.splitlines() == ['FAIL test-post line 5 contains the Do not say phrase "export   MENU"']


GOOD_CARD = "<!-- part: problem -->\n{problem}\n<!-- part: change -->\nEvery report exports as CSV, up to 50000 rows in under 10 seconds. [c1, c3]\n"


def variant(tmp_path, card=None, post=None, quotes=None, do_not_say=None):
    """A copy of good-pr with one change, so each case shows the one input that must fail."""
    folder = tmp_path / "run"
    shutil.copytree(FIXTURES / "records/good-pr", folder)
    if card is not None:
        (folder / "gates/test-card/draft.md").write_bytes(GOOD_CARD.format(problem=card).encode("utf-8"))
    if post:
        path = folder / "gates/test-post/draft.md"
        old, new = post
        text = path.read_bytes().decode("utf-8")
        assert old in text
        path.write_bytes(text.replace(old, new).encode("utf-8"))
    run = json.loads((folder / "run.json").read_text("utf-8"))
    for claim in run["claims"]:
        claim["quote"] = (quotes or {}).get(claim["id"], claim["quote"])
    if do_not_say is not None:
        run["source"]["do_not_say"] = do_not_say
    (folder / "run.json").write_text(json.dumps(run, ensure_ascii=False), "utf-8")
    return folder


def run_check(folder, gate=None):
    args = [sys.executable, str(CHECK), str(folder), *([gate] if gate else []), "--skill", str(FIXTURES / "skill")]
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8")


def test_a_variant_with_no_change_passes(tmp_path):
    result = run_check(variant(tmp_path))
    assert result.returncode == 0, result.stderr


WORDLESS = {
    "two-citations": "[c1] [c1]",
    "adjacent-citations": "[c1][c3]",
    "dash": "- [c1]",
    "dot": ". [c1]",
    "punctuation": "( ) ; : ! ? [c1]",
}


@pytest.mark.parametrize("problem", WORDLESS.values(), ids=WORDLESS.keys())
def test_a_line_with_no_words_fails(tmp_path, problem):
    result = run_check(variant(tmp_path, card=problem))
    assert result.returncode == 1
    assert "FAIL test-card line 2 has no words" in result.stderr.splitlines()


SHORT_QUOTES = {"one-char": "e", "dot": ".", "two-words": "user picked", "symbols": "-- !! ??"}


@pytest.mark.parametrize("quote", SHORT_QUOTES.values(), ids=SHORT_QUOTES.keys())
def test_a_quote_shorter_than_three_words_fails_naming_the_claim(tmp_path, quote):
    result = run_check(variant(tmp_path, quotes={"c2": quote}))
    assert result.returncode == 1
    assert f'FAIL claim c2: quote "{quote}" is shorter than 3 words' in result.stderr.splitlines()


def test_a_quote_must_match_whole_snapshot_words(tmp_path):
    result = run_check(variant(tmp_path, quotes={"c2": "xport keeps the filters"}))
    assert 'FAIL claim c2: quote not found in the Snapshot: "xport keeps the filters"' in result.stderr.splitlines()


def test_a_quote_matches_across_case_and_snapshot_line_breaks(tmp_path):
    result = run_check(variant(tmp_path, quotes={"c3": "Exports UP to 50000 rows finish in under 10 seconds in our TESTS"}))
    assert result.returncode == 0, result.stderr


def test_a_quote_with_its_words_reordered_fails(tmp_path):
    quote = "the user picked the export keeps the filters"
    result = run_check(variant(tmp_path, quotes={"c2": quote}))
    assert f'FAIL claim c2: quote not found in the Snapshot: "{quote}"' in result.stderr.splitlines()


def test_a_quote_outside_plain_text_fails_naming_the_character(tmp_path):
    result = run_check(variant(tmp_path, quotes={"c2": "The **filters**"}))
    assert result.returncode == 1
    assert result.stderr.splitlines() == ["FAIL claim c2: quote has the character U+002A ASTERISK, which plain text does not allow"]


def test_a_number_with_a_minus_sign_is_checked_with_its_sign(tmp_path):
    result = run_check(variant(tmp_path, post=("under 10 seconds", "under -10 seconds")), "test-post")
    assert "FAIL test-post line 9: number -10 is not in its cited claims c3" in result.stderr.splitlines()


def test_a_range_is_two_numbers_without_signs(tmp_path):
    result = run_check(variant(tmp_path, post=("under 10 seconds", "under 10-10 seconds")), "test-post")
    assert result.returncode == 0, result.stderr


def test_a_number_must_carry_the_label_of_its_cited_claim(tmp_path):
    result = run_check(variant(tmp_path, post=("under 10 seconds", "under 10 minutes")), "test-post")
    assert "FAIL test-post line 9: number 10 minutes is not in its cited claims c3" in result.stderr.splitlines()


def test_a_percent_sign_is_part_of_the_number(tmp_path):
    result = run_check(variant(tmp_path, post=("under 10 seconds", "under 10% seconds")), "test-post")
    assert "FAIL test-post line 9: number 10% is not in its cited claims c3" in result.stderr.splitlines()


def test_a_decimal_is_one_number(tmp_path):
    result = run_check(variant(tmp_path, post=("under 10 seconds", "under 10.50000 seconds")), "test-post")
    assert "FAIL test-post line 9: number 10.50000 is not in its cited claims c3" in result.stderr.splitlines()


def test_a_claim_id_used_twice_fails(tmp_path):
    folder = variant(tmp_path)
    run = json.loads((folder / "run.json").read_text("utf-8"))
    run["claims"].insert(0, {"id": "c2", "quote": "This quote is completely fabricated."})
    (folder / "run.json").write_text(json.dumps(run), "utf-8")
    result = run_check(folder)
    assert result.returncode == 1
    assert "FAIL claim id c2 is used by 2 claims" in result.stderr.splitlines()


def test_a_run_json_that_is_not_utf8_fails_with_a_fail_line(tmp_path):
    folder = variant(tmp_path)
    (folder / "run.json").write_bytes(b'{"id": "\xff"}')
    result = run_check(folder)
    assert result.returncode == 1
    assert result.stderr.splitlines() == ["FAIL run.json is not UTF-8 text"]


WRONG_TYPES = {
    "gates-null": (("gates",), None, "gates must be an object"),
    "claims-object": (("claims",), {}, "claims must be a list"),
    "claim-no-quote": (("claims",), [{"id": "c1"}], "claim 1 must have a text id and quote"),
    "claim-number-id": (("claims",), [{"id": 1, "quote": "Any report now exports as CSV"}], "claim 1 must have a text id and quote"),
    "do-not-say-null": (("source", "do_not_say"), None, "source.do_not_say must be a list"),
    "do-not-say-number":(("source", "do_not_say"), [3], "source.do_not_say must be a list of text"),
    "decision-list": (("verdict", "decision"), ["write"], "verdict.decision must be text"),
    "open-questions-number": (("source", "open_questions"), [1], "source.open_questions must be a list of text"),
    "claim-gate-number": (("claims",), [{"id": "c1", "quote": "Any report now exports as CSV", "gate": 1}], "claim 1 gate must be text"),
    "owner-sources-number": (("gates", "test-post", "owner_sources"), 1, "gates.test-post.owner_sources must be text"),
    "gate-entry-list": (("gates", "test-post"), [], "gates.test-post must be an object"),
}


@pytest.mark.parametrize("keys, value, message", WRONG_TYPES.values(), ids=WRONG_TYPES.keys())
def test_a_field_of_the_wrong_type_fails_with_a_fail_line(tmp_path, keys, value, message):
    folder = variant(tmp_path)
    run = json.loads((folder / "run.json").read_text("utf-8"))
    parent = run
    for key in keys[:-1]:
        parent = parent[key]
    parent[keys[-1]] = value
    (folder / "run.json").write_text(json.dumps(run), "utf-8")
    result = run_check(folder)
    assert result.returncode == 1
    assert f"FAIL {message}" in result.stderr.splitlines()
    assert "Traceback" not in result.stderr


def test_a_number_glued_to_a_word_is_still_checked(tmp_path):
    result = run_check(variant(tmp_path, post=("50000 rows", "50001rows")), "test-post")
    assert "FAIL test-post line 9: number 50001 is not in its cited claims c3" in result.stderr.splitlines()


def test_a_hyphen_does_not_hide_a_do_not_say_phrase(tmp_path):
    result = run_check(variant(tmp_path, post=("filters you picked.", "filters you picked at the beta-price.")))
    assert 'FAIL test-post line 6 contains the Do not say phrase "beta price"' in result.stderr.splitlines()


@pytest.mark.parametrize("draft, phrase", [("stra\u00dfe", "strasse"), ("strasse", "Stra\u00dfe")], ids=["in-draft", "in-phrase"])
def test_a_do_not_say_phrase_matches_a_casefolded_word(tmp_path, draft, phrase):
    result = run_check(variant(tmp_path, post=("filters you picked.", f"filters you picked at the {draft}."), do_not_say=[phrase]))
    assert f'FAIL test-post line 6 contains the Do not say phrase "{phrase}"' in result.stderr.splitlines()


def test_a_do_not_say_phrase_with_markup_is_read_as_source_text(tmp_path):
    result = run_check(variant(tmp_path, post=("filters you picked.", "filters you picked at the beta price."), do_not_say=["beta&nbsp;price"]))
    assert 'FAIL test-post line 6 contains the Do not say phrase "beta&nbsp;price"' in result.stderr.splitlines()


# Each input shows a reader something other than its plain characters. The closed format fails the line
# and names the first character outside plain text: (gate, line, text to replace), new text, character.
POST = ("test-post", 6, "filters you picked.")
NUMBER = ("test-post", 9, "under 10 seconds")
ROWS = ("test-post", 9, "50000 rows")
CARD = ("test-card", 2, None)
NOT_PLAIN = {
    "dns-br": (POST, "filters you picked at the beta<br>price.", "U+003C LESS-THAN SIGN"),
    "dns-p-tags": (POST, "filters you picked at the <p>beta</p><p>price</p>.", "U+003C LESS-THAN SIGN"),
    "dns-nbsp-entity": (POST, "filters you picked at the beta&nbsp;price.", "U+0026 AMPERSAND"),
    "dns-shy-entity": (POST, "filters you picked at the beta pri&shy;ce.", "U+0026 AMPERSAND"),
    "dns-entity-letter": (POST, "filters you picked at the beta pri&#99;e.", "U+0026 AMPERSAND"),
    "dns-soft-hyphen": (POST, "filters you picked at the beta pri\u00adce.", "U+00AD SOFT HYPHEN"),
    "dns-zero-width-space": (POST, "filters you picked at the beta pri\u200bce.", "U+200B ZERO WIDTH SPACE"),
    "dns-zero-width-joiner": (POST, "filters you picked at the beta pri\u200dce.", "U+200D ZERO WIDTH JOINER"),
    "dns-word-joiner": (POST, "filters you picked at the beta pri\u2060ce.", "U+2060 WORD JOINER"),
    "dns-byte-order-mark": (POST, "filters you picked at the beta pri\ufeffce.", "U+FEFF ZERO WIDTH NO-BREAK SPACE"),
    "dns-combining-joiner": (POST, "filters you picked at the beta pri\u034fce.", "U+034F COMBINING GRAPHEME JOINER"),
    "dns-emphasis": (POST, "filters you picked at the beta **price**.", "U+002A ASTERISK"),
    "dns-underscore-emphasis": (POST, "filters you picked at the beta __price__.", "U+005F LOW LINE"),
    "dns-strike": (POST, "filters you picked at the beta pri~~ce~~.", "U+007E TILDE"),
    "dns-code": (POST, "filters you picked at the beta pri`ce`.", "U+0060 GRAVE ACCENT"),
    "dns-html-comment": (POST, "filters you picked at the beta <!-- x --> price.", "U+003C LESS-THAN SIGN"),
    "dns-link": (POST, "filters you picked at the [beta price](http://x).", "U+005B LEFT SQUARE BRACKET"),
    "dns-backslash": (POST, "filters you picked at the beta pri\\ce.", "U+005C REVERSE SOLIDUS"),
    "dns-cyrillic-e": (POST, "filters you picked at the b\u0435ta price.", "U+0435 CYRILLIC SMALL LETTER IE"),
    "dns-fullwidth": (POST, "filters you picked at the \uff42eta price.", "U+FF42 FULLWIDTH LATIN SMALL LETTER B"),
    "num-unicode-minus": (NUMBER, "under \u221210 seconds", "U+2212 MINUS SIGN"),
    "num-modifier-minus": (NUMBER, "under \u02d710 seconds", "U+02D7 MODIFIER LETTER MINUS SIGN"),
    "num-minus-entity": (NUMBER, "under &minus;10 seconds", "U+0026 AMPERSAND"),
    "num-soft-hyphen-split": (NUMBER, "under 1\u00ad0 seconds", "U+00AD SOFT HYPHEN"),
    "num-zero-width-split": (ROWS, "500\u200b00 rows", "U+200B ZERO WIDTH SPACE"),
    "num-tag-join": (ROWS, "5<b></b>0000 rows", "U+003C LESS-THAN SIGN"),
    "num-br-split": (NUMBER, "under 1<br>0 seconds", "U+003C LESS-THAN SIGN"),
    "num-superscript": (NUMBER, "under 10\u00b2 seconds", "U+00B2 SUPERSCRIPT TWO"),
    "num-fraction": (NUMBER, "under 10\u00bd seconds", "U+00BD VULGAR FRACTION ONE HALF"),
    "num-times": (NUMBER, "under 10\u00d7 seconds", "U+00D7 MULTIPLICATION SIGN"),
    "heading-text": (("test-post", 2, "# CSV export for every report"), "# CSV export for **every** report", "U+002A ASTERISK"),
    "line-only-nbsp": (CARD, "&nbsp; [c1]", "U+0026 AMPERSAND"),
    "line-only-soft-hyphen": (CARD, "\u00ad [c1]", "U+00AD SOFT HYPHEN"),
    "line-only-br": (CARD, "<br> [c1]", "U+003C LESS-THAN SIGN"),
    "line-only-image": (CARD, "![](x.png) [c1]", "U+005B LEFT SQUARE BRACKET"),
    "line-only-tags": (CARD, "<b></b> [c1]", "U+003C LESS-THAN SIGN"),
    "line-only-emphasis": (CARD, "** __ [c1]", "U+002A ASTERISK"),
    "line-tab": (CARD, "Getting report numbers\tby hand. [c1]", "U+0009"),
    "line-leading-tab": (CARD, "\tGetting report numbers by hand. [c1]", "U+0009"),
    "nbsp-before-citation": (CARD, "Getting report numbers by hand.\u00a0[c1]", "U+00A0 NO-BREAK SPACE"),
    "part-marker-trailing": (CARD, "<!-- part: change --> by hand. [c1]", "U+003C LESS-THAN SIGN"),
    "part-marker-in-text": (CARD, "Getting report numbers <!-- part: change --> by hand. [c1]", "U+003C LESS-THAN SIGN"),
    "part-marker-loose": (CARD, "<!--part: change-->", "U+003C LESS-THAN SIGN"),
    "deep-heading": (CARD, "### Getting report numbers by hand. [c1]", "U+0023 NUMBER SIGN"),
    "micro-sign": (CARD, "Getting report numbers in \u00b5s by hand. [c1]", "U+00B5 MICRO SIGN"),
}


@pytest.mark.parametrize("where, text, character", NOT_PLAIN.values(), ids=NOT_PLAIN.keys())
def test_a_draft_line_outside_plain_text_fails_naming_the_character(tmp_path, where, text, character):
    gate, line, old = where
    folder = variant(tmp_path, card=text) if old is None else variant(tmp_path, post=(old, text))
    result = run_check(folder)
    assert result.returncode == 1
    assert f"FAIL {gate} line {line} has the character {character}, which plain text does not allow" in result.stderr.splitlines()


def test_latin1_letters_and_plain_punctuation_pass(tmp_path):
    text = "filters you picked (caf\u00e9, na\u00efve: yes; 'ok' \"ok\" / $ + ! ?)."
    result = run_check(variant(tmp_path, post=("filters you picked.", text)))
    assert result.returncode == 0, result.stderr


def test_an_uncited_bullet_line_fails(tmp_path):
    result = run_check(variant(tmp_path, card="- Getting report numbers into a sheet meant copying them by hand."))
    assert 'FAIL test-card line 2 cites no claim: "getting report numbers into a sheet meant copying them by hand"' in result.stderr.splitlines()


def test_a_heading_fails_where_the_contract_does_not_exempt_headings(tmp_path):
    result = run_check(variant(tmp_path, card="# Getting report numbers by hand [c1]"))
    assert "FAIL test-card line 2 is a heading, which test-card does not allow" in result.stderr.splitlines()


def test_a_draft_exactly_at_its_maximum_passes(tmp_path):
    lines = "Getting report numbers meant copying them by hand. [c1]\nAny report now exports as CSV. [c1]\nThe export keeps the filters. [c2]"
    result = run_check(variant(tmp_path, card=lines), "test-card")
    assert result.returncode == 0, result.stderr
    assert "test-card: 4 lines, 3 claims, 2/2 parts" in result.stdout


def snapshot_variant(tmp_path, old, new, quotes):
    folder = variant(tmp_path, quotes=quotes)
    path = folder / "snapshot.md"
    text = path.read_bytes().decode("utf-8")
    assert old in text
    path.write_bytes(text.replace(old, new).encode("utf-8"))
    return folder


SNAPSHOT_FAILS = {
    "entity-read-as-a-word": ("the user picked", "the user&nbsp;picked", "the user nbsp picked"),
    "tag-joins-nothing": ("the filters", "the<br>filters", "keeps thefilters the"),
    "zero-width-splits": ("the filters", "the fil\u200bters", "keeps the filters"),
    "comment-holding-a-bracket": ("# Add CSV export", "# Add CSV export\n<!-- x > a hidden claim text -->", "a hidden claim text"),
    "tag-attribute-across-lines": ("the filters", 'the <span\nclass="launch ready">filters</span>', "class launch ready"),
    "comment-hides-words": ("# Add CSV export", "# Add CSV export\n<!-- a hidden\nclaim text -->", "a hidden claim text"),
}


@pytest.mark.parametrize("old, new, quote", SNAPSHOT_FAILS.values(), ids=SNAPSHOT_FAILS.keys())
def test_snapshot_markup_can_split_words_but_never_join_them(tmp_path, old, new, quote):
    result = run_check(snapshot_variant(tmp_path, old, new, {"c2": quote}))
    assert f'FAIL claim c2: quote not found in the Snapshot: "{quote}"' in result.stderr.splitlines()


SNAPSHOT_PASSES = {
    "entity-is-a-space": ("the user picked", "the user&nbsp;picked", "the user picked"),
    "tag-is-a-space": ("the filters", "the<br>filters", "keeps the filters the"),
    "emphasis-around-words": ("the filters", "the **filters**", "keeps the filters the"),
    "fullwidth": ("keeps", "\uff4beeps", "export keeps the filters"),
    "tag-across-lines": ("the filters", 'the <span\nclass="x">filters</span>', "keeps the filters the"),
    "escaped-tag-is-text": ("the filters", "the &lt;filters&gt;", "keeps the filters the"),
}


@pytest.mark.parametrize("old, new, quote", SNAPSHOT_PASSES.values(), ids=SNAPSHOT_PASSES.keys())
def test_a_quote_matches_a_snapshot_after_markup_becomes_spaces(tmp_path, old, new, quote):
    result = run_check(snapshot_variant(tmp_path, old, new, {"c2": quote}))
    assert result.returncode == 0, result.stderr


def owner_variant(tmp_path, edit):
    folder = tmp_path / "run"
    shutil.copytree(FIXTURES / "records/owner-claim", folder)
    run = json.loads((folder / "run.json").read_text("utf-8"))
    edit(run, folder)
    (folder / "run.json").write_text(json.dumps(run), "utf-8")
    return folder


def test_owner_sources_are_read_as_source_text(tmp_path):
    def edit(run, folder):
        run["gates"]["test-post"]["owner_sources"] = "Release notes: Exports also<br><b>run</b> on a schedule every night."
    result = run_check(owner_variant(tmp_path, edit))
    assert result.returncode == 0, result.stderr


def test_an_owner_claim_cited_by_another_gate_fails(tmp_path):
    def edit(run, folder):
        path = folder / "gates/test-card/draft.md"
        path.write_bytes(path.read_bytes().replace(b"[c1, c3]", b"[c1, c3, c4]"))
    result = run_check(owner_variant(tmp_path, edit))
    assert "FAIL test-card line 4 cites claim c4, an owner claim of gate test-post" in result.stderr.splitlines()


def test_an_owner_claim_of_a_gate_the_run_does_not_open_fails(tmp_path):
    result = run_check(owner_variant(tmp_path, lambda run, folder: run["claims"][3].__setitem__("gate", "test-video")))
    assert "FAIL claim c4 belongs to gate test-video, which run pr-csv-owner does not open" in result.stderr.splitlines()


def test_an_owner_claim_quote_found_only_in_the_snapshot_fails(tmp_path):
    def edit(run, folder):
        run["claims"][3]["quote"] = "The export keeps the filters the user picked."
    result = run_check(owner_variant(tmp_path, edit))
    message = 'claim c4: quote not found in the Owner sources of gate test-post: "The export keeps the filters the user picked."'
    assert f"FAIL {message}" in result.stderr.splitlines()


def test_a_do_not_say_phrase_with_no_words_fails(tmp_path):
    result = run_check(variant(tmp_path, do_not_say=["   "]))
    assert result.stderr.splitlines() == ['FAIL Do not say phrase "   " has no words']


def test_a_gate_name_with_a_plain_prefix_is_still_rejected():
    result = check("good-pr", "test-card/../x")
    assert result.returncode == 1
    assert 'FAIL gate name "test-card/../x" is not a plain name' in result.stderr.splitlines()


def test_a_missing_snapshot_fails_with_a_fail_line(tmp_path):
    folder = variant(tmp_path)
    (folder / "snapshot.md").unlink()
    result = run_check(folder)
    assert result.returncode == 1
    assert result.stderr.splitlines() == ["FAIL run pr-csv has no snapshot.md"]


@pytest.mark.parametrize("content", ["{not json", ""], ids=["broken", "empty"])
def test_an_invalid_run_json_fails_with_a_fail_line(tmp_path, content):
    folder = variant(tmp_path)
    (folder / "run.json").write_text(content, "utf-8")
    result = run_check(folder)
    assert result.returncode == 1
    assert result.stderr.splitlines() == ["FAIL run.json is not valid JSON"]


def test_a_missing_run_json_fails_with_a_fail_line(tmp_path):
    result = run_check(tmp_path)
    assert result.returncode == 1
    assert result.stderr.splitlines() == ["FAIL the run folder has no run.json"]


@pytest.mark.parametrize("contract", ["# Test card\n\nNo block here.\n", "```json\n{broken\n```\n"], ids=["no-block", "bad-json"])
def test_a_contract_with_no_json_block_fails_with_a_fail_line(tmp_path, contract):
    skill = tmp_path / "skill"
    shutil.copytree(FIXTURES / "skill", skill)
    (skill / "gates/test-card.md").write_text(contract, "utf-8")
    args = [sys.executable, str(CHECK), str(FIXTURES / "records/good-pr"), "test-card", "--skill", str(skill)]
    result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 1
    assert result.stderr.splitlines() == ["FAIL contract gates/test-card.md has no valid JSON block"]


CONTRACT_SHAPES = {
    "empty-object": "{}",
    "parts-not-a-list": '{"parts": "problem", "uncited": []}',
    "uncited-missing": '{"parts": ["problem", "change"]}',
    "limit-not-a-pair": '{"parts": ["problem", "change"], "uncited": [], "lines": 4}',
    "limit-of-one": '{"parts": ["problem", "change"], "uncited": [], "lines": [4]}',
    "limit-of-text": '{"parts": ["problem", "change"], "uncited": [], "lines": ["2", "4"]}',
    "not-an-object": "[]",
}


@pytest.mark.parametrize("block", CONTRACT_SHAPES.values(), ids=CONTRACT_SHAPES.keys())
def test_a_contract_of_the_wrong_shape_fails_with_a_fail_line(tmp_path, block):
    skill = tmp_path / "skill"
    shutil.copytree(FIXTURES / "skill", skill)
    (skill / "gates/test-card.md").write_text(f"```json\n{block}\n```\n", "utf-8")
    args = [sys.executable, str(CHECK), str(FIXTURES / "records/good-pr"), "test-card", "--skill", str(skill)]
    result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 1
    assert result.stderr.splitlines() == ["FAIL contract gates/test-card.md must list parts and uncited, and give each limit as two numbers"]
