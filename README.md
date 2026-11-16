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

It reads each Draft line, the Snapshot and every quote as a list of words. A word is what a reader sees after Unicode NFKC, with minus signs read as `-`, Markdown emphasis marks, HTML tags and comments deleted even inside a word, and case ignored. Every rule below reads those words, so markup, hyphens, line breaks and Windows line endings cannot hide or fake one. The character limit counts those words joined by single spaces.

It fails a run when a claim's quote has fewer than 3 words or is not a run of whole words in the Snapshot, when a line has no words, cites no claim or cites an unknown claim, when a number, sign included, is not in the claims a line cites, when a Draft holds a Do not say phrase anywhere, even across lines, when a Do not say phrase has no words, when a part is missing, when a gate has no draft.md, when a gate name is not a plain name, when a Draft is outside its contract's limits or has zero lines or zero claims, when a claim is cited by no opened gate, and when a skip or ask verdict opens a gate. It also fails a run.json field of the wrong type, a claim without a text id and quote, and a claim id used twice. A missing, non UTF-8 or invalid run.json, snapshot.md or contract block prints a `FAIL` line, not a traceback.

The contracts in `tests/fixtures/check/skill/gates/` exist for the tests only.

## Tests

    pip install pytest
    python -m pytest

## License

See [LICENSE](LICENSE).
