# Launch Factory

Turn a merged pull request or a product briefing into content your team can approve.

## Status

Being rebuilt. Version 2 is kept at the [v2.0.0 tag](https://github.com/gabchess/launch-factory/tree/v2.0.0).

Besides the license and the test setup, this branch holds `launch_factory.py`, whose claim checking is kept as prior art, its tests, and the decision records in `docs/adr/`. Nothing on this branch reads a pull request or a briefing yet.

## What the new version will do

- Two intakes: a merged pull request and a product briefing.
- An agent will give each one a verdict of write, skip or ask, with a reason.
- A quote check in code: every drafted sentence must match its source text exactly.
- Approval by a person before anything leaves the system.
- Publish on merge.

## Tests

    pip install pytest tzdata
    python -m pytest

`tzdata` is needed on Windows, which ships no time zone data. The tests that build media need `ffmpeg` and `ffprobe` and are skipped without them.

## License

See [LICENSE](LICENSE).
