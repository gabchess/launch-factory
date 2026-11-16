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

It fails a run when a claim's quote is empty or not in the Snapshot, when a line cites no claim or an unknown claim, when a line holds only a citation, when a number, sign included, is not in the claims a line cites, when a Draft holds a Do not say phrase on one line or across lines, when a part is missing, when a gate has no draft.md, when a gate name is not a plain name, when a Draft is outside its contract's limits or has zero lines or zero claims, when a claim is cited by no opened gate, and when a skip or ask verdict opens a gate. It normalises Windows line endings and runs of whitespace before it matches quotes.

The contracts in `tests/fixtures/check/skill/gates/` exist for the tests only.

## Tests

    pip install pytest
    python -m pytest

## License

See [LICENSE](LICENSE).
