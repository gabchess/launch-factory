# Changelog

## v2.0.0 · 2026-09-13

- Build all six local launch assets, five email variants, and a two-week campaign from source-backed drafts and footage.
- Review the package in one responsive page with playable video and working motion/popup previews.
- Bind Claims Lock to source bytes; reject stale inputs, escaping paths, and changed packages. Preserve earlier output when a build fails.
- Include this release as a reproducible example, with a recorded documentation walkthrough and explicit rehearsal status.
- Replace the old adapter copier and duplicate manifests. Keep channel specialists, simplify the guides, and add CI.

The next major release is v3. Human content approval and publication remain separate.

## Before v2: open-source repackaging

- **Claude Code plugin packaging.** Added `.claude-plugin/plugin.json` and `skills/launch/SKILL.md`, so the repository installs as a plugin (`/plugin install launch-factory --source .`) exposing `/launch-factory:launch`. Bring your own voice bank; the skill carries no personal voice or identity-bound references.
- **Tix example run removed.** `packages/camp_tix_launch_001/` (25MB, including two mp4s, the author's own product) is deleted along with every reference to it: README, START-HERE, docs/HUMAN-GAPS.md, docs/REFERENCE.md, the engineer handoff, and `tests/test_article_handoff.py`. No worked example package ships in this repository; `packages/README.md` explains what lands there and `engine/fixtures/` still has runnable fixtures (`demo-release`, `mock-gtm-ship`, `specialist-demo`).
- **Client engagement removed.** The original client's demo package and its supporting release fixture are deleted from the repository, along with the client's name throughout the root docs.
- **Root docs rewritten for a public audience.** `README.md`, `START-HERE.md`, `AGENTS.md`, and `CHANGELOG.md` no longer name the client; the reviewer role stays generic ("Reviewer"), and every linked path was checked against the current tree before publishing.
- **Repository rename.** The public repository is `gabchess/launch-factory`; root docs use that clone URL.

## 0.2.0: 2026-09-07

- **Repo-root install door (ADR 0012):** the pack envelope rose from `launch-factory/` to the repo root: `START-HERE.md`, `README.md` (merged: agent-install door on top, human prose below), `CHANGELOG.md`, `HOST-MATRIX.md`, `LICENSE-STATUS.md`, `PROVENANCE.md`, manifests, onboarding one-pager, `reviewer/` (human HITL cards), `claude/`, `codex/`, `maintainer-source/`, `scripts/regen_manifests.py`. Pack `docs/*.md` merged into root `docs/` alongside CONTEXT/ADRs/agents docs (no overwrites).
- **Engine single SoT (Option B):** former repo-root working dirs (`schemas/`, `scripts/`, `adapters/`, `fixtures/`, `honesty/`, Reviewer templates) deduplicated into `engine/` by hash comparison, one copy kept; `engine/reviewer/` renamed `engine/reviewer-templates/` to distinguish generator templates from the human `reviewer/` cards. Tests repointed (`.venv/bin/pytest` 22 passed).
- **One release record:** `engine/schemas/release-record.schema.json`, canonical per-release state (input hashes, claims with evidence statuses, claims-lock state, seven slots with states `drafted/reviewed/approved/packaged/held`, voice-check results, validations with retries, gate decisions, run log). New STRUCTURAL_INTEGRITY_ONLY scripts: `engine/scripts/init_release.py` (workspace + skeleton, refuses overwrite), `engine/scripts/validate_record.py` (schema + authority gates: no `approved` without a recorded Reviewer decision), `engine/scripts/transition_slot.py` (permitted transitions only; `approved`/`packaged` require `--human-confirmed`). Fixture example: `engine/fixtures/demo-release/release-record.json`.
- **Skill reframed as one launch-ops operator:** `codex/launch-factory/SKILL.md` rewritten: one visible loop (Ingest, Ground, Claims Lock, Create, Review, Package, Learn), the operating covenant, downshift ladder, deterministic script edges. Never a panel; the user never picks a specialist. Trust/Do-not block and `knowledge/capability-and-authority.md` preserved.
- **Campaign Plan (ADR 0016):** seventh output slot, `engine/adapters/07_campaign_plan.md` (day-by-day multi-channel sequence from locked claims only; one-release cells; no invented future features). `validate_campaign.py` + schema now require slot 7; `cadence_binder.json` stays as the data shape. Customer-facing "cadence" language renamed to Campaign Plan.
- **Voice Bank interim (ADR 0015):** `codex/launch-factory/knowledge/voice-bank-brief.md` placeholder (interim, seed = Reviewer email) + `voice-bank/README.md` collection plan; `knowledge/operating-doctrine.md` added (covenant expanded).
- **One-command door (ADR 0014):** root `run.sh RELEASE_FOLDER`, creates `.venv` if missing, installs requirements, runs init_release, validate_ledger, validate_campaign, build_package with stage banners, fail-fast with the exact failed check + safest re-entry point, prints Reviewer card locations.
- **Version 0.2.0** across manifests, onboarding one-pager (renamed), docs; Claude ZIP rebuilt single-root as `claude/launch-factory-v0.2.0.zip` (old zip deleted); manifests regenerated (self-excluded; `runs/` + `packages/` excluded as run outputs).

## 0.1.1: 2026-09-07

- **Manifest self-reference fix:** `release-manifest.json` no longer lists itself or `documentation-manifest.json` in its files array (circular hashes could never validate). Both manifests regenerated by `scripts/regen_manifests.py` (STRUCTURAL_INTEGRITY_ONLY); version bumped to 0.1.1 in both.
- **Skill interior filled:** `codex/launch-factory/` gains real content: `evals/` (core-transfer-cases + eval-manifest), `examples/` (3 fixture-labelled walkthroughs), `fallbacks/` (degraded-capability + universal copy/paste workflow), `personas/` (writer-seat, reviewer-seat), `references/` (run-log-template). Stale `.gitkeep` files removed from filled directories.
- **Trigger evals added:** `codex/launch-factory/trigger-evals.json` (positive/negative activation cases).
- **Evidence boundary added:** top-level `evidence_boundary` key in `release-manifest.json`, states plainly what the pack proves and does not prove (consistent with HOST-MATRIX).
- Version references updated across docs; onboarding one-pager renamed to v0.1.1; Claude ZIP rebuilt as `claude/launch-factory-v0.1.1.zip` (one-root skill door, now carrying the filled interior). No claim-boundary changes; slots 1/5/6 remain HOLD; no auto-publish.

## 0.1.0: 2026-09-07

### A5: Reviewer HITL cards (product-root `reviewer/`)

- Review nit: OPERATE/FIRST-RUN/reviewer clarify draft first real then spot-check then remaining; product-root `reviewer/` vs `engine/reviewer/` humans-vs-templates line.
- Human card pack: `reviewer/README.md`, `claims-lock.md`, `spot-check.md`, `pack-approve.md` (three gates in order).
- Docs/skill aligned: START-HERE, FIRST-RUN, OPERATE, SKILL, capability-and-authority, TRUST, VALIDATION point at `reviewer/` gates.
- Locks: WIP=1; Writer≠Reviewer; Slack thumbs ≠ approve; no invent $; no auto-publish; no HubSpot before pack approve; HOLD 1/5/6 HELD-skip; first real spot-check = blog.
- Coexists with `engine/reviewer/` templates from A3; does not delete or replace engine templates.

### A3: Wire factory engine (Option B)

- Import live factory spine into `launch-factory/engine/`: schemas, scripts (`validate_ledger`, `validate_campaign`, `build_package`), adapters, fixtures, reviewer templates, honesty note.
- Option B locked: sibling `engine/` is pack SoT; `codex/launch-factory/schemas/` is thin pointer only, no third divergent schema tree.
- Docs/skill/HOST-MATRIX/START-HERE/FIRST-RUN/INSTALL-CODEX updated: engine present; Run may use structural validators when Python available; Claims Lock honesty retained; A7/A8 HOLD.
- Repo-root SHOW-ME spine kept working (pytest). Pack SoT documented as `engine/`; root mirrors until consolidation.
- No auto-publish; no HubSpot send; no invent $; slots 1/5/6 HOLD; ADR 0001 preserved.

### A1 / A2 (prior)

- First Launch Factory workflow pack **skeleton** ship (A1 / gabchess/launch-factory#15).
- Strict finished-pack envelope around factory engine Option B (`engine/` sibling placeholder → now wired in A3).
- Customer docs: START-HERE, dual-host install doors, FIRST-RUN, OPERATE, TRUST, VALIDATION, TROUBLESHOOTING, HUMAN-GAPS.
- Codex skill stub: SKILL, README claim ceiling, capability-and-authority, structural scripts note.
- HITL locks aligned: Reviewer Claims Lock; no auto-publish; no invent pricing; slots 1/5/6 HOLD honesty stubs.
- Claude host ZIP door (A2).
