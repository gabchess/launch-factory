# Launch Factory

Turn a merged pull request or a product briefing into content your team can approve.

## Status

Being rebuilt. Version 2 is kept at the [v2.0.0 tag](https://github.com/gabchess/launch-factory/tree/v2.0.0).

This branch holds the Check, its tests and the decision records in `docs/adr/`. Nothing on this branch reads a pull request or a briefing yet.

## The Check

The Check confirms a run record against its gate contracts and fails closed.

    python skills/launch-content/scripts/check.py RUN_FOLDER [GATE] [--skill SKILL_FOLDER]

A run folder holds `run.json`, the Source saved as `snapshot.md`, and one `gates/<gate>/draft.md` per opened gate. A gate contract is `gates/<gate>.md` in the skill folder, with a JSON block that lists its parts and its limits on lines, words and characters.

On a pass, the Check prints one line per gate, such as `test-post: 4 lines, 3 claims, 3/3 parts`, and exits 0. On a fail, it prints one `FAIL` line per problem, naming the claim, line, part or phrase, and exits 1.

Drafts and quotes are plain text, a closed format. A Draft line is one of three kinds: a part marker, exactly `<!-- part: <name> -->`; a heading, `# ` or `## ` and words, only where the gate contract exempts headings; or a sentence, words and then its citations such as `[c1, c2]`. Plain text holds ASCII letters and digits, the Latin-1 letters such as `é` and `ß`, the space and the punctuation `. , ; : ! ? ' " ( ) - / % $ +`. Any other character fails its line, and the `FAIL` line names the line and the character by its code point, such as `U+003C LESS-THAN SIGN`. So HTML, entities, Markdown emphasis, links, invisible characters and letters from other scripts all fail, and the Check never guesses how they render. Formatting belongs in the page a Draft becomes, outside the Check.

The Snapshot, a gate's Owner sources and each Do not say phrase are source text, which the Check does not control. It reads them so that markup can split a word but never join two: every HTML tag and comment becomes a space, entities are decoded, every format or control character becomes a space, minus signs and dashes such as `U+2212` are read as `-` so a number keeps its sign, then Unicode NFKC is applied. A quote must be a run of whole words in what remains, so a quote that needs markup to match fails. Case is ignored everywhere, by Unicode casefold, so `straße` matches `strasse`.

The Check expects plain text in every Draft. Owner edits will later be read from Notion, and that reader, a later ticket, must pass Notion's `plain_text` field. Nothing in this repo reads Notion yet.

It fails a run when a claim's quote is not plain text, has fewer than 3 words or is not a run of whole words in the Snapshot, when a line is not plain text, has no words, cites no claim or cites an unknown claim, when a heading appears in a gate whose contract does not exempt headings, when a number, with its sign, its `%` and its label (the word after it, unless that word holds a digit), is not in the claims a line cites, when a Draft holds a Do not say phrase anywhere, even across lines, when a Do not say phrase has no words, when a part is missing, when a gate has no draft.md, when a gate name is not a plain name, when a Draft is outside its contract's limits or has zero lines or zero claims, when a claim is cited by no opened gate, and when a skip or ask verdict opens a gate. It also fails a run.json field of the wrong type, a claim without a text id and quote, and a claim id used twice. A missing, non UTF-8 or invalid run.json, snapshot.md or contract block prints a `FAIL` line, not a traceback.

An owner claim is a claim with a `gate` field. Its quote must be found in that gate's `owner_sources` text in run.json, not in the Snapshot, and only that gate may cite it. The character limit counts a Draft's words joined by single spaces.

The contracts in `tests/fixtures/check/skill/gates/` exist for the tests only.

## Tests

    pip install pytest
    python -m pytest

## License

See [LICENSE](LICENSE).
