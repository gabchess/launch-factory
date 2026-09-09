# packages/

Built packages land here, one directory per campaign, named after the campaign
id (for example `camp_myproduct_launch_001/`).

Run `./run.sh RELEASE_FOLDER` or the `/launch-factory:launch` plugin skill to
build one from your own release folder. `engine/scripts/build_package.py`
writes `01_social_video/` through `07_campaign_plan/` (one directory per
slot, `HELD.txt` for a held slot), plus `cadence/`, `provenance/`,
`honesty/still-needs-human.md`, `MANIFEST.json`, and a generated
`REVIEWER.md` card. See [docs/REFERENCE.md](../docs/REFERENCE.md) for the
exact shape.

No pre-built example ships in this repository. `engine/fixtures/` has
runnable fixtures (`demo-release`, `mock-gtm-ship`, `specialist-demo`) if you
want to see the validators pass before pointing the pipeline at your own
material.
