# Engine reference

This is a from-source reference for operating the Launch Factory engine. Every
claim below was checked against the code in this checkout (`run.sh`,
`engine/scripts/*.py`, `engine/schemas/*.json`). Where the code and the
existing prose docs (`README.md`, `docs/OPERATE-LAUNCH-FACTORY.md`) disagree,
this file follows the code and calls out the gap.

## 1. Commands

### `run.sh`: the one-command door

```
./run.sh RELEASE_FOLDER
```

No flags. `RELEASE_FOLDER` is a directory containing `release_campaign.json`
(directly, or the script falls back to `engine/fixtures/<folder-name>/`).
Runs five stages in order, `set -euo pipefail`, and stops at the first
failure. `fail()` prints the failed check plus a "safest re-entry" message to
stderr and exits 1. It does not retry.

| Stage | What runs | On failure |
| --- | --- | --- |
| 0 | Creates `.venv/`, installs `requirements.txt` if needed | exits 1 |
| 1 | `init_release.py`, then `validate_record.py` on the fresh record | resumes if a record already exists at `runs/<name>/` |
| 2 | `validate_ledger.py` on the release folder's `claim_ledger.json` | skipped with a warning if no ledger file is found |
| 3 | `validate_campaign.py` on `release_campaign.json` | exits 1 on any missing slot or bad `reviewer.wip` |
| 4 | `build_package.py` into `packages/<campaign id>/` | exits 1 if an adapter path is missing |

The fixture previously verified here (the original client fixture) has been
removed from this checkout along with the client material it held. Before
relying on `./run.sh FIXTURE`, confirm your target fixture under
`engine/fixtures/` actually has every path `build_package.py` needs
(`cadence_binder.json`, `sources/*`, `claim_ledger.json`,
`engine/adapters/02_blog.md`, and `engine/honesty/still-needs-human.md`);
do not assume a fixture is complete just because it is present.

### `engine/scripts/*.py`: the six STRUCTURAL_INTEGRITY_ONLY scripts

All are plain `python3 script.py ...`. None call a network or publish
anything. Each prints JSON, except `init_release.py`, which prints the
record path. Each uses its exit code as the pass/fail signal.

| Script | Usage | Exit code |
| --- | --- | --- |
| `init_release.py` | `RELEASE_FOLDER [--workspace DIR]` | 0, or a `SystemExit` message |
| `validate_record.py` | `RECORD` | 0 ok / 1 fail |
| `transition_slot.py` | `RECORD SLOT STATUS [--human-confirmed] [--reason TEXT]` | 0 ok / `SystemExit` on refusal |
| `validate_ledger.py` | `LEDGER_PATH` | 0 ok / 1 fail / 2 if kill-switch armed |
| `validate_campaign.py` | `CAMPAIGN_PATH` | 0 ok / 1 fail |
| `build_package.py` | `CAMPAIGN_JSON OUT_DIR [--work-root PATH]` | 0, prints the built path |

What each one does:

- **`init_release.py`**: sha256-hashes every file in `RELEASE_FOLDER`,
  writes `release-record.json` with all 7 slots defaulted to `held` (slots
  1/5/6 get a fixed ADR-0013 hold reason), and refuses to overwrite an
  existing record.
- **`validate_record.py`**: schema-checks the record, then confirms no slot
  is `approved`/`packaged` without a matching Reviewer `gates` entry, and that
  a `locked_by_reviewer` claims lock has its own timestamp and gate entry.
  Read-only.
- **`transition_slot.py`**: applies one permitted state transition to one
  slot and rewrites `RECORD` in place; see §3. `SLOT` accepts `1`-`7` or a
  slot name.
- **`validate_ledger.py`**: schema-checks the ledger, then confirms every
  `allowed` claim has a valid evidence span, no `allowed` text contains
  forbidden text, and every evidence `claim_id` resolves. Any failure arms
  `kill_switch.armed` and exits 2.
- **`validate_campaign.py`**: schema-checks the campaign, then confirms all
  7 slots exist with a `path` or `hold_reason`, all 7 artifact types are
  present, `reviewer.wip == 1`, and both segment lists are non-empty. Also
  exposes `validate_cadence_binder()`, unused by `run.sh`.
- **`build_package.py`**: builds `OUT_DIR/<campaign id>/` with one directory
  per slot, `cadence/` and `provenance/` copies, an `honesty/` stub,
  `MANIFEST.json` (`auto_publish: false` always), and a generated `REVIEWER.md`
  card. This shape matches neither package checked into `packages/` today;
  see §2.

### `engine/scripts/specialist_route.py`: offline specialist routing

```
python engine/scripts/specialist_route.py {route|validate-result|check-binding} REQUEST.json --workspace DIR [--result RESULT.json]
```

Not called by `run.sh`. Resolves specialist role(s) for a
`deliverable`/`stage` against `engine/specialists/registry.json`, re-hashes
every referenced file, and returns `status: held` with named reasons, or
`status: ready_for_protocol`. `human_approval_granted`,
`generation_authorized`, and `authentication_verified` are `false` in every
code path. Any error prints `{"status": "refused", ...}` and exits 2.

## 2. Package layout (ground truth: `engine/scripts/build_package.py`)

No package ships in this repository. `packages/` fills in only once you run
`run.sh` or `build_package.py` against your own release folder. Two hand-assembled
worked examples shipped here in earlier snapshots; both were removed along with the
client and product material they held. This section describes what
`build_package.py` actually writes, checked against its source.

`build_package.py CAMPAIGN_JSON OUT_DIR` writes `OUT_DIR/<campaign id>/`:

- `01_social_video/`, `02_blog/`, `03_email_segments/`, `04_changelog/`,
  `05_login_animation/`, `06_in_app_popup/`, `07_campaign_plan/`: one directory
  per slot. A held slot gets `HELD.txt` (the hold reason); a slot whose artifact
  path is missing gets `MISSING.txt` (the expected path); otherwise the artifact
  file is copied in under its own name.
- `cadence/`: a copy of the campaign's cadence file (`cadence_ref`, default
  `cadence_binder.json`), if it exists.
- `provenance/`: copies of the campaign's `sources.transcript`,
  `sources.github_outline`, and claim ledger (`claim_ledger_ref`), if they exist.
- `honesty/still-needs-human.md`: copied from `work_root/honesty/still-needs-human.md`
  if present, else generated from the campaign's `still_needs_human` list.
- `MANIFEST.json`: `campaign_id, title, fixture_label, status
  (review_ready_pre_claims_lock | packaged), auto_publish: false, reviewer_seat,
  hubspot_sandbox, note`.
- `REVIEWER.md`: a generated review card with campaign, seat, surface, package
  and Claims Lock status, the first non-held slot due for spot-check, a
  slot table, review links, a decision checklist, and a forbidden-actions list.

## 3. State machine (`engine/scripts/transition_slot.py`)

One `release-record.json` holds 7 slots (`1`-`7`, fixed names
`social_video, blog, email_segments, changelog, login_animation,
in_app_popup, campaign_plan`). Each slot's `state` is one of `held, drafted,
reviewed, approved, packaged`.

| From | To | Extra requirement |
| --- | --- | --- |
| `held` | `drafted` | none, clears `hold_reason` |
| `drafted` | `reviewed` | none |
| `drafted` | `held` | `--reason TEXT` |
| `reviewed` | `approved` | `--human-confirmed` |
| `reviewed` | `held` | `--reason TEXT` |
| `reviewed` | `drafted` | none (request changes) |
| `approved` | `packaged` | `--human-confirmed` |
| `approved` | `reviewed` | none (request changes after approve) |

Every other `(from, to)` pair, including any transition into `held` without
`--reason`, is refused: the script raises `SystemExit("refused: ...")`,
printed to stderr, exit 1, and nothing is written to disk. A transition into
`approved`/`packaged` without `--human-confirmed` refuses the same way; only
Reviewer, the human, authorizes those two states, and the writer seat never
self-approves.

On success the script always appends one `run_log` entry, and, only for
transitions into `approved`/`packaged`, one `gates` entry
(`decided_by: "reviewer"`, `decision: "approve"`). This gate entry is what
`validate_record.py` later checks for, and it is written by the CLI flag
alone, not by any identity check (see §5).

`claims_lock.state` (`drafted` to `locked_by_reviewer`) is a separate record
field that no script in `engine/scripts/` transitions. `validate_record.py`
only checks that, once already `locked_by_reviewer`, a matching `locked_at`
timestamp and `gates` entry (`gate: "claims_lock"`) both exist.

## 4. Data files

**`claim_ledger.schema.json`** requires `campaign_id, allowed, forbidden,
needs_disclaimer, evidence, kill_switch`. Each `evidence` row's `source`
field is a closed enum: `loom_transcript | github_outline | footage_index`.
Redacted shape:

```json
{
  "campaign_id": "camp_...",
  "allowed": [{ "claim_id": "vw1", "text": "..." }],
  "forbidden": [{ "claim_id": "f1", "text": "...", "reason": "..." }],
  "needs_disclaimer": [{ "claim_id": "d1", "text": "...", "disclaimer": "..." }],
  "evidence": [{ "claim_id": "vw1", "source": "loom_transcript",
                 "path": "sources/...", "span_start": 498, "span_end": 550,
                 "quote": "..." }],
  "kill_switch": { "armed": false, "reason": null }
}
```

A fixture that previously shipped here (the original client fixture)
conformed to this schema, while the fuller example package's ledger did not:
its `evidence[].source` values (`supplied_email_source_text`,
`repository_source_text`, `public_web_capture`) were not in the schema enum,
so `validate_ledger.py` would fail against that file. Both were removed from
this checkout with the client material they held; check any fixture you add
against the schema's closed `evidence[].source` enum before assuming
`validate_ledger.py` will pass.

**`release-record.schema.json`** (`release-record/v1`): a record has
`record_id, release_folder{path,files[]}, ingest{state,at},
claims{allowed,forbidden,held}, claims_lock{state,locked_at}, slots[7],
voice_check, validations[], gates[], package_path, run_log[]`. Each slot is
`{slot,name,state,hold_reason}`; each gate is
`{gate,decision,decided_by,at}` with `decided_by` one of `reviewer | writer |
orchestrator`.

**`release_campaign.schema.json`**: `id, title, folder_id, status` (13-value
enum), `sources{loom,transcript,github_outline,footage[]}, claim_ledger_ref,
voice_pack_ref, segments{leads,customers,affiliate_rules}, artifacts[7],
cadence_ref, reviewer{seat,surface,wip}, hubspot_sandbox{draft_ids,status}`
(the field is literally named `hubspot_sandbox` in the schema regardless of
which CRM or ESP you actually use), `still_needs_human[]`. Each artifact is
`{slot,type,version,path,validation,reviewer_status,held,hold_reason}`.

**`cadence_binder.schema.json`**: `campaign_id, fixture_label, cells[]`,
each cell `{order,channel,artifact_slot,utm{utm_source,utm_medium,
utm_campaign},notes}`. `channel` is one of 8 fixed cadence values
(`changelog, email_interrupt, story_video, linkedin_written, x_written,
threads_written, instagram_video, tiktok_video`).

**`campaign/calendar.csv`** columns: `week, proposed_day, order, timezone,
channel, audience, asset_id, asset_path, action, review_state`. Illustrative
row, from a package removed with the client material it held:

```
1,Mon (proposed),1,America/Sao_Paulo,blog,all social managers,blog-v1,artifacts/blog.html,read linked-task story,delegated_review_pending_reviewer
```

`campaign/calendar.json` wraps the same rows, plus `scheduled: false`, a
`timezone`, and an `asset_index` mapping every `asset_id` to its file path.

**`costs/costs.json`**, redacted real example:

```json
{
  "currency": "USD",
  "incremental_paid_calls_this_run": 0,
  "observed_usd_this_run": 0,
  "prior_observed_usd": 0.235,
  "prior_provider_credit_usd_unknown": true,
  "ceiling_usd": 500
}
```

**`jobs/jobs.json`** shape: `{"jobs": [{"id","state","provider","paid"}]}`.
In the removed example package, every recorded job had `"state": "completed"`
and `"paid": false`.

**`events/events.jsonl`**: one JSON object per line, illustrative example
`{"event": "local_package_built", "at": "...", "paid_provider_call": false,
"route": "..."}`.

## 5. What is NOT implemented

The existing prose docs make several claims the code does not back up.
Verified against the actual scripts in this checkout:

- **No retries.** `run.sh`'s `fail()` exits on the first failure; no script
  under `engine/scripts/` loops or retries. The schemas carry a `retries`
  counter and a `retryable_fail` enum value, but nothing increments or acts
  on them yet.
- **No hash-bound approval invalidation.** `transition_slot.py` never reads
  or compares a file hash on approval. Nothing here reopens a gate when an
  approved file's content changes. The narrow exception is the video
  production validator, which binds its own approval to content bytes.
- **No auto-publish.** True as claimed: `build_package.py` hardcodes
  `"auto_publish": false` always, and nothing under `engine/` calls a send,
  publish, or schedule API.
- **No hosted trigger.** Every entrypoint here is a local CLI script, run
  from a shell or an agent session; no server, webhook, or UI starts a run.
- **No authentication on `--human-confirmed`.** It is a boolean CLI flag,
  not an identity check; anyone who can run the script can pass it.
  `specialist_route.py` says as much about itself, marking every output
  `"authentication_verified": false`.
