# V2 reference

| Command | Input | Result |
|---|---|---|
| `inspect FOLDER` | release.json with identity and sourced claims | Quotes, source hashes, Claims Lock digest |
| `lock-claims FOLDER --reviewer NAME` | Same sources, interactive human decision | Local claims-lock.json |
| `build FOLDER --out NEW_FOLDER` | Full release.json, footage, current lock | Six assets, campaign, evidence, review page |
| `verify OUTPUT_FOLDER` | Built package | File hashes, required outputs, video stream/duration checks |

Prefix commands with `python3 launch_factory.py`. `./run.sh` calls `build`. `--example` works only with the bundled self-release rehearsal. Exit 0 means the command completed; exit 2 reports a stopping error.

## Input

Copy the shape of [release.json](../examples/v2-release/release.json). Claims use exact UTF-8 character offsets and quotes. Each copy block contains `text` and existing `claims` IDs. Provide five distinct email segments, written social for LinkedIn/X/Threads, captions within a 1–30 second cut, and 7–30 calendar rows covering the required channels within 14 days.

Source paths must stay within the release folder. Hidden paths and symlinks are refused. Text/JSON inputs are limited to 1 MB, footage to 200 MB. Media must be MP4, MOV, or WebM. The CTA must use HTTPS. The validator is in [launch_factory.py](../launch_factory.py).

## Output

`social/`, `blog/`, `emails/`, `changelog/`, `animation/`, `popup/`, and `campaign/` hold the assets. `evidence/` holds draft inputs, quoted source copies, source/footage hashes, and the Claims Lock record for a normal build. `MANIFEST.json` binds the output bytes. `index.html` is the review page.

Every package stays `review_draft` with `human_approved: false`. A manifest detects accidental edits when trusted; it does not authenticate a reviewer or resist someone rewriting both files and manifest.

## Specialist routing

`engine/scripts/specialist_route.py` remains an optional, offline helper for selecting channel protocols and checking request/result bindings. It is separate from the renderer and grants no provider or approval authority. See [the specialist guide](../engine/specialists/README.md).
