# Engine (Option B: single source of truth)

The repo root is the pack (ADR 0012); this `engine/` is its canonical spine. The workflow pack's docs/skill sell **Run + Reviewer HITL**, not a schema catalog. Schemas here are the correctness spine inside the product, not the Wed hero.

## Canonical layout

```text
engine/
  schemas/         claim_ledger, release_campaign, cadence_binder, release-record
  scripts/         validate_ledger, validate_campaign, build_package,
                   init_release, validate_record, transition_slot  (STRUCTURAL_INTEGRITY_ONLY)
  adapters/        seven slots (2/3/4 real drafts; 07 Campaign Plan; 1/5/6 HOLD stubs)
  fixtures/        labelled mock release folders (demo-release, seed-release, mock-gtm-ship)
  reviewer-templates/ Claims Lock + pack-approve generator templates (NOT the human cards)
  honesty/         still-needs-human.md
  packages/        local build output only, not shipped as engine SoT
```

`codex/launch-factory/schemas/` is a **thin pointer** only: do not fork a second schema set. The Claude ZIP must mirror the same SoT (no third tree). Human Reviewer cards live at repo-root `reviewer/`. `engine/reviewer-templates/` are pack-builder generator templates; don't open both in a demo.

## How to run (from repo root)

Requires Python 3 + `jsonschema` (repo-root `requirements.txt` / `.venv`).

```bash
cd <repo-root>

# One-command door (ADR 0014): ingest → validate → package
./run.sh engine/fixtures/demo-release

# Stage by stage
.venv/bin/python engine/scripts/init_release.py engine/fixtures/demo-release
.venv/bin/python engine/scripts/validate_record.py runs/demo-release/release-record.json
.venv/bin/python engine/scripts/validate_ledger.py engine/fixtures/seed-release/claim_ledger.json
.venv/bin/python engine/scripts/validate_campaign.py engine/fixtures/seed-release/release_campaign.json
.venv/bin/python engine/scripts/build_package.py engine/fixtures/seed-release/release_campaign.json packages --work-root engine
```

`build_package`'s `work_root` defaults to `campaign_json.parents[2]` → for `engine/fixtures/<name>/*.json` that is `engine/`, so adapter paths resolve as `engine/adapters/...` with no flag.

Repo prove:

```bash
.venv/bin/pytest -q        # expect 77 passed
```

## Hard stops

- **STRUCTURAL_INTEGRITY_ONLY**: validate / package structure; **no publish**, no HubSpot send, no CMS/social mutate.
- **No invent $** / features / limits / competitive claims.
- **Claims Lock before adapters.** Writer ≠ Reviewer. `approved`/`packaged` states require a recorded Reviewer decision (`validate_record.py` enforces; `transition_slot.py` needs `--human-confirmed`).
- **Slots 1 / 5 / 6 HOLD**: honesty stubs only (ADR 0013). Do not claim "all six review-ready."
- **ADR 0001:** Demo Assets ≠ Claim Ledger evidence.
- **No auto-publish.**

## Product wrap

The repo root (`START-HERE`, Codex/Claude doors, manifests) is the installable product. This engine is what Run invokes for structural validation when Python is available. Chat-only Runs still obey Claims Lock honesty. Structural validators do not replace Reviewer.
